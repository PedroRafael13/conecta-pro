"""
Models do módulo Facilities.
"""

from modules.facilities.models.area import Area, AreaStatus, AreaType
from modules.facilities.models.checklist import Checklist, ChecklistItem, ChecklistStatus
from modules.facilities.models.inspection import (
    Inspection,
    InspectionResult,
    InspectionStatus,
    InspectionType,
)
from modules.facilities.models.maintenance import (
    Maintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)
from modules.facilities.models.service_request import (
    ServiceRequest,
    ServiceRequestPriority,
    ServiceRequestStatus,
)

__all__ = [
    # Area
    "Area",
    "AreaType",
    "AreaStatus",
    # Maintenance
    "Maintenance",
    "MaintenanceType",
    "MaintenanceStatus",
    "MaintenancePriority",
    # Inspection
    "Inspection",
    "InspectionType",
    "InspectionStatus",
    "InspectionResult",
    # Checklist
    "Checklist",
    "ChecklistItem",
    "ChecklistStatus",
    # ServiceRequest
    "ServiceRequest",
    "ServiceRequestStatus",
    "ServiceRequestPriority",
]
