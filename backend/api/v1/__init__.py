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

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(lead_router)
router.include_router(opportunity_router)
router.include_router(proposal_router)
router.include_router(commission_router)
router.include_router(dashboard_router)
router.include_router(contract_router)
