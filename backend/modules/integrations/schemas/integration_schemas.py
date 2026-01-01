"""
Schemas Pydantic para o módulo de Integrações
Sprint 32: API Gateway / Integrações
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from modules.integrations.models import (
    HTTPMethod,
    EndpointCategory,
    EndpointStatus,
    RateLimitType,
    APIKeyType,
    APIKeyStatus,
    WebhookEvent,
    WebhookStatus,
    WebhookFormat,
    WebhookAuthType,
    LogType,
    LogLevel,
    LogStatus,
    SyncDirection,
    SyncPriority,
    SyncStatus,
    SyncEntityType,
    SyncOperationType,
    ExternalSystem,
)


# ==================== API Endpoint Schemas ====================

class APIEndpointBase(BaseModel):
    """Schema base para API Endpoint."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    version: str = Field(default="v1", max_length=20)
    path: str = Field(..., min_length=1, max_length=500)
    method: HTTPMethod
    category: EndpointCategory = EndpointCategory.SERVICES

    # Autenticação
    requires_auth: bool = True
    auth_methods: Optional[List[str]] = None
    required_scopes: Optional[List[str]] = None
    required_permissions: Optional[List[str]] = None

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_type: Optional[RateLimitType] = RateLimitType.PER_MINUTE
    rate_limit_value: Optional[int] = 60
    rate_limit_by_key: bool = True

    # Request/Response
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    request_example: Optional[Dict[str, Any]] = None
    response_example: Optional[Dict[str, Any]] = None
    error_responses: Optional[Dict[str, Any]] = None

    # Validação
    request_validation_enabled: bool = True
    response_validation_enabled: bool = False
    max_request_size_bytes: Optional[int] = 1048576

    # Cache
    cache_enabled: bool = False
    cache_ttl_seconds: Optional[int] = None
    cache_key_pattern: Optional[str] = None

    # Configurações
    timeout_seconds: Optional[int] = 30
    retry_enabled: bool = False
    retry_count: Optional[int] = 3
    circuit_breaker_enabled: bool = False

    # Documentação
    documentation_url: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class APIEndpointCreate(APIEndpointBase):
    """Schema para criar API Endpoint."""


class APIEndpointUpdate(BaseModel):
    """Schema para atualizar API Endpoint."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[EndpointStatus] = None
    requires_auth: Optional[bool] = None
    auth_methods: Optional[List[str]] = None
    required_scopes: Optional[List[str]] = None
    rate_limit_enabled: Optional[bool] = None
    rate_limit_value: Optional[int] = None
    cache_enabled: Optional[bool] = None
    cache_ttl_seconds: Optional[int] = None
    timeout_seconds: Optional[int] = None
    documentation_url: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class APIEndpointResponse(APIEndpointBase):
    """Schema de resposta para API Endpoint."""
    id: UUID
    status: EndpointStatus
    deprecated_at: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    replacement_endpoint_id: Optional[UUID] = None
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    avg_response_time_ms: Optional[int] = None
    last_called_at: Optional[datetime] = None
    success_rate: float = 100.0
    full_path: str
    ativo: bool
    created_at: datetime
    updated_at: datetime


class APIEndpointList(BaseModel):
    """Schema para listagem de API Endpoints."""
    items: List[APIEndpointResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== API Key Schemas ====================

class APIKeyBase(BaseModel):
    """Schema base para API Key."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    client_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    key_type: APIKeyType = APIKeyType.PRODUCTION

    # Permissões
    scopes: Optional[List[str]] = None
    allowed_endpoints: Optional[List[str]] = None
    blocked_endpoints: Optional[List[str]] = None

    # Rate Limiting
    rate_limit_per_minute: Optional[int] = 60
    rate_limit_per_hour: Optional[int] = 1000
    rate_limit_per_day: Optional[int] = 10000

    # Restrições de IP
    ip_whitelist: Optional[List[str]] = None
    ip_blacklist: Optional[List[str]] = None

    # Validade
    expires_at: Optional[datetime] = None
    never_expires: bool = False

    # Metadados
    notes: Optional[str] = None

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
    expires_at: Optional[datetime] = None
    created_at: datetime


