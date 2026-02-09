"""
Schemas Pydantic para GuardianOccurrence.
"""

from datetime import datetime

from modules.remote_gatehouse.models.guardian_occurrence import (
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GuardianOccurrenceCreate(BaseModel):
    """Schema para criar ocorrência."""

    guardian_id: str = Field(..., min_length=1, max_length=100)
    occurrence_type: OccurrenceType = Field(default=OccurrenceType.OTHER)
    severity: OccurrenceSeverity = Field(default=OccurrenceSeverity.MEDIUM)
    client_id: str = Field(..., description="ID do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    post_id: str | None = Field(None, description="ID do posto")

    # Descrição
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: str | None = Field(None, max_length=255)
    location_details: str | None = Field(None)

    # Ações
    action_taken: str | None = Field(None)
    action_required: str | None = Field(None)

    # Pessoas
    involved_persons: list[dict] | None = Field(None)
    witnesses: list[dict] | None = Field(None)
    reported_by: str | None = Field(None, max_length=100)
    reported_by_id: str | None = Field(None)

    # Serviços externos
    police_notified: bool = Field(default=False)
    police_report_number: str | None = Field(None, max_length=50)
    fire_department_notified: bool = Field(default=False)
    ambulance_notified: bool = Field(default=False)

    # Mídia
    images: list[str] | None = Field(None)
    videos: list[str] | None = Field(None)
    audio_recordings: list[str] | None = Field(None)
    attachments: list[dict] | None = Field(None)

    # Timestamp
    event_timestamp: datetime = Field(..., description="Data/hora do evento")

    # Metadados
    guardian_metadata: dict | None = Field(None)
    tags: list[str] | None = Field(None)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        """Valida e limpa o título."""
        return value.strip()


class GuardianOccurrenceResponse(BaseModel):
    """Schema de resposta para ocorrência."""

    id: str
    guardian_id: str
    occurrence_code: str
    occurrence_type: str
    severity: str
    status: str
    client_id: str
    contract_id: str | None
    post_id: str | None
    title: str
    description: str
    location: str | None
    location_details: str | None
    action_taken: str | None
    action_required: str | None
    resolution: str | None
    involved_persons: list | None
    witnesses: list | None
    reported_by: str | None
    reported_by_id: str | None
    operator_id: str | None
    operator_name: str | None
    response_time_seconds: int | None
    resolution_time_seconds: int | None
    escalated_to: str | None
    escalation_reason: str | None
    escalated_at: datetime | None
    police_notified: bool
    police_report_number: str | None
    fire_department_notified: bool
    ambulance_notified: bool
    images: list | None
    videos: list | None
    audio_recordings: list | None
    attachments: list | None
    event_timestamp: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    closed_at: datetime | None
    received_at: datetime
    is_false_alarm: bool
    requires_followup: bool
    followup_notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tags: list | None

    model_config = ConfigDict(from_attributes=True)


class GuardianOccurrenceFilter(BaseModel):
    """Schema para filtrar ocorrências."""

    search: str | None = Field(None, description="Busca textual")
    occurrence_type: OccurrenceType | None = Field(None, description="Tipo")
    severity: OccurrenceSeverity | None = Field(None, description="Gravidade")
    status: OccurrenceStatus | None = Field(None, description="Status")
    client_id: str | None = Field(None, description="ID do cliente")
    post_id: str | None = Field(None, description="ID do posto")
    is_open: bool | None = Field(None, description="Está aberta")
    is_critical: bool | None = Field(None, description="É crítica")
    is_false_alarm: bool | None = Field(None, description="É falso alarme")
    requires_followup: bool | None = Field(None, description="Requer follow-up")
    date_from: datetime | None = Field(None, description="Data inicial")
    date_to: datetime | None = Field(None, description="Data final")

    model_config = ConfigDict(use_enum_values=True)


class GuardianOccurrenceListResponse(BaseModel):
    """Schema para lista paginada de ocorrências."""

    items: list[GuardianOccurrenceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GuardianOccurrenceAcknowledge(BaseModel):
    """Schema para reconhecer ocorrência."""

    notes: str | None = Field(None, max_length=1000, description="Observações")


class GuardianOccurrenceResolve(BaseModel):
    """Schema para resolver ocorrência."""

    resolution: str = Field(..., min_length=1, description="Descrição da resolução")
    is_false_alarm: bool = Field(default=False, description="É falso alarme")
    requires_followup: bool = Field(default=False, description="Requer follow-up")
    followup_notes: str | None = Field(None, description="Notas de follow-up")


class GuardianOccurrenceEscalate(BaseModel):
    """Schema para escalar ocorrência."""

    escalated_to: str = Field(..., min_length=1, max_length=100)
    reason: str = Field(..., min_length=1, description="Motivo da escalação")


class GuardianOccurrenceStats(BaseModel):
    """Estatísticas de ocorrências."""

    total: int = Field(default=0, description="Total de ocorrências")
    open: int = Field(default=0, description="Abertas")
    acknowledged: int = Field(default=0, description="Reconhecidas")
    in_progress: int = Field(default=0, description="Em atendimento")
    resolved: int = Field(default=0, description="Resolvidas")
    escalated: int = Field(default=0, description="Escaladas")
    closed: int = Field(default=0, description="Fechadas")
    false_alarms: int = Field(default=0, description="Falsos alarmes")
    by_type: dict = Field(default_factory=dict, description="Por tipo")
    by_severity: dict = Field(default_factory=dict, description="Por gravidade")
    avg_response_time_seconds: float = Field(
        default=0.0,
        description="Tempo médio de resposta",
    )
    avg_resolution_time_seconds: float = Field(
        default=0.0,
        description="Tempo médio de resolução",
    )
    critical_open: int = Field(default=0, description="Críticas abertas")
    requires_followup_count: int = Field(default=0, description="Aguardando follow-up")
