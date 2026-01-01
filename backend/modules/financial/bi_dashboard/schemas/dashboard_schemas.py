"""Schemas de Dashboard Financeiro."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.financial.bi_dashboard.models.dashboard_config import (
    DashboardType,
    DashboardStatus,
    DashboardLayout,
    RefreshInterval,
)


class DashboardBase(BaseModel):
    """Schema base de Dashboard."""

    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: DashboardType = Field(default=DashboardType.OPERATIONAL)
    layout: DashboardLayout = Field(default=DashboardLayout.GRID_3X2)
    refresh_interval: RefreshInterval = Field(default=RefreshInterval.MINUTE_15)
    is_public: bool = Field(default=False)
    is_default: bool = Field(default=False)
    theme: str = Field(default="light", max_length=50)
    primary_color: str = Field(default="#1976d2", max_length=20)
    background_color: str = Field(default="#ffffff", max_length=20)
    default_period_days: int = Field(default=30, ge=1, le=365)
    default_filters: dict = Field(default_factory=dict)
    available_filters: list = Field(default_factory=list)
    tags: list = Field(default_factory=list)


class DashboardCreate(DashboardBase):
    """Schema para criar Dashboard."""

    codigo: str = Field(..., min_length=1, max_length=50)
    allowed_roles: list = Field(default_factory=list)
    allowed_users: list = Field(default_factory=list)
    custom_css: Optional[str] = None


class DashboardUpdate(BaseModel):
    """Schema para atualizar Dashboard."""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    tipo: Optional[DashboardType] = None
    status: Optional[DashboardStatus] = None
    layout: Optional[DashboardLayout] = None
    refresh_interval: Optional[RefreshInterval] = None
    is_public: Optional[bool] = None
    is_default: Optional[bool] = None
    is_favorite: Optional[bool] = None
    theme: Optional[str] = Field(None, max_length=50)
    primary_color: Optional[str] = Field(None, max_length=20)
    background_color: Optional[str] = Field(None, max_length=20)
    custom_css: Optional[str] = None
    default_period_days: Optional[int] = Field(None, ge=1, le=365)
    default_filters: Optional[dict] = None
    available_filters: Optional[list] = None
    allowed_roles: Optional[list] = None
    allowed_users: Optional[list] = None
    tags: Optional[list] = None


class WidgetSummary(BaseModel):
    """Resumo de widget para listagem."""

    id: UUID
    codigo: str
    titulo: str
    tipo: str
    tamanho: str

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(DashboardBase):
    """Schema de resposta de Dashboard."""

    id: UUID
    condominio_id: UUID
    codigo: str
    status: DashboardStatus
    is_favorite: bool = False
    owner_id: Optional[UUID] = None
    allowed_roles: list = Field(default_factory=list)
    allowed_users: list = Field(default_factory=list)
    custom_css: Optional[str] = None
    version: int = 1
    view_count: int = 0
    last_viewed_at: Optional[datetime] = None
    last_modified_at: Optional[datetime] = None
    widget_count: int = 0
    refresh_seconds: int = 900
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardListResponse(BaseModel):
    """Schema de lista de Dashboards."""

    items: list[DashboardResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DashboardFilters(BaseModel):
    """Filtros para busca de Dashboards."""

    tipo: Optional[DashboardType] = None
    status: Optional[DashboardStatus] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None
    owner_id: Optional[UUID] = None
    search: Optional[str] = Field(None, max_length=200)
    tags: Optional[list[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class DashboardStats(BaseModel):
    """Estatisticas de Dashboards."""

    total: int = 0
    active: int = 0
    draft: int = 0
    archived: int = 0
    public: int = 0
    private: int = 0
    total_widgets: int = 0
    total_views: int = 0
    most_viewed: Optional[dict] = None
    by_type: dict = Field(default_factory=dict)
    by_layout: dict = Field(default_factory=dict)


class DashboardDuplicate(BaseModel):
    """Schema para duplicar Dashboard."""

    novo_nome: str = Field(..., min_length=1, max_length=200)
    novo_codigo: Optional[str] = Field(None, max_length=50)
    incluir_widgets: bool = Field(default=True)


class DashboardExport(BaseModel):
    """Schema de exportacao de Dashboard."""

    dashboard: dict
    widgets: list[dict]
    kpis: list[dict]
    export_date: datetime
    version: str = "1.0"


class DashboardImport(BaseModel):
    """Schema de importacao de Dashboard."""

    data: dict
    override_existing: bool = Field(default=False)
    new_name: Optional[str] = None
