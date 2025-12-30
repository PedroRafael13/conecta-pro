"""
Controller FastAPI para Maintenance.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.facilities.models.maintenance import (
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.facilities.repositories.maintenance_repository import MaintenanceRepository
from modules.facilities.schemas.maintenance import (
    MaintenanceApprove,
    MaintenanceComplete,
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceListResponse,
    MaintenanceReject,
    MaintenanceResponse,
    MaintenanceStats,
    MaintenanceUpdate,
)
from modules.facilities.services.maintenance_scheduler import maintenance_scheduler

router = APIRouter(prefix="/maintenances", tags=["Maintenances"])


@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Cria uma nova manutenção."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.create(data)
    logger.info(f"Manutenção criada: {maintenance.id}")
    return MaintenanceResponse.model_validate(maintenance)


@router.get("/", response_model=MaintenanceListResponse)
async def list_maintenances(
    search: Optional[str] = Query(None),
    maintenance_type: Optional[MaintenanceType] = Query(None, alias="type"),
    maintenance_status: Optional[MaintenanceStatus] = Query(None, alias="status"),
    priority: Optional[MaintenancePriority] = Query(None),
    area_id: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    is_overdue: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> MaintenanceListResponse:
    """Lista manutenções com filtros e paginação."""
    repo = MaintenanceRepository(db)
    filters = MaintenanceFilter(
        search=search,
        maintenance_type=maintenance_type,
        status=maintenance_status,
        priority=priority,
        area_id=area_id,
        assigned_to=assigned_to,
        is_overdue=is_overdue,
    )
    maintenances, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return MaintenanceListResponse(
        items=[MaintenanceResponse.model_validate(m) for m in maintenances],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=MaintenanceStats)
async def get_maintenance_stats(
    client_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> MaintenanceStats:
    """Obtém estatísticas de manutenções."""
    repo = MaintenanceRepository(db)
    return await repo.get_stats(client_id, area_id)


@router.get("/suggest-schedule")
async def suggest_schedule(
    maintenance_type: MaintenanceType = Query(...),
    equipment_type: str = Query(...),
    last_maintenance: Optional[date] = Query(None),
    priority: MaintenancePriority = Query(default=MaintenancePriority.MEDIUM),
) -> dict:
    """Sugere data ideal para manutenção usando IA."""
    return maintenance_scheduler.suggest_schedule(
        maintenance_type=maintenance_type,
        equipment_type=equipment_type,
        last_maintenance=last_maintenance,
        priority=priority,
    )


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
async def get_maintenance(
    maintenance_id: str,
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Obtém uma manutenção por ID."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.get_by_id(maintenance_id)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
    return MaintenanceResponse.model_validate(maintenance)


@router.patch("/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(
    maintenance_id: str,
    data: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Atualiza uma manutenção."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.update(maintenance_id, data)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
    return MaintenanceResponse.model_validate(maintenance)


@router.post("/{maintenance_id}/start", response_model=MaintenanceResponse)
async def start_maintenance(
    maintenance_id: str,
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Inicia uma manutenção."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.start(maintenance_id)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
    return MaintenanceResponse.model_validate(maintenance)


@router.post("/{maintenance_id}/complete", response_model=MaintenanceResponse)
async def complete_maintenance(
    maintenance_id: str,
    data: MaintenanceComplete,
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Conclui uma manutenção."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.complete(
        maintenance_id,
        work_performed=data.work_performed,
        actual_hours=data.actual_hours,
        actual_cost=data.actual_cost,
        labor_cost=data.labor_cost,
        material_cost=data.material_cost,
        materials_used=data.materials_used,
        root_cause=data.root_cause,
        preventive_actions=data.preventive_actions,
        after_photos=data.after_photos,
        notes=data.notes,
    )
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
    return MaintenanceResponse.model_validate(maintenance)


@router.post("/{maintenance_id}/approve", response_model=MaintenanceResponse)
async def approve_maintenance(
    maintenance_id: str,
    data: MaintenanceApprove,
    approved_by: str = Query(..., description="ID do aprovador"),
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Aprova uma manutenção."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.approve(maintenance_id, approved_by, data.notes)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
    return MaintenanceResponse.model_validate(maintenance)


@router.post("/{maintenance_id}/reject", response_model=MaintenanceResponse)
async def reject_maintenance(
    maintenance_id: str,
    data: MaintenanceReject,
    approved_by: str = Query(..., description="ID do rejeitador"),
    db: AsyncSession = Depends(get_db),
) -> MaintenanceResponse:
    """Rejeita uma manutenção."""
    repo = MaintenanceRepository(db)
    maintenance = await repo.reject(maintenance_id, data.rejection_reason, approved_by)
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
    return MaintenanceResponse.model_validate(maintenance)


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(
    maintenance_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove uma manutenção (soft delete)."""
    repo = MaintenanceRepository(db)
    deleted = await repo.delete(maintenance_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manutenção não encontrada",
        )
