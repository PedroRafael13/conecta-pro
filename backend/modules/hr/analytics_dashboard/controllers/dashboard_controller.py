"""Controller para endpoints de Dashboard."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.hr.analytics_dashboard.schemas import (
    DashboardCloneRequest,
    DashboardConfigCreate,
    DashboardConfigResponse,
    DashboardConfigUpdate,
    DashboardListResponse,
    DashboardWidgetCreate,
    DashboardWidgetResponse,
    DashboardWidgetUpdate,
    WidgetBatchPositionUpdate,
    WidgetDataResponse,
)
from modules.hr.analytics_dashboard.services import DashboardService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get("", response_model=list[DashboardListResponse])
async def list_dashboards(
    dashboard_type: str | None = Query(None, description="Filtrar por tipo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista dashboards do usuário."""
    service = DashboardService(db)
    dashboards, _total = await service.list_user_dashboards(
        condominio_id=current_user["condominio_id"],
        user_id=current_user.id,
        user_role=current_user.get("role"),
        dashboard_type=dashboard_type,
        page=page,
        page_size=page_size,
    )
    return dashboards


@router.post("", response_model=DashboardConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    data: DashboardConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cria novo dashboard."""
    service = DashboardService(db)
    dashboard = await service.create_dashboard(
        data=data,
        condominio_id=current_user["condominio_id"],
        owner_id=current_user.id,
    )
    return dashboard


@router.get("/{dashboard_id}", response_model=DashboardConfigResponse)
async def get_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtém dashboard por ID."""
    service = DashboardService(db)
    dashboard = await service.get_dashboard(
        dashboard_id=dashboard_id,
        user_id=current_user.id,
        include_widgets=True,
    )
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard não encontrado",
        )
    return dashboard


@router.patch("/{dashboard_id}", response_model=DashboardConfigResponse)
async def update_dashboard(
    dashboard_id: UUID,
    data: DashboardConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Atualiza dashboard."""
    service = DashboardService(db)
    dashboard = await service.update_dashboard(
        dashboard_id=dashboard_id,
        data=data,
        user_id=current_user.id,
    )
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard não encontrado ou sem permissão",
        )
    return dashboard


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Deleta dashboard."""
    service = DashboardService(db)
    deleted = await service.delete_dashboard(
        dashboard_id=dashboard_id,
        user_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard não encontrado ou sem permissão",
        )


@router.post("/{dashboard_id}/clone", response_model=DashboardConfigResponse)
async def clone_dashboard(
    dashboard_id: UUID,
    data: DashboardCloneRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Clona dashboard."""
    service = DashboardService(db)
    dashboard = await service.clone_dashboard(
        source_id=dashboard_id,
        new_name=data.new_name,
        user_id=current_user.id,
        include_widgets=data.include_widgets,
    )
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard não encontrado",
        )
    return dashboard


@router.post("/{dashboard_id}/set-default", status_code=status.HTTP_204_NO_CONTENT)
async def set_default_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Define dashboard como padrão."""
    service = DashboardService(db)
    success = await service.set_default_dashboard(
        dashboard_id=dashboard_id,
        user_id=current_user.id,
        condominio_id=current_user["condominio_id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível definir como padrão",
        )


@router.post("/{dashboard_id}/refresh")
async def refresh_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Atualiza dados de todos os widgets."""
    service = DashboardService(db)
    result = await service.refresh_dashboard_data(
        dashboard_id=dashboard_id,
        user_id=current_user.id,
    )
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )
    return result


# ==================== Widget Endpoints ====================


@router.get("/{dashboard_id}/widgets", response_model=list[DashboardWidgetResponse])
async def list_widgets(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista widgets de um dashboard."""
    service = DashboardService(db)
    dashboard = await service.get_dashboard(
        dashboard_id=dashboard_id,
        user_id=current_user.id,
        record_view=False,
    )
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard não encontrado",
        )

    widgets = await service.dashboard_repo.list_widgets(dashboard_id)
    return widgets


@router.post(
    "/{dashboard_id}/widgets",
    response_model=DashboardWidgetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_widget(
    dashboard_id: UUID,
    data: DashboardWidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Adiciona widget ao dashboard."""
    service = DashboardService(db)
    widget = await service.add_widget(
        dashboard_id=dashboard_id,
        data=data,
        user_id=current_user.id,
    )
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard não encontrado ou sem permissão",
        )
    return widget


@router.patch("/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_widget(
    widget_id: UUID,
    data: DashboardWidgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Atualiza widget."""
    service = DashboardService(db)
    widget = await service.update_widget(
        widget_id=widget_id,
        data=data,
        user_id=current_user.id,
    )
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget não encontrado ou sem permissão",
        )
    return widget


@router.delete("/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove widget."""
    service = DashboardService(db)
    deleted = await service.remove_widget(
        widget_id=widget_id,
        user_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget não encontrado ou sem permissão",
        )


@router.put("/{dashboard_id}/widgets/positions", status_code=status.HTTP_204_NO_CONTENT)
async def update_widget_positions(
    dashboard_id: UUID,
    data: WidgetBatchPositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Atualiza posições de múltiplos widgets."""
    service = DashboardService(db)
    positions = [p.model_dump() for p in data.positions]
    success = await service.update_widget_positions(
        dashboard_id=dashboard_id,
        positions=positions,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível atualizar posições",
        )


@router.get("/widgets/{widget_id}/data", response_model=WidgetDataResponse)
async def get_widget_data(
    widget_id: UUID,
    force_refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtém dados de um widget."""
    service = DashboardService(db)
    data = await service.get_widget_data(
        widget_id=widget_id,
        user_id=current_user.id,
        force_refresh=force_refresh,
    )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget não encontrado",
        )
    return data
