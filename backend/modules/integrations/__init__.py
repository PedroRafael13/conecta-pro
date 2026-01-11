"""
Module: integrations
Description: Modulo de Integracoes - API Gateway, Webhooks, Banking, Email, WhatsApp
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo fornece:
- Gerenciamento de API Keys e Endpoints
- Configuracao e disparo de Webhooks
- Fila de sincronizacao com sistemas externos
- Logs de integracao
- Submodulos: Banking (Open Banking), Email (Campanhas), WhatsApp (Chatbot)

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
- banking/: Integracao Open Banking (BB, Itau, Bradesco)
- email/: Automacoes e campanhas de email
- whatsapp/: Automacoes e chatbot WhatsApp
"""

from fastapi import APIRouter

# Importa router do controller principal
from modules.integrations.controllers import router as integrations_controller_router

# Cria router principal que agrega todos os sub-routers
integrations_router = APIRouter(prefix="/integrations", tags=["Integrations"])

# O controller ja possui prefix="/integrations", entao usamos o router diretamente
router = integrations_controller_router

# Re-export models
from modules.integrations.models import (
    # API Endpoint
    APIEndpoint,
    HTTPMethod,
    EndpointCategory,
    EndpointStatus,
    RateLimitType,
    # API Key
    APIKey,
    APIKeyType,
    APIKeyStatus,
    APIKeyScope,
    # Webhook Config
    WebhookConfig,
    WebhookEvent,
    WebhookStatus,
    WebhookFormat,
    WebhookAuthType,
    # Integration Log
    IntegrationLog,
    LogType,
    LogLevel,
    LogStatus,
    # Sync Queue
    SyncQueue,
    SyncDirection,
    SyncPriority,
    SyncStatus,
    SyncEntityType,
    SyncOperationType,
    ExternalSystem,
)

# Re-export schemas
from modules.integrations.schemas import (
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

# Re-export services
from modules.integrations.services import (
    IntegrationService,
    WebhookService,
)

# Re-export repositories
from modules.integrations.repositories import (
    IntegrationRepository,
)

# Re-export submodulos - Banking (Open Banking)
from modules.integrations.banking import (
    BankingService,
    BBAdapter,
    ItauAdapter,
    BradescoAdapter,
    BankCode,
    AccountType,
    TransactionType,
    PaymentStatus,
    BankCredentials,
    AccountBalance,
    BankTransaction,
    BankStatement,
    PaymentRequest,
    PaymentResponse,
    PixKey,
    BankingAdapterError,
)

# Re-export submodulos - Email
from modules.integrations.email import (
    # Models
    EmailConfig,
    EmailConfigStatus,
    EmailProvider,
    EmailTemplate,
    TemplateCategory as EmailTemplateCategory,
    TemplateStatus as EmailTemplateStatus,
    EmailCampaign,
    CampaignType,
    CampaignStatus,
    TriggerType,
    EmailQueue,
    EmailStatus,
    EmailPriority,
    BounceType,
    EmailTracking,
    TrackingEventType,
    EmailSubscription,
    SubscriptionStatus,
    SubscriptionSource,
    # Services
    EmailService,
    SendResult as EmailSendResult,
    SendResponse as EmailSendResponse,
    QueueStats as EmailQueueStats,
    DailyReport as EmailDailyReport,
    TrackingPixel,
    CampaignService,
    CampaignStats,
    ABTestResult,
    DripStep,
)

# Re-export submodulos - WhatsApp
from modules.integrations.whatsapp import (
    # Models
    WhatsAppConfig,
    WhatsAppStatus,
    WhatsAppProvider,
    MessageTemplate,
    TemplateCategory as WhatsAppTemplateCategory,
    TemplateStatus as WhatsAppTemplateStatus,
    TemplateType,
    MessageQueue,
    MessageStatus,
    MessagePriority,
    MessageType,
    MessagePurpose,
    MessageLog,
    MessageDirection,
    ConversationType,
    # Services
    WhatsAppService,
    SendResult as WhatsAppSendResult,
    SendResponse as WhatsAppSendResponse,
    QueueStats as WhatsAppQueueStats,
    DailyReport as WhatsAppDailyReport,
    ChatbotService,
    ChatbotResponse,
    ConversationContext,
    ConversationState,
    Intent,
)

__all__ = [
    # Router principal
    "integrations_router",
    "router",

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

    # ==================== Core Repositories ====================
    "IntegrationRepository",

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
