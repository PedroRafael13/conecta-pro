"""Repository para REPEvent."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.rep_integration.models import (
    EventStatus,
    REPEvent,
)
from modules.hr.rep_integration.schemas import (
    REPEventCreate,
    REPEventFilter,
    REPEventUpdate,
)


class REPEventRepository:
    """Repository para operações de REPEvent."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: REPEventCreate) -> REPEvent:
        """Cria novo evento."""
        event = REPEvent(
            device_id=data.device_id,
            condominio_id=data.condominio_id,
            nsr=data.nsr,
            event_datetime=data.event_datetime,
            event_date=data.event_datetime.date(),
            event_time=data.event_datetime.time(),
            event_type=data.event_type,
            employee_id=data.employee_id,
            pis_number=data.pis_number,
            employee_code=data.employee_code,
            employee_name=data.employee_name,
            identification_method=data.identification_method,
            identification_score=data.identification_score,
            biometric_hash=data.biometric_hash,
            finger_index=data.finger_index,
            card_number=data.card_number,
            card_facility_code=data.card_facility_code,
            photo_captured=data.photo_captured,
            photo_path=data.photo_path,
            latitude=data.latitude,
            longitude=data.longitude,
            location_accuracy=data.location_accuracy,
            raw_data=data.raw_data,
            sync_id=data.sync_id,
            status=EventStatus.RECEIVED.value,
        )

        # Gera linha AFD
        event.afd_line = event.generate_afd_line()

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def create_bulk(
        self,
        events: list[REPEventCreate],
    ) -> tuple[int, int, int]:
        """Cria eventos em lote.

        Returns:
            Tuple: (criados, duplicados, erros)
        """
        created = 0
        duplicates = 0
        errors = 0

        for event_data in events:
            # Verifica duplicado
            existing = await self.get_by_device_nsr(
                event_data.device_id,
                event_data.nsr,
            )
            if existing:
                duplicates += 1
                continue

            try:
                await self.create(event_data)
                created += 1
            except Exception:  # pylint: disable=broad-exception-caught
                errors += 1

        return created, duplicates, errors

    async def get_by_id(self, event_id: UUID) -> REPEvent | None:
        """Busca evento por ID."""
        result = await self.db.execute(select(REPEvent).where(REPEvent.id == event_id))
        return result.scalar_one_or_none()

    async def get_by_device_nsr(
        self,
        device_id: UUID,
        nsr: int,
    ) -> REPEvent | None:
        """Busca evento por dispositivo e NSR."""
        result = await self.db.execute(
            select(REPEvent).where(
                REPEvent.device_id == device_id,
                REPEvent.nsr == nsr,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        event_id: UUID,
        data: REPEventUpdate,
    ) -> REPEvent | None:
        """Atualiza evento."""
        event = await self.get_by_id(event_id)
        if not event:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def list_events(  # pylint: disable=too-many-branches
        self,
        filters: REPEventFilter,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[REPEvent], int]:
        """Lista eventos com filtros e paginação."""
        query = select(REPEvent)

        # Aplicar filtros
        if filters.device_id:
            query = query.where(REPEvent.device_id == filters.device_id)
        if filters.condominio_id:
            query = query.where(REPEvent.condominio_id == filters.condominio_id)
        if filters.employee_id:
            query = query.where(REPEvent.employee_id == filters.employee_id)
        if filters.pis_number:
            query = query.where(REPEvent.pis_number == filters.pis_number)
        if filters.event_type:
            query = query.where(REPEvent.event_type == filters.event_type)
        if filters.status:
            query = query.where(REPEvent.status == filters.status)
        if filters.identification_method:
            query = query.where(REPEvent.identification_method == filters.identification_method)
        if filters.date_from:
            query = query.where(REPEvent.event_date >= filters.date_from)
        if filters.date_to:
            query = query.where(REPEvent.event_date <= filters.date_to)
        if filters.is_valid is not None:
            query = query.where(REPEvent.is_valid == filters.is_valid)
        if filters.has_employee is not None:
            if filters.has_employee:
                query = query.where(REPEvent.employee_id.isnot(None))
            else:
                query = query.where(REPEvent.employee_id.is_(None))
        if filters.nsr_from:
            query = query.where(REPEvent.nsr >= filters.nsr_from)
        if filters.nsr_to:
            query = query.where(REPEvent.nsr <= filters.nsr_to)

        # Contagem total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(REPEvent.event_datetime.desc())

        result = await self.db.execute(query)
        events = result.scalars().all()

        return list(events), total

    async def get_pending_processing(
        self,
        device_id: UUID = None,
        limit: int = 100,
    ) -> list[REPEvent]:
        """Retorna eventos pendentes de processamento."""
        query = select(REPEvent).where(
            REPEvent.status.in_(
                [
                    EventStatus.RECEIVED.value,
                    EventStatus.VALIDATED.value,
                ]
            )
        )

        if device_id:
            query = query.where(REPEvent.device_id == device_id)

        query = query.order_by(REPEvent.event_datetime).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unidentified_events(
        self,
        device_id: UUID = None,
        date_from: date = None,
        date_to: date = None,
        limit: int = 100,
    ) -> list[REPEvent]:
        """Retorna eventos sem funcionário identificado."""
        query = select(REPEvent).where(
            REPEvent.employee_id.is_(None),
            REPEvent.status != EventStatus.REJECTED.value,
        )

        if device_id:
            query = query.where(REPEvent.device_id == device_id)
        if date_from:
            query = query.where(REPEvent.event_date >= date_from)
        if date_to:
            query = query.where(REPEvent.event_date <= date_to)

        query = query.order_by(REPEvent.event_datetime.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_processed(
        self,
        event_id: UUID,
        time_entry_id: UUID,
    ) -> None:
        """Marca evento como processado."""
        await self.db.execute(
            update(REPEvent)
            .where(REPEvent.id == event_id)
            .values(
                status=EventStatus.PROCESSED.value,
                processed_at=datetime.utcnow(),
                time_entry_id=time_entry_id,
            )
        )
        await self.db.commit()

    async def mark_as_error(
        self,
        event_id: UUID,
        error_message: str,
        error_code: str = None,
    ) -> None:
        """Marca evento como erro."""
        event = await self.get_by_id(event_id)
        if event:
            event.status = EventStatus.ERROR.value
            event.error_message = error_message
            event.error_code = error_code
            event.retry_count += 1
            await self.db.commit()

    async def mark_as_duplicate(self, event_id: UUID) -> None:
        """Marca evento como duplicado."""
        await self.db.execute(
            update(REPEvent).where(REPEvent.id == event_id).values(status=EventStatus.DUPLICATE.value)
        )
        await self.db.commit()

    async def get_last_nsr(self, device_id: UUID) -> int | None:
        """Retorna último NSR do dispositivo."""
        result = await self.db.execute(select(func.max(REPEvent.nsr)).where(REPEvent.device_id == device_id))
        return result.scalar()

    async def get_events_by_date_range(
        self,
        device_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[REPEvent]:
        """Retorna eventos de um período."""
        result = await self.db.execute(
            select(REPEvent)
            .where(
                REPEvent.device_id == device_id,
                REPEvent.event_date >= start_date,
                REPEvent.event_date <= end_date,
            )
            .order_by(REPEvent.nsr)
        )
        return list(result.scalars().all())

    async def get_statistics(
        self,
        device_id: UUID = None,
        condominio_id: UUID = None,
        date_from: date = None,
        date_to: date = None,
    ) -> dict:
        """Retorna estatísticas de eventos."""
        base_where = []
        if device_id:
            base_where.append(REPEvent.device_id == device_id)
        if condominio_id:
            base_where.append(REPEvent.condominio_id == condominio_id)
        if date_from:
            base_where.append(REPEvent.event_date >= date_from)
        if date_to:
            base_where.append(REPEvent.event_date <= date_to)

        # Total
        total_result = await self.db.execute(select(func.count()).where(*base_where))
        total = total_result.scalar() or 0

        # Por tipo
        type_result = await self.db.execute(
            select(REPEvent.event_type, func.count(REPEvent.id)).where(*base_where).group_by(REPEvent.event_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Por status
        status_result = await self.db.execute(
            select(REPEvent.status, func.count(REPEvent.id)).where(*base_where).group_by(REPEvent.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Por método
        method_result = await self.db.execute(
            select(REPEvent.identification_method, func.count(REPEvent.id))
            .where(*base_where)
            .group_by(REPEvent.identification_method)
        )
        by_method = {row[0]: row[1] for row in method_result.all()}

        return {
            "total_events": total,
            "events_by_type": by_type,
            "events_by_status": by_status,
            "events_by_method": by_method,
            "pending_processing": by_status.get(EventStatus.RECEIVED.value, 0),
            "errors_count": by_status.get(EventStatus.ERROR.value, 0),
            "duplicates_count": by_status.get(EventStatus.DUPLICATE.value, 0),
        }
