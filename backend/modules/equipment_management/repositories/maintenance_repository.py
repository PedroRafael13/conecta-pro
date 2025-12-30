"""Repository para EquipmentMaintenance."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.models.maintenance import (
    EquipmentMaintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.equipment_management.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceStats,
    MaintenanceUpdate,
)

logger = logging.getLogger(__name__)


class MaintenanceRepository:
    """Repository para operações de EquipmentMaintenance."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: MaintenanceCreate) -> EquipmentMaintenance:
        """Cria uma nova manutenção."""
        maintenance = EquipmentMaintenance(
            maintenance_type=data.maintenance_type,
            priority=data.priority,
            equipment_id=data.equipment_id,
            equipment_code=data.equipment_code,
            equipment_name=data.equipment_name,
            equipment_type=data.equipment_type,
            serial_number=data.serial_number,
            client_id=data.client_id,
            client_name=data.client_name,
            contract_id=data.contract_id,
            title=data.title,
            description=data.description,
            symptoms=data.symptoms,
            reported_by=data.reported_by,
            scheduled_date=data.scheduled_date,
            scheduled_time=data.scheduled_time,
            estimated_duration_hours=data.estimated_duration_hours,
            sla_deadline=data.sla_deadline,
            technician_id=data.technician_id,
            technician_name=data.technician_name,
            checklist_template_id=data.checklist_template_id,
            is_recurring=data.is_recurring,
            recurrence_interval_days=data.recurrence_interval_days,
            notes=data.notes,
        )
        self.session.add(maintenance)
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção criada: {maintenance.maintenance_code}")
        return maintenance

    async def get_by_id(
        self, maintenance_id: str | UUID
    ) -> Optional[EquipmentMaintenance]:
        """Busca manutenção por ID."""
        if isinstance(maintenance_id, str):
            maintenance_id = UUID(maintenance_id)
        result = await self.session.execute(
            select(EquipmentMaintenance).where(
                and_(
                    EquipmentMaintenance.id == maintenance_id,
                    EquipmentMaintenance.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[EquipmentMaintenance]:
        """Busca manutenção por código."""
        result = await self.session.execute(
            select(EquipmentMaintenance).where(
                and_(
                    EquipmentMaintenance.maintenance_code == code,
                    EquipmentMaintenance.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, maintenance_id: str | UUID, data: MaintenanceUpdate
    ) -> Optional[EquipmentMaintenance]:
        """Atualiza uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(maintenance, field, value)

        maintenance.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção atualizada: {maintenance.maintenance_code}")
        return maintenance

    async def delete(self, maintenance_id: str | UUID) -> bool:
        """Soft delete de manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return False

        maintenance.is_active = False
        maintenance.updated_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Manutenção desativada: {maintenance.maintenance_code}")
        return True

    async def list_with_filters(
        self,
        filters: Optional[MaintenanceFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EquipmentMaintenance], int]:
        """Lista manutenções com filtros e paginação."""
        query = select(EquipmentMaintenance).where(
            EquipmentMaintenance.is_active == True
        )

        if filters:
            conditions = []

            if filters.search:
                search_term = f"%{filters.search}%"
                conditions.append(
                    or_(
                        EquipmentMaintenance.maintenance_code.ilike(search_term),
                        EquipmentMaintenance.title.ilike(search_term),
                        EquipmentMaintenance.equipment_name.ilike(search_term),
                        EquipmentMaintenance.equipment_code.ilike(search_term),
                        EquipmentMaintenance.technician_name.ilike(search_term),
                    )
                )

            if filters.maintenance_type:
                conditions.append(
                    EquipmentMaintenance.maintenance_type == filters.maintenance_type
                )

            if filters.status:
                conditions.append(EquipmentMaintenance.status == filters.status)

            if filters.priority:
                conditions.append(EquipmentMaintenance.priority == filters.priority)

            if filters.equipment_id:
                conditions.append(
                    EquipmentMaintenance.equipment_id == filters.equipment_id
                )

            if filters.client_id:
                conditions.append(EquipmentMaintenance.client_id == filters.client_id)

            if filters.technician_id:
                conditions.append(
                    EquipmentMaintenance.technician_id == filters.technician_id
                )

            if filters.is_overdue is not None:
                now = datetime.utcnow()
                if filters.is_overdue:
                    conditions.append(
                        and_(
                            EquipmentMaintenance.sla_deadline < now,
                            EquipmentMaintenance.status.in_(
                                [
                                    MaintenanceStatus.SCHEDULED,
                                    MaintenanceStatus.PENDING,
                                    MaintenanceStatus.IN_PROGRESS,
                                    MaintenanceStatus.WAITING_PARTS,
                                ]
                            ),
                        )
                    )
                else:
                    conditions.append(
                        or_(
                            EquipmentMaintenance.sla_deadline >= now,
                            EquipmentMaintenance.sla_deadline == None,
                            EquipmentMaintenance.status.in_(
                                [
                                    MaintenanceStatus.COMPLETED,
                                    MaintenanceStatus.CANCELLED,
                                ]
                            ),
                        )
                    )

            if filters.is_warranty is not None:
                conditions.append(
                    EquipmentMaintenance.is_warranty_repair == filters.is_warranty
                )

            if filters.problem_resolved is not None:
                conditions.append(
                    EquipmentMaintenance.problem_resolved == filters.problem_resolved
                )

            if filters.needs_followup is not None:
                conditions.append(
                    EquipmentMaintenance.needs_followup == filters.needs_followup
                )

            if filters.date_from:
                conditions.append(
                    EquipmentMaintenance.scheduled_date >= filters.date_from
                )

            if filters.date_to:
                conditions.append(
                    EquipmentMaintenance.scheduled_date <= filters.date_to
                )

            if conditions:
                query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        query = query.order_by(
            EquipmentMaintenance.priority.desc(),
            EquipmentMaintenance.scheduled_date.asc(),
        )
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_equipment(self, equipment_id: str) -> list[EquipmentMaintenance]:
        """Lista manutenções de um equipamento."""
        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.equipment_id == equipment_id,
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_client(self, client_id: str) -> list[EquipmentMaintenance]:
        """Lista manutenções de um cliente."""
        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.client_id == client_id,
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_technician(
        self, technician_id: str, include_completed: bool = False
    ) -> list[EquipmentMaintenance]:
        """Lista manutenções de um técnico."""
        conditions = [
            EquipmentMaintenance.technician_id == technician_id,
            EquipmentMaintenance.is_active == True,
        ]

        if not include_completed:
            conditions.append(
                EquipmentMaintenance.status.in_(
                    [
                        MaintenanceStatus.SCHEDULED,
                        MaintenanceStatus.PENDING,
                        MaintenanceStatus.IN_PROGRESS,
                        MaintenanceStatus.WAITING_PARTS,
                    ]
                )
            )

        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(and_(*conditions))
            .order_by(
                EquipmentMaintenance.priority.desc(),
                EquipmentMaintenance.scheduled_date,
            )
        )
        return list(result.scalars().all())

    async def get_scheduled_for_date(
        self, date: datetime
    ) -> list[EquipmentMaintenance]:
        """Lista manutenções agendadas para uma data."""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.scheduled_date >= start,
                    EquipmentMaintenance.scheduled_date < end,
                    EquipmentMaintenance.is_active == True,
                    EquipmentMaintenance.status.in_(
                        [
                            MaintenanceStatus.SCHEDULED,
                            MaintenanceStatus.PENDING,
                            MaintenanceStatus.IN_PROGRESS,
                        ]
                    ),
                )
            )
            .order_by(
                EquipmentMaintenance.priority.desc(),
                EquipmentMaintenance.scheduled_date,
            )
        )
        return list(result.scalars().all())

    async def get_overdue(self) -> list[EquipmentMaintenance]:
        """Lista manutenções atrasadas."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.sla_deadline < now,
                    EquipmentMaintenance.status.in_(
                        [
                            MaintenanceStatus.SCHEDULED,
                            MaintenanceStatus.PENDING,
                            MaintenanceStatus.IN_PROGRESS,
                            MaintenanceStatus.WAITING_PARTS,
                        ]
                    ),
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.sla_deadline)
        )
        return list(result.scalars().all())

    async def get_waiting_parts(self) -> list[EquipmentMaintenance]:
        """Lista manutenções aguardando peças."""
        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.status == MaintenanceStatus.WAITING_PARTS,
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.priority.desc())
        )
        return list(result.scalars().all())

    async def get_needing_followup(self) -> list[EquipmentMaintenance]:
        """Lista manutenções que precisam de follow-up."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.needs_followup == True,
                    EquipmentMaintenance.followup_date <= now,
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.followup_date)
        )
        return list(result.scalars().all())

    async def get_preventive_due(self) -> list[EquipmentMaintenance]:
        """Lista manutenções preventivas recorrentes pendentes."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(EquipmentMaintenance)
            .where(
                and_(
                    EquipmentMaintenance.is_recurring == True,
                    EquipmentMaintenance.next_maintenance_date <= now,
                    EquipmentMaintenance.status == MaintenanceStatus.COMPLETED,
                    EquipmentMaintenance.is_active == True,
                )
            )
            .order_by(EquipmentMaintenance.next_maintenance_date)
        )
        return list(result.scalars().all())

    async def start(
        self, maintenance_id: str | UUID
    ) -> Optional[EquipmentMaintenance]:
        """Inicia uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.start()
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção iniciada: {maintenance.maintenance_code}")
        return maintenance

    async def complete(
        self,
        maintenance_id: str | UUID,
        problem_resolved: bool = True,
        equipment_status_after: Optional[str] = None,
    ) -> Optional[EquipmentMaintenance]:
        """Conclui uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.complete(
            problem_resolved=problem_resolved,
            equipment_status_after=equipment_status_after,
        )
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção concluída: {maintenance.maintenance_code}")
        return maintenance

    async def cancel(
        self, maintenance_id: str | UUID
    ) -> Optional[EquipmentMaintenance]:
        """Cancela uma manutenção."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.cancel()
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção cancelada: {maintenance.maintenance_code}")
        return maintenance

    async def mark_waiting_parts(
        self, maintenance_id: str | UUID, parts_requested: list
    ) -> Optional[EquipmentMaintenance]:
        """Marca como aguardando peças."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.mark_waiting_parts(parts_requested=parts_requested)
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção aguardando peças: {maintenance.maintenance_code}")
        return maintenance

    async def add_part_replaced(
        self,
        maintenance_id: str | UUID,
        part_name: str,
        part_code: Optional[str] = None,
        quantity: int = 1,
        unit_cost: float = 0.0,
    ) -> Optional[EquipmentMaintenance]:
        """Adiciona peça substituída."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.add_part_replaced(
            part_name=part_name,
            part_code=part_code,
            quantity=quantity,
            unit_cost=unit_cost,
        )
        await self.session.flush()
        await self.session.refresh(maintenance)
        return maintenance

    async def sign_by_client(
        self, maintenance_id: str | UUID, signed_by: str, signature: str
    ) -> Optional[EquipmentMaintenance]:
        """Registra assinatura do cliente."""
        maintenance = await self.get_by_id(maintenance_id)
        if not maintenance:
            return None

        maintenance.sign_by_client(signed_by=signed_by, signature=signature)
        await self.session.flush()
        await self.session.refresh(maintenance)
        logger.info(f"Manutenção assinada: {maintenance.maintenance_code}")
        return maintenance

    async def get_stats(
        self,
        client_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> MaintenanceStats:
        """Calcula estatísticas de manutenções."""
        conditions = [EquipmentMaintenance.is_active == True]

        if client_id:
            conditions.append(EquipmentMaintenance.client_id == client_id)

        if date_from:
            conditions.append(EquipmentMaintenance.created_at >= date_from)

        if date_to:
            conditions.append(EquipmentMaintenance.created_at <= date_to)

        result = await self.session.execute(
            select(EquipmentMaintenance).where(and_(*conditions))
        )
        maintenances = list(result.scalars().all())

        stats = MaintenanceStats(
            total=len(maintenances),
            by_status={},
            by_type={},
            by_priority={},
        )

        now = datetime.utcnow()
        response_times = []
        resolution_times = []
        total_cost = 0.0
        sla_met_count = 0
        first_time_fix_count = 0

        for m in maintenances:
            # Por status
            status_key = m.status.value if m.status else "unknown"
            stats.by_status[status_key] = stats.by_status.get(status_key, 0) + 1

            # Por tipo
            type_key = m.maintenance_type.value if m.maintenance_type else "unknown"
            stats.by_type[type_key] = stats.by_type.get(type_key, 0) + 1

            # Por prioridade
            priority_key = m.priority.value if m.priority else "unknown"
            stats.by_priority[priority_key] = (
                stats.by_priority.get(priority_key, 0) + 1
            )

            # Contadores
            if m.status == MaintenanceStatus.SCHEDULED:
                stats.scheduled += 1
            elif m.status == MaintenanceStatus.IN_PROGRESS:
                stats.in_progress += 1
            elif m.status == MaintenanceStatus.COMPLETED:
                stats.completed += 1
            elif m.status == MaintenanceStatus.WAITING_PARTS:
                stats.waiting_parts += 1

            if m.sla_deadline and m.sla_deadline < now and m.status not in [
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.CANCELLED,
            ]:
                stats.overdue += 1

            if m.maintenance_type == MaintenanceType.PREVENTIVA:
                stats.preventive += 1
            elif m.maintenance_type == MaintenanceType.CORRETIVA:
                stats.corrective += 1

            # Tempos e custos
            if m.response_time_hours:
                response_times.append(m.response_time_hours)

            if m.resolution_time_hours:
                resolution_times.append(m.resolution_time_hours)

            if m.total_cost:
                total_cost += m.total_cost

            if m.sla_met:
                sla_met_count += 1

            if m.problem_resolved and not m.needs_followup:
                first_time_fix_count += 1

        # Médias
        if response_times:
            stats.avg_response_time_hours = sum(response_times) / len(response_times)

        if resolution_times:
            stats.avg_resolution_time_hours = sum(resolution_times) / len(
                resolution_times
            )

        if stats.completed > 0:
            stats.sla_compliance_rate = (sla_met_count / stats.completed) * 100
            stats.first_time_fix_rate = (first_time_fix_count / stats.completed) * 100

        stats.total_cost = total_cost
        if stats.completed > 0:
            stats.avg_cost = total_cost / stats.completed

        return stats

    async def create_recurring(
        self, parent_id: str | UUID
    ) -> Optional[EquipmentMaintenance]:
        """Cria próxima manutenção recorrente."""
        parent = await self.get_by_id(parent_id)
        if not parent or not parent.is_recurring:
            return None

        next_date = parent.next_maintenance_date
        if not next_date:
            return None

        # Cria nova manutenção
        new_maintenance = EquipmentMaintenance(
            maintenance_type=parent.maintenance_type,
            priority=parent.priority,
            equipment_id=parent.equipment_id,
            equipment_code=parent.equipment_code,
            equipment_name=parent.equipment_name,
            equipment_type=parent.equipment_type,
            serial_number=parent.serial_number,
            client_id=parent.client_id,
            client_name=parent.client_name,
            contract_id=parent.contract_id,
            title=parent.title,
            description=parent.description,
            scheduled_date=next_date,
            estimated_duration_hours=parent.estimated_duration_hours,
            checklist_template_id=parent.checklist_template_id,
            is_recurring=True,
            recurrence_interval_days=parent.recurrence_interval_days,
            parent_maintenance_id=str(parent.id),
        )

        self.session.add(new_maintenance)
        await self.session.flush()
        await self.session.refresh(new_maintenance)
        logger.info(
            f"Manutenção recorrente criada: {new_maintenance.maintenance_code}"
        )
        return new_maintenance
