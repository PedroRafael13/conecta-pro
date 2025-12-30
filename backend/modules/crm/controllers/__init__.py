"""Controllers do módulo CRM."""

from .lead_controller import router as lead_router
from .opportunity_controller import router as opportunity_router
from .proposal_controller import router as proposal_router

__all__ = ["lead_router", "opportunity_router", "proposal_router"]
