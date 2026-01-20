"""Models do módulo de Notificações.

Sprint 36 - Notification Hub.
"""

from modules.notifications.models.notification_channel import (
    ChannelProvider,
    ChannelStatus,
    ChannelType,
    NotificationChannel,
)
from modules.notifications.models.notification_log import (
    LogEventType,
    LogLevel,
    NotificationLog,
    NotificationMetric,
)
from modules.notifications.models.notification_preference import (
    DigestType,
    FrequencyType,
    NotificationPreference,
    NotificationSubscription,
)
from modules.notifications.models.notification_queue import (
    NotificationQueue,
    QueuePriority,
    QueueStatus,
)
from modules.notifications.models.notification_template import (
    NotificationTemplate,
    TemplateCategory,
    TemplateStatus,
)

__all__ = [
    # Channel
    "NotificationChannel",
    "ChannelType",
    "ChannelStatus",
    "ChannelProvider",
    # Template
    "NotificationTemplate",
    "TemplateStatus",
    "TemplateCategory",
    # Preference
    "NotificationPreference",
    "NotificationSubscription",
    "FrequencyType",
    "DigestType",
    # Queue
    "NotificationQueue",
    "QueueStatus",
    "QueuePriority",
    # Log
    "NotificationLog",
    "NotificationMetric",
    "LogEventType",
    "LogLevel",
]
