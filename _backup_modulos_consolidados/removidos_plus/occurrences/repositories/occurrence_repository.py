"""Repository para Occurrence."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.occurrences.models.occurrence import (
    Occurrence,
    OccurrencePriority,
    OccurrenceStatus,
)
from modules.occurrences.schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceFilter,
    OccurrenceUpdate,
)

logger = logging.getLogger(__name__)


class OccurrenceRepository:
    """Repository para operações de Occurrence."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: OccurrenceCreate) -> Occurrence:
        """Cria uma nova ocorrência."""
        occurrence = Occurrence(**data.model_dump(exclude_none=True))
        self.session.add(occurrence)
        await self.session.flush()
        await self.session.refresh(occurrence)
        logger.info(f"Ocorrência criada: {occurrence.occurrence_code}")
        return occurrence

    async def get_by_id(
        self, occurrence_id: str | UUID, include_relations: bool = False
    ) -> Optional[Occurrence]:
        """Busca ocorrência por ID."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        query = select(Occurrence).where(Occurrence.id == occurrence_id)
        if include_relations:
            query = query.options(
                selectinload(Occurrence.category),
                selectinload(Occurrence.comments),
                selectinload(Occurrence.attachments),
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Occurrence]:
        """Busca ocorrência por código."""
        result = await self.session.execute(
            select(Occurrence).where(Occurrence.occurrence_code == code)
        )
        return result.scalar_one_or_none()

    async def update(
        self, occurrence_id: str | UUID, data: OccurrenceUpdate
    ) -> Optional[Occurrence]:
        """Atualiza uma ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(occurrence, field, value)

        occurrence.increment_updates()
        await self.session.flush()
        await self.session.refresh(occurrence)
        return occurrence

    async def delete(self, occurrence_id: str | UUID) -> bool:
        """Deleta uma ocorrência (soft delete)."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return False

        occurrence.is_active = False
        await self.session.flush()
        return True

    async def list_with_filters(  # pylint: disable=too-many-branches
        self,
        filters: Optional[OccurrenceFilter] = None,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Occurrence], int]:
        """Lista ocorrências com filtros."""
        query = select(Occurrence).where(Occurrence.is_active.is_(True))

        if filters:
            if filters.occurrence_type:
                query = query.where(Occurrence.occurrence_type == filters.occurrence_type)
            if filters.category_id:
                query = query.where(Occurrence.category_id == UUID(filters.category_id))
            if filters.priority:
                query = query.where(Occurrence.priority == filters.priority)
            if filters.status:
                query = query.where(Occurrence.status == filters.status)
            if filters.condominium_id:
                query = query.where(Occurrence.condominium_id == filters.condominium_id)
            if filters.unit_id:
                query = query.where(Occurrence.unit_id == filters.unit_id)
            if filters.reporter_id:
                query = query.where(Occurrence.reporter_id == filters.reporter_id)
            if filters.reporter_type:
                query = query.where(Occurrence.reporter_type == filters.reporter_type)
            if filters.assigned_to_id:
                query = query.where(Occurrence.assigned_to_id == filters.assigned_to_id)
            if filters.is_anonymous is not None:
                query = query.where(Occurrence.is_anonymous == filters.is_anonymous)
            if filters.is_escalated is not None:
                query = query.where(Occurrence.is_escalated == filters.is_escalated)
            if filters.is_open is not None:
                if filters.is_open:
                    query = query.where(
                        Occurrence.status.in_([
                            OccurrenceStatus.ABERTA,
                            OccurrenceStatus.EM_ANALISE,
                            OccurrenceStatus.EM_ANDAMENTO,
                            OccurrenceStatus.AGUARDANDO_RESPOSTA,
                            OccurrenceStatus.AGUARDANDO_TERCEIRO,
                            OccurrenceStatus.REABERTA,
                        ])
                    )
                else:
                    query = query.where(
                        Occurrence.status.in_([
                            OccurrenceStatus.RESOLVIDA,
                            OccurrenceStatus.ARQUIVADA,
                            OccurrenceStatus.CANCELADA,
                        ])
                    )
            if filters.date_from:
                query = query.where(Occurrence.created_at >= filters.date_from)
            if filters.date_to:
                query = query.where(Occurrence.created_at <= filters.date_to)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Occurrence.title.ilike(search_term),
                        Occurrence.description.ilike(search_term),
                        Occurrence.occurrence_code.ilike(search_term),
                    )
                )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Order and paginate
        order_column = getattr(Occurrence, order_by, Occurrence.created_at)
        if order_desc:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        occurrences = list(result.scalars().all())

        return occurrences, total

    async def get_by_condominium(
        self, condominium_id: str, skip: int = 0, limit: int = 20
    ) -> list[Occurrence]:
        """Lista ocorrências por condomínio."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.condominium_id == condominium_id,
                    Occurrence.is_active.is_(True),
                )
            )
            .order_by(Occurrence.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_reporter(
        self, reporter_id: str, skip: int = 0, limit: int = 20
    ) -> list[Occurrence]:
        """Lista ocorrências por reportador."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.reporter_id == reporter_id,
                    Occurrence.is_active.is_(True),
                )
            )
            .order_by(Occurrence.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_assigned(
        self, assigned_to_id: str, skip: int = 0, limit: int = 20
    ) -> list[Occurrence]:
        """Lista ocorrências por responsável."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.assigned_to_id == assigned_to_id,
                    Occurrence.is_active.is_(True),
                )
            )
            .order_by(Occurrence.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_open(self, skip: int = 0, limit: int = 20) -> list[Occurrence]:
        """Lista ocorrências abertas."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.status.in_([
                        OccurrenceStatus.ABERTA,
                        OccurrenceStatus.EM_ANALISE,
                        OccurrenceStatus.EM_ANDAMENTO,
                        OccurrenceStatus.AGUARDANDO_RESPOSTA,
                        OccurrenceStatus.AGUARDANDO_TERCEIRO,
                        OccurrenceStatus.REABERTA,
                    ]),
                    Occurrence.is_active.is_(True),
                )
            )
            .order_by(Occurrence.priority.desc(), Occurrence.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_overdue(self, skip: int = 0, limit: int = 20) -> list[Occurrence]:
        """Lista ocorrências atrasadas."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.is_active.is_(True),
                    Occurrence.closed_at.is_(None),
                    or_(
                        and_(
                            Occurrence.sla_response_deadline.isnot(None),
                            Occurrence.first_response_at.is_(None),
                            Occurrence.sla_response_deadline < now,
                        ),
                        and_(
                            Occurrence.sla_resolution_deadline.isnot(None),
                            Occurrence.resolved_at.is_(None),
                            Occurrence.sla_resolution_deadline < now,
                        ),
                    ),
                )
            )
            .order_by(Occurrence.priority.desc(), Occurrence.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_escalated(self, skip: int = 0, limit: int = 20) -> list[Occurrence]:
        """Lista ocorrências escalonadas."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.is_escalated.is_(True),
                    Occurrence.is_active.is_(True),
                    Occurrence.closed_at.is_(None),
                )
            )
            .order_by(Occurrence.escalation_level.desc(), Occurrence.escalated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_high_priority(self, skip: int = 0, limit: int = 20) -> list[Occurrence]:
        """Lista ocorrências de alta prioridade."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.priority.in_([
                        OccurrencePriority.ALTA,
                        OccurrencePriority.URGENTE,
                        OccurrencePriority.CRITICA,
                    ]),
                    Occurrence.is_active.is_(True),
                    Occurrence.closed_at.is_(None),
                )
            )
            .order_by(Occurrence.priority.desc(), Occurrence.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_unassigned(self, skip: int = 0, limit: int = 20) -> list[Occurrence]:
        """Lista ocorrências não atribuídas."""
        result = await self.session.execute(
            select(Occurrence)
            .where(
                and_(
                    Occurrence.assigned_to_id.is_(None),
                    Occurrence.is_active.is_(True),
                    Occurrence.closed_at.is_(None),
                )
            )
            .order_by(Occurrence.priority.desc(), Occurrence.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_stats(  # pylint: disable=too-many-branches,too-many-locals,too-many-statements
        self, condominium_id: Optional[str] = None, date_from: Optional[datetime] = None
    ) -> dict:
        """Retorna estatísticas de ocorrências."""
        base_query = select(Occurrence).where(Occurrence.is_active.is_(True))

        if condominium_id:
            base_query = base_query.where(Occurrence.condominium_id == condominium_id)
        if date_from:
            base_query = base_query.where(Occurrence.created_at >= date_from)

        result = await self.session.execute(base_query)
        occurrences = list(result.scalars().all())

        now = datetime.utcnow()
        stats = {
            "total": len(occurrences),
            "open": 0,
            "closed": 0,
            "resolved": 0,
            "cancelled": 0,
            "escalated": 0,
            "overdue_response": 0,
            "overdue_resolution": 0,
            "by_type": {},
            "by_priority": {},
            "by_status": {},
            "by_category": {},
            "resolution_times": [],
            "response_times": [],
            "satisfaction_scores": [],
        }

        for occ in occurrences:
            # Status counts
            if occ.status in [
                OccurrenceStatus.ABERTA,
                OccurrenceStatus.EM_ANALISE,
                OccurrenceStatus.EM_ANDAMENTO,
                OccurrenceStatus.AGUARDANDO_RESPOSTA,
                OccurrenceStatus.AGUARDANDO_TERCEIRO,
                OccurrenceStatus.REABERTA,
            ]:
                stats["open"] += 1
            else:
                stats["closed"] += 1

            if occ.status == OccurrenceStatus.RESOLVIDA:
                stats["resolved"] += 1
            if occ.status == OccurrenceStatus.CANCELADA:
                stats["cancelled"] += 1
            if occ.is_escalated:
                stats["escalated"] += 1

            # SLA checks
            if occ.sla_response_deadline and not occ.first_response_at:
                if occ.sla_response_deadline < now:
                    stats["overdue_response"] += 1
            if occ.sla_resolution_deadline and not occ.resolved_at and not occ.closed_at:
                if occ.sla_resolution_deadline < now:
                    stats["overdue_resolution"] += 1

            # By type
            type_key = occ.occurrence_type.value if occ.occurrence_type else "unknown"
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1

            # By priority
            priority_key = occ.priority.value if occ.priority else "unknown"
            stats["by_priority"][priority_key] = stats["by_priority"].get(priority_key, 0) + 1

            # By status
            status_key = occ.status.value if occ.status else "unknown"
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            # By category
            if occ.category_id:
                cat_id = str(occ.category_id)
                stats["by_category"][cat_id] = stats["by_category"].get(cat_id, 0) + 1

            # Times
            if occ.resolved_at:
                resolution_hours = (occ.resolved_at - occ.created_at).total_seconds() / 3600
                stats["resolution_times"].append(resolution_hours)
            if occ.first_response_at:
                response_hours = (occ.first_response_at - occ.created_at).total_seconds() / 3600
                stats["response_times"].append(response_hours)
            if occ.satisfaction_rating:
                stats["satisfaction_scores"].append(occ.satisfaction_rating)

        # Calculate averages
        if stats["resolution_times"]:
            res_times = stats["resolution_times"]
            stats["avg_resolution_hours"] = sum(res_times) / len(res_times)
        else:
            stats["avg_resolution_hours"] = None

        if stats["response_times"]:
            resp_times = stats["response_times"]
            stats["avg_response_hours"] = sum(resp_times) / len(resp_times)
        else:
            stats["avg_response_hours"] = None

        if stats["satisfaction_scores"]:
            sat_scores = stats["satisfaction_scores"]
            stats["avg_satisfaction"] = sum(sat_scores) / len(sat_scores)
        else:
            stats["avg_satisfaction"] = None

        # SLA rates
        resolved_count = stats["resolved"]
        if resolved_count > 0:
            sla_response_met = sum(1 for occ in occurrences if occ.sla_response_met is True)
            sla_resolution_met = sum(1 for occ in occurrences if occ.sla_resolution_met is True)
            stats["sla_response_rate"] = (sla_response_met / resolved_count) * 100
            stats["sla_resolution_rate"] = (sla_resolution_met / resolved_count) * 100
        else:
            stats["sla_response_rate"] = None
            stats["sla_resolution_rate"] = None

        # Remove temporary lists
        del stats["resolution_times"]
        del stats["response_times"]
        del stats["satisfaction_scores"]

        return stats

    async def assign(
        self,
        occurrence_id: str | UUID,
        assignee_id: str,
        assignee_name: str,
        assigned_by_id: str = None,
        assigned_by_name: str = None,
    ) -> Optional[Occurrence]:
        """Atribui responsável."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return None

        occurrence.assign(assignee_id, assignee_name, assigned_by_id, assigned_by_name)
        await self.session.flush()
        return occurrence

    async def resolve(
        self,
        occurrence_id: str | UUID,
        resolved_by_id: str,
        resolved_by_name: str,
        description: str = None,
        resolution_type: str = None,
    ) -> Optional[Occurrence]:
        """Resolve a ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return None

        occurrence.resolve(resolved_by_id, resolved_by_name, description, resolution_type)
        await self.session.flush()
        return occurrence

    async def escalate(
        self,
        occurrence_id: str | UUID,
        escalated_to_id: str,
        escalated_to_name: str,
        reason: str = None,
    ) -> Optional[Occurrence]:
        """Escalona a ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return None

        occurrence.escalate(escalated_to_id, escalated_to_name, reason)
        await self.session.flush()
        return occurrence

    async def change_status(
        self, occurrence_id: str | UUID, new_status: OccurrenceStatus, reason: str = None
    ) -> Optional[Occurrence]:
        """Altera status da ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return None

        old_status = occurrence.status
        occurrence.status = new_status
        msg = f"{old_status.value} -> {new_status.value}: {reason or 'N/A'}"
        occurrence._add_history("status_change", msg)  # pylint: disable=protected-access
        occurrence.increment_updates()

        closed_statuses = [
            OccurrenceStatus.RESOLVIDA,
            OccurrenceStatus.ARQUIVADA,
            OccurrenceStatus.CANCELADA,
        ]
        if new_status in closed_statuses:
            occurrence.closed_at = datetime.utcnow()

        await self.session.flush()
        return occurrence

    async def rate(
        self, occurrence_id: str | UUID, rating: int, comment: str = None
    ) -> Optional[Occurrence]:
        """Avalia a ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if not occurrence:
            return None

        occurrence.rate(rating, comment)
        await self.session.flush()
        return occurrence

    async def increment_views(self, occurrence_id: str | UUID) -> None:
        """Incrementa visualizações."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            occurrence.increment_views()
            await self.session.flush()
