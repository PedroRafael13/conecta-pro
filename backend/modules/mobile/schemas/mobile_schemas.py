"""Schemas gerais do módulo mobile."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QuickAction(BaseModel):
    """Ação rápida no mobile."""

    id: str
    label: str
    icon: str
    action: str
    route: str | None = None
    params: dict[str, Any] = {}
    badge_count: int = 0
    enabled: bool = True

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    """Resumo do dashboard."""

    total_leads: int = 0
    total_customers: int = 0
    total_orders: int = 0
    total_revenue: float = 0.0
    pending_tasks: int = 0
    unread_notifications: int = 0
    period_start: datetime | None = None
    period_end: datetime | None = None

    model_config = {"from_attributes": True}


class RecentActivity(BaseModel):
    """Atividade recente."""

    id: str
    type: str
    title: str
    description: str
    icon: str
    timestamp: datetime
    entity_type: str | None = None
    entity_id: str | None = None
    action_url: str | None = None

    model_config = {"from_attributes": True}


class LightweightChart(BaseModel):
    """Gráfico otimizado para mobile."""

    id: str
    title: str
    type: str = Field(..., description="line, bar, pie, area")
    data: list[dict[str, Any]]
    labels: list[str]
    colors: list[str] = []
    total: float | None = None
    trend: float | None = None
    trend_direction: str | None = None

    model_config = {"from_attributes": True}


class MobileDashboardResponse(BaseModel):
    """Dashboard otimizado para mobile."""

    summary: DashboardSummary
    recent_activities: list[RecentActivity] = []
    quick_actions: list[QuickAction] = []
    charts: dict[str, LightweightChart] | None = None
    last_updated: datetime
    cache_expires_at: datetime

    model_config = {"from_attributes": True}


class ModuleOfflineData(BaseModel):
    """Dados offline de um módulo."""

    module: str
    records: list[dict[str, Any]]
    total_count: int
    last_modified: datetime
    version: int
    sync_priority: int = Field(default=0, description="Prioridade de sincronização")

    model_config = {"from_attributes": True}


class UserProfileOffline(BaseModel):
    """Perfil do usuário para offline."""

    id: int
    name: str
    email: str
    avatar_url: str | None = None
    role: str
    permissions: list[str] = []
    preferences: dict[str, Any] = {}

    model_config = {"from_attributes": True}


class OfflineDataResponse(BaseModel):
    """Dados para funcionamento offline."""

    user_profile: UserProfileOffline
    essential_data: dict[str, ModuleOfflineData] = {}
    last_sync: datetime
    sync_token: str
    cache_expires_at: datetime
    total_size_bytes: int = 0
    modules_available: list[str] = []

    model_config = {"from_attributes": True}


class MobileFeature(BaseModel):
    """Feature disponível no mobile."""

    id: str
    name: str
    enabled: bool = True
    min_app_version: str | None = None
    config: dict[str, Any] = {}

    model_config = {"from_attributes": True}


class MobileConfigResponse(BaseModel):
    """Configuração do app mobile."""

    api_version: str = "1.0.0"
    min_app_version: str = "1.0.0"
    force_update: bool = False
    update_url: str | None = None
    maintenance_mode: bool = False
    maintenance_message: str | None = None
    features: list[MobileFeature] = []
    sync_config: dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_sync_enabled": True,
            "sync_interval_seconds": 300,
            "max_offline_days": 7,
            "max_cache_size_mb": 100,
        }
    )
    push_config: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "topics": ["general", "alerts"],
        }
    )
    analytics_config: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "sample_rate": 1.0,
        }
    )

    model_config = {"from_attributes": True}


class HealthCheckResponse(BaseModel):
    """Health check do serviço mobile."""

    status: str = "healthy"
    service: str = "mobile-api"
    version: str
    timestamp: datetime
    components: dict[str, str] = {}

    model_config = {"from_attributes": True}
