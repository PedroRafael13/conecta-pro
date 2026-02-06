"""Schemas Pydantic para REPSync."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


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
    triggered_by: Optional[UUID] = None
    events_from_datetime: Optional[datetime] = None
    events_to_datetime: Optional[datetime] = None


class REPSyncUpdate(BaseModel):
    """Schema para atualizar REPSync."""

    status: Optional[str] = None
    total_items: Optional[int] = None
    processed_items: Optional[int] = None
    success_items: Optional[int] = None
    error_items: Optional[int] = None
    skipped_items: Optional[int] = None
    last_nsr_after: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    error_details: Optional[dict] = None


class REPSyncResponse(REPSyncBase):
    """Schema de resposta para REPSync."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    condominio_id: UUID
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_items: int
    processed_items: int
    success_items: int
    error_items: int
    skipped_items: int
    last_nsr_before: Optional[int] = None
    last_nsr_after: Optional[int] = None
    events_from_datetime: Optional[datetime] = None
    events_to_datetime: Optional[datetime] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
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

    items: List[REPSyncResponse]
    total: int
    page: int
    page_size: int
    pages: int


class REPSyncFilter(BaseModel):
    """Filtros para busca de sincronizações."""

    device_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    sync_type: Optional[str] = None
    status: Optional[str] = None
    trigger: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_errors: Optional[bool] = None


class REPSyncStart(BaseModel):
    """Schema para iniciar sincronização."""

    device_id: UUID
    sync_type: str = Field(
        default="events_pull",
        description="Tipo de sincronização",
    )
    from_datetime: Optional[datetime] = Field(
        default=None,
        description="Data/hora inicial para buscar eventos",
    )
    to_datetime: Optional[datetime] = Field(
        default=None,
        description="Data/hora final para buscar eventos",
    )
    from_nsr: Optional[int] = Field(
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
    elapsed_seconds: Optional[int] = None
    estimated_remaining_seconds: Optional[int] = None
    current_nsr: Optional[int] = None
    last_error: Optional[str] = None


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
    last_nsr: Optional[int] = None
    errors: Optional[List[dict]] = None


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
    start_time: Optional[str] = Field(
        default=None,
        description="Hora de início (HH:MM)",
        pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
    )
    end_time: Optional[str] = Field(
        default=None,
        description="Hora de fim (HH:MM)",
        pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
    )
    weekdays_only: bool = False
