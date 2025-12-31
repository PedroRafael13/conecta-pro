"""Schemas Pydantic para o módulo de Contabilidade."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.financial.models import (
    AccountClassification,
    AccountNature,
    AccountStatus,
    AccountType,
    AllocationMethod,
    BalancePeriod,
    BalanceStatus,
    BalanceType,
    ChartStandard,
    ChartStatus,
    ChartType,
    ClosingType,
    CostCenterStatus,
    CostCenterType,
    EntryOrigin,
    EntryStatus,
    EntryType,
    PeriodStatus,
    PeriodType,
    SpedAccountNature,
)

# ============================================================================
# Chart of Accounts Schemas
# ============================================================================


class ChartOfAccountsBase(BaseModel):
    """Schema base para ChartOfAccounts."""

    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    chart_type: ChartType = ChartType.STANDARD
    standard: ChartStandard = ChartStandard.CUSTOM
    version: Optional[str] = Field(None, max_length=20)
    max_levels: int = Field(default=5, ge=1, le=10)
    account_mask: Optional[str] = Field(None, max_length=50)
    separator: Optional[str] = Field(".", max_length=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    sped_layout_code: Optional[str] = Field(None, max_length=10)
    sped_version: Optional[str] = Field(None, max_length=20)
    is_default: bool = False
    allow_modifications: bool = True
    notes: Optional[str] = None


class ChartOfAccountsCreate(ChartOfAccountsBase):
    """Schema para criar ChartOfAccounts."""


class ChartOfAccountsUpdate(BaseModel):
    """Schema para atualizar ChartOfAccounts."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    status: Optional[ChartStatus] = None
    version: Optional[str] = Field(None, max_length=20)
    valid_until: Optional[datetime] = None
    is_default: Optional[bool] = None
    allow_modifications: Optional[bool] = None
    notes: Optional[str] = None


class ChartOfAccountsResponse(ChartOfAccountsBase):
    """Schema de resposta para ChartOfAccounts."""

    id: UUID
    condominio_id: UUID
    status: ChartStatus
    version_date: Optional[datetime] = None
    total_accounts: int = 0
    total_analytical: int = 0
    total_synthetic: int = 0
    active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class ChartOfAccountsListResponse(BaseModel):
    """Schema de lista de ChartOfAccounts."""

    items: list[ChartOfAccountsResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ============================================================================
# Accounting Account Schemas
# ============================================================================


class AccountingAccountBase(BaseModel):
    """Schema base para AccountingAccount."""

    chart_id: UUID
    parent_id: Optional[UUID] = None
    code: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=150)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    account_type: AccountType
    nature: AccountNature
    classification: AccountClassification
    level: int = Field(default=1, ge=1, le=10)
    order_index: Optional[int] = None
    sped_nature: Optional[SpedAccountNature] = None
    sped_referential_code: Optional[str] = Field(None, max_length=30)
    default_cost_center_id: Optional[UUID] = None
    requires_cost_center: bool = False
    requires_project: bool = False
    requires_history: bool = True
    allows_manual_entry: bool = True
    dre_group: Optional[str] = Field(None, max_length=50)
    dre_order: Optional[int] = None
    balance_sheet_group: Optional[str] = Field(None, max_length=50)
    balance_sheet_order: Optional[int] = None
    is_tax_related: bool = False
    is_bank_account: bool = False
    bank_account_id: Optional[UUID] = None
    notes: Optional[str] = None


class AccountingAccountCreate(AccountingAccountBase):
    """Schema para criar AccountingAccount."""

    opening_balance: Decimal = Field(default=Decimal("0"))


class AccountingAccountUpdate(BaseModel):
    """Schema para atualizar AccountingAccount."""

    name: Optional[str] = Field(None, max_length=150)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[AccountStatus] = None
    sped_nature: Optional[SpedAccountNature] = None
    sped_referential_code: Optional[str] = Field(None, max_length=30)
    default_cost_center_id: Optional[UUID] = None
    requires_cost_center: Optional[bool] = None
    requires_project: Optional[bool] = None
    allows_manual_entry: Optional[bool] = None
    dre_group: Optional[str] = Field(None, max_length=50)
    dre_order: Optional[int] = None
    notes: Optional[str] = None


