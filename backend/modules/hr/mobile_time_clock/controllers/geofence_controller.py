"""Controller para gerenciamento de zonas de geofencing."""

import logging
from typing import List  # noqa: F401  # pylint: disable=unused-import
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user, require_roles
from modules.hr.mobile_time_clock.schemas import (
    GeofenceZoneCreate,
    GeofenceZoneUpdate,
    GeofenceZoneResponse,
    GeofenceZoneList,
    GeofenceZoneFilter,
    GeofenceCheckRequest,
    GeofenceCheckResponse,
    GeofenceZoneStats,
)
from modules.hr.mobile_time_clock.services import GeofenceService
from modules.hr.mobile_time_clock.repositories import GeofenceZoneRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile/geofences", tags=["Geofence Zones"])


@router.post(
    "/check",
    response_model=GeofenceCheckResponse,
    summary="Verificar localização",
)
async def check_location(
    data: GeofenceCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Verifica se localização está dentro de zona permitida."""
    service = GeofenceService(db)

    result = await service.check_location(
        request=data,
        employee_id=current_user["sub"],
    )

    return result


@router.get(
    "/available",
    summary="Zonas disponíveis",
)
async def get_available_zones(
    latitude: float = Query(None),
    longitude: float = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista zonas disponíveis para o funcionário."""
    service = GeofenceService(db)

    zones = await service.get_zones_for_employee(
        condominio_id=UUID(current_user.get("condominio_id")),
        employee_id=current_user["sub"],
        latitude=latitude,
        longitude=longitude,
    )

    return {"zones": zones, "total": len(zones)}


# === Endpoints Administrativos ===


@router.post(
    "/",
    response_model=GeofenceZoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar zona",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def create_zone(
    data: GeofenceZoneCreate,
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cria nova zona de geofencing."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    service = GeofenceService(db)

    zone = await service.create_zone(
        data=data,
        condominio_id=condo_id,
        created_by=UUID(current_user["sub"]),
    )

    return zone


@router.get(
    "/{zone_id}",
    response_model=GeofenceZoneResponse,
    summary="Detalhes da zona",
)
async def get_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Obtém detalhes de uma zona."""
    repo = GeofenceZoneRepository(db)
    zone = await repo.get_by_id(zone_id)

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona não encontrada",
        )

    return zone


@router.put(
    "/{zone_id}",
    response_model=GeofenceZoneResponse,
    summary="Atualizar zona",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def update_zone(
    zone_id: UUID,
    data: GeofenceZoneUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza zona existente."""
    service = GeofenceService(db)

    zone = await service.update_zone(zone_id, data)

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona não encontrada",
        )

    return zone


@router.post(
    "/{zone_id}/set-primary",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Definir como zona primária",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def set_primary_zone(
    zone_id: UUID,
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Define zona como primária do condomínio."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    service = GeofenceService(db)

    # Verificar se zona existe
    repo = GeofenceZoneRepository(db)
    zone = await repo.get_by_id(zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona não encontrada",
        )

    await service.set_primary_zone(zone_id, condo_id)


@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativar zona",
    dependencies=[Depends(require_roles(["admin", "rh"]))],
)
async def deactivate_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Desativa zona (soft delete)."""
    service = GeofenceService(db)

    if not await service.deactivate_zone(zone_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona não encontrada",
        )


@router.get(
    "/",
    response_model=GeofenceZoneList,
    summary="Listar zonas",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def list_zones(  # pylint: disable=too-many-locals
    condominio_id: UUID = Query(None),
    post_id: UUID = Query(None),
    category: str = Query(None),
    zone_status: str = Query(None, alias="status"),
    is_primary: bool = Query(None),
    is_active: bool = Query(None),
    near_latitude: float = Query(None),
    near_longitude: float = Query(None),
    max_distance_km: float = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lista zonas com filtros."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))

    filters = GeofenceZoneFilter(
        condominio_id=condo_id,
        post_id=post_id,
        category=category,
        status=zone_status,
        is_primary=is_primary,
        is_active=is_active,
        near_latitude=near_latitude,
        near_longitude=near_longitude,
        max_distance_km=max_distance_km,
    )

    repo = GeofenceZoneRepository(db)
    items, total = await repo.list_zones(filters, page, page_size)

    return GeofenceZoneList(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/statistics",
    response_model=GeofenceZoneStats,
    summary="Estatísticas de zonas",
    dependencies=[Depends(require_roles(["admin", "rh", "gestor"]))],
)
async def get_zone_statistics(
    condominio_id: UUID = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Obtém estatísticas de zonas."""
    condo_id = condominio_id or UUID(current_user.get("condominio_id"))
    service = GeofenceService(db)
    return await service.get_zone_statistics(condo_id)
