"""
Re-exportacao do controller de Predicao de Turnover.

Inclui o router de turnover sob o prefixo /human-resources/turnover.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/turnover", tags=["RH - Turnover"])

try:
    from modules.retention.turnover.controllers.turnover_controller import (
        router as turnover_router,
    )

    router.include_router(turnover_router)
except ImportError:
    logger.warning("Modulo retention/turnover/controller nao disponivel para re-export.")
