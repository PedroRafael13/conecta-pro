"""
Schemas Pydantic do modulo de Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from .communication_schemas import (
    AlertAcknowledgeRequest,
    # Alert
    AlertCreate,
    AlertFilter,
    AlertListResponse,
    AlertResponse,
    AnnouncementAcknowledgeRequest,
    # Announcement
    AnnouncementCreate,
    AnnouncementFilter,
    AnnouncementListResponse,
    AnnouncementPublishRequest,
    AnnouncementReadResponse,
    AnnouncementReadStats,
    AnnouncementResponse,
    AnnouncementUpdate,
    MarkNotificationReadRequest,
    # Notification
    NotificationCreate,
    NotificationFilter,
    NotificationListResponse,
    NotificationResponse,
    NotificationUnreadCount,
    WebSocketAlertMessage,
    WebSocketConnectionInfo,
    # WebSocket
    WebSocketMessage,
    WebSocketNotificationMessage,
)

__all__ = [
    # Announcement
    "AnnouncementCreate",
    "AnnouncementUpdate",
    "AnnouncementResponse",
    "AnnouncementListResponse",
    "AnnouncementFilter",
    "AnnouncementPublishRequest",
    "AnnouncementReadResponse",
    "AnnouncementReadStats",
    "AnnouncementAcknowledgeRequest",
    # Notification
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationFilter",
    "MarkNotificationReadRequest",
    "NotificationUnreadCount",
    # Alert
    "AlertCreate",
    "AlertResponse",
    "AlertListResponse",
    "AlertAcknowledgeRequest",
    "AlertFilter",
    # WebSocket
    "WebSocketMessage",
    "WebSocketAlertMessage",
    "WebSocketNotificationMessage",
    "WebSocketConnectionInfo",
]
