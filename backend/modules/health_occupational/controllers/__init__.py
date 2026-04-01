"""Controllers do modulo de Saude Ocupacional."""

from modules.health_occupational.controllers.epi_controller import router as epi_router
from modules.health_occupational.controllers.health_controller import router as health_router
from modules.health_occupational.controllers.pcmso_controller import router as pcmso_router
from modules.health_occupational.controllers.ppra_controller import router as ppra_router

__all__ = [
    "pcmso_router",
    "ppra_router",
    "epi_router",
    "health_router",
]
