"""Dashboard Unificado de Pendências."""

from .dashboard_controller import router  # noqa: F401
from .unified_dashboard import UnifiedDashboard

__all__ = ["UnifiedDashboard", "router"]
