"""
Módulo Facilities - Gestão de Áreas e Manutenção.

Este módulo gerencia:
- Áreas físicas (condomínios, clientes)
- Manutenções programadas e corretivas
- Inspeções e vistorias
- Checklists de vistoria
- Solicitações de serviço
"""

from modules.facilities.models import (
    Area,
    AreaStatus,
    AreaType,
    Checklist,
    ChecklistItem,
    ChecklistStatus,
    Inspection,
    InspectionResult,
    InspectionStatus,
    InspectionType,
    Maintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
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
