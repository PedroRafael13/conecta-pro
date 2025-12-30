"""Controllers do módulo de Visitantes."""

from modules.visitors.controllers.visitor_controller import router as visitor_router
from modules.visitors.controllers.authorization_controller import (
    router as authorization_router,
)
from modules.visitors.controllers.log_controller import router as log_router
from modules.visitors.controllers.schedule_controller import router as schedule_router

__all__ = [
    "visitor_router",
    "authorization_router",
    "log_router",
    "schedule_router",
]
