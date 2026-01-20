"""
Controller de Ocorrencias - Endpoints FastAPI.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from core.database import get_db
from modules.operacional.occurrences.models import (
    OccurrenceCategory,
    OccurrencePriority,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from modules.operacional.occurrences.schemas import (
    OccurrenceCreate,
    OccurrenceUpdate,
    OccurrenceResponse,
    OccurrenceListResponse,
    OccurrenceSummaryResponse,
    OccurrenceFilter,
    AttachmentCreate,
    AttachmentResponse,
    CommentCreate,
    CommentResponse,
    EscalateRequest,
    ResolveRequest,
    ReopenRequest,
    DashboardStats,
    SLABreachItem,
    PendingOccurrenceItem,
    CategoryConfigCreate,
    CategoryConfigUpdate,
    CategoryConfigResponse,
)
from modules.operacional.occurrences.services import (
    OccurrenceService,
    OccurrenceNotFoundError,
    OccurrenceValidationError,
    OccurrenceAIAnalyzer,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_occurrence_service(db: Session = Depends(get_db)) -> OccurrenceService:
    """Dependency para obter OccurrenceService."""
    return OccurrenceService(db)


def get_ai_analyzer(db: Session = Depends(get_db)) -> OccurrenceAIAnalyzer:
    """Dependency para obter OccurrenceAIAnalyzer."""
    return OccurrenceAIAnalyzer(db)


# ============================================================
# OCCURRENCE CRUD ENDPOINTS
# ============================================================


@router.post(
    "/",
    response_model=OccurrenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar ocorrencia",
    description="Cria uma nova ocorrencia operacional.",
)
async def create_occurrence(
    data: OccurrenceCreate,
    service: OccurrenceService = Depends(get_occurrence_service),
    ai_analyzer: OccurrenceAIAnalyzer = Depends(get_ai_analyzer),
) -> OccurrenceResponse:
    """Cria uma nova ocorrencia.

    Args:
        data: Dados da ocorrencia.
        service: Servico de ocorrencias.
        ai_analyzer: Analisador de IA.

    Returns:
        Ocorrencia criada.
    """
    try:
        # Classificar com IA
        classification = ai_analyzer.classify(
            title=data.title,
            description=data.description,
            tenant_id=str(data.tenant_id),
        )

        occurrence = service.create(data)

        # Adicionar classificacao e recomendacoes de IA
        recommendations = ai_analyzer.generate_recommendations(occurrence)
        occurrence.set_ai_classification(
            classification=classification.to_dict(),
            recommendations=recommendations,
        )

        logger.info(f"Ocorrencia criada via API: {occurrence.code}")

        return OccurrenceResponse.model_validate(occurrence)

    except OccurrenceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao criar ocorrencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar ocorrencia",
        )


@router.get(
    "/",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias",
    description="Lista ocorrencias com filtros e paginacao.",
)
async def list_occurrences(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    post_id: Optional[UUID] = Query(None, description="Filtrar por posto"),
    client_id: Optional[UUID] = Query(None, description="Filtrar por cliente"),
    category: Optional[OccurrenceCategory] = Query(None, description="Filtrar por categoria"),
    severity: Optional[OccurrenceSeverity] = Query(None, description="Filtrar por severidade"),
    status_filter: Optional[OccurrenceStatus] = Query(None, alias="status", description="Filtrar por status"),
    priority: Optional[OccurrencePriority] = Query(None, description="Filtrar por prioridade"),
    escalated: Optional[bool] = Query(None, description="Filtrar escaladas"),
    sla_breached: Optional[bool] = Query(None, description="Filtrar SLA violado"),
    search: Optional[str] = Query(None, min_length=2, description="Busca por texto"),
    created_at_start: Optional[datetime] = Query(None, description="Data inicial"),
    created_at_end: Optional[datetime] = Query(None, description="Data final"),
    service: OccurrenceService = Depends(get_occurrence_service),
) -> OccurrenceListResponse:
    """Lista ocorrencias com filtros.

    Args:
        Varios parametros de filtro.
        service: Servico de ocorrencias.

    Returns:
        Lista paginada de ocorrencias.
    """
    filters = OccurrenceFilter(
        post_id=post_id,
        client_id=client_id,
        category=category,
        severity=severity,
        status=status_filter,
        priority=priority,
        escalated=escalated,
        sla_breached=sla_breached,
        search=search,
        created_at_start=created_at_start,
        created_at_end=created_at_end,
    )

    occurrences, total = service.list(str(tenant_id), skip, limit, filters)

    pages = (total + limit - 1) // limit if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1

    return OccurrenceListResponse(
        items=[OccurrenceResponse.model_validate(occ) for occ in occurrences],
        total=total,
        page=page,
        page_size=limit,
        pages=pages,
    )


@router.get(
    "/{occurrence_id}",
    response_model=OccurrenceResponse,
    summary="Buscar ocorrencia",
    description="Busca uma ocorrencia por ID.",
)
async def get_occurrence(
    occurrence_id: UUID,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> OccurrenceResponse:
    """Busca ocorrencia por ID.

    Args:
        occurrence_id: ID da ocorrencia.
        service: Servico de ocorrencias.

    Returns:
        Ocorrencia encontrada.
    """
    try:
        occurrence = service.get_by_id(str(occurrence_id))
        return OccurrenceResponse.model_validate(occurrence)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{occurrence_id}",
    response_model=OccurrenceResponse,
    summary="Atualizar ocorrencia",
    description="Atualiza uma ocorrencia existente.",
)
async def update_occurrence(
    occurrence_id: UUID,
    data: OccurrenceUpdate,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> OccurrenceResponse:
    """Atualiza uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        data: Dados para atualizacao.
        service: Servico de ocorrencias.

    Returns:
        Ocorrencia atualizada.
    """
    try:
        occurrence = service.update(str(occurrence_id), data)
        return OccurrenceResponse.model_validate(occurrence)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except OccurrenceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{occurrence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover ocorrencia",
    description="Remove uma ocorrencia (soft delete).",
)
async def delete_occurrence(
    occurrence_id: UUID,
    service: OccurrenceService = Depends(get_occurrence_service),
):
    """Remove uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        service: Servico de ocorrencias.
    """
    try:
        service.delete(str(occurrence_id))
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# ATTACHMENT ENDPOINTS
# ============================================================


@router.post(
    "/{occurrence_id}/anexos",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar anexo",
    description="Adiciona um anexo a uma ocorrencia.",
)
async def add_attachment(
    occurrence_id: UUID,
    data: AttachmentCreate,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> AttachmentResponse:
    """Adiciona anexo a uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        data: Dados do anexo.
        service: Servico de ocorrencias.

    Returns:
        Anexo criado.
    """
    try:
        attachment = service.add_attachment(str(occurrence_id), data)
        return AttachmentResponse.model_validate(attachment)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{occurrence_id}/anexos",
    response_model=List[AttachmentResponse],
    summary="Listar anexos",
    description="Lista anexos de uma ocorrencia.",
)
async def get_attachments(
    occurrence_id: UUID,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> List[AttachmentResponse]:
    """Lista anexos de uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        service: Servico de ocorrencias.

    Returns:
        Lista de anexos.
    """
    try:
        attachments = service.get_attachments(str(occurrence_id))
        return [AttachmentResponse.model_validate(a) for a in attachments]
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# COMMENT ENDPOINTS
# ============================================================


@router.post(
    "/{occurrence_id}/comentarios",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar comentario",
    description="Adiciona um comentario a uma ocorrencia.",
)
async def add_comment(
    occurrence_id: UUID,
    data: CommentCreate,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> CommentResponse:
    """Adiciona comentario a uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        data: Dados do comentario.
        service: Servico de ocorrencias.

    Returns:
        Comentario criado.
    """
    try:
        comment = service.add_comment(str(occurrence_id), data)
        return CommentResponse.model_validate(comment)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{occurrence_id}/comentarios",
    response_model=List[CommentResponse],
    summary="Listar comentarios",
    description="Lista comentarios de uma ocorrencia.",
)
async def get_comments(
    occurrence_id: UUID,
    include_internal: bool = Query(True, description="Incluir comentarios internos"),
    service: OccurrenceService = Depends(get_occurrence_service),
) -> List[CommentResponse]:
    """Lista comentarios de uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        include_internal: Se deve incluir comentarios internos.
        service: Servico de ocorrencias.

    Returns:
        Lista de comentarios.
    """
    try:
        comments = service.get_comments(str(occurrence_id), include_internal)
        return [CommentResponse.model_validate(c) for c in comments]
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================
# WORKFLOW ENDPOINTS
# ============================================================


@router.post(
    "/{occurrence_id}/escalar",
    response_model=OccurrenceResponse,
    summary="Escalar ocorrencia",
    description="Escala uma ocorrencia para outro usuario.",
)
async def escalate_occurrence(
    occurrence_id: UUID,
    data: EscalateRequest,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> OccurrenceResponse:
    """Escala uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        data: Dados de escalacao.
        service: Servico de ocorrencias.

    Returns:
        Ocorrencia escalada.
    """
    try:
        occurrence = service.escalate(str(occurrence_id), data)
        return OccurrenceResponse.model_validate(occurrence)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except OccurrenceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{occurrence_id}/resolver",
    response_model=OccurrenceResponse,
    summary="Resolver ocorrencia",
    description="Resolve uma ocorrencia.",
)
async def resolve_occurrence(
    occurrence_id: UUID,
    data: ResolveRequest,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> OccurrenceResponse:
    """Resolve uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        data: Dados de resolucao.
        service: Servico de ocorrencias.

    Returns:
        Ocorrencia resolvida.
    """
    try:
        occurrence = service.resolve(str(occurrence_id), data)
        return OccurrenceResponse.model_validate(occurrence)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except OccurrenceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{occurrence_id}/reabrir",
    response_model=OccurrenceResponse,
    summary="Reabrir ocorrencia",
    description="Reabre uma ocorrencia resolvida ou arquivada.",
)
async def reopen_occurrence(
    occurrence_id: UUID,
    data: Optional[ReopenRequest] = None,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> OccurrenceResponse:
    """Reabre uma ocorrencia.

    Args:
        occurrence_id: ID da ocorrencia.
        data: Dados de reabertura.
        service: Servico de ocorrencias.

    Returns:
        Ocorrencia reaberta.
    """
    try:
        occurrence = service.reopen(str(occurrence_id), data)
        return OccurrenceResponse.model_validate(occurrence)
    except OccurrenceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except OccurrenceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================
# DASHBOARD ENDPOINTS
# ============================================================


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Dashboard de ocorrencias",
    description="Retorna estatisticas do dashboard.",
)
async def get_dashboard(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    service: OccurrenceService = Depends(get_occurrence_service),
) -> DashboardStats:
    """Retorna estatisticas do dashboard.

    Args:
        tenant_id: ID do tenant.
        start_date: Data inicial.
        end_date: Data final.
        service: Servico de ocorrencias.

    Returns:
        Estatisticas do dashboard.
    """
    return service.get_dashboard_stats(str(tenant_id), start_date, end_date)


@router.get(
    "/pendentes",
    response_model=List[PendingOccurrenceItem],
    summary="Ocorrencias pendentes",
    description="Lista ocorrencias pendentes do usuario.",
)
async def get_pending_occurrences(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    user_id: UUID = Query(..., description="ID do usuario"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: OccurrenceService = Depends(get_occurrence_service),
) -> List[PendingOccurrenceItem]:
    """Lista ocorrencias pendentes do usuario.

    Args:
        tenant_id: ID do tenant.
        user_id: ID do usuario.
        skip: Registros a pular.
        limit: Limite de registros.
        service: Servico de ocorrencias.

    Returns:
        Lista de ocorrencias pendentes.
    """
    occurrences = service.get_pending_by_user(
        str(user_id), str(tenant_id), skip, limit
    )
    return [
        PendingOccurrenceItem(
            id=occ.id,
            code=occ.code,
            title=occ.title,
            category=occ.category,
            severity=occ.severity,
            priority=occ.priority,
            status=occ.status,
            created_at=occ.created_at,
            sla_deadline=occ.sla_deadline,
            sla_breached=occ.sla_breached,
        )
        for occ in occurrences
    ]


@router.get(
    "/sla-vencendo",
    response_model=List[SLABreachItem],
    summary="SLA vencendo",
    description="Lista ocorrencias com SLA vencendo.",
)
async def get_sla_breaching(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    hours_threshold: int = Query(4, ge=1, le=48, description="Horas ate o vencimento"),
    service: OccurrenceService = Depends(get_occurrence_service),
) -> List[SLABreachItem]:
    """Lista ocorrencias com SLA vencendo.

    Args:
        tenant_id: ID do tenant.
        hours_threshold: Horas ate o vencimento.
        service: Servico de ocorrencias.

    Returns:
        Lista de ocorrencias com SLA em risco.
    """
    occurrences = service.get_sla_breaching(str(tenant_id), hours_threshold)

    result = []
    now = datetime.utcnow()
    for occ in occurrences:
        if occ.sla_deadline:
            hours_remaining = (occ.sla_deadline - now).total_seconds() / 3600
            result.append(
                SLABreachItem(
                    id=occ.id,
                    code=occ.code,
                    title=occ.title,
                    severity=occ.severity,
                    priority=occ.priority,
                    sla_deadline=occ.sla_deadline,
                    hours_remaining=round(hours_remaining, 1),
                    created_at=occ.created_at,
                )
            )

    return result


# ============================================================
# CATEGORY CONFIG ENDPOINTS
# ============================================================


@router.get(
    "/categorias",
    response_model=List[CategoryConfigResponse],
    summary="Listar categorias",
    description="Lista configuracoes de categorias do tenant.",
)
async def list_categories(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    service: OccurrenceService = Depends(get_occurrence_service),
) -> List[CategoryConfigResponse]:
    """Lista configuracoes de categorias.

    Args:
        tenant_id: ID do tenant.
        service: Servico de ocorrencias.

    Returns:
        Lista de configuracoes.
    """
    configs = service.get_category_configs(str(tenant_id))
    return [CategoryConfigResponse.model_validate(c) for c in configs]


@router.post(
    "/categorias",
    response_model=CategoryConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
    description="Cria uma nova configuracao de categoria.",
)
async def create_category(
    data: CategoryConfigCreate,
    service: OccurrenceService = Depends(get_occurrence_service),
) -> CategoryConfigResponse:
    """Cria configuracao de categoria.

    Args:
        data: Dados da configuracao.
        service: Servico de ocorrencias.

    Returns:
        Configuracao criada.
    """
    try:
        config = service.create_category_config(data)
        return CategoryConfigResponse.model_validate(config)
    except OccurrenceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================
# AI ENDPOINTS
# ============================================================


@router.post(
    "/classificar",
    summary="Classificar texto com IA",
    description="Classifica titulo e descricao usando IA.",
)
async def classify_text(
    title: str = Query(..., min_length=5, description="Titulo"),
    description: str = Query(..., min_length=10, description="Descricao"),
    tenant_id: Optional[UUID] = Query(None, description="ID do tenant"),
    ai_analyzer: OccurrenceAIAnalyzer = Depends(get_ai_analyzer),
) -> dict:
    """Classifica texto com IA.

    Args:
        title: Titulo da ocorrencia.
        description: Descricao.
        tenant_id: ID do tenant para buscar similares.
        ai_analyzer: Analisador de IA.

    Returns:
        Resultado da classificacao.
    """
    tenant_str = str(tenant_id) if tenant_id else None
    result = ai_analyzer.classify(title, description, tenant_str)
    return result.to_dict()


@router.get(
    "/analise-padroes",
    summary="Analise de padroes",
    description="Analisa padroes de ocorrencias do periodo.",
)
async def analyze_patterns(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    days: int = Query(30, ge=7, le=365, description="Dias para analise"),
    ai_analyzer: OccurrenceAIAnalyzer = Depends(get_ai_analyzer),
) -> dict:
    """Analisa padroes de ocorrencias.

    Args:
        tenant_id: ID do tenant.
        days: Numero de dias para analise.
        ai_analyzer: Analisador de IA.

    Returns:
        Analise de padroes.
    """
    analysis = ai_analyzer.analyze_patterns(str(tenant_id), days)
    return {
        "period_start": analysis.period_start.isoformat(),
        "period_end": analysis.period_end.isoformat(),
        "total_occurrences": analysis.total_occurrences,
        "trends": analysis.trends,
        "hotspots": analysis.hotspots,
        "recurring_issues": analysis.recurring_issues,
        "employee_patterns": analysis.employee_patterns,
        "recommendations": analysis.recommendations,
    }
