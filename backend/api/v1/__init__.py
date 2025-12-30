"""
API v1 - Router principal.
"""

from fastapi import APIRouter

from .endpoints.auth import router as auth_router
from modules.crm.controllers import lead_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(lead_router)
