"""
Module: integrations
Description: Modulo de Integracoes - API Gateway, Webhooks, Banking, Email, WhatsApp, Conectores
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo fornece:
- Gerenciamento de API Keys e Endpoints
- Configuracao e disparo de Webhooks
- Fila de sincronizacao com sistemas externos
- Logs de integracao
- Conectores externos (Bling, Solides, etc.) - Sprint 33
- Submodulos: Banking (Open Banking), Email (Campanhas), WhatsApp (Chatbot)

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
- connectors/: Conectores para sistemas externos (Sprint 33)
- sync/: Engine de sincronizacao (Sprint 33)
- banking/: Integracao Open Banking (BB, Itau, Bradesco)
- email/: Automacoes e campanhas de email
- whatsapp/: Automacoes e chatbot WhatsApp
"""

from fastapi import APIRouter

# Re-export submodulos - Banking (Open Banking)
from modules.integrations.banking import (
    AccountBalance,
    AccountType,
    BankCode,
    BankCredentials,
    BankingAdapterError,
    BankingService,
    BankStatement,
    BankTransaction,
    BBAdapter,
    BradescoAdapter,
    ItauAdapter,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PixKey,
    TransactionType,
)

# Importa routers dos controllers
from modules.integrations.controllers import connector_router, integration_router

# Re-export submodulos - Email
from modules.integrations.email import (
    ABTestResult,
    BounceType,
    CampaignService,
    CampaignStats,
    CampaignStatus,
    CampaignType,
    DripStep,
    EmailCampaign,
    EmailConfig,
    EmailConfigStatus,
    EmailPriority,
    EmailProvider,
    EmailQueue,
    EmailService,
    EmailStatus,
    EmailSubscription,
    EmailTemplate,
    EmailTracking,
    SubscriptionSource,
    SubscriptionStatus,
    TrackingEventType,
    TrackingPixel,
    TriggerType,
)
from modules.integrations.email import (
    DailyReport as EmailDailyReport,
)
from modules.integrations.email import (
    QueueStats as EmailQueueStats,
)
from modules.integrations.email import (
    SendResponse as EmailSendResponse,
)
from modules.integrations.email import (
    SendResult as EmailSendResult,
)
from modules.integrations.email import (
    TemplateCategory as EmailTemplateCategory,
)
from modules.integrations.email import (
    TemplateStatus as EmailTemplateStatus,
)

# Re-export models
from modules.integrations.models import (
    AccountStatus,
    APIEndpoint,
    APIKey,
    APIKeyScope,
    APIKeyStatus,
    APIKeyType,
    AuthType,
    ConnectorType,
    EndpointCategory,
    EndpointStatus,
    ExternalSystem,
    HTTPMethod,
    IDMap,
    IntegrationAccount,
    IntegrationLog,
    LogLevel,
    LogStatus,
    LogType,
    RateLimitType,
    SyncDirection,
    SyncEntityType,
    SyncOperationType,
    SyncPriority,
    SyncQueue,
    SyncRun,
    SyncRunMode,
    SyncRunStatus,
    SyncRunTrigger,
    SyncState,
    SyncStatus,
    WebhookAuthType,
    WebhookConfig,
    WebhookEvent,
    WebhookFormat,
    WebhookStatus,
)

# Re-export repositories
from modules.integrations.repositories import (
    ConnectorRepository,
    IntegrationRepository,
)

# Re-export schemas
from modules.integrations.schemas import (
    APIEndpointBase,
    APIEndpointCreate,
    APIEndpointList,
    APIEndpointResponse,
    APIEndpointUpdate,
    APIKeyBase,
    APIKeyCreate,
    APIKeyCreateResponse,
    APIKeyList,
    APIKeyResponse,
    APIKeyRevokeRequest,
    APIKeyUpdate,
    IntegrationDashboard,
    IntegrationHealthCheck,
    IntegrationLogFilter,
    IntegrationLogList,
    IntegrationLogResponse,
    SyncQueueBase,
    SyncQueueBatchCreate,
    SyncQueueCreate,
    SyncQueueFilter,
    SyncQueueList,
    SyncQueueResponse,
    SyncQueueStats,
    SyncQueueUpdate,
    WebhookConfigBase,
    WebhookConfigCreate,
    WebhookConfigList,
    WebhookConfigResponse,
    WebhookConfigUpdate,
    WebhookTestRequest,
    WebhookTestResponse,
)

