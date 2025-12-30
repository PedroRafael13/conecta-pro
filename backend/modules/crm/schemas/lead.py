"""
Schemas Pydantic para Lead.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from modules.crm.models.lead import LeadSource, LeadStatus


class LeadBase(BaseModel):
    """Schema base para Lead."""

    name: str = Field(..., min_length=2, max_length=255, description="Nome do contato")
    email: EmailStr = Field(..., description="Email do contato")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    company: Optional[str] = Field(None, max_length=255, description="Empresa")
    position: Optional[str] = Field(None, max_length=100, description="Cargo")
    company_size: Optional[str] = Field(None, max_length=50, description="Porte da empresa")
    industry: Optional[str] = Field(None, max_length=100, description="Setor/Indústria")
    source: LeadSource = Field(default=LeadSource.OTHER, description="Origem do lead")
    notes: Optional[str] = Field(None, description="Observações")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Valida formato do telefone."""
        if v is None:
            return v
        # Remove caracteres não numéricos para validação
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Telefone deve ter entre 10 e 15 dígitos")
        return v


class LeadCreate(LeadBase):
    """Schema para criação de Lead."""

    assigned_to_id: Optional[str] = Field(None, description="ID do usuário responsável")
    expected_value: float = Field(default=0.0, ge=0, description="Valor esperado")


class LeadUpdate(BaseModel):
    """Schema para atualização parcial de Lead."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[str] = None
    expected_value: Optional[float] = Field(None, ge=0)
    next_contact_at: Optional[datetime] = None


class LeadResponse(BaseModel):
    """Schema de resposta para Lead."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    position: Optional[str]
    company_size: Optional[str]
    industry: Optional[str]
    source: str
    status: str
    score: int
    probability: float
    expected_value: float
    notes: Optional[str]
    assigned_to_id: Optional[str]
    last_contact_at: Optional[datetime]
    next_contact_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_hot: bool
    is_qualified: bool
    weighted_value: float


class LeadListResponse(BaseModel):
    """Schema para listagem paginada de Leads."""

    items: List[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LeadFilter(BaseModel):
    """Schema para filtros de busca de Leads."""

    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    assigned_to_id: Optional[str] = None
    min_score: Optional[int] = Field(None, ge=0, le=100)
    max_score: Optional[int] = Field(None, ge=0, le=100)
    is_hot: Optional[bool] = None
    company: Optional[str] = None
    search: Optional[str] = Field(None, description="Busca por nome, email ou empresa")


class LeadScoreUpdate(BaseModel):
    """Schema para atualização de score."""

    score: int = Field(..., ge=0, le=100, description="Score de qualificação")
    probability: float = Field(..., ge=0, le=100, description="Probabilidade de fechamento")


class LeadStatusUpdate(BaseModel):
    """Schema para atualização de status."""

    status: LeadStatus
    notes: Optional[str] = Field(None, description="Observações sobre a mudança")


class LeadStats(BaseModel):
    """Estatísticas de leads."""

    total: int
    by_status: dict[str, int]
    by_source: dict[str, int]
    hot_leads: int
    avg_score: float
    total_expected_value: float
    total_weighted_value: float
