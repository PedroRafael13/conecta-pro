"""Schemas Pydantic para REPSync."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class REPSyncBase(BaseModel):
    """Schema base para REPSync."""

    sync_type: str = Field(
        ...,
        description="Tipo de sincronização",
    )
    trigger: str = Field(
        default="manual",
        description="O que disparou a sync",
    )


class REPSyncCreate(REPSyncBase):
    """Schema para criar REPSync."""

    device_id: UUID
    condominio_id: UUID
    triggered_by: UUID | None = None
    events_from_datetime: datetime | None = None
    events_to_datetime: datetime | None = None


class REPSyncUpdate(BaseModel):
    """Schema para atualizar REPSync."""

    status: str | None = None
    total_items: int | None = None
    processed_items: int | None = None
    success_items: int | None = None
    error_items: int | None = None
    skipped_items: int | None = None
    last_nsr_after: int | None = None
    error_message: str | None = None
    error_code: str | None = None
    error_details: dict | None = None


class REPSyncResponse(REPSyncBase):
    """Schema de resposta para REPSync."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    condominio_id: UUID
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    total_items: int
    processed_items: int
    success_items: int
    error_items: int
    skipped_items: int
    last_nsr_before: int | None = None
    last_nsr_after: int | None = None
    events_from_datetime: datetime | None = None
    events_to_datetime: datetime | None = None
    error_message: str | None = None
    error_code: str | None = None
    retry_count: int
    bytes_transferred: int
    api_calls_made: int
    created_at: datetime

    @property
    def progress_percent(self) -> float:
        """Calcula percentual de progresso."""
        if self.total_items == 0:
            return 0.0
        return round((self.processed_items / self.total_items) * 100, 2)

    @property
    def success_rate(self) -> float:
        """Calcula taxa de sucesso."""
        if self.processed_items == 0:
            return 0.0
        return round((self.success_items / self.processed_items) * 100, 2)


class REPSyncList(BaseModel):
    """Schema para lista de sincronizações."""

    items: list[REPSyncResponse]
    total: int
    page: int
    page_size: int
    pages: int


class REPSyncFilter(BaseModel):
    """Filtros para busca de sincronizações."""

    device_id: UUID | None = None
    condominio_id: UUID | None = None
    sync_type: str | None = None
    status: str | None = None
    trigger: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    has_errors: bool | None = None


class REPSyncStart(BaseModel):
    """Schema para iniciar sincronização."""

    device_id: UUID
    sync_type: str = Field(
        default="events_pull",
        description="Tipo de sincronização",
    )
    from_datetime: datetime | None = Field(
        default=None,
        description="Data/hora inicial para buscar eventos",
    )
    to_datetime: datetime | None = Field(
        default=None,
        description="Data/hora final para buscar eventos",
    )
    from_nsr: int | None = Field(
        default=None,
        description="NSR inicial para buscar eventos",
    )
    force: bool = Field(
        default=False,
        description="Forçar sync mesmo se houver uma em andamento",
    )


class REPSyncProgress(BaseModel):
    """Progresso da sincronização."""

    sync_id: UUID
    status: str
    progress_percent: float
    processed_items: int
    total_items: int
    success_items: int
    error_items: int
    elapsed_seconds: int | None = None
    estimated_remaining_seconds: int | None = None
    current_nsr: int | None = None
    last_error: str | None = None


class REPSyncResult(BaseModel):
    """Resultado final da sincronização."""

    sync_id: UUID
    status: str
    duration_seconds: int
    total_items: int
    success_items: int
    error_items: int
    skipped_items: int
    success_rate: float
    new_events_count: int
    last_nsr: int | None = None
    errors: list[dict] | None = None


class REPSyncSchedule(BaseModel):
    """Configuração de agendamento de sync."""

    device_id: UUID
    enabled: bool = True
    interval_seconds: int = Field(
        default=300,
        ge=60,
        le=86400,
    )
    sync_type: str = "events_pull"
    start_time: str | None = Field(
        default=None,
        description="Hora de início (HH:MM)",
        pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
    )
    end_time: str | None = Field(
        default=None,
        description="Hora de fim (HH:MM)",
        pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
    )
    weekdays_only: bool = False
