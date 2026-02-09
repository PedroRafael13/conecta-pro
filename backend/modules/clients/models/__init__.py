"""
Clients Module - Models
Sprint 30: Cadastro de Clientes/Condomínios
"""

from modules.clients.models.client import (
    Client,
    ClientSegment,
    ClientStatus,
    ClientType,
    DocumentType,
)
from modules.clients.models.client_contract import (
    ClientContract,
    ContractServiceType,
    ServiceStatus,
)
from modules.clients.models.condominium import (
    AdministrationType,
    Condominium,
    CondominiumStatus,
    CondominiumType,
)
from modules.clients.models.integration_settings import (
    IntegrationSettings,
    IntegrationType,
    SyncDirection,
    SyncStatus,
)
from modules.clients.models.unit import (
    Unit,
    UnitStatus,
    UnitType,
)

__all__ = [
    # Client
    "Client",
    "ClientType",
    "ClientStatus",
    "ClientSegment",
    "DocumentType",
    # Condominium
    "Condominium",
    "CondominiumType",
    "CondominiumStatus",
    "AdministrationType",
    # Unit
    "Unit",
    "UnitType",
    "UnitStatus",
    # ClientContract
    "ClientContract",
    "ContractServiceType",
    "ServiceStatus",
    # IntegrationSettings
    "IntegrationSettings",
    "IntegrationType",
    "SyncStatus",
    "SyncDirection",
]