# Re-export services
from modules.integrations.services import (
    ConnectorService,
    IntegrationService,
    WebhookService,
)

# Re-export submodulos - WhatsApp
from modules.integrations.whatsapp import (
    ChatbotResponse,
    ChatbotService,
    ConversationContext,
    ConversationState,
    ConversationType,
    Intent,
    MessageDirection,
    MessageLog,
    MessagePriority,
    MessagePurpose,
    MessageQueue,
    MessageStatus,
    MessageTemplate,
    MessageType,
    TemplateType,
    WhatsAppConfig,
    WhatsAppProvider,
    WhatsAppService,
    WhatsAppStatus,
)
from modules.integrations.whatsapp import (
    DailyReport as WhatsAppDailyReport,
)
from modules.integrations.whatsapp import (
    QueueStats as WhatsAppQueueStats,
)
from modules.integrations.whatsapp import (
    SendResponse as WhatsAppSendResponse,
)
from modules.integrations.whatsapp import (
    SendResult as WhatsAppSendResult,
)
from modules.integrations.whatsapp import (
    TemplateCategory as WhatsAppTemplateCategory,
)
from modules.integrations.whatsapp import (
    TemplateStatus as WhatsAppTemplateStatus,
)

# Cria router principal que agrega todos os sub-routers
integrations_router = APIRouter(prefix="/integrations", tags=["Integrations"])

# Router padrão (backward compatibility)
router = integration_router

__all__ = [
    # Routers
    "integrations_router",
    "router",
    "integration_router",
    "connector_router",
    # ==================== Core Models ====================
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
    # Sprint 33: Integration Framework Models
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
    # ==================== Core Schemas ====================
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
    # ==================== Core Services ====================
    "IntegrationService",
    "WebhookService",
    "ConnectorService",
    # ==================== Core Repositories ====================
    "IntegrationRepository",
    "ConnectorRepository",
    # ==================== Banking Submodule ====================
    "BankingService",
    "BBAdapter",
    "ItauAdapter",
    "BradescoAdapter",
    "BankCode",
    "AccountType",
    "TransactionType",
    "PaymentStatus",
    "BankCredentials",
    "AccountBalance",
    "BankTransaction",
    "BankStatement",
    "PaymentRequest",
    "PaymentResponse",
    "PixKey",
    "BankingAdapterError",
    # ==================== Email Submodule ====================
    # Models
    "EmailConfig",
    "EmailConfigStatus",
    "EmailProvider",
    "EmailTemplate",
    "EmailTemplateCategory",
    "EmailTemplateStatus",
    "EmailCampaign",
    "CampaignType",
    "CampaignStatus",
    "TriggerType",
    "EmailQueue",
    "EmailStatus",
    "EmailPriority",
    "BounceType",
    "EmailTracking",
    "TrackingEventType",
    "EmailSubscription",
    "SubscriptionStatus",
    "SubscriptionSource",
    # Services
    "EmailService",
    "EmailSendResult",
    "EmailSendResponse",
    "EmailQueueStats",
    "EmailDailyReport",
    "TrackingPixel",
    "CampaignService",
    "CampaignStats",
    "ABTestResult",
    "DripStep",
    # ==================== WhatsApp Submodule ====================
    # Models
    "WhatsAppConfig",
    "WhatsAppStatus",
    "WhatsAppProvider",
    "MessageTemplate",
    "WhatsAppTemplateCategory",
    "WhatsAppTemplateStatus",
    "TemplateType",
    "MessageQueue",
    "MessageStatus",
    "MessagePriority",
    "MessageType",
    "MessagePurpose",
    "MessageLog",
    "MessageDirection",
    "ConversationType",
    # Services
    "WhatsAppService",
    "WhatsAppSendResult",
    "WhatsAppSendResponse",
    "WhatsAppQueueStats",
    "WhatsAppDailyReport",
    "ChatbotService",
    "ChatbotResponse",
    "ConversationContext",
    "ConversationState",
    "Intent",
]

__version__ = "1.0.0"
