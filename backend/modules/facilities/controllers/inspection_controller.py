"""
Controller FastAPI para Inspection.
"""

from datetime import date
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.facilities.models.inspection import (
    InspectionResult,
    InspectionStatus,
    InspectionType,
)
from modules.facilities.repositories.inspection_repository import InspectionRepository
from modules.facilities.schemas.inspection import (
    InspectionComplete,
    InspectionCreate,
    InspectionFilter,
    InspectionListResponse,
    InspectionResponse,
    InspectionReview,
    InspectionStart,
    InspectionStats,
    InspectionUpdate,
)
from modules.facilities.services.inspection_analyzer import inspection_analyzer

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.post("/", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    data: InspectionCreate,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Cria uma nova inspeção."""
    repo = InspectionRepository(db)
    inspection = await repo.create(data)
    logger.info(f"Inspeção criada: {inspection.id}")
    return InspectionResponse.model_validate(inspection)


@router.get("/", response_model=InspectionListResponse)
async def list_inspections(  # pylint: disable=too-many-locals
    search: Optional[str] = Query(None),
    inspection_type: Optional[InspectionType] = Query(None, alias="type"),
    inspection_status: Optional[InspectionStatus] = Query(None, alias="status"),
    result: Optional[InspectionResult] = Query(None),
    area_id: Optional[str] = Query(None),
    inspector_id: Optional[str] = Query(None),
    scheduled_start: Optional[date] = Query(None),
    scheduled_end: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> InspectionListResponse:
    """Lista inspeções com filtros e paginação."""
    repo = InspectionRepository(db)
    filters = InspectionFilter(
        search=search,
        inspection_type=inspection_type,
        status=inspection_status,
        result=result,
        area_id=area_id,
        inspector_id=inspector_id,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_end,
    )
    inspections, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return InspectionListResponse(
        items=[InspectionResponse.model_validate(i) for i in inspections],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=InspectionStats)
async def get_inspection_stats(
    client_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> InspectionStats:
    """Obtém estatísticas de inspeções."""
    repo = InspectionRepository(db)
    return await repo.get_stats(client_id, area_id)


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Obtém uma inspeção por ID."""
    repo = InspectionRepository(db)
    inspection = await repo.get_by_id(inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )
    return InspectionResponse.model_validate(inspection)


@router.patch("/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(
    inspection_id: str,
    data: InspectionUpdate,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Atualiza uma inspeção."""
    repo = InspectionRepository(db)
    inspection = await repo.update(inspection_id, data)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )
    return InspectionResponse.model_validate(inspection)


@router.post("/{inspection_id}/start", response_model=InspectionResponse)
async def start_inspection(
    inspection_id: str,
    data: InspectionStart,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Inicia uma inspeção."""
    repo = InspectionRepository(db)
    inspection = await repo.start(
        inspection_id,
        inspector_id=data.inspector_id,
        inspector_name=data.inspector_name,
    )
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )
    return InspectionResponse.model_validate(inspection)


@router.post("/{inspection_id}/complete", response_model=InspectionResponse)
async def complete_inspection(
    inspection_id: str,
    data: InspectionComplete,
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Conclui uma inspeção."""
    repo = InspectionRepository(db)
    inspection = await repo.complete(
        inspection_id,
        result=data.result,
        score=data.score,
        findings=data.findings,
        recommendations=data.recommendations,
        non_conformities=data.non_conformities,
        corrective_actions=data.corrective_actions,
        photos=data.photos,
        next_inspection_date=data.next_inspection_date,
        signature_inspector=data.signature_inspector,
        signature_responsible=data.signature_responsible,
        notes=data.notes,
    )
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )
    return InspectionResponse.model_validate(inspection)


@router.post("/{inspection_id}/review", response_model=InspectionResponse)
async def review_inspection(
    inspection_id: str,
    data: InspectionReview,
    reviewed_by: str = Query(..., description="ID do revisor"),
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    """Revisa uma inspeção."""
    repo = InspectionRepository(db)
    inspection = await repo.review(
        inspection_id,
        reviewed_by=reviewed_by,
        approved=data.approved,
        internal_notes=data.internal_notes,
    )
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )
    return InspectionResponse.model_validate(inspection)


@router.post("/{inspection_id}/analyze")
async def analyze_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Analisa uma inspeção usando IA."""
    repo = InspectionRepository(db)
    inspection = await repo.get_by_id(inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )

    inspection_data = {
        "id": inspection.id,
        "score": inspection.score,
        "items_ok": inspection.items_ok,
        "items_warning": inspection.items_warning,
        "items_critical": inspection.items_critical,
    }

    # Converter itens do checklist se disponíveis
    checklist_items = []
    if inspection.checklists:
        for checklist in inspection.checklists:
            if checklist.items:
                for item in checklist.items:
                    checklist_items.append(
                        {
                            "question": item.question,
                            "category": item.category,
                            "status": item.status,
                            "notes": item.notes,
                            "photos": item.photos,
                            "weight": item.weight,
                        }
                    )

    return inspection_analyzer.analyze_inspection(inspection_data, checklist_items)


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inspection(
    inspection_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma inspeção (soft delete)."""
    repo = InspectionRepository(db)
    deleted = await repo.delete(inspection_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspeção não encontrada",
        )
