"""
Repositories do módulo de Integrações
Sprint 32: API Gateway / Integrações
Sprint 33: Integration Framework
"""

from modules.integrations.repositories.integration_repository import (
    IntegrationRepository,
)
from modules.integrations.repositories.connector_repository import (
    ConnectorRepository,
)

__all__ = [
    "IntegrationRepository",
    "ConnectorRepository",
]
