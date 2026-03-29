"""
Client Schemas - Pydantic Models
Sprint 30: Cadastro de Clientes/Condomínios
"""

import re
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.clients.models.client import ClientSegment, ClientStatus, ClientType, DocumentType
from modules.clients.models.client_contract import ContractServiceType, ServiceStatus
from modules.clients.models.condominium import AdministrationType, CondominiumStatus, CondominiumType
from modules.clients.models.integration_settings import IntegrationType, SyncDirection, SyncStatus
from modules.clients.models.unit import UnitStatus, UnitType

# =============================================================================
# CLIENT SCHEMAS
# =============================================================================


class ClientBase(BaseModel):
    """Base schema for Client."""

    type: ClientType = Field(default=ClientType.CONDOMINIO)
    segment: ClientSegment | None = None
    legal_name: str = Field(..., min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    document_type: DocumentType = Field(default=DocumentType.CNPJ)
    document_number: str = Field(..., min_length=11, max_length=20)
    state_registration: str | None = Field(None, max_length=20)
    municipal_registration: str | None = Field(None, max_length=20)

    # Endereço
    address_street: str | None = Field(None, max_length=200)
    address_number: str | None = Field(None, max_length=20)
    address_complement: str | None = Field(None, max_length=100)
    address_neighborhood: str | None = Field(None, max_length=100)
    address_city: str | None = Field(None, max_length=100)
    address_state: str | None = Field(None, max_length=2)
    address_zipcode: str | None = Field(None, max_length=10)
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    # Contatos
    phone: str | None = Field(None, max_length=20)
    phone_secondary: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)
    email_billing: str | None = Field(None, max_length=200)
    website: str | None = Field(None, max_length=200)

    # Contato principal
    contact_name: str | None = Field(None, max_length=100)
    contact_phone: str | None = Field(None, max_length=20)
    contact_email: str | None = Field(None, max_length=200)
    contact_role: str | None = Field(None, max_length=50)

    # Dados financeiros
    payment_terms: int | None = Field(None, ge=0, le=365)
    credit_limit: Decimal | None = Field(None, ge=0)

    # Dados comerciais
    sales_rep_id: UUID | None = None
    sales_rep_name: str | None = Field(None, max_length=100)
    acquisition_source: str | None = Field(None, max_length=50)

    # Configurações
    settings: dict | None = None
    tags: list[str] | None = None
    notes: str | None = None
    is_vip: bool = False

    @field_validator("document_number")
    @classmethod
    def validate_document(cls, v: str) -> str:
        """Valida e formata documento."""
        return re.sub(r"\D", "", v)

    @field_validator("address_zipcode")
    @classmethod
    def validate_zipcode(cls, v: str | None) -> str | None:
        """Valida CEP."""
        if v:
            return re.sub(r"\D", "", v)
        return v


class ClientCreate(ClientBase):
    """Schema for creating a client."""


class ClientUpdate(BaseModel):
    """Schema for updating a client."""

    type: ClientType | None = None
    status: ClientStatus | None = None
    segment: ClientSegment | None = None
    legal_name: str | None = Field(None, min_length=2, max_length=200)
    trade_name: str | None = Field(None, max_length=200)
    document_number: str | None = Field(None, max_length=20)
    state_registration: str | None = Field(None, max_length=20)
    municipal_registration: str | None = Field(None, max_length=20)

    address_street: str | None = Field(None, max_length=200)
    address_number: str | None = Field(None, max_length=20)
    address_complement: str | None = Field(None, max_length=100)
    address_neighborhood: str | None = Field(None, max_length=100)
    address_city: str | None = Field(None, max_length=100)
    address_state: str | None = Field(None, max_length=2)
    address_zipcode: str | None = Field(None, max_length=10)
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    phone: str | None = Field(None, max_length=20)
    phone_secondary: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)
    email_billing: str | None = Field(None, max_length=200)
    website: str | None = Field(None, max_length=200)

    contact_name: str | None = Field(None, max_length=100)
    contact_phone: str | None = Field(None, max_length=20)
    contact_email: str | None = Field(None, max_length=200)
    contact_role: str | None = Field(None, max_length=50)

    payment_terms: int | None = Field(None, ge=0, le=365)
    credit_limit: Decimal | None = Field(None, ge=0)

    sales_rep_id: UUID | None = None
    sales_rep_name: str | None = Field(None, max_length=100)

    settings: dict | None = None
    tags: list[str] | None = None
    notes: str | None = None
    is_vip: bool | None = None


