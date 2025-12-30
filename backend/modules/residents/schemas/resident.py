"""Schemas para Resident."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from modules.residents.models.resident import (
    ResidentType,
    ResidentStatus,
    DocumentType,
    Gender,
    MaritalStatus,
    AccessMethod,
)


# ========== Base Schemas ==========


class ResidentBase(BaseModel):
    """Schema base para Resident."""

    name: str = Field(..., min_length=2, max_length=200)
    social_name: Optional[str] = Field(None, max_length=200)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: Optional[str] = Field(None, max_length=100)
    profession: Optional[str] = Field(None, max_length=100)

    document_type: DocumentType
    document_number: str = Field(..., min_length=5, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    rg_issuer: Optional[str] = Field(None, max_length=20)

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)

    resident_type: ResidentType = ResidentType.PROPRIETARIO

    condominium_id: str = Field(..., max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)
    unit_id: str = Field(..., max_length=50)
    unit_number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    floor: Optional[str] = Field(None, max_length=10)

    is_unit_owner: bool = False
    is_main_resident: bool = False
    is_representative: bool = False


class ResidentCreate(ResidentBase):
    """Schema para criação de Resident."""

    photo_url: Optional[str] = Field(None, max_length=500)
    move_in_date: Optional[date] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None

    can_authorize_visitors: bool = True
    can_book_common_areas: bool = True
    can_vote_assembly: bool = True
    can_receive_deliveries: bool = True

    receive_email_notifications: bool = True
    receive_sms_notifications: bool = False
    receive_push_notifications: bool = True
    receive_whatsapp_notifications: bool = True

    notes: Optional[str] = None
    special_needs: Optional[str] = None
    tags: Optional[list[str]] = None


class ResidentUpdate(BaseModel):
    """Schema para atualização de Resident."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    social_name: Optional[str] = Field(None, max_length=200)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: Optional[str] = Field(None, max_length=100)
    profession: Optional[str] = Field(None, max_length=100)

    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    rg_issuer: Optional[str] = Field(None, max_length=20)

    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)

    resident_type: Optional[ResidentType] = None
    status: Optional[ResidentStatus] = None

    unit_id: Optional[str] = Field(None, max_length=50)
    unit_number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    floor: Optional[str] = Field(None, max_length=10)

    is_unit_owner: Optional[bool] = None
    is_main_resident: Optional[bool] = None
    is_representative: Optional[bool] = None

    photo_url: Optional[str] = Field(None, max_length=500)

    can_authorize_visitors: Optional[bool] = None
    can_book_common_areas: Optional[bool] = None
    can_vote_assembly: Optional[bool] = None
    can_receive_deliveries: Optional[bool] = None

    receive_email_notifications: Optional[bool] = None
    receive_sms_notifications: Optional[bool] = None
    receive_push_notifications: Optional[bool] = None
    receive_whatsapp_notifications: Optional[bool] = None

    notes: Optional[str] = None
    special_needs: Optional[str] = None
    tags: Optional[list[str]] = None


class ResidentResponse(BaseModel):
    """Schema de resposta para Resident."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    social_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: Optional[str] = None
    profession: Optional[str] = None

    document_type: DocumentType
    document_number: str
    cpf: Optional[str] = None
    rg: Optional[str] = None
    rg_issuer: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None
    phone_secondary: Optional[str] = None
    whatsapp: Optional[str] = None

    resident_type: ResidentType
    status: ResidentStatus

    condominium_id: str
    condominium_name: Optional[str] = None
    unit_id: str
    unit_number: Optional[str] = None
    block: Optional[str] = None
    floor: Optional[str] = None

    is_unit_owner: bool
    is_main_resident: bool
    is_representative: bool

    photo_url: Optional[str] = None
    qr_code: Optional[str] = None

    move_in_date: Optional[date] = None
    move_out_date: Optional[date] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None

    is_blocked: bool
    block_reason: Optional[str] = None
    is_defaulter: bool
    debt_amount: Optional[float] = None

    can_authorize_visitors: bool
    can_book_common_areas: bool
    can_vote_assembly: bool
    can_receive_deliveries: bool

    has_biometric: bool
    has_access_card: bool
    full_address: str
    display_name: str
    age: Optional[int] = None
    contract_status: str

    notes: Optional[str] = None
    special_needs: Optional[str] = None
    tags: Optional[list[str]] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Action Schemas ==========


class ResidentBlock(BaseModel):
    """Schema para bloqueio de morador."""

    reason: str = Field(..., min_length=5, max_length=500)
    blocked_by: str = Field(..., max_length=100)


class ResidentSetDefaulter(BaseModel):
    """Schema para marcar como inadimplente."""

    debt_amount: float = Field(0.0, ge=0)


class ResidentMoveOut(BaseModel):
    """Schema para mudança."""

    move_out_date: Optional[date] = None


class ResidentTransferUnit(BaseModel):
    """Schema para transferência de unidade."""

    new_unit_id: str = Field(..., max_length=50)
    new_unit_number: Optional[str] = Field(None, max_length=20)
    new_block: Optional[str] = Field(None, max_length=20)
    new_floor: Optional[str] = Field(None, max_length=10)
    transfer_date: Optional[date] = None


class ResidentEnableAccess(BaseModel):
    """Schema para habilitar método de acesso."""

    access_method: AccessMethod
    credential: Optional[str] = Field(None, max_length=100)


# ========== Filter Schemas ==========


class ResidentFilter(BaseModel):
    """Schema para filtros de busca."""

    name: Optional[str] = None
    resident_type: Optional[ResidentType] = None
    status: Optional[ResidentStatus] = None
    document_number: Optional[str] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    condominium_id: Optional[str] = None
    unit_id: Optional[str] = None
    block: Optional[str] = None
    is_blocked: Optional[bool] = None
    is_defaulter: Optional[bool] = None
    is_unit_owner: Optional[bool] = None
    is_main_resident: Optional[bool] = None
    has_biometric: Optional[bool] = None


# ========== List Response ==========


class ResidentListResponse(BaseModel):
    """Schema de resposta para lista de Residents."""

    items: list[ResidentResponse]
    total: int
    page: int
    page_size: int
    pages: int = 0


# ========== Stats ==========


class ResidentStats(BaseModel):
    """Estatísticas de moradores."""

    total: int = 0
    active: int = 0
    inactive: int = 0
    blocked: int = 0
    defaulters: int = 0
    pending: int = 0

    by_type: dict = {}
    by_status: dict = {}
    by_block: dict = {}

    with_biometric: int = 0
    with_access_card: int = 0
    with_vehicle: int = 0
    with_pet: int = 0

    owners: int = 0
    tenants: int = 0

    total_debt: float = 0.0
    avg_debt: float = 0.0


class ResidentSearch(BaseModel):
    """Resultado de busca de morador."""

    id: UUID
    code: str
    name: str
    document_number: str
    unit_number: Optional[str] = None
    block: Optional[str] = None
    photo_url: Optional[str] = None
    status: ResidentStatus
