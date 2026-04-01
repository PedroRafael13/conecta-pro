"""
Modulo de Comunicacao Operacional.

Este modulo fornece funcionalidades completas para:
- Comunicados (criacao, publicacao, agendamento, confirmacao de leitura)
- Notificacoes (push, email, SMS, WhatsApp, in-app)
- Alertas em Tempo Real (via WebSocket)

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100

Estrutura:
- models/: Modelos SQLAlchemy (Announcement, Notification, Alert)
- schemas/: Schemas Pydantic para validacao
- repositories/: Acesso a dados
- services/: Logica de negocio
- controllers/: Endpoints REST e WebSocket

Uso:
    from modules.operacional.communication import (
        communication_router,
        AnnouncementService,
        NotificationService,
        AlertService,
    )

    # Inclui router no app
    app.include_router(communication_router)

    # Usa services
    announcement_service = AnnouncementService(db)
    notification_service = NotificationService(db)
    alert_service = AlertService(db)
"""

from fastapi import APIRouter

# Importa routers
from .controllers import (
    announcement_router,
    notification_router,
    websocket_router,
)

# Importa models
from .models import (
    Alert,
    AlertSeverity,
    AlertType,
    Announcement,
    AnnouncementCategory,
    AnnouncementPriority,
    AnnouncementRead,
    AnnouncementStatus,
    AnnouncementTargetType,
    Notification,
    NotificationChannel,
    NotificationType,
)

# Importa repositories
from .repositories import (
    AlertRepository,
    AnnouncementRepository,
    NotificationRepository,
)

# Importa schemas
from .schemas import (
    AlertCreate,
    AlertListResponse,
    AlertResponse,
    AnnouncementCreate,
    AnnouncementFilter,
    AnnouncementListResponse,
    AnnouncementResponse,
    AnnouncementUpdate,
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    WebSocketMessage,
)

# Importa services
from .services import (
    AlertService,
    AnnouncementService,
    NotificationService,
    PushProvider,
    PushProviderFactory,
)

# Cria router principal
communication_router = APIRouter(prefix="/comunicacao", tags=["Comunicacao"])

# Inclui sub-routers
communication_router.include_router(announcement_router)
communication_router.include_router(notification_router)
communication_router.include_router(websocket_router)

__all__ = [
    # Router
    "communication_router",
    "announcement_router",
    "notification_router",
    "websocket_router",
    # Models - Announcement
    "Announcement",
    "AnnouncementStatus",
    "AnnouncementPriority",
    "AnnouncementCategory",
    "AnnouncementTargetType",
    "AnnouncementRead",
    # Models - Notification
    "Notification",
    "NotificationType",
    "NotificationChannel",
    # Models - Alert
    "Alert",
    "AlertType",
    "AlertSeverity",
    # Schemas
    "AnnouncementCreate",
    "AnnouncementUpdate",
    "AnnouncementResponse",
    "AnnouncementListResponse",
    "AnnouncementFilter",
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "AlertCreate",
    "AlertResponse",
    "AlertListResponse",
    "WebSocketMessage",
    # Repositories
    "AnnouncementRepository",
    "NotificationRepository",
    "AlertRepository",
    # Services
    "AnnouncementService",
    "NotificationService",
    "AlertService",
    "PushProvider",
    "PushProviderFactory",
]

__version__ = "1.0.0"
