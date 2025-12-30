"""Controller para VisitorSchedule."""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from modules.visitors.models.schedule import SchedulePriority, ScheduleStatus
from modules.visitors.schemas.schedule import (
    ScheduleCalendar,
    ScheduleCancel,
    ScheduleConfirm,
    ScheduleCreate,
    ScheduleFilter,
    ScheduleListResponse,
    ScheduleReschedule,
    ScheduleResponse,
    ScheduleStats,
    ScheduleUpdate,
)
from modules.visitors.services.schedule_service import ScheduleService

router = APIRouter(prefix="/visitor-schedules", tags=["Visitor Schedules"])


# ========== CRUD ==========


@router.post(
    "/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED
)
async def create_schedule(
    data: ScheduleCreate,
    session: AsyncSession = Depends(get_session),
):
    """Cria um novo agendamento."""
    service = ScheduleService(session)
    return await service.create(data)


@router.get("/", response_model=ScheduleListResponse)
async def list_schedules(
    visitor_id: Optional[UUID] = None,
    condominium_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    resident_id: Optional[str] = None,
    schedule_status: Optional[ScheduleStatus] = Query(None, alias="status"),
    priority: Optional[SchedulePriority] = None,
    date_from: Optional[date] = None,
    date_until: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = "scheduled_date",
    order_desc: bool = False,
    session: AsyncSession = Depends(get_session),
):
    """Lista agendamentos com filtros."""
    filters = ScheduleFilter(
        visitor_id=visitor_id,
        condominium_id=condominium_id,
        unit_id=unit_id,
        resident_id=resident_id,
        status=schedule_status,
        priority=priority,
        date_from=date_from,
        date_until=date_until,
    )
    service = ScheduleService(session)
    return await service.list(filters, page, page_size, order_by, order_desc)


@router.get("/stats", response_model=ScheduleStats)
async def get_schedule_stats(
    condominium_id: Optional[str] = None,
    date_from: Optional[date] = None,
    session: AsyncSession = Depends(get_session),
):
    """Retorna estatísticas de agendamentos."""
    service = ScheduleService(session)
    return await service.get_stats(condominium_id, date_from)


@router.get("/today/{condominium_id}", response_model=ScheduleListResponse)
async def get_today_schedules(
    condominium_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista agendamentos de hoje."""
    service = ScheduleService(session)
    return await service.get_today(condominium_id, page, page_size)


@router.get("/pending", response_model=ScheduleListResponse)
async def get_pending_schedules(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista agendamentos pendentes."""
    service = ScheduleService(session)
    return await service.get_pending(condominium_id, page, page_size)


@router.get("/by-date/{condominium_id}", response_model=list[ScheduleResponse])
async def get_schedules_by_date(
    condominium_id: str,
    scheduled_date: date = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """Lista agendamentos por data."""
    service = ScheduleService(session)
    return await service.get_by_date(condominium_id, scheduled_date)


@router.get("/by-resident/{resident_id}", response_model=ScheduleListResponse)
async def get_schedules_by_resident(
    resident_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista agendamentos de um morador."""
    service = ScheduleService(session)
    return await service.get_by_resident(resident_id, page, page_size)


@router.get("/calendar/{condominium_id}", response_model=list[ScheduleCalendar])
async def get_schedule_calendar(
    condominium_id: str,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    session: AsyncSession = Depends(get_session),
):
    """Retorna calendário de agendamentos do mês."""
    service = ScheduleService(session)
    return await service.get_calendar(condominium_id, month, year)


@router.get("/needing-reminder", response_model=list[ScheduleResponse])
async def get_schedules_needing_reminder(
    hours_before: int = Query(24, ge=1, le=72),
    session: AsyncSession = Depends(get_session),
):
    """Lista agendamentos que precisam de lembrete."""
    service = ScheduleService(session)
    return await service.get_needing_reminder(hours_before)


@router.get("/by-code/{code}", response_model=ScheduleResponse)
async def get_schedule_by_code(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    """Busca agendamento por código."""
    service = ScheduleService(session)
    schedule = await service.get_by_code(code)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.get("/by-qr/{qr_code}", response_model=ScheduleResponse)
async def get_schedule_by_qr_code(
    qr_code: str,
    session: AsyncSession = Depends(get_session),
):
    """Busca agendamento por QR Code."""
    service = ScheduleService(session)
    schedule = await service.get_by_qr_code(qr_code)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Busca agendamento por ID."""
    service = ScheduleService(session)
    schedule = await service.get_by_id(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    data: ScheduleUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza um agendamento."""
    service = ScheduleService(session)
    schedule = await service.update(schedule_id, data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Deleta um agendamento."""
    service = ScheduleService(session)
    if not await service.delete(schedule_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )


# ========== Ações ==========


@router.post("/{schedule_id}/confirm", response_model=ScheduleResponse)
async def confirm_schedule(
    schedule_id: UUID,
    data: ScheduleConfirm,
    session: AsyncSession = Depends(get_session),
):
    """Confirma um agendamento."""
    service = ScheduleService(session)
    schedule = await service.confirm(schedule_id, data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.post("/{schedule_id}/cancel", response_model=ScheduleResponse)
async def cancel_schedule(
    schedule_id: UUID,
    data: ScheduleCancel,
    session: AsyncSession = Depends(get_session),
):
    """Cancela um agendamento."""
    service = ScheduleService(session)
    schedule = await service.cancel(schedule_id, data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.post("/{schedule_id}/reschedule", response_model=ScheduleResponse)
async def reschedule_schedule(
    schedule_id: UUID,
    data: ScheduleReschedule,
    session: AsyncSession = Depends(get_session),
):
    """Reagenda um agendamento."""
    service = ScheduleService(session)
    schedule = await service.reschedule(schedule_id, data)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.post("/{schedule_id}/check-in", response_model=ScheduleResponse)
async def check_in_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Registra check-in do visitante."""
    service = ScheduleService(session)
    schedule = await service.check_in(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível realizar check-in",
        )
    return schedule


@router.post("/{schedule_id}/check-out", response_model=ScheduleResponse)
async def check_out_schedule(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Registra check-out do visitante."""
    service = ScheduleService(session)
    schedule = await service.check_out(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível realizar check-out",
        )
    return schedule


@router.post("/{schedule_id}/no-show", response_model=ScheduleResponse)
async def mark_no_show(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Marca como não compareceu."""
    service = ScheduleService(session)
    schedule = await service.no_show(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


@router.post("/{schedule_id}/send-reminder", response_model=ScheduleResponse)
async def send_reminder(
    schedule_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Envia lembrete do agendamento."""
    service = ScheduleService(session)
    schedule = await service.send_reminder(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )
    return schedule


# ========== Validação ==========


@router.post("/validate-code", response_model=ScheduleResponse)
async def validate_confirmation_code(
    confirmation_code: str = Query(..., min_length=6),
    condominium_id: str = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """Valida agendamento por código de confirmação."""
    service = ScheduleService(session)
    schedule = await service.validate_by_confirmation_code(
        confirmation_code, condominium_id
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido ou agendamento não pode ser utilizado",
        )
    return schedule


# ========== Manutenção ==========


@router.post("/expire-past", response_model=dict)
async def expire_past_schedules(
    session: AsyncSession = Depends(get_session),
):
    """Expira agendamentos passados não realizados."""
    service = ScheduleService(session)
    count = await service.expire_past()
    return {"expired_count": count}
