"""Controller para sincronização REP."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user
from modules.hr.rep_integration.services import SyncService
from modules.hr.rep_integration.repositories import REPSyncRepository
from modules.hr.rep_integration.schemas import (
    REPSyncStart,
    REPSyncResponse,
    REPSyncList,
    REPSyncFilter,
    REPSyncProgress,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["REP Sync"])


@router.post("/start", response_model=dict)
async def start_sync(
    data: REPSyncStart,
    background_tasks: BackgroundTasks,  # pylint: disable=unused-argument
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Inicia sincronização de eventos."""
    sync_service = SyncService(db)

    # Executar em background se solicitado
    success, result = await sync_service.sync_device_events(
        device_id=data.device_id,
        trigger="manual",
        triggered_by=UUID(current_user["sub"]),
        from_nsr=data.from_nsr,
        from_datetime=data.from_datetime,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Erro na sincronização"),
        )

    return result


@router.post("/all")
async def sync_all_devices(
    condominio_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Sincroniza todos os dispositivos pendentes."""
    sync_service = SyncService(db)
    return await sync_service.sync_all_devices(condominio_id)


@router.get("/", response_model=REPSyncList)
async def list_syncs(
    device_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    sync_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    has_errors: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPSyncList:
    """Lista histórico de sincronizações."""
    repo = REPSyncRepository(db)

    filters = REPSyncFilter(
        device_id=device_id,
        condominio_id=condominio_id,
        sync_type=sync_type,
        status=status_filter,
        has_errors=has_errors,
    )

    syncs, total = await repo.list_syncs(filters, page, page_size)

    return REPSyncList(
        items=syncs,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{sync_id}", response_model=REPSyncResponse)
async def get_sync(
    sync_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPSyncResponse:
    """Obtém detalhes de uma sincronização."""
    repo = REPSyncRepository(db)
    sync = await repo.get_by_id(sync_id)

    if not sync:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )

    return sync


@router.get("/{sync_id}/progress", response_model=REPSyncProgress)
async def get_sync_progress(
    sync_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> REPSyncProgress:
    """Obtém progresso de uma sincronização."""
    sync_service = SyncService(db)
    progress = await sync_service.get_sync_progress(sync_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )

    return REPSyncProgress(**progress)


@router.post("/{sync_id}/retry")
async def retry_sync(
    sync_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retenta uma sincronização que falhou."""
    sync_service = SyncService(db)
    success, result = await sync_service.retry_failed_sync(sync_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Erro ao retentar"),
        )

    return result


@router.get("/statistics/summary")
async def get_sync_statistics(
    device_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna estatísticas de sincronizações."""
    repo = REPSyncRepository(db)
    return await repo.get_statistics(device_id, condominio_id, days)


@router.post("/cancel-stale")
async def cancel_stale_syncs(
    timeout_minutes: int = Query(30, ge=5, le=120),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Cancela sincronizações travadas."""
    repo = REPSyncRepository(db)
    cancelled = await repo.cancel_stale_syncs(timeout_minutes)
    return {"cancelled": cancelled}
