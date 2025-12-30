"""Controller para ResidentPet."""

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.auth.dependencies import get_current_user
from modules.residents.services.pet_service import PetService
from modules.residents.schemas.pet import (
    PetCreate,
    PetUpdate,
    PetFilter,
    PetResponse,
    PetListResponse,
    PetStats,
    PetUpdateVaccination,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/residents/pets", tags=["Pets de Moradores"])


def get_service(session: AsyncSession = Depends(get_session)) -> PetService:
    """Retorna instância do service."""
    return PetService(session)


# ========== CRUD Endpoints ==========


@router.post(
    "/",
    response_model=PetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pet",
)
async def create_pet(
    data: PetCreate,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Cria um novo pet."""
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/",
    response_model=PetListResponse,
    summary="Listar pets",
)
async def list_pets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    resident_id: Optional[str] = None,
    pet_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    breed: Optional[str] = None,
    size: Optional[str] = None,
    is_vaccinated: Optional[bool] = None,
    is_neutered: Optional[bool] = None,
    is_aggressive: Optional[bool] = None,
    can_use_common_areas: Optional[bool] = None,
    condominium_id: Optional[str] = None,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista pets com filtros e paginação."""
    from modules.residents.models.pet import PetStatus, PetType, PetSize

    filters = PetFilter(
        resident_id=UUID(resident_id) if resident_id else None,
        pet_type=PetType(pet_type) if pet_type else None,
        status=PetStatus(status_filter) if status_filter else None,
        breed=breed,
        size=PetSize(size) if size else None,
        is_vaccinated=is_vaccinated,
        is_neutered=is_neutered,
        is_aggressive=is_aggressive,
        can_use_common_areas=can_use_common_areas,
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
    response_model=list[PetResponse],
    summary="Buscar pets",
)
async def search_pets(
    query: str = Query(..., min_length=1),
    condominium_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca pets por termo."""
    return await service.search(query, condominium_id, limit)


@router.get(
    "/stats",
    response_model=PetStats,
    summary="Estatísticas de pets",
)
async def get_pets_stats(
    condominium_id: Optional[str] = None,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna estatísticas de pets."""
    return await service.get_stats(condominium_id)


@router.get(
    "/aggressive",
    response_model=list[PetResponse],
    summary="Listar pets agressivos",
)
async def list_aggressive_pets(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista pets agressivos."""
    return await service.get_aggressive(condominium_id, page, page_size)


@router.get(
    "/not-vaccinated",
    response_model=list[PetResponse],
    summary="Listar pets não vacinados",
)
async def list_not_vaccinated_pets(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista pets não vacinados."""
    return await service.get_not_vaccinated(condominium_id, page, page_size)


@router.get(
    "/vaccination-expiring",
    response_model=list[PetResponse],
    summary="Listar pets com vacina expirando",
)
async def list_vaccination_expiring_pets(
    days: int = Query(30, ge=1, le=365),
    condominium_id: Optional[str] = None,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista pets com vacina expirando nos próximos dias."""
    return await service.get_vaccination_expiring(days, condominium_id)


@router.get(
    "/by-microchip/{microchip}",
    response_model=PetResponse,
    summary="Buscar por microchip",
)
async def get_pet_by_microchip(
    microchip: str,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca pet por microchip."""
    pet = await service.get_by_microchip(microchip)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.get(
    "/by-resident/{resident_id}",
    response_model=list[PetResponse],
    summary="Buscar por morador",
)
async def get_pets_by_resident(
    resident_id: UUID,
    include_inactive: bool = Query(False),
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca pets do morador."""
    return await service.get_by_resident(resident_id, include_inactive)


@router.get(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Buscar pet",
)
async def get_pet(
    pet_id: UUID,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca pet por ID."""
    pet = await service.get_by_id(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.put(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Atualizar pet",
)
async def update_pet(
    pet_id: UUID,
    data: PetUpdate,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza um pet."""
    try:
        pet = await service.update(pet_id, data)
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pet não encontrado",
            )
        return pet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover pet",
)
async def delete_pet(
    pet_id: UUID,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove um pet (soft delete)."""
    result = await service.delete(pet_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )


# ========== Action Endpoints ==========


@router.post(
    "/{pet_id}/update-vaccination",
    response_model=PetResponse,
    summary="Atualizar vacinação",
)
async def update_pet_vaccination(
    pet_id: UUID,
    data: PetUpdateVaccination,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza vacinação do pet."""
    pet = await service.update_vaccination(
        pet_id, data.vaccination_date, data.expiry_date
    )
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.post(
    "/{pet_id}/deactivate",
    response_model=PetResponse,
    summary="Desativar pet",
)
async def deactivate_pet(
    pet_id: UUID,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desativa um pet."""
    pet = await service.deactivate(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.post(
    "/{pet_id}/mark-deceased",
    response_model=PetResponse,
    summary="Marcar como falecido",
)
async def mark_pet_deceased(
    pet_id: UUID,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Marca pet como falecido."""
    pet = await service.mark_as_deceased(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.post(
    "/{pet_id}/mark-donated",
    response_model=PetResponse,
    summary="Marcar como doado",
)
async def mark_pet_donated(
    pet_id: UUID,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Marca pet como doado."""
    pet = await service.mark_as_donated(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.post(
    "/{pet_id}/mark-lost",
    response_model=PetResponse,
    summary="Marcar como perdido",
)
async def mark_pet_lost(
    pet_id: UUID,
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Marca pet como perdido."""
    pet = await service.mark_as_lost(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.post(
    "/{pet_id}/restrict-areas",
    response_model=PetResponse,
    summary="Restringir áreas",
)
async def restrict_pet_areas(
    pet_id: UUID,
    areas: list[str],
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Restringe áreas para o pet."""
    pet = await service.restrict_areas(pet_id, areas)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet


@router.post(
    "/{pet_id}/allow-areas",
    response_model=PetResponse,
    summary="Permitir áreas",
)
async def allow_pet_areas(
    pet_id: UUID,
    areas: list[str],
    service: PetService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Permite áreas para o pet."""
    pet = await service.allow_areas(pet_id, areas)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet não encontrado",
        )
    return pet
