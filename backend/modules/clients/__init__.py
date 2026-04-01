"""
Module: clients
Description: Modulo de Cadastro de Clientes e Condominios
Author: Conecta PRO Team
Date: 2026-01-10

DEPRECATED: Use 'modules.comercial' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.clients' is deprecated. "
    "Use 'modules.comercial' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from fastapi import APIRouter  # noqa: E402

# Importa router do controller
from modules.clients.controllers import router as client_router  # noqa: E402

# Cria router principal do modulo
clients_router = APIRouter(prefix="/clients", tags=["Clients - Gestao de Clientes"])

# Inclui sub-router
clients_router.include_router(client_router)

# Exporta tambem o router antigo para compatibilidade
router = clients_router

# Re-export dos models principais
from modules.clients.models import (  # noqa: E402
    AdministrationType,
    # Client
    Client,
    # ClientContract
    ClientContract,
    ClientSegment,
    ClientStatus,
    ClientType,
    # Condominium
    Condominium,
    CondominiumStatus,
    CondominiumType,
    ContractServiceType,
    DocumentType,
    # IntegrationSettings
    IntegrationSettings,
    IntegrationType,
    ServiceStatus,
    SyncDirection,
    SyncStatus,
    # Unit
    Unit,
    UnitStatus,
    UnitType,
)

# Re-export do repository
from modules.clients.repositories import (  # noqa: E402
    ClientRepository,
)

# Re-export dos schemas principais
from modules.clients.schemas import (  # noqa: E402
    # ClientContract
    ClientContractCreate,
    ClientContractResponse,
    ClientContractUpdate,
    # Client
    ClientCreate,
    ClientFilter,
    ClientListResponse,
    ClientResponse,
    ClientStats,
    ClientUpdate,
    # Condominium
    CondominiumCreate,
    CondominiumListResponse,
    CondominiumResponse,
    CondominiumStats,
    CondominiumUpdate,
    # IntegrationSettings
    IntegrationSettingsCreate,
    IntegrationSettingsResponse,
    IntegrationSettingsUpdate,
    # Unit
    UnitCreate,
    UnitListResponse,
    UnitResponse,
    UnitStats,
    UnitUpdate,
)

# Re-export dos services principais
from modules.clients.services import (  # noqa: E402
    ClientAIService,
    ClientService,
)

__all__ = [
    # Router principal
    "clients_router",
    "router",
    "client_router",
    # Models - Client
    "Client",
    "ClientType",
    "ClientStatus",
    "ClientSegment",
    "DocumentType",
    # Models - Condominium
    "Condominium",
    "CondominiumType",
    "CondominiumStatus",
    "AdministrationType",
    # Models - Unit
    "Unit",
    "UnitType",
    "UnitStatus",
    # Models - ClientContract
    "ClientContract",
    "ContractServiceType",
    "ServiceStatus",
    # Models - IntegrationSettings
    "IntegrationSettings",
    "IntegrationType",
    "SyncStatus",
    "SyncDirection",
    # Schemas - Client
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListResponse",
    "ClientStats",
    "ClientFilter",
    # Schemas - Condominium
    "CondominiumCreate",
    "CondominiumUpdate",
    "CondominiumResponse",
    "CondominiumListResponse",
    "CondominiumStats",
    # Schemas - Unit
    "UnitCreate",
    "UnitUpdate",
    "UnitResponse",
    "UnitListResponse",
    "UnitStats",
    # Schemas - ClientContract
    "ClientContractCreate",
    "ClientContractUpdate",
    "ClientContractResponse",
    # Schemas - IntegrationSettings
    "IntegrationSettingsCreate",
    "IntegrationSettingsUpdate",
    "IntegrationSettingsResponse",
    # Services
    "ClientService",
    "ClientAIService",
    # Repositories
    "ClientRepository",
]

__version__ = "1.0.0"
