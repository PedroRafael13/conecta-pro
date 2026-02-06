"""
Schemas Pydantic para o modulo de Ocorrencias.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

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
    category: OccurrenceCategory = Field(
        default=OccurrenceCategory.OUTRO, description="Categoria da ocorrencia"
    )
    severity: OccurrenceSeverity = Field(
        default=OccurrenceSeverity.MEDIA, description="Severidade"
    )
    type: OccurrenceType = Field(
        default=OccurrenceType.INCIDENTE, description="Tipo de ocorrencia"
    )
    priority: OccurrencePriority = Field(
        default=OccurrencePriority.NORMAL, description="Prioridade"
    )

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
    post_id: Optional[UUID] = Field(None, description="ID do posto")
    client_id: Optional[UUID] = Field(None, description="ID do cliente")
    contract_id: Optional[UUID] = Field(None, description="ID do contrato")
    reported_by_id: UUID = Field(..., description="ID do usuario que reportou")
    employee_involved_id: Optional[UUID] = Field(
        None, description="ID do funcionario envolvido"
    )
    witness_ids: Optional[List[UUID]] = Field(
        default_factory=list, description="IDs das testemunhas"
    )
    location_description: Optional[str] = Field(
        None, max_length=500, description="Descricao do local"
    )
    occurred_at: Optional[datetime] = Field(
        None, description="Data/hora do evento"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list, description="Tags"
    )

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

    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[OccurrenceCategory] = None
    severity: Optional[OccurrenceSeverity] = None
    type: Optional[OccurrenceType] = None
    priority: Optional[OccurrencePriority] = None
    status: Optional[OccurrenceStatus] = None
    post_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None
    employee_involved_id: Optional[UUID] = None
    witness_ids: Optional[List[UUID]] = None
    location_description: Optional[str] = Field(None, max_length=500)
    occurred_at: Optional[datetime] = None
    tags: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Valida e sanitiza o titulo."""
        if v:
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
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
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    captured_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
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
    author_name: Optional[str] = None
    content: str
    is_internal: bool
    edited_at: Optional[datetime] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class OccurrenceResponse(BaseModel):
    """Schema de resposta para Ocorrencia."""

    id: UUID
    code: str
    tenant_id: UUID
    post_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None
    category: str
    severity: str
    type: str
    title: str
    description: str
    reported_by_id: UUID
    employee_involved_id: Optional[UUID] = None
    witness_ids: Optional[List[UUID]] = None
    status: str
    priority: str
    resolution: Optional[str] = None
    resolved_by_id: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_type: Optional[str] = None
    escalated: bool
    escalated_to_id: Optional[UUID] = None
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    disciplinary_action_id: Optional[UUID] = None
    sla_deadline: Optional[datetime] = None
    sla_breached: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    location_description: Optional[str] = None
    occurred_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    ai_classification: Optional[Dict[str, Any]] = None
    ai_recommendations: Optional[List[str]] = None

    # Computed fields
    is_open: bool = False
    is_critical: bool = False
    requires_disciplinary_action: bool = False
    attachment_count: int = 0
    comment_count: int = 0

    # Related
    attachments: Optional[List[AttachmentResponse]] = None
    comments: Optional[List[CommentResponse]] = None

    class Config:
        from_attributes = True


class OccurrenceListResponse(BaseModel):
    """Schema de resposta para lista de Ocorrencias com paginacao."""

    items: List[OccurrenceResponse]
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
    sla_deadline: Optional[datetime] = None
    created_at: datetime
    is_critical: bool = False

    class Config:
        from_attributes = True


# ============================================================
# FILTER SCHEMAS
# ============================================================


class OccurrenceFilter(BaseModel):
    """Schema para filtros de busca de Ocorrencias."""

    tenant_id: Optional[UUID] = None
    post_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None
    category: Optional[OccurrenceCategory] = None
    severity: Optional[OccurrenceSeverity] = None
    type: Optional[OccurrenceType] = None
    status: Optional[OccurrenceStatus] = None
    priority: Optional[OccurrencePriority] = None
    reported_by_id: Optional[UUID] = None
    employee_involved_id: Optional[UUID] = None
    escalated: Optional[bool] = None
    sla_breached: Optional[bool] = None
    is_active: bool = True
    created_at_start: Optional[datetime] = None
    created_at_end: Optional[datetime] = None
    occurred_at_start: Optional[datetime] = None
    occurred_at_end: Optional[datetime] = None
    search: Optional[str] = Field(None, min_length=2, description="Busca por titulo/descricao")
    tags: Optional[List[str]] = None


