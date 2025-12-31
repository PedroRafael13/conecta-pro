"""
Schemas Pydantic para GuardianOccurrence.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.guardian.models.guardian_occurrence import (
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)


class GuardianOccurrenceCreate(BaseModel):
    """Schema para criar ocorrência."""

    guardian_id: str = Field(..., min_length=1, max_length=100)
    occurrence_type: OccurrenceType = Field(default=OccurrenceType.OTHER)
    severity: OccurrenceSeverity = Field(default=OccurrenceSeverity.MEDIUM)
    client_id: str = Field(..., description="ID do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    post_id: Optional[str] = Field(None, description="ID do posto")

    # Descrição
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: Optional[str] = Field(None, max_length=255)
    location_details: Optional[str] = Field(None)

    # Ações
    action_taken: Optional[str] = Field(None)
    action_required: Optional[str] = Field(None)

    # Pessoas
    involved_persons: Optional[List[dict]] = Field(None)
    witnesses: Optional[List[dict]] = Field(None)
    reported_by: Optional[str] = Field(None, max_length=100)
    reported_by_id: Optional[str] = Field(None)

    # Serviços externos
    police_notified: bool = Field(default=False)
    police_report_number: Optional[str] = Field(None, max_length=50)
    fire_department_notified: bool = Field(default=False)
    ambulance_notified: bool = Field(default=False)

    # Mídia
    images: Optional[List[str]] = Field(None)
    videos: Optional[List[str]] = Field(None)
    audio_recordings: Optional[List[str]] = Field(None)
    attachments: Optional[List[dict]] = Field(None)

    # Timestamp
    event_timestamp: datetime = Field(..., description="Data/hora do evento")

    # Metadados
    guardian_metadata: Optional[dict] = Field(None)
    tags: Optional[List[str]] = Field(None)

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
    contract_id: Optional[str]
    post_id: Optional[str]
    title: str
    description: str
    location: Optional[str]
    location_details: Optional[str]
    action_taken: Optional[str]
    action_required: Optional[str]
    resolution: Optional[str]
    involved_persons: Optional[list]
    witnesses: Optional[list]
    reported_by: Optional[str]
    reported_by_id: Optional[str]
    operator_id: Optional[str]
    operator_name: Optional[str]
    response_time_seconds: Optional[int]
    resolution_time_seconds: Optional[int]
    escalated_to: Optional[str]
    escalation_reason: Optional[str]
    escalated_at: Optional[datetime]
    police_notified: bool
    police_report_number: Optional[str]
    fire_department_notified: bool
    ambulance_notified: bool
    images: Optional[list]
    videos: Optional[list]
    audio_recordings: Optional[list]
    attachments: Optional[list]
    event_timestamp: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    received_at: datetime
    is_false_alarm: bool
    requires_followup: bool
    followup_notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tags: Optional[list]

    model_config = ConfigDict(from_attributes=True)


class GuardianOccurrenceFilter(BaseModel):
    """Schema para filtrar ocorrências."""

    search: Optional[str] = Field(None, description="Busca textual")
    occurrence_type: Optional[OccurrenceType] = Field(None, description="Tipo")
    severity: Optional[OccurrenceSeverity] = Field(None, description="Gravidade")
    status: Optional[OccurrenceStatus] = Field(None, description="Status")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    post_id: Optional[str] = Field(None, description="ID do posto")
    is_open: Optional[bool] = Field(None, description="Está aberta")
    is_critical: Optional[bool] = Field(None, description="É crítica")
    is_false_alarm: Optional[bool] = Field(None, description="É falso alarme")
    requires_followup: Optional[bool] = Field(None, description="Requer follow-up")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")

    model_config = ConfigDict(use_enum_values=True)


class GuardianOccurrenceListResponse(BaseModel):
    """Schema para lista paginada de ocorrências."""

    items: List[GuardianOccurrenceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GuardianOccurrenceAcknowledge(BaseModel):
    """Schema para reconhecer ocorrência."""

    notes: Optional[str] = Field(None, max_length=1000, description="Observações")


class GuardianOccurrenceResolve(BaseModel):
    """Schema para resolver ocorrência."""

    resolution: str = Field(..., min_length=1, description="Descrição da resolução")
    is_false_alarm: bool = Field(default=False, description="É falso alarme")
    requires_followup: bool = Field(default=False, description="Requer follow-up")
    followup_notes: Optional[str] = Field(None, description="Notas de follow-up")


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
