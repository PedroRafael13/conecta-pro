"""Email Services - Servicos do modulo de email.

Sprint 32 - Automacoes Email.
"""

from modules.integrations.email.services.campaign_service import (
    ABTestResult,
    CampaignService,
    CampaignStats,
    DripStep,
)
from modules.integrations.email.services.email_service import (
    DailyReport,
    EmailService,
    QueueStats,
    SendResponse,
    SendResult,
    TrackingPixel,
)

__all__ = [
    # Email Service
    "EmailService",
    "SendResult",
    "SendResponse",
    "QueueStats",
    "DailyReport",
    "TrackingPixel",
    # Campaign Service
    "CampaignService",
    "CampaignStats",
    "ABTestResult",
    "DripStep",
]
