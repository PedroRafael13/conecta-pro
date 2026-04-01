"""Schemas Pydantic para DashboardConfig."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.analytics_dashboard.models import (
    DashboardType,
    DashboardVisibility,
    RefreshInterval,
)


class DashboardConfigBase(BaseModel):
    """Schema base para dashboard."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    dashboard_type: DashboardType = DashboardType.CUSTOM
    visibility: DashboardVisibility = DashboardVisibility.PRIVATE


class DashboardConfigCreate(DashboardConfigBase):
    """Schema para criação de dashboard."""

    slug: str | None = Field(None, max_length=100)
    layout_type: str = Field(default="grid", pattern="^(grid|freeform|tabs)$")
    columns: int = Field(default=12, ge=1, le=24)
    row_height: int = Field(default=100, ge=50, le=500)

    refresh_interval: RefreshInterval = RefreshInterval.MINUTE_15
    auto_refresh: bool = True

    default_period: str = Field(default="last_30_days")
    default_filters: dict | None = None

    theme: str = Field(default="light", pattern="^(light|dark|auto)$")
    color_scheme: dict | None = None

    is_default: bool = False
    is_pinned: bool = False
    is_template: bool = False

    tags: list[str] | None = None
    settings: dict | None = None

    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v, info):
        """Gera slug a partir do nome se não fornecido."""
        if v:
            return v
        name = info.data.get("name", "")
        if name:
            import re  # pylint: disable=import-outside-toplevel

            slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower())
            return slug.strip("-")
        return None


class DashboardConfigUpdate(BaseModel):
    """Schema para atualização de dashboard."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=1000)
    dashboard_type: DashboardType | None = None
    visibility: DashboardVisibility | None = None

    layout_type: str | None = None
    columns: int | None = Field(None, ge=1, le=24)
    row_height: int | None = Field(None, ge=50, le=500)

    refresh_interval: RefreshInterval | None = None
    auto_refresh: bool | None = None

    default_period: str | None = None
    default_filters: dict | None = None

    theme: str | None = None
    color_scheme: dict | None = None
    custom_css: str | None = None

    is_default: bool | None = None
    is_pinned: bool | None = None

    tags: list[str] | None = None
    settings: dict | None = None


class DashboardShare(BaseModel):
    """Schema para compartilhamento de dashboard."""

    user_ids: list[UUID] | None = None
    role_names: list[str] | None = None
    department_ids: list[UUID] | None = None
    visibility: DashboardVisibility | None = None


class DashboardConfigResponse(DashboardConfigBase):
    """Schema de resposta de dashboard."""

    id: UUID
    slug: str
    condominio_id: UUID
    owner_id: UUID

    layout_type: str
    columns: int
    row_height: int

    refresh_interval: str
    auto_refresh: bool

    default_period: str
    default_filters: dict | None = None

    theme: str
    color_scheme: dict | None = None

    is_default: bool
    is_pinned: bool
    is_template: bool
    sort_order: int

    view_count: int
    last_viewed_at: datetime | None = None

    widget_count: int = 0
    is_shared: bool = False

    tags: list[str] | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardListResponse(BaseModel):
    """Schema para lista de dashboards."""

    id: UUID
    name: str
    slug: str
    dashboard_type: str
    visibility: str
    widget_count: int
    is_default: bool
    is_pinned: bool
    view_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class DashboardCloneRequest(BaseModel):
    """Schema para clonar dashboard."""

    new_name: str = Field(..., min_length=1, max_length=100)
    include_widgets: bool = True


class DashboardExport(BaseModel):
    """Schema para exportação de dashboard."""

    dashboard: DashboardConfigResponse
    widgets: list[dict]
    export_date: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"


class DashboardImport(BaseModel):
    """Schema para importação de dashboard."""

    dashboard: DashboardConfigCreate
    widgets: list[dict]
    overwrite_existing: bool = False
