"""
Clients Module - Models
Sprint 30: Cadastro de Clientes/Condomínios
"""

from modules.clients.models.client import (
    Client,
    ClientType,
    ClientStatus,
    ClientSegment,
    DocumentType,
)
from modules.clients.models.condominium import (
    Condominium,
    CondominiumType,
    CondominiumStatus,
    AdministrationType,
)
from modules.clients.models.unit import (
    Unit,
    UnitType,
    UnitStatus,
)
from modules.clients.models.client_contract import (
    ClientContract,
    ContractServiceType,
    ServiceStatus,
)
from modules.clients.models.integration_settings import (
    IntegrationSettings,
    IntegrationType,
    SyncStatus,
    SyncDirection,
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
