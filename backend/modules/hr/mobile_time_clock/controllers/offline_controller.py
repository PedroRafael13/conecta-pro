"""Controller para sincronização de check-ins offline."""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user, require_roles
from modules.hr.mobile_time_clock.schemas import (
    OfflineQueueItemCreate,
    OfflineQueueBatch,
    OfflineQueueResponse,
    OfflineQueueList,
    OfflineQueueFilter,
    OfflineQueueStats,
    SyncBatchResult,
    OfflineQueueRetry,
    OfflineQueueCleanup,
    OfflineQueueCleanupResult,
)
from modules.hr.mobile_time_clock.services import OfflineSyncService, DeviceService
from modules.hr.mobile_time_clock.repositories import (
    OfflineQueueRepository,
    MobileDeviceRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile/offline", tags=["Offline Queue"])


@router.post(
    "/queue",
    response_model=OfflineQueueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adicionar item à fila",
)
async def queue_item(
    data: OfflineQueueItemCreate,
    device_uuid: str = Query(..., description="UUID do dispositivo"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Adiciona check-in offline à fila de sincronização."""
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

    if str(device.employee_id) != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispositivo não pertence ao usuário",
        )

    sync_service = OfflineSyncService(db)
    item = await sync_service.queue_item(data, device)

    return item


@router.post(
    "/queue/batch",
    response_model=SyncBatchResult,
    summary="Adicionar batch à fila e sincronizar",
)
async def queue_and_sync_batch(
    data: OfflineQueueBatch,
    device_uuid: str = Query(..., description="UUID do dispositivo"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Adiciona batch de check-ins offline e tenta sincronizar."""
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

    if str(device.employee_id) != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispositivo não pertence ao usuário",
        )

    sync_service = OfflineSyncService(db)

    # Adicionar à fila
    await sync_service.queue_batch(data, device)

    # Sincronizar imediatamente
    result = await sync_service.sync_device_queue(device, limit=len(data.items))

    return result


@router.post(
    "/sync",
    response_model=SyncBatchResult,
    summary="Sincronizar fila pendente",
)
async def sync_queue(
    device_uuid: str = Query(..., description="UUID do dispositivo"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Sincroniza itens pendentes da fila do dispositivo."""
    device_repo = MobileDeviceRepository(db)
    device = await device_repo.get_by_uuid(device_uuid)

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

    sync_service = OfflineSyncService(db)
    result = await sync_service.sync_device_queue(device, limit)

    return result


@router.get(
    "/status",
    summary="Status de sincronização",
)
async def get_sync_status(
    device_uuid: str = Query(..., description="UUID do dispositivo"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém status de sincronização do dispositivo."""
    device_repo = MobileDeviceRepository(db)
    device = await device_repo.get_by_uuid(device_uuid)

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

    sync_service = OfflineSyncService(db)
    status_data = await sync_service.get_device_sync_status(device.id)

    return status_data


@router.get(
    "/pending",
    response_model=List[OfflineQueueResponse],
    summary="Itens pendentes",
)
async def get_pending_items(
    device_uuid: str = Query(..., description="UUID do dispositivo"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista itens pendentes de sincronização."""
    device_repo = MobileDeviceRepository(db)
    device = await device_repo.get_by_uuid(device_uuid)

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

    queue_repo = OfflineQueueRepository(db)
    items = await queue_repo.get_pending(device_id=device.id, limit=limit)

    return items


# === Endpoints Administrativos ===


@router.post(
    "/process-failed",
    response_model=SyncBatchResult,
    summary="Processar itens falhos",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def process_failed_items(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Processa itens que falharam e estão prontos para retry."""
    sync_service = OfflineSyncService(db)
    result = await sync_service.process_failed_items(limit)
    return result


@router.post(
    "/retry",
    summary="Forçar retry de itens",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def retry_items(
    data: OfflineQueueRetry,
    db: AsyncSession = Depends(get_db),
):
    """Força retry de itens específicos."""
    sync_service = OfflineSyncService(db)
    count = await sync_service.retry_items(data.item_ids, data.force)

    return {"reset_count": count}


@router.post(
    "/cleanup",
    response_model=OfflineQueueCleanupResult,
    summary="Limpar fila antiga",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def cleanup_queue(
    data: OfflineQueueCleanup,
    db: AsyncSession = Depends(get_db),
):
    """Limpa itens antigos da fila."""
    sync_service = OfflineSyncService(db)
    result = await sync_service.cleanup_queue(
        older_than_hours=data.older_than_hours,
        statuses=data.statuses,
        dry_run=data.dry_run,
    )

    return OfflineQueueCleanupResult(
        deleted_count=result["deleted_count"] if not data.dry_run else 0,
        by_status=result["by_status"],
        dry_run=data.dry_run,
    )


@router.get(
    "/",
    response_model=OfflineQueueList,
    summary="Listar fila",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def list_queue(
    device_id: UUID = Query(None),
    employee_id: UUID = Query(None),
    condominio_id: UUID = Query(None),
    queue_status: str = Query(None, alias="status"),
    priority: str = Query(None),
    is_expired: bool = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista itens da fila com filtros."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))

    filters = OfflineQueueFilter(
        device_id=device_id,
        employee_id=employee_id,
        condominio_id=condo_id,
        status=queue_status,
        priority=priority,
        is_expired=is_expired,
    )

    queue_repo = OfflineQueueRepository(db)
    items, total = await queue_repo.list_items(filters, page, page_size)

    return OfflineQueueList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/statistics",
    response_model=OfflineQueueStats,
    summary="Estatísticas da fila",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def get_queue_statistics(
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém estatísticas da fila offline."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    queue_repo = OfflineQueueRepository(db)
    return await queue_repo.get_statistics(condo_id)
