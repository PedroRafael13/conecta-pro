"""Repositories do modulo financeiro - Contas a Pagar, Contas a Receber, Fluxo de Caixa e Compras."""

# Contas a Pagar
from modules.financial.repositories.payable_repository import (
    PayableAccountRepository,
    PayableInstallmentRepository,
    PayablePaymentRepository,
)
from modules.financial.repositories.supplier_repository import SupplierRepository

# Contas a Receber
from modules.financial.repositories.receivable_repository import (
    BillingRuleRepository,
    CustomerRepository,
    ReceivableAccountRepository,
    ReceivableCategoryRepository,
    ReceivableInstallmentRepository,
    ReceivablePaymentRepository,
)

# Fluxo de Caixa
from modules.financial.repositories.cashflow_repository import (
    BankAccountRepository,
    BankReconciliationRepository,
    BankTransactionRepository,
    CashFlowEntryRepository,
    CashFlowForecastRepository,
)

# Compras
from modules.financial.repositories.purchase_repository import (
    GoodsReceiptRepository,
    ProductCategoryRepository,
    ProductRepository,
    PurchaseApprovalRepository,
    PurchaseOrderRepository,
    PurchaseQuotationRepository,
    PurchaseRequisitionRepository,
)

__all__ = [
    # Contas a Pagar
    "SupplierRepository",
    "PayableAccountRepository",
    "PayableInstallmentRepository",
    "PayablePaymentRepository",
    # Contas a Receber
    "CustomerRepository",
    "ReceivableCategoryRepository",
    "ReceivableAccountRepository",
    "ReceivableInstallmentRepository",
    "ReceivablePaymentRepository",
    "BillingRuleRepository",
    # Fluxo de Caixa
    "BankAccountRepository",
    "BankTransactionRepository",
    "BankReconciliationRepository",
    "CashFlowEntryRepository",
    "CashFlowForecastRepository",
    # Compras
    "ProductCategoryRepository",
    "ProductRepository",
    "PurchaseRequisitionRepository",
    "PurchaseQuotationRepository",
    "PurchaseOrderRepository",
    "GoodsReceiptRepository",
    "PurchaseApprovalRepository",
]
