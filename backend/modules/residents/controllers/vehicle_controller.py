"""Controller para ResidentVehicle."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.auth.dependencies import get_current_user
from modules.residents.services.vehicle_service import VehicleService
from modules.residents.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleFilter,
    VehicleResponse,
    VehicleListResponse,
    VehicleStats,
    VehicleBlock,
    VehicleAssignParking,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/residents/vehicles", tags=["Veículos de Moradores"])


def get_service(session: AsyncSession = Depends(get_session)) -> VehicleService:
    """Retorna instância do service."""
    return VehicleService(session)


# ========== CRUD Endpoints ==========


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar veículo",
)
async def create_vehicle(
    data: VehicleCreate,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Cria um novo veículo."""
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/",
    response_model=VehicleListResponse,
    summary="Listar veículos",
)
async def list_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    resident_id: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    brand: Optional[str] = None,
    model: Optional[str] = None,
    plate: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    has_rfid: Optional[bool] = None,
    condominium_id: Optional[str] = None,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista veículos com filtros e paginação."""
    from modules.residents.models.vehicle import VehicleStatus, VehicleType

    filters = VehicleFilter(
        resident_id=UUID(resident_id) if resident_id else None,
        vehicle_type=VehicleType(vehicle_type) if vehicle_type else None,
        status=VehicleStatus(status_filter) if status_filter else None,
        brand=brand,
        model=model,
        plate=plate,
        is_blocked=is_blocked,
        has_rfid=has_rfid,
        condominium_id=condominium_id,
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
    response_model=list[VehicleResponse],
    summary="Buscar veículos",
)
async def search_vehicles(
    query: str = Query(..., min_length=2),
    condominium_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca veículos por termo."""
    return await service.search(query, condominium_id, limit)


@router.get(
    "/stats",
    response_model=VehicleStats,
    summary="Estatísticas de veículos",
)
async def get_vehicles_stats(
    condominium_id: Optional[str] = None,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna estatísticas de veículos."""
    return await service.get_stats(condominium_id)


@router.get(
    "/blocked",
    response_model=list[VehicleResponse],
    summary="Listar veículos bloqueados",
)
async def list_blocked_vehicles(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista veículos bloqueados."""
    return await service.get_blocked(condominium_id, page, page_size)


@router.get(
    "/without-parking/{condominium_id}",
    response_model=list[VehicleResponse],
    summary="Listar veículos sem vaga",
)
async def list_vehicles_without_parking(
    condominium_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista veículos sem vaga de estacionamento."""
    return await service.get_without_parking(condominium_id, page, page_size)


@router.get(
    "/by-plate/{plate}",
    response_model=VehicleResponse,
    summary="Buscar por placa",
)
async def get_vehicle_by_plate(
    plate: str,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca veículo por placa."""
    vehicle = await service.get_by_plate(plate)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.get(
    "/by-rfid/{rfid_tag}",
    response_model=VehicleResponse,
    summary="Buscar por RFID",
)
async def get_vehicle_by_rfid(
    rfid_tag: str,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca veículo por tag RFID."""
    vehicle = await service.get_by_rfid(rfid_tag)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.get(
    "/by-resident/{resident_id}",
    response_model=list[VehicleResponse],
    summary="Buscar por morador",
)
async def get_vehicles_by_resident(
    resident_id: UUID,
    include_inactive: bool = Query(False),
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca veículos do morador."""
    return await service.get_by_resident(resident_id, include_inactive)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Buscar veículo",
)
async def get_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca veículo por ID."""
    vehicle = await service.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Atualizar veículo",
)
async def update_vehicle(
    vehicle_id: UUID,
    data: VehicleUpdate,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza um veículo."""
    try:
        vehicle = await service.update(vehicle_id, data)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado",
            )
        return vehicle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover veículo",
)
async def delete_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove um veículo (soft delete)."""
    result = await service.delete(vehicle_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )


# ========== Action Endpoints ==========


@router.post(
    "/{vehicle_id}/block",
    response_model=VehicleResponse,
    summary="Bloquear veículo",
)
async def block_vehicle(
    vehicle_id: UUID,
    data: VehicleBlock,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Bloqueia um veículo."""
    vehicle = await service.block(
        vehicle_id, data.reason, current_user.get("id", "system")
    )
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.post(
    "/{vehicle_id}/unblock",
    response_model=VehicleResponse,
    summary="Desbloquear veículo",
)
async def unblock_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desbloqueia um veículo."""
    vehicle = await service.unblock(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.post(
    "/{vehicle_id}/assign-parking",
    response_model=VehicleResponse,
    summary="Atribuir vaga",
)
async def assign_vehicle_parking(
    vehicle_id: UUID,
    data: VehicleAssignParking,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atribui vaga de estacionamento ao veículo."""
    try:
        vehicle = await service.assign_parking(vehicle_id, data.parking_spot)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado",
            )
        return vehicle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/{vehicle_id}/remove-parking",
    response_model=VehicleResponse,
    summary="Remover vaga",
)
async def remove_vehicle_parking(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove vaga de estacionamento do veículo."""
    vehicle = await service.remove_parking(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.post(
    "/{vehicle_id}/mark-sold",
    response_model=VehicleResponse,
    summary="Marcar como vendido",
)
async def mark_vehicle_sold(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Marca veículo como vendido."""
    vehicle = await service.mark_as_sold(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.post(
    "/{vehicle_id}/mark-stolen",
    response_model=VehicleResponse,
    summary="Marcar como roubado",
)
async def mark_vehicle_stolen(
    vehicle_id: UUID,
    report_number: Optional[str] = None,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Marca veículo como roubado."""
    vehicle = await service.mark_as_stolen(vehicle_id, report_number)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return vehicle


@router.post(
    "/validate-access",
    summary="Validar acesso de veículo",
)
async def validate_vehicle_access(
    plate: Optional[str] = None,
    rfid: Optional[str] = None,
    service: VehicleService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Valida acesso de veículo por placa ou RFID."""
    if not plate and not rfid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe placa ou RFID",
        )
    return await service.validate_access(plate, rfid)
