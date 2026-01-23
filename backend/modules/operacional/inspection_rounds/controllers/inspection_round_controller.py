"""
Controller de Rondas de Inspecao - Endpoints FastAPI.

Author: Conecta PRO Team
Date: 2026-01-23
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from ..services import (
    InspectionRoundService,
    InspectionRoundNotFoundError,
    InspectionRoundValidationError,
)
from ..schemas import (
    InspectionRoundCreate,
    InspectionRoundUpdate,
    InspectionRoundResponse,
    InspectionRoundListResponse,
    InspectionRoundSummary,
    InspectionRoundFilter,
    CheckpointCreate,
    CheckpointUpdate,
    CheckpointResponse,
    StartRoundRequest,
    CompleteRoundRequest,
    RegisterOccurrenceRequest,
    ApplyDisciplinaryRequest,
    InspectionDashboardStats,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_inspection_service(db: Session = Depends(get_db)) -> InspectionRoundService:
    """Dependency para obter InspectionRoundService."""
    return InspectionRoundService(db)


# =============================================================================
# CRUD ENDPOINTS
# =============================================================================


@router.post(
    "/",
    response_model=InspectionRoundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar ronda de inspecao",
    description="Cria uma nova ronda de inspecao.",
)
async def create_round(
    data: InspectionRoundCreate,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Cria uma nova ronda."""
    try:
        inspection_round = service.create(data)
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao criar ronda: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar ronda",
        )


