"""
Schemas para Conectores Externos
Sprint 33: Integration Framework

Schemas Pydantic para API REST de gerenciamento de conectores e sync.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ==================== Connector Info ====================

class ConnectorInfo(BaseModel):
    """Informações de um conector disponível."""
    name: str
    version: str
    display_name: str
    description: str
    supported_entities: List[str]
    auth_type: str
    supports_incremental_sync: bool
    supports_webhooks: bool
    supports_write: bool
    rate_limit_per_second: float
    rate_limit_per_minute: float


class ConnectorListResponse(BaseModel):
    """Lista de conectores disponíveis."""
    connectors: List[ConnectorInfo]
    total: int


# ==================== Integration Account ====================

class IntegrationAccountBase(BaseModel):
    """Base para conta de integração."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    connector_type: str = Field(..., description="Tipo do conector (bling, solides, etc.)")
    environment: str = Field(default="production", description="production ou sandbox")


class IntegrationAccountCreate(IntegrationAccountBase):
    """Schema para criar conta de integração."""
    credentials: dict = Field(..., description="Credenciais (api_key, client_id/secret, etc.)")
    config: Optional[dict] = Field(default=None, description="Configurações adicionais")
    sync_enabled: bool = Field(default=True)
    sync_interval_minutes: int = Field(default=60, ge=5, le=1440)
    sync_entities: Optional[List[str]] = Field(default=None, description="Entidades para sincronizar")


class IntegrationAccountUpdate(BaseModel):
    """Schema para atualizar conta de integração."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    credentials: Optional[dict] = None
    config: Optional[dict] = None
    sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = Field(None, ge=5, le=1440)
    sync_entities: Optional[List[str]] = None


class IntegrationAccountResponse(BaseModel):
    """Resposta de conta de integração."""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    connector_type: str
    auth_type: str
    environment: str
    status: str
    status_message: Optional[str]
    last_health_check_at: Optional[str]
    last_health_check_status: Optional[bool]
    sync_enabled: bool
    sync_interval_minutes: int
    sync_entities: Optional[List[str]]
    last_sync_at: Optional[str]
    next_sync_at: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class IntegrationAccountList(BaseModel):
    """Lista de contas de integração."""
    items: List[IntegrationAccountResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== Sync Run ====================

class SyncRunCreate(BaseModel):
    """Schema para iniciar sync."""
    account_id: str
    entities: Optional[List[str]] = Field(default=None, description="Entidades específicas ou todas")
    mode: str = Field(default="incremental", description="incremental ou full")


class SyncRunResponse(BaseModel):
    """Resposta de execução de sync."""
    id: str
    account_id: str
    connector_type: str
    mode: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    items_total: int
    items_processed: int
    items_created: int
    items_updated: int
    items_failed: int
    items_skipped: int = 0
    error_message: Optional[str]
    entity_stats: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class SyncRunList(BaseModel):
    """Lista de execuções de sync."""
    items: List[SyncRunResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SyncRunDetailResponse(SyncRunResponse):
    """Resposta detalhada de execução de sync."""
    entities: Optional[List[str]]
    trigger: str
    triggered_by: Optional[str]
    warnings: Optional[List[dict]]
    errors: Optional[List[dict]]
    duration_seconds: Optional[int]


# ==================== Health Check ====================

class HealthCheckResponse(BaseModel):
    """Resposta de health check."""
    connector: str
    healthy: bool
    latency_ms: int
    message: str
    details: Optional[dict] = None


# ==================== Sync State ====================

class SyncStateResponse(BaseModel):
    """Estado de sincronização de entidade."""
    id: str
    account_id: str
    entity_type: str
    last_sync_at: Optional[str]
    last_sync_cursor: Optional[str]
    last_sync_status: str
    items_synced: int
    items_total: Optional[int]
    error_count: int
    last_error: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SyncStateList(BaseModel):
    """Lista de estados de sincronização."""
    items: List[SyncStateResponse]
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
    external_data_hash: Optional[str]
    last_synced_at: Optional[str]
    sync_direction: str
    sync_status: str

    model_config = ConfigDict(from_attributes=True)


class IDMapList(BaseModel):
    """Lista de mapeamentos de ID."""
    items: List[IDMapResponse]
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
    last_sync_success: Optional[str]
    last_sync_failure: Optional[str]
    items_synced_24h: int
    items_failed_24h: int
    avg_sync_duration_seconds: Optional[int]


class IntegrationStats(BaseModel):
    """Estatísticas gerais de integração."""
    total_accounts: int
    active_accounts: int
    error_accounts: int
    syncs_today: int
    syncs_success_today: int
    syncs_failed_today: int
    items_synced_today: int
    connectors: List[ConnectorStats]


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
