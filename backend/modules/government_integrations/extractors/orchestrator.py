"""
Orquestrador Principal de Extração de Dados Governamentais.

Coordena a extração de todos os serviços governamentais.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Type
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from enum import Enum
import asyncio
import logging

from ..core.credentials import (
    ProvedorCredenciais,
    TipoCredencial,
    get_credential_provider,
)
from ..core.rate_limiting import (
    GerenciadorFilas,
    get_queue_manager,
)
from ..core.compliance import (
    AuditLogger,
    TipoEvento,
    AuditEvent,
    get_audit_logger,
)
from ..core.events import (
    EventBus,
    EventoSincronizacao,
    TipoEvento as TipoEventoSistema,
    get_event_bus,
)
from ..core.contingency import (
    VerificadorDisponibilidade,
    ComutadorEndpoints,
)

logger = logging.getLogger(__name__)


class TipoServico(Enum):
    """Tipos de serviço para extração."""
    # SEFAZ - Documentos Fiscais
    SEFAZ_NFE = "sefaz_nfe"
    SEFAZ_CTE = "sefaz_cte"
    SEFAZ_MDFE = "sefaz_mdfe"
    SEFAZ_AM = "sefaz_am"

    # Trabalhista
    ESOCIAL = "esocial"
    FGTS_DIGITAL = "fgts_digital"

    # NFS-e
    NFSE_MANAUS = "nfse_manaus"
    NFSE_NACIONAL = "nfse_nacional"

    # Receita Federal
    RECEITA_FEDERAL = "receita_federal"
    DCTFWEB = "dctfweb"
    EFD_REINF = "efd_reinf"
    ECAC = "ecac"
    SIMPLES_NACIONAL = "simples_nacional"

    # SPED
    SPED_FISCAL = "sped_fiscal"
    SPED_CONTABIL = "sped_contabil"

    # Gov.br
    GOVBR = "govbr"


class StatusExtracao(Enum):
    """Status de uma extração."""
    INICIADA = "iniciada"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CONCLUIDA_PARCIAL = "concluida_parcial"
    FALHA = "falha"
    CANCELADA = "cancelada"


@dataclass
class ConfiguracaoExtracao:
    """Configuração para extração."""
    # Serviços a extrair
    servicos: List[TipoServico] = field(default_factory=list)

    # Período
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

    # Filtros
    cnpjs: Optional[List[str]] = None
    ufs: Optional[List[str]] = None

    # Comportamento
    modo_incremental: bool = True  # False = extração completa
    processar_em_paralelo: bool = True
    max_workers: int = 5
    timeout_por_servico: int = 300  # 5 minutos

    # Callbacks
    notificar_progresso: bool = True
    webhook_conclusao: Optional[str] = None


@dataclass
class ResultadoServico:
    """Resultado de extração de um serviço."""
    servico: TipoServico
    status: StatusExtracao
    inicio: datetime
    fim: Optional[datetime] = None
    documentos_processados: int = 0
    documentos_novos: int = 0
    documentos_atualizados: int = 0
    documentos_erro: int = 0
    erros: List[str] = field(default_factory=list)
    detalhes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoExtracao:
    """Resultado completo de uma extração."""
    id: UUID = field(default_factory=uuid4)
    tenant_id: UUID = None
    status: StatusExtracao = StatusExtracao.INICIADA
    inicio: datetime = field(default_factory=datetime.utcnow)
    fim: Optional[datetime] = None
    configuracao: ConfiguracaoExtracao = None
    resultados_servicos: Dict[str, ResultadoServico] = field(default_factory=dict)

    # Totais
    total_documentos: int = 0
    total_novos: int = 0
    total_atualizados: int = 0
    total_erros: int = 0

    # Erros gerais
    erros: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "status": self.status.value,
            "inicio": self.inicio.isoformat(),
            "fim": self.fim.isoformat() if self.fim else None,
            "duracao_segundos": (self.fim - self.inicio).total_seconds() if self.fim else None,
            "totais": {
                "documentos": self.total_documentos,
                "novos": self.total_novos,
                "atualizados": self.total_atualizados,
                "erros": self.total_erros,
            },
            "servicos": {
                nome: {
                    "status": res.status.value,
                    "documentos_processados": res.documentos_processados,
                    "documentos_novos": res.documentos_novos,
                    "erros": len(res.erros),
                }
                for nome, res in self.resultados_servicos.items()
            },
            "erros": self.erros[:10],  # Limitar erros no resumo
        }


class OrquestradorExtracao:
    """
    Orquestrador principal de extração de dados governamentais.

    Responsabilidades:
    - Validar pré-requisitos (certificados, credenciais)
    - Coordenar extração de múltiplos serviços
    - Gerenciar paralelismo e rate limits
    - Registrar auditoria e eventos
    - Gerar relatórios de execução
    """

    def __init__(
        self,
        credential_provider: Optional[ProvedorCredenciais] = None,
        queue_manager: Optional[GerenciadorFilas] = None,
        audit_logger: Optional[AuditLogger] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.credentials = credential_provider or get_credential_provider()
        self.queue = queue_manager or get_queue_manager()
        self.audit = audit_logger or get_audit_logger()
        self.events = event_bus or get_event_bus()

        # Extratores registrados
        self._extratores: Dict[TipoServico, Any] = {}

        # Verificador de disponibilidade
        self.verificador = VerificadorDisponibilidade()
        self.comutador = ComutadorEndpoints()

    def registrar_extrator(self, tipo: TipoServico, extrator: Any):
        """Registra um extrator para um tipo de serviço."""
        self._extratores[tipo] = extrator
        logger.info(f"Extrator registrado: {tipo.value}")

    async def validar_prerequisitos(
        self,
        tenant_id: UUID,
        servicos: List[TipoServico]
    ) -> Dict[str, Any]:
        """
        Valida pré-requisitos para extração.

        Verifica:
        - Certificados válidos
        - Credenciais configuradas
        - Endpoints disponíveis

        Returns:
            Dicionário com status de cada pré-requisito
        """
        resultado = {
            "valido": True,
            "certificados": {},
            "credenciais": {},
            "endpoints": {},
            "erros": [],
        }

        # Verificar certificados
        for servico in servicos:
            tipo_cred = self._mapear_tipo_credencial(servico)
            if tipo_cred:
                try:
                    validacao = await self.credentials.validar_credencial(
                        tenant_id, tipo_cred
                    )
                    resultado["certificados"][servico.value] = validacao

                    if not validacao.get("valida", False):
                        resultado["valido"] = False
                        resultado["erros"].append(
                            f"Credencial inválida para {servico.value}: {validacao.get('erro')}"
                        )

                except Exception as e:
                    resultado["valido"] = False
                    resultado["erros"].append(f"Erro ao validar {servico.value}: {e}")

        # Verificar endpoints (amostra)
        servicos_sefaz = [s for s in servicos if "sefaz" in s.value.lower()]
        if servicos_sefaz:
            try:
                verificacao = await self.verificador.verificar_endpoint(
                    "SP", "nfe", usar_principal=True
                )
                resultado["endpoints"]["sefaz_sp"] = {
                    "disponivel": verificacao.disponivel,
                    "tempo_ms": verificacao.tempo_resposta_ms,
                }
            except Exception as e:
                logger.warning(f"Erro ao verificar endpoint: {e}")

        return resultado

    async def iniciar_extracao(
        self,
        tenant_id: UUID,
        config: ConfiguracaoExtracao,
        usuario_id: Optional[UUID] = None
    ) -> ResultadoExtracao:
        """
        Inicia processo de extração de dados.

        Args:
            tenant_id: ID do tenant
            config: Configuração da extração
            usuario_id: ID do usuário que iniciou

        Returns:
            ResultadoExtracao com status e detalhes
        """
        resultado = ResultadoExtracao(
            tenant_id=tenant_id,
            configuracao=config,
        )

        # Registrar início na auditoria
        await self.audit.registrar(AuditEvent(
            tenant_id=tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.SINCRONIZACAO,
            recurso="extracao_governamental",
            recurso_id=str(resultado.id),
            acao="Extração iniciada",
            metadata={
                "servicos": [s.value for s in config.servicos],
                "modo_incremental": config.modo_incremental,
            },
        ))

        # Publicar evento de início
        await self.events.publicar(EventoSincronizacao(
            tipo_evento=TipoEventoSistema.SYNC_INICIADA,
            tenant_id=tenant_id,
            servico="extracao_completa",
            tipo_sync="incremental" if config.modo_incremental else "full",
        ))

        logger.info(
            f"Extração iniciada: {resultado.id} - "
            f"Tenant: {tenant_id} - "
            f"Serviços: {[s.value for s in config.servicos]}"
        )

        try:
            # Validar pré-requisitos
            validacao = await self.validar_prerequisitos(tenant_id, config.servicos)
            if not validacao["valido"]:
                resultado.status = StatusExtracao.FALHA
                resultado.erros = validacao["erros"]
                resultado.fim = datetime.utcnow()
                return resultado

            resultado.status = StatusExtracao.EM_ANDAMENTO

            # Executar extração
            if config.processar_em_paralelo:
                await self._extrair_paralelo(tenant_id, config, resultado)
            else:
                await self._extrair_sequencial(tenant_id, config, resultado)

            # Calcular totais
            self._calcular_totais(resultado)

            # Determinar status final
            if resultado.total_erros == 0:
                resultado.status = StatusExtracao.CONCLUIDA
            elif resultado.total_documentos > resultado.total_erros:
                resultado.status = StatusExtracao.CONCLUIDA_PARCIAL
            else:
                resultado.status = StatusExtracao.FALHA

        except Exception as e:
            logger.error(f"Erro na extração {resultado.id}: {e}")
            resultado.status = StatusExtracao.FALHA
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()

            # Registrar conclusão
            await self._registrar_conclusao(resultado, usuario_id)

        return resultado

    async def _extrair_paralelo(
        self,
        tenant_id: UUID,
        config: ConfiguracaoExtracao,
        resultado: ResultadoExtracao
    ):
        """Executa extração de serviços em paralelo."""
        semaphore = asyncio.Semaphore(config.max_workers)

        async def extrair_com_limite(servico: TipoServico):
            async with semaphore:
                return await self._extrair_servico(
                    tenant_id, servico, config, resultado
                )

        tarefas = [
            extrair_com_limite(servico)
            for servico in config.servicos
        ]

        await asyncio.gather(*tarefas, return_exceptions=True)

    async def _extrair_sequencial(
        self,
        tenant_id: UUID,
        config: ConfiguracaoExtracao,
        resultado: ResultadoExtracao
    ):
        """Executa extração de serviços sequencialmente."""
        for servico in config.servicos:
            await self._extrair_servico(tenant_id, servico, config, resultado)

    async def _extrair_servico(
        self,
        tenant_id: UUID,
        servico: TipoServico,
        config: ConfiguracaoExtracao,
        resultado: ResultadoExtracao
    ) -> ResultadoServico:
        """Extrai dados de um serviço específico."""
        resultado_servico = ResultadoServico(
            servico=servico,
            status=StatusExtracao.EM_ANDAMENTO,
            inicio=datetime.utcnow(),
        )

        logger.info(f"Iniciando extração: {servico.value}")

        try:
            # Obter extrator
            extrator = self._extratores.get(servico)

            if extrator is None:
                # Usar extrator genérico se disponível
                resultado_servico = await self._extrair_generico(
                    tenant_id, servico, config
                )
            else:
                # Usar extrator específico
                resultado_servico = await extrator.extrair(
                    tenant_id=tenant_id,
                    data_inicio=config.data_inicio,
                    data_fim=config.data_fim,
                    cnpjs=config.cnpjs,
                    ufs=config.ufs,
                    incremental=config.modo_incremental,
                )

            resultado_servico.status = StatusExtracao.CONCLUIDA

        except asyncio.TimeoutError:
            resultado_servico.status = StatusExtracao.FALHA
            resultado_servico.erros.append("Timeout na extração")
            logger.error(f"Timeout na extração: {servico.value}")

        except Exception as e:
            resultado_servico.status = StatusExtracao.FALHA
            resultado_servico.erros.append(str(e))
            logger.error(f"Erro na extração {servico.value}: {e}")

        finally:
            resultado_servico.fim = datetime.utcnow()
            resultado.resultados_servicos[servico.value] = resultado_servico

        return resultado_servico

    async def _extrair_generico(
        self,
        tenant_id: UUID,
        servico: TipoServico,
        config: ConfiguracaoExtracao
    ) -> ResultadoServico:
        """Extração genérica quando não há extrator específico."""
        resultado = ResultadoServico(
            servico=servico,
            status=StatusExtracao.EM_ANDAMENTO,
            inicio=datetime.utcnow(),
        )

        # Importar extratores específicos dinamicamente
        # SEFAZ - Documentos Fiscais
        if servico == TipoServico.SEFAZ_NFE:
            from .sefaz.nfe_extractor import ExtratorNFe
            extrator = ExtratorNFe(self.credentials, self.comutador)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.ufs, config.modo_incremental
            )

        elif servico == TipoServico.SEFAZ_CTE:
            from .sefaz.cte_extractor import ExtratorCTe
            extrator = ExtratorCTe(self.credentials, self.comutador)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.ufs, config.modo_incremental
            )

        elif servico == TipoServico.SEFAZ_MDFE:
            from .sefaz.mdfe_extractor import ExtratorMDFe
            extrator = ExtratorMDFe(self.credentials, self.comutador)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.ufs, config.modo_incremental
            )

        elif servico == TipoServico.SEFAZ_AM:
            from .sefaz_am.sefaz_am_extractor import ExtratorSEFAZAM
            extrator = ExtratorSEFAZAM(self.credentials, self.comutador)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.ufs, config.modo_incremental
            )

        # Trabalhista
        elif servico == TipoServico.ESOCIAL:
            from .esocial.esocial_extractor import ExtratoreSocial
            extrator = ExtratoreSocial(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.FGTS_DIGITAL:
            from .fgts.fgts_extractor import ExtratorFGTS
            extrator = ExtratorFGTS(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        # NFS-e
        elif servico == TipoServico.NFSE_MANAUS:
            from .nfse.manaus_extractor import ExtratorNFSeManaus
            extrator = ExtratorNFSeManaus(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.NFSE_NACIONAL:
            from .nfse.nfse_nacional_extractor import ExtratorNFSeNacional
            extrator = ExtratorNFSeNacional(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        # Receita Federal
        elif servico == TipoServico.RECEITA_FEDERAL:
            from .receita_federal.rfb_extractor import ExtratorRFB
            extrator = ExtratorRFB(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.DCTFWEB:
            from .receita_federal.dctfweb_extractor import ExtratorDCTFWeb
            extrator = ExtratorDCTFWeb(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.EFD_REINF:
            from .receita_federal.efd_reinf_extractor import ExtratorEFDReinf
            extrator = ExtratorEFDReinf(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.ECAC:
            from .receita_federal.ecac_extractor import ExtratorECAC
            extrator = ExtratorECAC(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.SIMPLES_NACIONAL:
            from .receita_federal.simples_nacional_extractor import ExtratorSimplesNacional
            extrator = ExtratorSimplesNacional(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        # SPED
        elif servico == TipoServico.SPED_FISCAL:
            from .sped.sped_fiscal_extractor import ExtratorSPEDFiscal
            extrator = ExtratorSPEDFiscal(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        elif servico == TipoServico.SPED_CONTABIL:
            from .sped.sped_contabil_extractor import ExtratorSPEDContabil
            extrator = ExtratorSPEDContabil(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        # Gov.br
        elif servico == TipoServico.GOVBR:
            from .govbr.govbr_extractor import ExtratorGovBR
            extrator = ExtratorGovBR(self.credentials)
            resultado = await extrator.extrair(
                tenant_id, config.data_inicio, config.data_fim,
                config.cnpjs, config.modo_incremental
            )

        else:
            resultado.status = StatusExtracao.FALHA
            resultado.erros.append(f"Extrator não implementado: {servico.value}")

        return resultado

    def _calcular_totais(self, resultado: ResultadoExtracao):
        """Calcula totais a partir dos resultados de serviços."""
        for res_servico in resultado.resultados_servicos.values():
            resultado.total_documentos += res_servico.documentos_processados
            resultado.total_novos += res_servico.documentos_novos
            resultado.total_atualizados += res_servico.documentos_atualizados
            resultado.total_erros += res_servico.documentos_erro

    async def _registrar_conclusao(
        self,
        resultado: ResultadoExtracao,
        usuario_id: Optional[UUID]
    ):
        """Registra conclusão da extração."""
        duracao = (resultado.fim - resultado.inicio).total_seconds()

        # Auditoria
        await self.audit.registrar(AuditEvent(
            tenant_id=resultado.tenant_id,
            usuario_id=usuario_id,
            tipo=TipoEvento.SINCRONIZACAO,
            recurso="extracao_governamental",
            recurso_id=str(resultado.id),
            acao=f"Extração {resultado.status.value}",
            sucesso=resultado.status in [
                StatusExtracao.CONCLUIDA,
                StatusExtracao.CONCLUIDA_PARCIAL,
            ],
            metadata={
                "duracao_segundos": duracao,
                "total_documentos": resultado.total_documentos,
                "total_erros": resultado.total_erros,
            },
        ))

        # Evento de sistema
        await self.events.publicar(EventoSincronizacao(
            tipo_evento=TipoEventoSistema.SYNC_CONCLUIDA if resultado.status == StatusExtracao.CONCLUIDA
            else TipoEventoSistema.SYNC_FALHA,
            tenant_id=resultado.tenant_id,
            servico="extracao_completa",
            registros_processados=resultado.total_documentos,
            registros_novos=resultado.total_novos,
            registros_atualizados=resultado.total_atualizados,
            registros_erro=resultado.total_erros,
            duracao_segundos=duracao,
            erro=resultado.erros[0] if resultado.erros else None,
        ))

        logger.info(
            f"Extração concluída: {resultado.id} - "
            f"Status: {resultado.status.value} - "
            f"Docs: {resultado.total_documentos} - "
            f"Erros: {resultado.total_erros} - "
            f"Duração: {duracao:.1f}s"
        )

    def _mapear_tipo_credencial(self, servico: TipoServico) -> Optional[TipoCredencial]:
        """Mapeia tipo de serviço para tipo de credencial."""
        mapeamento = {
            # SEFAZ
            TipoServico.SEFAZ_NFE: TipoCredencial.SEFAZ_NFE,
            TipoServico.SEFAZ_CTE: TipoCredencial.SEFAZ_CTE,
            TipoServico.SEFAZ_MDFE: TipoCredencial.SEFAZ_MDFE,
            TipoServico.SEFAZ_AM: TipoCredencial.SEFAZ_NFE,

            # Trabalhista
            TipoServico.ESOCIAL: TipoCredencial.ESOCIAL,
            TipoServico.FGTS_DIGITAL: TipoCredencial.FGTS_DIGITAL,

            # NFS-e
            TipoServico.NFSE_MANAUS: TipoCredencial.NFSE_MUNICIPAL,
            TipoServico.NFSE_NACIONAL: TipoCredencial.NFSE_NACIONAL,

            # Receita Federal
            TipoServico.RECEITA_FEDERAL: TipoCredencial.RECEITA_FEDERAL,
            TipoServico.DCTFWEB: TipoCredencial.RECEITA_FEDERAL,
            TipoServico.EFD_REINF: TipoCredencial.RECEITA_FEDERAL,
            TipoServico.ECAC: TipoCredencial.RECEITA_FEDERAL,
            TipoServico.SIMPLES_NACIONAL: TipoCredencial.RECEITA_FEDERAL,

            # SPED
            TipoServico.SPED_FISCAL: TipoCredencial.SPED,
            TipoServico.SPED_CONTABIL: TipoCredencial.SPED,

            # Gov.br
            TipoServico.GOVBR: TipoCredencial.RECEITA_FEDERAL,
        }
        return mapeamento.get(servico)

    async def obter_status_extracao(self, extracao_id: UUID) -> Optional[Dict]:
        """Obtém status de uma extração em andamento."""
        # TODO: Implementar busca em cache/banco
        pass

    async def cancelar_extracao(self, extracao_id: UUID) -> bool:
        """Cancela uma extração em andamento."""
        # TODO: Implementar cancelamento
        pass


# Instância singleton
_orchestrator_instance: Optional[OrquestradorExtracao] = None


def get_orchestrator() -> OrquestradorExtracao:
    """Obtém instância do orquestrador."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrquestradorExtracao()
    return _orchestrator_instance
