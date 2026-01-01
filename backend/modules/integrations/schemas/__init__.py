"""
Schemas do módulo de Integrações
Sprint 32: API Gateway / Integrações
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
]
