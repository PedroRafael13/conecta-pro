"""Models do modulo financeiro - Contas a Pagar, Contas a Receber e Fluxo de Caixa."""

# Contas a Pagar
from modules.financial.models.payable_account import (
    PayableAccount,
    PayablePriority,
    PayableStatus,
    PayableType,
    RecurrenceType,
)
from modules.financial.models.payable_category import CategoryNature, CategoryType, PayableCategory
from modules.financial.models.payable_installment import InstallmentStatus, PayableInstallment
from modules.financial.models.payable_payment import PayablePayment, PaymentOrigin, PaymentStatus
from modules.financial.models.payment_method import (
    PaymentMethod,
    PaymentMethodStatus,
    PaymentMethodType,
)
from modules.financial.models.supplier import (
    PaymentTerms,
    Supplier,
    SupplierCategory,
    SupplierStatus,
    SupplierType,
)

# Contas a Receber
from modules.financial.models.billing_rule import (
    BillingFrequency,
    BillingRule,
    BillingRuleStatus,
    BillingType,
    NotificationType,
)
from modules.financial.models.customer import (
    Customer,
    CustomerStatus,
    CustomerType,
)
from modules.financial.models.receivable_account import (
    ReceivableAccount,
    ReceivablePriority,
    ReceivableStatus,
    ReceivableType,
)
from modules.financial.models.receivable_account import (
    RecurrenceType as ReceivableRecurrenceType,
)
from modules.financial.models.receivable_category import (
    CategoryType as ReceivableCategoryType,
    ReceivableCategory,
)
from modules.financial.models.receivable_installment import (
    InstallmentStatus as ReceivableInstallmentStatus,
    ReceivableInstallment,
)
from modules.financial.models.receivable_payment import (
    PaymentOrigin as ReceivablePaymentOrigin,
    PaymentStatus as ReceivablePaymentStatus,
    ReceivablePayment,
)

# Fluxo de Caixa
from modules.financial.models.bank_account import (
    BankAccount,
    BankAccountStatus,
    BankAccountType,
    PixKeyType,
)
from modules.financial.models.bank_reconciliation import (
    BankReconciliation,
    ReconciliationPeriodType,
    ReconciliationStatus as BankReconciliationStatus,
)
from modules.financial.models.bank_transaction import (
    BankTransaction,
    ReconciliationStatus as TransactionReconciliationStatus,
    TransactionCategory,
    TransactionOrigin,
    TransactionStatus,
    TransactionType,
)
from modules.financial.models.cashflow_entry import (
    CashFlowEntry,
    CashFlowEntryStatus,
    CashFlowEntryType,
    CashFlowSourceType,
    RecurrenceFrequency,
)
from modules.financial.models.cashflow_forecast import (
    CashFlowForecast,
    ForecastConfidence,
    ForecastPeriodType,
    ForecastStatus,
)

__all__ = [
    # === Contas a Pagar ===
    # Supplier
    "Supplier",
    "SupplierType",
    "SupplierStatus",
    "SupplierCategory",
    "PaymentTerms",
    # PaymentMethod
    "PaymentMethod",
    "PaymentMethodType",
    "PaymentMethodStatus",
    # PayableCategory
    "PayableCategory",
    "CategoryType",
    "CategoryNature",
    # PayableAccount
    "PayableAccount",
    "PayableStatus",
    "PayableType",
    "PayablePriority",
    "RecurrenceType",
    # PayableInstallment
    "PayableInstallment",
    "InstallmentStatus",
    # PayablePayment
    "PayablePayment",
    "PaymentStatus",
    "PaymentOrigin",
    # === Contas a Receber ===
    # Customer
    "Customer",
    "CustomerType",
    "CustomerStatus",
    # ReceivableCategory
    "ReceivableCategory",
    "ReceivableCategoryType",
    # ReceivableAccount
    "ReceivableAccount",
    "ReceivableStatus",
    "ReceivableType",
    "ReceivablePriority",
    "ReceivableRecurrenceType",
    # ReceivableInstallment
    "ReceivableInstallment",
    "ReceivableInstallmentStatus",
    # ReceivablePayment
    "ReceivablePayment",
    "ReceivablePaymentStatus",
    "ReceivablePaymentOrigin",
    # BillingRule
    "BillingRule",
    "BillingType",
    "BillingFrequency",
    "BillingRuleStatus",
    "NotificationType",
    # === Fluxo de Caixa ===
    # BankAccount
    "BankAccount",
    "BankAccountType",
    "BankAccountStatus",
    "PixKeyType",
    # BankTransaction
    "BankTransaction",
    "TransactionType",
    "TransactionCategory",
    "TransactionStatus",
    "TransactionOrigin",
    "TransactionReconciliationStatus",
    # BankReconciliation
    "BankReconciliation",
    "ReconciliationPeriodType",
    "BankReconciliationStatus",
    # CashFlowEntry
    "CashFlowEntry",
    "CashFlowEntryType",
    "CashFlowSourceType",
    "CashFlowEntryStatus",
    "RecurrenceFrequency",
    # CashFlowForecast
    "CashFlowForecast",
    "ForecastPeriodType",
    "ForecastStatus",
    "ForecastConfidence",
]