class ClientResponse(BaseModel):
    """Schema for client response."""

    id: UUID
    code: str
    type: ClientType
    status: ClientStatus
    segment: ClientSegment | None
    legal_name: str
    trade_name: str | None
    document_type: DocumentType
    document_number: str
    formatted_document: str
    display_name: str
    full_address: str

    address_street: str | None
    address_number: str | None
    address_complement: str | None
    address_neighborhood: str | None
    address_city: str | None
    address_state: str | None
    address_zipcode: str | None

    phone: str | None
    email: str | None
    contact_name: str | None

    payment_terms: int | None
    credit_limit: Decimal | None
    current_balance: Decimal | None
    is_defaulter: bool
    total_debt: Decimal | None

    total_contracts: int
    active_contracts: int
    total_revenue: Decimal | None
    satisfaction_score: Decimal | None
    health_score: int

    plus_enabled: bool

    is_active: bool
    is_vip: bool
    tags: list[str] | None

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
    trade_name: str | None
    display_name: str
    document_number: str
    address_city: str | None
    address_state: str | None
    phone: str | None
    email: str | None
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

    type: ClientType | None = None
    status: ClientStatus | None = None
    segment: ClientSegment | None = None
    is_defaulter: bool | None = None
    is_vip: bool | None = None
    plus_enabled: bool | None = None
    city: str | None = None
    state: str | None = None
    sales_rep_id: UUID | None = None
    search: str | None = None


# =============================================================================
# CONDOMINIUM SCHEMAS
# =============================================================================


class CondominiumBase(BaseModel):
    """Base schema for Condominium."""

    name: str = Field(..., min_length=2, max_length=200)
    type: CondominiumType = Field(default=CondominiumType.RESIDENTIAL)
    administration_type: AdministrationType | None = None
    cnpj: str | None = Field(None, max_length=20)

    address_street: str = Field(..., min_length=2, max_length=200)
    address_number: str | None = Field(None, max_length=20)
    address_complement: str | None = Field(None, max_length=100)
    address_neighborhood: str | None = Field(None, max_length=100)
    address_city: str = Field(..., min_length=2, max_length=100)
    address_state: str = Field(..., min_length=2, max_length=2)
    address_zipcode: str | None = Field(None, max_length=10)
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    phone: str | None = Field(None, max_length=20)
    phone_portaria: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)

    syndic_name: str | None = Field(None, max_length=100)
    syndic_phone: str | None = Field(None, max_length=20)
    syndic_email: str | None = Field(None, max_length=200)

    total_units: int = Field(default=0, ge=0)
    total_towers: int | None = Field(None, ge=0)
    total_floors: int | None = Field(None, ge=0)
    total_elevators: int | None = Field(None, ge=0)
    total_parking_spots: int | None = Field(None, ge=0)
    total_area_m2: Decimal | None = Field(None, ge=0)

    has_pool: bool = False
    has_gym: bool = False
    has_party_room: bool = False
    has_playground: bool = False
    has_24h_security: bool = False
    has_cctv: bool = False
    has_access_control: bool = False

    settings: dict | None = None
    tags: list[str] | None = None
    notes: str | None = None


class CondominiumCreate(CondominiumBase):
    """Schema for creating a condominium."""

    client_id: UUID


class CondominiumUpdate(BaseModel):
    """Schema for updating a condominium."""

    name: str | None = Field(None, min_length=2, max_length=200)
    type: CondominiumType | None = None
    status: CondominiumStatus | None = None
    administration_type: AdministrationType | None = None
    cnpj: str | None = Field(None, max_length=20)

    address_street: str | None = Field(None, max_length=200)
    address_number: str | None = Field(None, max_length=20)
    address_complement: str | None = Field(None, max_length=100)
    address_neighborhood: str | None = Field(None, max_length=100)
    address_city: str | None = Field(None, max_length=100)
    address_state: str | None = Field(None, max_length=2)
    address_zipcode: str | None = Field(None, max_length=10)

    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)

    syndic_name: str | None = Field(None, max_length=100)
    syndic_phone: str | None = Field(None, max_length=20)
    syndic_email: str | None = Field(None, max_length=200)
    syndic_start_date: date | None = None
    syndic_end_date: date | None = None

    total_units: int | None = Field(None, ge=0)
    total_towers: int | None = Field(None, ge=0)

    has_pool: bool | None = None
    has_gym: bool | None = None
    has_party_room: bool | None = None
    has_24h_security: bool | None = None
    has_cctv: bool | None = None
    has_access_control: bool | None = None

    settings: dict | None = None
    tags: list[str] | None = None
    notes: str | None = None
    is_premium: bool | None = None


