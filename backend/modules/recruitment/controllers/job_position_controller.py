"""Controller para JobPosition."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user, require_permissions
from modules.recruitment.schemas.job_position import (
    JobPositionCreate,
    JobPositionUpdate,
    JobPositionResponse,
    JobPositionListResponse,
    JobPositionFilter,
    JobPositionStats,
    JobPositionPublish,
)
from modules.recruitment.models.job_position import (
    PositionStatus,
    PositionType,
    PositionLevel,
    WorkModel,
    Department,
)
from modules.recruitment.services.job_position_service import JobPositionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/job-positions", tags=["Recruitment - Vagas"])


@router.post(
    "/",
    response_model=JobPositionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar vaga",
)
async def create_position(
    data: JobPositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Cria uma nova vaga de emprego."""
    service = JobPositionService(db)

    try:
        position = await service.create(data)
        return JobPositionResponse.model_validate(position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar vaga: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar vaga",
        )


@router.get(
    "/",
    response_model=JobPositionListResponse,
    summary="Listar vagas",
)
async def list_positions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[PositionStatus] = Query(None, alias="status"),
    position_type: Optional[PositionType] = None,
    position_level: Optional[PositionLevel] = None,
    department: Optional[Department] = None,
    work_model: Optional[WorkModel] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    is_urgent: Optional[bool] = None,
    condominium_id: Optional[str] = None,
    search: Optional[str] = None,
    order_by: str = "created_at",
    order_desc: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionListResponse:
    """Lista vagas com filtros e paginação."""
    service = JobPositionService(db)

    filters = JobPositionFilter(
        status=status_filter,
        position_type=position_type,
        position_level=position_level,
        department=department,
        work_model=work_model,
        city=city,
        state=state,
        is_urgent=is_urgent,
        condominium_id=condominium_id,
        search=search,
    )

    positions, total = await service.list_with_filters(
        filters, skip, limit, order_by, order_desc
    )

    return JobPositionListResponse(
        items=[JobPositionResponse.model_validate(p) for p in positions],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/open",
    response_model=JobPositionListResponse,
    summary="Listar vagas abertas",
)
async def list_open_positions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    condominium_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionListResponse:
    """Lista vagas abertas para candidaturas."""
    service = JobPositionService(db)
    positions = await service.get_open_positions(condominium_id, skip, limit)

    return JobPositionListResponse(
        items=[JobPositionResponse.model_validate(p) for p in positions],
        total=len(positions),
        skip=skip,
        limit=limit,
    )


@router.get(
    "/expiring",
    response_model=JobPositionListResponse,
    summary="Vagas próximas da expiração",
)
async def list_expiring_positions(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionListResponse:
    """Lista vagas próximas da data limite."""
    service = JobPositionService(db)
    positions = await service.get_expiring_soon(days)

    return JobPositionListResponse(
        items=[JobPositionResponse.model_validate(p) for p in positions],
        total=len(positions),
        skip=0,
        limit=len(positions),
    )


@router.get(
    "/stats",
    response_model=JobPositionStats,
    summary="Estatísticas de vagas",
)
async def get_position_stats(
    condominium_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionStats:
    """Retorna estatísticas das vagas."""
    service = JobPositionService(db)
    stats = await service.get_stats(condominium_id)
    return JobPositionStats(**stats)


@router.get(
    "/{position_id}",
    response_model=JobPositionResponse,
    summary="Buscar vaga",
)
async def get_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Busca vaga por ID."""
    service = JobPositionService(db)
    position = await service.get_by_id(position_id)

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaga não encontrada",
        )

    # Incrementa visualização
    await service.increment_view(position_id)

    return JobPositionResponse.model_validate(position)


@router.get(
    "/code/{code}",
    response_model=JobPositionResponse,
    summary="Buscar vaga por código",
)
async def get_position_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Busca vaga por código."""
    service = JobPositionService(db)
    position = await service.get_by_code(code)

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaga não encontrada",
        )

    return JobPositionResponse.model_validate(position)


@router.put(
    "/{position_id}",
    response_model=JobPositionResponse,
    summary="Atualizar vaga",
)
async def update_position(
    position_id: str,
    data: JobPositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Atualiza uma vaga existente."""
    service = JobPositionService(db)

    try:
        position = await service.update(position_id, data)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vaga não encontrada",
            )
        return JobPositionResponse.model_validate(position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{position_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover vaga",
)
async def delete_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Remove uma vaga (soft delete)."""
    service = JobPositionService(db)
    result = await service.delete(position_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaga não encontrada",
        )


@router.post(
    "/{position_id}/publish",
    response_model=JobPositionResponse,
    summary="Publicar vaga",
)
async def publish_position(
    position_id: str,
    data: JobPositionPublish,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Publica uma vaga em rascunho."""
    service = JobPositionService(db)

    try:
        position = await service.publish(position_id, data)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vaga não encontrada",
            )
        return JobPositionResponse.model_validate(position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{position_id}/pause",
    response_model=JobPositionResponse,
    summary="Pausar vaga",
)
async def pause_position(
    position_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Pausa uma vaga aberta."""
    service = JobPositionService(db)

    try:
        position = await service.pause(position_id, reason)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vaga não encontrada",
            )
        return JobPositionResponse.model_validate(position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{position_id}/reopen",
    response_model=JobPositionResponse,
    summary="Reabrir vaga",
)
async def reopen_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Reabre uma vaga pausada."""
    service = JobPositionService(db)

    try:
        position = await service.reopen(position_id)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vaga não encontrada",
            )
        return JobPositionResponse.model_validate(position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{position_id}/close",
    response_model=JobPositionResponse,
    summary="Fechar vaga",
)
async def close_position(
    position_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Fecha uma vaga."""
    service = JobPositionService(db)

    try:
        position = await service.close(position_id, reason)
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vaga não encontrada",
            )
        return JobPositionResponse.model_validate(position)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{position_id}/duplicate",
    response_model=JobPositionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicar vaga",
)
async def duplicate_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> JobPositionResponse:
    """Duplica uma vaga existente."""
    service = JobPositionService(db)

    position = await service.duplicate(position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaga não encontrada",
        )

    return JobPositionResponse.model_validate(position)
