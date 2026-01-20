"""Controller para Occurrence."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.auth.dependencies import get_current_user, require_roles
from modules.occurrences.models.occurrence import OccurrenceStatus
from modules.occurrences.schemas.occurrence import (
    OccurrenceAssign,
    OccurrenceCreate,
    OccurrenceEscalate,
    OccurrenceFilter,
    OccurrenceListResponse,
    OccurrenceRate,
    OccurrenceResolve,
    OccurrenceResponse,
    OccurrenceStats,
    OccurrenceUpdate,
)
from modules.occurrences.services import ClassificationAIService, OccurrenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/occurrences", tags=["Occurrences"])


async def get_occurrence_service(
    session: AsyncSession = Depends(get_async_session),
) -> OccurrenceService:
    """Dependency para OccurrenceService."""
    return OccurrenceService(session)


async def get_classification_service(
    session: AsyncSession = Depends(get_async_session),
) -> ClassificationAIService:
    """Dependency para ClassificationAIService."""
    return ClassificationAIService(session)


@router.post(
    "/",
    response_model=OccurrenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar ocorrencia",
)
async def create_occurrence(
    data: OccurrenceCreate,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Cria uma nova ocorrencia."""
    try:
        # Define reporter se nao informado
        if not data.reporter_id:
            data.reporter_id = current_user.get("sub")
        if not data.reporter_name:
            data.reporter_name = current_user.get("name", "Usuario")

        result = await service.create(data)
        logger.info(f"Ocorrencia {result.id} criada por {current_user.get('email')}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar ocorrencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar ocorrencia",
        )


