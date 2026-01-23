"""
Controller (endpoints) para Scale.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.operacional.models.scale import ScaleStatus, ScaleType
from modules.operacional.permissions import Permission, require_operacional_permission
from modules.operacional.repositories.scale_repository import ScaleRepository
from modules.operacional.repositories.shift_repository import ShiftRepository
from modules.operacional.schemas.scale import (
    ScaleApproveRequest,
    ScaleCreate,
    ScaleFilter,
    ScaleGenerateRequest,
    ScaleListResponse,
    ScalePublishRequest,
    ScaleResponse,
    ScaleUpdate,
)
from modules.operacional.services.scale_generator import scale_generator

router = APIRouter(prefix="/scales", tags=["Operations - Scales"])


@router.post(
    "/",
    response_model=ScaleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_operacional_permission(Permission.SCALES_CREATE)],
)
async def create_scale(
    data: ScaleCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Cria uma nova escala.

    Cria apenas a escala, sem turnos. Use /generate para gerar turnos.
    """
    repo = ScaleRepository(db)

    # Verificar se já existe escala para o período
    existing = await repo.get_by_post_and_period(data.post_id, data.month, data.year)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe escala para este posto/período",
        )

    scale = await repo.create(data, created_by=current_user.id)

    logger.info(f"Scale criada por {current_user.email}: {scale.id}")
    return ScaleResponse.model_validate(scale)


@router.post(
    "/generate",
    response_model=ScaleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_operacional_permission(Permission.SCALES_CREATE)],
)
async def generate_scale(
    data: ScaleGenerateRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Gera escala automaticamente com IA.

    Cria a escala e todos os turnos baseado no tipo de escala
    e lista de funcionários.
    """
    scale_repo = ScaleRepository(db)
    shift_repo = ShiftRepository(db)

    # Verificar se já existe escala para o período
    existing = await scale_repo.get_by_post_and_period(data.post_id, data.month, data.year)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe escala para este posto/período",
        )

    # Criar escala
    scale_data = ScaleCreate(
        post_id=data.post_id,
        scale_type=data.scale_type,
        month=data.month,
        year=data.year,
        config=data.config,
    )
    scale = await scale_repo.create(scale_data, created_by=current_user.id)

    # Gerar turnos com IA
    shifts_data = scale_generator.generate(
        scale_id=scale.id,
        post_id=data.post_id,
        scale_type=data.scale_type,
        month=data.month,
        year=data.year,
        employee_ids=data.employee_ids,
        config=data.config,
    )

    # Criar turnos em lote
    await shift_repo.create_bulk(shifts_data)

    # Atualizar métricas da escala
    scale = await scale_repo.update_metrics(scale.id)

    logger.info(
        f"Scale gerada por {current_user.email}: {scale.id} " f"({len(shifts_data)} turnos)"
    )

    return ScaleResponse.model_validate(scale)


@router.get(
    "/",
    response_model=ScaleListResponse,
    dependencies=[require_operacional_permission(Permission.SCALES_VIEW_ALL, Permission.SCALES_VIEW_OWN)],
)
async def list_scales(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    post_id: Optional[str] = None,
    scale_type: Optional[ScaleType] = None,
    status_filter: Optional[ScaleStatus] = Query(None, alias="status"),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020, le=2100),
    is_current_month: Optional[bool] = None,
) -> ScaleListResponse:
    """
    Lista escalas com filtros e paginação.
    """
    repo = ScaleRepository(db)

    filters = ScaleFilter(
        post_id=post_id,
        scale_type=scale_type,
        status=status_filter,
        month=month,
        year=year,
        is_current_month=is_current_month,
    )

    scales, total = await repo.list(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return ScaleListResponse(
        items=[ScaleResponse.model_validate(scale) for scale in scales],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{scale_id}",
    response_model=ScaleResponse,
    dependencies=[require_operacional_permission(Permission.SCALES_VIEW_ALL, Permission.SCALES_VIEW_OWN)],
)
async def get_scale(
    scale_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Busca escala por ID.
    """
    repo = ScaleRepository(db)
    scale = await repo.get_by_id(scale_id)

    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada",
        )

    return ScaleResponse.model_validate(scale)


@router.patch(
    "/{scale_id}",
    response_model=ScaleResponse,
    dependencies=[require_operacional_permission(Permission.SCALES_CREATE)],
)
async def update_scale(
    scale_id: str,
    data: ScaleUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Atualiza uma escala.

    Só é possível editar escalas em rascunho ou pendentes de aprovação.
    """
    repo = ScaleRepository(db)
    scale = await repo.update(scale_id, data)

    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada ou não pode ser editada",
        )

    logger.info(f"Scale atualizada por {current_user.email}: {scale.id}")
    return ScaleResponse.model_validate(scale)


@router.post(
    "/{scale_id}/submit",
    response_model=ScaleResponse,
    dependencies=[require_operacional_permission(Permission.SCALES_CREATE)],
)
async def submit_scale_for_approval(
    scale_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Envia escala para aprovação.
    """
    repo = ScaleRepository(db)
    scale = await repo.get_by_id(scale_id)

    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada",
        )

    if scale.status != ScaleStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Escala não está em rascunho",
        )

    update = ScaleUpdate(status=ScaleStatus.PENDING_APPROVAL)
    scale = await repo.update(scale_id, update)

    logger.info(f"Scale enviada para aprovação por {current_user.email}: {scale.id}")
    return ScaleResponse.model_validate(scale)


@router.post(
    "/{scale_id}/approve",
    response_model=ScaleResponse,
    dependencies=[require_operacional_permission(Permission.SCALES_APPROVE)],
)
async def approve_scale(
    scale_id: str,
    data: ScaleApproveRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Aprova uma escala.
    """
    repo = ScaleRepository(db)
    scale = await repo.approve(scale_id, current_user.id, data.notes)

    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada ou não pode ser aprovada",
        )

    logger.info(f"Scale aprovada por {current_user.email}: {scale.id}")
    return ScaleResponse.model_validate(scale)


@router.post(
    "/{scale_id}/publish",
    response_model=ScaleResponse,
    dependencies=[require_operacional_permission(Permission.SCALES_PUBLISH)],
)
async def publish_scale(
    scale_id: str,
    data: ScalePublishRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ScaleResponse:
    """
    Publica uma escala.

    Após publicação, os funcionários são notificados.
    """
    repo = ScaleRepository(db)
    scale = await repo.publish(scale_id, current_user.id)

    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada ou não pode ser publicada",
        )

    # PENDENTE: Enviar notificações aos funcionários
    if data.notify_employees:
        logger.info(f"Notificando funcionários via {data.notification_channels}")

    logger.info(f"Scale publicada por {current_user.email}: {scale.id}")
    return ScaleResponse.model_validate(scale)


@router.delete(
    "/{scale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_operacional_permission(Permission.SCALES_CREATE)],
)
async def delete_scale(
    scale_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove uma escala (soft delete).

    Só é possível deletar escalas em rascunho.
    """
    repo = ScaleRepository(db)
    deleted = await repo.delete(scale_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada ou não pode ser deletada",
        )

    logger.info(f"Scale deletada por {current_user.email}: {scale_id}")
