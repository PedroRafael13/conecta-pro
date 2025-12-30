"""Controller para VisitorLog."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from modules.visitors.models.log import AccessMethod, AccessPoint, AccessType, DenialReason
from modules.visitors.schemas.log import (
    LogDeny,
    LogEntry,
    LogExit,
    LogFilter,
    LogListResponse,
    LogResponse,
    LogStats,
    LogTimeline,
    VisitorInside,
)
from modules.visitors.services.log_service import LogService

router = APIRouter(prefix="/visitor-logs", tags=["Visitor Logs"])


# ========== Registro de Acesso ==========


@router.post("/entry", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def register_entry(
    data: LogEntry,
    session: AsyncSession = Depends(get_session),
):
    """Registra entrada de visitante."""
    service = LogService(session)
    return await service.register_entry(data)


@router.post("/exit", response_model=LogResponse)
async def register_exit(
    data: LogExit,
    session: AsyncSession = Depends(get_session),
):
    """Registra saída de visitante."""
    service = LogService(session)
    log = await service.register_exit(data)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível registrar a saída",
        )
    return log


@router.post("/deny", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def register_denial(
    data: LogDeny,
    session: AsyncSession = Depends(get_session),
):
    """Registra negativa de acesso."""
    service = LogService(session)
    return await service.register_denial(data)


# ========== Listagem ==========


@router.get("/", response_model=LogListResponse)
async def list_logs(
    visitor_id: Optional[UUID] = None,
    condominium_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    resident_id: Optional[str] = None,
    access_type: Optional[AccessType] = None,
    access_method: Optional[AccessMethod] = None,
    access_point: Optional[AccessPoint] = None,
    denied: Optional[bool] = None,
    denial_reason: Optional[DenialReason] = None,
    has_vehicle: Optional[bool] = None,
    has_companions: Optional[bool] = None,
    operator_id: Optional[str] = None,
    timestamp_from: Optional[datetime] = None,
    timestamp_until: Optional[datetime] = None,
    is_still_inside: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = "timestamp",
    order_desc: bool = True,
    session: AsyncSession = Depends(get_session),
):
    """Lista logs com filtros."""
    filters = LogFilter(
        visitor_id=visitor_id,
        condominium_id=condominium_id,
        unit_id=unit_id,
        resident_id=resident_id,
        access_type=access_type,
        access_method=access_method,
        access_point=access_point,
        denied=denied,
        denial_reason=denial_reason,
        has_vehicle=has_vehicle,
        has_companions=has_companions,
        operator_id=operator_id,
        timestamp_from=timestamp_from,
        timestamp_until=timestamp_until,
        is_still_inside=is_still_inside,
    )
    service = LogService(session)
    return await service.list(filters, page, page_size, order_by, order_desc)


@router.get("/stats", response_model=LogStats)
async def get_log_stats(
    condominium_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
):
    """Retorna estatísticas de logs."""
    service = LogService(session)
    return await service.get_stats(condominium_id, date_from)


@router.get("/inside/{condominium_id}", response_model=list[VisitorInside])
async def get_visitors_inside(
    condominium_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
):
    """Lista visitantes atualmente dentro."""
    service = LogService(session)
    return await service.get_inside(condominium_id, page, page_size)


@router.get("/inside/{condominium_id}/count", response_model=dict)
async def count_visitors_inside(
    condominium_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Conta visitantes dentro."""
    service = LogService(session)
    count = await service.count_inside(condominium_id)
    return {"count": count}


@router.get("/denied", response_model=LogListResponse)
async def get_denied_logs(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista acessos negados."""
    service = LogService(session)
    return await service.get_denied(condominium_id, page, page_size)


@router.get("/by-date-range/{condominium_id}", response_model=LogListResponse)
async def get_logs_by_date_range(
    condominium_id: str,
    date_from: datetime = Query(...),
    date_until: datetime = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """Lista logs por período."""
    service = LogService(session)
    return await service.get_by_date_range(condominium_id, date_from, date_until)


@router.get("/timeline/{visitor_id}", response_model=LogTimeline)
async def get_visitor_timeline(
    visitor_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
):
    """Retorna timeline de logs de um visitante."""
    service = LogService(session)
    return await service.get_visitor_timeline(visitor_id, limit)


@router.get("/is-inside/{visitor_id}/{condominium_id}", response_model=dict)
async def check_visitor_inside(
    visitor_id: UUID,
    condominium_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Verifica se visitante está dentro."""
    service = LogService(session)
    is_inside = await service.is_visitor_inside(visitor_id, condominium_id)
    return {"is_inside": is_inside}


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Busca log por ID."""
    service = LogService(session)
    log = await service.get_by_id(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log não encontrado",
        )
    return log


# ========== Ações ==========


@router.post("/{log_id}/notify-resident", response_model=LogResponse)
async def notify_resident(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Marca morador como notificado."""
    service = LogService(session)
    log = await service.notify_resident(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log não encontrado",
        )
    return log
