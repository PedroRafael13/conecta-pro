"""
Schemas Pydantic para ServiceRequest (Solicitação de Serviço).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from modules.facilities.models.service_request import (
    ServiceRequestCategory,
    ServiceRequestPriority,
    ServiceRequestStatus,
)


class ServiceRequestBase(BaseModel):
    """Schema base para ServiceRequest."""

    title: str = Field(..., min_length=1, max_length=255, description="Título")
    description: str = Field(..., min_length=10, max_length=5000, description="Descrição")
    category: ServiceRequestCategory = Field(
        default=ServiceRequestCategory.MANUTENCAO,
        description="Categoria",
    )
    priority: ServiceRequestPriority = Field(
        default=ServiceRequestPriority.MEDIUM,
        description="Prioridade",
    )
    area_id: Optional[str] = Field(None, description="ID da área")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    condominium_id: Optional[str] = Field(None, description="ID do condomínio")
    requester_name: str = Field(..., min_length=2, max_length=255, description="Nome solicitante")
    requester_unit: Optional[str] = Field(None, max_length=50, description="Unidade")
    requester_contact: Optional[str] = Field(None, max_length=100, description="Contato")
    requester_email: Optional[EmailStr] = Field(None, description="Email")
    location_details: Optional[str] = Field(None, max_length=500, description="Local específico")
    floor: Optional[str] = Field(None, max_length=20, description="Andar")
    building: Optional[str] = Field(None, max_length=100, description="Bloco/Prédio")
    scheduled_date: Optional[date] = Field(None, description="Data agendada")
    photos: Optional[List[str]] = Field(None, description="Fotos")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")


class ServiceRequestCreate(ServiceRequestBase):
    """Schema para criação de ServiceRequest."""

    code: Optional[str] = Field(None, max_length=20, description="Código (auto-gerado se vazio)")
    requester_id: Optional[str] = Field(None, description="ID do solicitante")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida e normaliza o código da solicitação."""
        if v:
            return v.upper().strip()
        return v


