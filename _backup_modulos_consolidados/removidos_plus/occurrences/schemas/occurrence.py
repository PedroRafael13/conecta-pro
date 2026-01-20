"""Schemas para Occurrence."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.occurrences.models.occurrence import (
    OccurrencePriority,
    OccurrenceStatus,
    OccurrenceType,
    ReporterType,
)


class OccurrenceCreate(BaseModel):
    """Schema para criação de ocorrência."""

    model_config = ConfigDict(use_enum_values=True)

    # Classificação
    occurrence_type: OccurrenceType
    category_id: Optional[str] = None
    priority: OccurrencePriority = OccurrencePriority.MEDIA

    # Conteúdo
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    tags: Optional[list[str]] = None

    # Local
    condominium_id: str
    condominium_name: Optional[str] = None
    unit_id: Optional[str] = None
    unit_number: Optional[str] = None
    block: Optional[str] = None
    location: Optional[str] = None
    location_details: Optional[str] = None

    # Reportador
    reporter_type: ReporterType = ReporterType.MORADOR
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_email: Optional[str] = None
    reporter_phone: Optional[str] = None
    is_anonymous: bool = False

    # SLA (opcional, pode vir da categoria)
    sla_response_hours: Optional[int] = None
    sla_resolution_hours: Optional[int] = None

    # Metadados
    source: Optional[str] = None
    metadata: Optional[dict] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Valida título."""
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Valida descrição."""
        return v.strip()


class OccurrenceUpdate(BaseModel):
    """Schema para atualização de ocorrência."""

    model_config = ConfigDict(use_enum_values=True)

    occurrence_type: Optional[OccurrenceType] = None
    category_id: Optional[str] = None
    priority: Optional[OccurrencePriority] = None
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    tags: Optional[list[str]] = None
    location: Optional[str] = None
    location_details: Optional[str] = None
    is_public: Optional[bool] = None
    is_pinned: Optional[bool] = None


class OccurrenceAssign(BaseModel):
    """Schema para atribuição de ocorrência."""

    assigned_to_id: str
    assigned_to_name: str
    assigned_by_id: Optional[str] = None
    assigned_by_name: Optional[str] = None


class OccurrenceResolve(BaseModel):
    """Schema para resolução de ocorrência."""

    resolved_by_id: str
    resolved_by_name: str
    resolution_description: Optional[str] = None
    resolution_type: Optional[str] = None


class OccurrenceEscalate(BaseModel):
    """Schema para escalonamento de ocorrência."""

    escalated_to_id: str
    escalated_to_name: str
    reason: Optional[str] = None


class OccurrenceRate(BaseModel):
    """Schema para avaliação de ocorrência."""

    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class OccurrenceResponse(BaseModel):
    """Schema de resposta de ocorrência."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: str
    occurrence_code: str
    occurrence_type: str
    category_id: Optional[str] = None
    priority: str
    status: str
    title: str
    description: str
    tags: Optional[list] = None

    # Local
    condominium_id: str
    condominium_name: Optional[str] = None
    unit_id: Optional[str] = None
    unit_number: Optional[str] = None
    block: Optional[str] = None
    location: Optional[str] = None

    # Reportador
    reporter_type: str
    reporter_id: Optional[str] = None
    reporter_name: Optional[str] = None
    is_anonymous: bool

    # Responsável
    assigned_to_id: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_at: Optional[datetime] = None

    # SLA
    sla_response_deadline: Optional[datetime] = None
    sla_resolution_deadline: Optional[datetime] = None
    sla_response_met: Optional[bool] = None
    sla_resolution_met: Optional[bool] = None
    first_response_at: Optional[datetime] = None

    # Resolução
    resolved_at: Optional[datetime] = None
    resolved_by_name: Optional[str] = None
    resolution_description: Optional[str] = None

    # Avaliação
    satisfaction_rating: Optional[int] = None

    # Escalonamento
    is_escalated: bool
    escalation_level: int

    # Métricas
    comment_count: int
    attachment_count: int
    view_count: int

    # IA
    ai_priority_score: Optional[float] = None
    ai_sentiment: Optional[str] = None

    # Controle
    is_active: bool
    is_public: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    # Computed
    is_open: Optional[bool] = None
    is_overdue_response: Optional[bool] = None
    is_overdue_resolution: Optional[bool] = None
    age_hours: Optional[float] = None


class OccurrenceListResponse(BaseModel):
    """Schema de lista de ocorrências."""

    items: list[OccurrenceResponse]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


class OccurrenceFilter(BaseModel):
    """Schema de filtro de ocorrências."""

    model_config = ConfigDict(use_enum_values=True)

    occurrence_type: Optional[OccurrenceType] = None
    category_id: Optional[str] = None
    priority: Optional[OccurrencePriority] = None
    status: Optional[OccurrenceStatus] = None
    condominium_id: Optional[str] = None
    unit_id: Optional[str] = None
    reporter_id: Optional[str] = None
    reporter_type: Optional[ReporterType] = None
    assigned_to_id: Optional[str] = None
    is_anonymous: Optional[bool] = None
    is_escalated: Optional[bool] = None
    is_overdue: Optional[bool] = None
    is_open: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    tags: Optional[list[str]] = None


class OccurrenceStats(BaseModel):
    """Estatísticas de ocorrências."""

    total: int = 0
    open: int = 0
    closed: int = 0
    resolved: int = 0
    cancelled: int = 0
    escalated: int = 0
    overdue_response: int = 0
    overdue_resolution: int = 0
    by_type: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    by_category: dict = Field(default_factory=dict)
    avg_resolution_hours: Optional[float] = None
    avg_response_hours: Optional[float] = None
    avg_satisfaction: Optional[float] = None
    sla_response_rate: Optional[float] = None
    sla_resolution_rate: Optional[float] = None
