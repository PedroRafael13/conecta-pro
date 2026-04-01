"""
Schemas Pydantic para o módulo de Integrações
Sprint 32: API Gateway / Integrações
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.integrations.models import (
    APIKeyStatus,
    APIKeyType,
    EndpointCategory,
    EndpointStatus,
    ExternalSystem,
    HTTPMethod,
    LogLevel,
    LogStatus,
    LogType,
    RateLimitType,
    SyncDirection,
    SyncEntityType,
    SyncOperationType,
    SyncPriority,
    SyncStatus,
    WebhookAuthType,
    WebhookEvent,
    WebhookFormat,
    WebhookStatus,
)

# ==================== API Endpoint Schemas ====================


class APIEndpointBase(BaseModel):
    """Schema base para API Endpoint."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    version: str = Field(default="v1", max_length=20)
    path: str = Field(..., min_length=1, max_length=500)
    method: HTTPMethod
    category: EndpointCategory = EndpointCategory.SERVICES

    # Autenticação
    requires_auth: bool = True
    auth_methods: list[str] | None = None
    required_scopes: list[str] | None = None
    required_permissions: list[str] | None = None

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_type: RateLimitType | None = RateLimitType.PER_MINUTE
    rate_limit_value: int | None = 60
    rate_limit_by_key: bool = True

    # Request/Response
    request_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    request_example: dict[str, Any] | None = None
    response_example: dict[str, Any] | None = None
    error_responses: dict[str, Any] | None = None

    # Validação
    request_validation_enabled: bool = True
    response_validation_enabled: bool = False
    max_request_size_bytes: int | None = 1048576

    # Cache
    cache_enabled: bool = False
    cache_ttl_seconds: int | None = None
    cache_key_pattern: str | None = None

    # Configurações
    timeout_seconds: int | None = 30
    retry_enabled: bool = False
    retry_count: int | None = 3
    circuit_breaker_enabled: bool = False

    # Documentação
    documentation_url: str | None = None
    tags: list[str] | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class APIEndpointCreate(APIEndpointBase):
    """Schema para criar API Endpoint."""


class APIEndpointUpdate(BaseModel):
    """Schema para atualizar API Endpoint."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: EndpointStatus | None = None
    requires_auth: bool | None = None
    auth_methods: list[str] | None = None
    required_scopes: list[str] | None = None
    rate_limit_enabled: bool | None = None
    rate_limit_value: int | None = None
    cache_enabled: bool | None = None
    cache_ttl_seconds: int | None = None
    timeout_seconds: int | None = None
    documentation_url: str | None = None
    tags: list[str] | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class APIEndpointResponse(APIEndpointBase):
    """Schema de resposta para API Endpoint."""

    id: UUID
    status: EndpointStatus
    deprecated_at: datetime | None = None
    sunset_date: datetime | None = None
    replacement_endpoint_id: UUID | None = None
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    avg_response_time_ms: int | None = None
    last_called_at: datetime | None = None
    success_rate: float = 100.0
    full_path: str
    ativo: bool
    created_at: datetime
    updated_at: datetime


class APIEndpointList(BaseModel):
    """Schema para listagem de API Endpoints."""

    items: list[APIEndpointResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== API Key Schemas ====================


class APIKeyBase(BaseModel):
    """Schema base para API Key."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    client_id: UUID | None = None
    user_id: UUID | None = None
    key_type: APIKeyType = APIKeyType.PRODUCTION

    # Permissões
    scopes: list[str] | None = None
    allowed_endpoints: list[str] | None = None
    blocked_endpoints: list[str] | None = None

    # Rate Limiting
    rate_limit_per_minute: int | None = 60
    rate_limit_per_hour: int | None = 1000
    rate_limit_per_day: int | None = 10000

    # Restrições de IP
    ip_whitelist: list[str] | None = None
    ip_blacklist: list[str] | None = None

    # Validade
    expires_at: datetime | None = None
    never_expires: bool = False

    # Metadados
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreate(APIKeyBase):
    """Schema para criar API Key."""


class APIKeyCreateResponse(BaseModel):
    """Resposta após criar API Key - inclui a chave em texto."""

    id: UUID
    name: str
    key: str  # A chave completa, só mostrada uma vez
    key_prefix: str
    key_hint: str
    key_type: APIKeyType
    status: APIKeyStatus
    expires_at: datetime | None = None
    created_at: datetime


