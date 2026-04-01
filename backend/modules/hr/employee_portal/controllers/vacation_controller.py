"""Controller para férias."""

import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user, require_roles
from core.database import get_async_session
from modules.hr.employee_portal.models import VacationStatus
from modules.hr.employee_portal.schemas import (
    VacationBalanceResponse,
    VacationCalculationRequest,
    VacationCalculationResponse,
    VacationRequestCreate,
    VacationRequestListResponse,
    VacationRequestResponse,
)
from modules.hr.employee_portal.services import VacationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vacation", tags=["Portal - Férias"])


@router.get(
    "/balance",
    response_model=VacationBalanceResponse,
    summary="Saldo de férias",
)
async def get_vacation_balance(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna saldo de férias do funcionário."""
    service = VacationService(db)
    employee_id = UUID(current_user["employee_id"])

    return await service.get_vacation_balance(employee_id)


@router.post("/calculate", response_model=VacationCalculationResponse, summary="Calcular valores de férias")
async def calculate_vacation(
    data: VacationCalculationRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Calcula valores de férias (simulação)."""
    service = VacationService(db)

    # Em produção, buscar salário do funcionário
    base_salary = Decimal(current_user.get("base_salary", "3000.00"))

    return await service.calculate_vacation(data, base_salary)


@router.get(
    "/requests",
    response_model=VacationRequestListResponse,
    summary="Listar solicitações de férias",
)
async def list_vacation_requests(
    status_filter: VacationStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Lista solicitações de férias do funcionário."""
    service = VacationService(db)
    employee_id = UUID(current_user["employee_id"])

    requests, total = await service.request_repo.list_by_employee(
        employee_id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )

    return VacationRequestListResponse(
        items=[VacationRequestResponse.model_validate(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post(
    "/requests",
    response_model=VacationRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar solicitação de férias",
)
async def create_vacation_request(
    data: VacationRequestCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Cria nova solicitação de férias."""
    service = VacationService(db)
    employee_id = UUID(current_user["employee_id"])
    condominio_id = UUID(current_user["condominio_id"])

    try:
        request = await service.create_vacation_request(
            data,
            condominio_id,
            employee_id,
        )
        return VacationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/requests/{request_id}",
    response_model=VacationRequestResponse,
    summary="Detalhes da solicitação",
)
async def get_vacation_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna detalhes de uma solicitação de férias."""
    service = VacationService(db)
    employee_id = UUID(current_user["employee_id"])

    request = await service.request_repo.get_by_id(request_id)
    if not request or request.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada",
        )

    return VacationRequestResponse.model_validate(request)


@router.post(
    "/requests/{request_id}/submit",
    response_model=VacationRequestResponse,
    summary="Enviar solicitação para aprovação",
    status_code=201,
)
async def submit_vacation_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Envia solicitação para aprovação do gestor."""
    service = VacationService(db)
    employee_id = UUID(current_user["employee_id"])

    try:
        request = await service.submit_request(request_id, employee_id)
        return VacationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/requests/{request_id}/cancel",
    response_model=VacationRequestResponse,
    summary="Cancelar solicitação",
    status_code=201,
)
async def cancel_vacation_request(
    request_id: UUID,
    reason: str = Body(..., min_length=10, max_length=500, embed=True),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Cancela solicitação de férias."""
    service = VacationService(db)
    employee_id = UUID(current_user["employee_id"])

    try:
        request = await service.cancel_vacation(request_id, employee_id, reason)
        return VacationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# --- Endpoints administrativos (Gestor/RH) ---


@router.get(
    "/pending-approvals",
    response_model=VacationRequestListResponse,
    summary="Solicitações pendentes de aprovação",
    dependencies=[Depends(require_roles(["admin", "hr", "manager"]))],
)
async def list_pending_approvals(
    manager_level: bool = Query(True, description="Nível gestor ou RH"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Lista solicitações pendentes de aprovação."""
    service = VacationService(db)
    condominio_id = UUID(current_user["condominio_id"])

    requests, total = await service.get_pending_approvals(
        condominio_id,
        manager_level=manager_level,
        page=page,
        page_size=page_size,
    )

    return VacationRequestListResponse(
        items=[VacationRequestResponse.model_validate(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post(
    "/requests/{request_id}/approve",
    response_model=VacationRequestResponse,
    summary="Aprovar solicitação",
    dependencies=[Depends(require_roles(["admin", "hr", "manager"]))],
)
async def approve_vacation_request(
    request_id: UUID,
    level: str = Query("manager", regex="^(manager|hr)$"),
    notes: str | None = Body(None, max_length=500),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Aprova solicitação de férias."""
    service = VacationService(db)
    approved_by = UUID(current_user["sub"])

    try:
        request = await service.approve_vacation(
            request_id,
            approved_by,
            level=level,
            approved=True,
            notes=notes,
        )
        return VacationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/requests/{request_id}/reject",
    response_model=VacationRequestResponse,
    summary="Rejeitar solicitação",
    dependencies=[Depends(require_roles(["admin", "hr", "manager"]))],
)
async def reject_vacation_request(
    request_id: UUID,
    level: str = Query("manager", regex="^(manager|hr)$"),
    reason: str = Body(..., min_length=10, max_length=500, embed=True),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Rejeita solicitação de férias."""
    service = VacationService(db)
    rejected_by = UUID(current_user["sub"])

    try:
        request = await service.approve_vacation(
            request_id,
            rejected_by,
            level=level,
            approved=False,
            rejection_reason=reason,
        )
        return VacationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/upcoming",
    summary="Férias programadas",
    dependencies=[Depends(require_roles(["admin", "hr", "manager"]))],
)
async def get_upcoming_vacations(
    days_ahead: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna férias programadas para os próximos dias."""
    service = VacationService(db)
    condominio_id = UUID(current_user["condominio_id"])

    vacations = await service.get_upcoming_vacations(condominio_id, days_ahead)

    return {
        "days_ahead": days_ahead,
        "count": len(vacations),
        "items": [VacationRequestResponse.model_validate(v) for v in vacations],
    }
