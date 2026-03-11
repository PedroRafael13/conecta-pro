"""
Módulo de Recrutamento e Seleção.

DEPRECATED: Use 'modules.pessoas' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.recruitment' is deprecated. "
    "Use 'modules.pessoas' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from fastapi import APIRouter  # noqa: E402

from .controllers import (  # noqa: E402
    application_router,
    candidate_router,
    interview_router,
    job_position_router,
)

# Router principal do módulo
router = APIRouter(prefix="/recruitment", tags=["Recruitment"])

# Inclui sub-routers
router.include_router(job_position_router)
router.include_router(candidate_router)
router.include_router(application_router)
router.include_router(interview_router)

__all__ = [
    "router",
]
