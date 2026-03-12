"""
My Schedules Controller — Consulta de escalas do funcionario.

Endpoints:
- GET /portal/my-schedules
- GET /portal/my-schedules/current-month
- GET /portal/my-schedules/next-shift
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.people_management.employee_portal.schemas.schedule import (
    MyScheduleResponse,
    MyShiftResponse,
)
from modules.people_management.employee_portal.services.document_view_service import (
    DocumentViewService,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portal - Escalas"])


@router.get(
    "/my-schedules",
    response_model=MyScheduleResponse,
    summary="Minha escala",
    description="Retorna a escala do funcionario para o mes/ano especificado.",
)
async def get_my_schedules(
    month: int = Query(default=None, ge=1, le=12, description="Mes (1-12)"),
    year: int = Query(default=None, ge=2020, le=2030, description="Ano"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna escala do funcionario para o periodo.

    Args:
        month: Mes de referencia (default: mes atual).
        year: Ano de referencia (default: ano atual).
        db: Sessao do banco de dados.

    Returns:
        MyScheduleResponse com turnos e total de horas.
    """
    # TODO: Extrair employee_id do token JWT do portal
    service = DocumentViewService(db)
    schedule = await service.get_my_schedules(
        employee_id=None,  # type: ignore[arg-type]
        month=month,
        year=year,
    )
    return MyScheduleResponse(**schedule)


@router.get(
    "/my-schedules/current-month",
    response_model=MyScheduleResponse,
    summary="Escala do mes atual",
    description="Atalho para retornar a escala do mes corrente.",
)
async def get_current_month_schedule(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna escala do mes atual.

    Args:
        db: Sessao do banco de dados.

    Returns:
        MyScheduleResponse do mes corrente.
    """
    now = datetime.utcnow()
    service = DocumentViewService(db)
    schedule = await service.get_my_schedules(
        employee_id=None,  # type: ignore[arg-type]
        month=now.month,
        year=now.year,
    )
    return MyScheduleResponse(**schedule)


@router.get(
    "/my-schedules/next-shift",
    response_model=MyShiftResponse,
    summary="Proximo turno",
    description="Retorna dados do proximo turno agendado do funcionario.",
)
async def get_next_shift(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna o proximo turno agendado.

    Args:
        db: Sessao do banco de dados.

    Returns:
        MyShiftResponse com dados do proximo turno.

    Raises:
        HTTPException: 404 se nenhum turno futuro encontrado.
    """
    # TODO: Implementar busca do proximo turno com employee_id do JWT
    raise HTTPException(
        status_code=http_status.HTTP_404_NOT_FOUND,
        detail="Nenhum turno futuro encontrado.",
    )
