"""Schemas Pydantic para Fluxo de Caixa."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ===================== BANK ACCOUNT =====================


class BankAccountBase(BaseModel):
    """Schema base para conta bancaria."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    bank_code: str = Field(..., min_length=1, max_length=10)
    bank_name: str = Field(..., min_length=1, max_length=100)
    agency: str = Field(..., min_length=1, max_length=10)
    agency_digit: Optional[str] = Field(None, max_length=2)
    account_number: str = Field(..., min_length=1, max_length=20)
    account_digit: str = Field(..., min_length=1, max_length=2)
    account_type: str = Field(default="corrente")
    holder_name: Optional[str] = Field(None, max_length=150)
    holder_document: Optional[str] = Field(None, max_length=20)


class BankAccountCreate(BankAccountBase):
    """Schema para criacao de conta bancaria."""

    condominio_id: UUID
    opening_balance: Decimal = Field(default=Decimal("0"))
    opening_date: Optional[date] = None
    pix_enabled: bool = False
    pix_key: Optional[str] = None
    pix_key_type: Optional[str] = None
    boleto_enabled: bool = False
    boleto_wallet: Optional[str] = None
    boleto_agreement: Optional[str] = None
    is_main_account: bool = False


class BankAccountUpdate(BaseModel):
    """Schema para atualizacao de conta bancaria."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    holder_name: Optional[str] = Field(None, max_length=150)
    holder_document: Optional[str] = Field(None, max_length=20)
    pix_enabled: Optional[bool] = None
    pix_key: Optional[str] = None
    pix_key_type: Optional[str] = None
    boleto_enabled: Optional[bool] = None
    boleto_wallet: Optional[str] = None
    boleto_agreement: Optional[str] = None
    is_main_account: Optional[bool] = None
    allow_negative_balance: Optional[bool] = None
    overdraft_limit: Optional[Decimal] = None
    minimum_balance: Optional[Decimal] = None
    bank_manager_name: Optional[str] = None
    bank_manager_phone: Optional[str] = None
    bank_manager_email: Optional[str] = None
    notes: Optional[str] = None


class BankAccountResponse(BankAccountBase):
    """Schema de resposta para conta bancaria."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: str
    opening_balance: Decimal
    current_balance: Decimal
    available_balance: Decimal
    blocked_balance: Decimal
    pix_enabled: bool
    pix_key: Optional[str]
    boleto_enabled: bool
    is_main_account: bool
    opening_date: Optional[date]
    last_balance_update: Optional[datetime]
    created_at: datetime
    ativo: bool


class BankAccountFilter(BaseModel):
    """Filtros para busca de contas bancarias."""

    status: Optional[str] = None
    account_type: Optional[str] = None
    bank_code: Optional[str] = None
    is_main_account: Optional[bool] = None
    pix_enabled: Optional[bool] = None
    boleto_enabled: Optional[bool] = None


class BankAccountStats(BaseModel):
    """Estatisticas de contas bancarias."""

    total_accounts: int = 0
    active_accounts: int = 0
    total_balance: Decimal = Decimal("0")
    total_available: Decimal = Decimal("0")
    total_blocked: Decimal = Decimal("0")
    accounts_with_pix: int = 0
    accounts_with_boleto: int = 0


# ===================== BANK TRANSACTION =====================


class BankTransactionBase(BaseModel):
    """Schema base para movimentacao bancaria."""

    transaction_type: str
    category: str = "nao_identificado"
    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    memo: Optional[str] = None
    transaction_date: date
    competence_date: Optional[date] = None


class BankTransactionCreate(BankTransactionBase):
    """Schema para criacao de movimentacao."""

    bank_account_id: UUID
    document_number: Optional[str] = None
    reference: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_document: Optional[str] = None
    pix_key: Optional[str] = None
    barcode: Optional[str] = None


class BankTransactionUpdate(BaseModel):
    """Schema para atualizacao de movimentacao."""

    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    memo: Optional[str] = None
    competence_date: Optional[date] = None
    counterparty_name: Optional[str] = None
    counterparty_document: Optional[str] = None