@router.get(
    "/",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias",
)
async def list_occurrences(  # pylint: disable=too-many-locals
    condominium_id: Optional[str] = Query(None, description="ID do condominio"),
    category_id: Optional[str] = Query(None, description="ID da categoria"),
    occurrence_type: Optional[str] = Query(None, description="Tipo da ocorrencia"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status"),
    priority: Optional[str] = Query(None, description="Prioridade"),
    reporter_id: Optional[str] = Query(None, description="ID do reportador"),
    assigned_to_id: Optional[str] = Query(None, description="ID do responsavel"),
    is_anonymous: Optional[bool] = Query(None, description="Anonima"),
    is_escalated: Optional[bool] = Query(None, description="Escalonada"),
    page: int = Query(1, ge=1, description="Pagina"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por pagina"),
    order_by: str = Query("created_at", description="Campo de ordenacao"),
    order_desc: bool = Query(True, description="Ordem descendente"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias com filtros."""
    filters = OccurrenceFilter(
        condominium_id=condominium_id,
        category_id=category_id,
        type=occurrence_type,
        status=status_filter,
        priority=priority,
        reporter_id=reporter_id,
        assigned_to_id=assigned_to_id,
        is_anonymous=is_anonymous,
        is_escalated=is_escalated,
    )
    return await service.list(filters, page, page_size, order_by, order_desc)


@router.get(
    "/open",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias abertas",
)
async def list_open_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias abertas."""
    return await service.get_open(page, page_size)


@router.get(
    "/overdue",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias atrasadas",
)
async def list_overdue_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias atrasadas."""
    return await service.get_overdue(page, page_size)


@router.get(
    "/escalated",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias escalonadas",
)
async def list_escalated_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias escalonadas."""
    return await service.get_escalated(page, page_size)


@router.get(
    "/high-priority",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias de alta prioridade",
)
async def list_high_priority_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias de alta prioridade."""
    return await service.get_high_priority(page, page_size)


@router.get(
    "/unassigned",
    response_model=OccurrenceListResponse,
    summary="Listar ocorrencias nao atribuidas",
)
async def list_unassigned_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias nao atribuidas."""
    return await service.get_unassigned(page, page_size)


@router.get(
    "/stats",
    response_model=OccurrenceStats,
    summary="Estatisticas de ocorrencias",
)
async def get_occurrence_stats(
    condominium_id: Optional[str] = Query(None, description="ID do condominio"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceStats:
    """Retorna estatisticas de ocorrencias."""
    return await service.get_stats(condominium_id)


@router.get(
    "/my",
    response_model=OccurrenceListResponse,
    summary="Minhas ocorrencias",
)
async def list_my_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceListResponse:
    """Lista ocorrencias do usuario logado."""
    user_id = current_user.get("sub")
    return await service.get_by_reporter(user_id, page, page_size)


@router.get(
    "/assigned",
    response_model=OccurrenceListResponse,
    summary="Ocorrencias atribuidas a mim",
)
async def list_assigned_occurrences(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceListResponse:
    """Lista ocorrencias atribuidas ao usuario logado."""
    user_id = current_user.get("sub")
    return await service.get_by_assigned(user_id, page, page_size)


@router.get(
    "/condominium/{condominium_id}",
    response_model=OccurrenceListResponse,
    summary="Ocorrencias por condominio",
)
async def list_by_condominium(
    condominium_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceListResponse:
    """Lista ocorrencias de um condominio."""
    return await service.get_by_condominium(condominium_id, page, page_size)


@router.get(
    "/{occurrence_id}",
    response_model=OccurrenceResponse,
    summary="Buscar ocorrencia por ID",
)
async def get_occurrence(
    occurrence_id: UUID,
    include_relations: bool = Query(False, description="Incluir relacoes"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceResponse:
    """Busca ocorrencia por ID."""
    result = await service.get_by_id(occurrence_id, include_relations)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )

    # Incrementar visualizacoes
    await service.increment_views(occurrence_id)
    return result


@router.get(
    "/code/{code}",
    response_model=OccurrenceResponse,
    summary="Buscar ocorrencia por codigo",
)
async def get_occurrence_by_code(
    code: str,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceResponse:
    """Busca ocorrencia por codigo."""
    result = await service.get_by_code(code)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    return result


@router.put(
    "/{occurrence_id}",
    response_model=OccurrenceResponse,
    summary="Atualizar ocorrencia",
)
async def update_occurrence(
    occurrence_id: UUID,
    data: OccurrenceUpdate,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Atualiza uma ocorrencia."""
    result = await service.update(occurrence_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Ocorrencia {occurrence_id} atualizada por {current_user.get('email')}")
    return result


@router.delete(
    "/{occurrence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar ocorrencia",
)
async def delete_occurrence(
    occurrence_id: UUID,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> None:
    """Deleta uma ocorrencia."""
    result = await service.delete(occurrence_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Ocorrencia {occurrence_id} deletada por {current_user.get('email')}")


# ==================== WORKFLOW ====================


@router.post(
    "/{occurrence_id}/assign",
    response_model=OccurrenceResponse,
    summary="Atribuir responsavel",
)
async def assign_occurrence(
    occurrence_id: UUID,
    data: OccurrenceAssign,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Atribui responsavel a uma ocorrencia."""
    # Define quem esta atribuindo
    if not data.assigned_by_id:
        data.assigned_by_id = current_user.get("sub")
    if not data.assigned_by_name:
        data.assigned_by_name = current_user.get("name", "Usuario")

    result = await service.assign(occurrence_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(
        f"Ocorrencia {occurrence_id} atribuida a {data.assigned_to_name} "
        f"por {current_user.get('email')}"
    )
    return result


@router.post(
    "/{occurrence_id}/unassign",
    response_model=OccurrenceResponse,
    summary="Remover atribuicao",
)
async def unassign_occurrence(
    occurrence_id: UUID,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> OccurrenceResponse:
    """Remove atribuicao de responsavel."""
    result = await service.unassign(occurrence_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Atribuicao removida da ocorrencia {occurrence_id}")
    return result


@router.post(
    "/{occurrence_id}/resolve",
    response_model=OccurrenceResponse,
    summary="Resolver ocorrencia",
)
async def resolve_occurrence(
    occurrence_id: UUID,
    data: OccurrenceResolve,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Resolve uma ocorrencia."""
    # Define quem esta resolvendo
    if not data.resolved_by_id:
        data.resolved_by_id = current_user.get("sub")
    if not data.resolved_by_name:
        data.resolved_by_name = current_user.get("name", "Usuario")

    result = await service.resolve(occurrence_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Ocorrencia {occurrence_id} resolvida por {current_user.get('email')}")
    return result


@router.post(
    "/{occurrence_id}/escalate",
    response_model=OccurrenceResponse,
    summary="Escalonar ocorrencia",
)
async def escalate_occurrence(
    occurrence_id: UUID,
    data: OccurrenceEscalate,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Escalona uma ocorrencia."""
    result = await service.escalate(occurrence_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(
        f"Ocorrencia {occurrence_id} escalonada para {data.escalated_to_name} "
        f"por {current_user.get('email')}"
    )
    return result


@router.post(
    "/{occurrence_id}/status",
    response_model=OccurrenceResponse,
    summary="Alterar status",
)
async def change_occurrence_status(
    occurrence_id: UUID,
    new_status: OccurrenceStatus = Query(..., description="Novo status"),
    reason: Optional[str] = Query(None, description="Motivo da alteracao"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Altera status de uma ocorrencia."""
    result = await service.change_status(occurrence_id, new_status, reason)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(
        f"Status da ocorrencia {occurrence_id} alterado para {new_status} "
        f"por {current_user.get('email')}"
    )
    return result


@router.post(
    "/{occurrence_id}/reopen",
    response_model=OccurrenceResponse,
    summary="Reabrir ocorrencia",
)
async def reopen_occurrence(
    occurrence_id: UUID,
    reason: Optional[str] = Query(None, description="Motivo da reabertura"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Reabre uma ocorrencia."""
    reopened_by = current_user.get("name", "Usuario")
    result = await service.reopen(occurrence_id, reason, reopened_by)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Ocorrencia {occurrence_id} reaberta por {current_user.get('email')}")
    return result


@router.post(
    "/{occurrence_id}/cancel",
    response_model=OccurrenceResponse,
    summary="Cancelar ocorrencia",
)
async def cancel_occurrence(
    occurrence_id: UUID,
    reason: Optional[str] = Query(None, description="Motivo do cancelamento"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Cancela uma ocorrencia."""
    cancelled_by = current_user.get("name", "Usuario")
    result = await service.cancel(occurrence_id, reason, cancelled_by)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Ocorrencia {occurrence_id} cancelada por {current_user.get('email')}")
    return result


@router.post(
    "/{occurrence_id}/archive",
    response_model=OccurrenceResponse,
    summary="Arquivar ocorrencia",
)
async def archive_occurrence(
    occurrence_id: UUID,
    reason: Optional[str] = Query(None, description="Motivo do arquivamento"),
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> OccurrenceResponse:
    """Arquiva uma ocorrencia."""
    result = await service.archive(occurrence_id, reason)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(f"Ocorrencia {occurrence_id} arquivada por {current_user.get('email')}")
    return result


@router.post(
    "/{occurrence_id}/rate",
    response_model=OccurrenceResponse,
    summary="Avaliar ocorrencia",
)
async def rate_occurrence(
    occurrence_id: UUID,
    data: OccurrenceRate,
    service: OccurrenceService = Depends(get_occurrence_service),
    current_user: dict = Depends(get_current_user),
) -> OccurrenceResponse:
    """Avalia uma ocorrencia resolvida."""
    result = await service.rate(occurrence_id, data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrencia nao encontrada",
        )
    logger.info(
        f"Ocorrencia {occurrence_id} avaliada com nota {data.rating} "
        f"por {current_user.get('email')}"
    )
    return result


# ==================== IA ====================


@router.post(
    "/classify",
    summary="Classificar ocorrencia com IA",
)
async def classify_occurrence(
    title: str = Query(..., description="Titulo da ocorrencia"),
    description: str = Query(..., description="Descricao da ocorrencia"),
    service: ClassificationAIService = Depends(get_classification_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Classifica uma ocorrencia usando IA."""
    return await service.classify_occurrence(title, description)


@router.get(
    "/{occurrence_id}/priority-score",
    summary="Calcular score de prioridade",
)
async def get_priority_score(
    occurrence_id: UUID,
    service: ClassificationAIService = Depends(get_classification_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Calcula score de prioridade de uma ocorrencia."""
    result = await service.calculate_priority_score(occurrence_id)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )
    return result


@router.get(
    "/{occurrence_id}/suggest-assignee",
    summary="Sugerir responsavel",
)
async def suggest_assignee(
    occurrence_id: UUID,
    service: ClassificationAIService = Depends(get_classification_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Sugere responsavel para uma ocorrencia."""
    result = await service.suggest_assignee(occurrence_id)
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )
    return result


@router.get(
    "/ai/trends",
    summary="Analisar tendencias",
)
async def analyze_trends(
    condominium_id: Optional[str] = Query(None, description="ID do condominio"),
    days: int = Query(30, ge=7, le=365, description="Periodo em dias"),
    service: ClassificationAIService = Depends(get_classification_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Analisa tendencias de ocorrencias."""
    return await service.analyze_trends(condominium_id, days)
