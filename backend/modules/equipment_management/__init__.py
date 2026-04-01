"""
Módulo de Gestão de Equipamentos (Segurança Eletrônica).

DEPRECATED: Use 'modules.tecnico' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.equipment_management' is deprecated. "
    "Use 'modules.tecnico' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

# Models e Enums (sempre disponíveis)
from modules.equipment_management.models import (  # noqa: E402
    Equipment,
    EquipmentCategory,
    EquipmentComodato,
    EquipmentInstallation,
    EquipmentMaintenance,
    EquipmentStatus,
    EquipmentType,
)

# Schemas (sempre disponíveis)
from modules.equipment_management.schemas import (  # noqa: E402
    ComodatoCreate,
    ComodatoResponse,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentStats,
    InstallationCreate,
    InstallationResponse,
    MaintenanceCreate,
    MaintenanceResponse,
    MaintenanceStats,
)


def get_routers():
    """Retorna os routers do módulo (lazy import para evitar dependências circulares)."""
    # pylint: disable=import-outside-toplevel
    from modules.equipment_management.controllers import (  # noqa: E402
        comodato_router,
        equipment_router,
        installation_router,
        maintenance_router,
    )

    return {
        "equipment": equipment_router,
        "installation": installation_router,
        "maintenance": maintenance_router,
        "comodato": comodato_router,
    }


def get_services():
    """Retorna os services do módulo (lazy import)."""
    # pylint: disable=import-outside-toplevel
    from modules.equipment_management.services import (  # noqa: E402
        ComodatoService,
        EquipmentService,
        InstallationService,
        MaintenanceAIService,
        MaintenanceService,
    )

    return {
        "equipment": EquipmentService,
        "installation": InstallationService,
        "maintenance": MaintenanceService,
        "comodato": ComodatoService,
        "maintenance_ai": MaintenanceAIService,
    }


__all__ = [
    # Models
    "Equipment",
    "EquipmentInstallation",
    "EquipmentMaintenance",
    "EquipmentComodato",
    # Enums
    "EquipmentType",
    "EquipmentCategory",
    "EquipmentStatus",
    # Schemas
    "EquipmentCreate",
    "EquipmentResponse",
    "EquipmentStats",
    "InstallationCreate",
    "InstallationResponse",
    "MaintenanceCreate",
    "MaintenanceResponse",
    "MaintenanceStats",
    "ComodatoCreate",
    "ComodatoResponse",
    # Functions
    "get_routers",
    "get_services",
]
