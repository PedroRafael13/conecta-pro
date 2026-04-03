"""
Controller de Afastamentos (Leaves) — Departamento Pessoal.

Endpoint de listagem de afastamentos/licenças médicas.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leaves", tags=["DP - Afastamentos"])


@router.get(
    "",
    summary="Listar Afastamentos",
    description="Retorna lista paginada de afastamentos e licenças médicas dos funcionários.",
)
async def list_leaves(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista afastamentos e licenças."""
    # Tenta buscar do módulo de justificativas (medical leaves)
    try:
        from sqlalchemy import func, select

        from modules.hr.time_tracking.models.time_justification import TimeJustification

        base_filter = TimeJustification.justification_type == "medical_leave"
        count_q = select(func.count()).select_from(TimeJustification).where(base_filter)
        total = (await db.execute(count_q)).scalar() or 0
        query = select(TimeJustification).where(base_filter).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        return {
            "items": [
                {
                    "id": str(getattr(j, "id", "")),
                    "employee_id": str(getattr(j, "employee_id", "")),
                    "type": getattr(j, "justification_type", "medical_leave"),
                    "status": getattr(j, "status", "pending"),
                }
                for j in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    except Exception:
        return {"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 1}
