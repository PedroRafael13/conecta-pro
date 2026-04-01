"""
Controller de Férias e Afastamentos.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser, get_current_active_user
from core.database import get_db
from modules.operacional.models.employee import Employee

from .models import VacationRequest
from .schemas import (
    VacationRequestCreate,
    VacationRequestListResponse,
    VacationRequestResponse,
    VacationRequestUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/vacations",
    tags=["Operacional - Férias e Afastamentos"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("", response_model=VacationRequestListResponse)
async def list_vacation_requests(
    current_user: CurrentActiveUser,
    status: str | None = Query(None),
    type_filter: str | None = Query(None, alias="type"),
    employee_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> VacationRequestListResponse:
    """Lista solicitações de férias e afastamentos."""
    try:
        q = select(VacationRequest).where(VacationRequest.is_active)

        if status:
            q = q.where(VacationRequest.status == status)
        if type_filter:
            q = q.where(VacationRequest.type == type_filter)
        if employee_id:
            q = q.where(VacationRequest.employee_id == employee_id)

        q = q.order_by(VacationRequest.created_at.desc())
        result = await db.execute(q)
        items = result.scalars().all()

        # Count by status
        total = len(items)
        pendente = sum(1 for i in items if i.status == "pendente")
        aprovado = sum(1 for i in items if i.status == "aprovado")
        rejeitado = sum(1 for i in items if i.status == "rejeitado")

        return VacationRequestListResponse(
            items=[VacationRequestResponse.model_validate(i) for i in items],
            total=total,
            pendente=pendente,
            aprovado=aprovado,
            rejeitado=rejeitado,
        )
    except (RuntimeError, ValueError, OSError) as e:
        logger.error("Erro ao listar férias: %s", e)
        return VacationRequestListResponse(items=[], total=0, pendente=0, aprovado=0, rejeitado=0)


@router.post("", response_model=VacationRequestResponse, status_code=201)
async def create_vacation_request(
    data: VacationRequestCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> VacationRequestResponse:
    """Cria nova solicitação de férias/afastamento."""
    # Calculate days
    delta = (data.end_date - data.start_date).days + 1
    days_str = f"{delta} dia{'s' if delta > 1 else ''}"

    # BUG-03 fix: auto-preencher employee_name quando não fornecido
    employee_name = data.employee_name
    if not employee_name:
        emp_result = await db.execute(select(Employee).where(Employee.id == data.employee_id))
        emp = emp_result.scalar_one_or_none()
        if emp:
            employee_name = emp.nome

    req = VacationRequest(
        employee_id=str(data.employee_id),
        employee_name=employee_name,
        type=data.type,
        status="pendente",
        start_date=data.start_date,
        end_date=data.end_date,
        days=days_str,
        reason=data.reason,
        notes=data.notes,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return VacationRequestResponse.model_validate(req)


@router.get("/{request_id}", response_model=VacationRequestResponse)
async def get_vacation_request(
    request_id: str, current_user: CurrentActiveUser, db: AsyncSession = Depends(get_db)
) -> VacationRequestResponse:
    """Busca uma solicitação pelo ID."""
    result = await db.execute(
        select(VacationRequest).where(and_(VacationRequest.id == request_id, VacationRequest.is_active))
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    return VacationRequestResponse.model_validate(req)


@router.patch("/{request_id}", response_model=VacationRequestResponse)
async def update_vacation_request(
    request_id: str,
    data: VacationRequestUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> VacationRequestResponse:
    """Atualiza uma solicitação."""
    result = await db.execute(
        select(VacationRequest).where(and_(VacationRequest.id == request_id, VacationRequest.is_active))
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(req, field, value)

    req.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(req)
    return VacationRequestResponse.model_validate(req)


@router.post("/{request_id}/approve", response_model=VacationRequestResponse, status_code=201)
async def approve_vacation_request(
    request_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> VacationRequestResponse:
    """Aprova uma solicitação."""
    result = await db.execute(select(VacationRequest).where(VacationRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    req.status = "aprovado"
    req.approved_at = datetime.utcnow()
    req.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(req)
    return VacationRequestResponse.model_validate(req)


@router.post("/{request_id}/reject", response_model=VacationRequestResponse, status_code=201)
async def reject_vacation_request(
    request_id: str,
    current_user: CurrentActiveUser,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> VacationRequestResponse:
    """Rejeita uma solicitação."""
    result = await db.execute(select(VacationRequest).where(VacationRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    req.status = "rejeitado"
    req.rejected_reason = reason
    req.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(req)
    return VacationRequestResponse.model_validate(req)


@router.delete("/{request_id}", status_code=204)
async def delete_vacation_request(
    request_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Cancela/exclui uma solicitação."""
    result = await db.execute(select(VacationRequest).where(VacationRequest.id == request_id))
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    req.is_active = False
    req.status = "cancelado"
    req.updated_at = datetime.utcnow()
    await db.commit()