class APIKeyUpdate(BaseModel):
    """Schema para atualizar API Key."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    allowed_endpoints: Optional[List[str]] = None
    blocked_endpoints: Optional[List[str]] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None
    ip_blacklist: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class APIKeyResponse(BaseModel):
    """Schema de resposta para API Key."""
    id: UUID
    name: str
    description: Optional[str] = None
    key_prefix: str
    key_hint: Optional[str] = None
    key_type: APIKeyType
    status: APIKeyStatus
    client_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    scopes: Optional[List[str]] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    never_expires: bool
    last_used_at: Optional[datetime] = None
    last_used_ip: Optional[str] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 100.0
    is_valid: bool
    days_until_expiry: Optional[int] = None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyList(BaseModel):
    """Schema para listagem de API Keys."""
    items: List[APIKeyResponse]
    total: int
    page: int
    page_size: int
    pages: int


class APIKeyRevokeRequest(BaseModel):
    """Schema para revogar API Key."""
    reason: Optional[str] = None


# ==================== Webhook Schemas ====================

class WebhookConfigBase(BaseModel):
    """Schema base para Webhook Config."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    url: str = Field(..., min_length=1, max_length=1000)
    method: str = "POST"
    events: List[str]  # Lista de WebhookEvent
    event_filters: Optional[Dict[str, Any]] = None

    # Formato
    content_type: str = "application/json"
    payload_format: WebhookFormat = WebhookFormat.JSON
    payload_template: Optional[str] = None

    # Autenticação
    auth_type: WebhookAuthType = WebhookAuthType.HMAC
    auth_credentials: Optional[Dict[str, Any]] = None

    # Segurança
    verify_ssl: bool = True
    allowed_ips: Optional[List[str]] = None

    # Headers customizados
    custom_headers: Optional[Dict[str, str]] = None

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
    batch_size: Optional[int] = 10
    batch_interval_seconds: Optional[int] = 60

    # Configurações
    auto_disable_on_failures: Optional[int] = 10

    # Metadados
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("events")
    @classmethod
    def validate_events(cls, v: List[str]) -> List[str]:
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
    client_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None


