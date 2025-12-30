"""Controllers do módulo CRM."""

from .lead_controller import router as lead_router
from .opportunity_controller import router as opportunity_router

__all__ = ["lead_router", "opportunity_router"]
