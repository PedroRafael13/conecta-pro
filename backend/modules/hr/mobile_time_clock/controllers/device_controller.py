"""Controller para gerenciamento de dispositivos mobile."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user, require_roles
from core.database import get_db
from modules.hr.mobile_time_clock.repositories import MobileDeviceRepository
from modules.hr.mobile_time_clock.schemas import (
    DeviceHeartbeat,
    MobileDeviceApprove,
    MobileDeviceBlock,
    MobileDeviceFilter,
    MobileDeviceList,
    MobileDeviceRegister,
    MobileDeviceResponse,
    MobileDeviceStats,
)
from modules.hr.mobile_time_clock.services import DeviceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile/devices", tags=["Mobile Devices"])


@router.post(
    "/register",
    response_model=MobileDeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar dispositivo",
)
async def register_device(
    data: MobileDeviceRegister,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Registra novo dispositivo para uso no ponto mobile."""
    service = DeviceService(db)

    device, is_new = await service.register_device(
        data=data,
        employee_id=UUID(current_user["sub"]),
        condominio_id=UUID(current_user.get("condominio_id")),
    )

    status_msg = "registrado" if is_new else "atualizado"
    logger.info(f"Dispositivo {status_msg}: {device.id}")

    return device


@router.get(
    "/my-devices",
    response_model=list[MobileDeviceResponse],
    summary="Meus dispositivos",
)
async def get_my_devices(
    include_inactive: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista dispositivos do usuário autenticado."""
    service = DeviceService(db)

    devices = await service.get_employee_devices(
        employee_id=UUID(current_user["sub"]),
        include_inactive=include_inactive,
    )

    return devices


@router.post(
    "/heartbeat",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Heartbeat do dispositivo",
)
async def device_heartbeat(
    data: DeviceHeartbeat,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Envia heartbeat do dispositivo para manter status online."""
    repo = MobileDeviceRepository(db)
    device = await repo.get_by_uuid(data.device_uuid)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    if str(device.employee_id) != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispositivo não pertence ao usuário",
        )

    service = DeviceService(db)
    await service.process_heartbeat(device.id, data)


@router.put(
    "/push-token",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualizar token de push",
)
async def update_push_token(
    device_uuid: str,
    push_token: str,
    push_provider: str = "fcm",
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza token de push notification do dispositivo."""
    repo = MobileDeviceRepository(db)
    device = await repo.get_by_uuid(device_uuid)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    if str(device.employee_id) != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispositivo não pertence ao usuário",
        )

    service = DeviceService(db)
    await service.update_push_token(device.id, push_token, push_provider)


@router.get(
    "/validate/{device_uuid}",
    summary="Validar dispositivo para check-in",
)
async def validate_device(
    device_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Valida se dispositivo pode realizar check-in."""
    service = DeviceService(db)

    is_valid, device, error = await service.validate_device_for_checkin(device_uuid)

    return {
        "is_valid": is_valid,
        "device_id": str(device.id) if device else None,
        "status": device.status if device else None,
        "error": error,
    }


# === Endpoints Administrativos ===


@router.get(
    "/pending",
    response_model=list[MobileDeviceResponse],
    summary="Dispositivos pendentes de aprovação",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def get_pending_devices(
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista dispositivos aguardando aprovação."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    service = DeviceService(db)
    return await service.get_pending_approval(condo_id)


@router.post(
    "/{device_id}/approve",
    response_model=MobileDeviceResponse,
    summary="Aprovar dispositivo",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def approve_device(
    device_id: UUID,
    data: MobileDeviceApprove,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Aprova dispositivo para uso."""
    service = DeviceService(db)

    device = await service.approve_device(
        device_id=device_id,
        data=data,
        approved_by=UUID(current_user["sub"]),
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return device


@router.post(
    "/{device_id}/block",
    response_model=MobileDeviceResponse,
    summary="Bloquear dispositivo",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def block_device(
    device_id: UUID,
    data: MobileDeviceBlock,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Bloqueia dispositivo."""
    service = DeviceService(db)

    device = await service.block_device(
        device_id=device_id,
        data=data,
        blocked_by=UUID(current_user["sub"]),
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return device


@router.post(
    "/{device_id}/unblock",
    response_model=MobileDeviceResponse,
    summary="Desbloquear dispositivo",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def unblock_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Desbloqueia dispositivo."""
    service = DeviceService(db)

    device = await service.unblock_device(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return device


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revogar dispositivo",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def revoke_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Revoga dispositivo permanentemente."""
    service = DeviceService(db)

    if not await service.revoke_device(device_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )


@router.get(
    "/",
    response_model=MobileDeviceList,
    summary="Listar dispositivos",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def list_devices(
    employee_id: UUID = Query(None),
    condominio_id: UUID = Query(None),
    platform: str = Query(None),
    device_status: str = Query(None, alias="status"),
    is_trusted: bool = Query(None),
    is_active: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista dispositivos com filtros."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))

    filters = MobileDeviceFilter(
        employee_id=employee_id,
        condominio_id=condo_id,
        platform=platform,
        status=device_status,
        is_trusted=is_trusted,
        is_active=is_active,
    )

    repo = MobileDeviceRepository(db)
    items, total = await repo.list_devices(filters, page, page_size)

    return MobileDeviceList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/statistics",
    response_model=MobileDeviceStats,
    summary="Estatísticas de dispositivos",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def get_device_statistics(
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém estatísticas de dispositivos."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    service = DeviceService(db)
    return await service.get_device_statistics(condo_id)
