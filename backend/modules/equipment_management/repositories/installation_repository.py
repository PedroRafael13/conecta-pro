"""Repository para EquipmentInstallation."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.models.installation import (
    EquipmentInstallation,
    InstallationStatus,
)
from modules.equipment_management.schemas.installation import (
    InstallationCreate,
    InstallationFilter,
    InstallationUpdate,
)

logger = logging.getLogger(__name__)


class InstallationRepository:
    """Repository para operações de EquipmentInstallation."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: InstallationCreate) -> EquipmentInstallation:
        """Cria uma nova instalação."""
        installation = EquipmentInstallation(
            client_id=data.client_id,
            client_name=data.client_name,
            contract_id=data.contract_id,
            post_id=data.post_id,
            address=data.address,
            address_complement=data.address_complement,
            city=data.city,
            state=data.state,
            zip_code=data.zip_code,
            gps_latitude=data.gps_latitude,
            gps_longitude=data.gps_longitude,
            location_details=data.location_details,
            scheduled_date=data.scheduled_date,
            scheduled_time_start=data.scheduled_time_start,
            scheduled_time_end=data.scheduled_time_end,
            estimated_duration_hours=data.estimated_duration_hours,
            equipment_ids=data.equipment_ids,
            technician_id=data.technician_id,
            technician_name=data.technician_name,
            priority=data.priority,
            notes=data.notes,
        )
        self.session.add(installation)
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação criada: {installation.installation_code}")
        return installation

    async def get_by_id(
        self, installation_id: str | UUID
    ) -> Optional[EquipmentInstallation]:
        """Busca instalação por ID."""
        if isinstance(installation_id, str):
            installation_id = UUID(installation_id)
        result = await self.session.execute(
            select(EquipmentInstallation).where(
                and_(
                    EquipmentInstallation.id == installation_id,
                    EquipmentInstallation.is_active.is_(True),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[EquipmentInstallation]:
        """Busca instalação por código."""
        result = await self.session.execute(
            select(EquipmentInstallation).where(
                and_(
                    EquipmentInstallation.installation_code == code,
                    EquipmentInstallation.is_active.is_(True),
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, installation_id: str | UUID, data: InstallationUpdate
    ) -> Optional[EquipmentInstallation]:
        """Atualiza uma instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(installation, field, value)

        installation.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação atualizada: {installation.installation_code}")
        return installation

    async def delete(self, installation_id: str | UUID) -> bool:
        """Soft delete de instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return False

        installation.is_active = False
        installation.updated_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Instalação desativada: {installation.installation_code}")
        return True

    async def list_with_filters(  # pylint: disable=too-many-branches
        self,
        filters: Optional[InstallationFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EquipmentInstallation], int]:
        """Lista instalações com filtros e paginação."""
        query = select(EquipmentInstallation).where(
            EquipmentInstallation.is_active.is_(True)
        )

        if filters:
            conditions = []

            if filters.search:
                search_term = f"%{filters.search}%"
                conditions.append(
                    or_(
                        EquipmentInstallation.installation_code.ilike(search_term),
                        EquipmentInstallation.client_name.ilike(search_term),
                        EquipmentInstallation.address.ilike(search_term),
                        EquipmentInstallation.technician_name.ilike(search_term),
                    )
                )

            if filters.status:
                conditions.append(EquipmentInstallation.status == filters.status)

            if filters.client_id:
                conditions.append(EquipmentInstallation.client_id == filters.client_id)

            if filters.technician_id:
                conditions.append(
                    EquipmentInstallation.technician_id == filters.technician_id
                )

            if filters.priority:
                conditions.append(EquipmentInstallation.priority == filters.priority)

            if filters.date_from:
                conditions.append(
                    EquipmentInstallation.scheduled_date >= filters.date_from
                )

            if filters.date_to:
                conditions.append(
                    EquipmentInstallation.scheduled_date <= filters.date_to
                )

            if filters.is_overdue is not None:
                now = datetime.utcnow()
                if filters.is_overdue:
                    conditions.append(
                        and_(
                            EquipmentInstallation.scheduled_date < now,
                            EquipmentInstallation.status.in_(
                                [
                                    InstallationStatus.SCHEDULED,
                                    InstallationStatus.PENDING_APPROVAL,
                                ]
                            ),
                        )
                    )
                else:
                    conditions.append(
                        or_(
                            EquipmentInstallation.scheduled_date >= now,
                            EquipmentInstallation.status.in_(
                                [
                                    InstallationStatus.COMPLETED,
                                    InstallationStatus.CANCELLED,
                                ]
                            ),
                        )
                    )

            if filters.has_acceptance is not None:
                conditions.append(
                    EquipmentInstallation.client_accepted == filters.has_acceptance
                )

            if conditions:
                query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        query = query.order_by(EquipmentInstallation.scheduled_date.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_client(self, client_id: str) -> list[EquipmentInstallation]:
        """Lista instalações de um cliente."""
        result = await self.session.execute(
            select(EquipmentInstallation)
            .where(
                and_(
                    EquipmentInstallation.client_id == client_id,
                    EquipmentInstallation.is_active.is_(True),
                )
            )
            .order_by(EquipmentInstallation.scheduled_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_technician(
        self, technician_id: str, include_completed: bool = False
    ) -> list[EquipmentInstallation]:
        """Lista instalações de um técnico."""
        conditions = [
            EquipmentInstallation.technician_id == technician_id,
            EquipmentInstallation.is_active.is_(True),
        ]

        if not include_completed:
            conditions.append(
                EquipmentInstallation.status.in_(
                    [
                        InstallationStatus.SCHEDULED,
                        InstallationStatus.IN_PROGRESS,
                        InstallationStatus.PENDING_APPROVAL,
                    ]
                )
            )

        result = await self.session.execute(
            select(EquipmentInstallation)
            .where(and_(*conditions))
            .order_by(EquipmentInstallation.scheduled_date)
        )
        return list(result.scalars().all())

    async def get_scheduled_for_date(
        self, date: datetime
    ) -> list[EquipmentInstallation]:
        """Lista instalações agendadas para uma data."""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        result = await self.session.execute(
            select(EquipmentInstallation)
            .where(
                and_(
                    EquipmentInstallation.scheduled_date >= start,
                    EquipmentInstallation.scheduled_date < end,
                    EquipmentInstallation.is_active.is_(True),
                    EquipmentInstallation.status != InstallationStatus.CANCELLED,
                )
            )
            .order_by(EquipmentInstallation.scheduled_date)
        )
        return list(result.scalars().all())

    async def get_overdue(self) -> list[EquipmentInstallation]:
        """Lista instalações atrasadas."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(EquipmentInstallation)
            .where(
                and_(
                    EquipmentInstallation.scheduled_date < now,
                    EquipmentInstallation.status.in_(
                        [
                            InstallationStatus.SCHEDULED,
                            InstallationStatus.PENDING_APPROVAL,
                        ]
                    ),
                    EquipmentInstallation.is_active.is_(True),
                )
            )
            .order_by(EquipmentInstallation.scheduled_date)
        )
        return list(result.scalars().all())

    async def get_pending_acceptance(self) -> list[EquipmentInstallation]:
        """Lista instalações aguardando aceite do cliente."""
        result = await self.session.execute(
            select(EquipmentInstallation)
            .where(
                and_(
                    EquipmentInstallation.status == InstallationStatus.PENDING_APPROVAL,
                    EquipmentInstallation.client_accepted.is_(False),
                    EquipmentInstallation.is_active.is_(True),
                )
            )
            .order_by(EquipmentInstallation.completed_at)
        )
        return list(result.scalars().all())

    async def start(self, installation_id: str | UUID) -> Optional[EquipmentInstallation]:
        """Inicia uma instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        installation.start()
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação iniciada: {installation.installation_code}")
        return installation

    async def complete(
        self,
        installation_id: str | UUID,
        technical_report: Optional[str] = None,
    ) -> Optional[EquipmentInstallation]:
        """Conclui uma instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        installation.complete(technical_report=technical_report)
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação concluída: {installation.installation_code}")
        return installation

    async def cancel(
        self, installation_id: str | UUID, reason: str
    ) -> Optional[EquipmentInstallation]:
        """Cancela uma instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        installation.cancel(reason=reason)
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação cancelada: {installation.installation_code}")
        return installation

    async def reschedule(
        self,
        installation_id: str | UUID,
        new_date: datetime,
        reason: Optional[str] = None,
    ) -> Optional[EquipmentInstallation]:
        """Reagenda uma instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        installation.reschedule(new_date=new_date, reason=reason)
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação reagendada: {installation.installation_code}")
        return installation

    async def accept_by_client(
        self, installation_id: str | UUID, accepted_by: str
    ) -> Optional[EquipmentInstallation]:
        """Registra aceite do cliente."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        installation.accept_by_client(accepted_by=accepted_by)
        await self.session.flush()
        await self.session.refresh(installation)
        logger.info(f"Instalação aceita pelo cliente: {installation.installation_code}")
        return installation

    async def add_photo(
        self,
        installation_id: str | UUID,
        photo_url: str,
        photo_type: str = "after",
    ) -> Optional[EquipmentInstallation]:
        """Adiciona foto à instalação."""
        installation = await self.get_by_id(installation_id)
        if not installation:
            return None

        installation.add_photo(url=photo_url, photo_type=photo_type)
        await self.session.flush()
        await self.session.refresh(installation)
        return installation

    async def get_stats_by_period(
        self, date_from: datetime, date_to: datetime
    ) -> dict:
        """Estatísticas de instalações por período."""
        result = await self.session.execute(
            select(EquipmentInstallation).where(
                and_(
                    EquipmentInstallation.scheduled_date >= date_from,
                    EquipmentInstallation.scheduled_date <= date_to,
                    EquipmentInstallation.is_active.is_(True),
                )
            )
        )
        installations = list(result.scalars().all())

        stats = {
            "total": len(installations),
            "by_status": {},
            "completed": 0,
            "cancelled": 0,
            "pending": 0,
            "rescheduled": 0,
            "with_acceptance": 0,
            "avg_duration_hours": 0.0,
            "total_cost": 0.0,
        }

        durations = []
        for inst in installations:
            # Por status
            status_key = inst.status.value if inst.status else "unknown"
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            if inst.status == InstallationStatus.COMPLETED:
                stats["completed"] += 1
            elif inst.status == InstallationStatus.CANCELLED:
                stats["cancelled"] += 1
            elif inst.status in [
                InstallationStatus.SCHEDULED,
                InstallationStatus.IN_PROGRESS,
            ]:
                stats["pending"] += 1

            if inst.rescheduled_count > 0:
                stats["rescheduled"] += 1

            if inst.client_accepted:
                stats["with_acceptance"] += 1

            if inst.actual_duration_hours:
                durations.append(inst.actual_duration_hours)

            if inst.total_cost:
                stats["total_cost"] += inst.total_cost

        if durations:
            stats["avg_duration_hours"] = sum(durations) / len(durations)

        return stats
