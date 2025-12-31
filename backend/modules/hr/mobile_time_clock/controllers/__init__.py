"""Controllers do módulo Mobile Time Clock."""

from .device_controller import router as device_router
from .checkin_controller import router as checkin_router
from .geofence_controller import router as geofence_router
from .offline_controller import router as offline_router

__all__ = [
    "device_router",
    "checkin_router",
    "geofence_router",
    "offline_router",
]
