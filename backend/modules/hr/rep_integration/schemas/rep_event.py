"""Schemas Pydantic para REPEvent."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    pis_number: str | None = Field(
        default=None,
        min_length=11,
        max_length=11,
        description="Número PIS/PASEP",
    )
    employee_code: str | None = Field(
        default=None,
        max_length=50,
    )
    employee_name: str | None = Field(
        default=None,
        max_length=200,
    )
    identification_method: str = Field(
        default="biometric",
    )
    identification_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class REPEventCreate(REPEventBase):
    """Schema para criar REPEvent."""

    device_id: UUID
    condominio_id: UUID
    employee_id: UUID | None = None
    biometric_hash: str | None = None
    finger_index: int | None = Field(default=None, ge=1, le=10)
    card_number: str | None = None
    card_facility_code: str | None = None
    photo_captured: bool = False
    photo_path: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_accuracy: float | None = None
    raw_data: dict | None = None
    sync_id: UUID | None = None


class REPEventUpdate(BaseModel):
    """Schema para atualizar REPEvent."""

    employee_id: UUID | None = None
    status: str | None = None
    time_entry_id: UUID | None = None
    error_message: str | None = None
    is_valid: bool | None = None
    validation_errors: list | None = None


class REPEventResponse(REPEventBase):
    """Schema de resposta para REPEvent."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    condominio_id: UUID
    event_date: date
    event_time: time
    employee_id: UUID | None = None
    card_number: str | None = None
    photo_captured: bool
    status: str
    processed_at: datetime | None = None
    time_entry_id: UUID | None = None
    is_valid: bool
    afd_line: str | None = None
    created_at: datetime


class REPEventList(BaseModel):
    """Schema para lista de eventos."""

    items: list[REPEventResponse]
    total: int
    page: int
    page_size: int
    pages: int


class REPEventFilter(BaseModel):
    """Filtros para busca de eventos."""

    device_id: UUID | None = None
    condominio_id: UUID | None = None
    employee_id: UUID | None = None
    pis_number: str | None = None
    event_type: str | None = None
    status: str | None = None
    identification_method: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    is_valid: bool | None = None
    has_employee: bool | None = Field(
        default=None,
        description="Filtrar por eventos com/sem funcionário identificado",
    )
    nsr_from: int | None = None
    nsr_to: int | None = None


class REPEventBulkCreate(BaseModel):
    """Schema para criação em lote de eventos."""

    device_id: UUID
    events: list[REPEventCreate]


class REPEventProcess(BaseModel):
    """Schema para processamento de evento."""

    event_id: UUID
    employee_id: UUID
    create_time_entry: bool = True


class REPEventProcessResult(BaseModel):
    """Resultado do processamento de evento."""

    event_id: UUID
    success: bool
    time_entry_id: UUID | None = None
    error_message: str | None = None


class REPEventWebhook(BaseModel):
    """Schema para receber eventos via webhook."""

    device_serial: str
    events: list[dict]
    timestamp: datetime
    signature: str | None = None


class REPEventStats(BaseModel):
    """Estatísticas de eventos."""

    total_events: int
    events_by_type: dict
    events_by_status: dict
    events_by_method: dict
    pending_processing: int
    errors_count: int
    duplicates_count: int
    date_range_start: date | None = None
    date_range_end: date | None = None
