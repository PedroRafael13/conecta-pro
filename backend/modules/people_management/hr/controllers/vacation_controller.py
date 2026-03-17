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
# NOTA: o router ops tem prefix="/vacations" → resulta em /hr/vacations/vacations/
# Mantemos para compatibilidade, e adicionamos endpoint direto em /hr/vacations/
try:
    from modules.operacional.vacations.controller import router as _vacation_ops_router

    router.include_router(_vacation_ops_router)
except ImportError:
    logger.info("Router de férias operacional não disponível para re-export")


@router.get("/")
async def list_vacations(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
) -> Any:
    """Lista solicitações de férias."""
    try:
        from sqlalchemy import func
        from sqlalchemy import select as sa_select

        from modules.operacional.vacations.models import VacationRequest

        count_q = sa_select(func.count()).select_from(VacationRequest)
        total = (await db.execute(count_q)).scalar() or 0
        query = sa_select(VacationRequest).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "items": [{"id": str(v.id), "employee_id": str(v.employee_id), "status": v.status} for v in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    except Exception:
        return {"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 1}


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
