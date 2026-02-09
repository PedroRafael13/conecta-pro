"""
Controller (endpoints) para Relatorios Operacionais.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.operacional.permissions import Permission, require_operacional_permission
from modules.operacional.repositories.reports_repository import ReportsRepository
from modules.operacional.schemas.reports import (
    CostsReportResponse,
    CoverageReportResponse,
    HoursReportResponse,
)

router = APIRouter(prefix="/reports", tags=["Operations - Reports"])


def _default_dates() -> tuple[date, date]:
    today = date.today()
    start = date(today.year, today.month, 1)
    return start, today


@router.get(
    "/coverage",
    response_model=CoverageReportResponse,
    dependencies=[require_operacional_permission(Permission.REPORTS_VIEW)],
)
async def coverage_report(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    post_id: str | None = Query(None),
) -> CoverageReportResponse:
    """Relatorio de cobertura (postos x alocacoes)."""
    default_start, default_end = _default_dates()
    start = start_date or default_start
    end = end_date or default_end

    repo = ReportsRepository(db)
    items: list[dict[str, Any]] = await repo.get_coverage(start, end, post_id=post_id)

    total_allocations = sum(item["total_allocations"] for item in items)
    active_allocations = sum(item["active_allocations"] for item in items)
    coverage_rate = (active_allocations / total_allocations * 100) if total_allocations else 0.0

    logger.info(
        "Relatorio cobertura gerado: %s a %s (postos=%s)",
        start,
        end,
        len(items),
    )

    return CoverageReportResponse(
        start_date=start,
        end_date=end,
        total_posts=len(items),
        total_allocations=total_allocations,
        active_allocations=active_allocations,
        coverage_rate=round(coverage_rate, 2),
        items=items,
    )


@router.get(
    "/hours",
    response_model=HoursReportResponse,
    dependencies=[require_operacional_permission(Permission.REPORTS_VIEW)],
)
async def hours_report(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    employee_id: str | None = Query(None),
) -> HoursReportResponse:
    """Relatorio de horas trabalhadas."""
    default_start, default_end = _default_dates()
    start = start_date or default_start
    end = end_date or default_end

    repo = ReportsRepository(db)
    items: list[dict[str, Any]] = await repo.get_hours(start, end, employee_id=employee_id)

    total_hours = sum(item["total_hours"] for item in items)
    total_overtime = sum(item["overtime_hours"] for item in items)

    logger.info(
        "Relatorio horas gerado: %s a %s (funcionarios=%s)",
        start,
        end,
        len(items),
    )

    return HoursReportResponse(
        start_date=start,
        end_date=end,
        total_employees=len(items),
        total_hours=round(total_hours, 2),
        total_overtime=round(total_overtime, 2),
        items=items,
    )


@router.get(
    "/costs",
    response_model=CostsReportResponse,
    dependencies=[require_operacional_permission(Permission.REPORTS_VIEW)],
)
async def costs_report(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    post_id: str | None = Query(None),
) -> CostsReportResponse:
    """Relatorio de custos estimados por posto."""
    default_start, default_end = _default_dates()
    start = start_date or default_start
    end = end_date or default_end

    repo = ReportsRepository(db)
    items: list[dict[str, Any]] = await repo.get_costs(start, end, post_id=post_id)

    total_cost = sum(item["total_cost"] for item in items)

    logger.info(
        "Relatorio custos gerado: %s a %s (postos=%s)",
        start,
        end,
        len(items),
    )

    return CostsReportResponse(
        start_date=start,
        end_date=end,
        total_posts=len(items),
        total_cost=round(total_cost, 2),
        items=items,
    )
