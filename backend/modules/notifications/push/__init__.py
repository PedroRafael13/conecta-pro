"""Módulo Push Notifications - Sprint 37.

Sistema completo de Push Notifications para iOS e Android.

Funcionalidades:
- Registro e gerenciamento de dispositivos
- Envio via FCM (Firebase Cloud Messaging) e APNs (Apple Push)
- Campanhas com targeting por segmento, tópico, tags
- Notificações rich (imagens, botões de ação)
- Analytics completo (entrega, abertura, clique)
- A/B Testing
- Rate limiting e TTL

Estrutura:
- models/: Modelos SQLAlchemy (Device, Campaign, Notification, Analytics)
- schemas/: Schemas Pydantic para API
- services/: Lógica de negócio (FCM, APNs, PushService)
- controllers/: Endpoints REST
"""

# Lazy import do router para evitar dependências circulares em testes
def get_router():
    """Retorna o router do módulo."""
    from modules.notifications.push.controllers import router
    return router


# Models - importação direta (sem dependências externas pesadas)
from modules.notifications.push.models import (
    CampaignStatus,
    CampaignType,
    DevicePlatform,
    DeviceStatus,
    MetricPeriod,
    NotificationPriority,
    NotificationStatus,
    PushABTestResult,
    PushCampaign,
    PushDeliveryReport,
    PushDevice,
    PushDeviceSession,
    PushMetric,
    PushNotification,
    PushNotificationAction,
    PushSegment,
    TargetType,
)

# Services - importação direta
from modules.notifications.push.services import (
    APNsPayload,
    APNsResponse,
    APNsService,
    FCMMessage,
    FCMResponse,
    FCMService,
    PushService,
)

__all__ = [
    # Router (lazy)
    "get_router",
    # Models
    "PushDevice",
    "PushDeviceSession",
    "PushCampaign",
    "PushSegment",
    "PushNotification",
    "PushNotificationAction",
    "PushMetric",
    "PushABTestResult",
    "PushDeliveryReport",
    # Enums
    "DevicePlatform",
    "DeviceStatus",
    "CampaignStatus",
    "CampaignType",
    "TargetType",
    "NotificationStatus",
    "NotificationPriority",
    "MetricPeriod",
    # Services
    "PushService",
    "FCMService",
    "FCMMessage",
    "FCMResponse",
    "APNsService",
    "APNsPayload",
    "APNsResponse",
]
