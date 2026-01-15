"""
Schemas do módulo de Integrações
Sprint 32: API Gateway / Integrações
Sprint 33: Integration Framework
"""

from modules.integrations.schemas.integration_schemas import (
    # API Endpoint
    APIEndpointBase,
    APIEndpointCreate,
    APIEndpointUpdate,
    APIEndpointResponse,
    APIEndpointList,
    # API Key
    APIKeyBase,
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyUpdate,
    APIKeyResponse,
    APIKeyList,
    APIKeyRevokeRequest,
    # Webhook
    WebhookConfigBase,
    WebhookConfigCreate,
    WebhookConfigUpdate,
    WebhookConfigResponse,
    WebhookConfigList,
    WebhookTestRequest,
    WebhookTestResponse,
    # Integration Log
    IntegrationLogResponse,
    IntegrationLogList,
    IntegrationLogFilter,
    # Sync Queue
    SyncQueueBase,
    SyncQueueCreate,
    SyncQueueBatchCreate,
    SyncQueueUpdate,
    SyncQueueResponse,
    SyncQueueList,
    SyncQueueFilter,
    SyncQueueStats,
    # Dashboard
    IntegrationDashboard,
    IntegrationHealthCheck,
)

from modules.integrations.schemas.connector_schemas import (
    # Connector Info
    ConnectorInfo,
    ConnectorListResponse,
    # Integration Account
    IntegrationAccountBase,
    IntegrationAccountCreate,
    IntegrationAccountUpdate,
    IntegrationAccountResponse,
    IntegrationAccountList,
    # Sync Run
    SyncRunCreate,
    SyncRunResponse,
    SyncRunList,
    SyncRunDetailResponse,
    # Health Check
    HealthCheckResponse,
    # Sync State
    SyncStateResponse,
    SyncStateList,
    # ID Map
    IDMapResponse,
    IDMapList,
    # Statistics
    ConnectorStats,
    IntegrationStats,
)

__all__ = [
    # API Endpoint
    "APIEndpointBase",
    "APIEndpointCreate",
    "APIEndpointUpdate",
    "APIEndpointResponse",
    "APIEndpointList",
    # API Key
    "APIKeyBase",
    "APIKeyCreate",
    "APIKeyCreateResponse",
    "APIKeyUpdate",
    "APIKeyResponse",
    "APIKeyList",
    "APIKeyRevokeRequest",
    # Webhook
    "WebhookConfigBase",
    "WebhookConfigCreate",
    "WebhookConfigUpdate",
    "WebhookConfigResponse",
    "WebhookConfigList",
    "WebhookTestRequest",
    "WebhookTestResponse",
    # Integration Log
    "IntegrationLogResponse",
    "IntegrationLogList",
    "IntegrationLogFilter",
    # Sync Queue
    "SyncQueueBase",
    "SyncQueueCreate",
    "SyncQueueBatchCreate",
    "SyncQueueUpdate",
    "SyncQueueResponse",
    "SyncQueueList",
    "SyncQueueFilter",
    "SyncQueueStats",
    # Dashboard
    "IntegrationDashboard",
    "IntegrationHealthCheck",
    # Sprint 33: Conectores
    "ConnectorInfo",
    "ConnectorListResponse",
    "IntegrationAccountBase",
    "IntegrationAccountCreate",
    "IntegrationAccountUpdate",
    "IntegrationAccountResponse",
    "IntegrationAccountList",
    "SyncRunCreate",
    "SyncRunResponse",
    "SyncRunList",
    "SyncRunDetailResponse",
    "HealthCheckResponse",
    "SyncStateResponse",
    "SyncStateList",
    "IDMapResponse",
    "IDMapList",
    "ConnectorStats",
    "IntegrationStats",
]
