"""
Controller FastAPI para Checklist.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.facilities.models.checklist import ChecklistStatus
from modules.facilities.repositories.checklist_repository import ChecklistRepository
from modules.facilities.schemas.checklist import (
    ChecklistClone,
    ChecklistCreate,
    ChecklistFilter,
    ChecklistItemAnswer,
    ChecklistItemCreate,
    ChecklistItemResponse,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistStats,
    ChecklistUpdate,
)

router = APIRouter(prefix="/checklists", tags=["Checklists"])


@router.post("/", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    data: ChecklistCreate,
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Cria um novo checklist."""
    repo = ChecklistRepository(db)
    checklist = await repo.create(data)
    logger.info(f"Checklist criado: {checklist.id}")
    return ChecklistResponse.model_validate(checklist)


@router.get("/", response_model=ChecklistListResponse)
async def list_checklists(
    search: Optional[str] = Query(None),
    checklist_status: Optional[ChecklistStatus] = Query(None, alias="status"),
    is_template: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    inspection_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ChecklistListResponse:
    """Lista checklists com filtros e paginação."""
    repo = ChecklistRepository(db)
    filters = ChecklistFilter(
        search=search,
        status=checklist_status,
        is_template=is_template,
        category=category,
        area_id=area_id,
        inspection_id=inspection_id,
    )
    checklists, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return ChecklistListResponse(
        items=[ChecklistResponse.model_validate(c) for c in checklists],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/templates", response_model=ChecklistListResponse)
async def list_templates(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ChecklistListResponse:
    """Lista templates de checklist."""
    repo = ChecklistRepository(db)
    filters = ChecklistFilter(is_template=True, category=category)
    checklists, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return ChecklistListResponse(
        items=[ChecklistResponse.model_validate(c) for c in checklists],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=ChecklistStats)
async def get_checklist_stats(
    client_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> ChecklistStats:
    """Obtém estatísticas de checklists."""
    repo = ChecklistRepository(db)
    return await repo.get_stats(client_id, area_id)


@router.get("/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(
    checklist_id: str,
    include_items: bool = Query(True, description="Incluir itens"),
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Obtém um checklist por ID."""
    repo = ChecklistRepository(db)
    checklist = await repo.get_by_id(checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )

    response = ChecklistResponse.model_validate(checklist)
    if include_items and checklist.items:
        response.items = [ChecklistItemResponse.model_validate(i) for i in checklist.items]
    return response


@router.patch("/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    checklist_id: str,
    data: ChecklistUpdate,
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Atualiza um checklist."""
    repo = ChecklistRepository(db)
    checklist = await repo.update(checklist_id, data)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )
    return ChecklistResponse.model_validate(checklist)


@router.post("/{checklist_id}/items", response_model=ChecklistItemResponse)
async def add_item(
    checklist_id: str,
    data: ChecklistItemCreate,
    db: AsyncSession = Depends(get_db),
) -> ChecklistItemResponse:
    """Adiciona um item ao checklist."""
    repo = ChecklistRepository(db)
    item = await repo.add_item(checklist_id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )
    return ChecklistItemResponse.model_validate(item)


@router.patch("/{checklist_id}/items/{item_id}", response_model=ChecklistItemResponse)
async def answer_item(
    checklist_id: str,
    item_id: str,
    data: ChecklistItemAnswer,
    answered_by: Optional[str] = Query(None, description="ID do respondente"),
    db: AsyncSession = Depends(get_db),
) -> ChecklistItemResponse:
    """Responde um item do checklist."""
    repo = ChecklistRepository(db)

    # Verificar se checklist existe
    checklist = await repo.get_by_id(checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )

    item = await repo.answer_item(
        item_id=item_id,
        status=data.status,
        answer=data.answer,
        notes=data.notes,
        photos=data.photos,
        answered_by=answered_by,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado",
        )
    return ChecklistItemResponse.model_validate(item)


@router.post("/{checklist_id}/clone", response_model=ChecklistResponse)
async def clone_checklist(
    checklist_id: str,
    data: ChecklistClone,
    created_by: Optional[str] = Query(None, description="ID do criador"),
    db: AsyncSession = Depends(get_db),
) -> ChecklistResponse:
    """Clona um checklist (útil para usar templates)."""
    repo = ChecklistRepository(db)
    checklist = await repo.clone(
        checklist_id=checklist_id,
        new_name=data.name,
        area_id=data.area_id,
        inspection_id=data.inspection_id,
        created_by=created_by,
    )
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )
    return ChecklistResponse.model_validate(checklist)


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove um checklist (soft delete)."""
    repo = ChecklistRepository(db)
    deleted = await repo.delete(checklist_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist não encontrado",
        )
