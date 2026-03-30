"""
Controller de Férias — Departamento Pessoal.

Re-exporta endpoints de férias do operacional e adiciona endpoints DP:
cálculo de saldo, detalhes e aprovação.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.operacional.vacations.schemas import VacationRequestResponse
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


@router.get("")
async def list_vacations(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista solicitações de férias."""
    try:
        from sqlalchemy import func
        from sqlalchemy import select as sa_select

        from modules.operacional.vacations.models import VacationRequest

        count_q = sa_select(func.count()).select_from(VacationRequest)
        total = (await db.execute(count_q)).scalar() or 0
        query = (
            sa_select(VacationRequest)
            .order_by(VacationRequest.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
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


@router.get("/employee/{employee_id}", response_model=None)
async def list_vacations_by_employee(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista solicitações de férias de um funcionário específico."""
    service = VacationService(db)
    result = await service.list_by_employee(employee_id, page=page, page_size=page_size)
    # Serialize items using the response schema
    serialized_items = []
    for item in result["items"]:
        try:
            serialized_items.append(VacationRequestResponse.model_validate(item).model_dump())
        except Exception:
            serialized_items.append(
                {
                    "id": str(item.id),
                    "employee_id": str(item.employee_id),
                    "employee_name": item.employee_name,
                    "type": item.type,
                    "status": item.status,
                    "start_date": str(item.start_date) if item.start_date else None,
                    "end_date": str(item.end_date) if item.end_date else None,
                    "days": item.days,
                    "reason": item.reason,
                    "notes": item.notes,
                    "approved_by": str(item.approved_by) if item.approved_by else None,
                    "approved_at": item.approved_at.isoformat() if item.approved_at else None,
                    "rejected_reason": item.rejected_reason,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                }
            )
    return {
        "items": serialized_items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    }


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


@router.get("/{vacation_id}", response_model=VacationRequestResponse)
async def get_vacation(
    vacation_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de uma solicitação de férias."""
    service = VacationService(db)
    vacation = await service.get_by_id(vacation_id)
    if not vacation:
        raise HTTPException(status_code=404, detail="Solicitação de férias não encontrada")
    return vacation


@router.post("/sync-solides")
async def sync_ferias_solides(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    periodo_inicio: str | None = Query(None, description="YYYY-MM-DD"),
    periodo_fim: str | None = Query(None, description="YYYY-MM-DD"),
) -> Any:
    """Sincroniza férias do Sólides Tangerino para o módulo de férias do DP."""
    service = VacationService(db)
    try:
        result = await service.sync_vacations_from_solides(
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
        )
        if result.get("success"):
            await db.commit()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
