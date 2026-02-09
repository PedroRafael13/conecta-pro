"""Repository para TimeEntry."""

import builtins
from datetime import date
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.time_tracking.models import (
    AnomalyType,
    EntryStatus,
    EntryType,
    TimeEntry,
)
from modules.hr.time_tracking.schemas import (
    TimeEntryCreate,
    TimeEntryFilter,
    TimeEntryUpdate,
)


class TimeEntryRepository:
    """Repository para operações de TimeEntry."""

    def __init__(self, db: AsyncSession):
        """Inicializa o repository.

        Args:
            db: Sessão do banco de dados
        """
        self.db = db

    async def create(
        self,
        data: TimeEntryCreate,
        created_by_id: str = None,
    ) -> TimeEntry:
        """Cria um novo registro de ponto.

        Args:
            data: Dados do registro
            created_by_id: ID do criador

        Returns:
            TimeEntry: Registro criado
        """
        entry = TimeEntry(
            **data.model_dump(exclude_unset=True),
            created_by_id=created_by_id,
        )
        entry.calculate_difference()
        entry.detect_anomaly()
        entry.calculate_night_hours()

        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def get_by_id(self, entry_id: UUID) -> TimeEntry | None:
        """Busca registro por ID.

        Args:
            entry_id: ID do registro

        Returns:
            TimeEntry ou None
        """
        result = await self.db.execute(
            select(TimeEntry).where(
                TimeEntry.id == entry_id,
                TimeEntry.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> TimeEntry | None:
        """Busca registro por código.

        Args:
            code: Código do registro

        Returns:
            TimeEntry ou None
        """
        result = await self.db.execute(
            select(TimeEntry).where(
                TimeEntry.code == code,
                TimeEntry.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        entry: TimeEntry,
        data: TimeEntryUpdate,
    ) -> TimeEntry:
        """Atualiza um registro.

        Args:
            entry: Registro a atualizar
            data: Dados de atualização

        Returns:
            TimeEntry: Registro atualizado
        """
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)

        entry.calculate_difference()
        entry.detect_anomaly()

        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def delete(self, entry: TimeEntry) -> None:
        """Soft delete de um registro.

        Args:
            entry: Registro a deletar
        """
        entry.soft_delete()
        await self.db.flush()

    async def list(  # pylint: disable=too-many-branches
        self,
        filters: TimeEntryFilter = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[TimeEntry], int]:
        """Lista registros com filtros.

        Args:
            filters: Filtros opcionais
            skip: Offset
            limit: Limite

        Returns:
            Tuple: (registros, total)
        """
        query = select(TimeEntry).where(TimeEntry.is_deleted.is_(False))

        if filters:
            if filters.employee_id:
                query = query.where(TimeEntry.employee_id == filters.employee_id)
            if filters.entry_type:
                query = query.where(TimeEntry.entry_type == filters.entry_type)
            if filters.status:
                query = query.where(TimeEntry.status == filters.status)
            if filters.registration_method:
                query = query.where(TimeEntry.registration_method == filters.registration_method)
            if filters.anomaly_type:
                query = query.where(TimeEntry.anomaly_type == filters.anomaly_type)
            if filters.condominium_id:
                query = query.where(TimeEntry.condominium_id == filters.condominium_id)
            if filters.department_id:
                query = query.where(TimeEntry.department_id == filters.department_id)
            if filters.date_from:
                query = query.where(TimeEntry.entry_date >= filters.date_from)
            if filters.date_to:
                query = query.where(TimeEntry.entry_date <= filters.date_to)
            if filters.has_anomaly is not None:
                if filters.has_anomaly:
                    query = query.where(
                        TimeEntry.anomaly_type != AnomalyType.SEM_ANOMALIA,
                        TimeEntry.anomaly_resolved.is_(False),
                    )
                else:
                    query = query.where(
                        or_(
                            TimeEntry.anomaly_type == AnomalyType.SEM_ANOMALIA,
                            TimeEntry.anomaly_resolved.is_(True),
                        )
                    )
            if filters.requires_approval is not None:
                query = query.where(TimeEntry.requires_approval == filters.requires_approval)
            if filters.is_manual_entry is not None:
                query = query.where(TimeEntry.is_manual_entry == filters.is_manual_entry)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginação
        query = (
            query.order_by(
                TimeEntry.entry_date.desc(),
                TimeEntry.entry_time.desc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        entries = result.scalars().all()

        return list(entries), total

    async def get_by_employee_date(
        self,
        employee_id: str,
        entry_date: date,
    ) -> builtins.list[TimeEntry]:
        """Busca registros de um funcionário em uma data.

        Args:
            employee_id: ID do funcionário
            entry_date: Data

        Returns:
            Lista de registros
        """
        result = await self.db.execute(
            select(TimeEntry)
            .where(
                TimeEntry.employee_id == employee_id,
                TimeEntry.entry_date == entry_date,
                TimeEntry.is_deleted.is_(False),
            )
            .order_by(TimeEntry.entry_time)
        )
        return list(result.scalars().all())

    async def get_by_employee_period(
        self,
        employee_id: str,
        start_date: date,
        end_date: date,
    ) -> builtins.list[TimeEntry]:
        """Busca registros de um funcionário em um período.

        Args:
            employee_id: ID do funcionário
            start_date: Data inicial
            end_date: Data final

        Returns:
            Lista de registros
        """
        result = await self.db.execute(
            select(TimeEntry)
            .where(
                TimeEntry.employee_id == employee_id,
                TimeEntry.entry_date >= start_date,
                TimeEntry.entry_date <= end_date,
                TimeEntry.is_deleted.is_(False),
            )
            .order_by(TimeEntry.entry_date, TimeEntry.entry_time)
        )
        return list(result.scalars().all())

    async def get_pending_approval(
        self,
        condominium_id: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> builtins.list[TimeEntry]:
        """Busca registros pendentes de aprovação.

        Args:
            condominium_id: ID do condomínio (opcional)
            skip: Offset
            limit: Limite

        Returns:
            Lista de registros
        """
        query = select(TimeEntry).where(
            TimeEntry.requires_approval.is_(True),
            TimeEntry.status == EntryStatus.PENDENTE,
            TimeEntry.is_deleted.is_(False),
        )

        if condominium_id:
            query = query.where(TimeEntry.condominium_id == condominium_id)

        query = query.order_by(TimeEntry.entry_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_with_anomalies(
        self,
        condominium_id: str = None,
        date_from: date = None,
        date_to: date = None,
        skip: int = 0,
        limit: int = 100,
    ) -> builtins.list[TimeEntry]:
        """Busca registros com anomalias não resolvidas.

        Args:
            condominium_id: ID do condomínio
            date_from: Data inicial
            date_to: Data final
            skip: Offset
            limit: Limite

        Returns:
            Lista de registros
        """
        query = select(TimeEntry).where(
            TimeEntry.anomaly_type != AnomalyType.SEM_ANOMALIA,
            TimeEntry.anomaly_resolved.is_(False),
            TimeEntry.is_deleted.is_(False),
        )

        if condominium_id:
            query = query.where(TimeEntry.condominium_id == condominium_id)
        if date_from:
            query = query.where(TimeEntry.entry_date >= date_from)
        if date_to:
            query = query.where(TimeEntry.entry_date <= date_to)

        query = query.order_by(TimeEntry.entry_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_stats(  # pylint: disable=too-many-locals
        self,
        condominium_id: str = None,
        employee_id: str = None,
        date_from: date = None,
        date_to: date = None,
    ) -> dict:
        """Calcula estatísticas de registros.

        Args:
            condominium_id: ID do condomínio
            employee_id: ID do funcionário
            date_from: Data inicial
            date_to: Data final

        Returns:
            Estatísticas
        """
        base_where = [TimeEntry.is_deleted.is_(False)]

        if condominium_id:
            base_where.append(TimeEntry.condominium_id == condominium_id)
        if employee_id:
            base_where.append(TimeEntry.employee_id == employee_id)
        if date_from:
            base_where.append(TimeEntry.entry_date >= date_from)
        if date_to:
            base_where.append(TimeEntry.entry_date <= date_to)

        # Total
        total_result = await self.db.execute(select(func.count()).where(*base_where))
        total = total_result.scalar() or 0

        # Por tipo
        type_result = await self.db.execute(
            select(TimeEntry.entry_type, func.count()).where(*base_where).group_by(TimeEntry.entry_type)
        )
        by_type = {row[0].value: row[1] for row in type_result.all()}

        # Por status
        status_result = await self.db.execute(
            select(TimeEntry.status, func.count()).where(*base_where).group_by(TimeEntry.status)
        )
        by_status = {row[0].value: row[1] for row in status_result.all()}

        # Anomalias
        anomaly_result = await self.db.execute(
            select(func.count()).where(
                *base_where,
                TimeEntry.anomaly_type != AnomalyType.SEM_ANOMALIA,
            )
        )
        anomaly_count = anomaly_result.scalar() or 0

        # Anomalias por tipo
        anomaly_type_result = await self.db.execute(
            select(TimeEntry.anomaly_type, func.count())
            .where(
                *base_where,
                TimeEntry.anomaly_type != AnomalyType.SEM_ANOMALIA,
            )
            .group_by(TimeEntry.anomaly_type)
        )
        by_anomaly = {row[0].value: row[1] for row in anomaly_type_result.all()}

        # Pendentes aprovação
        pending_result = await self.db.execute(
            select(func.count()).where(
                *base_where,
                TimeEntry.requires_approval.is_(True),
                TimeEntry.status == EntryStatus.PENDENTE,
            )
        )
        pending_count = pending_result.scalar() or 0

        # Manuais
        manual_result = await self.db.execute(
            select(func.count()).where(
                *base_where,
                TimeEntry.is_manual_entry.is_(True),
            )
        )
        manual_count = manual_result.scalar() or 0

        # Atrasos
        late_result = await self.db.execute(
            select(func.count()).where(
                *base_where,
                TimeEntry.is_late.is_(True),
            )
        )
        late_count = late_result.scalar() or 0

        return {
            "total_entries": total,
            "entries_by_type": by_type,
            "entries_by_status": by_status,
            "anomaly_count": anomaly_count,
            "anomaly_by_type": by_anomaly,
            "pending_approval_count": pending_count,
            "manual_entries_count": manual_count,
            "late_count": late_count,
        }

    async def check_duplicate(  # pylint: disable=unused-argument
        self,
        employee_id: str,
        entry_date: date,
        entry_type: EntryType,
        tolerance_minutes: int = 5,
    ) -> TimeEntry | None:
        """Verifica se existe registro duplicado.

        Args:
            employee_id: ID do funcionário
            entry_date: Data
            entry_type: Tipo de registro
            tolerance_minutes: Tolerância em minutos (reservado para uso futuro)

        Returns:
            Registro duplicado ou None
        """
        # Busca registros do mesmo tipo no mesmo dia
        entries = await self.get_by_employee_date(employee_id, entry_date)

        for entry in entries:
            if entry.entry_type == entry_type:
                return entry

        return None
