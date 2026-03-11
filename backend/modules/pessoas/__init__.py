"""
Módulo PESSOAS — Agregador
Unifica: recruitment + retention + reimbursement + ged + health_occupational

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Recruitment ---
# --- GED (Gestão Eletrônica de Documentos) ---
from modules.ged.controllers import (
    document_router as ged_document_router,
)
from modules.ged.controllers import (
    folder_router as ged_folder_router,
)
from modules.ged.controllers import (
    share_router as ged_share_router,
)
from modules.ged.controllers import (
    signature_router as ged_signature_router,
)
from modules.ged.controllers import (
    stats_router as ged_stats_router,
)
from modules.ged.controllers import (
    tag_router as ged_tag_router,
)
from modules.ged.controllers import (
    version_router as ged_version_router,
)
from modules.recruitment import router as recruitment_router

# --- Reimbursement ---
from modules.reimbursement import reimbursement_router

# --- Retention ---
from modules.retention import (
    climate_router,
    onboarding_router,
    profile_router,
    turnover_router,
)

__all__ = [
    "recruitment_router",
    "onboarding_router",
    "profile_router",
    "climate_router",
    "turnover_router",
    "reimbursement_router",
    "ged_folder_router",
    "ged_document_router",
    "ged_version_router",
    "ged_share_router",
    "ged_tag_router",
    "ged_signature_router",
    "ged_stats_router",
]
