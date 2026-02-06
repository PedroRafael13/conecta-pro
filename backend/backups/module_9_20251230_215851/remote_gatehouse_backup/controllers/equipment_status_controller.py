"""
Controller FastAPI para EquipmentStatus.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.logging import logger
from modules.remote_gatehouse.models.equipment_status import EquipmentStatusType
from modules.remote_gatehouse.repositories.equipment_status_repository import (
    EquipmentStatusRepository,
)
from modules.remote_gatehouse.schemas.equipment_status import (
    EquipmentStatusCreate,
    EquipmentStatusFilter,
    EquipmentStatusListResponse,
    EquipmentStatusResponse,
    EquipmentStatusStats,
    EquipmentStatusUpdate,
)

router = APIRouter(prefix="/guardian/equipment-status", tags=["EquipmentStatus"])


@router.post(
    "/",
    response_model=EquipmentStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_equipment_status(
    data: EquipmentStatusCreate,
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Cria um novo status de equipamento (recebido do Guardian)."""
    repo = EquipmentStatusRepository(db)

    # Verificar se já existe
    existing = await repo.get_by_guardian_id(data.guardian_id)
    if existing:
        # Atualizar ao invés de criar
        update_data = EquipmentStatusUpdate(
            status=data.status,
            status_message=data.status_message,
            last_ping_at=data.last_ping_at,
            ping_latency_ms=data.ping_latency_ms,
            metrics=data.metrics,
            has_alerts=data.has_alerts,
            active_alerts=data.active_alerts,
        )
        equipment = await repo.update_by_guardian_id(data.guardian_id, update_data)
        logger.info(f"Status de equipamento atualizado: {equipment.equipment_name}")
        return EquipmentStatusResponse.model_validate(equipment)

    equipment = await repo.create(data)
    logger.info(f"Status de equipamento criado: {equipment.equipment_name}")
    return EquipmentStatusResponse.model_validate(equipment)


