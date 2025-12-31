"""Repositories do modulo financeiro - Contas a Pagar, Contas a Receber, Fluxo de Caixa, Compras, Estoque e Contabilidade."""

# Contabilidade
from modules.financial.repositories.accounting_repository import (
    AccountingAccountRepository,
    AccountingPeriodRepository,
    ChartOfAccountsRepository,
    CostCenterRepository,
    JournalEntryLineRepository,
    JournalEntryRepository,
    TrialBalanceItemRepository,
    TrialBalanceRepository,
)

# Contas a Pagar
# Fluxo de Caixa
from modules.financial.repositories.cashflow_repository import (
    BankAccountRepository,
    BankReconciliationRepository,
    BankTransactionRepository,
    CashFlowEntryRepository,
    CashFlowForecastRepository,
)

# Estoque
from modules.financial.repositories.inventory_repository import (
    StockInventoryItemRepository,
    StockInventoryRepository,
    StockItemRepository,
    StockMovementRepository,
    StockReservationRepository,
    WarehouseRepository,
)
from modules.financial.repositories.payable_repository import (
    PayableAccountRepository,
    PayableInstallmentRepository,
    PayablePaymentRepository,
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

# Contas a Receber
from modules.financial.repositories.receivable_repository import (
    BillingRuleRepository,
    CustomerRepository,
    ReceivableAccountRepository,
    ReceivableCategoryRepository,
    ReceivableInstallmentRepository,
    ReceivablePaymentRepository,
)
from modules.financial.repositories.supplier_repository import SupplierRepository

# Fiscal
from modules.financial.repositories.fiscal_repository import FiscalRepository

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
    # Estoque
    "WarehouseRepository",
    "StockItemRepository",
    "StockMovementRepository",
    "StockInventoryRepository",
    "StockInventoryItemRepository",
    "StockReservationRepository",
    # Contabilidade
    "ChartOfAccountsRepository",
    "AccountingAccountRepository",
    "CostCenterRepository",
    "AccountingPeriodRepository",
    "JournalEntryRepository",
    "JournalEntryLineRepository",
    "TrialBalanceRepository",
    "TrialBalanceItemRepository",
    # Fiscal
    "FiscalRepository",
]
