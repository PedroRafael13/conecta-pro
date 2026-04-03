"""
Controller de Controle de Ponto — Departamento Pessoal.

Re-exporta endpoints de ponto do módulo HR e adiciona endpoint
para registro via operações.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.services.time_tracking_service import (
    TimeTrackingService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/time-tracking", tags=["DP - Ponto"])

# Re-export do router existente de time tracking
# NOTA: o router HR tem prefix="/time-tracking" → resulta em /hr/time-tracking/time-tracking/
# Mantemos para compatibilidade, e adicionamos endpoints diretos
try:
    from modules.hr.time_tracking.controllers import router as _tt_router

    router.include_router(_tt_router)
except ImportError:
    logger.info("Router de time tracking não disponível para re-export")


class OperationsTimeEntry(BaseModel):
    """Schema para registro de ponto via operações."""

    employee_id: str
    shift_start: datetime
    shift_end: datetime
    location_id: str | None = None
    notes: str | None = None


@router.post("/from-operations", summary="Registrar Ponto de Turno Operacional", status_code=201)
async def register_from_operations(
    data: OperationsTimeEntry,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Registra ponto a partir de dados de turno operacional."""
    service = TimeTrackingService(db)
    result = await service.register_from_operations(
        employee_id=data.employee_id,
        shift_start=data.shift_start,
        shift_end=data.shift_end,
        location_id=data.location_id,
        notes=data.notes,
    )
    await db.commit()
    return result


@router.get("/employee/{employee_id}/entries", summary="Registros de Ponto do Funcionário")
async def get_employee_entries(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
) -> Any:
    """Lista registros de ponto de um funcionário."""
    service = TimeTrackingService(db)
    entries = await service.get_entries(employee_id, start_date=start_date, end_date=end_date)
    return {"items": entries, "total": len(entries)}
