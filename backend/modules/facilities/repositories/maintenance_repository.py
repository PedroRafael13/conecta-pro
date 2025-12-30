"""
Repository para operações de banco de dados com Maintenance.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.facilities.models.maintenance import (
    Maintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.facilities.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceStats,
    MaintenanceUpdate,
)


class MaintenanceRepository:
    """Repository para operações CRUD de Maintenance."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _generate_code(self) -> str:
        """Gera código único para manutenção."""
        result = await self.db.execute(
            select(func.count(Maintenance.id)).where(Maintenance.is_active.is_(True))
        )
        count = result.scalar() or 0
        return f"MNT-{count + 1:05d}"

    async def create(
        self,
        data: MaintenanceCreate,
        created_by: Optional[str] = None,
    ) -> Maintenance:
        """
        Cria uma nova manutenção.

        Args:
            data: Dados da manutenção
            created_by: ID do usuário criador

        Returns:
            Maintenance criada
        """
        code = data.code or await self._generate_code()

        maintenance = Maintenance(
            id=str(uuid4()),
            code=code,
            title=data.title,
            description=data.description,
            maintenance_type=data.maintenance_type.value,
            status=MaintenanceStatus.PENDING.value,
            priority=data.priority.value,
            area_id=data.area_id,
            client_id=data.client_id,
            equipment_id=data.equipment_id,
            service_request_id=data.service_request_id,
            scheduled_date=data.scheduled_date,
            deadline=data.deadline,
            assigned_to=data.assigned_to,
            team_ids=data.team_ids,
            requested_by=data.requested_by,
            estimated_hours=data.estimated_hours,
            estimated_cost=data.estimated_cost,
            notes=data.notes,
            is_recurring=data.is_recurring,
            recurrence_pattern=data.recurrence_pattern,
            recurrence_interval=data.recurrence_interval,
            requires_approval=data.requires_approval,
            created_by=created_by,
        )

        self.db.add(maintenance)
        await self.db.commit()
        await self.db.refresh(maintenance)

        logger.info(f"Maintenance criada: {maintenance.id} - {maintenance.code}")
        return maintenance

    async def get_by_id(self, maintenance_id: str) -> Optional[Maintenance]:
        """Busca manutenção por ID."""
        result = await self.db.execute(
            select(Maintenance).where(
                Maintenance.id == maintenance_id,
                Maintenance.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Maintenance]:
        """Busca manutenção por código."""
        result = await self.db.execute(
            select(Maintenance).where(
                Maintenance.code == code.upper(),
                Maintenance.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[MaintenanceFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Maintenance], int]:
        """Lista manutenções com filtros e paginação."""
        query = select(Maintenance).where(Maintenance.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Maintenance.id)).where(
            Maintenance.is_active.is_(True)
        )
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Maintenance.scheduled_date.desc().nullsfirst())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        maintenances = list(result.scalars().all())

        return maintenances, total

    def _apply_filters(self, query, filters: MaintenanceFilter):
        """Aplica filtros à query."""
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Maintenance.title.ilike(search_term),
                    Maintenance.code.ilike(search_term),
                    Maintenance.description.ilike(search_term),
                )
            )

        if filters.maintenance_type:
            query = query.where(
                Maintenance.maintenance_type == filters.maintenance_type.value
            )

        if filters.status:
            query = query.where(Maintenance.status == filters.status.value)

        if filters.priority:
            query = query.where(Maintenance.priority == filters.priority.value)

        if filters.area_id:
            query = query.where(Maintenance.area_id == filters.area_id)

        if filters.client_id:
            query = query.where(Maintenance.client_id == filters.client_id)

        if filters.equipment_id:
            query = query.where(Maintenance.equipment_id == filters.equipment_id)

        if filters.assigned_to:
            query = query.where(Maintenance.assigned_to == filters.assigned_to)

        if filters.scheduled_start:
            query = query.where(Maintenance.scheduled_date >= filters.scheduled_start)

        if filters.scheduled_end:
            query = query.where(Maintenance.scheduled_date <= filters.scheduled_end)

        if filters.is_overdue:
            today = date.today()
            query = query.where(
                and_(
                    Maintenance.deadline.isnot(None),
                    Maintenance.deadline < today,
                    Maintenance.status.notin_(
                        [
                            MaintenanceStatus.COMPLETED.value,
                            MaintenanceStatus.CANCELLED.value,
                            MaintenanceStatus.VERIFIED.value,
                        ]
                    ),
                )
            )

        if filters.is_recurring is not None:
            query = query.where(Maintenance.is_recurring == filters.is_recurring)

        if filters.requires_approval is not None:
            query = query.where(Maintenance.requires_approval == filters.requires_approval)

        return query

    async def update(
        self,
        maintenance_id: str,
        data: MaintenanceUpdate,
    ) -> Optional[Maintenance]:
        """Atualiza uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ("maintenance_type", "status", "priority") and value:
                setattr(maintenance, field, value.value)
            else:
                setattr(maintenance, field, value)

        maintenance.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(maintenance)

        logger.info(f"Maintenance atualizada: {maintenance.id}")
        return maintenance

    async def start(self, maintenance_id: str) -> Optional[Maintenance]:
        """Inicia uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.status = MaintenanceStatus.IN_PROGRESS.value
        maintenance.started_at = datetime.utcnow()
        maintenance.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(maintenance)

        logger.info(f"Maintenance iniciada: {maintenance.id}")
        return maintenance

    async def complete(
        self,
        maintenance_id: str,
        work_performed: str,
        actual_hours: float,
        actual_cost: Optional[float] = None,
        **kwargs,
    ) -> Optional[Maintenance]:
        """Conclui uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.status = MaintenanceStatus.COMPLETED.value
        maintenance.completed_at = datetime.utcnow()
        maintenance.work_performed = work_performed
        maintenance.actual_hours = actual_hours

        if actual_cost is not None:
            maintenance.actual_cost = actual_cost

        for field, value in kwargs.items():
            if hasattr(maintenance, field):
                setattr(maintenance, field, value)

        maintenance.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(maintenance)

        logger.info(f"Maintenance concluída: {maintenance.id}")
        return maintenance

    async def approve(
        self,
        maintenance_id: str,
        approved_by: str,
        notes: Optional[str] = None,
    ) -> Optional[Maintenance]:
        """Aprova uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.approved_by = approved_by
        maintenance.approved_at = datetime.utcnow()
        if notes:
            maintenance.notes = f"{maintenance.notes or ''}\n[Aprovação] {notes}".strip()
        maintenance.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(maintenance)

        logger.info(f"Maintenance aprovada: {maintenance.id}")
        return maintenance

    async def reject(
        self,
        maintenance_id: str,
        rejection_reason: str,
        approved_by: str,
    ) -> Optional[Maintenance]:
        """Rejeita uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.status = MaintenanceStatus.CANCELLED.value
        maintenance.rejection_reason = rejection_reason
        maintenance.approved_by = approved_by
        maintenance.approved_at = datetime.utcnow()
        maintenance.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(maintenance)

        logger.info(f"Maintenance rejeitada: {maintenance.id}")
        return maintenance

    async def delete(self, maintenance_id: str) -> bool:
        """Soft delete de manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return False

        maintenance.is_active = False
        maintenance.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Maintenance deletada (soft): {maintenance.id}")
        return True

    async def get_stats(
        self,
        client_id: Optional[str] = None,
        area_id: Optional[str] = None,
    ) -> MaintenanceStats:
        """Obtém estatísticas de manutenções."""
        base_filter = [Maintenance.is_active.is_(True)]
        if client_id:
            base_filter.append(Maintenance.client_id == client_id)
        if area_id:
            base_filter.append(Maintenance.area_id == area_id)

        # Total
        total_result = await self.db.execute(
            select(func.count(Maintenance.id)).where(and_(*base_filter))
        )
        total = total_result.scalar() or 0

        # Por tipo
        by_type: Dict[str, int] = {}
        for mtype in MaintenanceType:
            type_result = await self.db.execute(
                select(func.count(Maintenance.id)).where(
                    and_(*base_filter, Maintenance.maintenance_type == mtype.value)
                )
            )
            count = type_result.scalar() or 0
            if count > 0:
                by_type[mtype.value] = count

        # Por status
        by_status: Dict[str, int] = {}
        for status in MaintenanceStatus:
            status_result = await self.db.execute(
                select(func.count(Maintenance.id)).where(
                    and_(*base_filter, Maintenance.status == status.value)
                )
            )
            count = status_result.scalar() or 0
            if count > 0:
                by_status[status.value] = count

        # Por prioridade
        by_priority: Dict[str, int] = {}
        for priority in MaintenancePriority:
            priority_result = await self.db.execute(
                select(func.count(Maintenance.id)).where(
                    and_(*base_filter, Maintenance.priority == priority.value)
                )
            )
            count = priority_result.scalar() or 0
            if count > 0:
                by_priority[priority.value] = count

        # Atrasadas
        today = date.today()
        overdue_result = await self.db.execute(
            select(func.count(Maintenance.id)).where(
                and_(
                    *base_filter,
                    Maintenance.deadline.isnot(None),
                    Maintenance.deadline < today,
                    Maintenance.status.notin_(
                        [
                            MaintenanceStatus.COMPLETED.value,
                            MaintenanceStatus.CANCELLED.value,
                        ]
                    ),
                )
            )
        )
        overdue_count = overdue_result.scalar() or 0

        # Aguardando aprovação
        pending_result = await self.db.execute(
            select(func.count(Maintenance.id)).where(
                and_(
                    *base_filter,
                    Maintenance.requires_approval.is_(True),
                    Maintenance.approved_by.is_(None),
                    Maintenance.status == MaintenanceStatus.PENDING.value,
                )
            )
        )
        pending_approval = pending_result.scalar() or 0

        # Custos
        estimated_result = await self.db.execute(
            select(func.sum(Maintenance.estimated_cost)).where(and_(*base_filter))
        )
        total_estimated = estimated_result.scalar() or 0.0

        actual_result = await self.db.execute(
            select(func.sum(Maintenance.actual_cost)).where(and_(*base_filter))
        )
        total_actual = actual_result.scalar() or 0.0

        # Média de horas para conclusão
        avg_hours_result = await self.db.execute(
            select(func.avg(Maintenance.actual_hours)).where(
                and_(
                    *base_filter,
                    Maintenance.status == MaintenanceStatus.COMPLETED.value,
                )
            )
        )
        avg_hours = avg_hours_result.scalar() or 0.0

        # Média de satisfação
        avg_sat_result = await self.db.execute(
            select(func.avg(Maintenance.satisfaction_rating)).where(
                and_(
                    *base_filter,
                    Maintenance.satisfaction_rating.isnot(None),
                )
            )
        )
        avg_satisfaction = avg_sat_result.scalar()

        return MaintenanceStats(
            total=total,
            by_type=by_type,
            by_status=by_status,
            by_priority=by_priority,
            overdue_count=overdue_count,
            pending_approval=pending_approval,
            total_estimated_cost=float(total_estimated),
            total_actual_cost=float(total_actual),
            avg_completion_hours=float(avg_hours),
            avg_satisfaction=float(avg_satisfaction) if avg_satisfaction else None,
        )
