"""
Re-exportacao do controller de Clima Organizacional.

Inclui o router de clima sob o prefixo /human-resources/climate.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/climate", tags=["RH - Clima"])

try:
    from modules.retention.climate.controllers.climate_controller import (
        router as climate_router,
    )

    router.include_router(climate_router)
except ImportError:
    logger.warning("Modulo retention/climate/controller nao disponivel para re-export.")
