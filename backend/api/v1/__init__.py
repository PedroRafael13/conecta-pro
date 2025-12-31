"""
API v1 - Router principal.
"""

from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from modules.crm.controllers import (
    commission_router,
    contract_router,
    dashboard_router,
    lead_router,
    opportunity_router,
    proposal_router,
)

# ===================================================================
# GUARDIAN UNIFIED v3.0.0 - MÓDULO 9
# ===================================================================
from modules.guardian.controllers import (
    # Segurança Física (Legacy)
    sync_router,
    access_log_router,
    occurrence_router,
    equipment_status_router,
    # Segurança Cibernética + CAMPO
    security_audit_router,
    ssh_gateway_router,
    campo_service_router,
)

router = APIRouter(prefix="/api/v1")

# ===================================================================
# ROUTERS EXISTENTES
# ===================================================================
router.include_router(auth_router)
router.include_router(lead_router)
router.include_router(opportunity_router)
router.include_router(proposal_router)
router.include_router(commission_router)
router.include_router(dashboard_router)
router.include_router(contract_router)

# ===================================================================
# GUARDIAN UNIFIED - TODOS OS ROUTERS
# ===================================================================
# Segurança Física (Portaria Remota Absorvida)
router.include_router(sync_router, prefix="")
router.include_router(access_log_router, prefix="")
router.include_router(occurrence_router, prefix="")
router.include_router(equipment_status_router, prefix="")

# Segurança Cibernética
router.include_router(security_audit_router, prefix="")
router.include_router(ssh_gateway_router, prefix="")

# CAMPO Service
router.include_router(campo_service_router, prefix="")
