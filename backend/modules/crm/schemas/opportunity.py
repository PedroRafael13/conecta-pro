"""
Schemas Pydantic para Opportunity.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.crm.models.opportunity import (
    LossReason,
    OpportunityPriority,
    OpportunityStage,
)


class OpportunityBase(BaseModel):
    """Schema base para Opportunity."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    value: float = Field(default=0.0, ge=0)
    probability: int = Field(default=10, ge=0, le=100)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    """Schema para criação de Opportunity."""

    lead_id: Optional[str] = None
    stage: OpportunityStage = OpportunityStage.QUALIFICATION
    priority: OpportunityPriority = OpportunityPriority.MEDIUM
    owner_id: Optional[str] = None


class OpportunityCreateFromLead(BaseModel):
    """Schema para criar Opportunity a partir de um Lead."""

    lead_id: str
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    value: float = Field(default=0.0, ge=0)
    probability: int = Field(default=20, ge=0, le=100)
    expected_close_date: Optional[date] = None
    priority: OpportunityPriority = OpportunityPriority.MEDIUM
    owner_id: Optional[str] = None
    notes: Optional[str] = None


class OpportunityUpdate(BaseModel):
    """Schema para atualização de Opportunity."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)
    stage: Optional[OpportunityStage] = None
    priority: Optional[OpportunityPriority] = None
    value: Optional[float] = Field(None, ge=0)
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    owner_id: Optional[str] = None
    notes: Optional[str] = None


class OpportunityStageUpdate(BaseModel):
    """Schema para atualização de estágio."""

    stage: OpportunityStage
    notes: Optional[str] = None


class OpportunityClose(BaseModel):
    """Schema para fechar oportunidade (ganhou ou perdeu)."""

    won: bool
    actual_close_date: Optional[date] = None
    notes: Optional[str] = None
    # Campos para perda
    loss_reason: Optional[LossReason] = None
    competitor: Optional[str] = Field(None, max_length=255)


class OpportunityResponse(BaseModel):
    """Schema de resposta para Opportunity."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: Optional[str]
    lead_id: Optional[str]
    contact_name: str
    contact_email: str
    contact_phone: Optional[str]
    company_name: Optional[str]
    stage: OpportunityStage
    priority: OpportunityPriority
    value: float
    probability: int
    weighted_value: float
    expected_close_date: Optional[date]
    actual_close_date: Optional[date]
    owner_id: Optional[str]
    loss_reason: Optional[LossReason]
    competitor: Optional[str]
    win_notes: Optional[str]
    loss_notes: Optional[str]
    notes: Optional[str]
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

    stage: Optional[OpportunityStage] = None
    priority: Optional[OpportunityPriority] = None
    owner_id: Optional[str] = None
    is_open: Optional[bool] = None
    is_overdue: Optional[bool] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    company_name: Optional[str] = None
    search: Optional[str] = None


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
