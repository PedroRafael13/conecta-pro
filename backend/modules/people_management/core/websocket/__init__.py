"""WebSocket para Gestao de Pessoas."""

from .gp_websocket import manager as gp_ws_manager
from .gp_websocket import router as gp_ws_router

__all__ = ["gp_ws_router", "gp_ws_manager"]
