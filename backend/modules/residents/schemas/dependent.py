"""Schemas para ResidentDependent."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from modules.residents.models.dependent import (
    RelationshipType,
    DependentStatus,
    DependentDocumentType,
)


# ========== Base Schemas ==========


class DependentBase(BaseModel):
    """Schema base para Dependent."""

    name: str = Field(..., min_length=2, max_length=200)
    social_name: Optional[str] = Field(None, max_length=200)
    relationship_type: RelationshipType
    relationship_description: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=30)


class DependentCreate(DependentBase):
    """Schema para criação de Dependent."""

    resident_id: UUID
    document_type: Optional[DependentDocumentType] = None
    document_number: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)

    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

    photo_url: Optional[str] = Field(None, max_length=500)

    has_access: bool = True
    access_card_number: Optional[str] = Field(None, max_length=50)
    access_tag_rfid: Optional[str] = Field(None, max_length=50)

    can_authorize_visitors: bool = False
    can_receive_deliveries: bool = True
    can_use_common_areas: bool = True

    # Para menores
    school_name: Optional[str] = Field(None, max_length=200)
    school_phone: Optional[str] = Field(None, max_length=20)
    authorized_pickup_persons: Optional[list[dict]] = None

    # Para funcionários
    work_schedule: Optional[dict] = None
    employment_start_date: Optional[date] = None
    employment_end_date: Optional[date] = None

    # Validade
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    has_special_needs: bool = False
    special_needs_description: Optional[str] = None

    notes: Optional[str] = None


class DependentUpdate(BaseModel):
    """Schema para atualização de Dependent."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    social_name: Optional[str] = Field(None, max_length=200)
    relationship_type: Optional[RelationshipType] = None
    relationship_description: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=30)

    document_type: Optional[DependentDocumentType] = None
    document_number: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)

    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

    status: Optional[DependentStatus] = None
    photo_url: Optional[str] = Field(None, max_length=500)

    has_access: Optional[bool] = None
    access_card_number: Optional[str] = Field(None, max_length=50)
    access_tag_rfid: Optional[str] = Field(None, max_length=50)

    can_authorize_visitors: Optional[bool] = None
    can_receive_deliveries: Optional[bool] = None
    can_use_common_areas: Optional[bool] = None

    school_name: Optional[str] = Field(None, max_length=200)
    school_phone: Optional[str] = Field(None, max_length=20)
    authorized_pickup_persons: Optional[list[dict]] = None

    work_schedule: Optional[dict] = None
    employment_start_date: Optional[date] = None
    employment_end_date: Optional[date] = None

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    has_special_needs: Optional[bool] = None
    special_needs_description: Optional[str] = None

    notes: Optional[str] = None


class DependentResponse(BaseModel):
    """Schema de resposta para Dependent."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resident_id: UUID
    relationship_type: RelationshipType
    relationship_description: Optional[str] = None

    name: str
    social_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None

    document_type: Optional[DependentDocumentType] = None
    document_number: Optional[str] = None
    cpf: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

    status: DependentStatus
    photo_url: Optional[str] = None
    facial_id: Optional[str] = None
    fingerprint_id: Optional[str] = None

    has_access: bool
    access_card_number: Optional[str] = None
    access_tag_rfid: Optional[str] = None

    can_authorize_visitors: bool
    can_receive_deliveries: bool
    can_use_common_areas: bool

    is_minor: bool
    school_name: Optional[str] = None
    school_phone: Optional[str] = None
    authorized_pickup_persons: Optional[list[dict]] = None

    is_employee: bool
    work_schedule: Optional[dict] = None
    employment_start_date: Optional[date] = None
    employment_end_date: Optional[date] = None

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    is_blocked: bool
    block_reason: Optional[str] = None

    has_special_needs: bool
    special_needs_description: Optional[str] = None

    is_active: bool
    is_valid: bool
    age: Optional[int] = None
    has_biometric: bool
    display_name: str
    relationship_display: str

    notes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Action Schemas ==========


class DependentBlock(BaseModel):
    """Schema para bloqueio."""

    reason: str = Field(..., min_length=5, max_length=500)


class DependentSetTemporary(BaseModel):
    """Schema para definir como temporário."""

    valid_from: date
    valid_until: date


class DependentAddPickupPerson(BaseModel):
    """Schema para adicionar pessoa autorizada a buscar."""

    name: str = Field(..., min_length=2, max_length=200)
    phone: str = Field(..., max_length=20)
    document: Optional[str] = Field(None, max_length=50)


# ========== Filter Schemas ==========


class DependentFilter(BaseModel):
    """Schema para filtros de busca."""

    resident_id: Optional[UUID] = None
    relationship_type: Optional[RelationshipType] = None
    status: Optional[DependentStatus] = None
    is_minor: Optional[bool] = None
    is_employee: Optional[bool] = None
    has_access: Optional[bool] = None
    is_blocked: Optional[bool] = None
    condominium_id: Optional[str] = None


# ========== List Response ==========


class DependentListResponse(BaseModel):
    """Schema de resposta para lista de Dependents."""

    items: list[DependentResponse]
    total: int
    page: int
    page_size: int
    pages: int = 0


# ========== Stats ==========


class DependentStats(BaseModel):
    """Estatísticas de dependentes."""

    total: int = 0
    active: int = 0
    blocked: int = 0
    minors: int = 0
    employees: int = 0
    temporary: int = 0
    by_relationship: dict = {}
    with_access: int = 0
    with_biometric: int = 0
