"""
Client Schemas - Pydantic Models
Sprint 30: Cadastro de Clientes/Condomínios
"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.clients.models.client import (
    ClientType, ClientStatus, ClientSegment, DocumentType
)
from modules.clients.models.condominium import (
    CondominiumType, CondominiumStatus, AdministrationType
)
from modules.clients.models.unit import UnitType, UnitStatus
from modules.clients.models.client_contract import ContractServiceType, ServiceStatus
from modules.clients.models.integration_settings import (
    IntegrationType, SyncStatus, SyncDirection
)


# =============================================================================
# CLIENT SCHEMAS
# =============================================================================

class ClientBase(BaseModel):
    """Base schema for Client."""
    type: ClientType = Field(default=ClientType.CONDOMINIO)
    segment: Optional[ClientSegment] = None
    legal_name: str = Field(..., min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    document_type: DocumentType = Field(default=DocumentType.CNPJ)
    document_number: str = Field(..., min_length=11, max_length=20)
    state_registration: Optional[str] = Field(None, max_length=20)
    municipal_registration: Optional[str] = Field(None, max_length=20)

    # Endereço
    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zipcode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # Contatos
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    email_billing: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=200)

    # Contato principal
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=200)
    contact_role: Optional[str] = Field(None, max_length=50)

    # Dados financeiros
    payment_terms: Optional[int] = Field(None, ge=0, le=365)
    credit_limit: Optional[Decimal] = Field(None, ge=0)

    # Dados comerciais
    sales_rep_id: Optional[UUID] = None
    sales_rep_name: Optional[str] = Field(None, max_length=100)
    acquisition_source: Optional[str] = Field(None, max_length=50)

    # Configurações
    settings: Optional[dict] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_vip: bool = False

    @field_validator("document_number")
    @classmethod
    def validate_document(cls, v: str) -> str:
        """Valida e formata documento."""
        return re.sub(r"\D", "", v)

    @field_validator("address_zipcode")
    @classmethod
    def validate_zipcode(cls, v: Optional[str]) -> Optional[str]:
        """Valida CEP."""
        if v:
            return re.sub(r"\D", "", v)
        return v


class ClientCreate(ClientBase):
    """Schema for creating a client."""


class ClientUpdate(BaseModel):
    """Schema for updating a client."""
    type: Optional[ClientType] = None
    status: Optional[ClientStatus] = None
    segment: Optional[ClientSegment] = None
    legal_name: Optional[str] = Field(None, min_length=2, max_length=200)
    trade_name: Optional[str] = Field(None, max_length=200)
    document_number: Optional[str] = Field(None, max_length=20)
    state_registration: Optional[str] = Field(None, max_length=20)
    municipal_registration: Optional[str] = Field(None, max_length=20)

    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zipcode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    email_billing: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=200)

    contact_name: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=200)
    contact_role: Optional[str] = Field(None, max_length=50)

    payment_terms: Optional[int] = Field(None, ge=0, le=365)
    credit_limit: Optional[Decimal] = Field(None, ge=0)

    sales_rep_id: Optional[UUID] = None
    sales_rep_name: Optional[str] = Field(None, max_length=100)

    settings: Optional[dict] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_vip: Optional[bool] = None


class ClientResponse(BaseModel):
    """Schema for client response."""
    id: UUID
    code: str
    type: ClientType
    status: ClientStatus
    segment: Optional[ClientSegment]
    legal_name: str
    trade_name: Optional[str]
    document_type: DocumentType
    document_number: str
    formatted_document: str
    display_name: str
    full_address: str

    address_street: Optional[str]
    address_number: Optional[str]
    address_complement: Optional[str]
    address_neighborhood: Optional[str]
    address_city: Optional[str]
    address_state: Optional[str]
    address_zipcode: Optional[str]

    phone: Optional[str]
    email: Optional[str]
    contact_name: Optional[str]

    payment_terms: Optional[int]
    credit_limit: Optional[Decimal]
    current_balance: Optional[Decimal]
    is_defaulter: bool
    total_debt: Optional[Decimal]

    total_contracts: int
    active_contracts: int
    total_revenue: Optional[Decimal]
    satisfaction_score: Optional[Decimal]
    health_score: int

    guardian_enabled: bool
    plus_enabled: bool

    is_active: bool
    is_vip: bool
    tags: Optional[List[str]]

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientListResponse(BaseModel):
    """Schema for client list response."""
    id: UUID
    code: str
    type: ClientType
    status: ClientStatus
    legal_name: str
    trade_name: Optional[str]
    display_name: str
    document_number: str
    address_city: Optional[str]
    address_state: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_defaulter: bool
    active_contracts: int
    health_score: int
    is_vip: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientStats(BaseModel):
    """Schema for client statistics."""
    total_clients: int = 0
    active_clients: int = 0
    inactive_clients: int = 0
    defaulter_clients: int = 0
    vip_clients: int = 0
    by_type: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    by_segment: dict = Field(default_factory=dict)
    total_revenue: Decimal = Decimal("0")
    average_contracts_per_client: float = 0.0


class ClientFilter(BaseModel):
    """Schema for filtering clients."""
    type: Optional[ClientType] = None
    status: Optional[ClientStatus] = None
    segment: Optional[ClientSegment] = None
    is_defaulter: Optional[bool] = None
    is_vip: Optional[bool] = None
    guardian_enabled: Optional[bool] = None
    plus_enabled: Optional[bool] = None
    city: Optional[str] = None
    state: Optional[str] = None
    sales_rep_id: Optional[UUID] = None
    search: Optional[str] = None


# =============================================================================
# CONDOMINIUM SCHEMAS
# =============================================================================

class CondominiumBase(BaseModel):
    """Base schema for Condominium."""
    name: str = Field(..., min_length=2, max_length=200)
    type: CondominiumType = Field(default=CondominiumType.RESIDENTIAL)
    administration_type: Optional[AdministrationType] = None
    cnpj: Optional[str] = Field(None, max_length=20)

    address_street: str = Field(..., min_length=2, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: str = Field(..., min_length=2, max_length=100)
    address_state: str = Field(..., min_length=2, max_length=2)
    address_zipcode: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    phone: Optional[str] = Field(None, max_length=20)
    phone_portaria: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)

    syndic_name: Optional[str] = Field(None, max_length=100)
    syndic_phone: Optional[str] = Field(None, max_length=20)
    syndic_email: Optional[str] = Field(None, max_length=200)

    total_units: int = Field(default=0, ge=0)
    total_towers: Optional[int] = Field(None, ge=0)
    total_floors: Optional[int] = Field(None, ge=0)
    total_elevators: Optional[int] = Field(None, ge=0)
    total_parking_spots: Optional[int] = Field(None, ge=0)
    total_area_m2: Optional[Decimal] = Field(None, ge=0)

    has_pool: bool = False
    has_gym: bool = False
    has_party_room: bool = False
    has_playground: bool = False
    has_24h_security: bool = False
    has_cctv: bool = False
    has_access_control: bool = False

    settings: Optional[dict] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CondominiumCreate(CondominiumBase):
    """Schema for creating a condominium."""
    client_id: UUID


class CondominiumUpdate(BaseModel):
    """Schema for updating a condominium."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    type: Optional[CondominiumType] = None
    status: Optional[CondominiumStatus] = None
    administration_type: Optional[AdministrationType] = None
    cnpj: Optional[str] = Field(None, max_length=20)

    address_street: Optional[str] = Field(None, max_length=200)
    address_number: Optional[str] = Field(None, max_length=20)
    address_complement: Optional[str] = Field(None, max_length=100)
    address_neighborhood: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=100)
    address_state: Optional[str] = Field(None, max_length=2)
    address_zipcode: Optional[str] = Field(None, max_length=10)

    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)

    syndic_name: Optional[str] = Field(None, max_length=100)
    syndic_phone: Optional[str] = Field(None, max_length=20)
    syndic_email: Optional[str] = Field(None, max_length=200)
    syndic_start_date: Optional[date] = None
    syndic_end_date: Optional[date] = None

    total_units: Optional[int] = Field(None, ge=0)
    total_towers: Optional[int] = Field(None, ge=0)

    has_pool: Optional[bool] = None
    has_gym: Optional[bool] = None
    has_party_room: Optional[bool] = None
    has_24h_security: Optional[bool] = None
    has_cctv: Optional[bool] = None
    has_access_control: Optional[bool] = None

    settings: Optional[dict] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_premium: Optional[bool] = None


