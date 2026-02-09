"""
Schemas Pydantic para Opportunity.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.crm.models.opportunity import (
    LossReason,
    OpportunityPriority,
    OpportunityStage,
)


class OpportunityBase(BaseModel):
    """Schema base para Opportunity."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: str | None = Field(None, max_length=20)
    company_name: str | None = Field(None, max_length=255)
    value: float = Field(default=0.0, ge=0)
    probability: int = Field(default=10, ge=0, le=100)
    expected_close_date: date | None = None
    notes: str | None = None


class OpportunityCreate(OpportunityBase):
    """Schema para criação de Opportunity."""

    lead_id: str | None = None
    stage: OpportunityStage = OpportunityStage.QUALIFICATION
    priority: OpportunityPriority = OpportunityPriority.MEDIUM
    owner_id: str | None = None


class OpportunityCreateFromLead(BaseModel):
    """Schema para criar Opportunity a partir de um Lead."""

    lead_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    value: float = Field(default=0.0, ge=0)
    probability: int = Field(default=20, ge=0, le=100)
    expected_close_date: date | None = None
    priority: OpportunityPriority = OpportunityPriority.MEDIUM
    owner_id: str | None = None
    notes: str | None = None


class OpportunityUpdate(BaseModel):
    """Schema para atualização de Opportunity."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    contact_name: str | None = Field(None, min_length=1, max_length=255)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(None, max_length=20)
    company_name: str | None = Field(None, max_length=255)
    stage: OpportunityStage | None = None
    priority: OpportunityPriority | None = None
    value: float | None = Field(None, ge=0)
    probability: int | None = Field(None, ge=0, le=100)
    expected_close_date: date | None = None
    owner_id: str | None = None
    notes: str | None = None


class OpportunityStageUpdate(BaseModel):
    """Schema para atualização de estágio."""

    stage: OpportunityStage
    notes: str | None = None


class OpportunityClose(BaseModel):
    """Schema para fechar oportunidade (ganhou ou perdeu)."""

    won: bool
    actual_close_date: date | None = None
    notes: str | None = None
    # Campos para perda
    loss_reason: LossReason | None = None
    competitor: str | None = Field(None, max_length=255)


class OpportunityResponse(BaseModel):
    """Schema de resposta para Opportunity."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    lead_id: str | None
    contact_name: str
    contact_email: str
    contact_phone: str | None
    company_name: str | None
    stage: OpportunityStage
    priority: OpportunityPriority
    value: float
    probability: int
    weighted_value: float
    expected_close_date: date | None
    actual_close_date: date | None
    owner_id: str | None
    loss_reason: LossReason | None
    competitor: str | None
    win_notes: str | None
    loss_notes: str | None
    notes: str | None
    is_open: bool
    is_won: bool
    is_lost: bool
    is_overdue: bool
    days_in_pipeline: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OpportunityListResponse(BaseModel):
    """Schema de resposta para lista de Opportunities."""

    items: list[OpportunityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class OpportunityFilter(BaseModel):
    """Schema para filtros de busca."""

    stage: OpportunityStage | None = None
    priority: OpportunityPriority | None = None
    owner_id: str | None = None
    is_open: bool | None = None
    is_overdue: bool | None = None
    min_value: float | None = None
    max_value: float | None = None
    company_name: str | None = None
    search: str | None = None


class PipelineStats(BaseModel):
    """Estatísticas do pipeline de vendas."""

    total_opportunities: int
    open_opportunities: int
    won_opportunities: int
    lost_opportunities: int
    total_value: float
    weighted_value: float
    won_value: float
    lost_value: float
    win_rate: float  # Percentual de ganhos
    avg_deal_size: float
    avg_days_to_close: float
    by_stage: dict[str, int]
    by_priority: dict[str, int]
    overdue_count: int


class PipelineForecast(BaseModel):
    """Previsão de vendas do pipeline."""

    period: str  # Ex: "2024-Q1", "2024-01"
    expected_value: float
    weighted_value: float
    opportunity_count: int
    avg_probability: float
