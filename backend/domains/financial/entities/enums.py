"""
domains/financial/entities/enums.py - FINANCIAL ENUMS
=====================================================
Enterprise financial accounting enumerations
"""

from enum import StrEnum


class AccountType(StrEnum):
    """Tipo de conta contabil (Plano de Contas)."""

    # Ativo (Assets)
    ASSET_CURRENT = "asset_current"  # Ativo Circulante
    ASSET_NON_CURRENT = "asset_non_current"  # Ativo Nao Circulante
    ASSET_FIXED = "asset_fixed"  # Ativo Imobilizado
    ASSET_INTANGIBLE = "asset_intangible"  # Ativo Intangivel

    # Passivo (Liabilities)
    LIABILITY_CURRENT = "liability_current"  # Passivo Circulante
    LIABILITY_NON_CURRENT = "liability_non_current"  # Passivo Nao Circulante

    # Patrimonio Liquido (Equity)
    EQUITY_CAPITAL = "equity_capital"  # Capital Social
    EQUITY_RESERVES = "equity_reserves"  # Reservas
    EQUITY_RETAINED = "equity_retained"  # Lucros/Prejuizos Acumulados

    # Receitas (Revenue)
    REVENUE_OPERATING = "revenue_operating"  # Receita Operacional
    REVENUE_FINANCIAL = "revenue_financial"  # Receita Financeira
    REVENUE_OTHER = "revenue_other"  # Outras Receitas

    # Despesas (Expenses)
    EXPENSE_OPERATING = "expense_operating"  # Despesa Operacional
    EXPENSE_ADMINISTRATIVE = "expense_administrative"  # Despesa Administrativa
    EXPENSE_FINANCIAL = "expense_financial"  # Despesa Financeira
    EXPENSE_TAX = "expense_tax"  # Despesa Tributaria
    EXPENSE_OTHER = "expense_other"  # Outras Despesas

    # Custos (Costs)
    COST_GOODS = "cost_goods"  # CMV - Custo Mercadorias Vendidas
    COST_SERVICES = "cost_services"  # CSV - Custo Servicos Vendidos

    def is_debit_nature(self) -> bool:
        """Verifica se conta tem natureza devedora."""
        return self in [
            self.ASSET_CURRENT,
            self.ASSET_NON_CURRENT,
            self.ASSET_FIXED,
            self.ASSET_INTANGIBLE,
            self.EXPENSE_OPERATING,
            self.EXPENSE_ADMINISTRATIVE,
            self.EXPENSE_FINANCIAL,
            self.EXPENSE_TAX,
            self.EXPENSE_OTHER,
            self.COST_GOODS,
            self.COST_SERVICES,
        ]

    def is_credit_nature(self) -> bool:
        """Verifica se conta tem natureza credora."""
        return not self.is_debit_nature()

    def is_balance_sheet_account(self) -> bool:
        """Verifica se e conta patrimonial."""
        return self in [
            self.ASSET_CURRENT,
            self.ASSET_NON_CURRENT,
            self.ASSET_FIXED,
            self.ASSET_INTANGIBLE,
            self.LIABILITY_CURRENT,
            self.LIABILITY_NON_CURRENT,
            self.EQUITY_CAPITAL,
            self.EQUITY_RESERVES,
            self.EQUITY_RETAINED,
        ]

    def is_income_statement_account(self) -> bool:
        """Verifica se e conta de resultado."""
        return not self.is_balance_sheet_account()


class AccountStatus(StrEnum):
    """Status da conta contabil."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"


class JournalEntryType(StrEnum):
    """Tipo de lancamento contabil."""

    STANDARD = "standard"  # Lancamento padrao
    ADJUSTING = "adjusting"  # Lancamento de ajuste
    CLOSING = "closing"  # Lancamento de encerramento
    OPENING = "opening"  # Lancamento de abertura
    REVERSAL = "reversal"  # Lancamento de estorno
    RECLASSIFICATION = "reclassification"  # Reclassificacao
    ACCRUAL = "accrual"  # Provisao/Apropriacao
    DEPRECIATION = "depreciation"  # Depreciacao/Amortizacao

    def requires_approval(self) -> bool:
        """Verifica se tipo requer aprovacao."""
        return self in [self.ADJUSTING, self.CLOSING, self.REVERSAL, self.RECLASSIFICATION]

    def is_automatic(self) -> bool:
        """Verifica se e lancamento automatico."""
        return self in [self.DEPRECIATION, self.ACCRUAL]


class JournalEntryStatus(StrEnum):
    """Status do lancamento contabil."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    POSTED = "posted"
    REVERSED = "reversed"
    REJECTED = "rejected"

    @classmethod
    def editable_statuses(cls) -> list["JournalEntryStatus"]:
        """Retorna status que permitem edicao."""
        return [cls.DRAFT, cls.REJECTED]

    @classmethod
    def terminal_statuses(cls) -> list["JournalEntryStatus"]:
        """Retorna status terminais."""
        return [cls.POSTED, cls.REVERSED]

    def can_edit(self) -> bool:
        """Verifica se pode editar."""
        return self in self.editable_statuses()

    def can_post(self) -> bool:
        """Verifica se pode contabilizar."""
        return self == self.APPROVED

    def can_reverse(self) -> bool:
        """Verifica se pode estornar."""
        return self == self.POSTED


class FiscalPeriodStatus(StrEnum):
    """Status do periodo fiscal."""

    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    LOCKED = "locked"

    def allows_posting(self) -> bool:
        """Verifica se permite lancamentos."""
        return self == self.OPEN

    def allows_adjustments(self) -> bool:
        """Verifica se permite ajustes."""
        return self in [self.OPEN, self.CLOSING]


class CostCenterType(StrEnum):
    """Tipo de centro de custo."""

    ADMINISTRATIVE = "administrative"
    COMMERCIAL = "commercial"
    PRODUCTION = "production"
    SUPPORT = "support"
    PROJECT = "project"
    DEPARTMENT = "department"


class TransactionSource(StrEnum):
    """Origem da transacao contabil."""

    MANUAL = "manual"
    ACCOUNTS_PAYABLE = "accounts_payable"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    PAYROLL = "payroll"
    INVENTORY = "inventory"
    FIXED_ASSETS = "fixed_assets"
    BANK_RECONCILIATION = "bank_reconciliation"
    TAX_MODULE = "tax_module"
    PROCUREMENT = "procurement"
    SALES = "sales"
    IMPORT = "import"


class ReconciliationStatus(StrEnum):
    """Status de conciliacao bancaria."""

    NOT_RECONCILED = "not_reconciled"
    PARTIALLY_RECONCILED = "partially_reconciled"
    RECONCILED = "reconciled"
    DISCREPANCY = "discrepancy"