class CondominiumResponse(BaseModel):
    """Schema for condominium response."""
    id: UUID
    code: str
    client_id: UUID
    name: str
    type: CondominiumType
    status: CondominiumStatus
    administration_type: Optional[AdministrationType]
    cnpj: Optional[str]
    full_address: str
    address_city: str
    address_state: str

    syndic_name: Optional[str]
    syndic_phone: Optional[str]
    syndic_mandate_active: bool

    total_units: int
    occupied_units: int
    occupancy_rate: float
    total_towers: Optional[int]

    security_level: str
    amenities_count: int

    guardian_enabled: bool
    plus_enabled: bool
    is_active: bool
    is_premium: bool

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CondominiumListResponse(BaseModel):
    """Schema for condominium list response."""
    id: UUID
    code: str
    client_id: UUID
    name: str
    type: CondominiumType
    status: CondominiumStatus
    address_city: str
    address_state: str
    total_units: int
    occupancy_rate: float
    security_level: str
    is_premium: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CondominiumStats(BaseModel):
    """Schema for condominium statistics."""
    total_condominiums: int = 0
    active_condominiums: int = 0
    total_units: int = 0
    occupied_units: int = 0
    average_occupancy_rate: float = 0.0
    by_type: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    by_city: dict = Field(default_factory=dict)


