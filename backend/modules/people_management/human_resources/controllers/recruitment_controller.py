"""
Re-exportacao dos controllers de Recrutamento.

Inclui todos os routers de recrutamento (candidatos, vagas,
aplicacoes, entrevistas) sob o prefixo /human-resources/recruitment.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recruitment", tags=["RH - Recrutamento"])

try:
    from modules.recruitment.controllers.candidate_controller import (
        router as candidate_router,
    )

    router.include_router(candidate_router)
except ImportError:
    logger.warning("Modulo recruitment/candidate_controller nao disponivel para re-export.")

try:
    from modules.recruitment.controllers.job_position_controller import (
        router as job_position_router,
    )

    router.include_router(job_position_router)
except ImportError:
    logger.warning("Modulo recruitment/job_position_controller nao disponivel para re-export.")

try:
    from modules.recruitment.controllers.application_controller import (
        router as application_router,
    )

    router.include_router(application_router)
except ImportError:
    logger.warning("Modulo recruitment/application_controller nao disponivel para re-export.")

try:
    from modules.recruitment.controllers.interview_controller import (
        router as interview_router,
    )

    router.include_router(interview_router)
except ImportError:
    logger.warning("Modulo recruitment/interview_controller nao disponivel para re-export.")