class APIKeyUpdate(BaseModel):
    """Schema para atualizar API Key."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    scopes: list[str] | None = None
    allowed_endpoints: list[str] | None = None
    blocked_endpoints: list[str] | None = None
    rate_limit_per_minute: int | None = None
    rate_limit_per_hour: int | None = None
    rate_limit_per_day: int | None = None
    ip_whitelist: list[str] | None = None
    ip_blacklist: list[str] | None = None
    expires_at: datetime | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class APIKeyResponse(BaseModel):
    """Schema de resposta para API Key."""

    id: UUID
    name: str
    description: str | None = None
    key_prefix: str
    key_hint: str | None = None
    key_type: APIKeyType
    status: APIKeyStatus
    client_id: UUID | None = None
    user_id: UUID | None = None
    scopes: list[str] | None = None
    rate_limit_per_minute: int | None = None
    rate_limit_per_hour: int | None = None
    rate_limit_per_day: int | None = None
    ip_whitelist: list[str] | None = None
    expires_at: datetime | None = None
    never_expires: bool
    last_used_at: datetime | None = None
    last_used_ip: str | None = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 100.0
    is_valid: bool
    days_until_expiry: int | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyList(BaseModel):
    """Schema para listagem de API Keys."""

    items: list[APIKeyResponse]
    total: int
    page: int
    page_size: int
    pages: int


class APIKeyRevokeRequest(BaseModel):
    """Schema para revogar API Key."""

    reason: str | None = None


# ==================== Webhook Schemas ====================


class WebhookConfigBase(BaseModel):
    """Schema base para Webhook Config."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    url: str = Field(..., min_length=1, max_length=1000)
    method: str = "POST"
    events: list[str]  # Lista de WebhookEvent
    event_filters: dict[str, Any] | None = None

    # Formato
    content_type: str = "application/json"
    payload_format: WebhookFormat = WebhookFormat.JSON
    payload_template: str | None = None

    # Autenticação
    auth_type: WebhookAuthType = WebhookAuthType.HMAC
    auth_credentials: dict[str, Any] | None = None

    # Segurança
    verify_ssl: bool = True
    allowed_ips: list[str] | None = None

    # Headers customizados
    custom_headers: dict[str, str] | None = None

    # Retry
    retry_enabled: bool = True
    max_retries: int = 3
    retry_delay_seconds: int = 60
    retry_backoff_multiplier: int = 2

    # Timeout
    timeout_seconds: int = 30
    connect_timeout_seconds: int = 10

    # Batching
    batch_enabled: bool = False
    batch_size: int | None = 10
    batch_interval_seconds: int | None = 60

    # Configurações
    auto_disable_on_failures: int | None = 10

    # Metadados
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: list[str]) -> list[str]:
        """Valida lista de eventos."""
        if not v:
            raise ValueError("Pelo menos um evento é obrigatório")
        valid_events = [e.value for e in WebhookEvent]
        for event in v:
            if event not in valid_events:
                raise ValueError(f"Evento inválido: {event}")
        return v


class WebhookConfigCreate(WebhookConfigBase):
    """Schema para criar Webhook Config."""

    client_id: UUID | None = None
    api_key_id: UUID | None = None


