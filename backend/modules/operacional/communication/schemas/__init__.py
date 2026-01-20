"""
Schemas Pydantic do modulo de Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from .communication_schemas import (
    # Announcement
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
    AnnouncementListResponse,
    AnnouncementFilter,
    AnnouncementPublishRequest,
    AnnouncementReadResponse,
    AnnouncementReadStats,
    AnnouncementAcknowledgeRequest,
    # Notification
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationFilter,
    MarkNotificationReadRequest,
    NotificationUnreadCount,
    # Alert
    AlertCreate,
    AlertResponse,
    AlertListResponse,
    AlertAcknowledgeRequest,
    AlertFilter,
    # WebSocket
    WebSocketMessage,
    WebSocketAlertMessage,
    WebSocketNotificationMessage,
    WebSocketConnectionInfo,
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
