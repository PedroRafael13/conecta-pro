"""Controllers do módulo Remote Gatehouse."""

from .access_log_controller import router as access_log_router
from .equipment_status_controller import router as equipment_status_router
from .guardian_occurrence_controller import router as occurrence_router
from .guardian_sync_controller import router as sync_router

__all__ = [
    "sync_router",
    "access_log_router",
    "occurrence_router",
    "equipment_status_router",
]
