"""Controller para Resident."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.auth.dependencies import get_current_user
from modules.residents.services.resident_service import ResidentService
from modules.residents.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    ResidentFilter,
    ResidentResponse,
    ResidentListResponse,
    ResidentStats,
    ResidentBlock,
    ResidentSetDefaulter,
    ResidentMoveOut,
    ResidentTransferUnit,
    ResidentEnableAccess,
    ResidentSearch,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/residents", tags=["Moradores"])


def get_service(session: AsyncSession = Depends(get_session)) -> ResidentService:
    """Retorna instância do service."""
    return ResidentService(session)


# ========== CRUD Endpoints ==========


@router.post(
    "/",
    response_model=ResidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar morador",
)
async def create_resident(
    data: ResidentCreate,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Cria um novo morador."""
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/",
    response_model=ResidentListResponse,
    summary="Listar moradores",
)
async def list_residents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    name: Optional[str] = None,
    resident_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    condominium_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    block: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    is_defaulter: Optional[bool] = None,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista moradores com filtros e paginação."""
    from modules.residents.models.resident import ResidentStatus, ResidentType

    filters = ResidentFilter(
        name=name,
        resident_type=ResidentType(resident_type) if resident_type else None,
        status=ResidentStatus(status_filter) if status_filter else None,
        condominium_id=condominium_id,
        unit_id=unit_id,
        block=block,
        is_blocked=is_blocked,
        is_defaulter=is_defaulter,
    )

    return await service.list(
        filters=filters,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_desc=order_desc,
    )


@router.get(
    "/search",
    response_model=list[ResidentResponse],
    summary="Buscar moradores",
)
async def search_residents(
    query: str = Query(..., min_length=2),
    condominium_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca moradores por termo."""
    return await service.search(query, condominium_id, limit)


@router.get(
    "/stats",
    response_model=ResidentStats,
    summary="Estatísticas de moradores",
)
async def get_residents_stats(
    condominium_id: Optional[str] = None,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna estatísticas de moradores."""
    return await service.get_stats(condominium_id)


@router.get(
    "/blocked",
    response_model=list[ResidentResponse],
    summary="Listar moradores bloqueados",
)
async def list_blocked_residents(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista moradores bloqueados."""
    return await service.get_blocked(condominium_id, page, page_size)


@router.get(
    "/defaulters",
    response_model=list[ResidentResponse],
    summary="Listar moradores inadimplentes",
)
async def list_defaulter_residents(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista moradores inadimplentes."""
    return await service.get_defaulters(condominium_id, page, page_size)


@router.get(
    "/owners/{condominium_id}",
    response_model=list[ResidentResponse],
    summary="Listar proprietários",
)
async def list_owners(
    condominium_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista proprietários do condomínio."""
    return await service.get_owners(condominium_id, page, page_size)


@router.get(
    "/by-code/{code}",
    response_model=ResidentResponse,
    summary="Buscar por código",
)
async def get_resident_by_code(
    code: str,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca morador por código."""
    resident = await service.get_by_code(code)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.get(
    "/by-cpf/{cpf}",
    response_model=ResidentResponse,
    summary="Buscar por CPF",
)
async def get_resident_by_cpf(
    cpf: str,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca morador por CPF."""
    resident = await service.get_by_cpf(cpf)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.get(
    "/by-unit/{condominium_id}/{unit_id}",
    response_model=list[ResidentResponse],
    summary="Buscar por unidade",
)
async def get_residents_by_unit(
    condominium_id: str,
    unit_id: str,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca moradores da unidade."""
    return await service.get_by_unit(condominium_id, unit_id)


@router.get(
    "/{resident_id}",
    response_model=ResidentResponse,
    summary="Buscar morador",
)
async def get_resident(
    resident_id: UUID,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca morador por ID."""
    resident = await service.get_by_id(resident_id)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.put(
    "/{resident_id}",
    response_model=ResidentResponse,
    summary="Atualizar morador",
)
async def update_resident(
    resident_id: UUID,
    data: ResidentUpdate,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza um morador."""
    try:
        resident = await service.update(resident_id, data)
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Morador não encontrado",
            )
        return resident
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{resident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover morador",
)
async def delete_resident(
    resident_id: UUID,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove um morador (soft delete)."""
    result = await service.delete(resident_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )


# ========== Action Endpoints ==========


@router.post(
    "/{resident_id}/block",
    response_model=ResidentResponse,
    summary="Bloquear morador",
)
async def block_resident(
    resident_id: UUID,
    data: ResidentBlock,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Bloqueia um morador."""
    resident = await service.block(
        resident_id, data.reason, current_user.get("id", "system")
    )
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.post(
    "/{resident_id}/unblock",
    response_model=ResidentResponse,
    summary="Desbloquear morador",
)
async def unblock_resident(
    resident_id: UUID,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desbloqueia um morador."""
    resident = await service.unblock(resident_id)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.post(
    "/{resident_id}/set-defaulter",
    response_model=ResidentResponse,
    summary="Marcar como inadimplente",
)
async def set_resident_defaulter(
    resident_id: UUID,
    data: ResidentSetDefaulter,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Marca morador como inadimplente."""
    resident = await service.set_defaulter(resident_id, data.debt_amount)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.post(
    "/{resident_id}/clear-defaulter",
    response_model=ResidentResponse,
    summary="Remover inadimplência",
)
async def clear_resident_defaulter(
    resident_id: UUID,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove inadimplência do morador."""
    resident = await service.clear_defaulter(resident_id)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.post(
    "/{resident_id}/move-out",
    response_model=ResidentResponse,
    summary="Registrar mudança",
)
async def resident_move_out(
    resident_id: UUID,
    data: ResidentMoveOut,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Registra mudança do morador."""
    resident = await service.move_out(resident_id, data.move_out_date)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.post(
    "/{resident_id}/transfer-unit",
    response_model=ResidentResponse,
    summary="Transferir unidade",
)
async def transfer_resident_unit(
    resident_id: UUID,
    data: ResidentTransferUnit,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Transfere morador para nova unidade."""
    resident = await service.transfer_unit(
        resident_id, data.new_unit_id, data.new_unit_number, data.new_block
    )
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return resident


@router.post(
    "/{resident_id}/enable-access",
    response_model=ResidentResponse,
    summary="Habilitar acesso",
)
async def enable_resident_access(
    resident_id: UUID,
    data: ResidentEnableAccess,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Habilita método de acesso para morador."""
    try:
        resident = await service.enable_access(
            resident_id, data.method, data.identifier
        )
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Morador não encontrado",
            )
        return resident
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/{resident_id}/disable-access/{method}",
    response_model=ResidentResponse,
    summary="Desabilitar acesso",
)
async def disable_resident_access(
    resident_id: UUID,
    method: str,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desabilita método de acesso para morador."""
    try:
        resident = await service.disable_access(resident_id, method)
        if not resident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Morador não encontrado",
            )
        return resident
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/{resident_id}/qr-code",
    summary="Gerar QR Code",
)
async def generate_resident_qr_code(
    resident_id: UUID,
    service: ResidentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Gera QR Code para morador."""
    qr_code = await service.generate_qr_code(resident_id)
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador não encontrado",
        )
    return {"qr_code": qr_code}