class CondominiumResponse(BaseModel):
    """Schema for condominium response."""

    id: UUID
    code: str | None = None
    client_id: UUID | None = None
    name: str | None = None
    condominium_type: CondominiumType | None = None
    status: CondominiumStatus | None = None
    administration_type: AdministrationType | None = None
    cnpj: str | None = None
    full_address: str | None = None
    address_city: str | None = None
    address_state: str | None = None

    syndic_name: str | None = None
    syndic_phone: str | None = None
    syndic_mandate_active: bool | None = None

    total_units: int | None = 0
    occupied_units: int | None = 0
    occupancy_rate: float | None = 0.0
    total_towers: int | None = None

    security_level: str | None = None
    amenities_count: int | None = 0

    plus_enabled: bool | None = False
    is_active: bool | None = True
    is_premium: bool | None = False

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CondominiumListResponse(BaseModel):
    """Schema for condominium list response."""

    id: UUID
    code: str | None = None
    client_id: UUID | None = None
    name: str | None = None
    condominium_type: CondominiumType | None = None
    status: CondominiumStatus | None = None
    address_city: str | None = None
    address_state: str | None = None
    total_units: int | None = 0
    occupancy_rate: float | None = 0.0
    security_level: str | None = None
    is_premium: bool | None = False
    created_at: datetime | None = None

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
    block: str | None = Field(None, max_length=20)
    tower: str | None = Field(None, max_length=50)
    floor: int | None = None
    type: UnitType = Field(default=UnitType.APARTAMENTO)

    area_m2: Decimal | None = Field(None, ge=0)
    bedrooms: int | None = Field(None, ge=0)
    bathrooms: int | None = Field(None, ge=0)
    parking_spots: int | None = Field(None, ge=0)

    owner_name: str | None = Field(None, max_length=200)
    owner_document: str | None = Field(None, max_length=20)
    owner_phone: str | None = Field(None, max_length=20)
    owner_email: str | None = Field(None, max_length=200)

    monthly_fee: Decimal | None = Field(None, ge=0)
    fraction: Decimal | None = Field(None, ge=0, le=1)

    notes: str | None = None
    tags: list[str] | None = None


class UnitCreate(UnitBase):
    """Schema for creating a unit."""

    condominium_id: UUID


class UnitUpdate(BaseModel):
    """Schema for updating a unit."""

    number: str | None = Field(None, max_length=20)
    block: str | None = Field(None, max_length=20)
    tower: str | None = Field(None, max_length=50)
    floor: int | None = None
    type: UnitType | None = None
    status: UnitStatus | None = None

    area_m2: Decimal | None = Field(None, ge=0)
    bedrooms: int | None = Field(None, ge=0)
    bathrooms: int | None = Field(None, ge=0)
    parking_spots: int | None = Field(None, ge=0)

    owner_name: str | None = Field(None, max_length=200)
    owner_document: str | None = Field(None, max_length=20)
    owner_phone: str | None = Field(None, max_length=20)
    owner_email: str | None = Field(None, max_length=200)

    resident_name: str | None = Field(None, max_length=200)
    resident_phone: str | None = Field(None, max_length=20)
    resident_email: str | None = Field(None, max_length=200)
    is_tenant: bool | None = None

    monthly_fee: Decimal | None = Field(None, ge=0)
    notes: str | None = None
    tags: list[str] | None = None


