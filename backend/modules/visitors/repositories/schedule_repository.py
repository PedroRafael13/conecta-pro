"""Repository para VisitorSchedule."""

import logging
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.models.schedule import ScheduleStatus, VisitorSchedule
from modules.visitors.schemas.schedule import ScheduleCreate, ScheduleFilter, ScheduleUpdate

logger = logging.getLogger(__name__)


class ScheduleRepository:
    """Repository para operações de VisitorSchedule."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: ScheduleCreate) -> VisitorSchedule:
        """Cria um novo agendamento."""
        schedule = VisitorSchedule(**data.model_dump(exclude_none=True))
        self.session.add(schedule)
        await self.session.flush()
        await self.session.refresh(schedule)
        logger.info(f"Agendamento criado: {schedule.code}")
        return schedule

    async def get_by_id(self, schedule_id: str | UUID) -> Optional[VisitorSchedule]:
        """Busca agendamento por ID."""
        if isinstance(schedule_id, str):
            schedule_id = UUID(schedule_id)

        result = await self.session.execute(
            select(VisitorSchedule).where(
                and_(
                    VisitorSchedule.id == schedule_id,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[VisitorSchedule]:
        """Busca agendamento por código."""
        result = await self.session.execute(
            select(VisitorSchedule).where(
                and_(
                    VisitorSchedule.code == code,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_qr_code(self, qr_code: str) -> Optional[VisitorSchedule]:
        """Busca agendamento por QR Code."""
        result = await self.session.execute(
            select(VisitorSchedule).where(
                and_(
                    VisitorSchedule.qr_code == qr_code,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_confirmation_code(
        self, confirmation_code: str, condominium_id: str
    ) -> Optional[VisitorSchedule]:
        """Busca agendamento por código de confirmação."""
        result = await self.session.execute(
            select(VisitorSchedule).where(
                and_(
                    VisitorSchedule.confirmation_code == confirmation_code,
                    VisitorSchedule.condominium_id == condominium_id,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, schedule_id: str | UUID, data: ScheduleUpdate
    ) -> Optional[VisitorSchedule]:
        """Atualiza um agendamento."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        await self.session.flush()
        return schedule

    async def delete(self, schedule_id: str | UUID) -> bool:
        """Deleta um agendamento (soft delete)."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return False

        schedule.soft_delete()
        await self.session.flush()
        return True

    async def list_with_filters(
        self,
        filters: Optional[ScheduleFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "scheduled_date",
        order_desc: bool = False,
    ) -> tuple[list[VisitorSchedule], int]:
        """Lista agendamentos com filtros."""
        query = select(VisitorSchedule).where(VisitorSchedule.is_deleted.is_(False))

        if filters:
            if filters.visitor_id:
                query = query.where(VisitorSchedule.visitor_id == filters.visitor_id)
            if filters.visitor_name:
                query = query.where(
                    VisitorSchedule.visitor_name.ilike(f"%{filters.visitor_name}%")
                )
            if filters.condominium_id:
                query = query.where(
                    VisitorSchedule.condominium_id == filters.condominium_id
                )
            if filters.unit_id:
                query = query.where(VisitorSchedule.unit_id == filters.unit_id)
            if filters.resident_id:
                query = query.where(VisitorSchedule.resident_id == filters.resident_id)
            if filters.status:
                query = query.where(VisitorSchedule.status == filters.status)
            if filters.priority:
                query = query.where(VisitorSchedule.priority == filters.priority)
            if filters.scheduled_date:
                query = query.where(
                    VisitorSchedule.scheduled_date == filters.scheduled_date
                )
            if filters.scheduled_date_from:
                query = query.where(
                    VisitorSchedule.scheduled_date >= filters.scheduled_date_from
                )
            if filters.scheduled_date_until:
                query = query.where(
                    VisitorSchedule.scheduled_date <= filters.scheduled_date_until
                )
            if filters.has_vehicle is not None:
                query = query.where(VisitorSchedule.has_vehicle == filters.has_vehicle)
            if filters.needs_parking is not None:
                query = query.where(
                    VisitorSchedule.needs_parking == filters.needs_parking
                )
            if filters.confirmation_required is not None:
                query = query.where(
                    VisitorSchedule.confirmation_required
                    == filters.confirmation_required
                )
            if filters.is_confirmed is not None:
                if filters.is_confirmed:
                    query = query.where(
                        VisitorSchedule.status == ScheduleStatus.CONFIRMADO
                    )
                else:
                    query = query.where(
                        VisitorSchedule.status != ScheduleStatus.CONFIRMADO
                    )
            if filters.requires_approval is not None:
                query = query.where(
                    VisitorSchedule.requires_approval == filters.requires_approval
                )
            if filters.is_approved is not None:
                if filters.is_approved:
                    query = query.where(VisitorSchedule.approved_at.isnot(None))
                else:
                    query = query.where(VisitorSchedule.approved_at.is_(None))
            if filters.is_today is not None:
                today = datetime.utcnow().date()
                if filters.is_today:
                    query = query.where(VisitorSchedule.scheduled_date == today)
                else:
                    query = query.where(VisitorSchedule.scheduled_date != today)

        # Contar total
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Ordenar
        order_column = getattr(
            VisitorSchedule, order_by, VisitorSchedule.scheduled_date
        )
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        # Paginar
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_today(
        self, condominium_id: str, skip: int = 0, limit: int = 50
    ) -> list[VisitorSchedule]:
        """Lista agendamentos de hoje."""
        today = datetime.utcnow().date()

        result = await self.session.execute(
            select(VisitorSchedule)
            .where(
                and_(
                    VisitorSchedule.condominium_id == condominium_id,
                    VisitorSchedule.scheduled_date == today,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
            .order_by(VisitorSchedule.scheduled_time_from.asc().nulls_last())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(
        self, condominium_id: str = None, skip: int = 0, limit: int = 20
    ) -> list[VisitorSchedule]:
        """Lista agendamentos pendentes."""
        query = select(VisitorSchedule).where(
            and_(
                VisitorSchedule.status == ScheduleStatus.PENDENTE,
                VisitorSchedule.scheduled_date >= datetime.utcnow().date(),
                VisitorSchedule.is_deleted.is_(False),
            )
        )

        if condominium_id:
            query = query.where(VisitorSchedule.condominium_id == condominium_id)

        query = query.order_by(VisitorSchedule.scheduled_date.asc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_date(
        self, condominium_id: str, scheduled_date: date
    ) -> list[VisitorSchedule]:
        """Lista agendamentos por data."""
        result = await self.session.execute(
            select(VisitorSchedule)
            .where(
                and_(
                    VisitorSchedule.condominium_id == condominium_id,
                    VisitorSchedule.scheduled_date == scheduled_date,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
            .order_by(VisitorSchedule.scheduled_time_from.asc().nulls_last())
        )
        return list(result.scalars().all())

    async def get_by_resident(
        self, resident_id: str, skip: int = 0, limit: int = 20
    ) -> list[VisitorSchedule]:
        """Lista agendamentos de um morador."""
        result = await self.session.execute(
            select(VisitorSchedule)
            .where(
                and_(
                    VisitorSchedule.resident_id == resident_id,
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
            .order_by(VisitorSchedule.scheduled_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_needing_reminder(self, hours_before: int = 24) -> list[VisitorSchedule]:
        """Lista agendamentos que precisam de lembrete."""
        now = datetime.utcnow()
        target_date = (now + timedelta(hours=hours_before)).date()

        result = await self.session.execute(
            select(VisitorSchedule)
            .where(
                and_(
                    VisitorSchedule.scheduled_date == target_date,
                    VisitorSchedule.status.in_([
                        ScheduleStatus.PENDENTE,
                        ScheduleStatus.CONFIRMADO,
                    ]),
                    VisitorSchedule.reminder_sent.is_(False),
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
            .order_by(VisitorSchedule.scheduled_time_from.asc().nulls_last())
        )
        return list(result.scalars().all())

    async def confirm(
        self,
        schedule_id: str | UUID,
        confirmed_by_id: str = None,
        confirmed_by_name: str = None,
    ) -> Optional[VisitorSchedule]:
        """Confirma um agendamento."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.confirm(confirmed_by_id, confirmed_by_name)
        await self.session.flush()
        logger.info(f"Agendamento confirmado: {schedule.code}")
        return schedule

    async def cancel(
        self,
        schedule_id: str | UUID,
        reason: str = None,
        cancelled_by_id: str = None,
        cancelled_by_name: str = None,
    ) -> Optional[VisitorSchedule]:
        """Cancela um agendamento."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.cancel(reason, cancelled_by_id, cancelled_by_name)
        await self.session.flush()
        logger.info(f"Agendamento cancelado: {schedule.code}")
        return schedule

    async def check_in(self, schedule_id: str | UUID) -> Optional[VisitorSchedule]:
        """Registra check-in."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.check_in()
        await self.session.flush()
        logger.info(f"Check-in: {schedule.code}")
        return schedule

    async def check_out(self, schedule_id: str | UUID) -> Optional[VisitorSchedule]:
        """Registra check-out."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.check_out()
        await self.session.flush()
        return schedule

    async def no_show(self, schedule_id: str | UUID) -> Optional[VisitorSchedule]:
        """Marca como não compareceu."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None

        schedule.no_show()
        await self.session.flush()
        logger.info(f"No-show: {schedule.code}")
        return schedule

    async def expire_past(self) -> int:
        """Expira agendamentos passados não realizados."""
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()

        result = await self.session.execute(
            select(VisitorSchedule).where(
                and_(
                    VisitorSchedule.scheduled_date < yesterday,
                    VisitorSchedule.status.in_([
                        ScheduleStatus.PENDENTE,
                        ScheduleStatus.CONFIRMADO,
                    ]),
                    VisitorSchedule.is_deleted.is_(False),
                )
            )
        )

        schedules = result.scalars().all()
        count = 0
        for schedule in schedules:
            schedule.expire()
            count += 1

        await self.session.flush()
        return count

    async def get_stats(
        self, condominium_id: str = None, date_from: date = None
    ) -> dict:
        """Retorna estatísticas de agendamentos."""
        base_cond = [VisitorSchedule.is_deleted.is_(False)]

        if condominium_id:
            base_cond.append(VisitorSchedule.condominium_id == condominium_id)
        if date_from:
            base_cond.append(VisitorSchedule.scheduled_date >= date_from)

        # Total
        total_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorSchedule)
            .where(and_(*base_cond))
        )
        total = total_result.scalar() or 0

        # Por status
        status_query = (
            select(VisitorSchedule.status, func.count())
            .where(and_(*base_cond))
            .group_by(VisitorSchedule.status)
        )
        status_result = await self.session.execute(status_query)
        by_status = {str(row[0].value): row[1] for row in status_result.all()}

        # Por prioridade
        priority_query = (
            select(VisitorSchedule.priority, func.count())
            .where(and_(*base_cond))
            .group_by(VisitorSchedule.priority)
        )
        priority_result = await self.session.execute(priority_query)
        by_priority = {str(row[0].value): row[1] for row in priority_result.all()}

        # Por dia da semana
        dow_query = (
            select(extract("dow", VisitorSchedule.scheduled_date), func.count())
            .where(and_(*base_cond))
            .group_by(extract("dow", VisitorSchedule.scheduled_date))
        )
        dow_result = await self.session.execute(dow_query)
        by_dow = {str(int(row[0])): row[1] for row in dow_result.all()}

        # Com veículo
        vehicle_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorSchedule)
            .where(and_(*base_cond, VisitorSchedule.has_vehicle.is_(True)))
        )
        with_vehicle = vehicle_result.scalar() or 0

        # Com acompanhantes
        companions_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorSchedule)
            .where(and_(*base_cond, VisitorSchedule.companions_count > 0))
        )
        with_companions = companions_result.scalar() or 0

        # Total acompanhantes
        total_companions_result = await self.session.execute(
            select(func.sum(VisitorSchedule.companions_count)).where(and_(*base_cond))
        )
        total_companions = total_companions_result.scalar() or 0

        # Taxa de reagendamento
        reschedule_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorSchedule)
            .where(and_(*base_cond, VisitorSchedule.reschedule_count > 0))
        )
        rescheduled = reschedule_result.scalar() or 0
        reschedule_rate = (rescheduled / total * 100) if total > 0 else 0

        # Taxa de no-show
        no_show_result = await self.session.execute(
            select(func.count())
            .select_from(VisitorSchedule)
            .where(
                and_(*base_cond, VisitorSchedule.status == ScheduleStatus.NAO_COMPARECEU)
            )
        )
        no_show = no_show_result.scalar() or 0
        no_show_rate = (no_show / total * 100) if total > 0 else 0

        return {
            "total": total,
            "pending": by_status.get("pendente", 0),
            "confirmed": by_status.get("confirmado", 0),
            "cancelled": by_status.get("cancelado", 0),
            "realized": by_status.get("realizado", 0),
            "no_show": no_show,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_day_of_week": by_dow,
            "with_vehicle": with_vehicle,
            "with_companions": with_companions,
            "total_companions": int(total_companions),
            "reschedule_rate": round(reschedule_rate, 2),
            "no_show_rate": round(no_show_rate, 2),
        }
