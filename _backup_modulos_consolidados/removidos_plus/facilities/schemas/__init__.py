"""
Schemas Pydantic do módulo Facilities.
"""

from modules.facilities.schemas.area import (
    AreaCreate,
    AreaFilter,
    AreaListResponse,
    AreaResponse,
    AreaStats,
    AreaUpdate,
)
from modules.facilities.schemas.checklist import (
    ChecklistCreate,
    ChecklistFilter,
    ChecklistItemCreate,
    ChecklistItemResponse,
    ChecklistItemUpdate,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistStats,
    ChecklistUpdate,
)
from modules.facilities.schemas.inspection import (
    InspectionCreate,
    InspectionFilter,
    InspectionListResponse,
    InspectionResponse,
    InspectionStats,
    InspectionUpdate,
)
from modules.facilities.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceListResponse,
    MaintenanceResponse,
    MaintenanceStats,
    MaintenanceUpdate,
)
from modules.facilities.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestFilter,
    ServiceRequestListResponse,
    ServiceRequestResponse,
    ServiceRequestStats,
    ServiceRequestUpdate,
)

__all__ = [
    # Area
    "AreaCreate",
    "AreaUpdate",
    "AreaResponse",
    "AreaListResponse",
    "AreaFilter",
    "AreaStats",
    # Maintenance
    "MaintenanceCreate",
    "MaintenanceUpdate",
    "MaintenanceResponse",
    "MaintenanceListResponse",
    "MaintenanceFilter",
    "MaintenanceStats",
    # Inspection
    "InspectionCreate",
    "InspectionUpdate",
    "InspectionResponse",
    "InspectionListResponse",
    "InspectionFilter",
    "InspectionStats",
    # Checklist
    "ChecklistCreate",
    "ChecklistUpdate",
    "ChecklistResponse",
    "ChecklistListResponse",
    "ChecklistFilter",
    "ChecklistStats",
    "ChecklistItemCreate",
    "ChecklistItemUpdate",
    "ChecklistItemResponse",
    # ServiceRequest
    "ServiceRequestCreate",
    "ServiceRequestUpdate",
    "ServiceRequestResponse",
    "ServiceRequestListResponse",
    "ServiceRequestFilter",
    "ServiceRequestStats",
]
