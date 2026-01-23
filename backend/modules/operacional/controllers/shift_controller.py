"""
Controller (endpoints) para Shift.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.operacional.models.shift import ShiftStatus
from modules.operacional.permissions import Permission, require_operacional_permission
from modules.operacional.repositories.shift_repository import ShiftRepository
from modules.operacional.schemas.shift import (
    ShiftCheckIn,
    ShiftCheckOut,
    ShiftCreate,
    ShiftFilter,
    ShiftListResponse,
    ShiftResponse,
    ShiftUpdate,
)

router = APIRouter(prefix="/shifts", tags=["Operations - Shifts"])


@router.post(
    "/",
    response_model=ShiftResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_operacional_permission(Permission.SHIFTS_CREATE)],
)
async def create_shift(
    data: ShiftCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ShiftResponse:
    """
    Cria um novo turno.
    """
    repo = ShiftRepository(db)
    shift = await repo.create(data)

    logger.info(f"Shift criado por {current_user.email}: {shift.id}")
    return ShiftResponse.model_validate(shift)


@router.get(
    "/",
    response_model=ShiftListResponse,
    dependencies=[require_operacional_permission(Permission.SHIFTS_VIEW_ALL, Permission.SHIFTS_VIEW_OWN)],
)
async def list_shifts(  # pylint: disable=too-many-locals
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Página atual"),
    page_size: int = Query(50, ge=1, le=200, description="Itens por página"),
    scale_id: Optional[str] = None,
    employee_id: Optional[str] = None,
    post_id: Optional[str] = None,
    status_filter: Optional[ShiftStatus] = Query(None, alias="status"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_holiday: Optional[bool] = None,
    is_night_shift: Optional[bool] = None,
    is_off_day: Optional[bool] = None,
    is_filled: Optional[bool] = None,
    needs_substitution: Optional[bool] = None,
) -> ShiftListResponse:
    """
    Lista turnos com filtros e paginação.
    """
    repo = ShiftRepository(db)

    filters = ShiftFilter(
        scale_id=scale_id,
        employee_id=employee_id,
        post_id=post_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        is_holiday=is_holiday,
        is_night_shift=is_night_shift,
        is_off_day=is_off_day,
        is_filled=is_filled,
        needs_substitution=needs_substitution,
    )

    shifts, total = await repo.list(filters=filters, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size

    return ShiftListResponse(
        items=[ShiftResponse.model_validate(shift) for shift in shifts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/today",
    dependencies=[require_operacional_permission(Permission.SHIFTS_VIEW_ALL, Permission.SHIFTS_VIEW_OWN)],
)
async def get_today_shifts(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    post_id: Optional[str] = None,
) -> ShiftListResponse:
    """
    Lista turnos do dia atual.
    """
    repo = ShiftRepository(db)
    today = date.today()

    filters = ShiftFilter(
        start_date=today,
        end_date=today,
        post_id=post_id,
    )

    shifts, total = await repo.list(filters=filters, page=1, page_size=100)

    return ShiftListResponse(
        items=[ShiftResponse.model_validate(shift) for shift in shifts],
        total=total,
        page=1,
        page_size=100,
        total_pages=1,
    )


@router.get(
    "/scale/{scale_id}",
    response_model=list[ShiftResponse],
    dependencies=[require_operacional_permission(Permission.SHIFTS_VIEW_ALL, Permission.SHIFTS_VIEW_OWN)],
)
async def get_shifts_by_scale(
    scale_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> list[ShiftResponse]:
    """
    Lista todos os turnos de uma escala.
    """
    repo = ShiftRepository(db)
    shifts = await repo.get_by_scale(scale_id)

    return [ShiftResponse.model_validate(shift) for shift in shifts]


@router.get(
    "/{shift_id}",
    response_model=ShiftResponse,
    dependencies=[require_operacional_permission(Permission.SHIFTS_VIEW_ALL, Permission.SHIFTS_VIEW_OWN)],
)
async def get_shift(
    shift_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ShiftResponse:
    """
    Busca turno por ID.
    """
    repo = ShiftRepository(db)
    shift = await repo.get_by_id(shift_id)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno não encontrado",
        )

    return ShiftResponse.model_validate(shift)


@router.patch(
    "/{shift_id}",
    response_model=ShiftResponse,
    dependencies=[require_operacional_permission(Permission.SHIFTS_CREATE)],
)
async def update_shift(
    shift_id: str,
    data: ShiftUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ShiftResponse:
    """
    Atualiza um turno.
    """
    repo = ShiftRepository(db)
    shift = await repo.update(shift_id, data)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno não encontrado",
        )

    logger.info(f"Shift atualizado por {current_user.email}: {shift.id}")
    return ShiftResponse.model_validate(shift)


@router.post(
    "/{shift_id}/check-in",
    response_model=ShiftResponse,
    dependencies=[require_operacional_permission(Permission.SHIFTS_CHECKIN)],
)
async def check_in(
    shift_id: str,
    data: ShiftCheckIn,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ShiftResponse:
    """
    Registra entrada no turno.
    """
    repo = ShiftRepository(db)
    shift = await repo.check_in(shift_id, data.actual_start_time, data.notes)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno não encontrado",
        )

    logger.info(f"Check-in registrado: {shift.id}")
    return ShiftResponse.model_validate(shift)


@router.post(
    "/{shift_id}/check-out",
    response_model=ShiftResponse,
    dependencies=[require_operacional_permission(Permission.SHIFTS_CHECKIN)],
)
async def check_out(
    shift_id: str,
    data: ShiftCheckOut,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> ShiftResponse:
    """
    Registra saída do turno.
    """
    repo = ShiftRepository(db)
    shift = await repo.check_out(
        shift_id,
        data.actual_end_time,
        data.actual_break_minutes,
        data.notes,
    )

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno não encontrado",
        )

    logger.info(f"Check-out registrado: {shift.id}")
    return ShiftResponse.model_validate(shift)


@router.post(
    "/{shift_id}/mark-missed",
    response_model=ShiftResponse,
    dependencies=[require_operacional_permission(Permission.SHIFTS_MARK_MISSED)],
)
async def mark_as_missed(
    shift_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    reason: Optional[str] = Query(None, description="Motivo da falta"),
) -> ShiftResponse:
    """
    Marca turno como falta.
    """
    repo = ShiftRepository(db)
    shift = await repo.mark_as_missed(shift_id, reason)

    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno não encontrado",
        )

    logger.info(f"Turno marcado como falta: {shift.id}")
    return ShiftResponse.model_validate(shift)


@router.delete(
    "/{shift_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_operacional_permission(Permission.SHIFTS_CREATE)],
)
async def delete_shift(
    shift_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove um turno (soft delete).
    """
    repo = ShiftRepository(db)
    deleted = await repo.delete(shift_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turno não encontrado",
        )

    logger.info(f"Shift deletado por {current_user.email}: {shift_id}")
