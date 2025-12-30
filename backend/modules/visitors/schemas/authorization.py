"""Schemas de Autorização de Visitante."""

from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.visitors.models.authorization import (
    AuthorizationStatus,
    AuthorizationType,
    RecurrenceType,
)


class AuthorizationBase(BaseModel):
    """Schema base de autorização."""

    visitor_id: UUID
    authorization_type: AuthorizationType = Field(default=AuthorizationType.UNICA)
    condominium_id: str = Field(..., max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)
    unit_id: Optional[str] = Field(None, max_length=50)
    unit_number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    resident_id: Optional[str] = Field(None, max_length=50)
    resident_name: Optional[str] = Field(None, max_length=200)
    resident_phone: Optional[str] = Field(None, max_length=20)
    resident_email: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class AuthorizationCreate(AuthorizationBase):
    """Schema para criação de autorização."""

    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    valid_date: Optional[datetime] = None
    time_from: Optional[time] = None
    time_until: Optional[time] = None
    allow_all_hours: bool = False
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_days: Optional[list[int]] = Field(default_factory=list)
    max_uses: Optional[int] = Field(None, ge=1)
    allowed_areas: Optional[list[str]] = Field(default_factory=list)
    allowed_parking: bool = False
    parking_spot: Optional[str] = Field(None, max_length=20)
    notify_on_entry: bool = True
    notify_on_exit: bool = False
    notify_resident: bool = True
    notify_admin: bool = False
    event_name: Optional[str] = Field(None, max_length=200)
    event_description: Optional[str] = None
    expected_guests: Optional[int] = Field(None, ge=1)
    requires_approval: bool = True
    created_by_id: Optional[str] = Field(None, max_length=50)
    created_by_name: Optional[str] = Field(None, max_length=200)

    @field_validator("recurrence_days")
    @classmethod
    def validate_recurrence_days(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        """Valida dias de recorrência (0-6, seg-dom)."""
        if v:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError("Dia da semana deve ser entre 0 (seg) e 6 (dom)")
        return v


class AuthorizationUpdate(BaseModel):
    """Schema para atualização de autorização."""

    authorization_type: Optional[AuthorizationType] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    valid_date: Optional[datetime] = None
    time_from: Optional[time] = None
    time_until: Optional[time] = None
    allow_all_hours: Optional[bool] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_days: Optional[list[int]] = None
    max_uses: Optional[int] = Field(None, ge=1)
    allowed_areas: Optional[list[str]] = None
    allowed_parking: Optional[bool] = None
    parking_spot: Optional[str] = Field(None, max_length=20)
    purpose: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    notify_on_entry: Optional[bool] = None
    notify_on_exit: Optional[bool] = None
    notify_resident: Optional[bool] = None
    notify_admin: Optional[bool] = None
    event_name: Optional[str] = Field(None, max_length=200)
    event_description: Optional[str] = None
    expected_guests: Optional[int] = Field(None, ge=1)
    requires_approval: Optional[bool] = None


class AuthorizationResponse(BaseModel):
    """Schema de resposta de autorização."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    visitor_id: UUID
    authorization_type: AuthorizationType
    status: AuthorizationStatus
    condominium_id: str
    condominium_name: Optional[str] = None
    unit_id: Optional[str] = None
    unit_number: Optional[str] = None
    block: Optional[str] = None
    resident_id: Optional[str] = None
    resident_name: Optional[str] = None
    resident_phone: Optional[str] = None
    valid_from: datetime
    valid_until: Optional[datetime] = None
    valid_date: Optional[datetime] = None
    time_from: Optional[time] = None
    time_until: Optional[time] = None
    allow_all_hours: bool
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_days: Optional[list[int]] = None
    max_uses: Optional[int] = None
    uses_count: int
    allowed_areas: Optional[list[str]] = None
    allowed_parking: bool
    parking_spot: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    notify_on_entry: bool
    notify_on_exit: bool
    event_name: Optional[str] = None
    expected_guests: Optional[int] = None
    qr_code: Optional[str] = None
    access_code: Optional[str] = None
    is_valid: bool
    can_use: bool
    remaining_uses: Optional[int] = None
    days_until_expiry: Optional[int] = None
    is_expired: bool
    status_display: str
    created_at: datetime
    updated_at: datetime


class AuthorizationListResponse(BaseModel):
    """Schema de listagem de autorizações."""

    items: list[AuthorizationResponse]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


class AuthorizationApprove(BaseModel):
    """Schema para aprovação de autorização."""

    approved_by_id: Optional[str] = Field(None, max_length=50)
    approved_by_name: Optional[str] = Field(None, max_length=200)


class AuthorizationReject(BaseModel):
    """Schema para rejeição de autorização."""

    reason: str = Field(..., min_length=5, max_length=500)


class AuthorizationFilter(BaseModel):
    """Schema de filtros de autorização."""

    visitor_id: Optional[UUID] = None
    authorization_type: Optional[AuthorizationType] = None
    status: Optional[AuthorizationStatus] = None
    condominium_id: Optional[str] = None
    unit_id: Optional[str] = None
    resident_id: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_valid: Optional[bool] = None
    is_expired: Optional[bool] = None
    can_use: Optional[bool] = None


class AuthorizationStats(BaseModel):
    """Schema de estatísticas de autorizações."""

    total: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    expired: int = 0
    used: int = 0
    by_type: dict = Field(default_factory=dict)
    by_condominium: dict = Field(default_factory=dict)
    total_uses: int = 0


class AuthorizationValidate(BaseModel):
    """Schema para validação de autorização."""

    code: Optional[str] = None
    qr_code: Optional[str] = None
    access_code: Optional[str] = None
    condominium_id: str = Field(..., max_length=50)


class AuthorizationValidateResponse(BaseModel):
    """Resposta de validação de autorização."""

    valid: bool
    authorization: Optional[AuthorizationResponse] = None
    reason: Optional[str] = None
    visitor_name: Optional[str] = None
    visitor_photo: Optional[str] = None
    unit_number: Optional[str] = None
    resident_name: Optional[str] = None