class WebhookConfigUpdate(BaseModel):
    """Schema para atualizar Webhook Config."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    url: str | None = Field(None, min_length=1, max_length=1000)
    events: list[str] | None = None
    event_filters: dict[str, Any] | None = None
    status: WebhookStatus | None = None
    payload_template: str | None = None
    auth_type: WebhookAuthType | None = None
    auth_credentials: dict[str, Any] | None = None
    verify_ssl: bool | None = None
    custom_headers: dict[str, str] | None = None
    retry_enabled: bool | None = None
    max_retries: int | None = None
    timeout_seconds: int | None = None
    batch_enabled: bool | None = None
    batch_size: int | None = None
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WebhookConfigResponse(WebhookConfigBase):
    """Schema de resposta para Webhook Config."""

    id: UUID
    client_id: UUID | None = None
    api_key_id: UUID | None = None
    status: WebhookStatus
    secret_key: str | None = None  # Mostrado apenas na criação
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    consecutive_failures: int = 0
    avg_response_time_ms: int | None = None
    last_delivery_at: datetime | None = None
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    last_failure_reason: str | None = None
    delivery_rate: float = 100.0
    health_status: str
    is_available: bool
    ativo: bool
    created_at: datetime
    updated_at: datetime


class WebhookConfigList(BaseModel):
    """Schema para listagem de Webhook Configs."""

    items: list[WebhookConfigResponse]
    total: int
    page: int
    page_size: int
    pages: int


class WebhookTestRequest(BaseModel):
    """Schema para testar webhook."""

    event: str
    payload: dict[str, Any] | None = None


class WebhookTestResponse(BaseModel):
    """Resposta do teste de webhook."""

    success: bool
    status_code: int | None = None
    response_time_ms: int
    response_body: str | None = None
    error: str | None = None


# ==================== Integration Log Schemas ====================


class IntegrationLogResponse(BaseModel):
    """Schema de resposta para Integration Log."""

    id: UUID
    endpoint_id: UUID | None = None
    api_key_id: UUID | None = None
    webhook_id: UUID | None = None
    sync_queue_id: UUID | None = None
    log_type: LogType
    level: LogLevel
    status: LogStatus
    correlation_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None
    method: str | None = None
    path: str | None = None
    response_status_code: int | None = None
    duration_ms: int | None = None
    client_ip: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    retry_count: int = 0
    is_retry: bool = False
    user_id: UUID | None = None
    client_id: UUID | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    action: str | None = None
    tags: list[str] | None = None
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntegrationLogList(BaseModel):
    """Schema para listagem de logs."""

    items: list[IntegrationLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class IntegrationLogFilter(BaseModel):
    """Filtros para busca de logs."""

    log_type: LogType | None = None
    level: LogLevel | None = None
    status: LogStatus | None = None
    endpoint_id: UUID | None = None
    api_key_id: UUID | None = None
    webhook_id: UUID | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    client_id: UUID | None = None
    user_id: UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    error_only: bool = False


# ==================== Sync Queue Schemas ====================


class SyncQueueBase(BaseModel):
    """Schema base para Sync Queue."""

    external_system: ExternalSystem = ExternalSystem.CUSTOM
    external_system_config_id: UUID | None = None
    direction: SyncDirection = SyncDirection.OUTBOUND
    entity_type: SyncEntityType
    entity_id: UUID | None = None
    external_id: str | None = None
    operation: SyncOperationType = SyncOperationType.UPSERT
    payload: dict[str, Any] | None = None
    priority: SyncPriority = SyncPriority.NORMAL

    # Agendamento
    scheduled_at: datetime | None = None
    not_before: datetime | None = None
    not_after: datetime | None = None

    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 60
    retry_backoff_multiplier: int = 2

    # Callbacks
    callback_url: str | None = None
    callback_on_success: bool = False
    callback_on_failure: bool = False

    # Metadados
    notes: str | None = None
    tags: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class SyncQueueCreate(SyncQueueBase):
    """Schema para criar item na fila de sync."""

    correlation_id: str | None = None
    batch_id: UUID | None = None


class SyncQueueBatchCreate(BaseModel):
    """Schema para criar múltiplos itens na fila."""

    items: list[SyncQueueCreate]
    batch_id: UUID | None = None


class SyncQueueUpdate(BaseModel):
    """Schema para atualizar item na fila."""

    priority: SyncPriority | None = None
    scheduled_at: datetime | None = None
    not_before: datetime | None = None
    not_after: datetime | None = None
    max_retries: int | None = None
    notes: str | None = None
    tags: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class SyncQueueResponse(SyncQueueBase):
    """Schema de resposta para Sync Queue."""

    id: UUID
    correlation_id: str | None = None
    batch_id: UUID | None = None
    payload_hash: str | None = None
    status: SyncStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    processing_time_ms: int | None = None
    processed_by: str | None = None
    retry_count: int = 0
    next_retry_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None
    external_response: dict[str, Any] | None = None
    external_status_code: int | None = None
    validation_errors: list[dict[str, Any]] | None = None
    requires_review: bool = False
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    is_ready_to_process: bool
    is_expired: bool
    can_retry: bool
    wait_time_seconds: int | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime


class SyncQueueList(BaseModel):
    """Schema para listagem de itens da fila."""

    items: list[SyncQueueResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SyncQueueFilter(BaseModel):
    """Filtros para busca na fila."""

    status: SyncStatus | None = None
    priority: SyncPriority | None = None
    entity_type: SyncEntityType | None = None
    external_system: ExternalSystem | None = None
    direction: SyncDirection | None = None
    batch_id: UUID | None = None
    correlation_id: str | None = None
    requires_review: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    ready_only: bool = False


class SyncQueueStats(BaseModel):
    """Estatísticas da fila de sincronização."""

    total: int = 0
    pending: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0
    retrying: int = 0
    requires_review: int = 0
    by_entity_type: dict[str, int] = Field(default_factory=dict)
    by_external_system: dict[str, int] = Field(default_factory=dict)
    avg_processing_time_ms: int | None = None
    oldest_pending_at: datetime | None = None


# ==================== Dashboard Schemas ====================


class IntegrationDashboard(BaseModel):
    """Dashboard de integrações."""

    # API Stats
    total_endpoints: int = 0
    active_endpoints: int = 0
    deprecated_endpoints: int = 0
    total_api_calls_today: int = 0
    api_success_rate: float = 100.0
    avg_response_time_ms: int | None = None

    # API Keys
    total_api_keys: int = 0
    active_api_keys: int = 0
    expired_api_keys: int = 0
    revoked_api_keys: int = 0

    # Webhooks
    total_webhooks: int = 0
    active_webhooks: int = 0
    failing_webhooks: int = 0
    webhook_delivery_rate: float = 100.0

    # Sync Queue
    sync_stats: SyncQueueStats = Field(default_factory=SyncQueueStats)

    # Recent Errors
    recent_errors: list[IntegrationLogResponse] = Field(default_factory=list)

    # Health
    overall_health: str = "healthy"  # healthy, degraded, critical


class IntegrationHealthCheck(BaseModel):
    """Health check de integrações."""

    api_gateway: str = "healthy"
    webhooks: str = "healthy"
    sync_queue: str = "healthy"
    external_systems: dict[str, str] = Field(default_factory=dict)
    last_check_at: datetime = Field(default_factory=datetime.utcnow)