# =============================================================================
# UNIT SCHEMAS
# =============================================================================

class UnitBase(BaseModel):
    """Base schema for Unit."""
    number: str = Field(..., min_length=1, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    tower: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = None
    type: UnitType = Field(default=UnitType.APARTAMENTO)

    area_m2: Optional[Decimal] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    parking_spots: Optional[int] = Field(None, ge=0)

    owner_name: Optional[str] = Field(None, max_length=200)
    owner_document: Optional[str] = Field(None, max_length=20)
    owner_phone: Optional[str] = Field(None, max_length=20)
    owner_email: Optional[str] = Field(None, max_length=200)

    monthly_fee: Optional[Decimal] = Field(None, ge=0)
    fraction: Optional[Decimal] = Field(None, ge=0, le=1)

    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class UnitCreate(UnitBase):
    """Schema for creating a unit."""
    condominium_id: UUID


class UnitUpdate(BaseModel):
    """Schema for updating a unit."""
    number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    tower: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = None
    type: Optional[UnitType] = None
    status: Optional[UnitStatus] = None

    area_m2: Optional[Decimal] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[int] = Field(None, ge=0)
    parking_spots: Optional[int] = Field(None, ge=0)

    owner_name: Optional[str] = Field(None, max_length=200)
    owner_document: Optional[str] = Field(None, max_length=20)
    owner_phone: Optional[str] = Field(None, max_length=20)
    owner_email: Optional[str] = Field(None, max_length=200)

    resident_name: Optional[str] = Field(None, max_length=200)
    resident_phone: Optional[str] = Field(None, max_length=20)
    resident_email: Optional[str] = Field(None, max_length=200)
    is_tenant: Optional[bool] = None

    monthly_fee: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class UnitResponse(BaseModel):
    """Schema for unit response."""
    id: UUID
    code: str
    condominium_id: UUID
    number: str
    block: Optional[str]
    tower: Optional[str]
    floor: Optional[int]
    type: UnitType
    status: UnitStatus
    display_name: str
    short_name: str

    area_m2: Optional[Decimal]
    bedrooms: Optional[int]
    parking_spots: Optional[int]

    owner_name: Optional[str]
    resident_name: Optional[str]
    current_resident: Optional[str]
    is_tenant: bool
    is_occupied: bool

    monthly_fee: Optional[Decimal]
    total_fee: Decimal
    is_defaulter: bool
    debt_amount: Optional[Decimal]

    has_access_credentials: bool
    total_authorized_persons: int
    total_vehicles: int

    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UnitListResponse(BaseModel):
    """Schema for unit list response."""
    id: UUID
    code: str
    number: str
    block: Optional[str]
    tower: Optional[str]
    type: UnitType
    status: UnitStatus
    display_name: str
    current_resident: Optional[str]
    is_occupied: bool
    is_defaulter: bool
    monthly_fee: Optional[Decimal]

    model_config = {"from_attributes": True}


class UnitStats(BaseModel):
    """Schema for unit statistics."""
    total_units: int = 0
    occupied_units: int = 0
    available_units: int = 0
    defaulter_units: int = 0
    occupancy_rate: float = 0.0
    by_type: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    total_monthly_fees: Decimal = Decimal("0")


# =============================================================================
# CLIENT CONTRACT SCHEMAS
# =============================================================================

class ClientContractBase(BaseModel):
    """Base schema for ClientContract."""
    service_type: ContractServiceType
    description: Optional[str] = Field(None, max_length=500)
    scope: Optional[str] = None
    monthly_value: Optional[Decimal] = Field(None, ge=0)
    setup_fee: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sla_response_time_minutes: Optional[int] = Field(None, ge=0)
    sla_resolution_time_hours: Optional[int] = Field(None, ge=0)
    is_24h: bool = False
    auto_renew: bool = True
    settings: Optional[dict] = None
    features: Optional[List[str]] = None
    notes: Optional[str] = None


class ClientContractCreate(ClientContractBase):
    """Schema for creating a client contract."""
    client_id: UUID
    contract_id: Optional[UUID] = None
    condominium_id: Optional[UUID] = None


class ClientContractUpdate(BaseModel):
    """Schema for updating a client contract."""
    service_type: Optional[ContractServiceType] = None
    status: Optional[ServiceStatus] = None
    description: Optional[str] = Field(None, max_length=500)
    scope: Optional[str] = None
    monthly_value: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    end_date: Optional[date] = None
    sla_response_time_minutes: Optional[int] = Field(None, ge=0)
    sla_resolution_time_hours: Optional[int] = Field(None, ge=0)
    settings: Optional[dict] = None
    features: Optional[List[str]] = None
    notes: Optional[str] = None
    auto_renew: Optional[bool] = None


class ClientContractResponse(BaseModel):
    """Schema for client contract response."""
    id: UUID
    client_id: UUID
    contract_id: Optional[UUID]
    condominium_id: Optional[UUID]
    service_type: ContractServiceType
    status: ServiceStatus
    description: Optional[str]
    monthly_value: Optional[Decimal]
    final_value: Optional[Decimal]
    start_date: Optional[date]
    end_date: Optional[date]
    days_until_end: Optional[int]
    is_expiring_soon: bool
    is_guardian_service: bool
    is_plus_service: bool
    is_active: bool
    is_main_service: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# INTEGRATION SETTINGS SCHEMAS
# =============================================================================

class IntegrationSettingsBase(BaseModel):
    """Base schema for IntegrationSettings."""
    integration_type: IntegrationType
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sync_direction: SyncDirection = Field(default=SyncDirection.BIDIRECTIONAL)
    api_url: Optional[str] = Field(None, max_length=500)
    sync_interval_minutes: Optional[int] = Field(None, ge=1)
    auto_sync: bool = True
    sync_on_change: bool = True
    settings: Optional[dict] = None
    notes: Optional[str] = None


class IntegrationSettingsCreate(IntegrationSettingsBase):
    """Schema for creating integration settings."""
    client_id: UUID
    api_key: Optional[str] = Field(None, max_length=500)
    api_secret: Optional[str] = Field(None, max_length=500)
    webhook_url: Optional[str] = Field(None, max_length=500)
    webhook_secret: Optional[str] = Field(None, max_length=200)


class IntegrationSettingsUpdate(BaseModel):
    """Schema for updating integration settings."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sync_direction: Optional[SyncDirection] = None
    api_url: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = Field(None, max_length=500)
    api_secret: Optional[str] = Field(None, max_length=500)
    webhook_url: Optional[str] = Field(None, max_length=500)
    sync_interval_minutes: Optional[int] = Field(None, ge=1)
    auto_sync: Optional[bool] = None
    sync_on_change: Optional[bool] = None
    settings: Optional[dict] = None
    notes: Optional[str] = None
    is_enabled: Optional[bool] = None


class IntegrationSettingsResponse(BaseModel):
    """Schema for integration settings response."""
    id: UUID
    client_id: UUID
    integration_type: IntegrationType
    name: str
    description: Optional[str]
    sync_status: SyncStatus
    sync_direction: SyncDirection
    api_url: Optional[str]
    external_client_id: Optional[str]
    webhook_url: Optional[str]
    sync_interval_minutes: Optional[int]
    last_sync_at: Optional[datetime]
    last_sync_success_at: Optional[datetime]
    last_sync_error: Optional[str]
    success_rate: float
    total_syncs: int
    records_synced: int
    is_configured: bool
    is_enabled: bool
    is_active: bool
    auto_sync: bool
    created_at: datetime

    model_config = {"from_attributes": True}
