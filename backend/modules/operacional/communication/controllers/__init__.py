"""
Controllers do modulo de Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from .announcement_controller import router as announcement_router
from .notification_controller import router as notification_router
from .websocket_controller import router as websocket_router

__all__ = [
    "announcement_router",
    "notification_router",
    "websocket_router",
]