@router.get(
    "/",
    response_model=InspectionRoundListResponse,
    summary="Listar rondas",
    description="Lista rondas com filtros e paginacao.",
)
async def list_rounds(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    skip: int = Query(0, ge=0, description="Registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    inspector_id: Optional[UUID] = Query(None, description="Filtrar por inspetor"),
    inspector_role: Optional[str] = Query(None, description="Filtrar por cargo"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por status"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    has_occurrences: Optional[bool] = Query(None, description="Com ocorrencias"),
    has_disciplinary_actions: Optional[bool] = Query(None, description="Com medidas disciplinares"),
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundListResponse:
    """Lista rondas com filtros."""
    filters = InspectionRoundFilter(
        inspector_id=inspector_id,
        inspector_role=inspector_role,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        has_occurrences=has_occurrences,
        has_disciplinary_actions=has_disciplinary_actions,
    )

    rounds, total = service.list(str(tenant_id), skip, limit, filters)

    pages = (total + limit - 1) // limit if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1

    return InspectionRoundListResponse(
        items=[InspectionRoundSummary.model_validate(r) for r in rounds],
        total=total,
        page=page,
        page_size=limit,
        pages=pages,
    )


@router.get(
    "/dashboard",
    response_model=InspectionDashboardStats,
    summary="Dashboard de rondas",
    description="Retorna estatisticas do dashboard de rondas.",
)
async def get_dashboard(
    tenant_id: UUID = Query(..., description="ID do tenant"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionDashboardStats:
    """Retorna estatisticas do dashboard."""
    return service.get_dashboard_stats(str(tenant_id), start_date, end_date)


@router.get(
    "/minhas-rondas",
    response_model=List[InspectionRoundSummary],
    summary="Minhas rondas",
    description="Lista rondas do inspetor logado.",
)
async def get_my_rounds(
    inspector_id: UUID = Query(..., description="ID do inspetor"),
    tenant_id: UUID = Query(..., description="ID do tenant"),
    limit: int = Query(50, ge=1, le=200),
    service: InspectionRoundService = Depends(get_inspection_service),
) -> List[InspectionRoundSummary]:
    """Lista rondas do inspetor."""
    rounds = service.get_rounds_by_inspector(str(inspector_id), str(tenant_id), limit)
    return [InspectionRoundSummary.model_validate(r) for r in rounds]


@router.get(
    "/{round_id}",
    response_model=InspectionRoundResponse,
    summary="Buscar ronda",
    description="Busca uma ronda por ID.",
)
async def get_round(
    round_id: UUID,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Busca ronda por ID."""
    try:
        inspection_round = service.get_by_id(str(round_id))
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{round_id}",
    response_model=InspectionRoundResponse,
    summary="Atualizar ronda",
    description="Atualiza uma ronda existente.",
)
async def update_round(
    round_id: UUID,
    data: InspectionRoundUpdate,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Atualiza uma ronda."""
    try:
        inspection_round = service.update(str(round_id), data)
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{round_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover ronda",
    description="Remove uma ronda (soft delete).",
)
async def delete_round(
    round_id: UUID,
    service: InspectionRoundService = Depends(get_inspection_service),
):
    """Remove uma ronda."""
    try:
        service.delete(str(round_id))
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =============================================================================
# WORKFLOW ENDPOINTS
# =============================================================================


@router.post(
    "/{round_id}/iniciar",
    response_model=InspectionRoundResponse,
    summary="Iniciar ronda",
    description="Inicia uma ronda agendada.",
)
async def start_round(
    round_id: UUID,
    data: Optional[StartRoundRequest] = None,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Inicia uma ronda."""
    try:
        inspection_round = service.start_round(str(round_id), data)
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{round_id}/pausar",
    response_model=InspectionRoundResponse,
    summary="Pausar ronda",
    description="Pausa uma ronda em andamento.",
)
async def pause_round(
    round_id: UUID,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Pausa uma ronda."""
    try:
        inspection_round = service.pause_round(str(round_id))
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{round_id}/retomar",
    response_model=InspectionRoundResponse,
    summary="Retomar ronda",
    description="Retoma uma ronda pausada.",
)
async def resume_round(
    round_id: UUID,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Retoma uma ronda pausada."""
    try:
        inspection_round = service.resume_round(str(round_id))
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{round_id}/concluir",
    response_model=InspectionRoundResponse,
    summary="Concluir ronda",
    description="Conclui uma ronda em andamento.",
)
async def complete_round(
    round_id: UUID,
    data: Optional[CompleteRoundRequest] = None,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Conclui uma ronda."""
    try:
        inspection_round = service.complete_round(str(round_id), data)
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{round_id}/cancelar",
    response_model=InspectionRoundResponse,
    summary="Cancelar ronda",
    description="Cancela uma ronda.",
)
async def cancel_round(
    round_id: UUID,
    reason: Optional[str] = Query(None, description="Motivo do cancelamento"),
    service: InspectionRoundService = Depends(get_inspection_service),
) -> InspectionRoundResponse:
    """Cancela uma ronda."""
    try:
        inspection_round = service.cancel_round(str(round_id), reason)
        return InspectionRoundResponse.model_validate(inspection_round)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =============================================================================
# CHECKPOINT ENDPOINTS
# =============================================================================


@router.post(
    "/{round_id}/checkpoints",
    response_model=CheckpointResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar checkpoint",
    description="Cria um checkpoint durante a ronda.",
)
async def create_checkpoint(
    round_id: UUID,
    data: CheckpointCreate,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> CheckpointResponse:
    """Cria um checkpoint."""
    try:
        checkpoint = service.create_checkpoint(str(round_id), data)
        return CheckpointResponse.model_validate(checkpoint)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{round_id}/checkpoints",
    response_model=List[CheckpointResponse],
    summary="Listar checkpoints",
    description="Lista checkpoints de uma ronda.",
)
async def get_checkpoints(
    round_id: UUID,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> List[CheckpointResponse]:
    """Lista checkpoints de uma ronda."""
    try:
        checkpoints = service.get_checkpoints(str(round_id))
        return [CheckpointResponse.model_validate(c) for c in checkpoints]
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{round_id}/checkpoints/{checkpoint_id}",
    response_model=CheckpointResponse,
    summary="Atualizar checkpoint",
    description="Atualiza um checkpoint.",
)
async def update_checkpoint(
    round_id: UUID,
    checkpoint_id: UUID,
    data: CheckpointUpdate,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> CheckpointResponse:
    """Atualiza um checkpoint."""
    try:
        checkpoint = service.update_checkpoint(str(checkpoint_id), data)
        return CheckpointResponse.model_validate(checkpoint)
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =============================================================================
# OCORRENCIA E MEDIDA DISCIPLINAR ENDPOINTS
# =============================================================================


@router.post(
    "/{round_id}/registrar-ocorrencia",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar ocorrencia",
    description="Registra uma ocorrencia durante a ronda.",
)
async def register_occurrence(
    round_id: UUID,
    data: RegisterOccurrenceRequest,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> dict:
    """Registra uma ocorrencia durante a ronda."""
    try:
        checkpoint, occurrence_info = service.register_occurrence(str(round_id), data)
        return {
            "checkpoint": CheckpointResponse.model_validate(checkpoint),
            "occurrence": occurrence_info,
            "message": f"Ocorrencia {occurrence_info['occurrence_code']} registrada com sucesso",
        }
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao registrar ocorrencia: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao registrar ocorrencia",
        )


@router.post(
    "/{round_id}/aplicar-medida-disciplinar",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Aplicar medida disciplinar",
    description="Aplica medida disciplinar durante a ronda.",
)
async def apply_disciplinary_action(
    round_id: UUID,
    data: ApplyDisciplinaryRequest,
    service: InspectionRoundService = Depends(get_inspection_service),
) -> dict:
    """Aplica medida disciplinar durante a ronda."""
    try:
        checkpoint, action_info = service.apply_disciplinary_action(str(round_id), data)
        return {
            "checkpoint": CheckpointResponse.model_validate(checkpoint),
            "disciplinary_action": action_info,
            "message": f"Medida disciplinar {action_info['disciplinary_action_code']} aplicada com sucesso",
        }
    except InspectionRoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InspectionRoundValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Erro ao aplicar medida disciplinar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao aplicar medida disciplinar",
        )
