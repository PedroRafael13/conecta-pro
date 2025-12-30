"""Controllers do módulo de Moradores."""

from modules.residents.controllers.resident_controller import (
    router as resident_router,
)
from modules.residents.controllers.vehicle_controller import (
    router as vehicle_router,
)
from modules.residents.controllers.pet_controller import (
    router as pet_router,
)
from modules.residents.controllers.dependent_controller import (
    router as dependent_router,
)
from modules.residents.controllers.emergency_contact_controller import (
    router as emergency_contact_router,
)
from modules.residents.controllers.resident_ai_controller import (
    router as resident_ai_router,
)

__all__ = [
    "resident_router",
    "vehicle_router",
    "pet_router",
    "dependent_router",
    "emergency_contact_router",
    "resident_ai_router",
]
