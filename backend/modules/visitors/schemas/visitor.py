"""Schemas de Visitante."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from modules.visitors.models.visitor import (
    DocumentType,
    VisitorStatus,
    VisitorType,
)


class VisitorBase(BaseModel):
    """Schema base de visitante."""

    name: str = Field(..., min_length=2, max_length=200)
    visitor_type: VisitorType = Field(default=VisitorType.OUTRO)
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=200)
    company_cnpj: Optional[str] = Field(None, max_length=18)
    company_role: Optional[str] = Field(None, max_length=100)
    badge_number: Optional[str] = Field(None, max_length=50)
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    vehicle_model: Optional[str] = Field(None, max_length=100)
    vehicle_color: Optional[str] = Field(None, max_length=50)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    default_condominium_id: Optional[str] = Field(None, max_length=50)
    default_condominium_name: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None
    tags: Optional[list] = Field(default_factory=list)


class VisitorCreate(VisitorBase):
    """Schema para criação de visitante."""

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_by_id: Optional[str] = Field(None, max_length=50)
    created_by_name: Optional[str] = Field(None, max_length=200)

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, v: Optional[str]) -> Optional[str]:
        """Valida CPF."""
        if v:
            v = v.replace(".", "").replace("-", "").replace(" ", "")
            if len(v) != 11 or not v.isdigit():
                raise ValueError("CPF inválido")
        return v

    @field_validator("phone", "phone_secondary")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Valida telefone."""
        if v:
            v = v.replace("(", "").replace(")", "").replace("-", "")
            v = v.replace(" ", "").replace("+", "")
            if len(v) < 10 or len(v) > 13:
                raise ValueError("Telefone inválido")
        return v


class VisitorUpdate(BaseModel):
    """Schema para atualização de visitante."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    visitor_type: Optional[VisitorType] = None
    status: Optional[VisitorStatus] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = Field(None, max_length=50)
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_secondary: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=200)
    company_cnpj: Optional[str] = Field(None, max_length=18)
    company_role: Optional[str] = Field(None, max_length=100)
    badge_number: Optional[str] = Field(None, max_length=50)
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    vehicle_model: Optional[str] = Field(None, max_length=100)
    vehicle_color: Optional[str] = Field(None, max_length=50)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    card_number: Optional[str] = Field(None, max_length=50)
    default_condominium_id: Optional[str] = Field(None, max_length=50)
    default_condominium_name: Optional[str] = Field(None, max_length=200)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    tags: Optional[list] = None


class VisitorResponse(VisitorBase):
    """Schema de resposta de visitante."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    status: VisitorStatus
    card_number: Optional[str] = None
    qr_code: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    blocked_reason: Optional[str] = None
    blocked_at: Optional[datetime] = None
    blocked_until: Optional[datetime] = None
    visit_count: int = 0
    last_visit_at: Optional[datetime] = None
    first_visit_at: Optional[datetime] = None
    avg_visit_duration_minutes: Optional[int] = None
    is_blocked: bool
    is_valid: bool
    is_active: bool
    has_vehicle: bool
    has_biometric: bool
    display_name: str
    frequency_category: str
    created_at: datetime
    updated_at: datetime


class VisitorListResponse(BaseModel):
    """Schema de listagem de visitantes."""

    items: list[VisitorResponse]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


class VisitorBlock(BaseModel):
    """Schema para bloqueio de visitante."""

    reason: str = Field(..., min_length=5, max_length=500)
    blocked_by_id: Optional[str] = Field(None, max_length=50)
    blocked_by_name: Optional[str] = Field(None, max_length=200)
    until: Optional[datetime] = None


class VisitorFilter(BaseModel):
    """Schema de filtros de visitante."""

    name: Optional[str] = None
    visitor_type: Optional[VisitorType] = None
    status: Optional[VisitorStatus] = None
    document_number: Optional[str] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    vehicle_plate: Optional[str] = None
    condominium_id: Optional[str] = None
    is_blocked: Optional[bool] = None
    has_vehicle: Optional[bool] = None
    has_biometric: Optional[bool] = None
    frequency_category: Optional[str] = None
    tags: Optional[list] = None
    created_from: Optional[datetime] = None
    created_until: Optional[datetime] = None


class VisitorStats(BaseModel):
    """Schema de estatísticas de visitantes."""

    total: int = 0
    active: int = 0
    blocked: int = 0
    vip: int = 0
    temporary: int = 0
    inactive: int = 0
    by_type: dict = Field(default_factory=dict)
    by_frequency: dict = Field(default_factory=dict)
    with_vehicle: int = 0
    with_biometric: int = 0
    avg_visits: float = 0
    total_visits: int = 0


class VisitorBulkCreate(BaseModel):
    """Schema para criação em lote."""

    visitors: list[VisitorCreate] = Field(..., min_length=1, max_length=100)
    condominium_id: str = Field(..., max_length=50)
    created_by_id: Optional[str] = Field(None, max_length=50)
    created_by_name: Optional[str] = Field(None, max_length=200)


class VisitorSearch(BaseModel):
    """Schema de busca de visitante."""

    query: str = Field(..., min_length=2)
    condominium_id: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