class WebhookConfigUpdate(BaseModel):
    """Schema para atualizar Webhook Config."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    url: Optional[str] = Field(None, min_length=1, max_length=1000)
    events: Optional[List[str]] = None
    event_filters: Optional[Dict[str, Any]] = None
    status: Optional[WebhookStatus] = None
    payload_template: Optional[str] = None
    auth_type: Optional[WebhookAuthType] = None
    auth_credentials: Optional[Dict[str, Any]] = None
    verify_ssl: Optional[bool] = None
    custom_headers: Optional[Dict[str, str]] = None
    retry_enabled: Optional[bool] = None
    max_retries: Optional[int] = None
    timeout_seconds: Optional[int] = None
    batch_enabled: Optional[bool] = None
    batch_size: Optional[int] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WebhookConfigResponse(WebhookConfigBase):
    """Schema de resposta para Webhook Config."""
    id: UUID
    client_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    status: WebhookStatus
    secret_key: Optional[str] = None  # Mostrado apenas na criação
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    consecutive_failures: int = 0
    avg_response_time_ms: Optional[int] = None
    last_delivery_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    last_failure_reason: Optional[str] = None
    delivery_rate: float = 100.0
    health_status: str
    is_available: bool
    ativo: bool
    created_at: datetime
    updated_at: datetime


class WebhookConfigList(BaseModel):
    """Schema para listagem de Webhook Configs."""
    items: List[WebhookConfigResponse]
    total: int
    page: int
    page_size: int
    pages: int


class WebhookTestRequest(BaseModel):
    """Schema para testar webhook."""
    event: str
    payload: Optional[Dict[str, Any]] = None


class WebhookTestResponse(BaseModel):
    """Resposta do teste de webhook."""
    success: bool
    status_code: Optional[int] = None
    response_time_ms: int
    response_body: Optional[str] = None
    error: Optional[str] = None


# ==================== Integration Log Schemas ====================

class IntegrationLogResponse(BaseModel):
    """Schema de resposta para Integration Log."""
    id: UUID
    endpoint_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    webhook_id: Optional[UUID] = None
    sync_queue_id: Optional[UUID] = None
    log_type: LogType
    level: LogLevel
    status: LogStatus
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    response_status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    client_ip: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    is_retry: bool = False
    user_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    action: Optional[str] = None
    tags: Optional[List[str]] = None
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IntegrationLogList(BaseModel):
    """Schema para listagem de logs."""
    items: List[IntegrationLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class IntegrationLogFilter(BaseModel):
    """Filtros para busca de logs."""
    log_type: Optional[LogType] = None
    level: Optional[LogLevel] = None
    status: Optional[LogStatus] = None
    endpoint_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    webhook_id: Optional[UUID] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    client_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    error_only: bool = False


# ==================== Sync Queue Schemas ====================

class SyncQueueBase(BaseModel):
    """Schema base para Sync Queue."""
    external_system: ExternalSystem = ExternalSystem.CUSTOM
    external_system_config_id: Optional[UUID] = None
    direction: SyncDirection = SyncDirection.OUTBOUND
    entity_type: SyncEntityType
    entity_id: Optional[UUID] = None
    external_id: Optional[str] = None
    operation: SyncOperationType = SyncOperationType.UPSERT
    payload: Optional[Dict[str, Any]] = None
    priority: SyncPriority = SyncPriority.NORMAL

    # Agendamento
    scheduled_at: Optional[datetime] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None

    # Retry
    max_retries: int = 3
    retry_delay_seconds: int = 60
    retry_backoff_multiplier: int = 2

    # Callbacks
    callback_url: Optional[str] = None
    callback_on_success: bool = False
    callback_on_failure: bool = False

    # Metadados
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class SyncQueueCreate(SyncQueueBase):
    """Schema para criar item na fila de sync."""
    correlation_id: Optional[str] = None
    batch_id: Optional[UUID] = None


class SyncQueueBatchCreate(BaseModel):
    """Schema para criar múltiplos itens na fila."""
    items: List[SyncQueueCreate]
    batch_id: Optional[UUID] = None


class SyncQueueUpdate(BaseModel):
    """Schema para atualizar item na fila."""
    priority: Optional[SyncPriority] = None
    scheduled_at: Optional[datetime] = None
    not_before: Optional[datetime] = None
    not_after: Optional[datetime] = None
    max_retries: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class SyncQueueResponse(SyncQueueBase):
    """Schema de resposta para Sync Queue."""
    id: UUID
    correlation_id: Optional[str] = None
    batch_id: Optional[UUID] = None
    payload_hash: Optional[str] = None
    status: SyncStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    processed_by: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    external_response: Optional[Dict[str, Any]] = None
    external_status_code: Optional[int] = None
    validation_errors: Optional[List[Dict[str, Any]]] = None
    requires_review: bool = False
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    is_ready_to_process: bool
    is_expired: bool
    can_retry: bool
    wait_time_seconds: Optional[int] = None
    ativo: bool
    created_at: datetime
    updated_at: datetime


class SyncQueueList(BaseModel):
    """Schema para listagem de itens da fila."""
    items: List[SyncQueueResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SyncQueueFilter(BaseModel):
    """Filtros para busca na fila."""
    status: Optional[SyncStatus] = None
    priority: Optional[SyncPriority] = None
    entity_type: Optional[SyncEntityType] = None
    external_system: Optional[ExternalSystem] = None
    direction: Optional[SyncDirection] = None
    batch_id: Optional[UUID] = None
    correlation_id: Optional[str] = None
    requires_review: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
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
    by_entity_type: Dict[str, int] = Field(default_factory=dict)
    by_external_system: Dict[str, int] = Field(default_factory=dict)
    avg_processing_time_ms: Optional[int] = None
    oldest_pending_at: Optional[datetime] = None


# ==================== Dashboard Schemas ====================

class IntegrationDashboard(BaseModel):
    """Dashboard de integrações."""
    # API Stats
    total_endpoints: int = 0
    active_endpoints: int = 0
    deprecated_endpoints: int = 0
    total_api_calls_today: int = 0
    api_success_rate: float = 100.0
    avg_response_time_ms: Optional[int] = None

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
    recent_errors: List[IntegrationLogResponse] = Field(default_factory=list)

    # Health
    overall_health: str = "healthy"  # healthy, degraded, critical


class IntegrationHealthCheck(BaseModel):
    """Health check de integrações."""
    api_gateway: str = "healthy"
    webhooks: str = "healthy"
    sync_queue: str = "healthy"
    external_systems: Dict[str, str] = Field(default_factory=dict)
    last_check_at: datetime = Field(default_factory=datetime.utcnow)