class UnitResponse(BaseModel):
    """Schema for unit response."""

    id: UUID
    code: str
    condominium_id: UUID
    number: str
    block: str | None
    tower: str | None
    floor: int | None
    type: UnitType
    status: UnitStatus
    display_name: str
    short_name: str

    area_m2: Decimal | None
    bedrooms: int | None
    parking_spots: int | None

    owner_name: str | None
    resident_name: str | None
    current_resident: str | None
    is_tenant: bool
    is_occupied: bool

    monthly_fee: Decimal | None
    total_fee: Decimal
    is_defaulter: bool
    debt_amount: Decimal | None

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
    block: str | None
    tower: str | None
    type: UnitType
    status: UnitStatus
    display_name: str
    current_resident: str | None
    is_occupied: bool
    is_defaulter: bool
    monthly_fee: Decimal | None

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
    description: str | None = Field(None, max_length=500)
    scope: str | None = None
    monthly_value: Decimal | None = Field(None, ge=0)
    setup_fee: Decimal | None = Field(None, ge=0)
    discount_percentage: Decimal | None = Field(None, ge=0, le=100)
    start_date: date | None = None
    end_date: date | None = None
    sla_response_time_minutes: int | None = Field(None, ge=0)
    sla_resolution_time_hours: int | None = Field(None, ge=0)
    is_24h: bool = False
    auto_renew: bool = True
    settings: dict | None = None
    features: list[str] | None = None
    notes: str | None = None


class ClientContractCreate(ClientContractBase):
    """Schema for creating a client contract."""

    client_id: UUID
    contract_id: UUID | None = None
    condominium_id: UUID | None = None


class ClientContractUpdate(BaseModel):
    """Schema for updating a client contract."""

    service_type: ContractServiceType | None = None
    status: ServiceStatus | None = None
    description: str | None = Field(None, max_length=500)
    scope: str | None = None
    monthly_value: Decimal | None = Field(None, ge=0)
    discount_percentage: Decimal | None = Field(None, ge=0, le=100)
    end_date: date | None = None
    sla_response_time_minutes: int | None = Field(None, ge=0)
    sla_resolution_time_hours: int | None = Field(None, ge=0)
    settings: dict | None = None
    features: list[str] | None = None
    notes: str | None = None
    auto_renew: bool | None = None


class ClientContractResponse(BaseModel):
    """Schema for client contract response."""

    id: UUID
    client_id: UUID
    contract_id: UUID | None
    condominium_id: UUID | None
    service_type: ContractServiceType
    status: ServiceStatus
    description: str | None
    monthly_value: Decimal | None
    final_value: Decimal | None
    start_date: date | None
    end_date: date | None
    days_until_end: int | None
    is_expiring_soon: bool
    is_electronic_security_service: bool
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
    description: str | None = Field(None, max_length=500)
    sync_direction: SyncDirection = Field(default=SyncDirection.BIDIRECTIONAL)
    api_url: str | None = Field(None, max_length=500)
    sync_interval_minutes: int | None = Field(None, ge=1)
    auto_sync: bool = True
    sync_on_change: bool = True
    settings: dict | None = None
    notes: str | None = None


class IntegrationSettingsCreate(IntegrationSettingsBase):
    """Schema for creating integration settings."""

    client_id: UUID
    api_key: str | None = Field(None, max_length=500)
    api_secret: str | None = Field(None, max_length=500)
    webhook_url: str | None = Field(None, max_length=500)
    webhook_secret: str | None = Field(None, max_length=200)


class IntegrationSettingsUpdate(BaseModel):
    """Schema for updating integration settings."""

    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    sync_direction: SyncDirection | None = None
    api_url: str | None = Field(None, max_length=500)
    api_key: str | None = Field(None, max_length=500)
    api_secret: str | None = Field(None, max_length=500)
    webhook_url: str | None = Field(None, max_length=500)
    sync_interval_minutes: int | None = Field(None, ge=1)
    auto_sync: bool | None = None
    sync_on_change: bool | None = None
    settings: dict | None = None
    notes: str | None = None
    is_enabled: bool | None = None


class IntegrationSettingsResponse(BaseModel):
    """Schema for integration settings response."""

    id: UUID
    client_id: UUID
    integration_type: IntegrationType
    name: str
    description: str | None
    sync_status: SyncStatus
    sync_direction: SyncDirection
    api_url: str | None
    external_client_id: str | None
    webhook_url: str | None
    sync_interval_minutes: int | None
    last_sync_at: datetime | None
    last_sync_success_at: datetime | None
    last_sync_error: str | None
    success_rate: float
    total_syncs: int
    records_synced: int
    is_configured: bool
    is_enabled: bool
    is_active: bool
    auto_sync: bool
    created_at: datetime

    model_config = {"from_attributes": True}
