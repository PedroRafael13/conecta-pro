"""Controllers do módulo de integração com folha de pagamento."""

from fastapi import APIRouter

from modules.hr.payroll_integration.controllers.esocial_controller import router as esocial_router
from modules.hr.payroll_integration.controllers.payroll_event_controller import (
    router as event_router,
)
from modules.hr.payroll_integration.controllers.payroll_export_controller import (
    router as export_router,
)
from modules.hr.payroll_integration.controllers.payroll_period_controller import (
    router as period_router,
)

# Router principal do módulo
router = APIRouter(prefix="/payroll", tags=["Payroll Integration"])

# Incluir sub-routers
router.include_router(period_router)
router.include_router(event_router)
router.include_router(export_router)
router.include_router(esocial_router)

__all__ = [
    "router",
    "period_router",
    "event_router",
    "export_router",
    "esocial_router",
]
