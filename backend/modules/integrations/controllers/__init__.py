"""
Controllers do módulo de Integrações
Sprint 32: API Gateway / Integrações
Sprint 33: Integration Framework
"""

from modules.integrations.controllers.integration_controller import router as integration_router
from modules.integrations.controllers.connector_controller import router as connector_router

__all__ = [
    "integration_router",
    "connector_router",
]
