"""
Controller do Dashboard de Monitoramento.

Endpoints para visualização de métricas e status das integrações.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..core.events import get_event_bus, TipoEvento
from ..core.contingency import VerificadorDisponibilidade, MATRIZ_CONTINGENCIA_NFE
from ..core.credentials import get_vault_client, GerenciadorCertificados

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard Monitoramento"])


# ============================================================================
# Schemas
# ============================================================================

class ResumoExtracao(BaseModel):
    """Resumo de extrações do período."""

    total_documentos: int = 0
    documentos_novos: int = 0
    documentos_atualizados: int = 0
    documentos_erro: int = 0
    extracoes_executadas: int = 0
    extracoes_sucesso: int = 0
    extracoes_falha: int = 0
    ultima_extracao: Optional[datetime] = None


class ResumoServico(BaseModel):
    """Resumo por serviço governamental."""

    servico: str
    nome_exibicao: str
    status: str  # online, offline, degraded
    documentos_processados: int = 0
    documentos_erro: int = 0
    ultima_sincronizacao: Optional[datetime] = None
    tempo_medio_resposta_ms: Optional[float] = None
    taxa_sucesso: float = 100.0


class StatusEndpoint(BaseModel):
    """Status de um endpoint."""

    uf: str
    servico: str
    endpoint: str
    disponivel: bool
    tempo_resposta_ms: Optional[float] = None
    ultimo_check: datetime
    falhas_consecutivas: int = 0


class AlertaCertificado(BaseModel):
    """Alerta de certificado expirando."""

    tenant_id: str
    tipo_certificado: str
    dias_restantes: int
    validade_fim: datetime
    severidade: str  # warning, critical


class EventoRecente(BaseModel):
    """Evento recente do sistema."""

    tipo: str
    servico: Optional[str] = None
    uf: Optional[str] = None
    descricao: str
    severidade: str
    timestamp: datetime
    detalhes: Optional[Dict[str, Any]] = None


class DashboardResponse(BaseModel):
    """Resposta completa do dashboard."""

    periodo_inicio: datetime
    periodo_fim: datetime
    resumo_geral: ResumoExtracao
    servicos: List[ResumoServico]
    endpoints_indisponiveis: List[StatusEndpoint]
    alertas_certificados: List[AlertaCertificado]
    eventos_recentes: List[EventoRecente]
    atualizado_em: datetime


class MetricasResponse(BaseModel):
    """Métricas detalhadas por período."""

    periodo_inicio: datetime
    periodo_fim: datetime
    documentos_por_dia: Dict[str, int]
    documentos_por_servico: Dict[str, int]
    erros_por_servico: Dict[str, int]
    tempo_medio_por_servico: Dict[str, float]


# ============================================================================
# Service Layer
# ============================================================================

class DashboardService:
    """Serviço de coleta de métricas para o dashboard."""

    SERVICOS = {
        "sefaz_nfe": "NF-e/NFC-e",
        "sefaz_cte": "CT-e",
        "sefaz_mdfe": "MDF-e",
        "esocial": "eSocial",
        "fgts_digital": "FGTS Digital",
        "nfse_manaus": "NFS-e Manaus",
        "receita_federal": "Receita Federal",
        "simples_nacional": "Simples Nacional",
    }

    def __init__(self):
        self.event_bus = get_event_bus()
        self.verificador = VerificadorDisponibilidade()

    async def obter_dashboard(
        self,
        tenant_id: Optional[UUID] = None,
        periodo_dias: int = 7
    ) -> DashboardResponse:
        """Obtém dados completos do dashboard."""
        periodo_fim = datetime.utcnow()
        periodo_inicio = periodo_fim - timedelta(days=periodo_dias)

        # Coletar dados
        resumo = await self._obter_resumo_geral(tenant_id, periodo_inicio, periodo_fim)
        servicos = await self._obter_status_servicos(tenant_id, periodo_inicio, periodo_fim)
        endpoints_down = await self._obter_endpoints_indisponiveis()
        alertas_cert = await self._obter_alertas_certificados(tenant_id)
        eventos = await self._obter_eventos_recentes(tenant_id, limite=20)

        return DashboardResponse(
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            resumo_geral=resumo,
            servicos=servicos,
            endpoints_indisponiveis=endpoints_down,
            alertas_certificados=alertas_cert,
            eventos_recentes=eventos,
            atualizado_em=datetime.utcnow(),
        )

    async def _obter_resumo_geral(
        self,
        tenant_id: Optional[UUID],
        inicio: datetime,
        fim: datetime
    ) -> ResumoExtracao:
        """Obtém resumo geral das extrações."""
        # Em produção, buscar do banco de dados
        # SELECT COUNT(*), SUM(documentos_novos), ... FROM extracoes WHERE ...

        return ResumoExtracao(
            total_documentos=0,
            documentos_novos=0,
            documentos_atualizados=0,
            documentos_erro=0,
            extracoes_executadas=0,
            extracoes_sucesso=0,
            extracoes_falha=0,
            ultima_extracao=None,
        )

    async def _obter_status_servicos(
        self,
        tenant_id: Optional[UUID],
        inicio: datetime,
        fim: datetime
    ) -> List[ResumoServico]:
        """Obtém status de cada serviço."""
        servicos = []

        for codigo, nome in self.SERVICOS.items():
            # Em produção, agregar dados do banco
            servicos.append(ResumoServico(
                servico=codigo,
                nome_exibicao=nome,
                status="online",
                documentos_processados=0,
                documentos_erro=0,
                ultima_sincronizacao=None,
                tempo_medio_resposta_ms=None,
                taxa_sucesso=100.0,
            ))

        return servicos

    async def _obter_endpoints_indisponiveis(self) -> List[StatusEndpoint]:
        """Lista endpoints atualmente indisponíveis."""
        indisponiveis = []

        # Verificar status em cache/banco
        # Em produção, manter histórico de verificações

        for uf in MATRIZ_CONTINGENCIA_NFE.keys():
            resultado = await self.verificador.verificar_endpoint(uf, "nfe")

            if not resultado.disponivel:
                indisponiveis.append(StatusEndpoint(
                    uf=uf,
                    servico="nfe",
                    endpoint=resultado.endpoint or "N/A",
                    disponivel=False,
                    tempo_resposta_ms=resultado.tempo_resposta_ms,
                    ultimo_check=datetime.utcnow(),
                    falhas_consecutivas=resultado.falhas_consecutivas or 0,
                ))

        return indisponiveis

    async def _obter_alertas_certificados(
        self,
        tenant_id: Optional[UUID]
    ) -> List[AlertaCertificado]:
        """Lista certificados próximos da expiração."""
        alertas = []

        try:
            vault = get_vault_client()
            cert_manager = GerenciadorCertificados(vault)

            # Em produção, buscar tenants do banco
            if tenant_id:
                certificados = await cert_manager.listar_certificados(tenant_id)

                for cert in certificados:
                    if cert.alerta_expiracao:
                        alertas.append(AlertaCertificado(
                            tenant_id=str(tenant_id),
                            tipo_certificado=cert.tipo.value,
                            dias_restantes=cert.dias_restantes,
                            validade_fim=cert.validade_fim,
                            severidade="critical" if cert.dias_restantes <= 7 else "warning",
                        ))
        except Exception as e:
            logger.error(f"Erro ao verificar certificados: {e}")

        return alertas

    async def _obter_eventos_recentes(
        self,
        tenant_id: Optional[UUID],
        limite: int = 20
    ) -> List[EventoRecente]:
        """Lista eventos recentes do sistema."""
        eventos = []

        # Em produção, buscar do banco de eventos
        # SELECT * FROM eventos ORDER BY timestamp DESC LIMIT ...

        return eventos

    async def obter_metricas(
        self,
        tenant_id: Optional[UUID],
        periodo_dias: int = 30
    ) -> MetricasResponse:
        """Obtém métricas detalhadas para gráficos."""
        periodo_fim = datetime.utcnow()
        periodo_inicio = periodo_fim - timedelta(days=periodo_dias)

        # Em produção, agregar dados do banco por dia/serviço
        documentos_por_dia = {}
        documentos_por_servico = {s: 0 for s in self.SERVICOS.keys()}
        erros_por_servico = {s: 0 for s in self.SERVICOS.keys()}
        tempo_medio_por_servico = {s: 0.0 for s in self.SERVICOS.keys()}

        return MetricasResponse(
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            documentos_por_dia=documentos_por_dia,
            documentos_por_servico=documentos_por_servico,
            erros_por_servico=erros_por_servico,
            tempo_medio_por_servico=tempo_medio_por_servico,
        )


# ============================================================================
# Endpoints
# ============================================================================

dashboard_service = DashboardService()


@router.get("/", response_model=DashboardResponse)
async def obter_dashboard(
    tenant_id: Optional[str] = Query(None, description="ID do tenant"),
    dias: int = Query(7, ge=1, le=90, description="Período em dias"),
):
    """
    Obtém visão geral do dashboard de monitoramento.

    Inclui:
    - Resumo de extrações do período
    - Status de cada serviço governamental
    - Endpoints indisponíveis
    - Alertas de certificados
    - Eventos recentes
    """
    try:
        tid = UUID(tenant_id) if tenant_id else None
        return await dashboard_service.obter_dashboard(tid, dias)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de tenant inválido: {e}"
        )
    except Exception as e:
        logger.error(f"Erro ao obter dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao carregar dashboard"
        )


@router.get("/metricas", response_model=MetricasResponse)
async def obter_metricas(
    tenant_id: Optional[str] = Query(None, description="ID do tenant"),
    dias: int = Query(30, ge=1, le=365, description="Período em dias"),
):
    """
    Obtém métricas detalhadas para gráficos.

    Retorna dados agregados por dia e por serviço.
    """
    try:
        tid = UUID(tenant_id) if tenant_id else None
        return await dashboard_service.obter_metricas(tid, dias)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de tenant inválido: {e}"
        )
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao carregar métricas"
        )


@router.get("/endpoints", response_model=List[StatusEndpoint])
async def listar_status_endpoints():
    """
    Lista status de todos os endpoints governamentais.

    Mostra disponibilidade atual de cada endpoint por UF.
    """
    try:
        return await dashboard_service._obter_endpoints_indisponiveis()
    except Exception as e:
        logger.error(f"Erro ao listar endpoints: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar endpoints"
        )


@router.get("/certificados/alertas", response_model=List[AlertaCertificado])
async def listar_alertas_certificados(
    tenant_id: Optional[str] = Query(None, description="ID do tenant"),
):
    """
    Lista alertas de certificados próximos da expiração.
    """
    try:
        tid = UUID(tenant_id) if tenant_id else None
        return await dashboard_service._obter_alertas_certificados(tid)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de tenant inválido: {e}"
        )
    except Exception as e:
        logger.error(f"Erro ao verificar certificados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao verificar certificados"
        )


@router.get("/eventos", response_model=List[EventoRecente])
async def listar_eventos_recentes(
    tenant_id: Optional[str] = Query(None, description="ID do tenant"),
    limite: int = Query(50, ge=1, le=200, description="Limite de eventos"),
):
    """
    Lista eventos recentes do sistema.

    Inclui alertas, erros e notificações.
    """
    try:
        tid = UUID(tenant_id) if tenant_id else None
        return await dashboard_service._obter_eventos_recentes(tid, limite)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID de tenant inválido: {e}"
        )
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao carregar eventos"
        )


@router.post("/endpoints/{uf}/{servico}/verificar")
async def verificar_endpoint(uf: str, servico: str):
    """
    Força verificação de disponibilidade de um endpoint específico.
    """
    try:
        verificador = VerificadorDisponibilidade()
        resultado = await verificador.verificar_endpoint(uf.upper(), servico)

        return {
            "uf": uf.upper(),
            "servico": servico,
            "disponivel": resultado.disponivel,
            "tempo_resposta_ms": resultado.tempo_resposta_ms,
            "erro": resultado.erro,
            "verificado_em": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Erro ao verificar endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar endpoint: {e}"
        )
