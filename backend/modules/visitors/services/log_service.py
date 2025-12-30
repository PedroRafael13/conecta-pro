"""Service para VisitorLog."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.repositories.authorization_repository import AuthorizationRepository
from modules.visitors.repositories.log_repository import LogRepository
from modules.visitors.repositories.visitor_repository import VisitorRepository
from modules.visitors.schemas.log import (
    LogDeny,
    LogEntry,
    LogExit,
    LogFilter,
    LogListResponse,
    LogResponse,
    LogStats,
    LogTimeline,
    VisitorInside,
)

logger = logging.getLogger(__name__)


class LogService:
    """Service para operações de VisitorLog."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = LogRepository(session)
        self.visitor_repo = VisitorRepository(session)
        self.auth_repo = AuthorizationRepository(session)

    async def register_entry(self, data: LogEntry) -> LogResponse:
        """Registra entrada de visitante."""
        # Validar autorização se fornecida
        if data.authorization_id:
            auth = await self.auth_repo.get_by_id(data.authorization_id)
            if auth and auth.can_use:
                await self.auth_repo.use(data.authorization_id)

        log = await self.repository.create_entry(data)

        # Registrar visita no visitante
        await self.visitor_repo.register_visit(data.visitor_id)

        await self.session.commit()
        await self.session.refresh(log)
        return LogResponse.model_validate(log)

    async def register_exit(self, data: LogExit) -> Optional[LogResponse]:
        """Registra saída de visitante."""
        log = await self.repository.create_exit(data)
        if log:
            # Atualizar duração média no visitante
            if log.duration_minutes:
                visitor = await self.visitor_repo.get_by_id(data.visitor_id)
                if visitor:
                    visitor.register_visit(log.duration_minutes)

            await self.session.commit()
            return LogResponse.model_validate(log)
        return None

    async def register_denial(self, data: LogDeny) -> LogResponse:
        """Registra negativa de acesso."""
        log = await self.repository.create_denial(data)
        await self.session.commit()
        await self.session.refresh(log)
        return LogResponse.model_validate(log)

    async def get_by_id(self, log_id: str | UUID) -> Optional[LogResponse]:
        """Busca log por ID."""
        log = await self.repository.get_by_id(log_id)
        if not log:
            return None
        return LogResponse.model_validate(log)

    async def list(
        self,
        filters: Optional[LogFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "timestamp",
        order_desc: bool = True,
    ) -> LogListResponse:
        """Lista logs com filtros."""
        skip = (page - 1) * page_size
        logs, total = await self.repository.list_with_filters(
            filters, skip, page_size, order_by, order_desc
        )

        items = [LogResponse.model_validate(log) for log in logs]
        pages = (total + page_size - 1) // page_size

        return LogListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_visitor_timeline(
        self, visitor_id: str | UUID, limit: int = 50
    ) -> LogTimeline:
        """Retorna timeline de logs de um visitante."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        visitor = await self.visitor_repo.get_by_id(visitor_id)
        if not visitor:
            return LogTimeline(
                visitor_id=visitor_id,
                visitor_name="Desconhecido",
                logs=[],
                total_visits=0,
                total_duration_minutes=0,
                avg_duration_minutes=0,
            )

        logs = await self.repository.get_by_visitor(visitor_id, limit=limit)
        log_responses = [LogResponse.model_validate(log) for log in logs]

        # Calcular métricas
        durations = [log.duration_minutes for log in logs if log.duration_minutes]
        total_duration = sum(durations)
        avg_duration = total_duration / len(durations) if durations else 0

        first_visit = logs[-1].timestamp if logs else None
        last_visit = logs[0].timestamp if logs else None
        denied_count = sum(1 for log in logs if log.denied)

        return LogTimeline(
            visitor_id=visitor_id,
            visitor_name=visitor.name,
            logs=log_responses,
            total_visits=visitor.visit_count,
            total_duration_minutes=total_duration,
            avg_duration_minutes=round(avg_duration, 1),
            first_visit_at=first_visit,
            last_visit_at=last_visit,
            denied_count=denied_count,
        )

    async def get_inside(
        self, condominium_id: str, page: int = 1, page_size: int = 100
    ) -> list[VisitorInside]:
        """Lista visitantes atualmente dentro."""
        skip = (page - 1) * page_size
        logs = await self.repository.get_inside(condominium_id, skip, page_size)

        result = []
        for log in logs:
            visitor = await self.visitor_repo.get_by_id(log.visitor_id)
            if visitor:
                duration = 0
                if log.entry_at:
                    duration = int(
                        (datetime.utcnow() - log.entry_at).total_seconds() / 60
                    )

                result.append(
                    VisitorInside(
                        visitor_id=visitor.id,
                        visitor_name=visitor.name,
                        visitor_photo=visitor.photo_url,
                        visitor_type=visitor.visitor_type.value,
                        entry_at=log.entry_at,
                        duration_minutes=duration,
                        unit_number=log.unit_number,
                        resident_name=log.resident_name,
                        purpose=log.purpose,
                        has_vehicle=log.has_vehicle,
                        vehicle_plate=log.vehicle_plate,
                        companions_count=log.companions_count,
                    )
                )

        return result

    async def count_inside(self, condominium_id: str) -> int:
        """Conta visitantes dentro."""
        return await self.repository.count_inside(condominium_id)

    async def get_denied(
        self, condominium_id: str = None, page: int = 1, page_size: int = 50
    ) -> LogListResponse:
        """Lista acessos negados."""
        skip = (page - 1) * page_size
        logs = await self.repository.get_denied(condominium_id, skip, page_size)
        items = [LogResponse.model_validate(log) for log in logs]
        return LogListResponse(
            items=items, total=len(items), page=page, page_size=page_size
        )

    async def get_by_date_range(
        self,
        condominium_id: str,
        date_from: datetime,
        date_until: datetime,
    ) -> LogListResponse:
        """Lista logs por período."""
        logs = await self.repository.get_by_date_range(
            condominium_id, date_from, date_until
        )
        items = [LogResponse.model_validate(log) for log in logs]
        return LogListResponse(items=items, total=len(items))

    async def get_stats(
        self, condominium_id: str = None, date_from: datetime = None
    ) -> LogStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id, date_from)
        return LogStats(**stats)

    async def notify_resident(self, log_id: str | UUID) -> Optional[LogResponse]:
        """Marca morador como notificado."""
        log = await self.repository.notify_resident(log_id)
        if not log:
            return None
        await self.session.commit()
        return LogResponse.model_validate(log)

    async def is_visitor_inside(
        self, visitor_id: str | UUID, condominium_id: str
    ) -> bool:
        """Verifica se visitante está dentro."""
        entry = await self.repository.get_current_entry(visitor_id, condominium_id)
        return entry is not None