@router.get("/", response_model=EquipmentStatusListResponse)
async def list_equipment_status(
    search: Optional[str] = Query(None),
    equipment_type: Optional[str] = Query(None),
    equipment_status: Optional[EquipmentStatusType] = Query(None, alias="status"),
    client_id: Optional[str] = Query(None),
    post_id: Optional[str] = Query(None),
    is_online: Optional[bool] = Query(None),
    has_alerts: Optional[bool] = Query(None),
    has_issues: Optional[bool] = Query(None),
    needs_maintenance: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusListResponse:
    """Lista status de equipamentos com filtros e paginação."""
    repo = EquipmentStatusRepository(db)
    filters = EquipmentStatusFilter(
        search=search,
        equipment_type=equipment_type,
        status=equipment_status,
        client_id=client_id,
        post_id=post_id,
        is_online=is_online,
        has_alerts=has_alerts,
        has_issues=has_issues,
        needs_maintenance=needs_maintenance,
    )
    equipments, total = await repo.list(filters, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return EquipmentStatusListResponse(
        items=[EquipmentStatusResponse.model_validate(e) for e in equipments],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=EquipmentStatusStats)
async def get_equipment_stats(
    client_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusStats:
    """Obtém estatísticas de equipamentos."""
    repo = EquipmentStatusRepository(db)
    return await repo.get_stats(client_id)


@router.get("/offline")
async def get_offline_equipment(
    client_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[EquipmentStatusResponse]:
    """Obtém equipamentos offline."""
    repo = EquipmentStatusRepository(db)
    equipments = await repo.get_offline(client_id, limit)
    return [EquipmentStatusResponse.model_validate(e) for e in equipments]


@router.get("/with-alerts")
async def get_equipment_with_alerts(
    client_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[EquipmentStatusResponse]:
    """Obtém equipamentos com alertas ativos."""
    repo = EquipmentStatusRepository(db)
    equipments = await repo.get_with_alerts(client_id, limit)
    return [EquipmentStatusResponse.model_validate(e) for e in equipments]


@router.get("/needs-maintenance")
async def get_equipment_needs_maintenance(
    days_ahead: int = Query(7, ge=1, le=90),
    client_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[EquipmentStatusResponse]:
    """Obtém equipamentos que precisam de manutenção."""
    repo = EquipmentStatusRepository(db)
    equipments = await repo.get_needs_maintenance(days_ahead, client_id)
    return [EquipmentStatusResponse.model_validate(e) for e in equipments]


@router.get("/{equipment_id}", response_model=EquipmentStatusResponse)
async def get_equipment_status(
    equipment_id: str,
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Obtém status de um equipamento por ID."""
    repo = EquipmentStatusRepository(db)
    equipment = await repo.get_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )
    return EquipmentStatusResponse.model_validate(equipment)


@router.patch("/{equipment_id}", response_model=EquipmentStatusResponse)
async def update_equipment_status(
    equipment_id: str,
    data: EquipmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Atualiza status de um equipamento."""
    repo = EquipmentStatusRepository(db)
    equipment = await repo.update(equipment_id, data)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )
    logger.info(f"Status de equipamento atualizado: {equipment.equipment_name}")
    return EquipmentStatusResponse.model_validate(equipment)


@router.post("/{equipment_id}/set-online", response_model=EquipmentStatusResponse)
async def set_equipment_online(
    equipment_id: str,
    latency_ms: Optional[int] = Query(None, ge=0),
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Marca equipamento como online."""
    repo = EquipmentStatusRepository(db)
    equipment = await repo.get_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )

    equipment.set_online(latency_ms)
    await repo.db.commit()
    await repo.db.refresh(equipment)

    logger.info(f"Equipamento online: {equipment.equipment_name}")
    return EquipmentStatusResponse.model_validate(equipment)


@router.post("/{equipment_id}/set-offline", response_model=EquipmentStatusResponse)
async def set_equipment_offline(
    equipment_id: str,
    reason: Optional[str] = Query(None, max_length=255),
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Marca equipamento como offline."""
    repo = EquipmentStatusRepository(db)
    equipment = await repo.get_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )

    equipment.set_offline(reason)
    await repo.db.commit()
    await repo.db.refresh(equipment)

    logger.warning(f"Equipamento offline: {equipment.equipment_name}")
    return EquipmentStatusResponse.model_validate(equipment)


@router.post("/{equipment_id}/add-alert", response_model=EquipmentStatusResponse)
async def add_equipment_alert(
    equipment_id: str,
    alert_type: str = Query(..., description="Tipo do alerta"),
    alert_message: str = Query(..., description="Mensagem do alerta"),
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Adiciona um alerta ao equipamento."""
    repo = EquipmentStatusRepository(db)
    equipment = await repo.get_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )

    equipment.add_alert({
        "type": alert_type,
        "message": alert_message,
        "created_at": datetime.utcnow().isoformat(),
    })
    await repo.db.commit()
    await repo.db.refresh(equipment)

    logger.warning(f"Alerta adicionado ao equipamento: {equipment.equipment_name}")
    return EquipmentStatusResponse.model_validate(equipment)


@router.post("/{equipment_id}/clear-alerts", response_model=EquipmentStatusResponse)
async def clear_equipment_alerts(
    equipment_id: str,
    db: AsyncSession = Depends(get_db),
) -> EquipmentStatusResponse:
    """Limpa alertas do equipamento."""
    repo = EquipmentStatusRepository(db)
    equipment = await repo.get_by_id(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )

    equipment.clear_alerts()
    await repo.db.commit()
    await repo.db.refresh(equipment)

    logger.info(f"Alertas limpos do equipamento: {equipment.equipment_name}")
    return EquipmentStatusResponse.model_validate(equipment)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment_status(
    equipment_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove um status de equipamento (soft delete)."""
    repo = EquipmentStatusRepository(db)
    deleted = await repo.delete(equipment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipamento não encontrado",
        )
