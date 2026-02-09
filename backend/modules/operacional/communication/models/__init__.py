"""
Models do modulo de Comunicacao Operacional.

Este modulo fornece modelos para:
- Comunicados (Announcements)
- Confirmacao de Leitura (AnnouncementRead)
- Notificacoes (Notifications)
- Alertas em Tempo Real (Alerts)

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from .alert import (
    Alert,
    AlertSeverity,
    AlertType,
)
from .announcement import (
    Announcement,
    AnnouncementCategory,
    AnnouncementPriority,
    AnnouncementStatus,
    AnnouncementTargetType,
)
from .announcement_read import AnnouncementRead
from .notification import (
    Notification,
    NotificationChannel,
    NotificationType,
)

__all__ = [
    # Announcement
    "Announcement",
    "AnnouncementStatus",
    "AnnouncementPriority",
    "AnnouncementCategory",
    "AnnouncementTargetType",
    # AnnouncementRead
    "AnnouncementRead",
    # Notification
    "Notification",
    "NotificationType",
    "NotificationChannel",
    # Alert
    "Alert",
    "AlertType",
    "AlertSeverity",
]
