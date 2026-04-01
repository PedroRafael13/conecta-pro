"""Repositories do módulo de Gestão de Equipamentos."""

from modules.equipment_management.repositories.comodato_repository import (
    ComodatoRepository,
)
from modules.equipment_management.repositories.equipment_repository import (
    EquipmentRepository,
)
from modules.equipment_management.repositories.installation_repository import (
    InstallationRepository,
)
from modules.equipment_management.repositories.maintenance_repository import (
    MaintenanceRepository,
)

__all__ = [
    "EquipmentRepository",
    "InstallationRepository",
    "MaintenanceRepository",
    "ComodatoRepository",
]
