"""
Módulo de Gestão de Equipamentos (Segurança Eletrônica).

Gerencia equipamentos de segurança eletrônica:
- Cadastro de equipamentos (câmeras, alarmes, sensores, etc.)
- Instalações
- Manutenções preventivas e corretivas
- Comodato
- Technology Park (parque tecnológico por cliente)
- IA para manutenção preditiva
"""

# Models e Enums (sempre disponíveis)
from modules.equipment_management.models import (
    Equipment,
    EquipmentCategory,
    EquipmentComodato,
    EquipmentInstallation,
    EquipmentMaintenance,
    EquipmentStatus,
    EquipmentType,
)

# Schemas (sempre disponíveis)
from modules.equipment_management.schemas import (
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
    from modules.equipment_management.controllers import (
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
    from modules.equipment_management.services import (
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
