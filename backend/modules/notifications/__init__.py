"""Módulo de Notificações - Notification Hub.

DEPRECATED: Use 'modules.gestao' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.notifications' is deprecated. "
    "Use 'modules.gestao' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.notifications.models import (  # noqa: E402
    ChannelProvider,
    ChannelStatus,
    ChannelType,
    DigestType,
    FrequencyType,
    LogEventType,
    LogLevel,
    NotificationChannel,
    NotificationLog,
    NotificationMetric,
    NotificationPreference,
    NotificationQueue,
    NotificationSubscription,
    NotificationTemplate,
    QueuePriority,
    QueueStatus,
    TemplateCategory,
    TemplateStatus,
)

# Services importados sob demanda para evitar dependências circulares
# from modules.notifications.services import ChannelDispatcher, NotificationService

__all__ = [
    # Models
    "NotificationChannel",
    "NotificationTemplate",
    "NotificationPreference",
    "NotificationSubscription",
    "NotificationQueue",
    "NotificationLog",
    "NotificationMetric",
    # Enums
    "ChannelType",
    "ChannelStatus",
    "ChannelProvider",
    "TemplateStatus",
    "TemplateCategory",
    "FrequencyType",
    "DigestType",
    "QueueStatus",
    "QueuePriority",
    "LogEventType",
    "LogLevel",
]
