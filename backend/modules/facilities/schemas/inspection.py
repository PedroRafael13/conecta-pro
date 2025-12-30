"""
Schemas Pydantic para Inspection (Inspeção/Vistoria).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.facilities.models.inspection import (
    InspectionResult,
    InspectionStatus,
    InspectionType,
)


class InspectionBase(BaseModel):
    """Schema base para Inspection."""

    title: str = Field(..., min_length=1, max_length=255, description="Título")
    description: Optional[str] = Field(None, max_length=2000, description="Descrição")
    inspection_type: InspectionType = Field(
        default=InspectionType.ROTINA,
        description="Tipo de inspeção",
    )
    area_id: Optional[str] = Field(None, description="ID da área")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    checklist_template_id: Optional[str] = Field(None, description="Template de checklist")
    scheduled_date: Optional[date] = Field(None, description="Data agendada")
    inspector_id: Optional[str] = Field(None, description="ID do inspetor")
    inspector_name: Optional[str] = Field(None, max_length=255, description="Nome do inspetor")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")
    is_recurring: bool = Field(default=False, description="É recorrente")
    recurrence_pattern: Optional[str] = Field(None, description="Padrão de recorrência")
    recurrence_interval: Optional[int] = Field(None, ge=1, description="Intervalo")


class InspectionCreate(InspectionBase):
    """Schema para criação de Inspection."""

    code: Optional[str] = Field(None, max_length=20, description="Código (auto-gerado se vazio)")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida e normaliza o código da inspeção."""
        if v:
            return v.upper().strip()
        return v


class InspectionUpdate(BaseModel):
    """Schema para atualização parcial de Inspection."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    inspection_type: Optional[InspectionType] = None
    status: Optional[InspectionStatus] = None
    result: Optional[InspectionResult] = None
    area_id: Optional[str] = None
    scheduled_date: Optional[date] = None
    next_inspection_date: Optional[date] = None
    inspector_id: Optional[str] = None
    inspector_name: Optional[str] = Field(None, max_length=255)
    score: Optional[float] = Field(None, ge=0, le=100)
    findings: Optional[str] = Field(None, max_length=5000)
    recommendations: Optional[str] = Field(None, max_length=5000)
    non_conformities: Optional[Dict[str, Any]] = None
    corrective_actions: Optional[Dict[str, Any]] = None
    photos: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=2000)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None


class InspectionStart(BaseModel):
    """Schema para iniciar uma inspeção."""

    inspector_id: Optional[str] = Field(None, description="ID do inspetor")
    inspector_name: Optional[str] = Field(None, max_length=255, description="Nome do inspetor")
    notes: Optional[str] = Field(None, max_length=500, description="Observações iniciais")


class InspectionComplete(BaseModel):
    """Schema para concluir uma inspeção."""

    result: InspectionResult = Field(..., description="Resultado")
    score: Optional[float] = Field(None, ge=0, le=100, description="Pontuação")
    findings: Optional[str] = Field(None, max_length=5000, description="Achados")
    recommendations: Optional[str] = Field(None, max_length=5000, description="Recomendações")
    non_conformities: Optional[Dict[str, Any]] = Field(None, description="Não conformidades")
    corrective_actions: Optional[Dict[str, Any]] = Field(None, description="Ações corretivas")
    photos: Optional[List[str]] = Field(None, description="Fotos")
    next_inspection_date: Optional[date] = Field(None, description="Próxima inspeção")
    signature_inspector: Optional[str] = Field(None, description="Assinatura inspetor")
    signature_responsible: Optional[str] = Field(None, description="Assinatura responsável")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")


class InspectionReview(BaseModel):
    """Schema para revisão de inspeção."""

    approved: bool = Field(..., description="Se aprovada")
    internal_notes: Optional[str] = Field(None, max_length=2000, description="Notas internas")


class InspectionResponse(BaseModel):
    """Schema de resposta para Inspection."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: Optional[str]
    inspection_type: str
    status: str
    result: Optional[str]
    area_id: Optional[str]
    client_id: Optional[str]
    checklist_template_id: Optional[str]
    scheduled_date: Optional[date]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    next_inspection_date: Optional[date]
    inspector_id: Optional[str]
    inspector_name: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    score: Optional[float]
    total_items: int
    items_ok: int
    items_warning: int
    items_critical: int
    findings: Optional[str]
    recommendations: Optional[str]
    non_conformities: Optional[Dict[str, Any]]
    corrective_actions: Optional[Dict[str, Any]]
    photos: Optional[List[str]]
    documents: Optional[List[str]]
    signature_inspector: Optional[str]
    signature_responsible: Optional[str]
    ai_analysis: Optional[Dict[str, Any]]
    ai_score: Optional[float]
    ai_recommendations: Optional[List[str]]
    notes: Optional[str]
    internal_notes: Optional[str]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_interval: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_completed: bool
    is_pending: bool
    compliance_rate: Optional[float]
    has_critical_issues: bool
    duration_minutes: Optional[int]


class InspectionListResponse(BaseModel):
    """Schema para listagem paginada de Inspections."""

    items: List[InspectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class InspectionFilter(BaseModel):
    """Schema para filtros de busca de Inspections."""

    search: Optional[str] = Field(None, description="Busca por título ou código")
    inspection_type: Optional[InspectionType] = None
    status: Optional[InspectionStatus] = None
    result: Optional[InspectionResult] = None
    area_id: Optional[str] = None
    client_id: Optional[str] = None
    inspector_id: Optional[str] = None
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    has_critical_issues: Optional[bool] = None
    is_recurring: Optional[bool] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)


class InspectionStats(BaseModel):
    """Estatísticas de inspeções."""

    total: int = Field(..., description="Total de inspeções")
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    by_status: Dict[str, int] = Field(..., description="Por status")
    by_result: Dict[str, int] = Field(..., description="Por resultado")
    avg_score: Optional[float] = Field(None, description="Pontuação média")
    avg_compliance_rate: Optional[float] = Field(None, description="Taxa média de conformidade")
    with_critical_issues: int = Field(..., description="Com issues críticos")
    pending_review: int = Field(..., description="Aguardando revisão")
    scheduled_this_month: int = Field(..., description="Agendadas este mês")
    completed_this_month: int = Field(..., description="Concluídas este mês")


class InspectionAIAnalysis(BaseModel):
    """Resultado da análise de IA da inspeção."""

    score: float = Field(..., ge=0, le=100, description="Pontuação IA")
    risk_level: str = Field(..., description="Nível de risco")
    key_findings: List[str] = Field(..., description="Achados principais")
    recommendations: List[str] = Field(..., description="Recomendações")
    trend: str = Field(..., description="Tendência (improving, stable, declining)")
    priority_areas: List[str] = Field(..., description="Áreas prioritárias")
    estimated_remediation_cost: Optional[float] = Field(None, description="Custo estimado")
