"""Controller para VisitorAuthorization."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from modules.visitors.models.authorization import AuthorizationStatus, AuthorizationType
from modules.visitors.schemas.authorization import (
    AuthorizationApprove,
    AuthorizationCreate,
    AuthorizationFilter,
    AuthorizationListResponse,
    AuthorizationReject,
    AuthorizationResponse,
    AuthorizationStats,
    AuthorizationUpdate,
    AuthorizationValidate,
    AuthorizationValidateResponse,
)
from modules.visitors.services.authorization_service import AuthorizationService

router = APIRouter(prefix="/visitor-authorizations", tags=["Visitor Authorizations"])


# ========== CRUD ==========


@router.post(
    "/", response_model=AuthorizationResponse, status_code=status.HTTP_201_CREATED
)
async def create_authorization(
    data: AuthorizationCreate,
    session: AsyncSession = Depends(get_session),
):
    """Cria uma nova autorização."""
    service = AuthorizationService(session)
    return await service.create(data)


@router.get("/", response_model=AuthorizationListResponse)
async def list_authorizations(
    visitor_id: Optional[UUID] = None,
    authorization_type: Optional[AuthorizationType] = None,
    auth_status: Optional[AuthorizationStatus] = Query(None, alias="status"),
    condominium_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    resident_id: Optional[str] = None,
    is_expired: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = "created_at",
    order_desc: bool = True,
    session: AsyncSession = Depends(get_session),
):
    """Lista autorizações com filtros."""
    filters = AuthorizationFilter(
        visitor_id=visitor_id,
        authorization_type=authorization_type,
        status=auth_status,
        condominium_id=condominium_id,
        unit_id=unit_id,
        resident_id=resident_id,
        is_expired=is_expired,
    )
    service = AuthorizationService(session)
    return await service.list(filters, page, page_size, order_by, order_desc)


@router.get("/stats", response_model=AuthorizationStats)
async def get_authorization_stats(
    condominium_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    session: AsyncSession = Depends(get_session),
):
    """Retorna estatísticas de autorizações."""
    service = AuthorizationService(session)
    return await service.get_stats(condominium_id, date_from)


@router.get("/pending", response_model=AuthorizationListResponse)
async def get_pending_authorizations(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista autorizações pendentes."""
    service = AuthorizationService(session)
    return await service.get_pending(condominium_id, page, page_size)


@router.get("/active", response_model=AuthorizationListResponse)
async def get_active_authorizations(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista autorizações ativas."""
    service = AuthorizationService(session)
    return await service.get_active(condominium_id, page, page_size)


@router.get("/expiring-soon", response_model=list[AuthorizationResponse])
async def get_expiring_authorizations(
    days: int = Query(7, ge=1, le=30),
    condominium_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Lista autorizações que expiram em breve."""
    service = AuthorizationService(session)
    return await service.get_expiring_soon(days, condominium_id)


@router.get("/by-visitor/{visitor_id}", response_model=AuthorizationListResponse)
async def get_visitor_authorizations(
    visitor_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Lista autorizações de um visitante."""
    service = AuthorizationService(session)
    return await service.get_by_visitor(visitor_id, page, page_size)


@router.get("/by-code/{code}", response_model=AuthorizationResponse)
async def get_authorization_by_code(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    """Busca autorização por código."""
    service = AuthorizationService(session)
    auth = await service.get_by_code(code)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


@router.get("/{auth_id}", response_model=AuthorizationResponse)
async def get_authorization(
    auth_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Busca autorização por ID."""
    service = AuthorizationService(session)
    auth = await service.get_by_id(auth_id)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


@router.put("/{auth_id}", response_model=AuthorizationResponse)
async def update_authorization(
    auth_id: UUID,
    data: AuthorizationUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza uma autorização."""
    service = AuthorizationService(session)
    auth = await service.update(auth_id, data)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


@router.delete("/{auth_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_authorization(
    auth_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Deleta uma autorização."""
    service = AuthorizationService(session)
    if not await service.delete(auth_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )


# ========== Ações ==========


@router.post("/{auth_id}/approve", response_model=AuthorizationResponse)
async def approve_authorization(
    auth_id: UUID,
    data: AuthorizationApprove,
    session: AsyncSession = Depends(get_session),
):
    """Aprova uma autorização."""
    service = AuthorizationService(session)
    auth = await service.approve(auth_id, data)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


@router.post("/{auth_id}/reject", response_model=AuthorizationResponse)
async def reject_authorization(
    auth_id: UUID,
    data: AuthorizationReject,
    session: AsyncSession = Depends(get_session),
):
    """Rejeita uma autorização."""
    service = AuthorizationService(session)
    auth = await service.reject(auth_id, data)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


@router.post("/{auth_id}/cancel", response_model=AuthorizationResponse)
async def cancel_authorization(
    auth_id: UUID,
    reason: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    """Cancela uma autorização."""
    service = AuthorizationService(session)
    auth = await service.cancel(auth_id, reason)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


@router.post("/{auth_id}/use", response_model=AuthorizationResponse)
async def use_authorization(
    auth_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Registra uso da autorização."""
    service = AuthorizationService(session)
    auth = await service.use(auth_id)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Autorização não pode ser utilizada",
        )
    return auth


@router.post("/{auth_id}/extend", response_model=AuthorizationResponse)
async def extend_authorization(
    auth_id: UUID,
    days: int = Query(..., ge=1, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Estende a validade de uma autorização."""
    service = AuthorizationService(session)
    auth = await service.extend_validity(auth_id, days)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autorização não encontrada",
        )
    return auth


# ========== Validação ==========


@router.post("/validate", response_model=AuthorizationValidateResponse)
async def validate_authorization(
    data: AuthorizationValidate,
    session: AsyncSession = Depends(get_session),
):
    """Valida uma autorização."""
    service = AuthorizationService(session)
    return await service.validate(data)
