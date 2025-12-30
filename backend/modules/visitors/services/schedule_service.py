"""Service para VisitorSchedule."""

import calendar
import logging
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.repositories.schedule_repository import ScheduleRepository
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

logger = logging.getLogger(__name__)


class ScheduleService:
    """Service para operações de VisitorSchedule."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = ScheduleRepository(session)

    async def create(self, data: ScheduleCreate) -> ScheduleResponse:
        """Cria um novo agendamento."""
        schedule = await self.repository.create(data)
        await self.session.commit()
        await self.session.refresh(schedule)
        return ScheduleResponse.model_validate(schedule)

    async def get_by_id(
        self, schedule_id: str | UUID
    ) -> Optional[ScheduleResponse]:
        """Busca agendamento por ID."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            return None
        return ScheduleResponse.model_validate(schedule)

    async def get_by_code(self, code: str) -> Optional[ScheduleResponse]:
        """Busca agendamento por código."""
        schedule = await self.repository.get_by_code(code)
        if not schedule:
            return None
        return ScheduleResponse.model_validate(schedule)

    async def get_by_qr_code(self, qr_code: str) -> Optional[ScheduleResponse]:
        """Busca agendamento por QR Code."""
        schedule = await self.repository.get_by_qr_code(qr_code)
        if not schedule:
            return None
        return ScheduleResponse.model_validate(schedule)

    async def update(
        self, schedule_id: str | UUID, data: ScheduleUpdate
    ) -> Optional[ScheduleResponse]:
        """Atualiza um agendamento."""
        schedule = await self.repository.update(schedule_id, data)
        if not schedule:
            return None
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def delete(self, schedule_id: str | UUID) -> bool:
        """Deleta um agendamento."""
        result = await self.repository.delete(schedule_id)
        if result:
            await self.session.commit()
        return result

    async def list(
        self,
        filters: Optional[ScheduleFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "scheduled_date",
        order_desc: bool = False,
    ) -> ScheduleListResponse:
        """Lista agendamentos com filtros."""
        skip = (page - 1) * page_size
        schedules, total = await self.repository.list_with_filters(
            filters, skip, page_size, order_by, order_desc
        )

        items = [ScheduleResponse.model_validate(s) for s in schedules]
        pages = (total + page_size - 1) // page_size

        return ScheduleListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_today(
        self, condominium_id: str, page: int = 1, page_size: int = 50
    ) -> ScheduleListResponse:
        """Lista agendamentos de hoje."""
        skip = (page - 1) * page_size
        schedules = await self.repository.get_today(condominium_id, skip, page_size)
        items = [ScheduleResponse.model_validate(s) for s in schedules]
        return ScheduleListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_pending(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> ScheduleListResponse:
        """Lista agendamentos pendentes."""
        skip = (page - 1) * page_size
        schedules = await self.repository.get_pending(condominium_id, skip, page_size)
        items = [ScheduleResponse.model_validate(s) for s in schedules]
        return ScheduleListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_by_date(
        self, condominium_id: str, scheduled_date: date
    ) -> list[ScheduleResponse]:
        """Lista agendamentos por data."""
        schedules = await self.repository.get_by_date(condominium_id, scheduled_date)
        return [ScheduleResponse.model_validate(s) for s in schedules]

    async def get_by_resident(
        self, resident_id: str, page: int = 1, page_size: int = 20
    ) -> ScheduleListResponse:
        """Lista agendamentos de um morador."""
        skip = (page - 1) * page_size
        schedules = await self.repository.get_by_resident(resident_id, skip, page_size)
        items = [ScheduleResponse.model_validate(s) for s in schedules]
        return ScheduleListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_calendar(
        self, condominium_id: str, month: int, year: int
    ) -> list[ScheduleCalendar]:
        """Retorna calendário de agendamentos."""
        # Primeiro e último dia do mês
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])

        result = []
        current = first_day

        while current <= last_day:
            schedules = await self.repository.get_by_date(condominium_id, current)
            schedule_responses = [
                ScheduleResponse.model_validate(s) for s in schedules
            ]

            pending = sum(1 for s in schedules if s.is_pending)
            confirmed = sum(1 for s in schedules if s.is_confirmed)

            result.append(
                ScheduleCalendar(
                    date=current,
                    schedules=schedule_responses,
                    total=len(schedules),
                    pending=pending,
                    confirmed=confirmed,
                )
            )

            current += timedelta(days=1)

        return result

    async def get_stats(
        self, condominium_id: str = None, date_from: date = None
    ) -> ScheduleStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id, date_from)
        return ScheduleStats(**stats)

    async def confirm(
        self, schedule_id: str | UUID, data: ScheduleConfirm
    ) -> Optional[ScheduleResponse]:
        """Confirma um agendamento."""
        schedule = await self.repository.confirm(
            schedule_id, data.confirmed_by_id, data.confirmed_by_name
        )
        if not schedule:
            return None
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def cancel(
        self, schedule_id: str | UUID, data: ScheduleCancel
    ) -> Optional[ScheduleResponse]:
        """Cancela um agendamento."""
        schedule = await self.repository.cancel(
            schedule_id,
            data.reason,
            data.cancelled_by_id,
            data.cancelled_by_name,
        )
        if not schedule:
            return None
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def reschedule(
        self, schedule_id: str | UUID, data: ScheduleReschedule
    ) -> Optional[ScheduleResponse]:
        """Reagenda um agendamento."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.reschedule(data.new_date, data.new_time_from)
        if data.new_time_until:
            schedule.scheduled_time_until = data.new_time_until

        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def check_in(
        self, schedule_id: str | UUID
    ) -> Optional[ScheduleResponse]:
        """Registra check-in."""
        schedule = await self.repository.check_in(schedule_id)
        if not schedule:
            return None
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def check_out(
        self, schedule_id: str | UUID
    ) -> Optional[ScheduleResponse]:
        """Registra check-out."""
        schedule = await self.repository.check_out(schedule_id)
        if not schedule:
            return None
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def no_show(
        self, schedule_id: str | UUID
    ) -> Optional[ScheduleResponse]:
        """Marca como não compareceu."""
        schedule = await self.repository.no_show(schedule_id)
        if not schedule:
            return None
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def expire_past(self) -> int:
        """Expira agendamentos passados."""
        count = await self.repository.expire_past()
        await self.session.commit()
        logger.info(f"{count} agendamentos expirados")
        return count

    async def get_needing_reminder(
        self, hours_before: int = 24
    ) -> list[ScheduleResponse]:
        """Lista agendamentos que precisam de lembrete."""
        schedules = await self.repository.get_needing_reminder(hours_before)
        return [ScheduleResponse.model_validate(s) for s in schedules]

    async def send_reminder(self, schedule_id: str | UUID) -> Optional[ScheduleResponse]:
        """Marca lembrete como enviado."""
        schedule = await self.repository.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.send_reminder()
        await self.session.commit()
        return ScheduleResponse.model_validate(schedule)

    async def validate_by_confirmation_code(
        self, confirmation_code: str, condominium_id: str
    ) -> Optional[ScheduleResponse]:
        """Valida agendamento por código de confirmação."""
        schedule = await self.repository.get_by_confirmation_code(
            confirmation_code, condominium_id
        )
        if not schedule:
            return None

        if not schedule.can_check_in:
            return None

        return ScheduleResponse.model_validate(schedule)
