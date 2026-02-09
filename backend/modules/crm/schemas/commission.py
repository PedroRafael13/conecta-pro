"""
Schemas Pydantic para Commission (Comissões de Vendedores).
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.crm.models.commission import (
    CommissionStatus,
    CommissionTrigger,
    CommissionType,
    PaymentMethod,
)

# ============== CommissionRule Schemas ==============


class ProgressiveTier(BaseModel):
    """Faixa de escala progressiva."""

    min: float = Field(ge=0, description="Valor mínimo da faixa")
    max: float = Field(ge=0, description="Valor máximo da faixa")
    rate: float = Field(ge=0, le=100, description="Percentual de comissão")


class CommissionRuleBase(BaseModel):
    """Schema base para regra de comissão."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    commission_type: CommissionType = CommissionType.PERCENTAGE
    base_value: float = Field(default=0.0, ge=0, description="Valor ou percentual base")
    min_value: float | None = Field(None, ge=0, description="Comissão mínima")
    max_value: float | None = Field(None, ge=0, description="Comissão máxima")
    trigger: CommissionTrigger = CommissionTrigger.ON_FIRST_PAYMENT
    trigger_delay_days: int = Field(default=0, ge=0, description="Dias após gatilho")


class CommissionRuleCreate(CommissionRuleBase):
    """Schema para criação de regra de comissão."""

    progressive_scale: list[ProgressiveTier] | None = None
    applies_to_all: bool = True
    product_categories: list[str] | None = None
    service_types: list[str] | None = None
    min_sale_value: float | None = Field(None, ge=0)
    max_sale_value: float | None = Field(None, ge=0)
    valid_from: date = Field(default_factory=date.today)
    valid_until: date | None = None
    priority: int = Field(default=0, ge=0)


class CommissionRuleUpdate(BaseModel):
    """Schema para atualização de regra de comissão."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    commission_type: CommissionType | None = None
    base_value: float | None = Field(None, ge=0)
    min_value: float | None = Field(None, ge=0)
    max_value: float | None = Field(None, ge=0)
    progressive_scale: list[ProgressiveTier] | None = None
    trigger: CommissionTrigger | None = None
    trigger_delay_days: int | None = Field(None, ge=0)
    applies_to_all: bool | None = None
    product_categories: list[str] | None = None
    service_types: list[str] | None = None
    min_sale_value: float | None = Field(None, ge=0)
    max_sale_value: float | None = Field(None, ge=0)
    valid_from: date | None = None
    valid_until: date | None = None
    priority: int | None = Field(None, ge=0)
    is_active: bool | None = None


class CommissionRuleResponse(CommissionRuleBase):
    """Schema de resposta para regra de comissão."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    progressive_scale: str | None  # JSON string
    applies_to_all: bool
    product_categories: str | None
    service_types: str | None
    min_sale_value: float | None
    max_sale_value: float | None
    valid_from: date
    valid_until: date | None
    priority: int
    is_valid: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: str | None


