"""Schemas do módulo de Notificações.

Sprint 36 - Notification Hub.
"""

from modules.notifications.schemas.notification_schemas import (  # Channel; Template; Preference; Send; Queue; Log
    CategoryPreferenceSchema,
    ChannelConfigBase,
    ChannelConfigCreate,
    ChannelConfigResponse,
    ChannelConfigUpdate,
    LogEntryResponse,
    MetricsSummaryResponse,
    PreferenceBase,
    PreferenceCreate,
    PreferenceResponse,
    PreferenceUpdate,
    QueueItemResponse,
    QueueStatsResponse,
    RecipientSchema,
    SendNotificationRequest,
    SendNotificationResponse,
    TemplateBase,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
    TemplateVariableSchema,
)

__all__ = [
    # Channel
    "ChannelConfigBase",
    "ChannelConfigCreate",
    "ChannelConfigUpdate",
    "ChannelConfigResponse",
    # Template
    "TemplateVariableSchema",
    "TemplateBase",
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
    # Preference
    "CategoryPreferenceSchema",
    "PreferenceBase",
    "PreferenceCreate",
    "PreferenceUpdate",
    "PreferenceResponse",
    # Send
    "RecipientSchema",
    "SendNotificationRequest",
    "SendNotificationResponse",
    # Queue
    "QueueItemResponse",
    "QueueStatsResponse",
    # Log
    "LogEntryResponse",
    "MetricsSummaryResponse",
]
