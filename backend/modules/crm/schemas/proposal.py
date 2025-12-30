"""
Schemas Pydantic para Proposal.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.crm.models.proposal import (
    ApprovalAction,
    DiscountType,
    ProposalStatus,
    ProposalType,
)


# ============== ProposalItem Schemas ==============


class ProposalItemBase(BaseModel):
    """Schema base para item de proposta."""

    code: Optional[str] = Field(None, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    unit: str = Field(default="un", max_length=20)
    quantity: float = Field(default=1.0, ge=0)
    unit_price: float = Field(default=0.0, ge=0)
    discount_percent: float = Field(default=0.0, ge=0, le=100)
    is_optional: bool = False


class ProposalItemCreate(ProposalItemBase):
    """Schema para criacao de item."""

    sort_order: int = 0


class ProposalItemUpdate(BaseModel):
    """Schema para atualizacao de item."""

    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=20)
    quantity: Optional[float] = Field(None, ge=0)
    unit_price: Optional[float] = Field(None, ge=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    is_optional: Optional[bool] = None
    sort_order: Optional[int] = None


class ProposalItemResponse(ProposalItemBase):
    """Schema de resposta para item."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    total: float
    subtotal: float
    discount_amount: float
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============== ProposalTemplate Schemas ==============


class ProposalTemplateBase(BaseModel):
    """Schema base para template."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    default_title: Optional[str] = Field(None, max_length=255)
    default_description: Optional[str] = None
    terms_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    validity_days: int = Field(default=30, ge=1, le=365)
    proposal_type: ProposalType = ProposalType.SERVICE


class ProposalTemplateCreate(ProposalTemplateBase):
    """Schema para criacao de template."""

    header_html: Optional[str] = None
    footer_html: Optional[str] = None
    css_styles: Optional[str] = None
    is_default: bool = False


class ProposalTemplateUpdate(BaseModel):
    """Schema para atualizacao de template."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    default_title: Optional[str] = Field(None, max_length=255)
    default_description: Optional[str] = None
    terms_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    validity_days: Optional[int] = Field(None, ge=1, le=365)
    proposal_type: Optional[ProposalType] = None
    header_html: Optional[str] = None
    footer_html: Optional[str] = None
    css_styles: Optional[str] = None
    is_default: Optional[bool] = None


class ProposalTemplateResponse(ProposalTemplateBase):
    """Schema de resposta para template."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    header_html: Optional[str]
    footer_html: Optional[str]
    css_styles: Optional[str]
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============== Proposal Schemas ==============


class ProposalBase(BaseModel):
    """Schema base para proposta."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    proposal_type: ProposalType = ProposalType.SERVICE

    # Cliente
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: EmailStr
    client_phone: Optional[str] = Field(None, max_length=20)
    client_company: Optional[str] = Field(None, max_length=255)
    client_document: Optional[str] = Field(None, max_length=20)
    client_address: Optional[str] = None

    # Condicoes
    terms_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    payment_conditions: Optional[str] = Field(None, max_length=255)
    installments: int = Field(default=1, ge=1, le=120)
    notes: Optional[str] = None

    # Datas
    valid_until: Optional[date] = None


class ProposalCreate(ProposalBase):
    """Schema para criacao de proposta."""

    opportunity_id: Optional[str] = None
    template_id: Optional[str] = None

    # Desconto global
    discount_type: Optional[DiscountType] = None
    discount_value: float = Field(default=0.0, ge=0)
    discount_reason: Optional[str] = Field(None, max_length=255)
    taxes: float = Field(default=0.0, ge=0)

    # Itens (opcional na criacao)
    items: list[ProposalItemCreate] = []


class ProposalCreateFromOpportunity(BaseModel):
    """Schema para criar proposta a partir de opportunity."""

    opportunity_id: str
    template_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    valid_until: Optional[date] = None
    items: list[ProposalItemCreate] = []


