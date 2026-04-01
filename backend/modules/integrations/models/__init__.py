"""
Models do módulo de Integrações
Sprint 32: API Gateway / Integrações
Sprint 33: Integration Framework (Sólides, Bling, Domínio, GOV)
"""

from modules.integrations.models.api_endpoint import (
    APIEndpoint,
    EndpointCategory,
    EndpointStatus,
    HTTPMethod,
    RateLimitType,
)
from modules.integrations.models.api_key import (
    APIKey,
    APIKeyScope,
    APIKeyStatus,
    APIKeyType,
)
from modules.integrations.models.id_map import IDMap

# Sprint 33: Integration Framework
from modules.integrations.models.integration_account import (
    AccountStatus,
    AuthType,
    ConnectorType,
    IntegrationAccount,
)
from modules.integrations.models.integration_log import (
    IntegrationLog,
    LogLevel,
    LogStatus,
    LogType,
)
from modules.integrations.models.sync_queue import (
    ExternalSystem,
    SyncDirection,
    SyncEntityType,
    SyncOperationType,
    SyncPriority,
    SyncQueue,
    SyncStatus,
)
from modules.integrations.models.sync_run import (
    SyncRun,
    SyncRunMode,
    SyncRunStatus,
    SyncRunTrigger,
)
from modules.integrations.models.sync_state import SyncState
from modules.integrations.models.webhook_config import (
    WebhookAuthType,
    WebhookConfig,
    WebhookEvent,
    WebhookFormat,
    WebhookStatus,
)

__all__ = [
    # API Endpoint
    "APIEndpoint",
    "HTTPMethod",
    "EndpointCategory",
    "EndpointStatus",
    "RateLimitType",
    # API Key
    "APIKey",
    "APIKeyType",
    "APIKeyStatus",
    "APIKeyScope",
    # Webhook Config
    "WebhookConfig",
    "WebhookEvent",
    "WebhookStatus",
    "WebhookFormat",
    "WebhookAuthType",
    # Integration Log
    "IntegrationLog",
    "LogType",
    "LogLevel",
    "LogStatus",
    # Sync Queue
    "SyncQueue",
    "SyncDirection",
    "SyncPriority",
    "SyncStatus",
    "SyncEntityType",
    "SyncOperationType",
    "ExternalSystem",
    # Sprint 33: Integration Framework
    "IntegrationAccount",
    "ConnectorType",
    "AuthType",
    "AccountStatus",
    "SyncRun",
    "SyncRunStatus",
    "SyncRunMode",
    "SyncRunTrigger",
    "SyncState",
    "IDMap",
]
