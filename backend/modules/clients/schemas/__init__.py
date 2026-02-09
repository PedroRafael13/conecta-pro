"""
Clients Module - Schemas
Sprint 30: Cadastro de Clientes/Condomínios
"""

from modules.clients.schemas.client_schemas import (
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

__all__ = [
    # Client
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListResponse",
    "ClientStats",
    "ClientFilter",
    # Condominium
    "CondominiumCreate",
    "CondominiumUpdate",
    "CondominiumResponse",
    "CondominiumListResponse",
    "CondominiumStats",
    # Unit
    "UnitCreate",
    "UnitUpdate",
    "UnitResponse",
    "UnitListResponse",
    "UnitStats",
    # ClientContract
    "ClientContractCreate",
    "ClientContractUpdate",
    "ClientContractResponse",
    # IntegrationSettings
    "IntegrationSettingsCreate",
    "IntegrationSettingsUpdate",
    "IntegrationSettingsResponse",
]
