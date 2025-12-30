"""Controllers do módulo CRM."""

from .commission_controller import router as commission_router
from .contract_controller import router as contract_router
from .dashboard_controller import router as dashboard_router
from .lead_controller import router as lead_router
from .opportunity_controller import router as opportunity_router
from .proposal_controller import router as proposal_router

__all__ = [
    "lead_router",
    "opportunity_router",
    "proposal_router",
    "commission_router",
    "dashboard_router",
    "contract_router",
]
