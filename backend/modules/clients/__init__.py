"""
Module: clients
Description: Modulo de Cadastro de Clientes e Condominios
Author: Conecta PRO Team
Date: 2026-01-10
Sprint: 30 - Cadastro de Clientes/Condominios
Quality Score Target: 99+/100

Este modulo fornece:
- Gestao completa de clientes (administradoras, sindicos, empresas)
- Cadastro de condominios com tipos e configuracoes
- Gestao de unidades (apartamentos, salas, lojas)
- Contratos de servicos por cliente
- Configuracoes de integracao por cliente

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

from fastapi import APIRouter

# Importa router do controller
from modules.clients.controllers import router as client_router

# Cria router principal do modulo
clients_router = APIRouter(prefix="/clients", tags=["Clients - Gestao de Clientes"])

# Inclui sub-router
clients_router.include_router(client_router)

# Exporta tambem o router antigo para compatibilidade
router = clients_router

# Re-export dos models principais
from modules.clients.models import (
    # Client
    Client,
    ClientType,
    ClientStatus,
    ClientSegment,
    DocumentType,
    # Condominium
    Condominium,
    CondominiumType,
    CondominiumStatus,
    AdministrationType,
    # Unit
    Unit,
    UnitType,
    UnitStatus,
    # ClientContract
    ClientContract,
    ContractServiceType,
    ServiceStatus,
    # IntegrationSettings
    IntegrationSettings,
    IntegrationType,
    SyncStatus,
    SyncDirection,
)

# Re-export dos schemas principais
from modules.clients.schemas import (
    # Client
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
    ClientStats,
    ClientFilter,
    # Condominium
    CondominiumCreate,
    CondominiumUpdate,
    CondominiumResponse,
    CondominiumListResponse,
    CondominiumStats,
    # Unit
    UnitCreate,
    UnitUpdate,
    UnitResponse,
    UnitListResponse,
    UnitStats,
    # ClientContract
    ClientContractCreate,
    ClientContractUpdate,
    ClientContractResponse,
    # IntegrationSettings
    IntegrationSettingsCreate,
    IntegrationSettingsUpdate,
    IntegrationSettingsResponse,
)

# Re-export dos services principais
from modules.clients.services import (
    ClientService,
    ClientAIService,
)

# Re-export do repository
from modules.clients.repositories import (
    ClientRepository,
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
