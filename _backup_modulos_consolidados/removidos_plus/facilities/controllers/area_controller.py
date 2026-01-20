"""
Controller FastAPI para Area.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.facilities.models.area import AreaStatus, AreaType
from modules.facilities.repositories.area_repository import AreaRepository
from modules.facilities.schemas.area import (
    AreaCreate,
    AreaFilter,
    AreaListResponse,
    AreaResponse,
    AreaStats,
    AreaUpdate,
)

router = APIRouter(prefix="/areas", tags=["Areas"])


@router.post("/", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
async def create_area(
    data: AreaCreate,
    db: AsyncSession = Depends(get_db),
) -> AreaResponse:
    """Cria uma nova área."""
    repo = AreaRepository(db)
    area = await repo.create(data)
    logger.info(f"Área criada: {area.id}")
    return AreaResponse.model_validate(area)


@router.get("/", response_model=AreaListResponse)
async def list_areas(
    search: Optional[str] = Query(None, description="Busca por nome ou código"),
    area_type: Optional[AreaType] = Query(None, description="Tipo de área"),
    area_status: Optional[AreaStatus] = Query(None, alias="status", description="Status"),
    parent_id: Optional[str] = Query(None, description="ID da área pai"),
    client_id: Optional[str] = Query(None, description="ID do cliente"),
    condominium_id: Optional[str] = Query(None, description="ID do condomínio"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: AsyncSession = Depends(get_db),
) -> AreaListResponse:
    """Lista áreas com filtros e paginação."""
    repo = AreaRepository(db)
    filters = AreaFilter(
        search=search,
        area_type=area_type,
        status=area_status,
        parent_id=parent_id,
        client_id=client_id,
        condominium_id=condominium_id,
    )
    areas, total = await repo.list(filters, page, page_size)

    total_pages = (total + page_size - 1) // page_size

    return AreaListResponse(
        items=[AreaResponse.model_validate(a) for a in areas],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=AreaStats)
async def get_area_stats(
    client_id: Optional[str] = Query(None, description="ID do cliente"),
    condominium_id: Optional[str] = Query(None, description="ID do condomínio"),
    db: AsyncSession = Depends(get_db),
) -> AreaStats:
    """Obtém estatísticas de áreas."""
    repo = AreaRepository(db)
    return await repo.get_stats(client_id, condominium_id)


@router.get("/{area_id}", response_model=AreaResponse)
async def get_area(
    area_id: str,
    db: AsyncSession = Depends(get_db),
) -> AreaResponse:
    """Obtém uma área por ID."""
    repo = AreaRepository(db)
    area = await repo.get_by_id(area_id)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área não encontrada",
        )
    return AreaResponse.model_validate(area)


@router.patch("/{area_id}", response_model=AreaResponse)
async def update_area(
    area_id: str,
    data: AreaUpdate,
    db: AsyncSession = Depends(get_db),
) -> AreaResponse:
    """Atualiza uma área."""
    repo = AreaRepository(db)
    area = await repo.update(area_id, data)
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área não encontrada",
        )
    return AreaResponse.model_validate(area)


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_area(
    area_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma área (soft delete)."""
    repo = AreaRepository(db)
    deleted = await repo.delete(area_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área não encontrada",
        )


@router.get("/{area_id}/children", response_model=list[AreaResponse])
async def get_area_children(
    area_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[AreaResponse]:
    """Obtém subáreas de uma área."""
    repo = AreaRepository(db)
    children = await repo.get_children(area_id)
    return [AreaResponse.model_validate(c) for c in children]


@router.get("/{area_id}/hierarchy", response_model=list[AreaResponse])
async def get_area_hierarchy(
    area_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[AreaResponse]:
    """Obtém hierarquia (ancestrais) de uma área."""
    repo = AreaRepository(db)
    hierarchy = await repo.get_hierarchy(area_id)
    return [AreaResponse.model_validate(h) for h in hierarchy]
