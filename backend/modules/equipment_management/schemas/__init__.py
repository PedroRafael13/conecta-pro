"""Schemas do módulo de Gestão de Equipamentos."""

from modules.equipment_management.schemas.comodato import (
    ComodatoCreate,
    ComodatoFilter,
    ComodatoListResponse,
    ComodatoResponse,
    ComodatoUpdate,
)
from modules.equipment_management.schemas.equipment import (
    EquipmentCreate,
    EquipmentFilter,
    EquipmentListResponse,
    EquipmentResponse,
    EquipmentStats,
    EquipmentUpdate,
)
from modules.equipment_management.schemas.installation import (
    InstallationCreate,
    InstallationFilter,
    InstallationListResponse,
    InstallationResponse,
    InstallationUpdate,
)
from modules.equipment_management.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceFilter,
    MaintenanceListResponse,
    MaintenanceResponse,
    MaintenanceStats,
    MaintenanceUpdate,
)

__all__ = [
    "EquipmentCreate",
    "EquipmentUpdate",
    "EquipmentResponse",
    "EquipmentFilter",
    "EquipmentListResponse",
    "EquipmentStats",
    "InstallationCreate",
    "InstallationUpdate",
    "InstallationResponse",
    "InstallationFilter",
    "InstallationListResponse",
    "MaintenanceCreate",
    "MaintenanceUpdate",
    "MaintenanceResponse",
    "MaintenanceFilter",
    "MaintenanceListResponse",
    "MaintenanceStats",
    "ComodatoCreate",
    "ComodatoUpdate",
    "ComodatoResponse",
    "ComodatoFilter",
    "ComodatoListResponse",
]