class ServiceRequestUpdate(BaseModel):
    """Schema para atualização parcial de ServiceRequest."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    category: Optional[ServiceRequestCategory] = None
    status: Optional[ServiceRequestStatus] = None
    priority: Optional[ServiceRequestPriority] = None
    area_id: Optional[str] = None
    location_details: Optional[str] = Field(None, max_length=500)
    assigned_to: Optional[str] = None
    assigned_team: Optional[List[str]] = None
    scheduled_date: Optional[date] = None
    deadline: Optional[date] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    photos: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    resolution: Optional[str] = Field(None, max_length=5000)
    work_performed: Optional[str] = Field(None, max_length=5000)
    notes: Optional[str] = Field(None, max_length=2000)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    sla_hours: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class ServiceRequestAcknowledge(BaseModel):
    """Schema para reconhecer/receber solicitação."""

    notes: Optional[str] = Field(None, max_length=500, description="Observações")
    estimated_completion: Optional[date] = Field(None, description="Previsão de conclusão")


class ServiceRequestAssign(BaseModel):
    """Schema para atribuir responsável."""

    assigned_to: str = Field(..., description="ID do responsável")
    assigned_team: Optional[List[str]] = Field(None, description="IDs da equipe")
    scheduled_date: Optional[date] = Field(None, description="Data agendada")
    deadline: Optional[date] = Field(None, description="Prazo limite")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Custo estimado")
    notes: Optional[str] = Field(None, max_length=500, description="Observações")


class ServiceRequestApprove(BaseModel):
    """Schema para aprovar solicitação (quando requer aprovação de orçamento)."""

    notes: Optional[str] = Field(None, max_length=500, description="Observações")


class ServiceRequestReject(BaseModel):
    """Schema para rejeitar solicitação."""

    rejection_reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo da rejeição",
    )


class ServiceRequestComplete(BaseModel):
    """Schema para concluir solicitação."""

    resolution: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Resolução/Solução aplicada",
    )
    work_performed: Optional[str] = Field(
        None,
        max_length=5000,
        description="Trabalho realizado",
    )
    actual_cost: Optional[float] = Field(None, ge=0, description="Custo real")
    root_cause: Optional[str] = Field(None, max_length=2000, description="Causa raiz")
    completion_photos: Optional[List[str]] = Field(None, description="Fotos de conclusão")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")


class ServiceRequestCancel(BaseModel):
    """Schema para cancelar solicitação."""

    cancellation_reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo do cancelamento",
    )


class ServiceRequestFeedback(BaseModel):
    """Schema para avaliação do solicitante."""

    satisfaction_rating: int = Field(..., ge=1, le=5, description="Nota (1-5)")
    feedback: Optional[str] = Field(None, max_length=1000, description="Comentário")


class ServiceRequestResponse(BaseModel):
    """Schema de resposta para ServiceRequest."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: str
    category: str
    status: str
    priority: str
    area_id: Optional[str]
    client_id: Optional[str]
    condominium_id: Optional[str]
    requester_id: Optional[str]
    requester_name: str
    requester_unit: Optional[str]
    requester_contact: Optional[str]
    requester_email: Optional[str]
    location_details: Optional[str]
    floor: Optional[str]
    building: Optional[str]
    assigned_to: Optional[str]
    assigned_team: Optional[List[str]]
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    scheduled_date: Optional[date]
    deadline: Optional[date]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    closed_at: Optional[datetime]
    estimated_cost: float
    actual_cost: float
    requires_budget_approval: bool
    budget_approved: bool
    budget_approved_by: Optional[str]
    budget_approved_at: Optional[datetime]
    photos: Optional[List[str]]
    documents: Optional[List[str]]
    completion_photos: Optional[List[str]]
    resolution: Optional[str]
    root_cause: Optional[str]
    work_performed: Optional[str]
    satisfaction_rating: Optional[int]
    feedback: Optional[str]
    feedback_at: Optional[datetime]
    sla_hours: Optional[int]
    sla_breached: bool
    response_time_hours: Optional[float]
    resolution_time_hours: Optional[float]
    rejection_reason: Optional[str]
    cancellation_reason: Optional[str]
    ai_category_suggestion: Optional[str]
    ai_priority_suggestion: Optional[str]
    ai_analysis: Optional[Dict[str, Any]]
    notes: Optional[str]
    internal_notes: Optional[str]
    status_history: Optional[List[Dict[str, Any]]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_open: bool
    is_in_progress: bool
    is_completed: bool
    is_overdue: bool
    days_open: int
    has_sla_breach: bool


class ServiceRequestListResponse(BaseModel):
    """Schema para listagem paginada de ServiceRequests."""

    items: List[ServiceRequestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ServiceRequestFilter(BaseModel):
    """Schema para filtros de busca de ServiceRequests."""

    search: Optional[str] = Field(None, description="Busca por título ou código")
    category: Optional[ServiceRequestCategory] = None
    status: Optional[ServiceRequestStatus] = None
    priority: Optional[ServiceRequestPriority] = None
    area_id: Optional[str] = None
    client_id: Optional[str] = None
    condominium_id: Optional[str] = None
    requester_id: Optional[str] = None
    assigned_to: Optional[str] = None
    created_start: Optional[date] = None
    created_end: Optional[date] = None
    deadline_start: Optional[date] = None
    deadline_end: Optional[date] = None
    is_overdue: Optional[bool] = None
    has_sla_breach: Optional[bool] = None
    has_feedback: Optional[bool] = None
    min_rating: Optional[int] = Field(None, ge=1, le=5)


class ServiceRequestStats(BaseModel):
    """Estatísticas de solicitações de serviço."""

    total: int = Field(..., description="Total de solicitações")
    by_category: Dict[str, int] = Field(..., description="Por categoria")
    by_status: Dict[str, int] = Field(..., description="Por status")
    by_priority: Dict[str, int] = Field(..., description="Por prioridade")
    open_count: int = Field(..., description="Em aberto")
    overdue_count: int = Field(..., description="Atrasadas")
    sla_breach_count: int = Field(..., description="SLA violado")
    avg_response_time_hours: Optional[float] = Field(None, description="Tempo médio de resposta")
    avg_resolution_time_hours: Optional[float] = Field(None, description="Tempo médio de resolução")
    avg_satisfaction: Optional[float] = Field(None, description="Satisfação média")
    total_cost: float = Field(..., description="Custo total")
    created_this_month: int = Field(..., description="Criadas este mês")
    completed_this_month: int = Field(..., description="Concluídas este mês")


class ServiceRequestAISuggestion(BaseModel):
    """Sugestão de IA para solicitação."""

    suggested_category: ServiceRequestCategory = Field(..., description="Categoria sugerida")
    suggested_priority: ServiceRequestPriority = Field(..., description="Prioridade sugerida")
    confidence: float = Field(..., ge=0, le=1, description="Confiança (0-1)")
    similar_requests: List[str] = Field(..., description="IDs de solicitações similares")
    estimated_resolution_time: Optional[int] = Field(
        None,
        description="Tempo estimado de resolução (horas)",
    )
    suggested_assignee: Optional[str] = Field(None, description="Responsável sugerido")
    analysis: str = Field(..., description="Análise detalhada")
