"""Controller para check-ins mobile."""

import logging
from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user, require_roles
from modules.hr.mobile_time_clock.schemas import (
    MobileCheckInCreate,
    MobileCheckInReview,
    MobileCheckInResponse,
    MobileCheckInList,
    MobileCheckInFilter,
    MobileCheckInStats,
    CheckInConfirmation,
)
from modules.hr.mobile_time_clock.services import (
    CheckInValidationService,
    DeviceService,
    PushNotificationService,
)
from modules.hr.mobile_time_clock.repositories import (
    MobileCheckInRepository,
    MobileDeviceRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile/checkins", tags=["Mobile Check-ins"])


@router.post(
    "/",
    response_model=CheckInConfirmation,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar check-in",
)
async def create_checkin(
    data: MobileCheckInCreate,
    device_uuid: str = Query(..., description="UUID do dispositivo"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Registra check-in via app mobile."""
    # Validar dispositivo
    device_service = DeviceService(db)
    is_valid, device, error = await device_service.validate_device_for_checkin(
        device_uuid
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error,
        )

    # Verificar se dispositivo pertence ao usuário
    if str(device.employee_id) != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispositivo não pertence ao usuário",
        )

    # Processar check-in
    validation_service = CheckInValidationService(db)
    checkin, validation = await validation_service.process_checkin(
        data=data,
        device=device,
        employee_id=UUID(current_user["sub"]),
        condominio_id=device.condominio_id,
    )

    # Notificar resultado
    push_service = PushNotificationService(db)
    if validation.is_valid:
        await push_service.notify_checkin_confirmed(
            device=device,
            checkin_type=data.checkin_type,
            checkin_time=checkin.checkin_datetime,
        )
    elif validation.errors:
        await push_service.notify_checkin_rejected(
            device=device,
            reason=validation.errors[0],
        )

    return CheckInConfirmation(
        checkin_id=checkin.id,
        status=checkin.status,
        is_valid=validation.is_valid,
        validation_score=validation.score,
        validation_methods=validation.validation_methods,
        requires_review=validation.requires_review,
        geofence_zone_name=validation.geofence_zone_name,
        server_time=checkin.server_timestamp,
        message="Check-in registrado" if validation.is_valid else "Check-in requer revisão",
        warnings=validation.warnings,
    )


@router.get(
    "/today",
    response_model=List[MobileCheckInResponse],
    summary="Check-ins de hoje",
)
async def get_today_checkins(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista check-ins do usuário hoje."""
    repo = MobileCheckInRepository(db)
    checkins = await repo.get_employee_today(
        employee_id=UUID(current_user["sub"]),
        today=date.today(),
    )
    return checkins


@router.get(
    "/last",
    response_model=MobileCheckInResponse,
    summary="Último check-in",
)
async def get_last_checkin(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém último check-in do usuário."""
    repo = MobileCheckInRepository(db)
    checkin = await repo.get_last_checkin(UUID(current_user["sub"]))

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum check-in encontrado",
        )

    return checkin


@router.get(
    "/{checkin_id}",
    response_model=MobileCheckInResponse,
    summary="Detalhes do check-in",
)
async def get_checkin(
    checkin_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém detalhes de um check-in."""
    repo = MobileCheckInRepository(db)
    checkin = await repo.get_by_id(checkin_id)

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in não encontrado",
        )

    # Verificar permissão (próprio ou admin)
    if str(checkin.employee_id) != current_user["sub"]:
        if current_user.get("role") not in ["admin", "rh", "gestor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para visualizar este check-in",
            )

    return checkin


# === Endpoints Administrativos ===


@router.get(
    "/pending-review",
    response_model=List[MobileCheckInResponse],
    summary="Check-ins pendentes de revisão",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def get_pending_review(
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista check-ins que precisam de revisão."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    repo = MobileCheckInRepository(db)
    return await repo.get_pending_review(condo_id)


@router.post(
    "/{checkin_id}/review",
    response_model=MobileCheckInResponse,
    summary="Revisar check-in",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def review_checkin(
    checkin_id: UUID,
    data: MobileCheckInReview,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Revisa e aprova/rejeita check-in flagado."""
    repo = MobileCheckInRepository(db)

    checkin = await repo.review(
        checkin_id=checkin_id,
        reviewer_id=UUID(current_user["sub"]),
        approved=data.approved,
        notes=data.notes,
        rejection_reason=data.rejection_reason,
    )

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in não encontrado",
        )

    # Notificar funcionário
    device_repo = MobileDeviceRepository(db)
    devices = await device_repo.get_by_employee(checkin.employee_id)

    if devices:
        push_service = PushNotificationService(db)
        if data.approved:
            await push_service.notify_checkin_confirmed(
                device=devices[0],
                checkin_type=checkin.checkin_type,
                checkin_time=checkin.checkin_datetime,
            )
        else:
            await push_service.notify_checkin_rejected(
                device=devices[0],
                reason=data.rejection_reason or "Rejeitado pela supervisão",
            )

    return checkin


@router.get(
    "/",
    response_model=MobileCheckInList,
    summary="Listar check-ins",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def list_checkins(  # pylint: disable=too-many-locals
    device_id: UUID = Query(None),
    employee_id: UUID = Query(None),
    condominio_id: UUID = Query(None),
    geofence_id: UUID = Query(None),
    checkin_type: str = Query(None),
    checkin_status: str = Query(None, alias="status"),
    date_from: date = Query(None),
    date_to: date = Query(None),
    inside_geofence: bool = Query(None),
    is_offline: bool = Query(None),
    has_anomaly: bool = Query(None),
    needs_review: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista check-ins com filtros."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))

    filters = MobileCheckInFilter(
        device_id=device_id,
        employee_id=employee_id,
        condominio_id=condo_id,
        geofence_id=geofence_id,
        checkin_type=checkin_type,
        status=checkin_status,
        date_from=date_from,
        date_to=date_to,
        inside_geofence=inside_geofence,
        is_offline=is_offline,
        has_anomaly=has_anomaly,
        needs_review=needs_review,
    )

    repo = MobileCheckInRepository(db)
    items, total = await repo.list_checkins(filters, page, page_size)

    return MobileCheckInList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/statistics",
    response_model=MobileCheckInStats,
    summary="Estatísticas de check-ins",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def get_checkin_statistics(
    condominio_id: UUID = Query(None),
    date_from: date = Query(None),
    date_to: date = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém estatísticas de check-ins."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    repo = MobileCheckInRepository(db)
    return await repo.get_statistics(condo_id, date_from, date_to)
