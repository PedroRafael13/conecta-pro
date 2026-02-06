"""Controllers do Bartolo."""

from modules.ai.bartolo.controllers.bartolo_controller import bartolo_router
from modules.ai.bartolo.controllers.openclaw_controller import openclaw_router

__all__ = ["bartolo_router", "openclaw_router"]
