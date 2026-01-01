"""
Schemas Pydantic para o módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""
# pylint: disable=too-few-public-methods

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# ==================== Tenant Schemas ====================

class TenantBase(BaseModel):
    """Schema base para Tenant."""
    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=1, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = None
    tenant_type: str = Field(default="empresa")
    cnpj: Optional[str] = Field(None, max_length=18)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)


class TenantCreate(TenantBase):
    """Schema para criação de Tenant."""
    plan: str = Field(default="free")
    max_usuarios: int = Field(default=5, ge=1)
    max_storage_gb: int = Field(default=1, ge=1)
    trial_days: Optional[int] = Field(default=14, ge=0)


class TenantUpdate(BaseModel):
    """Schema para atualização de Tenant."""
    nome: Optional[str] = Field(None, max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)
    tema: Optional[Dict[str, Any]] = None


class TenantPlanUpdate(BaseModel):
    """Schema para atualização de plano."""
    plan: str
    max_usuarios: Optional[int] = Field(None, ge=1)
    max_storage_gb: Optional[int] = Field(None, ge=1)
    max_api_calls_month: Optional[int] = Field(None, ge=1000)


class TenantAddressUpdate(BaseModel):
    """Schema para atualização de endereço."""
    logradouro: str = Field(..., max_length=200)
    numero: str = Field(..., max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: str = Field(..., max_length=100)
    cidade: str = Field(..., max_length=100)
    estado: str = Field(..., max_length=2)
    cep: str = Field(..., max_length=10)


class TenantResponse(TenantBase):
    """Schema de resposta para Tenant."""
    id: UUID
    status: str
    plan: str
    max_usuarios: int
    max_storage_gb: int
    max_api_calls_month: int
    usuarios_ativos: int
    storage_usado_mb: int
    api_calls_mes: int
    dominio_personalizado: Optional[str]
    subdominio: Optional[str]
    logo_url: Optional[str]
    data_inicio: Optional[datetime]
    trial_ends_at: Optional[datetime]
    features_enabled: Optional[List[str]]
    modules_enabled: Optional[List[str]]
    ativo: bool
    created_at: datetime

    class Config:
        """Configuração do schema."""
        from_attributes = True


class TenantList(BaseModel):
    """Schema para listagem de Tenants."""
    items: List[TenantResponse]
    total: int
    skip: int
    limit: int


class TenantFilter(BaseModel):
    """Schema para filtro de Tenants."""
    status: Optional[str] = None
    plan: Optional[str] = None
    tenant_type: Optional[str] = None
    search: Optional[str] = None


# ==================== TenantSettings Schemas ====================

class TenantSettingsBase(BaseModel):
    """Schema base para TenantSettings."""
    chave: str = Field(..., max_length=100)
    nome: str = Field(..., max_length=200)
    descricao: Optional[str] = None
    category: str = Field(default="geral")
    setting_type: str = Field(default="string")


class TenantSettingsCreate(TenantSettingsBase):
    """Schema para criação de TenantSettings."""
    tenant_id: UUID
    valor: Optional[str] = None
    valor_default: Optional[str] = None
    required: bool = False
    visible: bool = True
    editable: bool = True
    group: Optional[str] = None


class TenantSettingsUpdate(BaseModel):
    """Schema para atualização de TenantSettings."""
    valor: Optional[str] = None
    nome: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = None
    visible: Optional[bool] = None
    editable: Optional[bool] = None


class TenantSettingsValueUpdate(BaseModel):
    """Schema para atualização de valor."""
    valor: Any


class TenantSettingsResponse(TenantSettingsBase):
    """Schema de resposta para TenantSettings."""
    id: UUID
    tenant_id: UUID
    valor: Optional[str]
    valor_default: Optional[str]
    required: bool
    visible: bool
    editable: bool
    group: Optional[str]
    display_order: int
    sensitive: bool
    last_modified_at: Optional[datetime]
    ativo: bool
    created_at: datetime

    class Config:
        """Configuração do schema."""
        from_attributes = True


class TenantSettingsList(BaseModel):
    """Schema para listagem de TenantSettings."""
    items: List[TenantSettingsResponse]
    total: int


class TenantSettingsFilter(BaseModel):
    """Schema para filtro de TenantSettings."""
    category: Optional[str] = None
    group: Optional[str] = None
    visible: Optional[bool] = None


# ==================== SystemConfig Schemas ====================

class SystemConfigBase(BaseModel):
    """Schema base para SystemConfig."""
    chave: str = Field(..., max_length=100)
    nome: str = Field(..., max_length=200)
    descricao: Optional[str] = None
    scope: str = Field(default="global")
    valor_type: str = Field(default="string")


class SystemConfigCreate(SystemConfigBase):
    """Schema para criação de SystemConfig."""
    valor: Optional[str] = None
    priority: str = Field(default="normal")
    cacheable: bool = True
    cache_ttl_seconds: int = Field(default=3600, ge=0)
    override_allowed: bool = True
    admin_only: bool = False
    category: Optional[str] = None
    group: Optional[str] = None


class SystemConfigUpdate(BaseModel):
    """Schema para atualização de SystemConfig."""
    valor: Optional[str] = None
    nome: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = None
    cacheable: Optional[bool] = None
    cache_ttl_seconds: Optional[int] = Field(None, ge=0)
    visible: Optional[bool] = None
    editable: Optional[bool] = None


class SystemConfigValueUpdate(BaseModel):
    """Schema para atualização de valor."""
    valor: Any


class SystemConfigResponse(SystemConfigBase):
    """Schema de resposta para SystemConfig."""
    id: UUID
    valor: Optional[str]
    priority: str
    cacheable: bool
    cache_ttl_seconds: int
    requires_restart: bool
    override_allowed: bool
    admin_only: bool
    category: Optional[str]
    group: Optional[str]
    display_order: int
    visible: bool
    editable: bool
    version: int
    last_modified_at: Optional[datetime]
    ativo: bool
    created_at: datetime

    class Config:
        """Configuração do schema."""
        from_attributes = True


class SystemConfigList(BaseModel):
    """Schema para listagem de SystemConfig."""
    items: List[SystemConfigResponse]
    total: int


class SystemConfigFilter(BaseModel):
    """Schema para filtro de SystemConfig."""
    scope: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    admin_only: Optional[bool] = None


# ==================== FeatureFlag Schemas ====================

class FeatureFlagBase(BaseModel):
    """Schema base para FeatureFlag."""
    codigo: str = Field(..., max_length=100)
    nome: str = Field(..., max_length=200)
    descricao: Optional[str] = None
    flag_type: str = Field(default="release")


class FeatureFlagCreate(FeatureFlagBase):
    """Schema para criação de FeatureFlag."""
    status: str = Field(default="inativo")
    rollout_strategy: str = Field(default="none")
    rollout_percentage: float = Field(default=0, ge=0, le=100)
    category: Optional[str] = None
    owner_team: Optional[str] = None
    jira_ticket: Optional[str] = None


class FeatureFlagUpdate(BaseModel):
    """Schema para atualização de FeatureFlag."""
    nome: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = None
    category: Optional[str] = None
    owner_team: Optional[str] = None
    jira_ticket: Optional[str] = None
    documentation_url: Optional[str] = None


class FeatureFlagRolloutUpdate(BaseModel):
    """Schema para atualização de rollout."""
    rollout_strategy: str
    rollout_percentage: Optional[float] = Field(None, ge=0, le=100)


class FeatureFlagGradualRollout(BaseModel):
    """Schema para rollout gradual."""
    start_percentage: float = Field(..., ge=0, le=100)
    end_percentage: float = Field(..., ge=0, le=100)
    duration_days: int = Field(..., ge=1, le=365)


class FeatureFlagTenantToggle(BaseModel):
    """Schema para toggle de tenant."""
    tenant_id: str
    enabled: bool


class FeatureFlagUserToggle(BaseModel):
    """Schema para toggle de usuário."""
    user_id: str
    enabled: bool


class FeatureFlagEvaluate(BaseModel):
    """Schema para avaliação de flag."""
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class FeatureFlagEvaluateResponse(BaseModel):
    """Schema de resposta para avaliação."""
    enabled: bool
    variant: Optional[str] = None


class FeatureFlagResponse(FeatureFlagBase):
    """Schema de resposta para FeatureFlag."""
    id: UUID
    status: str
    rollout_strategy: str
    rollout_percentage: float
    enabled_tenants: Optional[List[str]]
    disabled_tenants: Optional[List[str]]
    enabled_users: Optional[List[str]]
    disabled_users: Optional[List[str]]
    gradual_start_date: Optional[datetime]
    gradual_end_date: Optional[datetime]
    variants: Optional[List[Dict[str, Any]]]
    scheduled_enable_at: Optional[datetime]
    scheduled_disable_at: Optional[datetime]
    expires_at: Optional[datetime]
    evaluation_count: int
    enabled_count: int
    disabled_count: int
    category: Optional[str]
    owner_team: Optional[str]
    ativo: bool
    created_at: datetime

    class Config:
        """Configuração do schema."""
        from_attributes = True


class FeatureFlagList(BaseModel):
    """Schema para listagem de FeatureFlag."""
    items: List[FeatureFlagResponse]
    total: int
    skip: int
    limit: int


class FeatureFlagFilter(BaseModel):
    """Schema para filtro de FeatureFlag."""
    status: Optional[str] = None
    flag_type: Optional[str] = None
    category: Optional[str] = None
    owner_team: Optional[str] = None


# ==================== NotificationTemplate Schemas ====================

class NotificationTemplateBase(BaseModel):
    """Schema base para NotificationTemplate."""
    codigo: str = Field(..., max_length=100)
    nome: str = Field(..., max_length=200)
    descricao: Optional[str] = None
    channel: str = Field(default="email")
    notification_type: str = Field(default="transacional")


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schema para criação de NotificationTemplate."""
    tenant_id: Optional[UUID] = None
    email_subject: Optional[str] = Field(None, max_length=500)
    email_body_html: Optional[str] = None
    email_body_text: Optional[str] = None
    sms_body: Optional[str] = None
    push_title: Optional[str] = Field(None, max_length=200)
    push_body: Optional[str] = None
    in_app_title: Optional[str] = Field(None, max_length=200)
    in_app_body: Optional[str] = None
    language: str = Field(default="pt-BR")
    category: Optional[str] = None


