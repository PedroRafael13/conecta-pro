"""Schemas de Log de Visitante."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.visitors.models.log import (
    AccessMethod,
    AccessPoint,
    AccessType,
    DenialReason,
)


class LogBase(BaseModel):
    """Schema base de log."""

    visitor_id: UUID
    condominium_id: str = Field(..., max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)
    unit_id: Optional[str] = Field(None, max_length=50)
    unit_number: Optional[str] = Field(None, max_length=20)
    block: Optional[str] = Field(None, max_length=20)
    resident_id: Optional[str] = Field(None, max_length=50)
    resident_name: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class LogEntry(LogBase):
    """Schema para registro de entrada."""

    authorization_id: Optional[UUID] = None
    access_method: AccessMethod = Field(default=AccessMethod.PORTARIA)
    access_point: AccessPoint = Field(default=AccessPoint.PORTARIA_PRINCIPAL)
    operator_id: Optional[str] = Field(None, max_length=50)
    operator_name: Optional[str] = Field(None, max_length=200)
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    vehicle_model: Optional[str] = Field(None, max_length=100)
    vehicle_color: Optional[str] = Field(None, max_length=50)
    parking_spot: Optional[str] = Field(None, max_length=20)
    document_type: Optional[str] = Field(None, max_length=20)
    document_number: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    companions_count: int = Field(default=0, ge=0)
    companions_names: Optional[list[str]] = Field(default_factory=list)
    items_description: Optional[str] = None
    items_count: int = Field(default=0, ge=0)
    device_id: Optional[str] = Field(None, max_length=50)
    device_name: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = Field(None, ge=30, le=45)
    health_check_passed: Optional[bool] = None


class LogExit(BaseModel):
    """Schema para registro de saída."""

    visitor_id: UUID
    condominium_id: str = Field(..., max_length=50)
    access_method: AccessMethod = Field(default=AccessMethod.PORTARIA)
    access_point: AccessPoint = Field(default=AccessPoint.PORTARIA_PRINCIPAL)
    operator_id: Optional[str] = Field(None, max_length=50)
    operator_name: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class LogDeny(LogBase):
    """Schema para registro de negativa."""

    denial_reason: DenialReason
    denial_notes: Optional[str] = None
    access_method: AccessMethod = Field(default=AccessMethod.PORTARIA)
    access_point: AccessPoint = Field(default=AccessPoint.PORTARIA_PRINCIPAL)
    operator_id: Optional[str] = Field(None, max_length=50)
    operator_name: Optional[str] = Field(None, max_length=200)
    document_type: Optional[str] = Field(None, max_length=20)
    document_number: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)


class LogResponse(BaseModel):
    """Schema de resposta de log."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    visitor_id: UUID
    authorization_id: Optional[UUID] = None
    access_type: AccessType
    access_method: AccessMethod
    access_point: AccessPoint
    condominium_id: str
    condominium_name: Optional[str] = None
    unit_id: Optional[str] = None
    unit_number: Optional[str] = None
    block: Optional[str] = None
    timestamp: datetime
    entry_at: Optional[datetime] = None
    exit_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    resident_id: Optional[str] = None
    resident_name: Optional[str] = None
    resident_notified: bool
    resident_notified_at: Optional[datetime] = None
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    vehicle_plate: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    parking_spot: Optional[str] = None
    document_verified: bool
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    denied: bool
    denial_reason: Optional[DenialReason] = None
    denial_notes: Optional[str] = None
    photo_url: Optional[str] = None
    photo_vehicle_url: Optional[str] = None
    photo_document_url: Optional[str] = None
    companions_count: int
    companions_names: Optional[list[str]] = None
    items_description: Optional[str] = None
    items_count: int
    purpose: Optional[str] = None
    notes: Optional[str] = None
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    temperature: Optional[float] = None
    health_check_passed: Optional[bool] = None
    is_entry: bool
    is_exit: bool
    is_denied: bool
    is_still_inside: bool
    has_companions: bool
    has_items: bool
    has_vehicle: bool
    formatted_duration: str
    access_type_display: str
    created_at: datetime


class LogListResponse(BaseModel):
    """Schema de listagem de logs."""

    items: list[LogResponse]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


class LogFilter(BaseModel):
    """Schema de filtros de log."""

    visitor_id: Optional[UUID] = None
    condominium_id: Optional[str] = None
    unit_id: Optional[str] = None
    resident_id: Optional[str] = None
    access_type: Optional[AccessType] = None
    access_method: Optional[AccessMethod] = None
    access_point: Optional[AccessPoint] = None
    denied: Optional[bool] = None
    denial_reason: Optional[DenialReason] = None
    has_vehicle: Optional[bool] = None
    has_companions: Optional[bool] = None
    operator_id: Optional[str] = None
    device_id: Optional[str] = None
    timestamp_from: Optional[datetime] = None
    timestamp_until: Optional[datetime] = None
    is_still_inside: Optional[bool] = None


class LogStats(BaseModel):
    """Schema de estatísticas de logs."""

    total: int = 0
    entries: int = 0
    exits: int = 0
    denied: int = 0
    still_inside: int = 0
    by_access_type: dict = Field(default_factory=dict)
    by_access_method: dict = Field(default_factory=dict)
    by_access_point: dict = Field(default_factory=dict)
    by_hour: dict = Field(default_factory=dict)
    by_day_of_week: dict = Field(default_factory=dict)
    avg_duration_minutes: float = 0
    with_vehicle: int = 0
    with_companions: int = 0
    total_companions: int = 0
    denial_reasons: dict = Field(default_factory=dict)


class LogTimeline(BaseModel):
    """Timeline de logs de um visitante."""

    visitor_id: UUID
    visitor_name: str
    logs: list[LogResponse]
    total_visits: int
    total_duration_minutes: int
    avg_duration_minutes: float
    first_visit_at: Optional[datetime] = None
    last_visit_at: Optional[datetime] = None
    denied_count: int = 0


class VisitorInside(BaseModel):
    """Visitante atualmente dentro."""

    visitor_id: UUID
    visitor_name: str
    visitor_photo: Optional[str] = None
    visitor_type: str
    entry_at: datetime
    duration_minutes: int
    unit_number: Optional[str] = None
    resident_name: Optional[str] = None
    purpose: Optional[str] = None
    has_vehicle: bool
    vehicle_plate: Optional[str] = None
    companions_count: int