class AccountingAccountResponse(AccountingAccountBase):
    """Schema de resposta para AccountingAccount."""

    id: UUID
    condominio_id: UUID
    status: AccountStatus
    path: Optional[str] = None
    opening_balance: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")
    debit_total: Decimal = Decimal("0")
    credit_total: Decimal = Decimal("0")
    period_debit: Decimal = Decimal("0")
    period_credit: Decimal = Decimal("0")
    period_balance: Decimal = Decimal("0")
    last_movement_date: Optional[datetime] = None
    is_system: bool = False
    active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class AccountingAccountListResponse(BaseModel):
    """Schema de lista de AccountingAccount."""

    items: list[AccountingAccountResponse]
    total: int
    page: int
    per_page: int
    pages: int


class AccountTreeResponse(BaseModel):
    """Schema para árvore de contas."""

    id: UUID
    code: str
    name: str
    account_type: AccountType
    nature: AccountNature
    classification: AccountClassification
    level: int
    current_balance: Decimal = Decimal("0")
    children: list["AccountTreeResponse"] = []

    class Config:
        """Configuração do schema."""

        from_attributes = True


# ============================================================================
# Cost Center Schemas
# ============================================================================


class CostCenterBase(BaseModel):
    """Schema base para CostCenter."""

    parent_id: Optional[UUID] = None
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    short_name: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = None
    cost_center_type: CostCenterType = CostCenterType.ADMINISTRATIVE
    level: int = Field(default=1, ge=1, le=10)
    manager_id: Optional[UUID] = None
    manager_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    budget_annual: Decimal = Field(default=Decimal("0"))
    budget_monthly: Decimal = Field(default=Decimal("0"))
    allocation_method: AllocationMethod = AllocationMethod.DIRECT
    allocation_percentage: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    headcount: int = Field(default=0, ge=0)
    area_m2: Decimal = Field(default=Decimal("0"), ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_default: bool = False
    requires_approval: bool = False
    approval_limit: Optional[Decimal] = None
    allows_over_budget: bool = False
    notes: Optional[str] = None


class CostCenterCreate(CostCenterBase):
    """Schema para criar CostCenter."""


class CostCenterUpdate(BaseModel):
    """Schema para atualizar CostCenter."""

    name: Optional[str] = Field(None, max_length=100)
    short_name: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = None
    status: Optional[CostCenterStatus] = None
    manager_id: Optional[UUID] = None
    manager_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    budget_annual: Optional[Decimal] = None
    budget_monthly: Optional[Decimal] = None
    allocation_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    headcount: Optional[int] = Field(None, ge=0)
    area_m2: Optional[Decimal] = Field(None, ge=0)
    valid_until: Optional[datetime] = None
    requires_approval: Optional[bool] = None
    approval_limit: Optional[Decimal] = None
    notes: Optional[str] = None


class CostCenterResponse(CostCenterBase):
    """Schema de resposta para CostCenter."""

    id: UUID
    condominio_id: UUID
    status: CostCenterStatus
    path: Optional[str] = None
    order_index: Optional[int] = None
    budget_used: Decimal = Decimal("0")
    budget_available: Decimal = Decimal("0")
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")
    period_debit: Decimal = Decimal("0")
    period_credit: Decimal = Decimal("0")
    last_movement_date: Optional[datetime] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class CostCenterListResponse(BaseModel):
    """Schema de lista de CostCenter."""

    items: list[CostCenterResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ============================================================================
# Accounting Period Schemas
# ============================================================================


class AccountingPeriodBase(BaseModel):
    """Schema base para AccountingPeriod."""

    chart_id: Optional[UUID] = None
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    period_type: PeriodType = PeriodType.MONTHLY
    year: int = Field(..., ge=2000, le=2100)
    month: Optional[int] = Field(None, ge=1, le=12)
    quarter: Optional[int] = Field(None, ge=1, le=4)
    start_date: date
    end_date: date
    requires_approval: bool = True
    is_initial: bool = False
    is_adjustment: bool = False
    notes: Optional[str] = None

    @field_validator("end_date")
    @classmethod
    def end_date_after_start(cls, v: date, info) -> date:
        """Valida que end_date é posterior a start_date."""
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date deve ser posterior a start_date")
        return v


class AccountingPeriodCreate(AccountingPeriodBase):
    """Schema para criar AccountingPeriod."""


class AccountingPeriodUpdate(BaseModel):
    """Schema para atualizar AccountingPeriod."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    requires_approval: Optional[bool] = None
    notes: Optional[str] = None


class AccountingPeriodResponse(AccountingPeriodBase):
    """Schema de resposta para AccountingPeriod."""

    id: UUID
    condominio_id: UUID
    status: PeriodStatus
    opening_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    closing_type: Optional[ClosingType] = None
    total_entries: int = 0
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    total_documents: int = 0
    opening_balance_total: Decimal = Decimal("0")
    closing_balance_total: Decimal = Decimal("0")
    period_revenue: Decimal = Decimal("0")
    period_expenses: Decimal = Decimal("0")
    period_result: Decimal = Decimal("0")
    closed_by: Optional[UUID] = None
    sped_transmitted: bool = False
    allows_entries: bool = True
    active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class AccountingPeriodListResponse(BaseModel):
    """Schema de lista de AccountingPeriod."""

    items: list[AccountingPeriodResponse]
    total: int
    page: int
    per_page: int
    pages: int


class PeriodCloseRequest(BaseModel):
    """Schema para fechar período."""

    closing_type: ClosingType = ClosingType.PROVISIONAL
    closing_notes: Optional[str] = None


class PeriodReopenRequest(BaseModel):
    """Schema para reabrir período."""

    reopen_reason: str = Field(..., min_length=10, max_length=500)


# ============================================================================
# Journal Entry Schemas
# ============================================================================


class JournalEntryLineBase(BaseModel):
    """Schema base para JournalEntryLine."""

    account_id: UUID
    cost_center_id: Optional[UUID] = None
    line_number: int = Field(..., ge=1)
    debit_amount: Decimal = Field(default=Decimal("0"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0"), ge=0)
    description: Optional[str] = Field(None, max_length=500)
    history_code: Optional[str] = Field(None, max_length=10)
    document_type: Optional[str] = Field(None, max_length=30)
    document_number: Optional[str] = Field(None, max_length=50)
    document_date: Optional[date] = None
    project_id: Optional[UUID] = None
    project_code: Optional[str] = Field(None, max_length=30)

    @field_validator("credit_amount")
    @classmethod
    def validate_amounts(cls, v: Decimal, info) -> Decimal:
        """Valida que apenas um dos valores (débito ou crédito) é preenchido."""
        if "debit_amount" in info.data:
            if info.data["debit_amount"] > 0 and v > 0:
                raise ValueError("Apenas débito ou crédito pode ser preenchido, não ambos")
            if info.data["debit_amount"] == 0 and v == 0:
                raise ValueError("Débito ou crédito deve ser maior que zero")
        return v


class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema para criar JournalEntryLine."""


class JournalEntryLineResponse(JournalEntryLineBase):
    """Schema de resposta para JournalEntryLine."""

    id: UUID
    journal_entry_id: UUID
    counterpart_account_id: Optional[UUID] = None
    counterpart_account_code: Optional[str] = None
    is_reconciled: bool = False
    reconciliation_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Configuração do schema."""

        from_attributes = True


class JournalEntryBase(BaseModel):
    """Schema base para JournalEntry."""

    period_id: UUID
    description: str = Field(..., min_length=1, max_length=500)
    complement: Optional[str] = None
    entry_type: EntryType = EntryType.MANUAL
    origin: EntryOrigin = EntryOrigin.MANUAL
    entry_date: date
    competence_date: date
    source_type: Optional[str] = Field(None, max_length=50)
    source_id: Optional[UUID] = None
    source_number: Optional[str] = Field(None, max_length=50)
    requires_approval: bool = False
    notes: Optional[str] = None


class JournalEntryCreate(JournalEntryBase):
    """Schema para criar JournalEntry."""

    lines: list[JournalEntryLineCreate] = Field(..., min_length=2)

    @field_validator("lines")
    @classmethod
    def validate_balanced(cls, v: list[JournalEntryLineCreate]) -> list[JournalEntryLineCreate]:
        """Valida que o lançamento está balanceado."""
        total_debit = sum(line.debit_amount for line in v)
        total_credit = sum(line.credit_amount for line in v)
        if total_debit != total_credit:
            raise ValueError(
                f"Lançamento desbalanceado: Débito={total_debit}, Crédito={total_credit}"
            )
        return v


class JournalEntryUpdate(BaseModel):
    """Schema para atualizar JournalEntry."""

    description: Optional[str] = Field(None, max_length=500)
    complement: Optional[str] = None
    competence_date: Optional[date] = None
    notes: Optional[str] = None


class JournalEntryResponse(JournalEntryBase):
    """Schema de resposta para JournalEntry."""

    id: UUID
    condominio_id: UUID
    entry_number: str
    batch_number: Optional[str] = None
    status: EntryStatus
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    line_count: int = 0
    posting_date: Optional[datetime] = None
    is_reversal: bool = False
    reversed_entry_id: Optional[UUID] = None
    reversal_entry_id: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    posted_by: Optional[UUID] = None
    sped_included: bool = False
    is_balanced: bool = True
    active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    lines: list[JournalEntryLineResponse] = []

    class Config:
        """Configuração do schema."""

        from_attributes = True


class JournalEntryListResponse(BaseModel):
    """Schema de lista de JournalEntry."""

    items: list[JournalEntryResponse]
    total: int
    page: int
    per_page: int
    pages: int


class JournalEntryReversalRequest(BaseModel):
    """Schema para estornar lançamento."""

    reversal_reason: str = Field(..., min_length=10, max_length=200)
    reversal_date: Optional[date] = None


class JournalEntryApprovalRequest(BaseModel):
    """Schema para aprovar/rejeitar lançamento."""

    approved: bool
    notes: Optional[str] = Field(None, max_length=500)


# ============================================================================
# Trial Balance Schemas
# ============================================================================


class TrialBalanceBase(BaseModel):
    """Schema base para TrialBalance."""

    chart_id: UUID
    period_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    balance_type: BalanceType = BalanceType.VERIFICATION
    balance_period: BalancePeriod = BalancePeriod.MONTHLY
    reference_date: date
    start_date: date
    end_date: date
    year: int = Field(..., ge=2000, le=2100)
    month: Optional[int] = Field(None, ge=1, le=12)
    include_zero_balance: bool = False
    include_inactive: bool = False
    show_cost_centers: bool = False
    notes: Optional[str] = None


class TrialBalanceCreate(TrialBalanceBase):
    """Schema para criar TrialBalance."""

    filter_account_types: Optional[list[AccountType]] = None
    filter_levels: Optional[list[int]] = None
    filter_cost_centers: Optional[list[UUID]] = None


class TrialBalanceResponse(TrialBalanceBase):
    """Schema de resposta para TrialBalance."""

    id: UUID
    condominio_id: UUID
    code: str
    status: BalanceStatus
    total_accounts: int = 0
    total_analytical: int = 0
    previous_debit_total: Decimal = Decimal("0")
    previous_credit_total: Decimal = Decimal("0")
    previous_balance_debit: Decimal = Decimal("0")
    previous_balance_credit: Decimal = Decimal("0")
    period_debit_total: Decimal = Decimal("0")
    period_credit_total: Decimal = Decimal("0")
    current_debit_total: Decimal = Decimal("0")
    current_credit_total: Decimal = Decimal("0")
    current_balance_debit: Decimal = Decimal("0")
    current_balance_credit: Decimal = Decimal("0")
    is_balanced: bool = True
    difference_amount: Decimal = Decimal("0")
    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    period_result: Decimal = Decimal("0")
    total_assets: Decimal = Decimal("0")
    total_liabilities: Decimal = Decimal("0")
    total_equity: Decimal = Decimal("0")
    generated_at: Optional[datetime] = None
    generated_by: Optional[UUID] = None
    generation_time_ms: Optional[int] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    exported_pdf: bool = False
    exported_excel: bool = False
    active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class TrialBalanceItemResponse(BaseModel):
    """Schema de resposta para TrialBalanceItem."""

    id: UUID
    trial_balance_id: UUID
    account_id: UUID
    account_code: str
    account_name: str
    account_type: str
    account_nature: str
    account_level: int
    is_analytical: bool
    cost_center_id: Optional[UUID] = None
    cost_center_code: Optional[str] = None
    cost_center_name: Optional[str] = None
    previous_debit: Decimal = Decimal("0")
    previous_credit: Decimal = Decimal("0")
    previous_balance: Decimal = Decimal("0")
    period_debit: Decimal = Decimal("0")
    period_credit: Decimal = Decimal("0")
    current_debit: Decimal = Decimal("0")
    current_credit: Decimal = Decimal("0")
    current_balance: Decimal = Decimal("0")
    variation_absolute: Optional[Decimal] = None
    variation_percentage: Optional[Decimal] = None
    display_order: Optional[int] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class TrialBalanceListResponse(BaseModel):
    """Schema de lista de TrialBalance."""

    items: list[TrialBalanceResponse]
    total: int
    page: int
    per_page: int
    pages: int


class TrialBalanceDetailResponse(TrialBalanceResponse):
    """Schema detalhado de TrialBalance com itens."""

    items: list[TrialBalanceItemResponse] = []


# ============================================================================
# Statistics Schemas
# ============================================================================


class ChartStats(BaseModel):
    """Estatísticas do plano de contas."""

    total_charts: int = 0
    active_charts: int = 0
    total_accounts: int = 0
    analytical_accounts: int = 0
    synthetic_accounts: int = 0
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}


class AccountStats(BaseModel):
    """Estatísticas de contas contábeis."""

    total_accounts: int = 0
    active_accounts: int = 0
    by_type: dict[str, int] = {}
    by_nature: dict[str, int] = {}
    by_classification: dict[str, int] = {}
    total_balance: Decimal = Decimal("0")
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")


class CostCenterStats(BaseModel):
    """Estatísticas de centros de custo."""

    total_cost_centers: int = 0
    active_cost_centers: int = 0
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total_budget: Decimal = Decimal("0")
    total_used: Decimal = Decimal("0")
    budget_usage_percent: Decimal = Decimal("0")
    over_budget_count: int = 0


class PeriodStats(BaseModel):
    """Estatísticas de períodos contábeis."""

    total_periods: int = 0
    open_periods: int = 0
    closed_periods: int = 0
    by_status: dict[str, int] = {}
    total_entries: int = 0
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")


class JournalStats(BaseModel):
    """Estatísticas de lançamentos contábeis."""

    total_entries: int = 0
    posted_entries: int = 0
    pending_entries: int = 0
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_origin: dict[str, int] = {}
    total_debit: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    entries_today: int = 0
    entries_this_month: int = 0


class BalanceStats(BaseModel):
    """Estatísticas de balancetes."""

    total_balances: int = 0
    generated: int = 0
    approved: int = 0
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    last_generated: Optional[datetime] = None


# ============================================================================
# Filter Schemas
# ============================================================================


class AccountFilter(BaseModel):
    """Filtros para contas contábeis."""

    chart_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    account_type: Optional[AccountType] = None
    nature: Optional[AccountNature] = None
    classification: Optional[AccountClassification] = None
    status: Optional[AccountStatus] = None
    level: Optional[int] = None
    has_balance: Optional[bool] = None
    search: Optional[str] = None


class JournalFilter(BaseModel):
    """Filtros para lançamentos contábeis."""

    period_id: Optional[UUID] = None
    entry_type: Optional[EntryType] = None
    status: Optional[EntryStatus] = None
    origin: Optional[EntryOrigin] = None
    account_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    search: Optional[str] = None


class BalanceFilter(BaseModel):
    """Filtros para balancetes."""

    balance_type: Optional[BalanceType] = None
    status: Optional[BalanceStatus] = None
    year: Optional[int] = None
    month: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