class ProposalUpdate(BaseModel):
    """Schema para atualizacao de proposta."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    proposal_type: Optional[ProposalType] = None

    # Cliente
    client_name: Optional[str] = Field(None, min_length=1, max_length=255)
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = Field(None, max_length=20)
    client_company: Optional[str] = Field(None, max_length=255)
    client_document: Optional[str] = Field(None, max_length=20)
    client_address: Optional[str] = None

    # Condicoes
    terms_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    payment_conditions: Optional[str] = Field(None, max_length=255)
    installments: Optional[int] = Field(None, ge=1, le=120)
    notes: Optional[str] = None

    # Datas
    valid_until: Optional[date] = None

    # Desconto
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, ge=0)
    discount_reason: Optional[str] = Field(None, max_length=255)
    taxes: Optional[float] = Field(None, ge=0)


class ProposalStatusUpdate(BaseModel):
    """Schema para atualizacao de status."""

    status: ProposalStatus
    notes: Optional[str] = None


class ProposalSend(BaseModel):
    """Schema para enviar proposta."""

    recipient_email: Optional[EmailStr] = None  # Se diferente do client_email
    subject: Optional[str] = None
    message: Optional[str] = None
    cc_emails: list[str] = []


class ProposalApprovalRequest(BaseModel):
    """Schema para solicitar aprovacao."""

    action: ApprovalAction
    comments: Optional[str] = None


class ProposalClientResponse(BaseModel):
    """Schema para resposta do cliente."""

    accepted: bool
    feedback: Optional[str] = None
    signature: Optional[str] = None  # Base64 da assinatura


class ProposalResponse(BaseModel):
    """Schema de resposta para proposta."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    version: int
    parent_id: Optional[str]

    # Relacionamentos
    opportunity_id: Optional[str]
    template_id: Optional[str]

    # Cliente
    client_name: str
    client_email: str
    client_phone: Optional[str]
    client_company: Optional[str]
    client_document: Optional[str]
    client_address: Optional[str]

    # Conteudo
    title: str
    description: Optional[str]
    proposal_type: ProposalType
    terms_conditions: Optional[str]
    notes: Optional[str]

    # Valores
    subtotal: float
    discount_type: Optional[DiscountType]
    discount_value: float
    discount_reason: Optional[str]
    discount_amount: float
    taxes: float
    total: float

    # Pagamento
    payment_terms: Optional[str]
    payment_conditions: Optional[str]
    installments: int

    # Datas
    issue_date: date
    valid_until: Optional[date]
    sent_at: Optional[datetime]
    viewed_at: Optional[datetime]
    responded_at: Optional[datetime]

    # Status
    status: ProposalStatus
    rejection_reason: Optional[str]

    # Responsaveis
    created_by_id: Optional[str]
    approved_by_id: Optional[str]
    approved_at: Optional[datetime]

    # Propriedades calculadas
    is_draft: bool
    is_pending: bool
    is_approved: bool
    is_sent: bool
    is_closed: bool
    is_accepted: bool
    is_expired: bool
    days_until_expiry: Optional[int]
    item_count: int

    # Controle
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProposalDetailResponse(ProposalResponse):
    """Schema de resposta detalhada com itens."""

    items: list[ProposalItemResponse] = []


class ProposalListResponse(BaseModel):
    """Schema de resposta para lista de propostas."""

    items: list[ProposalResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProposalFilter(BaseModel):
    """Schema para filtros de busca."""

    status: Optional[ProposalStatus] = None
    proposal_type: Optional[ProposalType] = None
    opportunity_id: Optional[str] = None
    created_by_id: Optional[str] = None
    is_expired: Optional[bool] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    client_name: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class ProposalStats(BaseModel):
    """Estatisticas de propostas."""

    total_proposals: int
    draft_count: int
    pending_count: int
    sent_count: int
    accepted_count: int
    rejected_count: int
    expired_count: int
    total_value: float
    accepted_value: float
    pending_value: float
    acceptance_rate: float  # Percentual
    avg_proposal_value: float
    avg_response_time_days: float
    by_status: dict[str, int]
    by_type: dict[str, int]


# ============== Approval Schemas ==============


class ProposalApprovalResponse(BaseModel):
    """Schema de resposta para aprovacao."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    user_id: Optional[str]
    action: ApprovalAction
    comments: Optional[str]
    created_at: datetime
