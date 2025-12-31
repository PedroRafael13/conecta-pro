"""Repository para férias."""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.employee_portal.models import (
    VacationPeriod,
    VacationRequest,
    VacationStatus,
    VacationType,
)
from modules.hr.employee_portal.schemas import (
    VacationPeriodCreate,
    VacationRequestCreate,
    VacationRequestUpdate,
)

logger = logging.getLogger(__name__)


class VacationPeriodRepository:
    """Repository para períodos aquisitivos de férias."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: VacationPeriodCreate,
        condominio_id: UUID,
    ) -> VacationPeriod:
        """Cria novo período aquisitivo."""
        period = VacationPeriod(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=data.employee_id,
            start_date=data.start_date,
            end_date=data.end_date,
            concession_start=data.concession_start,
            concession_end=data.concession_end,
            total_days_entitled=data.total_days_entitled,
            days_remaining=data.total_days_entitled,
            absences_count=data.absences_count,
            expires_at=data.concession_end,
        )

        self.db.add(period)
        await self.db.commit()
        await self.db.refresh(period)

        logger.info("Período aquisitivo %s criado para funcionário %s", period.id, data.employee_id)
        return period

    async def get_by_id(self, period_id: UUID) -> Optional[VacationPeriod]:
        """Busca período por ID."""
        result = await self.db.execute(
            select(VacationPeriod).where(VacationPeriod.id == period_id)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: UUID,
        *,
        include_expired: bool = False,
        include_fully_used: bool = False,
    ) -> List[VacationPeriod]:
        """Lista períodos do funcionário."""
        query = select(VacationPeriod).where(
            VacationPeriod.employee_id == employee_id
        )

        if not include_expired:
            query = query.where(VacationPeriod.is_expired.is_(False))

        if not include_fully_used:
            query = query.where(VacationPeriod.is_fully_used.is_(False))

        query = query.order_by(desc(VacationPeriod.start_date))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_available_days(self, employee_id: UUID) -> int:
        """Retorna total de dias disponíveis."""
        result = await self.db.execute(
            select(func.sum(VacationPeriod.days_remaining)).where(
                and_(
                    VacationPeriod.employee_id == employee_id,
                    VacationPeriod.is_expired.is_(False),
                    VacationPeriod.is_fully_used.is_(False),
                )
            )
        )
        return result.scalar() or 0

    async def use_days(
        self,
        period_id: UUID,
        days: int,
        *,
        sell_days: int = 0,
    ) -> Optional[VacationPeriod]:
        """Usa dias do período."""
        period = await self.get_by_id(period_id)
        if not period:
            return None

        if days + sell_days > period.days_remaining:
            raise ValueError("Dias solicitados excedem o saldo disponível")

        period.days_used += days
        period.days_sold += sell_days
        period.days_remaining = period.total_days_entitled - period.days_used - period.days_sold

        if period.days_remaining == 0:
            period.is_fully_used = True

        await self.db.commit()
        await self.db.refresh(period)

        return period

    async def check_expiring_periods(
        self,
        days_ahead: int = 30,
    ) -> List[VacationPeriod]:
        """Busca períodos prestes a expirar."""
        target_date = date.today() + timedelta(days=days_ahead)
        result = await self.db.execute(
            select(VacationPeriod).where(
                and_(
                    VacationPeriod.is_expired.is_(False),
                    VacationPeriod.is_fully_used.is_(False),
                    VacationPeriod.concession_end <= target_date,
                    VacationPeriod.days_remaining > 0,
                )
            )
        )
        return list(result.scalars().all())


class VacationRequestRepository:
    """Repository para solicitações de férias."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: VacationRequestCreate,
        condominio_id: UUID,
        *,
        created_by: Optional[UUID] = None,
    ) -> VacationRequest:
        """Cria nova solicitação de férias."""
        request = VacationRequest(
            id=uuid4(),
            condominio_id=condominio_id,
            employee_id=created_by or uuid4(),  # Será o funcionário logado
            vacation_period_id=data.vacation_period_id,
            request_code=self._generate_code(),
            vacation_type=data.vacation_type.value,
            status=VacationStatus.DRAFT.value,
            start_date=data.start_date,
            end_date=data.end_date,
            days_requested=data.days_requested,
            sell_days=data.sell_days,
            sell_requested=data.sell_requested,
            advance_13th_requested=data.advance_13th_requested,
            employee_notes=data.employee_notes,
            substitute_employee_id=data.substitute_employee_id,
            return_date=data.end_date + timedelta(days=1),
            created_by=created_by,
        )

        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)

        logger.info("Solicitação de férias %s criada", request.request_code)
        return request

    def _generate_code(self) -> str:
        """Gera código único da solicitação."""
        import random
        import string
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"FER{suffix}"

    async def get_by_id(self, request_id: UUID) -> Optional[VacationRequest]:
        """Busca solicitação por ID."""
        result = await self.db.execute(
            select(VacationRequest).where(VacationRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[VacationRequest]:
        """Busca solicitação por código."""
        result = await self.db.execute(
            select(VacationRequest).where(VacationRequest.request_code == code)
        )
        return result.scalar_one_or_none()

    async def list_by_employee(
        self,
        employee_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[VacationStatus] = None,
    ) -> Tuple[List[VacationRequest], int]:
        """Lista solicitações do funcionário."""
        query = select(VacationRequest).where(
            VacationRequest.employee_id == employee_id
        )

        if status:
            query = query.where(VacationRequest.status == status.value)

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(desc(VacationRequest.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_pending_approval(
        self,
        condominio_id: UUID,
        *,
        manager_level: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[VacationRequest], int]:
        """Lista solicitações pendentes de aprovação."""
        query = select(VacationRequest).where(
            and_(
                VacationRequest.condominio_id == condominio_id,
                VacationRequest.status == VacationStatus.PENDING.value,
            )
        )

        if manager_level:
            query = query.where(VacationRequest.manager_approved.is_(None))
        else:
            query = query.where(
                and_(
                    VacationRequest.manager_approved.is_(True),
                    VacationRequest.hr_approved.is_(None),
                )
            )

        # Total
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Paginação
        query = query.order_by(VacationRequest.start_date)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def update(
        self,
        request_id: UUID,
        data: VacationRequestUpdate,
    ) -> Optional[VacationRequest]:
        """Atualiza solicitação de férias."""
        request = await self.get_by_id(request_id)
        if not request:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(request, field, value)

        request.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(request)

        return request

    async def submit(self, request_id: UUID) -> Optional[VacationRequest]:
        """Submete solicitação para aprovação."""
        request = await self.get_by_id(request_id)
        if not request:
            return None

        if request.status != VacationStatus.DRAFT.value:
            raise ValueError("Apenas rascunhos podem ser submetidos")

        request.status = VacationStatus.PENDING.value
        request.submitted_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(request)

        logger.info("Solicitação de férias %s submetida", request.request_code)
        return request

    async def approve_manager(
        self,
        request_id: UUID,
        approved: bool,
        *,
        approved_by: UUID,
        notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
    ) -> Optional[VacationRequest]:
        """Aprovação do gestor."""
        request = await self.get_by_id(request_id)
        if not request:
            return None

        request.manager_approved = approved
        request.manager_approved_at = datetime.utcnow()
        request.manager_approved_by = approved_by
        request.manager_notes = notes

        if not approved:
            request.status = VacationStatus.REJECTED.value
            request.manager_rejection_reason = rejection_reason

        await self.db.commit()
        await self.db.refresh(request)

        logger.info(
            "Férias %s %s pelo gestor",
            request.request_code,
            "aprovadas" if approved else "rejeitadas",
        )
        return request

    async def approve_hr(
        self,
        request_id: UUID,
        approved: bool,
        *,
        approved_by: UUID,
        notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
    ) -> Optional[VacationRequest]:
        """Aprovação do RH."""
        request = await self.get_by_id(request_id)
        if not request:
            return None

        request.hr_approved = approved
        request.hr_approved_at = datetime.utcnow()
        request.hr_approved_by = approved_by
        request.hr_notes = notes

        if approved:
            request.status = VacationStatus.APPROVED.value
        else:
            request.status = VacationStatus.REJECTED.value
            request.hr_rejection_reason = rejection_reason

        await self.db.commit()
        await self.db.refresh(request)

        logger.info(
            "Férias %s %s pelo RH",
            request.request_code,
            "aprovadas" if approved else "rejeitadas",
        )
        return request

    async def schedule(
        self,
        request_id: UUID,
        *,
        scheduled_by: UUID,
        payment_date: date,
    ) -> Optional[VacationRequest]:
        """Programa férias aprovadas."""
        request = await self.get_by_id(request_id)
        if not request:
            return None

        if not request.is_approved:
            raise ValueError("Férias não estão aprovadas")

        request.status = VacationStatus.SCHEDULED.value
        request.scheduled_at = datetime.utcnow()
        request.scheduled_by = scheduled_by
        request.payment_date = payment_date

        await self.db.commit()
        await self.db.refresh(request)

        logger.info("Férias %s programadas para %s", request.request_code, request.start_date)
        return request

    async def cancel(
        self,
        request_id: UUID,
        reason: str,
        *,
        cancelled_by: UUID,
    ) -> Optional[VacationRequest]:
        """Cancela solicitação de férias."""
        request = await self.get_by_id(request_id)
        if not request:
            return None

        if not request.can_cancel:
            raise ValueError("Férias não podem ser canceladas neste status")

        request.status = VacationStatus.CANCELLED.value
        request.cancelled_at = datetime.utcnow()
        request.cancelled_by = cancelled_by
        request.cancel_reason = reason

        await self.db.commit()
        await self.db.refresh(request)

        logger.info("Férias %s canceladas", request.request_code)
        return request

    async def check_date_conflict(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
        *,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        """Verifica conflito de datas com outras solicitações."""
        query = select(VacationRequest).where(
            and_(
                VacationRequest.employee_id == employee_id,
                VacationRequest.status.in_([
                    VacationStatus.PENDING.value,
                    VacationStatus.APPROVED.value,
                    VacationStatus.SCHEDULED.value,
                    VacationStatus.IN_PROGRESS.value,
                ]),
                VacationRequest.start_date <= end_date,
                VacationRequest.end_date >= start_date,
            )
        )

        if exclude_id:
            query = query.where(VacationRequest.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_upcoming(
        self,
        condominio_id: UUID,
        days_ahead: int = 30,
    ) -> List[VacationRequest]:
        """Retorna férias programadas para os próximos dias."""
        target_date = date.today() + timedelta(days=days_ahead)
        result = await self.db.execute(
            select(VacationRequest).where(
                and_(
                    VacationRequest.condominio_id == condominio_id,
                    VacationRequest.status == VacationStatus.SCHEDULED.value,
                    VacationRequest.start_date <= target_date,
                    VacationRequest.start_date >= date.today(),
                )
            ).order_by(VacationRequest.start_date)
        )
        return list(result.scalars().all())
