"""Controllers do módulo de Notificações.

Sprint 36 - Notification Hub.
Sprint 03 - Intelligent Notifications.
"""

from modules.notifications.controllers.notification_controller import router
from modules.notifications.controllers.intelligent_notification_controller import (
    router as intelligent_router,
)

__all__ = ["router", "intelligent_router"]
