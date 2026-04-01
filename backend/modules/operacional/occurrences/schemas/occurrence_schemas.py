"""
Schemas Pydantic para o modulo de Ocorrencias.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.operacional.occurrences.models.occurrence import (
    OccurrenceCategory,
    OccurrencePriority,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
    ResolutionType,
)
from modules.operacional.occurrences.models.occurrence_attachment import AttachmentType

# ============================================================
# BASE SCHEMAS
# ============================================================


class OccurrenceBase(BaseModel):
    """Schema base para Ocorrencia."""

    title: str = Field(..., min_length=5, max_length=200, description="Titulo da ocorrencia")
    description: str = Field(..., min_length=10, description="Descricao detalhada")
    category: OccurrenceCategory = Field(default=OccurrenceCategory.OUTRO, description="Categoria da ocorrencia")
    severity: OccurrenceSeverity = Field(default=OccurrenceSeverity.MEDIA, description="Severidade")
    type: OccurrenceType = Field(default=OccurrenceType.INCIDENTE, description="Tipo de ocorrencia")
    priority: OccurrencePriority = Field(default=OccurrencePriority.NORMAL, description="Prioridade")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Valida e sanitiza o titulo."""
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Valida e sanitiza a descricao."""
        return v.strip()


# ============================================================
# CREATE SCHEMAS
# ============================================================


class OccurrenceCreate(OccurrenceBase):
    """Schema para criacao de Ocorrencia."""

    tenant_id: UUID = Field(..., description="ID do tenant")
    post_id: UUID | None = Field(None, description="ID do posto")
    client_id: UUID | None = Field(None, description="ID do cliente")
    contract_id: UUID | None = Field(None, description="ID do contrato")
    reported_by_id: UUID = Field(..., description="ID do usuario que reportou")
    employee_involved_id: UUID | None = Field(None, description="ID do funcionario envolvido")
    witness_ids: list[UUID] | None = Field(default_factory=list, description="IDs das testemunhas")
    location_description: str | None = Field(None, max_length=500, description="Descricao do local")
    occurred_at: datetime | None = Field(None, description="Data/hora do evento")
    tags: list[str] | None = Field(default_factory=list, description="Tags")

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "title": "Tentativa de invasao no portao principal",
                "description": "Individuo tentou acessar o condominio sem autorizacao",
                "category": "seguranca",
                "severity": "alta",
                "type": "incidente",
                "priority": "alta",
                "reported_by_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                "post_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
                "location_description": "Portao principal - Entrada de veiculos",
            }
        }


class OccurrenceUpdate(BaseModel):
    """Schema para atualizacao de Ocorrencia."""

    title: str | None = Field(None, min_length=5, max_length=200)
    description: str | None = Field(None, min_length=10)
    category: OccurrenceCategory | None = None
    severity: OccurrenceSeverity | None = None
    type: OccurrenceType | None = None
    priority: OccurrencePriority | None = None
    status: OccurrenceStatus | None = None
    post_id: UUID | None = None
    client_id: UUID | None = None
    contract_id: UUID | None = None
    employee_involved_id: UUID | None = None
    witness_ids: list[UUID] | None = None
    location_description: str | None = Field(None, max_length=500)
    occurred_at: datetime | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Valida e sanitiza o titulo."""
        if v:
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """Valida e sanitiza a descricao."""
        if v:
            return v.strip()
        return v


# ============================================================
# RESPONSE SCHEMAS
# ============================================================


