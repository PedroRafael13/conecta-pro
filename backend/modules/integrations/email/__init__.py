"""Modulo Email - Automacoes e Campanhas.

Sprint 32 - Automacoes Email.
"""

from modules.integrations.email.models import (
    BounceType,
    CampaignStatus,
    CampaignType,
    EmailCampaign,
    EmailConfig,
    EmailConfigStatus,
    EmailPriority,
    EmailProvider,
    EmailQueue,
    EmailStatus,
    EmailSubscription,
    EmailTemplate,
    EmailTracking,
    SubscriptionSource,
    SubscriptionStatus,
    TemplateCategory,
    TemplateStatus,
    TrackingEventType,
    TriggerType,
)
from modules.integrations.email.services import (
    ABTestResult,
    CampaignService,
    CampaignStats,
    DailyReport,
    DripStep,
    EmailService,
    QueueStats,
    SendResponse,
    SendResult,
    TrackingPixel,
)

__all__ = [
    # Models - Config
    "EmailConfig",
    "EmailConfigStatus",
    "EmailProvider",
    # Models - Template
    "EmailTemplate",
    "TemplateCategory",
    "TemplateStatus",
    # Models - Campaign
    "EmailCampaign",
    "CampaignType",
    "CampaignStatus",
    "TriggerType",
    # Models - Queue
    "EmailQueue",
    "EmailStatus",
    "EmailPriority",
    "BounceType",
    # Models - Tracking
    "EmailTracking",
    "TrackingEventType",
    # Models - Subscription
    "EmailSubscription",
    "SubscriptionStatus",
    "SubscriptionSource",
    # Services - Email
    "EmailService",
    "SendResult",
    "SendResponse",
    "QueueStats",
    "DailyReport",
    "TrackingPixel",
    # Services - Campaign
    "CampaignService",
    "CampaignStats",
    "ABTestResult",
    "DripStep",
]
