"""Controllers do módulo de Ponto Eletrônico."""

from fastapi import APIRouter

from .time_entry_controller import router as time_entry_router
from .time_sheet_controller import router as time_sheet_router
from .overtime_controller import router as overtime_router
from .justification_controller import router as justification_router

# Router principal do módulo
router = APIRouter(prefix="/time-tracking", tags=["Ponto Eletrônico"])

# Inclui sub-routers
router.include_router(time_entry_router)
router.include_router(time_sheet_router)
router.include_router(overtime_router)
router.include_router(justification_router)

__all__ = [
    "router",
    "time_entry_router",
    "time_sheet_router",
    "overtime_router",
    "justification_router",
]
