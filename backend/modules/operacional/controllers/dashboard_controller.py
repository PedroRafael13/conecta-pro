"""
Controller de Dashboard Unificado do Operacional.

Fornece endpoints para:
- Dashboard consolidado (funcionários + diaristas)
- Métricas de ocupação
- Alocação de diaristas a postos
- Sugestões de alocação
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db
from modules.operacional.services.integration_service import (
    IntegrationService,
    get_integration_service,
)

router = APIRouter()


# =============================================================================
# SCHEMAS
# =============================================================================

class AlocarDiaristaPostoRequest(BaseModel):
    """Request para alocar diarista a um posto."""
    diarista_id: UUID
    post_id: UUID
    data_inicio: date
    data_fim: Optional[date] = None
    shift_id: Optional[UUID] = None
    cliente_id: Optional[UUID] = None
    contrato_id: Optional[UUID] = None
    observacoes: Optional[str] = Field(None, max_length=500)


class DesalocarDiaristaRequest(BaseModel):
    """Request para desalocar diarista."""
    motivo: Optional[str] = Field(None, max_length=500)


class DashboardResponse(BaseModel):
    """Response do dashboard unificado."""
    data_referencia: str
    postos: Dict[str, Any]
    escalas: Dict[str, Any]
    turnos: Dict[str, Any]
    funcionarios: Dict[str, Any]
    diaristas: Dict[str, Any]
    ocupacao: Dict[str, Any]
    alertas: List[Dict[str, Any]]


class MetricasPeriodoResponse(BaseModel):
    """Response das métricas de período."""
    periodo: Dict[str, Any]
    diaristas: Dict[str, Any]
    funcionarios: Dict[str, Any]
    consolidado: Dict[str, Any]


class OcupacaoPostoResponse(BaseModel):
    """Response da ocupação de um posto."""
    posto_id: str
    posto_nome: str
    posto_tipo: str
    funcionarios_alocados: int
    diaristas_alocados: int
    total_alocados: int
    status: str
    detalhes: Dict[str, Any]


class SugestaoDiaristaResponse(BaseModel):
    """Response de sugestão de diarista."""
    diarist_id: str
    nome: str
    score: int
    motivos: List[str]
    avaliacao: Optional[float]
    total_servicos: int


# =============================================================================
# ENDPOINTS - DASHBOARD
# =============================================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Dashboard unificado",
    description="Retorna métricas consolidadas de funcionários fixos e diaristas"
)
async def get_dashboard(
    data: Optional[date] = Query(None, description="Data de referência (default: hoje)"),
    cliente_id: Optional[UUID] = Query(None, description="Filtrar por cliente"),
    db: Session = Depends(get_db),
):
    """
    Retorna dashboard unificado do operacional.

    Inclui:
    - Status de postos
    - Escalas e turnos
    - Funcionários alocados
    - Diaristas em serviço
    - Taxa de ocupação
    - Alertas automáticos
    """
    service = get_integration_service(db)

    try:
        dashboard = service.get_dashboard_unificado(
            data_referencia=data,
            cliente_id=cliente_id,
        )
        return dashboard
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar dashboard: {str(e)}"
        )


@router.get(
    "/metricas",
    response_model=MetricasPeriodoResponse,
    summary="Métricas de período",
    description="Retorna métricas consolidadas para um período específico"
)
async def get_metricas_periodo(
    data_inicio: date = Query(..., description="Data inicial"),
    data_fim: date = Query(..., description="Data final"),
    cliente_id: Optional[UUID] = Query(None, description="Filtrar por cliente"),
    db: Session = Depends(get_db),
):
    """
    Retorna métricas de um período específico.

    Inclui:
    - Schedules de diaristas realizados/cancelados/faltas
    - Horas trabalhadas
    - Turnos de funcionários
    - Taxa de comparecimento
    """
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data fim deve ser maior ou igual a data início"
        )

    service = get_integration_service(db)

    try:
        metricas = service.get_metricas_periodo(
            data_inicio=data_inicio,
            data_fim=data_fim,
            cliente_id=cliente_id,
        )
        return metricas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular métricas: {str(e)}"
        )


# =============================================================================
# ENDPOINTS - OCUPAÇÃO DE POSTOS
# =============================================================================

@router.get(
    "/ocupacao",
    response_model=List[OcupacaoPostoResponse],
    summary="Ocupação de postos",
    description="Retorna status de ocupação de cada posto ativo"
)
async def get_ocupacao_postos(
    data: Optional[date] = Query(None, description="Data de referência (default: hoje)"),
    db: Session = Depends(get_db),
):
    """
    Retorna ocupação detalhada de cada posto.

    Mostra para cada posto:
    - Funcionários fixos alocados
    - Diaristas alocados
    - Status (coberto/descoberto)
    """
    service = get_integration_service(db)

    try:
        ocupacao = service.get_ocupacao_postos(data_referencia=data)
        return ocupacao
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar ocupação: {str(e)}"
        )


# =============================================================================
# ENDPOINTS - ALOCAÇÃO DE DIARISTAS
# =============================================================================

@router.post(
    "/alocar-diarista",
    summary="Alocar diarista a posto",
    description="Aloca um diarista a um posto de trabalho"
)
async def alocar_diarista_posto(
    request: AlocarDiaristaPostoRequest,
    db: Session = Depends(get_db),
):
    """
    Aloca um diarista a um posto de trabalho.

    Validações:
    - Diarista deve estar ativo e disponível
    - Posto deve estar ativo
    - Não pode haver conflito de datas
    """
    service = get_integration_service(db)

    try:
        assignment = service.alocar_diarista_posto(
            diarista_id=request.diarista_id,
            post_id=request.post_id,
            data_inicio=request.data_inicio,
            data_fim=request.data_fim,
            shift_id=request.shift_id,
            cliente_id=request.cliente_id,
            contrato_id=request.contrato_id,
            observacoes=request.observacoes,
        )

        return {
            "success": True,
            "message": "Diarista alocado com sucesso",
            "assignment_id": str(assignment.id),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alocar diarista: {str(e)}"
        )


@router.post(
    "/desalocar-diarista/{assignment_id}",
    summary="Desalocar diarista",
    description="Remove alocação de diarista de um posto"
)
async def desalocar_diarista(
    assignment_id: UUID,
    request: DesalocarDiaristaRequest,
    db: Session = Depends(get_db),
):
    """
    Remove alocação de diarista de um posto.

    Finaliza o assignment e libera o diarista.
    """
    service = get_integration_service(db)

    try:
        assignment = service.desalocar_diarista_posto(
            assignment_id=assignment_id,
            motivo=request.motivo,
        )

        return {
            "success": True,
            "message": "Diarista desalocado com sucesso",
            "assignment_id": str(assignment.id),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao desalocar diarista: {str(e)}"
        )


# =============================================================================
# ENDPOINTS - SUGESTÕES
# =============================================================================

@router.get(
    "/sugerir-diarista/{post_id}",
    response_model=List[SugestaoDiaristaResponse],
    summary="Sugerir diarista para posto",
    description="Retorna diaristas sugeridos para cobrir um posto"
)
async def sugerir_diarista_posto(
    post_id: UUID,
    data: date = Query(..., description="Data desejada para cobertura"),
    habilidades: Optional[str] = Query(
        None,
        description="Habilidades requeridas (separadas por vírgula)"
    ),
    db: Session = Depends(get_db),
):
    """
    Sugere diaristas disponíveis para um posto.

    Ordena por:
    - Score de adequação
    - Habilidades compatíveis
    - Avaliação média
    """
    service = get_integration_service(db)

    habilidades_lista = None
    if habilidades:
        habilidades_lista = [h.strip() for h in habilidades.split(",")]

    try:
        sugestoes = service.sugerir_diarista_posto(
            post_id=post_id,
            data=data,
            habilidades_requeridas=habilidades_lista,
        )
        return sugestoes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao sugerir diaristas: {str(e)}"
        )


# =============================================================================
# ENDPOINTS - RELATÓRIOS RÁPIDOS
# =============================================================================

@router.get(
    "/resumo-dia",
    summary="Resumo do dia",
    description="Retorna resumo executivo do dia atual"
)
async def get_resumo_dia(
    db: Session = Depends(get_db),
):
    """
    Retorna resumo executivo do dia atual.

    Inclui principais métricas e alertas.
    """
    service = get_integration_service(db)

    try:
        dashboard = service.get_dashboard_unificado()

        return {
            "data": dashboard["data_referencia"],
            "resumo": {
                "postos_ativos": dashboard["postos"]["ativos"],
                "turnos_hoje": dashboard["turnos"]["hoje"],
                "turnos_em_andamento": dashboard["turnos"]["em_andamento"],
                "diaristas_em_servico": dashboard["diaristas"]["em_servico"],
                "taxa_ocupacao": dashboard["ocupacao"]["taxa_ocupacao_percentual"],
            },
            "alertas_criticos": [
                a for a in dashboard["alertas"] if a["tipo"] == "error"
            ],
            "total_alertas": len(dashboard["alertas"]),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar resumo: {str(e)}"
        )


@router.get(
    "/kpis",
    summary="KPIs operacionais",
    description="Retorna KPIs principais do operacional"
)
async def get_kpis(
    periodo_dias: int = Query(30, ge=7, le=365, description="Período em dias"),
    db: Session = Depends(get_db),
):
    """
    Retorna KPIs operacionais.

    Métricas calculadas para o período especificado.
    """
    service = get_integration_service(db)

    data_fim = date.today()
    data_inicio = data_fim - __import__("datetime").timedelta(days=periodo_dias)

    try:
        metricas = service.get_metricas_periodo(data_inicio, data_fim)
        dashboard = service.get_dashboard_unificado()

        return {
            "periodo": metricas["periodo"],
            "kpis": {
                "taxa_ocupacao_atual": dashboard["ocupacao"]["taxa_ocupacao_percentual"],
                "taxa_comparecimento_diaristas": metricas["diaristas"]["taxa_comparecimento"],
                "taxa_conclusao_turnos": metricas["funcionarios"]["taxa_conclusao"],
                "total_horas_diaristas": metricas["diaristas"]["horas_trabalhadas"],
                "total_servicos_realizados": metricas["consolidado"]["servicos_concluidos"],
            },
            "tendencia": {
                "comparado_periodo_anterior": "Não calculado",  # TODO: Implementar comparação
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular KPIs: {str(e)}"
        )
