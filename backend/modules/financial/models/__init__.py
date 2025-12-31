"""Models do modulo financeiro - Contas a Pagar, Contas a Receber, Fluxo de Caixa, Compras e Estoque."""

# Contas a Pagar
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
)
from modules.financial.models.bank_reconciliation import (
    ReconciliationStatus as BankReconciliationStatus,
)
from modules.financial.models.bank_transaction import BankTransaction
from modules.financial.models.bank_transaction import (
    ReconciliationStatus as TransactionReconciliationStatus,
)
from modules.financial.models.bank_transaction import (
    TransactionCategory,
    TransactionOrigin,
    TransactionStatus,
    TransactionType,
)

# Contas a Receber
from modules.financial.models.billing_rule import (
    BillingFrequency,
    BillingRule,
    BillingRuleStatus,
    BillingType,
    NotificationType,
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
from modules.financial.models.customer import Customer, CustomerStatus, CustomerType

# Compras
from modules.financial.models.goods_receipt import (
    GoodsReceipt,
    GoodsReceiptItem,
    InspectionResult,
    ReceiptStatus,
    ReceiptType,
)
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
from modules.financial.models.product import Product, ProductStatus, ProductType, UnitOfMeasure
from modules.financial.models.product_category import (
    ProductCategory,
    ProductCategoryStatus,
    ProductCategoryType,
)
from modules.financial.models.purchase_approval import (
    ApprovalAction,
    ApprovalLevel,
    ApprovalStatus,
    ApprovalType,
    PurchaseApproval,
)
from modules.financial.models.purchase_order import (
    OrderPriority,
    OrderStatus,
    PurchaseOrder,
    PurchaseOrderItem,
)
from modules.financial.models.purchase_quotation import (
    DeliveryType,
    PaymentCondition,
    PurchaseQuotation,
    PurchaseQuotationItem,
    QuotationStatus,
)
from modules.financial.models.purchase_requisition import (
    PurchaseRequisition,
    PurchaseRequisitionItem,
    RequisitionPriority,
    RequisitionStatus,
    RequisitionType,
)
from modules.financial.models.receivable_account import (
    ReceivableAccount,
    ReceivablePriority,
    ReceivableStatus,
    ReceivableType,
)
from modules.financial.models.receivable_account import RecurrenceType as ReceivableRecurrenceType
from modules.financial.models.receivable_category import CategoryType as ReceivableCategoryType
from modules.financial.models.receivable_category import ReceivableCategory
from modules.financial.models.receivable_installment import (
    InstallmentStatus as ReceivableInstallmentStatus,
)
from modules.financial.models.receivable_installment import ReceivableInstallment
from modules.financial.models.receivable_payment import PaymentOrigin as ReceivablePaymentOrigin
from modules.financial.models.receivable_payment import PaymentStatus as ReceivablePaymentStatus
from modules.financial.models.receivable_payment import ReceivablePayment

# Estoque
from modules.financial.models.stock_inventory import (
    InventoryItemStatus,
    InventoryStatus,
    InventoryType,
    StockInventory,
    StockInventoryItem,
)
from modules.financial.models.stock_item import CostingMethod, StockItem, StockItemStatus
from modules.financial.models.stock_movement import (
    MovementReason,
    MovementStatus,
    MovementType,
    StockMovement,
)
from modules.financial.models.stock_reservation import (
    ReservationPriority,
    ReservationStatus,
    ReservationType,
    StockReservation,
)
from modules.financial.models.supplier import (
    PaymentTerms,
    Supplier,
    SupplierCategory,
    SupplierStatus,
    SupplierType,
)
from modules.financial.models.warehouse import (
    StorageType,
    Warehouse,
    WarehouseStatus,
    WarehouseType,
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
    # === Compras ===
    # ProductCategory
    "ProductCategory",
    "ProductCategoryType",
    "ProductCategoryStatus",
    # Product
    "Product",
    "ProductType",
    "ProductStatus",
    "UnitOfMeasure",
    # PurchaseRequisition
    "PurchaseRequisition",
    "PurchaseRequisitionItem",
    "RequisitionStatus",
    "RequisitionPriority",
    "RequisitionType",
    # PurchaseQuotation
    "PurchaseQuotation",
    "PurchaseQuotationItem",
    "QuotationStatus",
    "PaymentCondition",
    "DeliveryType",
    # PurchaseOrder
    "PurchaseOrder",
    "PurchaseOrderItem",
    "OrderStatus",
    "OrderPriority",
    # GoodsReceipt
    "GoodsReceipt",
    "GoodsReceiptItem",
    "ReceiptStatus",
    "ReceiptType",
    "InspectionResult",
    # PurchaseApproval
    "PurchaseApproval",
    "ApprovalType",
    "ApprovalStatus",
    "ApprovalLevel",
    "ApprovalAction",
    # === Estoque ===
    # Warehouse
    "Warehouse",
    "WarehouseType",
    "WarehouseStatus",
    "StorageType",
    # StockItem
    "StockItem",
    "StockItemStatus",
    "CostingMethod",
    # StockMovement
    "StockMovement",
    "MovementType",
    "MovementReason",
    "MovementStatus",
    # StockInventory
    "StockInventory",
    "StockInventoryItem",
    "InventoryType",
    "InventoryStatus",
    "InventoryItemStatus",
    # StockReservation
    "StockReservation",
    "ReservationType",
    "ReservationStatus",
    "ReservationPriority",
]
