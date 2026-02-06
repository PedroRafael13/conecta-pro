"""Schemas Pydantic para REPEvent."""

from datetime import datetime, date, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class REPEventBase(BaseModel):
    """Schema base para REPEvent."""

    nsr: int = Field(
        ...,
        ge=1,
        description="Número Sequencial de Registro",
    )
    event_datetime: datetime
    event_type: str = Field(
        default="entry",
        description="Tipo do evento",
    )
    pis_number: Optional[str] = Field(
        default=None,
        min_length=11,
        max_length=11,
        description="Número PIS/PASEP",
    )
    employee_code: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    employee_name: Optional[str] = Field(
        default=None,
        max_length=200,
    )
    identification_method: str = Field(
        default="biometric",
    )
    identification_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )


class REPEventCreate(REPEventBase):
    """Schema para criar REPEvent."""

    device_id: UUID
    condominio_id: UUID
    employee_id: Optional[UUID] = None
    biometric_hash: Optional[str] = None
    finger_index: Optional[int] = Field(default=None, ge=1, le=10)
    card_number: Optional[str] = None
    card_facility_code: Optional[str] = None
    photo_captured: bool = False
    photo_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_accuracy: Optional[float] = None
    raw_data: Optional[dict] = None
    sync_id: Optional[UUID] = None


class REPEventUpdate(BaseModel):
    """Schema para atualizar REPEvent."""

    employee_id: Optional[UUID] = None
    status: Optional[str] = None
    time_entry_id: Optional[UUID] = None
    error_message: Optional[str] = None
    is_valid: Optional[bool] = None
    validation_errors: Optional[list] = None


class REPEventResponse(REPEventBase):
    """Schema de resposta para REPEvent."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    condominio_id: UUID
    event_date: date
    event_time: time
    employee_id: Optional[UUID] = None
    card_number: Optional[str] = None
    photo_captured: bool
    status: str
    processed_at: Optional[datetime] = None
    time_entry_id: Optional[UUID] = None
    is_valid: bool
    afd_line: Optional[str] = None
    created_at: datetime


class REPEventList(BaseModel):
    """Schema para lista de eventos."""

    items: List[REPEventResponse]
    total: int
    page: int
    page_size: int
    pages: int


class REPEventFilter(BaseModel):
    """Filtros para busca de eventos."""

    device_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    pis_number: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    identification_method: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_valid: Optional[bool] = None
    has_employee: Optional[bool] = Field(
        default=None,
        description="Filtrar por eventos com/sem funcionário identificado",
    )
    nsr_from: Optional[int] = None
    nsr_to: Optional[int] = None


class REPEventBulkCreate(BaseModel):
    """Schema para criação em lote de eventos."""

    device_id: UUID
    events: List[REPEventCreate]


class REPEventProcess(BaseModel):
    """Schema para processamento de evento."""

    event_id: UUID
    employee_id: UUID
    create_time_entry: bool = True


class REPEventProcessResult(BaseModel):
    """Resultado do processamento de evento."""

    event_id: UUID
    success: bool
    time_entry_id: Optional[UUID] = None
    error_message: Optional[str] = None


class REPEventWebhook(BaseModel):
    """Schema para receber eventos via webhook."""

    device_serial: str
    events: List[dict]
    timestamp: datetime
    signature: Optional[str] = None


class REPEventStats(BaseModel):
    """Estatísticas de eventos."""

    total_events: int
    events_by_type: dict
    events_by_status: dict
    events_by_method: dict
    pending_processing: int
    errors_count: int
    duplicates_count: int
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
