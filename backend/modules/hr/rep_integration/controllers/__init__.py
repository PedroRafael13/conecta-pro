"""Controllers do módulo de Integração REP."""

from fastapi import APIRouter

from .device_controller import router as device_router
from .sync_controller import router as sync_router
from .event_controller import router as event_router
from .webhook_controller import router as webhook_router
from .afd_controller import router as afd_router

# Router principal do módulo
router = APIRouter(prefix="/rep", tags=["REP Integration"])

# Inclui sub-routers
router.include_router(device_router)
router.include_router(sync_router)
router.include_router(event_router)
router.include_router(webhook_router)
router.include_router(afd_router)

__all__ = [
    "router",
    "device_router",
    "sync_router",
    "event_router",
    "webhook_router",
    "afd_router",
]
