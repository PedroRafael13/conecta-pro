"""
Schemas do módulo de Integrações
Sprint 32: API Gateway / Integrações
Sprint 33: Integration Framework
"""

from modules.integrations.schemas.connector_schemas import (
    # Connector Info
    ConnectorInfo,
    ConnectorListResponse,
    # Statistics
    ConnectorStats,
    # Health Check
    HealthCheckResponse,
    IDMapList,
    # ID Map
    IDMapResponse,
    # Integration Account
    IntegrationAccountBase,
    IntegrationAccountCreate,
    IntegrationAccountList,
    IntegrationAccountResponse,
    IntegrationAccountUpdate,
    IntegrationStats,
    # Sync Run
    SyncRunCreate,
    SyncRunDetailResponse,
    SyncRunList,
    SyncRunResponse,
    SyncStateList,
    # Sync State
    SyncStateResponse,
)
from modules.integrations.schemas.integration_schemas import (
    # API Endpoint
    APIEndpointBase,
    APIEndpointCreate,
    APIEndpointList,
    APIEndpointResponse,
    APIEndpointUpdate,
    # API Key
    APIKeyBase,
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyList,
    APIKeyResponse,
    APIKeyRevokeRequest,
    APIKeyUpdate,
    # Dashboard
    IntegrationDashboard,
    IntegrationHealthCheck,
    IntegrationLogFilter,
    IntegrationLogList,
    # Integration Log
    IntegrationLogResponse,
    # Sync Queue
    SyncQueueBase,
    SyncQueueBatchCreate,
    SyncQueueCreate,
    SyncQueueFilter,
    SyncQueueList,
    SyncQueueResponse,
    SyncQueueStats,
    SyncQueueUpdate,
    # Webhook
    WebhookConfigBase,
    WebhookConfigCreate,
    WebhookConfigList,
    WebhookConfigResponse,
    WebhookConfigUpdate,
    WebhookTestRequest,
    WebhookTestResponse,
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
