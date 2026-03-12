"""
Re-exportacao do controller de Onboarding Digital.

Inclui o router de onboarding sob o prefixo /human-resources/onboarding.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["RH - Onboarding"])

try:
    from modules.retention.onboarding.controllers.onboarding_controller import (
        router as onboarding_router,
    )

    router.include_router(onboarding_router)
except ImportError:
    logger.warning("Modulo retention/onboarding/controller nao disponivel para re-export.")
