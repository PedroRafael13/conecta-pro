"""
Controllers do módulo Facilities.
"""

from modules.facilities.controllers.area_controller import router as area_router
from modules.facilities.controllers.checklist_controller import router as checklist_router
from modules.facilities.controllers.inspection_controller import router as inspection_router
from modules.facilities.controllers.maintenance_controller import router as maintenance_router
from modules.facilities.controllers.service_request_controller import (
    router as service_request_router,
)

__all__ = [
    "area_router",
    "maintenance_router",
    "inspection_router",
    "checklist_router",
    "service_request_router",
]
