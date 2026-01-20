"""Analytics Controllers - Sprint 04 + FASE 3."""

from .predictive_analytics_controller import analytics_router
from .executive_dashboard_controller import router as executive_dashboard_router

__all__ = ["analytics_router", "executive_dashboard_router"]
