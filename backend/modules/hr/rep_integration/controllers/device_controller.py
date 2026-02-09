"""Controller para dispositivos REP."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.hr.rep_integration.repositories import REPDeviceRepository
from modules.hr.rep_integration.schemas import (
    REPDeviceCreate,
    REPDeviceFilter,
    REPDeviceList,
    REPDeviceResponse,
    REPDeviceTestConnection,
    REPDeviceUpdate,
)
from modules.hr.rep_integration.services import REPCommunicationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["REP Devices"])


@router.post("/", response_model=REPDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    data: REPDeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPDeviceResponse:
    """Cadastra novo dispositivo REP."""
    repo = REPDeviceRepository(db)

    # Verificar se serial já existe
    existing = await repo.get_by_serial(data.serial_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de série já cadastrado",
        )

    device = await repo.create(data)
    return device


@router.get("/", response_model=REPDeviceList)
async def list_devices(
    condominio_id: UUID | None = None,
    manufacturer: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    is_active: bool | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPDeviceList:
    """Lista dispositivos REP."""
    repo = REPDeviceRepository(db)

    filters = REPDeviceFilter(
        condominio_id=condominio_id,
        manufacturer=manufacturer,
        status=status_filter,
        is_active=is_active,
        search=search,
    )

    devices, total = await repo.list_devices(filters, page, page_size)

    return REPDeviceList(
        items=devices,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{device_id}", response_model=REPDeviceResponse)
async def get_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPDeviceResponse:
    """Obtém dispositivo por ID."""
    repo = REPDeviceRepository(db)
    device = await repo.get_by_id(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return device


@router.put("/{device_id}", response_model=REPDeviceResponse)
async def update_device(
    device_id: UUID,
    data: REPDeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> REPDeviceResponse:
    """Atualiza dispositivo."""
    repo = REPDeviceRepository(db)

    device = await repo.update(
        device_id,
        data,
        updated_by=UUID(current_user["sub"]),
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> None:
    """Desativa dispositivo (soft delete)."""
    repo = REPDeviceRepository(db)

    success = await repo.delete(device_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )


@router.post("/{device_id}/test", response_model=REPDeviceTestConnection)
async def test_connection(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPDeviceTestConnection:
    """Testa conexão com o dispositivo."""
    repo = REPDeviceRepository(db)
    device = await repo.get_by_id(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    comm_service = REPCommunicationService()
    result = await comm_service.test_connection(device)

    # Atualizar status baseado no teste
    if result.get("success"):
        await repo.update_status(device_id, "online")
        device_info = await comm_service.get_device_info(device)
        result["device_info"] = device_info
    else:
        await repo.update_status(
            device_id,
            "error",
            result.get("error_message"),
        )

    return REPDeviceTestConnection(**result)


@router.post("/{device_id}/sync-time")
async def sync_device_time(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Sincroniza horário do dispositivo."""
    repo = REPDeviceRepository(db)
    device = await repo.get_by_id(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    comm_service = REPCommunicationService()
    success = await comm_service.sync_time(device)

    return {"success": success}


@router.get("/{device_id}/users")
async def get_device_users(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Lista usuários cadastrados no dispositivo."""
    repo = REPDeviceRepository(db)
    device = await repo.get_by_id(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    comm_service = REPCommunicationService()
    users = await comm_service.get_users(device)

    # Atualizar contadores
    await repo.update_counters(device_id, users=len(users))

    return {"users": users, "total": len(users)}


@router.get("/statistics/summary")
async def get_devices_statistics(
    condominio_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna estatísticas dos dispositivos."""
    repo = REPDeviceRepository(db)
    return await repo.get_statistics(condominio_id)
