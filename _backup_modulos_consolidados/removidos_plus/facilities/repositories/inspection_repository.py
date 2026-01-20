"""
Repository para operações de banco de dados com Inspection.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.facilities.models.inspection import (
    Inspection,
    InspectionResult,
    InspectionStatus,
    InspectionType,
)
from modules.facilities.schemas.inspection import (
    InspectionCreate,
    InspectionFilter,
    InspectionStats,
    InspectionUpdate,
)


class InspectionRepository:
    """Repository para operações CRUD de Inspection."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self) -> str:
        """Gera código único para inspeção."""
        result = await self.db.execute(
            select(func.count(Inspection.id)).where(Inspection.is_active.is_(True))
        )
        count = result.scalar() or 0
        return f"INS-{count + 1:05d}"

    async def create(
        self,
        data: InspectionCreate,
        created_by: Optional[str] = None,
    ) -> Inspection:
        """Cria uma nova inspeção."""
        code = data.code or await self._generate_code()

        inspection = Inspection(
            id=str(uuid4()),
            code=code,
            title=data.title,
            description=data.description,
            inspection_type=data.inspection_type.value,
            status=InspectionStatus.SCHEDULED.value,
            area_id=data.area_id,
            client_id=data.client_id,
            checklist_template_id=data.checklist_template_id,
            scheduled_date=data.scheduled_date,
            inspector_id=data.inspector_id,
            inspector_name=data.inspector_name,
            notes=data.notes,
            is_recurring=data.is_recurring,
            recurrence_pattern=data.recurrence_pattern,
            recurrence_interval=data.recurrence_interval,
            created_by=created_by,
        )

        self.db.add(inspection)
        await self.db.commit()
        await self.db.refresh(inspection)

        logger.info(f"Inspection criada: {inspection.id} - {inspection.code}")
        return inspection

    async def get_by_id(self, inspection_id: str) -> Optional[Inspection]:
        """Busca inspeção por ID."""
        result = await self.db.execute(
            select(Inspection).where(
                Inspection.id == inspection_id,
                Inspection.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Inspection]:
        """Busca inspeção por código."""
        result = await self.db.execute(
            select(Inspection).where(
                Inspection.code == code.upper(),
                Inspection.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[InspectionFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Inspection], int]:
        """Lista inspeções com filtros e paginação."""
        query = select(Inspection).where(Inspection.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Inspection.id)).where(
            Inspection.is_active.is_(True)
        )
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Inspection.scheduled_date.desc().nullsfirst())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        inspections = list(result.scalars().all())

        return inspections, total

    def _apply_filters(self, query, filters: InspectionFilter):  # pylint: disable=too-many-branches
        """Aplica filtros à query."""
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Inspection.title.ilike(search_term),
                    Inspection.code.ilike(search_term),
                )
            )

        if filters.inspection_type:
            query = query.where(
                Inspection.inspection_type == filters.inspection_type.value
            )

        if filters.status:
            query = query.where(Inspection.status == filters.status.value)

        if filters.result:
            query = query.where(Inspection.result == filters.result.value)

        if filters.area_id:
            query = query.where(Inspection.area_id == filters.area_id)

        if filters.client_id:
            query = query.where(Inspection.client_id == filters.client_id)

        if filters.inspector_id:
            query = query.where(Inspection.inspector_id == filters.inspector_id)

        if filters.scheduled_start:
            query = query.where(Inspection.scheduled_date >= filters.scheduled_start)

        if filters.scheduled_end:
            query = query.where(Inspection.scheduled_date <= filters.scheduled_end)

        if filters.has_critical_issues:
            query = query.where(Inspection.items_critical > 0)

        if filters.is_recurring is not None:
            query = query.where(Inspection.is_recurring == filters.is_recurring)

        if filters.min_score is not None:
            query = query.where(Inspection.score >= filters.min_score)

        if filters.max_score is not None:
            query = query.where(Inspection.score <= filters.max_score)

        return query

    async def update(
        self,
        inspection_id: str,
        data: InspectionUpdate,
    ) -> Optional[Inspection]:
        """Atualiza uma inspeção."""
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("inspection_type", "status", "result") and value:
                setattr(inspection, field, value.value)
            else:
                setattr(inspection, field, value)

        inspection.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(inspection)

        logger.info(f"Inspection atualizada: {inspection.id}")
        return inspection

    async def start(
        self,
        inspection_id: str,
        inspector_id: Optional[str] = None,
        inspector_name: Optional[str] = None,
    ) -> Optional[Inspection]:
        """Inicia uma inspeção."""
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return None

        inspection.status = InspectionStatus.IN_PROGRESS.value
        inspection.started_at = datetime.utcnow()
        if inspector_id:
            inspection.inspector_id = inspector_id
        if inspector_name:
            inspection.inspector_name = inspector_name
        inspection.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(inspection)

        logger.info(f"Inspection iniciada: {inspection.id}")
        return inspection

    async def complete(
        self,
        inspection_id: str,
        result: InspectionResult,
        **kwargs,
    ) -> Optional[Inspection]:
        """Conclui uma inspeção."""
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return None

        inspection.status = InspectionStatus.COMPLETED.value
        inspection.result = result.value
        inspection.completed_at = datetime.utcnow()

        for field, value in kwargs.items():
            if hasattr(inspection, field):
                setattr(inspection, field, value)

        inspection.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(inspection)

        logger.info(f"Inspection concluída: {inspection.id}")
        return inspection

    async def review(
        self,
        inspection_id: str,
        reviewed_by: str,
        approved: bool,
        internal_notes: Optional[str] = None,
    ) -> Optional[Inspection]:
        """Revisa uma inspeção."""
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return None

        inspection.status = (
            InspectionStatus.APPROVED.value
            if approved
            else InspectionStatus.REJECTED.value
        )
        inspection.reviewed_by = reviewed_by
        inspection.reviewed_at = datetime.utcnow()
        if internal_notes:
            inspection.internal_notes = internal_notes
        inspection.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(inspection)

        logger.info(f"Inspection revisada: {inspection.id}")
        return inspection

    async def delete(self, inspection_id: str) -> bool:
        """Soft delete de inspeção."""
        inspection = await self.get_by_id(inspection_id)
        if not inspection:
            return False

        inspection.is_active = False
        inspection.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Inspection deletada (soft): {inspection.id}")
        return True

    async def get_stats(  # pylint: disable=too-many-locals
        self,
        client_id: Optional[str] = None,
        area_id: Optional[str] = None,
    ) -> InspectionStats:
        """Obtém estatísticas de inspeções."""
        base_filter = [Inspection.is_active.is_(True)]
        if client_id:
            base_filter.append(Inspection.client_id == client_id)
        if area_id:
            base_filter.append(Inspection.area_id == area_id)

        # Total
        total_result = await self.db.execute(
            select(func.count(Inspection.id)).where(and_(*base_filter))
        )
        total = total_result.scalar() or 0

        # Por tipo
        by_type: Dict[str, int] = {}
        for itype in InspectionType:
            type_result = await self.db.execute(
                select(func.count(Inspection.id)).where(
                    and_(*base_filter, Inspection.inspection_type == itype.value)
                )
            )
            count = type_result.scalar() or 0
            if count > 0:
                by_type[itype.value] = count

        # Por status
        by_status: Dict[str, int] = {}
        for status in InspectionStatus:
            status_result = await self.db.execute(
                select(func.count(Inspection.id)).where(
                    and_(*base_filter, Inspection.status == status.value)
                )
            )
            count = status_result.scalar() or 0
            if count > 0:
                by_status[status.value] = count

        # Por resultado
        by_result: Dict[str, int] = {}
        for result in InspectionResult:
            result_result = await self.db.execute(
                select(func.count(Inspection.id)).where(
                    and_(*base_filter, Inspection.result == result.value)
                )
            )
            count = result_result.scalar() or 0
            if count > 0:
                by_result[result.value] = count

        # Pontuação média
        avg_score_result = await self.db.execute(
            select(func.avg(Inspection.score)).where(
                and_(*base_filter, Inspection.score.isnot(None))
            )
        )
        avg_score = avg_score_result.scalar()

        # Com issues críticos
        critical_result = await self.db.execute(
            select(func.count(Inspection.id)).where(
                and_(*base_filter, Inspection.items_critical > 0)
            )
        )
        with_critical = critical_result.scalar() or 0

        # Aguardando revisão
        pending_result = await self.db.execute(
            select(func.count(Inspection.id)).where(
                and_(
                    *base_filter,
                    Inspection.status == InspectionStatus.PENDING_REVIEW.value,
                )
            )
        )
        pending_review = pending_result.scalar() or 0

        # Este mês
        today = date.today()
        first_day = today.replace(day=1)

        scheduled_result = await self.db.execute(
            select(func.count(Inspection.id)).where(
                and_(
                    *base_filter,
                    Inspection.scheduled_date >= first_day,
                    Inspection.scheduled_date <= today,
                )
            )
        )
        scheduled_this_month = scheduled_result.scalar() or 0

        completed_result = await self.db.execute(
            select(func.count(Inspection.id)).where(
                and_(
                    *base_filter,
                    Inspection.completed_at >= datetime.combine(first_day, datetime.min.time()),
                    Inspection.status.in_(
                        [
                            InspectionStatus.COMPLETED.value,
                            InspectionStatus.APPROVED.value,
                        ]
                    ),
                )
            )
        )
        completed_this_month = completed_result.scalar() or 0

        return InspectionStats(
            total=total,
            by_type=by_type,
            by_status=by_status,
            by_result=by_result,
            avg_score=float(avg_score) if avg_score else None,
            avg_compliance_rate=None,  # Calculado via checklists
            with_critical_issues=with_critical,
            pending_review=pending_review,
            scheduled_this_month=scheduled_this_month,
            completed_this_month=completed_this_month,
        )
