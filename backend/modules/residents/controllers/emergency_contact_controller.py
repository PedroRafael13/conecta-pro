"""Controller para ResidentEmergencyContact."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.auth.dependencies import get_current_user
from modules.residents.services.emergency_contact_service import EmergencyContactService
from modules.residents.schemas.emergency_contact import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactFilter,
    EmergencyContactResponse,
    EmergencyContactListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/residents/emergency-contacts",
    tags=["Contatos de Emergência"],
)


def get_service(
    session: AsyncSession = Depends(get_session),
) -> EmergencyContactService:
    """Retorna instância do service."""
    return EmergencyContactService(session)


# ========== CRUD Endpoints ==========


@router.post(
    "/",
    response_model=EmergencyContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar contato de emergência",
)
async def create_emergency_contact(
    data: EmergencyContactCreate,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Cria um novo contato de emergência."""
    return await service.create(data)


@router.get(
    "/",
    response_model=EmergencyContactListResponse,
    summary="Listar contatos de emergência",
)
async def list_emergency_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("priority"),
    order_desc: bool = Query(False),
    resident_id: Optional[str] = None,
    relationship: Optional[str] = None,
    is_primary: Optional[bool] = None,
    is_active: Optional[bool] = None,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista contatos de emergência com filtros e paginação."""
    from modules.residents.models.emergency_contact import ContactRelationship

    filters = EmergencyContactFilter(
        resident_id=UUID(resident_id) if resident_id else None,
        relationship=(
            ContactRelationship(relationship) if relationship else None
        ),
        is_primary=is_primary,
        is_active=is_active,
    )

    return await service.list(
        filters=filters,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order_desc=order_desc,
    )


@router.get(
    "/by-resident/{resident_id}",
    response_model=list[EmergencyContactResponse],
    summary="Buscar por morador",
)
async def get_emergency_contacts_by_resident(
    resident_id: UUID,
    include_inactive: bool = Query(False),
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca contatos de emergência do morador."""
    return await service.get_by_resident(resident_id, include_inactive)


@router.get(
    "/primary/{resident_id}",
    response_model=EmergencyContactResponse,
    summary="Buscar contato principal",
)
async def get_primary_emergency_contact(
    resident_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca contato de emergência principal do morador."""
    contact = await service.get_primary_by_resident(resident_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato principal não encontrado",
        )
    return contact


@router.get(
    "/by-relationship/{resident_id}/{relationship}",
    response_model=list[EmergencyContactResponse],
    summary="Buscar por relacionamento",
)
async def get_emergency_contacts_by_relationship(
    resident_id: UUID,
    relationship: str,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca contatos de emergência por relacionamento."""
    return await service.get_by_relationship(resident_id, relationship)


@router.get(
    "/stats/{resident_id}",
    summary="Estatísticas de contatos",
)
async def get_emergency_contacts_stats(
    resident_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna estatísticas de contatos do morador."""
    return await service.get_stats_by_resident(resident_id)


@router.get(
    "/{contact_id}",
    response_model=EmergencyContactResponse,
    summary="Buscar contato",
)
async def get_emergency_contact(
    contact_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca contato de emergência por ID."""
    contact = await service.get_by_id(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado",
        )
    return contact


@router.put(
    "/{contact_id}",
    response_model=EmergencyContactResponse,
    summary="Atualizar contato",
)
async def update_emergency_contact(
    contact_id: UUID,
    data: EmergencyContactUpdate,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza um contato de emergência."""
    contact = await service.update(contact_id, data)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado",
        )
    return contact


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover contato",
)
async def delete_emergency_contact(
    contact_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove um contato de emergência (soft delete)."""
    result = await service.delete(contact_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado",
        )


# ========== Action Endpoints ==========


@router.post(
    "/{contact_id}/set-primary",
    response_model=EmergencyContactResponse,
    summary="Definir como principal",
)
async def set_emergency_contact_primary(
    contact_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Define contato como principal."""
    contact = await service.set_as_primary(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado",
        )
    return contact


@router.post(
    "/{contact_id}/deactivate",
    response_model=EmergencyContactResponse,
    summary="Desativar contato",
)
async def deactivate_emergency_contact(
    contact_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desativa um contato de emergência."""
    contact = await service.deactivate(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado",
        )
    return contact


@router.post(
    "/{contact_id}/activate",
    response_model=EmergencyContactResponse,
    summary="Ativar contato",
)
async def activate_emergency_contact(
    contact_id: UUID,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Ativa um contato de emergência."""
    contact = await service.activate(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado",
        )
    return contact


@router.put(
    "/{contact_id}/priority/{priority}",
    response_model=EmergencyContactResponse,
    summary="Atualizar prioridade",
)
async def update_emergency_contact_priority(
    contact_id: UUID,
    priority: int,
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza prioridade do contato."""
    try:
        contact = await service.update_priority(contact_id, priority)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contato não encontrado",
            )
        return contact
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/reorder/{resident_id}",
    response_model=list[EmergencyContactResponse],
    summary="Reordenar prioridades",
)
async def reorder_emergency_contacts_priorities(
    resident_id: UUID,
    contact_ids: list[str],
    service: EmergencyContactService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Reordena prioridades dos contatos."""
    return await service.reorder_priorities(resident_id, contact_ids)
