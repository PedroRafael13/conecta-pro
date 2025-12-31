"""Controller para eventos REP."""

import logging
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user
from modules.hr.rep_integration.repositories import REPEventRepository
from modules.hr.rep_integration.services import EventProcessorService, SyncService
from modules.hr.rep_integration.schemas import (
    REPEventResponse,
    REPEventList,
    REPEventFilter,
    REPEventProcess,
    REPEventProcessResult,
    REPEventStats,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["REP Events"])


@router.get("/", response_model=REPEventList)
async def list_events(
    device_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    employee_id: Optional[UUID] = None,
    pis_number: Optional[str] = None,
    event_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    has_employee: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> REPEventList:
    """Lista eventos de ponto."""
    repo = REPEventRepository(db)

    filters = REPEventFilter(
        device_id=device_id,
        condominio_id=condominio_id,
        employee_id=employee_id,
        pis_number=pis_number,
        event_type=event_type,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        has_employee=has_employee,
    )

    events, total = await repo.list_events(filters, page, page_size)

    return REPEventList(
        items=events,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{event_id}", response_model=REPEventResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> REPEventResponse:
    """Obtém evento por ID."""
    repo = REPEventRepository(db)
    event = await repo.get_by_id(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado",
        )

    return event


@router.post("/process", response_model=dict)
async def process_pending_events(
    device_id: Optional[UUID] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Processa eventos pendentes."""
    processor = EventProcessorService(db)
    return await processor.process_pending_events(device_id, limit)


@router.post("/{event_id}/link", response_model=REPEventProcessResult)
async def link_event_to_employee(
    event_id: UUID,
    data: REPEventProcess,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> REPEventProcessResult:
    """Vincula evento a funcionário e processa."""
    processor = EventProcessorService(db)

    success = await processor.link_event_to_employee(
        event_id,
        data.employee_id,
    )

    if success:
        event = await REPEventRepository(db).get_by_id(event_id)
        return REPEventProcessResult(
            event_id=event_id,
            success=True,
            time_entry_id=event.time_entry_id if event else None,
        )

    return REPEventProcessResult(
        event_id=event_id,
        success=False,
        error_message="Falha ao processar evento",
    )


@router.post("/link-bulk", response_model=dict)
async def bulk_link_events(
    mappings: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Vincula múltiplos eventos a funcionários."""
    processor = EventProcessorService(db)

    # Converter para formato esperado
    formatted_mappings = [
        {"event_id": UUID(m["event_id"]), "employee_id": UUID(m["employee_id"])}
        for m in mappings
    ]

    return await processor.bulk_link_events(formatted_mappings)


@router.get("/unidentified/list")
async def list_unidentified_events(
    device_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Lista eventos sem funcionário identificado."""
    processor = EventProcessorService(db)
    events = await processor.get_unidentified_events(
        device_id=device_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )

    return {
        "events": [e.to_dict() for e in events],
        "total": len(events),
    }


@router.post("/reprocess-failed")
async def reprocess_failed_events(
    device_id: Optional[UUID] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Reprocessa eventos que falharam."""
    processor = EventProcessorService(db)
    return await processor.reprocess_failed_events(device_id, limit)


@router.get("/statistics/summary", response_model=REPEventStats)
async def get_events_statistics(
    device_id: Optional[UUID] = None,
    condominio_id: Optional[UUID] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> REPEventStats:
    """Retorna estatísticas de eventos."""
    repo = REPEventRepository(db)
    stats = await repo.get_statistics(
        device_id=device_id,
        condominio_id=condominio_id,
        date_from=date_from,
        date_to=date_to,
    )

    return REPEventStats(
        total_events=stats.get("total_events", 0),
        events_by_type=stats.get("events_by_type", {}),
        events_by_status=stats.get("events_by_status", {}),
        events_by_method=stats.get("events_by_method", {}),
        pending_processing=stats.get("pending_processing", 0),
        errors_count=stats.get("errors_count", 0),
        duplicates_count=stats.get("duplicates_count", 0),
        date_range_start=date_from,
        date_range_end=date_to,
    )