class NotificationTemplateUpdate(BaseModel):
    """Schema para atualização de NotificationTemplate."""
    nome: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = None
    email_subject: Optional[str] = Field(None, max_length=500)
    email_body_html: Optional[str] = None
    email_body_text: Optional[str] = None
    sms_body: Optional[str] = None
    push_title: Optional[str] = Field(None, max_length=200)
    push_body: Optional[str] = None
    in_app_title: Optional[str] = Field(None, max_length=200)
    in_app_body: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    category: Optional[str] = None


class NotificationTemplateRender(BaseModel):
    """Schema para renderização de template."""
    variables: Dict[str, Any]


class NotificationTemplateRenderResponse(BaseModel):
    """Schema de resposta para renderização."""
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Schema de resposta para NotificationTemplate."""
    id: UUID
    tenant_id: Optional[UUID]
    status: str
    email_subject: Optional[str]
    email_from_name: Optional[str]
    email_from_address: Optional[str]
    sms_body: Optional[str]
    push_title: Optional[str]
    push_body: Optional[str]
    in_app_title: Optional[str]
    in_app_body: Optional[str]
    available_variables: Optional[List[Dict[str, Any]]]
    language: str
    priority: int
    track_opens: bool
    track_clicks: bool
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    version: int
    category: Optional[str]
    ativo: bool
    created_at: datetime

    class Config:
        """Configuração do schema."""
        from_attributes = True


class NotificationTemplateList(BaseModel):
    """Schema para listagem de NotificationTemplate."""
    items: List[NotificationTemplateResponse]
    total: int
    skip: int
    limit: int


class NotificationTemplateFilter(BaseModel):
    """Schema para filtro de NotificationTemplate."""
    channel: Optional[str] = None
    notification_type: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    tenant_id: Optional[UUID] = None


# ==================== Dashboard Schemas ====================

class ConfigDashboard(BaseModel):
    """Schema para dashboard de configurações."""
    total_tenants: int
    active_tenants: int
    trial_tenants: int
    suspended_tenants: int
    total_configs: int
    total_feature_flags: int
    active_feature_flags: int
    total_notification_templates: int
    recent_tenants: List[Dict[str, Any]]
    feature_flags_stats: Dict[str, Any]


class TenantDashboard(BaseModel):
    """Schema para dashboard do tenant."""
    tenant: TenantResponse
    settings_count: int
    feature_flags_enabled: int
    notification_templates: int
    storage_usage_percent: float
    users_usage_percent: float
    api_usage_percent: float
