"""
My Payslips Controller — Consulta de contracheques do funcionario.

Endpoints:
- GET /portal/my-payslips
- GET /portal/my-payslips/{month}/{year}
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.people_management.employee_portal.schemas.payslip import MyPayslipResponse
from modules.people_management.employee_portal.services.document_view_service import (
    DocumentViewService,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portal - Contracheques"])


@router.get(
    "/my-payslips",
    response_model=list[MyPayslipResponse],
    summary="Meus contracheques",
    description="Retorna lista de contracheques do funcionario para o ano especificado.",
)
async def get_my_payslips(
    year: int = Query(default=None, ge=2020, le=2030, description="Ano de referencia"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna contracheques do funcionario para o ano.

    Args:
        year: Ano de referencia (default: ano atual).
        db: Sessao do banco de dados.

    Returns:
        Lista de MyPayslipResponse com dados dos contracheques.
    """
    # TODO: Extrair employee_id do token JWT do portal
    target_year = year or datetime.utcnow().year
    service = DocumentViewService(db)
    payslips = await service.get_my_payslips(
        employee_id=None,  # type: ignore[arg-type]
        year=target_year,
    )
    return [MyPayslipResponse(**p) for p in payslips]


@router.get(
    "/my-payslips/{month}/{year}",
    response_model=MyPayslipResponse,
    summary="Contracheque especifico",
    description="Retorna o contracheque de um mes/ano especifico.",
)
async def get_payslip_by_month(
    month: int = Path(..., ge=1, le=12, description="Mes (1-12)"),
    year: int = Path(..., ge=2020, le=2030, description="Ano"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna contracheque de um mes/ano especifico.

    Args:
        month: Mes de referencia.
        year: Ano de referencia.
        db: Sessao do banco de dados.

    Returns:
        MyPayslipResponse do mes especificado.

    Raises:
        HTTPException: 404 se contracheque nao encontrado.
    """
    # TODO: Extrair employee_id do token JWT do portal
    service = DocumentViewService(db)
    payslips = await service.get_my_payslips(
        employee_id=None,  # type: ignore[arg-type]
        year=year,
    )

    for p in payslips:
        if p.get("month") == month:
            return MyPayslipResponse(**p)

    raise HTTPException(
        status_code=http_status.HTTP_404_NOT_FOUND,
        detail=f"Contracheque de {month:02d}/{year} nao encontrado.",
    )
