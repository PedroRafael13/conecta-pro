"""
Controller FastAPI para GuardianSync.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.campo.models.guardian_sync import (
    SyncDirection,
    SyncEntityType,
    SyncStatus,
)
from modules.campo.repositories.guardian_sync_repository import (
    GuardianSyncRepository,
)
from modules.campo.schemas.guardian_sync import (
    GuardianSyncCreate,
    GuardianSyncFilter,
    GuardianSyncListResponse,
    GuardianSyncResponse,
    GuardianSyncRetry,
    GuardianSyncStats,
)
from modules.campo.services.guardian_sync_service import (
    guardian_sync_service,
)

router = APIRouter(prefix="/guardian/sync", tags=["GuardianSync"])


@router.post(
    "/",
    response_model=GuardianSyncResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sync(
    data: GuardianSyncCreate,
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncResponse:
    """Cria uma nova sincronização."""
    repo = GuardianSyncRepository(db)
    sync = await repo.create(data)
    logger.info(f"Sincronização criada: {sync.sync_code}")
    return GuardianSyncResponse.model_validate(sync)


@router.get("/", response_model=GuardianSyncListResponse)
async def list_syncs(
    search: str | None = Query(None),
    direction: SyncDirection | None = Query(None),
    entity_type: SyncEntityType | None = Query(None),
    sync_status: SyncStatus | None = Query(None, alias="status"),
    client_id: str | None = Query(None),
    contract_id: str | None = Query(None),
    can_retry: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncListResponse:
    """Lista sincronizações com filtros e paginação."""
    repo = GuardianSyncRepository(db)
    filters = GuardianSyncFilter(
        search=search,
        direction=direction,
        entity_type=entity_type,
        status=sync_status,
        client_id=client_id,
        contract_id=contract_id,
        can_retry=can_retry,
    )
    syncs, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return GuardianSyncListResponse(
        items=[GuardianSyncResponse.model_validate(s) for s in syncs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=GuardianSyncStats)
async def get_sync_stats(
    client_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncStats:
    """Obtém estatísticas de sincronização."""
    repo = GuardianSyncRepository(db)
    return await repo.get_stats(client_id)


@router.get("/pending")
async def get_pending_syncs(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[GuardianSyncResponse]:
    """Obtém sincronizações pendentes."""
    repo = GuardianSyncRepository(db)
    syncs = await repo.get_pending(limit)
    return [GuardianSyncResponse.model_validate(s) for s in syncs]


@router.get("/failed-for-retry")
async def get_failed_for_retry(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[GuardianSyncResponse]:
    """Obtém sincronizações falhas que podem ser reprocessadas."""
    repo = GuardianSyncRepository(db)
    syncs = await repo.get_failed_for_retry(limit)
    return [GuardianSyncResponse.model_validate(s) for s in syncs]


@router.get("/summary")
async def get_sync_summary(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Obtém resumo das sincronizações."""
    repo = GuardianSyncRepository(db)
    stats = await repo.get_stats()

    return guardian_sync_service.format_sync_summary(
        total=stats.total,
        completed=stats.completed,
        failed=stats.failed,
        pending=stats.pending,
    )


@router.get("/{sync_id}", response_model=GuardianSyncResponse)
async def get_sync(
    sync_id: str,
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncResponse:
    """Obtém uma sincronização por ID."""
    repo = GuardianSyncRepository(db)
    sync = await repo.get_by_id(sync_id)
    if not sync:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )
    return GuardianSyncResponse.model_validate(sync)


@router.post("/{sync_id}/retry", response_model=GuardianSyncResponse)
async def retry_sync(
    sync_id: str,
    data: GuardianSyncRetry,
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncResponse:
    """Tenta reprocessar uma sincronização falha."""
    repo = GuardianSyncRepository(db)
    sync = await repo.get_by_id(sync_id)

    if not sync:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )

    if not sync.can_retry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sincronização não pode ser reprocessada",
        )

    sync = await repo.retry(sync_id, notes=data.notes)
    logger.info(f"Sincronização reprocessando: {sync.sync_code}")
    return GuardianSyncResponse.model_validate(sync)


@router.post("/{sync_id}/mark-completed", response_model=GuardianSyncResponse)
async def mark_sync_completed(
    sync_id: str,
    external_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncResponse:
    """Marca uma sincronização como concluída."""
    repo = GuardianSyncRepository(db)
    sync = await repo.mark_completed(sync_id, external_id=external_id)

    if not sync:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )

    logger.info(f"Sincronização concluída: {sync.sync_code}")
    return GuardianSyncResponse.model_validate(sync)


@router.post("/{sync_id}/mark-failed", response_model=GuardianSyncResponse)
async def mark_sync_failed(
    sync_id: str,
    error: str = Query(..., description="Mensagem de erro"),
    db: AsyncSession = Depends(get_db),
) -> GuardianSyncResponse:
    """Marca uma sincronização como falha."""
    repo = GuardianSyncRepository(db)
    sync = await repo.mark_failed(sync_id, error)

    if not sync:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )

    logger.warning(f"Sincronização falhou: {sync.sync_code} - {error}")
    return GuardianSyncResponse.model_validate(sync)


@router.delete("/{sync_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sync(
    sync_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma sincronização (soft delete)."""
    repo = GuardianSyncRepository(db)
    deleted = await repo.delete(sync_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sincronização não encontrada",
        )
