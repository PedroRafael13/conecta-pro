"""
Módulo INTELIGÊNCIA — Agregador
Unifica: analytics + reports + monitoring

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Analytics ---
from modules.analytics.controllers import analytics_router, executive_dashboard_router

# --- Monitoring ---
from modules.monitoring import router as monitoring_router

# --- Reports ---
from modules.reports.controllers import router as report_router

__all__ = [
    "executive_dashboard_router",
    "analytics_router",
    "report_router",
    "monitoring_router",
]
