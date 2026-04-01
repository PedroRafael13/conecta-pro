"""
Controllers do módulo de Configurações e Multi-tenant
Sprint 35: Configurações e Multi-tenant
"""

from fastapi import APIRouter

from modules.config.controllers.config_controller import router as _config_router

# Agrega config + security/lgpd num único router sem prefix
# para que main_production.py (ZONA PROIBIDA) não precise ser alterado.
try:
    from modules.security_lgpd import security_lgpd_router as _lgpd_router

    router = APIRouter()
    router.include_router(_config_router)
    router.include_router(_lgpd_router, prefix="/security")
except Exception:
    router = _config_router

__all__ = ["router"]