class BankTransactionResponse(BankTransactionBase):
    """Schema de resposta para movimentacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bank_account_id: UUID
    status: str
    balance_before: Optional[Decimal]
    balance_after: Optional[Decimal]
    origin: str
    source_type: Optional[str]
    reconciliation_status: str
    external_id: Optional[str]
    document_number: Optional[str]
    counterparty_name: Optional[str]
    is_transfer: bool
    is_reversal: bool
    created_at: datetime


class BankTransactionFilter(BaseModel):
    """Filtros para busca de movimentacoes."""

    transaction_type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    reconciliation_status: Optional[str] = None
    origin: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    counterparty_name: Optional[str] = None


class BankTransactionImport(BaseModel):
    """Schema para importacao de extrato."""

    bank_account_id: UUID
    file_format: str = Field(..., pattern="^(ofx|cnab|csv)$")
    transactions: List[Dict[str, Any]]


class TransferRequest(BaseModel):
    """Schema para transferencia entre contas."""

    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    transaction_date: date
    competence_date: Optional[date] = None


# ===================== BANK RECONCILIATION =====================


class BankReconciliationBase(BaseModel):
    """Schema base para conciliacao."""

    reference: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    period_type: str = "mensal"
    period_start: date
    period_end: date


class BankReconciliationCreate(BankReconciliationBase):
    """Schema para criacao de conciliacao."""

    bank_account_id: UUID
    condominio_id: UUID
    system_opening_balance: Decimal


class BankReconciliationUpdate(BaseModel):
    """Schema para atualizacao de conciliacao."""

    bank_opening_balance: Optional[Decimal] = None
    bank_closing_balance: Optional[Decimal] = None
    notes: Optional[str] = None


class BankReconciliationResponse(BankReconciliationBase):
    """Schema de resposta para conciliacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bank_account_id: UUID
    condominio_id: UUID
    status: str
    system_opening_balance: Decimal
    system_closing_balance: Optional[Decimal]
    bank_opening_balance: Optional[Decimal]
    bank_closing_balance: Optional[Decimal]
    closing_difference: Decimal
    reconciliation_progress: Decimal
    reconciled_count: int
    pending_system_count: int
    pending_bank_count: int
    divergent_count: int
    statement_imported: bool
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class BankReconciliationFilter(BaseModel):
    """Schema para filtros de listagem de conciliacoes."""

    bank_account_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    status: Optional[str] = None
    period_type: Optional[str] = None
    period_start_from: Optional[date] = None
    period_start_to: Optional[date] = None


class ReconciliationItemMatch(BaseModel):
    """Schema para conciliar item."""

    system_transaction_id: UUID
    bank_transaction_id: Optional[UUID] = None
    note: Optional[str] = None


class ReconciliationAdjustment(BaseModel):
    """Schema para ajuste de conciliacao."""

    adjustment_type: str = Field(..., pattern="^(credito|debito)$")
    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)


class StatementImport(BaseModel):
    """Schema para importacao de extrato."""

    reconciliation_id: UUID
    file_name: str
    file_format: str = Field(..., pattern="^(ofx|cnab|csv|pdf)$")
    transactions: List[Dict[str, Any]]


# ===================== CASHFLOW ENTRY =====================


class CashFlowEntryBase(BaseModel):
    """Schema base para lancamento de fluxo de caixa."""

    entry_type: str
    description: str = Field(..., min_length=1, max_length=500)
    memo: Optional[str] = None
    expected_amount: Decimal = Field(..., gt=0)
    entry_date: date
    competence_date: Optional[date] = None
    due_date: Optional[date] = None


class CashFlowEntryCreate(CashFlowEntryBase):
    """Schema para criacao de lancamento."""

    condominio_id: UUID
    bank_account_id: Optional[UUID] = None
    payable_category_id: Optional[UUID] = None
    receivable_category_id: Optional[UUID] = None
    counterparty_name: Optional[str] = None
    is_recurring: bool = False
    recurrence_frequency: Optional[str] = None
    recurrence_start: Optional[date] = None
    recurrence_end: Optional[date] = None
    recurrence_count: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class CashFlowEntryUpdate(BaseModel):
    """Schema para atualizacao de lancamento."""

    description: Optional[str] = Field(None, max_length=500)
    memo: Optional[str] = None
    expected_amount: Optional[Decimal] = Field(None, gt=0)
    entry_date: Optional[date] = None
    due_date: Optional[date] = None
    bank_account_id: Optional[UUID] = None
    counterparty_name: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CashFlowEntryResponse(CashFlowEntryBase):
    """Schema de resposta para lancamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    bank_account_id: Optional[UUID]
    source_type: str
    status: str
    realized_amount: Optional[Decimal]
    realized_date: Optional[date]
    difference: Optional[Decimal]
    is_recurring: bool
    counterparty_name: Optional[str]
    tags: List[str]
    is_approved: bool
    created_at: datetime


class CashFlowEntryFilter(BaseModel):
    """Filtros para busca de lancamentos."""

    entry_type: Optional[str] = None
    source_type: Optional[str] = None
    status: Optional[str] = None
    bank_account_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    is_recurring: Optional[bool] = None
    is_overdue: Optional[bool] = None


class CashFlowEntryRealize(BaseModel):
    """Schema para realizar lancamento."""

    realized_amount: Decimal = Field(..., gt=0)
    realized_date: date
    bank_transaction_id: Optional[UUID] = None


# ===================== CASHFLOW FORECAST =====================


class CashFlowForecastBase(BaseModel):
    """Schema base para previsao."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    reference: Optional[str] = Field(None, max_length=50)
    period_type: str = "mensal"
    period_start: date
    period_end: date
    forecast_date: date


class CashFlowForecastCreate(CashFlowForecastBase):
    """Schema para criacao de previsao."""

    condominio_id: UUID
    expected_opening_balance: Decimal = Decimal("0")
    expected_receivables: Decimal = Decimal("0")
    expected_other_income: Decimal = Decimal("0")
    expected_payables: Decimal = Decimal("0")
    expected_other_expenses: Decimal = Decimal("0")
    assumptions: List[str] = Field(default_factory=list)
    target_balance: Optional[Decimal] = None


