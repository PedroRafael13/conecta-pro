"""Models do modulo financeiro - Contas a Pagar e Contas a Receber."""

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
]
