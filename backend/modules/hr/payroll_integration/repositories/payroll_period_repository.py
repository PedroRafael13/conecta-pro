"""Repository para período de folha de pagamento."""

import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.hr.payroll_integration.models import PayrollPeriod, PeriodStatus, PeriodType
from modules.hr.payroll_integration.schemas import PayrollPeriodCreate, PayrollPeriodUpdate

logger = logging.getLogger(__name__)


class PayrollPeriodRepository:
    """Repository para operações de período de folha."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: PayrollPeriodCreate,
        condominio_id: UUID,
        created_by: UUID = None,
    ) -> PayrollPeriod:
        """Cria novo período de folha."""
        period = PayrollPeriod(
            condominio_id=condominio_id,
            code=data.code,
            name=data.name,
            period_type=data.period_type.value,
            reference_month=data.reference_month,
            reference_year=data.reference_year,
            start_date=data.start_date,
            end_date=data.end_date,
            payment_date=data.payment_date,
            notes=data.notes,
            settings=data.settings or {},
            status=PeriodStatus.DRAFT.value,
            created_by=created_by,
        )

        self.db.add(period)
        await self.db.commit()
        await self.db.refresh(period)

        logger.info("Período criado: %s", period.code)
        return period

    async def get_by_id(
        self,
        period_id: UUID,
        *,
        include_events: bool = False,
    ) -> Optional[PayrollPeriod]:
        """Busca período por ID."""
        query = select(PayrollPeriod).where(
            and_(
                PayrollPeriod.id == period_id,
                PayrollPeriod.ativo.is_(True),
            )
        )

        if include_events:
            query = query.options(selectinload(PayrollPeriod.events))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        code: str,
        condominio_id: UUID,
    ) -> Optional[PayrollPeriod]:
        """Busca período por código."""
        query = select(PayrollPeriod).where(
            and_(
                PayrollPeriod.code == code,
                PayrollPeriod.condominio_id == condominio_id,
                PayrollPeriod.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_reference(
        self,
        reference_year: int,
        reference_month: int,
        condominio_id: UUID,
        *,
        period_type: PeriodType = None,
    ) -> Optional[PayrollPeriod]:
        """Busca período por ano/mês de referência."""
        conditions = [
            PayrollPeriod.reference_year == reference_year,
            PayrollPeriod.reference_month == reference_month,
            PayrollPeriod.condominio_id == condominio_id,
            PayrollPeriod.ativo.is_(True),
        ]

        if period_type:
            conditions.append(PayrollPeriod.period_type == period_type.value)

        query = select(PayrollPeriod).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_periods(
        self,
        condominio_id: UUID,
        *,
        year: int = None,
        status: PeriodStatus = None,
        period_type: PeriodType = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[PayrollPeriod], int]:
        """Lista períodos com filtros e paginação."""
        conditions = [
            PayrollPeriod.condominio_id == condominio_id,
            PayrollPeriod.ativo.is_(True),
        ]

        if year:
            conditions.append(PayrollPeriod.reference_year == year)
        if status:
            conditions.append(PayrollPeriod.status == status.value)
        if period_type:
            conditions.append(PayrollPeriod.period_type == period_type.value)

        # Count total
        count_query = select(func.count(PayrollPeriod.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch with pagination
        query = (
            select(PayrollPeriod)
            .where(and_(*conditions))
            .order_by(
                PayrollPeriod.reference_year.desc(),
                PayrollPeriod.reference_month.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        periods = list(result.scalars().all())

        return periods, total

    async def update(
        self,
        period_id: UUID,
        data: PayrollPeriodUpdate,
    ) -> Optional[PayrollPeriod]:
        """Atualiza período."""
        period = await self.get_by_id(period_id)
        if not period:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(period, field, value)

        period.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(period)

        return period

    async def update_status(
        self,
        period_id: UUID,
        status: PeriodStatus,
        *,
        user_id: UUID = None,
    ) -> Optional[PayrollPeriod]:
        """Atualiza status do período."""
        period = await self.get_by_id(period_id)
        if not period:
            return None

        period.status = status.value
        period.updated_at = datetime.utcnow()

        if status == PeriodStatus.CALCULATED:
            period.calculation_date = datetime.utcnow()
        elif status == PeriodStatus.APPROVED:
            period.approval_date = datetime.utcnow()
            period.approved_by = user_id
        elif status == PeriodStatus.CLOSED:
            period.closing_date = datetime.utcnow()
        elif status == PeriodStatus.EXPORTED:
            period.export_date = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(period)

        return period

    async def update_totals(
        self,
        period_id: UUID,
        totals: dict,
    ) -> Optional[PayrollPeriod]:
        """Atualiza totalizadores do período."""
        period = await self.get_by_id(period_id)
        if not period:
            return None

        for field, value in totals.items():
            if hasattr(period, field):
                setattr(period, field, value)

        period.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(period)

        return period

    async def delete(self, period_id: UUID) -> bool:
        """Soft delete do período."""
        period = await self.get_by_id(period_id)
        if not period:
            return False

        period.ativo = False
        period.updated_at = datetime.utcnow()
        await self.db.commit()

        return True

    async def get_open_periods(
        self,
        condominio_id: UUID,
    ) -> List[PayrollPeriod]:
        """Retorna períodos abertos para lançamentos."""
        query = select(PayrollPeriod).where(
            and_(
                PayrollPeriod.condominio_id == condominio_id,
                PayrollPeriod.ativo.is_(True),
                PayrollPeriod.status.in_(
                    [
                        PeriodStatus.DRAFT.value,
                        PeriodStatus.OPEN.value,
                    ]
                ),
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_current_period(
        self,
        condominio_id: UUID,
    ) -> Optional[PayrollPeriod]:
        """Retorna período atual (mês corrente)."""
        now = datetime.utcnow()
        return await self.get_by_reference(
            reference_year=now.year,
            reference_month=now.month,
            condominio_id=condominio_id,
            period_type=PeriodType.MONTHLY,
        )

    async def get_years_with_periods(
        self,
        condominio_id: UUID,
    ) -> List[int]:
        """Retorna anos que possuem períodos."""
        query = (
            select(PayrollPeriod.reference_year)
            .where(
                and_(
                    PayrollPeriod.condominio_id == condominio_id,
                    PayrollPeriod.ativo.is_(True),
                )
            )
            .distinct()
            .order_by(PayrollPeriod.reference_year.desc())
        )

        result = await self.db.execute(query)
        return [row[0] for row in result.fetchall()]
