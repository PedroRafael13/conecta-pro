"""
Schemas Pydantic para Commission (Comissões de Vendedores).
"""

from datetime import date, datetime
from typing import Optional

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
    description: Optional[str] = None
    commission_type: CommissionType = CommissionType.PERCENTAGE
    base_value: float = Field(default=0.0, ge=0, description="Valor ou percentual base")
    min_value: Optional[float] = Field(None, ge=0, description="Comissão mínima")
    max_value: Optional[float] = Field(None, ge=0, description="Comissão máxima")
    trigger: CommissionTrigger = CommissionTrigger.ON_FIRST_PAYMENT
    trigger_delay_days: int = Field(default=0, ge=0, description="Dias após gatilho")


class CommissionRuleCreate(CommissionRuleBase):
    """Schema para criação de regra de comissão."""

    progressive_scale: Optional[list[ProgressiveTier]] = None
    applies_to_all: bool = True
    product_categories: Optional[list[str]] = None
    service_types: Optional[list[str]] = None
    min_sale_value: Optional[float] = Field(None, ge=0)
    max_sale_value: Optional[float] = Field(None, ge=0)
    valid_from: date = Field(default_factory=date.today)
    valid_until: Optional[date] = None
    priority: int = Field(default=0, ge=0)


class CommissionRuleUpdate(BaseModel):
    """Schema para atualização de regra de comissão."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    commission_type: Optional[CommissionType] = None
    base_value: Optional[float] = Field(None, ge=0)
    min_value: Optional[float] = Field(None, ge=0)
    max_value: Optional[float] = Field(None, ge=0)
    progressive_scale: Optional[list[ProgressiveTier]] = None
    trigger: Optional[CommissionTrigger] = None
    trigger_delay_days: Optional[int] = Field(None, ge=0)
    applies_to_all: Optional[bool] = None
    product_categories: Optional[list[str]] = None
    service_types: Optional[list[str]] = None
    min_sale_value: Optional[float] = Field(None, ge=0)
    max_sale_value: Optional[float] = Field(None, ge=0)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CommissionRuleResponse(CommissionRuleBase):
    """Schema de resposta para regra de comissão."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    progressive_scale: Optional[str]  # JSON string
    applies_to_all: bool
    product_categories: Optional[str]
    service_types: Optional[str]
    min_sale_value: Optional[float]
    max_sale_value: Optional[float]
    valid_from: date
    valid_until: Optional[date]
    priority: int
    is_valid: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[str]


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
    custom_base_value: Optional[float] = Field(None, ge=0)
    valid_from: date = Field(default_factory=date.today)
    valid_until: Optional[date] = None


class SellerCommissionRuleResponse(BaseModel):
    """Schema de resposta para associação vendedor-regra."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    rule_id: str
    custom_base_value: Optional[float]
    valid_from: date
    valid_until: Optional[date]
    is_active: bool
    created_at: datetime


# ============== Commission Schemas ==============


class CommissionBase(BaseModel):
    """Schema base para comissão."""

    seller_id: str
    proposal_id: Optional[str] = None
    sale_value: float = Field(..., gt=0)
    sale_margin: float = Field(default=0.0, ge=0)
    description: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class CommissionCreate(CommissionBase):
    """Schema para criação de comissão."""

    rule_id: Optional[str] = None
    commission_type: Optional[CommissionType] = None
    commission_rate: Optional[float] = Field(None, ge=0)
    trigger: Optional[CommissionTrigger] = None
    trigger_date: Optional[date] = None
    due_date: Optional[date] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class CommissionCalculateRequest(BaseModel):
    """Schema para solicitar cálculo de comissão."""

    seller_id: str
    proposal_id: str
    sale_value: float = Field(..., gt=0)
    sale_margin: float = Field(default=0.0, ge=0)
    rule_id: Optional[str] = None  # Se não informado, usa regra padrão


class CommissionUpdate(BaseModel):
    """Schema para atualização de comissão."""

    adjustments: Optional[float] = None
    description: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    due_date: Optional[date] = None


class CommissionStatusUpdate(BaseModel):
    """Schema para atualização de status."""

    status: CommissionStatus
    notes: Optional[str] = None


class CommissionApprove(BaseModel):
    """Schema para aprovar comissão."""

    notes: Optional[str] = None


class CommissionResponse(BaseModel):
    """Schema de resposta para comissão."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_number: str
    seller_id: Optional[str]
    proposal_id: Optional[str]
    rule_id: Optional[str]

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
    trigger_date: Optional[date]
    due_date: Optional[date]
    paid_date: Optional[date]

    # Período
    period_start: Optional[date]
    period_end: Optional[date]

    # Descrição
    description: Optional[str]
    notes: Optional[str]

    # Propriedades calculadas
    is_pending: bool
    is_approved: bool
    is_paid: bool
    paid_amount: float
    pending_amount: float
    is_overdue: bool
    days_until_due: Optional[int]

    # Controle
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[str]
    approved_by_id: Optional[str]
    approved_at: Optional[datetime]


class CommissionDetailResponse(CommissionResponse):
    """Schema de resposta detalhada com pagamentos."""

    payments: list["CommissionPaymentResponse"] = []
    rule: Optional[CommissionRuleResponse] = None


class CommissionListResponse(BaseModel):
    """Schema de resposta para lista de comissões."""

    items: list[CommissionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CommissionFilter(BaseModel):
    """Schema para filtros de busca de comissões."""

    seller_id: Optional[str] = None
    proposal_id: Optional[str] = None
    status: Optional[CommissionStatus] = None
    trigger: Optional[CommissionTrigger] = None
    is_overdue: Optional[bool] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None


# ============== CommissionPayment Schemas ==============


class CommissionPaymentCreate(BaseModel):
    """Schema para criação de pagamento."""

    commission_id: str
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.PAYROLL
    payment_date: date
    payment_reference: Optional[str] = Field(None, max_length=100)
    bank_account: Optional[str] = Field(None, max_length=50)
    transaction_id: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class CommissionPaymentConfirm(BaseModel):
    """Schema para confirmar pagamento."""

    notes: Optional[str] = None


class CommissionPaymentResponse(BaseModel):
    """Schema de resposta para pagamento."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    commission_id: str
    amount: float
    payment_method: PaymentMethod
    payment_date: date
    payment_reference: Optional[str]
    bank_account: Optional[str]
    transaction_id: Optional[str]
    is_confirmed: bool
    confirmed_at: Optional[datetime]
    confirmed_by_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    created_by_id: Optional[str]


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
    sales_target: Optional[float]
    target_percentage: Optional[float]
    bonus_earned: float
    is_target_achieved: bool
    remaining_to_target: float
    is_closed: bool
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CommissionSummaryFilter(BaseModel):
    """Schema para filtros de resumo."""

    seller_id: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    is_closed: Optional[bool] = None


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
    seller_name: Optional[str] = None
    total_sales: float
    total_commissions: float
    pending_commissions: float
    paid_commissions: float
    commission_rate_avg: float
    sales_count: int
    current_month_sales: float
    current_month_commissions: float
    target: Optional[float] = None
    target_percentage: Optional[float] = None


class CommissionRanking(BaseModel):
    """Ranking de vendedores por comissão."""

    sellers: list[SellerCommissionStats]
    period_start: date
    period_end: date
    total_commissions: float
    total_sales: float
