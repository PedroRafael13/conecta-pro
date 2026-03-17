"""
Controller de Folha de Pagamento — Departamento Pessoal.

Re-exporta endpoints de folha do módulo HR e adiciona endpoints
para cálculo individual e fechamento mensal.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.services.payroll_service import PayrollService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payroll", tags=["DP - Folha de Pagamento"])

# Re-export do router existente de payroll
# IMPORTANTE: usar include_router (NÃO append) para preservar prefixos
try:
    from modules.hr.payroll_integration.controllers import router as _payroll_router

    router.include_router(_payroll_router)
except ImportError:
    logger.info("Router de payroll não disponível para re-export")


@router.get("/employee/{employee_id}/calculate")
async def calculate_employee_payroll(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12, description="Mês de referência"),
    year: int = Query(..., ge=2020, le=2030, description="Ano de referência"),
) -> Any:
    """Calcula a folha de pagamento de um funcionário."""
    service = PayrollService(db)
    try:
        return await service.calculate_employee_payroll(employee_id, month, year)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/close")
async def close_payroll(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12, description="Mês de referência"),
    year: int = Query(..., ge=2020, le=2030, description="Ano de referência"),
) -> Any:
    """Fecha a folha de pagamento mensal para todos os funcionários ativos."""
    service = PayrollService(db)
    result = await service.close_payroll(month, year)
    await db.commit()
    return result
