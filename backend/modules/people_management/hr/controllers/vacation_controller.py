"""
Controller de Férias — Departamento Pessoal.

Re-exporta endpoints de férias do operacional e adiciona endpoints DP:
cálculo de saldo e aprovação.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.services.vacation_service import VacationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vacations", tags=["DP - Férias"])

# Re-export do router existente de férias
try:
    from modules.operacional.vacations.controller import router as _vacation_ops_router

    for route in _vacation_ops_router.routes:
        router.routes.append(route)
except ImportError:
    logger.info("Router de férias operacional não disponível para re-export")


@router.get("/employee/{employee_id}/balance")
async def get_vacation_balance(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calcula o saldo de férias do funcionário."""
    service = VacationService(db)
    try:
        return await service.calculate_vacation_balance(employee_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{vacation_id}/approve")
async def approve_vacation(
    vacation_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Aprova uma solicitação de férias."""
    service = VacationService(db)
    try:
        result = await service.approve_vacation(vacation_id, approved_by_id=current_user.id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
