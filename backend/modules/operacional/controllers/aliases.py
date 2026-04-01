"""
Alias routes para compatibilidade frontend PT-BR.

Implementam endpoints espelhados nos paths PT-BR
que executam as mesmas queries dos endpoints EN.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.operacional.models.scale_template import ScaleTemplate
from modules.operacional.models.time_bank import TimeBank
from modules.operacional.occurrences.models import Occurrence
from modules.operacional.vacations.models import VacationRequest

banco_horas_alias = APIRouter(
    prefix="/banco-horas",
    tags=["Operacional - Banco Horas"],
)
ocorrencias_alias = APIRouter(
    prefix="/ocorrencias",
    tags=["Operacional - Ocorrencias"],
)
ferias_alias = APIRouter(
    prefix="/ferias",
    tags=["Operacional - Ferias"],
)
scale_templates_alias = APIRouter(
    prefix="/scale-templates",
    tags=["Operacional - Scale Templates"],
)


@banco_horas_alias.get("/")
async def list_banco_horas(
    _user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """Lista banco de horas (alias PT-BR de /time-bank)."""
    offset = (page - 1) * page_size
    base = TimeBank.is_active.is_(True)
    total = (await db.execute(select(func.count(TimeBank.id)).where(base))).scalar() or 0
    query = select(TimeBank).where(base).order_by(TimeBank.created_at.desc()).offset(offset).limit(page_size)
    items = (await db.execute(query)).scalars().all()
    return {
        "items": [
            {
                "id": str(e.id),
                "employee_id": str(e.employee_id),
                "entry_type": e.entry_type,
                "hours": float(e.hours),
                "status": e.status,
                "created_at": (e.created_at.isoformat() if e.created_at else None),
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@ocorrencias_alias.get("/")
async def list_ocorrencias(
    _user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
) -> dict[str, Any]:
    """Lista ocorrencias (alias PT-BR de /occurrences)."""
    offset = (page - 1) * page_size
    query = select(Occurrence)
    count_q = select(func.count(Occurrence.id))

    if status_filter:
        query = query.where(Occurrence.status == status_filter)
        count_q = count_q.where(Occurrence.status == status_filter)

    total = (await db.execute(count_q)).scalar() or 0
    ordered = query.order_by(Occurrence.created_at.desc()).offset(offset).limit(page_size)
    items = (await db.execute(ordered)).scalars().all()
    return {
        "items": [
            {
                "id": str(i.id),
                "type": getattr(i, "type", None),
                "status": i.status,
                "severity": getattr(i, "severity", None),
                "created_at": (i.created_at.isoformat() if i.created_at else None),
            }
            for i in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@ocorrencias_alias.get("/stats")
async def ocorrencias_stats(
    _user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Estatisticas de ocorrencias (alias PT-BR)."""
    total = (await db.execute(select(func.count(Occurrence.id)))).scalar() or 0
    abertas = (await db.execute(select(func.count(Occurrence.id)).where(Occurrence.status == "aberta"))).scalar() or 0
    return {
        "total": total,
        "abertas": abertas,
        "resolvidas": total - abertas,
    }


@ferias_alias.get("/")
async def list_ferias(
    _user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    status: str | None = Query(None),
    employee_id: str | None = Query(None),
) -> dict[str, Any]:
    """Lista ferias (alias PT-BR de /vacations)."""
    query = select(VacationRequest).where(VacationRequest.is_active)
    if status:
        query = query.where(VacationRequest.status == status)
    if employee_id:
        query = query.where(VacationRequest.employee_id == employee_id)
    query = query.order_by(VacationRequest.created_at.desc())
    items = list((await db.execute(query)).scalars().all())
    total = len(items)
    return {
        "items": [
            {
                "id": str(i.id),
                "employee_id": str(i.employee_id),
                "employee_name": i.employee_name,
                "type": i.type,
                "status": i.status,
                "start_date": (i.start_date.isoformat() if i.start_date else None),
                "end_date": (i.end_date.isoformat() if i.end_date else None),
                "days": i.days,
            }
            for i in items
        ],
        "total": total,
        "pendente": sum(1 for i in items if i.status == "pendente"),
        "aprovado": sum(1 for i in items if i.status == "aprovado"),
        "rejeitado": sum(1 for i in items if i.status == "rejeitado"),
    }


@scale_templates_alias.get("/")
async def list_scale_templates(
    _user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Lista templates de escala (alias PT-BR)."""
    query = select(ScaleTemplate).where(ScaleTemplate.is_active.is_(True)).order_by(ScaleTemplate.name)
    items = (await db.execute(query)).scalars().all()
    return {
        "items": [
            {
                "id": str(i.id),
                "name": i.name,
                "description": i.description,
                "template_data": i.template_data,
                "times_used": i.times_used,
            }
            for i in items
        ],
        "total": len(items),
    }