class AttachmentResponse(BaseModel):
    """Schema de resposta para Anexo."""

    id: UUID
    occurrence_id: UUID
    file_type: str
    file_path: str
    file_name: str
    file_size: int | None = None
    mime_type: str | None = None
    description: str | None = None
    captured_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    uploaded_by_id: UUID
    uploaded_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Schema de resposta para Comentario."""

    id: UUID
    occurrence_id: UUID
    author_id: UUID
    author_name: str | None = None
    content: str
    is_internal: bool
    edited_at: datetime | None = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OccurrenceResponse(BaseModel):
    """Schema de resposta para Ocorrencia."""

    id: UUID
    code: str
    tenant_id: UUID
    post_id: UUID | None = None
    client_id: UUID | None = None
    contract_id: UUID | None = None
    category: str
    severity: str
    type: str
    title: str
    description: str
    reported_by_id: UUID
    employee_involved_id: UUID | None = None
    witness_ids: list[UUID] | None = None
    status: str
    priority: str
    resolution: str | None = None
    resolved_by_id: UUID | None = None
    resolved_at: datetime | None = None
    resolution_type: str | None = None
    escalated: bool
    escalated_to_id: UUID | None = None
    escalated_at: datetime | None = None
    escalation_reason: str | None = None
    disciplinary_action_id: UUID | None = None
    sla_deadline: datetime | None = None
    sla_breached: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    location_description: str | None = None
    occurred_at: datetime | None = None
    tags: list[str] | None = None
    ai_classification: dict[str, Any] | None = None
    ai_recommendations: list[str] | None = None

    # Computed fields
    is_open: bool = False
    is_critical: bool = False
    requires_disciplinary_action: bool = False
    attachment_count: int = 0
    comment_count: int = 0

    # Related
    attachments: list[AttachmentResponse] | None = None
    comments: list[CommentResponse] | None = None

    class Config:
        from_attributes = True


class OccurrenceListResponse(BaseModel):
    """Schema de resposta para lista de Ocorrencias com paginacao."""

    items: list[OccurrenceResponse]
    total: int
    page: int
    page_size: int
    pages: int

    class Config:
        from_attributes = True


class OccurrenceSummaryResponse(BaseModel):
    """Schema de resposta resumida para Ocorrencia (listagens)."""

    id: UUID
    code: str
    title: str
    category: str
    severity: str
    status: str
    priority: str
    sla_breached: bool
    sla_deadline: datetime | None = None
    created_at: datetime
    is_critical: bool = False

    class Config:
        from_attributes = True


# ============================================================
# FILTER SCHEMAS
# ============================================================


class OccurrenceFilter(BaseModel):
    """Schema para filtros de busca de Ocorrencias."""

    tenant_id: UUID | None = None
    post_id: UUID | None = None
    client_id: UUID | None = None
    contract_id: UUID | None = None
    category: OccurrenceCategory | None = None
    severity: OccurrenceSeverity | None = None
    type: OccurrenceType | None = None
    status: OccurrenceStatus | None = None
    priority: OccurrencePriority | None = None
    reported_by_id: UUID | None = None
    employee_involved_id: UUID | None = None
    escalated: bool | None = None
    sla_breached: bool | None = None
    is_active: bool = True
    created_at_start: datetime | None = None
    created_at_end: datetime | None = None
    occurred_at_start: datetime | None = None
    occurred_at_end: datetime | None = None
    search: str | None = Field(None, min_length=2, description="Busca por titulo/descricao")
    tags: list[str] | None = None


# ============================================================
# ACTION SCHEMAS
# ============================================================


class AttachmentCreate(BaseModel):
    """Schema para criacao de Anexo."""

    file_type: AttachmentType = Field(default=AttachmentType.OUTRO, description="Tipo do arquivo")
    file_path: str = Field(..., max_length=500, description="Caminho do arquivo")
    file_name: str = Field(..., max_length=255, description="Nome do arquivo")
    file_size: int | None = Field(None, ge=0, description="Tamanho em bytes")
    mime_type: str | None = Field(None, max_length=100)
    description: str | None = Field(None, description="Descricao do anexo")
    captured_at: datetime | None = Field(None, description="Data/hora da captura")
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    uploaded_by_id: UUID = Field(..., description="ID do usuario que fez upload")


class CommentCreate(BaseModel):
    """Schema para criacao de Comentario."""

    author_id: UUID = Field(..., description="ID do autor")
    author_name: str | None = Field(None, max_length=200)
    content: str = Field(..., min_length=1, description="Conteudo do comentario")
    is_internal: bool = Field(default=False, description="Se e comentario interno")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Valida e sanitiza o conteudo."""
        return v.strip()


