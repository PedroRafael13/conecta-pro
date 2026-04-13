"""Schemas de Dashboard Financeiro."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.financial.bi_dashboard.models.dashboard_config import (
    DashboardLayout,
    DashboardStatus,
    DashboardType,
    RefreshInterval,
)


class DashboardBase(BaseModel):
    """Schema base de Dashboard."""

    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    tipo: str = Field(default="operational")
    layout: str = Field(default="grid")
    refresh_interval: str = Field(default="minute_15")
    is_public: bool = Field(default=False)
    is_default: bool = Field(default=False)
    theme: str | None = Field(default="light", max_length=50)
    primary_color: str | None = Field(default="#1976d2", max_length=20)
    background_color: str | None = Field(default="#ffffff", max_length=20)
    default_period_days: int = Field(default=30, ge=1, le=365)
    default_filters: dict = Field(default_factory=dict)
    available_filters: list = Field(default_factory=list)
    tags: list = Field(default_factory=list)


class DashboardCreate(DashboardBase):
    """Schema para criar Dashboard."""

    codigo: str = Field(..., min_length=1, max_length=50)
    allowed_roles: list = Field(default_factory=list)
    allowed_users: list = Field(default_factory=list)
    custom_css: str | None = None


class DashboardUpdate(BaseModel):
    """Schema para atualizar Dashboard."""

    nome: str | None = Field(None, min_length=1, max_length=200)
    descricao: str | None = Field(None, max_length=2000)
    tipo: DashboardType | None = None
    status: DashboardStatus | None = None
    layout: DashboardLayout | None = None
    refresh_interval: RefreshInterval | None = None
    is_public: bool | None = None
    is_default: bool | None = None
    is_favorite: bool | None = None
    theme: str | None = Field(None, max_length=50)
    primary_color: str | None = Field(None, max_length=20)
    background_color: str | None = Field(None, max_length=20)
    custom_css: str | None = None
    default_period_days: int | None = Field(None, ge=1, le=365)
    default_filters: dict | None = None
    available_filters: list | None = None
    allowed_roles: list | None = None
    allowed_users: list | None = None
    tags: list | None = None


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
    codigo: str | None = None
    status: str = "draft"
    is_favorite: bool = False
    owner_id: UUID | None = None
    allowed_roles: list = Field(default_factory=list)
    allowed_users: list = Field(default_factory=list)
    custom_css: str | None = None
    version: int = 1
    view_count: int = 0
    last_viewed_at: datetime | None = None
    last_modified_at: datetime | None = None
    widget_count: int = 0
    refresh_seconds: int = 900
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None

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

    tipo: DashboardType | None = None
    status: DashboardStatus | None = None
    is_public: bool | None = None
    is_favorite: bool | None = None
    owner_id: UUID | None = None
    search: str | None = Field(None, max_length=200)
    tags: list[str] | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


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
    most_viewed: dict | None = None
    by_type: dict = Field(default_factory=dict)
    by_layout: dict = Field(default_factory=dict)


class DashboardDuplicate(BaseModel):
    """Schema para duplicar Dashboard."""

    novo_nome: str = Field(..., min_length=1, max_length=200)
    novo_codigo: str | None = Field(None, max_length=50)
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
    new_name: str | None = None
