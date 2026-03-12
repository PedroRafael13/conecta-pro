"""
Serviço de Controle de Ponto — Departamento Pessoal.

Re-exporta funcionalidades do módulo hr/time_tracking e adiciona
método para registro de ponto a partir de dados operacionais (turnos).
"""

import contextlib
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Re-export do serviço existente
try:
    from modules.hr.time_tracking.services import TimeTrackingService as HRTimeTrackingService
except ImportError:
    HRTimeTrackingService = None  # type: ignore[assignment, misc]

try:
    from modules.hr.time_tracking.models import TimeEntry
except ImportError:
    TimeEntry = None  # type: ignore[assignment, misc]


class TimeTrackingService:
    """Serviço de Controle de Ponto — visão DP."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._hr_service = None
        if HRTimeTrackingService:
            with contextlib.suppress(Exception):
                self._hr_service = HRTimeTrackingService(db)

    async def register_from_operations(
        self,
        employee_id: str | UUID,
        shift_start: datetime,
        shift_end: datetime,
        location_id: str | UUID | None = None,
        notes: str | None = None,
    ) -> dict:
        """Registra ponto a partir de dados de turno operacional.

        Converte informações de turno (escala) em registros de ponto
        no sistema de time tracking.

        Args:
            employee_id: ID do funcionário.
            shift_start: Início do turno.
            shift_end: Fim do turno.
            location_id: ID do local de trabalho.
            notes: Observações adicionais.

        Returns:
            Dicionário com resultado do registro.
        """
        if not TimeEntry:
            logger.warning("Módulo time_tracking não disponível")
            return {
                "status": "unavailable",
                "message": "Módulo de ponto não disponível",
            }

        from uuid import uuid4

        entry = TimeEntry(
            id=uuid4(),
            employee_id=str(employee_id),
            clock_in=shift_start,
            clock_out=shift_end,
            source="operations",
            location_id=str(location_id) if location_id else None,
            notes=notes,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)

        duration_hours = (shift_end - shift_start).total_seconds() / 3600

        logger.info(
            "Ponto registrado via operações: employee=%s, duração=%.1fh",
            employee_id,
            duration_hours,
        )
        return {
            "entry_id": str(entry.id),
            "employee_id": str(employee_id),
            "clock_in": shift_start.isoformat(),
            "clock_out": shift_end.isoformat(),
            "duration_hours": round(duration_hours, 2),
            "source": "operations",
            "status": "registered",
        }

    async def get_entries(
        self,
        employee_id: str | UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list:
        """Busca registros de ponto de um funcionário.

        Args:
            employee_id: ID do funcionário.
            start_date: Data inicial do filtro.
            end_date: Data final do filtro.

        Returns:
            Lista de registros de ponto.
        """
        if not TimeEntry:
            return []

        from sqlalchemy import select

        query = select(TimeEntry).where(TimeEntry.employee_id == str(employee_id))
        if start_date:
            query = query.where(TimeEntry.clock_in >= start_date)
        if end_date:
            query = query.where(TimeEntry.clock_in <= end_date)

        query = query.order_by(TimeEntry.clock_in.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