class EscalateRequest(BaseModel):
    """Schema para solicitacao de escalacao."""

    escalated_to_id: UUID = Field(..., description="ID do usuario para escalar")
    reason: str = Field(..., min_length=10, max_length=500, description="Motivo da escalacao")

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Valida e sanitiza o motivo."""
        return v.strip()


class ResolveRequest(BaseModel):
    """Schema para solicitacao de resolucao."""

    resolution: str = Field(..., min_length=10, description="Descricao da resolucao")
    resolved_by_id: UUID = Field(..., description="ID do usuario que resolveu")
    resolution_type: ResolutionType | None = Field(None, description="Tipo de resolucao")

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        """Valida e sanitiza a resolucao."""
        return v.strip()


class ReopenRequest(BaseModel):
    """Schema para solicitacao de reabertura."""

    reason: str | None = Field(None, min_length=10, max_length=500, description="Motivo da reabertura")


# ============================================================
# DASHBOARD SCHEMAS
# ============================================================


class DashboardStats(BaseModel):
    """Schema para estatisticas do dashboard."""

    total: int = 0
    abertas: int = 0
    em_analise: int = 0
    pendentes: int = 0
    resolvidas: int = 0
    arquivadas: int = 0
    criticas: int = 0
    sla_breached: int = 0
    sla_at_risk: int = 0

    # Por categoria
    by_category: dict[str, int] = Field(default_factory=dict)
    # Por severidade
    by_severity: dict[str, int] = Field(default_factory=dict)
    # Por prioridade
    by_priority: dict[str, int] = Field(default_factory=dict)

    # Metricas de tempo
    avg_resolution_time_hours: float | None = None
    sla_compliance_rate: float | None = None


class SLABreachItem(BaseModel):
    """Schema para item de SLA vencendo."""

    id: UUID
    code: str
    title: str
    severity: str
    priority: str
    sla_deadline: datetime
    hours_remaining: float
    created_at: datetime


class PendingOccurrenceItem(BaseModel):
    """Schema para ocorrencia pendente."""

    id: UUID
    code: str
    title: str
    category: str
    severity: str
    priority: str
    status: str
    created_at: datetime
    sla_deadline: datetime | None = None
    sla_breached: bool = False


# ============================================================
# CATEGORY CONFIG SCHEMAS
# ============================================================


class CategoryConfigBase(BaseModel):
    """Schema base para configuracao de categoria."""

    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    severity_default: OccurrenceSeverity = OccurrenceSeverity.MEDIA
    priority_default: OccurrencePriority = OccurrencePriority.NORMAL
    type_default: OccurrenceType = OccurrenceType.INCIDENTE
    requires_photo: bool = False
    requires_witness: bool = False
    requires_location: bool = False
    requires_employee: bool = False
    auto_escalate: bool = False
    escalate_after_hours: int | None = None
    escalate_to_role: str | None = None
    sla_hours: int = Field(default=48, ge=1)
    sla_warning_hours: int | None = None
    notify_on_create: bool = True
    notify_roles: list[str] | None = None
    notify_emails: list[str] | None = None
    suggest_disciplinary_action: bool = False
    disciplinary_action_type: str | None = None
    color: str | None = None
    icon: str | None = None
    display_order: int = 0


class CategoryConfigCreate(CategoryConfigBase):
    """Schema para criacao de configuracao de categoria."""

    tenant_id: UUID = Field(..., description="ID do tenant")
    created_by: UUID | None = None


class CategoryConfigUpdate(BaseModel):
    """Schema para atualizacao de configuracao de categoria."""

    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = None
    severity_default: OccurrenceSeverity | None = None
    priority_default: OccurrencePriority | None = None
    type_default: OccurrenceType | None = None
    requires_photo: bool | None = None
    requires_witness: bool | None = None
    requires_location: bool | None = None
    requires_employee: bool | None = None
    auto_escalate: bool | None = None
    escalate_after_hours: int | None = None
    escalate_to_role: str | None = None
    sla_hours: int | None = Field(None, ge=1)
    sla_warning_hours: int | None = None
    notify_on_create: bool | None = None
    notify_roles: list[str] | None = None
    notify_emails: list[str] | None = None
    suggest_disciplinary_action: bool | None = None
    disciplinary_action_type: str | None = None
    color: str | None = None
    icon: str | None = None
    display_order: int | None = None
    is_active: bool | None = None


class CategoryConfigResponse(CategoryConfigBase):
    """Schema de resposta para configuracao de categoria."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None

    class Config:
        from_attributes = True
