"""Controllers do módulo Analytics Dashboard."""

from fastapi import APIRouter

from .dashboard_controller import router as dashboard_router
from .kpi_controller import router as kpi_router
from .report_controller import router as report_router

# Router principal do módulo
router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Incluir sub-routers
router.include_router(dashboard_router)
router.include_router(kpi_router)
router.include_router(report_router)

__all__ = [
    "router",
    "dashboard_router",
    "kpi_router",
    "report_router",
]
