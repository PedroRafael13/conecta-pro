"""
Módulo INTELIGÊNCIA — Agregador
Unifica: ai/bartolo + analytics + reports + monitoring + search

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- AI Bartolo ---
from modules.ai.bartolo.controllers import bartolo_router

# --- Analytics ---
from modules.analytics.controllers import analytics_router, executive_dashboard_router

# --- Monitoring ---
from modules.monitoring import router as monitoring_router

# --- Reports ---
from modules.reports.controllers import router as report_router

# --- Search ---
from modules.search import search_router

__all__ = [
    "bartolo_router",
    "executive_dashboard_router",
    "analytics_router",
    "report_router",
    "monitoring_router",
    "search_router",
]
