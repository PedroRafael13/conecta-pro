"""Controllers do módulo de Gestão de Equipamentos."""

from modules.equipment_management.controllers.equipment_controller import (
    router as equipment_router,
)
from modules.equipment_management.controllers.installation_controller import (
    router as installation_router,
)
from modules.equipment_management.controllers.maintenance_controller import (
    router as maintenance_router,
)
from modules.equipment_management.controllers.comodato_controller import (
    router as comodato_router,
)

__all__ = [
    "equipment_router",
    "installation_router",
    "maintenance_router",
    "comodato_router",
]
