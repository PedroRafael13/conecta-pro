"""Email Models - Modelos do modulo de email.

Sprint 32 - Automacoes Email.
"""

from modules.integrations.email.models.email_campaign import (
    CampaignStatus,
    CampaignType,
    EmailCampaign,
    TriggerType,
)
from modules.integrations.email.models.email_config import (
    EmailConfig,
    EmailConfigStatus,
    EmailProvider,
)
from modules.integrations.email.models.email_queue import (
    BounceType,
    EmailPriority,
    EmailQueue,
    EmailStatus,
)
from modules.integrations.email.models.email_subscription import (
    EmailSubscription,
    SubscriptionSource,
    SubscriptionStatus,
)
from modules.integrations.email.models.email_template import (
    EmailTemplate,
    TemplateCategory,
    TemplateStatus,
)
from modules.integrations.email.models.email_tracking import (
    EmailTracking,
    TrackingEventType,
)

__all__ = [
    # Config
    "EmailConfig",
    "EmailConfigStatus",
    "EmailProvider",
    # Template
    "EmailTemplate",
    "TemplateCategory",
    "TemplateStatus",
    # Campaign
    "EmailCampaign",
    "CampaignType",
    "CampaignStatus",
    "TriggerType",
    # Queue
    "EmailQueue",
    "EmailStatus",
    "EmailPriority",
    "BounceType",
    # Tracking
    "EmailTracking",
    "TrackingEventType",
    # Subscription
    "EmailSubscription",
    "SubscriptionStatus",
    "SubscriptionSource",
]