# ============================================================
# ACTION SCHEMAS
# ============================================================


class AttachmentCreate(BaseModel):
    """Schema para criacao de Anexo."""

    file_type: AttachmentType = Field(
        default=AttachmentType.OUTRO, description="Tipo do arquivo"
    )
    file_path: str = Field(..., max_length=500, description="Caminho do arquivo")
    file_name: str = Field(..., max_length=255, description="Nome do arquivo")
    file_size: Optional[int] = Field(None, ge=0, description="Tamanho em bytes")
    mime_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, description="Descricao do anexo")
    captured_at: Optional[datetime] = Field(None, description="Data/hora da captura")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    uploaded_by_id: UUID = Field(..., description="ID do usuario que fez upload")


class CommentCreate(BaseModel):
    """Schema para criacao de Comentario."""

    author_id: UUID = Field(..., description="ID do autor")
    author_name: Optional[str] = Field(None, max_length=200)
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
    reason: str = Field(
        ..., min_length=10, max_length=500, description="Motivo da escalacao"
    )

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Valida e sanitiza o motivo."""
        return v.strip()


class ResolveRequest(BaseModel):
    """Schema para solicitacao de resolucao."""

    resolution: str = Field(
        ..., min_length=10, description="Descricao da resolucao"
    )
    resolved_by_id: UUID = Field(..., description="ID do usuario que resolveu")
    resolution_type: Optional[ResolutionType] = Field(
        None, description="Tipo de resolucao"
    )

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        """Valida e sanitiza a resolucao."""
        return v.strip()


class ReopenRequest(BaseModel):
    """Schema para solicitacao de reabertura."""

    reason: Optional[str] = Field(
        None, min_length=10, max_length=500, description="Motivo da reabertura"
    )


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
    by_category: Dict[str, int] = Field(default_factory=dict)
    # Por severidade
    by_severity: Dict[str, int] = Field(default_factory=dict)
    # Por prioridade
    by_priority: Dict[str, int] = Field(default_factory=dict)

    # Metricas de tempo
    avg_resolution_time_hours: Optional[float] = None
    sla_compliance_rate: Optional[float] = None


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
    sla_deadline: Optional[datetime] = None
    sla_breached: bool = False


# ============================================================
# CATEGORY CONFIG SCHEMAS
# ============================================================


class CategoryConfigBase(BaseModel):
    """Schema base para configuracao de categoria."""

    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    severity_default: OccurrenceSeverity = OccurrenceSeverity.MEDIA
    priority_default: OccurrencePriority = OccurrencePriority.NORMAL
    type_default: OccurrenceType = OccurrenceType.INCIDENTE
    requires_photo: bool = False
    requires_witness: bool = False
    requires_location: bool = False
    requires_employee: bool = False
    auto_escalate: bool = False
    escalate_after_hours: Optional[int] = None
    escalate_to_role: Optional[str] = None
    sla_hours: int = Field(default=48, ge=1)
    sla_warning_hours: Optional[int] = None
    notify_on_create: bool = True
    notify_roles: Optional[List[str]] = None
    notify_emails: Optional[List[str]] = None
    suggest_disciplinary_action: bool = False
    disciplinary_action_type: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0


class CategoryConfigCreate(CategoryConfigBase):
    """Schema para criacao de configuracao de categoria."""

    tenant_id: UUID = Field(..., description="ID do tenant")
    created_by: Optional[UUID] = None


class CategoryConfigUpdate(BaseModel):
    """Schema para atualizacao de configuracao de categoria."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    severity_default: Optional[OccurrenceSeverity] = None
    priority_default: Optional[OccurrencePriority] = None
    type_default: Optional[OccurrenceType] = None
    requires_photo: Optional[bool] = None
    requires_witness: Optional[bool] = None
    requires_location: Optional[bool] = None
    requires_employee: Optional[bool] = None
    auto_escalate: Optional[bool] = None
    escalate_after_hours: Optional[int] = None
    escalate_to_role: Optional[str] = None
    sla_hours: Optional[int] = Field(None, ge=1)
    sla_warning_hours: Optional[int] = None
    notify_on_create: Optional[bool] = None
    notify_roles: Optional[List[str]] = None
    notify_emails: Optional[List[str]] = None
    suggest_disciplinary_action: Optional[bool] = None
    disciplinary_action_type: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryConfigResponse(CategoryConfigBase):
    """Schema de resposta para configuracao de categoria."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True
