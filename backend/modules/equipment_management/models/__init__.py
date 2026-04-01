"""Models do módulo de Gestão de Equipamentos."""

from modules.equipment_management.models.comodato import (
    ComodatoStatus,
    EquipmentComodato,
)
from modules.equipment_management.models.equipment import (
    Equipment,
    EquipmentCategory,
    EquipmentStatus,
    EquipmentType,
)
from modules.equipment_management.models.installation import (
    EquipmentInstallation,
    InstallationStatus,
)
from modules.equipment_management.models.maintenance import (
    EquipmentMaintenance,
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)

__all__ = [
    "Equipment",
    "EquipmentType",
    "EquipmentCategory",
    "EquipmentStatus",
    "EquipmentInstallation",
    "InstallationStatus",
    "EquipmentMaintenance",
    "MaintenanceType",
    "MaintenanceStatus",
    "MaintenancePriority",
    "EquipmentComodato",
    "ComodatoStatus",
]
