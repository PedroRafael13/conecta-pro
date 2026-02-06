"""Módulo de Notificações - Notification Hub.

Sprint 36 - Sistema centralizado de notificações multi-canal.

Features:
- Suporte a múltiplos canais (email, SMS, WhatsApp, Push, Slack, In-App)
- Templates multi-canal com variáveis
- Preferências de usuário (opt-in/opt-out)
- Fila unificada com prioridades
- Rate limiting por canal
- Tracking (open, click, conversion)
- Webhooks para status de entrega
- Métricas e analytics
"""

from modules.notifications.models import (
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
