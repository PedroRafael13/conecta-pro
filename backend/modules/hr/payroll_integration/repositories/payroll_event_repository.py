"""Repository para eventos de folha de pagamento."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.payroll_integration.models import (
    EventCategory,
    EventStatus,
    EventType,
    PayrollEvent,
)
from modules.hr.payroll_integration.schemas import PayrollEventCreate, PayrollEventUpdate

logger = logging.getLogger(__name__)


class PayrollEventRepository:
    """Repository para operações de eventos de folha."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: PayrollEventCreate,
        condominio_id: UUID,
        *,
        created_by: UUID = None,
    ) -> PayrollEvent:
        """Cria novo evento de folha."""
        event = PayrollEvent(
            condominio_id=condominio_id,
            period_id=data.period_id,
            employee_id=data.employee_id,
            event_code=data.event_code,
            event_name=data.event_name,
            event_type=data.event_type.value,
            event_category=data.event_category.value,
            reference=data.reference,
            reference_unit=data.reference_unit,
            base_value=data.base_value,
            rate=data.rate,
            value=data.value,
            source=data.source,
            event_date=data.event_date,
            event_start=data.event_start,
            event_end=data.event_end,
            esocial_code=data.esocial_code,
            esocial_incidences=data.esocial_incidences or {},
            is_recurring=data.is_recurring,
            is_proportional=data.is_proportional,
            notes=data.notes,
            status=EventStatus.PENDING.value,
            created_by=created_by,
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def create_bulk(
        self,
        events: List[PayrollEventCreate],
        condominio_id: UUID,
        *,
        created_by: UUID = None,
    ) -> List[PayrollEvent]:
        """Cria múltiplos eventos em lote."""
        created_events = []

        for data in events:
            event = PayrollEvent(
                condominio_id=condominio_id,
                period_id=data.period_id,
                employee_id=data.employee_id,
                event_code=data.event_code,
                event_name=data.event_name,
                event_type=data.event_type.value,
                event_category=data.event_category.value,
                reference=data.reference,
                reference_unit=data.reference_unit,
                base_value=data.base_value,
                rate=data.rate,
                value=data.value,
                source=data.source,
                event_date=data.event_date,
                esocial_code=data.esocial_code,
                esocial_incidences=data.esocial_incidences or {},
                is_recurring=data.is_recurring,
                status=EventStatus.CALCULATED.value,
                created_by=created_by,
            )
            self.db.add(event)
            created_events.append(event)

        await self.db.commit()
        for event in created_events:
            await self.db.refresh(event)

        logger.info("Criados %d eventos em lote", len(created_events))
        return created_events

    async def get_by_id(self, event_id: UUID) -> Optional[PayrollEvent]:
        """Busca evento por ID."""
        query = select(PayrollEvent).where(
            and_(
                PayrollEvent.id == event_id,
                PayrollEvent.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_period(
        self,
        period_id: UUID,
        *,
        employee_id: UUID = None,
        event_type: EventType = None,
        event_category: EventCategory = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Tuple[List[PayrollEvent], int]:
        """Lista eventos de um período."""
        conditions = [
            PayrollEvent.period_id == period_id,
            PayrollEvent.ativo.is_(True),
        ]

        if employee_id:
            conditions.append(PayrollEvent.employee_id == employee_id)
        if event_type:
            conditions.append(PayrollEvent.event_type == event_type.value)
        if event_category:
            conditions.append(PayrollEvent.event_category == event_category.value)

        # Count
        count_query = select(func.count(PayrollEvent.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch
        query = (
            select(PayrollEvent)
            .where(and_(*conditions))
            .order_by(PayrollEvent.event_code)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        events = list(result.scalars().all())

        return events, total

    async def list_by_employee(
        self,
        employee_id: UUID,
        period_id: UUID,
    ) -> List[PayrollEvent]:
        """Lista todos eventos de um funcionário em um período."""
        query = (
            select(PayrollEvent)
            .where(
                and_(
                    PayrollEvent.employee_id == employee_id,
                    PayrollEvent.period_id == period_id,
                    PayrollEvent.ativo.is_(True),
                )
            )
            .order_by(PayrollEvent.event_type, PayrollEvent.event_code)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        event_id: UUID,
        data: PayrollEventUpdate,
    ) -> Optional[PayrollEvent]:
        """Atualiza evento."""
        event = await self.get_by_id(event_id)
        if not event:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        event.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def adjust_value(
        self,
        event_id: UUID,
        new_value: Decimal,
        reason: str,
        user_id: UUID,
    ) -> Optional[PayrollEvent]:
        """Ajusta valor do evento."""
        event = await self.get_by_id(event_id)
        if not event:
            return None

        event.adjust_value(new_value, reason, user_id)
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def cancel(
        self,
        event_id: UUID,
        reason: str,
        user_id: UUID,
    ) -> Optional[PayrollEvent]:
        """Cancela evento."""
        event = await self.get_by_id(event_id)
        if not event:
            return None

        event.cancel(reason, user_id)
        await self.db.commit()
        await self.db.refresh(event)

        return event

    async def delete_by_period(
        self,
        period_id: UUID,
        *,
        employee_id: UUID = None,
    ) -> int:
        """Remove eventos de um período (soft delete)."""
        conditions = [
            PayrollEvent.period_id == period_id,
            PayrollEvent.ativo.is_(True),
        ]

        if employee_id:
            conditions.append(PayrollEvent.employee_id == employee_id)

        query = select(PayrollEvent).where(and_(*conditions))
        result = await self.db.execute(query)
        events = list(result.scalars().all())

        count = 0
        for event in events:
            event.ativo = False
            event.updated_at = datetime.utcnow()
            count += 1

        await self.db.commit()
        return count

    async def get_period_totals(
        self,
        period_id: UUID,
    ) -> Dict[str, Decimal]:
        """Calcula totais do período."""
        # Total de proventos
        earnings_query = select(func.sum(PayrollEvent.value)).where(
            and_(
                PayrollEvent.period_id == period_id,
                PayrollEvent.event_type == EventType.EARNING.value,
                PayrollEvent.ativo.is_(True),
            )
        )
        earnings_result = await self.db.execute(earnings_query)
        total_earnings = earnings_result.scalar() or Decimal("0")

        # Total de descontos
        deductions_query = select(func.sum(PayrollEvent.value)).where(
            and_(
                PayrollEvent.period_id == period_id,
                PayrollEvent.event_type == EventType.DEDUCTION.value,
                PayrollEvent.ativo.is_(True),
            )
        )
        deductions_result = await self.db.execute(deductions_query)
        total_deductions = deductions_result.scalar() or Decimal("0")

        # Contagem de funcionários
        employees_query = select(func.count(func.distinct(PayrollEvent.employee_id))).where(
            and_(
                PayrollEvent.period_id == period_id,
                PayrollEvent.ativo.is_(True),
            )
        )
        employees_result = await self.db.execute(employees_query)
        total_employees = employees_result.scalar() or 0

        return {
            "total_earnings": total_earnings,
            "total_deductions": total_deductions,
            "total_net": total_earnings - total_deductions,
            "total_employees": total_employees,
        }

    async def get_employee_totals(
        self,
        employee_id: UUID,
        period_id: UUID,
    ) -> Dict[str, Decimal]:
        """Calcula totais de um funcionário no período."""
        events = await self.list_by_employee(employee_id, period_id)

        total_earnings = sum(e.value for e in events if e.event_type == EventType.EARNING.value)
        total_deductions = sum(e.value for e in events if e.event_type == EventType.DEDUCTION.value)

        return {
            "total_earnings": total_earnings,
            "total_deductions": total_deductions,
            "net_salary": total_earnings - total_deductions,
            "events_count": len(events),
        }

    async def get_events_by_category(
        self,
        period_id: UUID,
    ) -> Dict[str, List[PayrollEvent]]:
        """Agrupa eventos por categoria."""
        query = (
            select(PayrollEvent)
            .where(
                and_(
                    PayrollEvent.period_id == period_id,
                    PayrollEvent.ativo.is_(True),
                )
            )
            .order_by(PayrollEvent.event_category, PayrollEvent.event_code)
        )

        result = await self.db.execute(query)
        events = list(result.scalars().all())

        grouped: Dict[str, List[PayrollEvent]] = {}
        for event in events:
            category = event.event_category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(event)

        return grouped

    async def exists_for_employee(
        self,
        employee_id: UUID,
        period_id: UUID,
        event_code: str,
    ) -> bool:
        """Verifica se evento já existe para funcionário no período."""
        query = select(func.count(PayrollEvent.id)).where(
            and_(
                PayrollEvent.employee_id == employee_id,
                PayrollEvent.period_id == period_id,
                PayrollEvent.event_code == event_code,
                PayrollEvent.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count > 0