class CashFlowForecastUpdate(BaseModel):
    """Schema para atualizacao de previsao."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    expected_receivables: Optional[Decimal] = None
    expected_other_income: Optional[Decimal] = None
    expected_payables: Optional[Decimal] = None
    expected_other_expenses: Optional[Decimal] = None
    assumptions: Optional[List[str]] = None
    target_balance: Optional[Decimal] = None
    notes: Optional[str] = None


class CashFlowForecastResponse(CashFlowForecastBase):
    """Schema de resposta para previsao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    status: str
    expected_inflows: Decimal
    expected_outflows: Decimal
    expected_opening_balance: Decimal
    expected_closing_balance: Decimal
    expected_net_flow: Decimal
    actual_inflows: Optional[Decimal]
    actual_outflows: Optional[Decimal]
    actual_closing_balance: Optional[Decimal]
    balance_variance: Optional[Decimal]
    confidence_level: int
    confidence_category: str
    ai_generated: bool
    has_negative_balance_alert: bool
    risks: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    created_at: datetime


class CashFlowForecastFilter(BaseModel):
    """Filtros para busca de previsoes."""

    status: Optional[str] = None
    period_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    ai_generated: Optional[bool] = None
    has_alerts: Optional[bool] = None


class ForecastActualsUpdate(BaseModel):
    """Schema para atualizar valores realizados."""

    actual_inflows: Decimal
    actual_outflows: Decimal
    actual_opening_balance: Decimal
    actual_closing_balance: Decimal


class ForecastRisk(BaseModel):
    """Schema para adicionar risco."""

    risk_type: str = Field(..., max_length=50)
    probability: float = Field(..., ge=0, le=1)
    impact: Decimal = Field(..., gt=0)
    mitigation: str = Field(..., max_length=500)


class ForecastOpportunity(BaseModel):
    """Schema para adicionar oportunidade."""

    opportunity_type: str = Field(..., max_length=50)
    probability: float = Field(..., ge=0, le=1)
    value: Decimal = Field(..., gt=0)
    action: str = Field(..., max_length=500)


# ===================== PROJECTIONS & ANALYTICS =====================


class CashFlowProjection(BaseModel):
    """Projecao de fluxo de caixa."""

    date: date
    payables: Decimal = Decimal("0")
    receivables: Decimal = Decimal("0")
    balance: Decimal = Decimal("0")
    cumulative_balance: Decimal = Decimal("0")
    details: List[Dict[str, Any]] = Field(default_factory=list)


class CashFlowSummary(BaseModel):
    """Resumo de fluxo de caixa."""

    period_start: date
    period_end: date
    opening_balance: Decimal
    closing_balance: Decimal
    total_inflows: Decimal
    total_outflows: Decimal
    net_flow: Decimal
    inflows_by_category: Dict[str, Decimal]
    outflows_by_category: Dict[str, Decimal]
    pending_receivables: Decimal
    pending_payables: Decimal
    overdue_receivables: Decimal
    overdue_payables: Decimal


class CashFlowTrend(BaseModel):
    """Tendencia de fluxo de caixa."""

    period: str
    inflows: Decimal
    outflows: Decimal
    net_flow: Decimal
    balance: Decimal
    variance_pct: Optional[float] = None


class CashFlowDashboard(BaseModel):
    """Dashboard de fluxo de caixa."""

    summary: CashFlowSummary
    trends: List[CashFlowTrend]
    projections: List[CashFlowProjection]
    accounts: List[BankAccountResponse]
    alerts: List[Dict[str, Any]]
    upcoming_payables: int
    upcoming_receivables: int
    overdue_payables: int
    overdue_receivables: int


# ===================== AI ANALYSIS =====================


class AIForecastRequest(BaseModel):
    """Request para previsao por IA."""

    condominio_id: UUID
    months_ahead: int = Field(default=3, ge=1, le=12)
    include_scenarios: bool = True
    confidence_threshold: int = Field(default=70, ge=0, le=100)


class AIForecastResponse(BaseModel):
    """Resposta de previsao por IA."""

    forecast: CashFlowForecastResponse
    scenarios: Dict[str, Dict[str, Decimal]]
    confidence_factors: Dict[str, float]
    recommendations: List[str]
    risks: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]


class AnomalyDetectionRequest(BaseModel):
    """Request para deteccao de anomalias."""

    condominio_id: UUID
    period_months: int = Field(default=6, ge=3, le=12)
    sensitivity: str = Field(default="medium", pattern="^(low|medium|high)$")


class AnomalyDetectionResponse(BaseModel):
    """Resposta de deteccao de anomalias."""

    anomalies: List[Dict[str, Any]]
    total: int
    by_severity: Dict[str, int]
    by_category: Dict[str, int]


class OptimizationSuggestion(BaseModel):
    """Sugestao de otimizacao."""

    id: str
    type: str
    title: str
    description: str
    potential_savings: Decimal
    implementation_effort: str
    priority: str
    action_items: List[str]
