"""Controller para ResidentDependent."""

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.auth.dependencies import get_current_user
from modules.residents.services.dependent_service import DependentService
from modules.residents.schemas.dependent import (
    DependentCreate,
    DependentUpdate,
    DependentFilter,
    DependentResponse,
    DependentListResponse,
    DependentStats,
    DependentBlock,
    DependentSetTemporary,
    DependentAddPickupPerson,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/residents/dependents", tags=["Dependentes de Moradores"])


def get_service(session: AsyncSession = Depends(get_session)) -> DependentService:
    """Retorna instância do service."""
    return DependentService(session)


# ========== CRUD Endpoints ==========


@router.post(
    "/",
    response_model=DependentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar dependente",
)
async def create_dependent(
    data: DependentCreate,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Cria um novo dependente."""
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/",
    response_model=DependentListResponse,
    summary="Listar dependentes",
)
async def list_dependents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    resident_id: Optional[str] = None,
    relationship_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    is_minor: Optional[bool] = None,
    is_employee: Optional[bool] = None,
    has_access: Optional[bool] = None,
    is_blocked: Optional[bool] = None,
    condominium_id: Optional[str] = None,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista dependentes com filtros e paginação."""
    from modules.residents.models.dependent import DependentStatus, RelationshipType

    filters = DependentFilter(
        resident_id=UUID(resident_id) if resident_id else None,
        relationship_type=(
            RelationshipType(relationship_type) if relationship_type else None
        ),
        status=DependentStatus(status_filter) if status_filter else None,
        is_minor=is_minor,
        is_employee=is_employee,
        has_access=has_access,
        is_blocked=is_blocked,
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
    response_model=list[DependentResponse],
    summary="Buscar dependentes",
)
async def search_dependents(
    query: str = Query(..., min_length=2),
    condominium_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca dependentes por termo."""
    return await service.search(query, condominium_id, limit)


@router.get(
    "/stats",
    response_model=DependentStats,
    summary="Estatísticas de dependentes",
)
async def get_dependents_stats(
    condominium_id: Optional[str] = None,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Retorna estatísticas de dependentes."""
    return await service.get_stats(condominium_id)


@router.get(
    "/blocked",
    response_model=list[DependentResponse],
    summary="Listar dependentes bloqueados",
)
async def list_blocked_dependents(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista dependentes bloqueados."""
    return await service.get_blocked(condominium_id, page, page_size)


@router.get(
    "/employees",
    response_model=list[DependentResponse],
    summary="Listar funcionários domésticos",
)
async def list_employee_dependents(
    condominium_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista funcionários domésticos."""
    return await service.get_employees(condominium_id, page, page_size)


@router.get(
    "/temporary-expiring",
    response_model=list[DependentResponse],
    summary="Listar temporários expirando",
)
async def list_temporary_expiring_dependents(
    days: int = Query(30, ge=1, le=365),
    condominium_id: Optional[str] = None,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Lista dependentes temporários expirando."""
    return await service.get_temporary_expiring(days, condominium_id)


@router.get(
    "/by-cpf/{cpf}",
    response_model=DependentResponse,
    summary="Buscar por CPF",
)
async def get_dependent_by_cpf(
    cpf: str,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca dependente por CPF."""
    dependent = await service.get_by_cpf(cpf)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.get(
    "/by-resident/{resident_id}",
    response_model=list[DependentResponse],
    summary="Buscar por morador",
)
async def get_dependents_by_resident(
    resident_id: UUID,
    include_inactive: bool = Query(False),
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca dependentes do morador."""
    return await service.get_by_resident(resident_id, include_inactive)


@router.get(
    "/minors/{resident_id}",
    response_model=list[DependentResponse],
    summary="Buscar menores por morador",
)
async def get_minors_by_resident(
    resident_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca dependentes menores do morador."""
    return await service.get_minors_by_resident(resident_id)


@router.get(
    "/{dependent_id}",
    response_model=DependentResponse,
    summary="Buscar dependente",
)
async def get_dependent(
    dependent_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Busca dependente por ID."""
    dependent = await service.get_by_id(dependent_id)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.put(
    "/{dependent_id}",
    response_model=DependentResponse,
    summary="Atualizar dependente",
)
async def update_dependent(
    dependent_id: UUID,
    data: DependentUpdate,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Atualiza um dependente."""
    try:
        dependent = await service.update(dependent_id, data)
        if not dependent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dependente não encontrado",
            )
        return dependent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{dependent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover dependente",
)
async def delete_dependent(
    dependent_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove um dependente (soft delete)."""
    result = await service.delete(dependent_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )


# ========== Action Endpoints ==========


@router.post(
    "/{dependent_id}/block",
    response_model=DependentResponse,
    summary="Bloquear dependente",
)
async def block_dependent(
    dependent_id: UUID,
    data: DependentBlock,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Bloqueia um dependente."""
    dependent = await service.block(dependent_id, data.reason)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/unblock",
    response_model=DependentResponse,
    summary="Desbloquear dependente",
)
async def unblock_dependent(
    dependent_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desbloqueia um dependente."""
    dependent = await service.unblock(dependent_id)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/deactivate",
    response_model=DependentResponse,
    summary="Desativar dependente",
)
async def deactivate_dependent(
    dependent_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Desativa um dependente."""
    dependent = await service.deactivate(dependent_id)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/activate",
    response_model=DependentResponse,
    summary="Ativar dependente",
)
async def activate_dependent(
    dependent_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Ativa um dependente."""
    dependent = await service.activate(dependent_id)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/set-temporary",
    response_model=DependentResponse,
    summary="Definir como temporário",
)
async def set_dependent_temporary(
    dependent_id: UUID,
    data: DependentSetTemporary,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Define dependente como temporário."""
    try:
        dependent = await service.set_temporary(
            dependent_id, data.valid_from, data.valid_until
        )
        if not dependent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dependente não encontrado",
            )
        return dependent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/{dependent_id}/add-pickup-person",
    response_model=DependentResponse,
    summary="Adicionar pessoa autorizada",
)
async def add_dependent_pickup_person(
    dependent_id: UUID,
    data: DependentAddPickupPerson,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Adiciona pessoa autorizada a buscar o dependente."""
    dependent = await service.add_authorized_pickup(
        dependent_id, data.name, data.phone, data.document
    )
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/remove-pickup-person/{person_name}",
    response_model=DependentResponse,
    summary="Remover pessoa autorizada",
)
async def remove_dependent_pickup_person(
    dependent_id: UUID,
    person_name: str,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Remove pessoa autorizada a buscar o dependente."""
    dependent = await service.remove_authorized_pickup(dependent_id, person_name)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/set-work-schedule",
    response_model=DependentResponse,
    summary="Definir horário de trabalho",
)
async def set_dependent_work_schedule(
    dependent_id: UUID,
    schedule: dict,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Define horário de trabalho para funcionário doméstico."""
    dependent = await service.set_work_schedule(dependent_id, schedule)
    if not dependent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependente não encontrado",
        )
    return dependent


@router.post(
    "/{dependent_id}/validate-access",
    summary="Validar acesso",
)
async def validate_dependent_access(
    dependent_id: UUID,
    service: DependentService = Depends(get_service),
    current_user: dict = Depends(get_current_user),
):
    """Valida se dependente tem acesso."""
    return await service.validate_access(dependent_id)
