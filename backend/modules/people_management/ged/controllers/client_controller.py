"""
Controller de Clientes GED — endpoints REST.

Gerencia condominios e administradoras que recebem kits documentais.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.ged.schemas.client import (
    GedClientCreate,
    GedClientList,
    GedClientResponse,
    GedClientUpdate,
)
from modules.people_management.ged.services.client_service import ClientService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["GED - Clientes"])


class PortalAccessRequest(BaseModel):
    """Schema para habilitar/desabilitar acesso ao portal."""

    enabled: bool = Field(..., description="Habilitar (true) ou desabilitar (false) portal")
    username: str | None = Field(None, max_length=100, description="Login do portal")
    password: str | None = Field(None, min_length=6, description="Senha do portal")


@router.get("", response_model=GedClientList)
async def list_clients(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Offset para paginacao"),
    limit: int = Query(20, ge=1, le=100, description="Registros por pagina"),
    search: str | None = Query(None, description="Buscar por nome, CNPJ ou contato"),
    client_type: str | None = Query(None, description="Filtrar por tipo (condominio, administradora)"),
) -> Any:
    """Lista clientes GED com paginacao e filtros."""
    service = ClientService(db)
    return await service.list_clients(
        skip=skip,
        limit=limit,
        search=search,
        type_filter=client_type,
    )


@router.post("", response_model=GedClientResponse, status_code=201)
async def create_client(
    data: GedClientCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo cliente GED (condominio ou administradora)."""
    service = ClientService(db)
    try:
        result = await service.create_client(data, created_by=current_user.id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{client_id}", response_model=GedClientResponse)
async def get_client(
    client_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um cliente GED pelo ID."""
    service = ClientService(db)
    try:
        return await service.get_client(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{client_id}", response_model=GedClientResponse)
async def update_client(
    client_id: str,
    data: GedClientUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza parcialmente um cliente GED."""
    service = ClientService(db)
    try:
        result = await service.update_client(client_id, data)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove um cliente GED. Nao permite se possuir kits."""
    service = ClientService(db)
    try:
        result = await service.delete_client(client_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{client_id}/portal-access", response_model=GedClientResponse)
async def toggle_portal_access(
    client_id: str,
    data: PortalAccessRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Habilita ou desabilita o acesso ao portal do cliente."""
    service = ClientService(db)
    try:
        password_hash = None
        if data.password:
            password_hash = ClientService._hash_password(data.password)

        result = await service.toggle_portal_access(
            client_id=client_id,
            enabled=data.enabled,
            username=data.username,
            password_hash=password_hash,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
