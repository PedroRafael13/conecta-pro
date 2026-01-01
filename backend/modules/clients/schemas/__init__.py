"""
Clients Module - Schemas
Sprint 30: Cadastro de Clientes/Condomínios
"""

from modules.clients.schemas.client_schemas import (
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