class CommissionRuleListResponse(BaseModel):
    """Schema de resposta para lista de regras."""

    items: list[CommissionRuleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== SellerCommissionRule Schemas ==============


class SellerCommissionRuleCreate(BaseModel):
    """Schema para associar regra a vendedor."""

    seller_id: str
    rule_id: str
    custom_base_value: float | None = Field(None, ge=0)
    valid_from: date = Field(default_factory=date.today)
    valid_until: date | None = None


class SellerCommissionRuleResponse(BaseModel):
    """Schema de resposta para associação vendedor-regra."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    rule_id: str
    custom_base_value: float | None
    valid_from: date
    valid_until: date | None
    is_active: bool
    created_at: datetime


# ============== Commission Schemas ==============


class CommissionBase(BaseModel):
    """Schema base para comissão."""

    seller_id: str
    proposal_id: str | None = None
    sale_value: float = Field(..., gt=0)
    sale_margin: float = Field(default=0.0, ge=0)
    description: str | None = Field(None, max_length=255)
    notes: str | None = None


class CommissionCreate(CommissionBase):
    """Schema para criação de comissão."""

    rule_id: str | None = None
    commission_type: CommissionType | None = None
    commission_rate: float | None = Field(None, ge=0)
    trigger: CommissionTrigger | None = None
    trigger_date: date | None = None
    due_date: date | None = None
    period_start: date | None = None
    period_end: date | None = None


class CommissionCalculateRequest(BaseModel):
    """Schema para solicitar cálculo de comissão."""

    seller_id: str
    proposal_id: str
    sale_value: float = Field(..., gt=0)
    sale_margin: float = Field(default=0.0, ge=0)
    rule_id: str | None = None  # Se não informado, usa regra padrão


class CommissionUpdate(BaseModel):
    """Schema para atualização de comissão."""

    adjustments: float | None = None
    description: str | None = Field(None, max_length=255)
    notes: str | None = None
    due_date: date | None = None


class CommissionStatusUpdate(BaseModel):
    """Schema para atualização de status."""

    status: CommissionStatus
    notes: str | None = None


class CommissionApprove(BaseModel):
    """Schema para aprovar comissão."""

    notes: str | None = None


class CommissionResponse(BaseModel):
    """Schema de resposta para comissão."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_number: str
    seller_id: str | None
    proposal_id: str | None
    rule_id: str | None

    # Valores da venda
    sale_value: float
    sale_margin: float

    # Cálculo
    commission_type: str
    commission_rate: float
    base_commission: float
    adjustments: float
    final_commission: float

    # Status
    status: CommissionStatus
    trigger: str
    trigger_date: date | None
    due_date: date | None
    paid_date: date | None

    # Período
    period_start: date | None
    period_end: date | None

    # Descrição
    description: str | None
    notes: str | None

    # Propriedades calculadas
    is_pending: bool
    is_approved: bool
    is_paid: bool
    paid_amount: float
    pending_amount: float
    is_overdue: bool
    days_until_due: int | None

    # Controle
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: str | None
    approved_by_id: str | None
    approved_at: datetime | None


class CommissionDetailResponse(CommissionResponse):
    """Schema de resposta detalhada com pagamentos."""

    payments: list[CommissionPaymentResponse] = []
    rule: CommissionRuleResponse | None = None


class CommissionListResponse(BaseModel):
    """Schema de resposta para lista de comissões."""

    items: list[CommissionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CommissionFilter(BaseModel):
    """Schema para filtros de busca de comissões."""

    seller_id: str | None = None
    proposal_id: str | None = None
    status: CommissionStatus | None = None
    trigger: CommissionTrigger | None = None
    is_overdue: bool | None = None
    min_value: float | None = None
    max_value: float | None = None
    date_from: date | None = None
    date_to: date | None = None
    due_date_from: date | None = None
    due_date_to: date | None = None


# ============== CommissionPayment Schemas ==============


class CommissionPaymentCreate(BaseModel):
    """Schema para criação de pagamento."""

    commission_id: str
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.PAYROLL
    payment_date: date
    payment_reference: str | None = Field(None, max_length=100)
    bank_account: str | None = Field(None, max_length=50)
    transaction_id: str | None = Field(None, max_length=100)
    notes: str | None = None


class CommissionPaymentConfirm(BaseModel):
    """Schema para confirmar pagamento."""

    notes: str | None = None


class CommissionPaymentResponse(BaseModel):
    """Schema de resposta para pagamento."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    commission_id: str
    amount: float
    payment_method: PaymentMethod
    payment_date: date
    payment_reference: str | None
    bank_account: str | None
    transaction_id: str | None
    is_confirmed: bool
    confirmed_at: datetime | None
    confirmed_by_id: str | None
    notes: str | None
    created_at: datetime
    created_by_id: str | None


# ============== CommissionSummary Schemas ==============


class CommissionSummaryResponse(BaseModel):
    """Schema de resposta para resumo mensal."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    year: int
    month: int
    total_sales: float
    total_sales_count: int
    total_commissions: float
    total_paid: float
    total_pending: float
    sales_target: float | None
    target_percentage: float | None
    bonus_earned: float
    is_target_achieved: bool
    remaining_to_target: float
    is_closed: bool
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class CommissionSummaryFilter(BaseModel):
    """Schema para filtros de resumo."""

    seller_id: str | None = None
    year: int | None = None
    month: int | None = None
    is_closed: bool | None = None


# ============== Statistics Schemas ==============


class CommissionStats(BaseModel):
    """Estatísticas gerais de comissões."""

    total_commissions: int
    pending_count: int
    approved_count: int
    paid_count: int
    cancelled_count: int

    total_value: float
    pending_value: float
    approved_value: float
    paid_value: float

    overdue_count: int
    overdue_value: float

    avg_commission_value: float
    avg_days_to_payment: float

    by_status: dict[str, int]
    by_trigger: dict[str, int]
    by_month: dict[str, float]


class SellerCommissionStats(BaseModel):
    """Estatísticas de comissões por vendedor."""

    seller_id: str
    seller_name: str | None = None
    total_sales: float
    total_commissions: float
    pending_commissions: float
    paid_commissions: float
    commission_rate_avg: float
    sales_count: int
    current_month_sales: float
    current_month_commissions: float
    target: float | None = None
    target_percentage: float | None = None


class CommissionRanking(BaseModel):
    """Ranking de vendedores por comissão."""

    sellers: list[SellerCommissionStats]
    period_start: date
    period_end: date
    total_commissions: float
    total_sales: float


# Resolve forward references para Pydantic v2
CommissionDetailResponse.model_rebuild()
