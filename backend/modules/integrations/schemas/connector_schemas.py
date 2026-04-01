"""
Schemas para Conectores Externos
Sprint 33: Integration Framework

Schemas Pydantic para API REST de gerenciamento de conectores e sync.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ==================== Connector Info ====================


class ConnectorInfo(BaseModel):
    """Informações de um conector disponível."""

    name: str
    version: str
    display_name: str
    description: str
    supported_entities: list[str]
    auth_type: str
    supports_incremental_sync: bool
    supports_webhooks: bool
    supports_write: bool
    rate_limit_per_second: float
    rate_limit_per_minute: float


class ConnectorListResponse(BaseModel):
    """Lista de conectores disponíveis."""

    connectors: list[ConnectorInfo]
    total: int


# ==================== Integration Account ====================


class IntegrationAccountBase(BaseModel):
    """Base para conta de integração."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    connector_type: str = Field(..., description="Tipo do conector (bling, solides, etc.)")
    environment: str = Field(default="production", description="production ou sandbox")


class IntegrationAccountCreate(IntegrationAccountBase):
    """Schema para criar conta de integração."""

    credentials: dict = Field(..., description="Credenciais (api_key, client_id/secret, etc.)")
    config: dict | None = Field(default=None, description="Configurações adicionais")
    sync_enabled: bool = Field(default=True)
    sync_interval_minutes: int = Field(default=60, ge=5, le=1440)
    sync_entities: list[str] | None = Field(default=None, description="Entidades para sincronizar")


class IntegrationAccountUpdate(BaseModel):
    """Schema para atualizar conta de integração."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    credentials: dict | None = None
    config: dict | None = None
    sync_enabled: bool | None = None
    sync_interval_minutes: int | None = Field(None, ge=5, le=1440)
    sync_entities: list[str] | None = None


class IntegrationAccountResponse(BaseModel):
    """Resposta de conta de integração."""

    id: str
    tenant_id: str
    name: str
    description: str | None
    connector_type: str
    auth_type: str
    environment: str
    status: str
    status_message: str | None
    last_health_check_at: str | None
    last_health_check_status: bool | None
    sync_enabled: bool
    sync_interval_minutes: int
    sync_entities: list[str] | None
    last_sync_at: str | None
    next_sync_at: str | None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class IntegrationAccountList(BaseModel):
    """Lista de contas de integração."""

    items: list[IntegrationAccountResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== Sync Run ====================


class SyncRunCreate(BaseModel):
    """Schema para iniciar sync."""

    account_id: str
    entities: list[str] | None = Field(default=None, description="Entidades específicas ou todas")
    mode: str = Field(default="incremental", description="incremental ou full")


class SyncRunResponse(BaseModel):
    """Resposta de execução de sync."""

    id: str
    account_id: str
    connector_type: str
    mode: str
    status: str
    started_at: str | None
    completed_at: str | None
    items_total: int
    items_processed: int
    items_created: int
    items_updated: int
    items_failed: int
    items_skipped: int = 0
    error_message: str | None
    entity_stats: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class SyncRunList(BaseModel):
    """Lista de execuções de sync."""

    items: list[SyncRunResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SyncRunDetailResponse(SyncRunResponse):
    """Resposta detalhada de execução de sync."""

    entities: list[str] | None
    trigger: str
    triggered_by: str | None
    warnings: list[dict] | None
    errors: list[dict] | None
    duration_seconds: int | None


# ==================== Health Check ====================


class HealthCheckResponse(BaseModel):
    """Resposta de health check."""

    connector: str
    healthy: bool
    latency_ms: int
    message: str
    details: dict | None = None


# ==================== Sync State ====================


class SyncStateResponse(BaseModel):
    """Estado de sincronização de entidade."""

    id: str
    account_id: str
    entity_type: str
    last_sync_at: str | None
    last_sync_cursor: str | None
    last_sync_status: str
    items_synced: int
    items_total: int | None
    error_count: int
    last_error: str | None

    model_config = ConfigDict(from_attributes=True)


class SyncStateList(BaseModel):
    """Lista de estados de sincronização."""

    items: list[SyncStateResponse]
    total: int


# ==================== ID Map ====================


class IDMapResponse(BaseModel):
    """Mapeamento de ID externo para interno."""

    id: str
    account_id: str
    entity_type: str
    external_id: str
    internal_id: str
    internal_table: str
    external_data_hash: str | None
    last_synced_at: str | None
    sync_direction: str
    sync_status: str

    model_config = ConfigDict(from_attributes=True)


class IDMapList(BaseModel):
    """Lista de mapeamentos de ID."""

    items: list[IDMapResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== Statistics ====================


class ConnectorStats(BaseModel):
    """Estatísticas de um conector."""

    connector_type: str
    accounts_total: int
    accounts_active: int
    accounts_error: int
    last_sync_success: str | None
    last_sync_failure: str | None
    items_synced_24h: int
    items_failed_24h: int
    avg_sync_duration_seconds: int | None


class IntegrationStats(BaseModel):
    """Estatísticas gerais de integração."""

    total_accounts: int
    active_accounts: int
    error_accounts: int
    syncs_today: int
    syncs_success_today: int
    syncs_failed_today: int
    items_synced_today: int
    connectors: list[ConnectorStats]


# ==================== Webhook Payload ====================


class WebhookPayloadBase(BaseModel):
    """Base para payload de webhook de conectores."""

    event_type: str
    connector_type: str
    timestamp: datetime
    data: dict


class WebhookSyncCompleted(WebhookPayloadBase):
    """Payload de webhook quando sync é completado."""

    sync_run_id: str
    account_id: str
    mode: str
    status: str
    items_processed: int
    items_created: int
    items_updated: int
    items_failed: int
    duration_seconds: int


class WebhookSyncError(WebhookPayloadBase):
    """Payload de webhook quando sync falha."""

    sync_run_id: str
    account_id: str
    error_type: str
    error_message: str
    retryable: bool
