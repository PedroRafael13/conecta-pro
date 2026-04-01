"""
Controllers do módulo de Integrações
Sprint 32: API Gateway / Integrações
Sprint 33: Integration Framework
"""

from fastapi import APIRouter

from modules.integrations.banking.controllers.banking_controller import router as banking_router
from modules.integrations.controllers.connector_controller import router as connector_router
from modules.integrations.controllers.integration_controller import router as integration_router
from modules.integrations.controllers.solides_controller import router as solides_router

# Router principal que agrega os sub-routers
# Nota: Não usar prefix aqui pois api/v1/__init__.py já adiciona /integrations
router = APIRouter(tags=["Integrations"])
router.include_router(integration_router)
router.include_router(connector_router)
router.include_router(solides_router)
router.include_router(banking_router)

__all__ = [
    "router",
    "integration_router",
    "connector_router",
    "solides_router",
    "banking_router",
]
