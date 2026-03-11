"""
DEPRECATED: Guardian integration — scheduled for extraction to separate microservice.
Do not add new features. Existing code preserved for backward compatibility.
Deprecation date: 2026-03-11

Repository para GuardianOccurrence.
"""

import builtins
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.campo.models.guardian_occurrence import (
    GuardianOccurrence,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from modules.campo.schemas.guardian_occurrence import (
    GuardianOccurrenceCreate,
    GuardianOccurrenceFilter,
    GuardianOccurrenceStats,
)


class GuardianOccurrenceRepository:
    """Repository para operações com GuardianOccurrence."""

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o repository."""
        self.db = db

    async def create(self, data: GuardianOccurrenceCreate) -> GuardianOccurrence:
        """Cria uma nova ocorrência."""
        occurrence_code = f"OC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"

        occurrence = GuardianOccurrence(
            guardian_id=data.guardian_id,
            occurrence_code=occurrence_code,
            occurrence_type=data.occurrence_type,
            severity=data.severity,
            client_id=data.client_id,
            contract_id=data.contract_id,
            post_id=data.post_id,
            title=data.title,
            description=data.description,
            location=data.location,
            location_details=data.location_details,
            action_taken=data.action_taken,
            action_required=data.action_required,
            involved_persons=data.involved_persons,
            witnesses=data.witnesses,
            reported_by=data.reported_by,
            reported_by_id=data.reported_by_id,
            police_notified=data.police_notified,
            police_report_number=data.police_report_number,
            fire_department_notified=data.fire_department_notified,
            ambulance_notified=data.ambulance_notified,
            images=data.images,
            videos=data.videos,
            audio_recordings=data.audio_recordings,
            attachments=data.attachments,
            event_timestamp=data.event_timestamp,
            guardian_metadata=data.guardian_metadata,
            tags=data.tags,
            status=OccurrenceStatus.OPEN.value,
        )

        self.db.add(occurrence)
        await self.db.commit()
        await self.db.refresh(occurrence)
        return occurrence

    async def get_by_id(self, occurrence_id: str) -> GuardianOccurrence | None:
        """Busca ocorrência por ID."""
        result = await self.db.execute(
            select(GuardianOccurrence).where(
                GuardianOccurrence.id == occurrence_id,
                GuardianOccurrence.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, occurrence_code: str) -> GuardianOccurrence | None:
        """Busca ocorrência por código."""
        result = await self.db.execute(
            select(GuardianOccurrence).where(
                GuardianOccurrence.occurrence_code == occurrence_code,
                GuardianOccurrence.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_guardian_id(
        self,
        guardian_id: str,
    ) -> GuardianOccurrence | None:
        """Busca ocorrência por ID do Guardian."""
        result = await self.db.execute(
            select(GuardianOccurrence).where(
                GuardianOccurrence.guardian_id == guardian_id,
                GuardianOccurrence.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    def _apply_basic_filters(self, query, filters: GuardianOccurrenceFilter):
        """Aplica filtros básicos à query."""
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    GuardianOccurrence.occurrence_code.ilike(search_term),
                    GuardianOccurrence.title.ilike(search_term),
                    GuardianOccurrence.description.ilike(search_term),
                    GuardianOccurrence.location.ilike(search_term),
                )
            )

        # Filtros de igualdade simples
        simple_filters = [
            (filters.occurrence_type, GuardianOccurrence.occurrence_type),
            (filters.severity, GuardianOccurrence.severity),
            (filters.status, GuardianOccurrence.status),
            (filters.client_id, GuardianOccurrence.client_id),
            (filters.post_id, GuardianOccurrence.post_id),
        ]
        for value, column in simple_filters:
            if value:
                query = query.where(column == value)

        if filters.is_critical is True:
            query = query.where(GuardianOccurrence.severity == OccurrenceSeverity.CRITICAL.value)

        if filters.is_false_alarm is not None:
            query = query.where(GuardianOccurrence.is_false_alarm == filters.is_false_alarm)

        if filters.requires_followup is not None:
            query = query.where(GuardianOccurrence.requires_followup == filters.requires_followup)

        return query

    def _apply_status_and_date_filters(self, query, filters: GuardianOccurrenceFilter):
        """Aplica filtros de status e data à query."""
        if filters.is_open is True:
            open_statuses = [
                OccurrenceStatus.OPEN.value,
                OccurrenceStatus.ACKNOWLEDGED.value,
                OccurrenceStatus.IN_PROGRESS.value,
            ]
            query = query.where(GuardianOccurrence.status.in_(open_statuses))
        elif filters.is_open is False:
            closed_statuses = [
                OccurrenceStatus.RESOLVED.value,
                OccurrenceStatus.CLOSED.value,
                OccurrenceStatus.CANCELLED.value,
            ]
            query = query.where(GuardianOccurrence.status.in_(closed_statuses))

        if filters.date_from:
            query = query.where(GuardianOccurrence.event_timestamp >= filters.date_from)

        if filters.date_to:
            query = query.where(GuardianOccurrence.event_timestamp <= filters.date_to)

        return query

    async def list(
        self,
        filters: GuardianOccurrenceFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[GuardianOccurrence], int]:
        """Lista ocorrências com filtros e paginação."""
        query = select(GuardianOccurrence).where(GuardianOccurrence.is_active.is_(True))

        # Aplicar filtros
        query = self._apply_basic_filters(query, filters)
        query = self._apply_status_and_date_filters(query, filters)

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Aplicar paginação
        offset = (page - 1) * page_size
        query = query.order_by(GuardianOccurrence.event_timestamp.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        occurrences = list(result.scalars().all())

        return occurrences, total

    async def get_open(
        self,
        client_id: str | None = None,
        limit: int = 100,
    ) -> builtins.list[GuardianOccurrence]:
        """Busca ocorrências abertas."""
        open_statuses = [
            OccurrenceStatus.OPEN.value,
            OccurrenceStatus.ACKNOWLEDGED.value,
            OccurrenceStatus.IN_PROGRESS.value,
            OccurrenceStatus.ESCALATED.value,
        ]

        query = select(GuardianOccurrence).where(
            GuardianOccurrence.status.in_(open_statuses),
            GuardianOccurrence.is_active.is_(True),
        )

        if client_id:
            query = query.where(GuardianOccurrence.client_id == client_id)

        query = query.order_by(
            GuardianOccurrence.severity.desc(),
            GuardianOccurrence.event_timestamp.desc(),
        ).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_critical_open(self, limit: int = 50) -> builtins.list[GuardianOccurrence]:
        """Busca ocorrências críticas abertas."""
        open_statuses = [
            OccurrenceStatus.OPEN.value,
            OccurrenceStatus.ACKNOWLEDGED.value,
            OccurrenceStatus.IN_PROGRESS.value,
        ]

        result = await self.db.execute(
            select(GuardianOccurrence)
            .where(
                GuardianOccurrence.severity == OccurrenceSeverity.CRITICAL.value,
                GuardianOccurrence.status.in_(open_statuses),
                GuardianOccurrence.is_active.is_(True),
            )
            .order_by(GuardianOccurrence.event_timestamp)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def acknowledge(
        self,
        occurrence_id: str,
        operator_id: str,
        operator_name: str,
        notes: str | None = None,
    ) -> GuardianOccurrence | None:
        """Reconhece uma ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            occurrence.acknowledge(operator_id, operator_name)
            if notes:
                occurrence.action_taken = notes
            await self.db.commit()
            await self.db.refresh(occurrence)
        return occurrence

    async def start_progress(
        self,
        occurrence_id: str,
    ) -> GuardianOccurrence | None:
        """Inicia atendimento da ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            occurrence.start_progress()
            await self.db.commit()
            await self.db.refresh(occurrence)
        return occurrence

    async def resolve(
        self,
        occurrence_id: str,
        resolution: str,
        is_false_alarm: bool = False,
        requires_followup: bool = False,
        followup_notes: str | None = None,
    ) -> GuardianOccurrence | None:
        """Resolve uma ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            if is_false_alarm:
                occurrence.mark_as_false_alarm()
            else:
                occurrence.resolve(resolution)
            occurrence.requires_followup = requires_followup
            if followup_notes:
                occurrence.followup_notes = followup_notes
            await self.db.commit()
            await self.db.refresh(occurrence)
        return occurrence

    async def escalate(
        self,
        occurrence_id: str,
        escalated_to: str,
        reason: str,
    ) -> GuardianOccurrence | None:
        """Escala uma ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            occurrence.escalate(escalated_to, reason)
            await self.db.commit()
            await self.db.refresh(occurrence)
        return occurrence

    async def close(self, occurrence_id: str) -> GuardianOccurrence | None:
        """Fecha uma ocorrência."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            occurrence.close()
            await self.db.commit()
            await self.db.refresh(occurrence)
        return occurrence

    async def get_stats(  # pylint: disable=too-many-locals
        self,
        client_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> GuardianOccurrenceStats:
        """Retorna estatísticas de ocorrências."""
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()

        base_query = select(GuardianOccurrence).where(
            GuardianOccurrence.is_active.is_(True),
            GuardianOccurrence.event_timestamp >= date_from,
            GuardianOccurrence.event_timestamp <= date_to,
        )

        if client_id:
            base_query = base_query.where(GuardianOccurrence.client_id == client_id)

        # Contagem total
        total_result = await self.db.execute(select(func.count()).select_from(base_query.subquery()))
        total = total_result.scalar() or 0

        # Contagem por status
        status_counts = {}
        for status in OccurrenceStatus:
            status_query = base_query.where(GuardianOccurrence.status == status.value)
            count_result = await self.db.execute(select(func.count()).select_from(status_query.subquery()))
            status_counts[status.value] = count_result.scalar() or 0

        # Contagem por tipo
        type_counts = {}
        for occ_type in OccurrenceType:
            type_query = base_query.where(GuardianOccurrence.occurrence_type == occ_type.value)
            count_result = await self.db.execute(select(func.count()).select_from(type_query.subquery()))
            type_counts[occ_type.value] = count_result.scalar() or 0

        # Contagem por gravidade
        severity_counts = {}
        for severity in OccurrenceSeverity:
            sev_query = base_query.where(GuardianOccurrence.severity == severity.value)
            count_result = await self.db.execute(select(func.count()).select_from(sev_query.subquery()))
            severity_counts[severity.value] = count_result.scalar() or 0

        # Falsos alarmes
        false_alarm_result = await self.db.execute(
            select(func.count()).select_from(base_query.where(GuardianOccurrence.is_false_alarm.is_(True)).subquery())
        )
        false_alarms = false_alarm_result.scalar() or 0

        # Críticas abertas
        critical_open_result = await self.db.execute(
            select(func.count()).select_from(
                base_query.where(
                    GuardianOccurrence.severity == OccurrenceSeverity.CRITICAL.value,
                    GuardianOccurrence.status.in_(
                        [
                            OccurrenceStatus.OPEN.value,
                            OccurrenceStatus.ACKNOWLEDGED.value,
                            OccurrenceStatus.IN_PROGRESS.value,
                        ]
                    ),
                ).subquery()
            )
        )
        critical_open = critical_open_result.scalar() or 0

        # Aguardando follow-up
        followup_result = await self.db.execute(
            select(func.count()).select_from(
                base_query.where(GuardianOccurrence.requires_followup.is_(True)).subquery()
            )
        )
        requires_followup_count = followup_result.scalar() or 0

        # Tempos médios
        avg_response_result = await self.db.execute(
            select(func.avg(GuardianOccurrence.response_time_seconds)).where(
                GuardianOccurrence.is_active.is_(True),
                GuardianOccurrence.response_time_seconds.isnot(None),
            )
        )
        avg_response = avg_response_result.scalar() or 0.0

        avg_resolution_result = await self.db.execute(
            select(func.avg(GuardianOccurrence.resolution_time_seconds)).where(
                GuardianOccurrence.is_active.is_(True),
                GuardianOccurrence.resolution_time_seconds.isnot(None),
            )
        )
        avg_resolution = avg_resolution_result.scalar() or 0.0

        return GuardianOccurrenceStats(
            total=total,
            open=status_counts.get(OccurrenceStatus.OPEN.value, 0),
            acknowledged=status_counts.get(OccurrenceStatus.ACKNOWLEDGED.value, 0),
            in_progress=status_counts.get(OccurrenceStatus.IN_PROGRESS.value, 0),
            resolved=status_counts.get(OccurrenceStatus.RESOLVED.value, 0),
            escalated=status_counts.get(OccurrenceStatus.ESCALATED.value, 0),
            closed=status_counts.get(OccurrenceStatus.CLOSED.value, 0),
            false_alarms=false_alarms,
            by_type=type_counts,
            by_severity=severity_counts,
            avg_response_time_seconds=round(float(avg_response), 2),
            avg_resolution_time_seconds=round(float(avg_resolution), 2),
            critical_open=critical_open,
            requires_followup_count=requires_followup_count,
        )

    async def delete(self, occurrence_id: str) -> bool:
        """Remove uma ocorrência (soft delete)."""
        occurrence = await self.get_by_id(occurrence_id)
        if occurrence:
            occurrence.is_active = False
            await self.db.commit()
            return True
        return False
