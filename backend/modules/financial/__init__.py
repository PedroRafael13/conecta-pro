"""
Module: financial
Description: Modulo Financeiro Completo - Conecta PRO
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Legislacao fiscal e contabil brasileira

Este modulo fornece gestao financeira completa:
- Contas a Pagar: Fornecedores, parcelas, pagamentos
- Contas a Receber: Clientes, cobrancas, recebimentos
- Fluxo de Caixa: Contas bancarias, transacoes, reconciliacao
- Compras: Requisicoes, cotacoes, pedidos, recebimento
- Estoque: Armazens, itens, movimentacoes, inventarios
- Contabilidade: Plano de contas, lancamentos, balancetes
- Fiscal: NFe, NFSe, SPED, obrigacoes fiscais
- BI/Dashboard: KPIs, widgets, relatorios agendados
- Custeio ABC: Drivers, atividades, pools, alocacoes

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio e IA
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
- bi_dashboard/: Submodulo de BI e dashboards
- costing/: Submodulo de custeio ABC
"""

from fastapi import APIRouter

# Routers dos submodulos
from modules.financial.bi_dashboard.controllers import router as bi_dashboard_router

# Models do BI Dashboard
from modules.financial.bi_dashboard.models import (
    AnalyticsCache,
    FinancialDashboard,
    FinancialKPI,
    FinancialWidget,
    ScheduledReport,
)

# Repositories do BI Dashboard
from modules.financial.bi_dashboard.repositories import (
    CacheRepository,
    DashboardRepository,
    KPIRepository,
    ReportRepository,
    WidgetRepository,
)

# Services do BI Dashboard
from modules.financial.bi_dashboard.services import (
    AnalyticsService,
    BIService,
    ForecastService,
)

# =============================================================================
# ROUTERS DOS CONTROLLERS PRINCIPAIS
# =============================================================================
from modules.financial.controllers import (
    # Contabilidade
    accounting_router,
    # Fluxo de Caixa
    bank_account_router,
    bank_reconciliation_router,
    bank_transaction_router,
    billing_rule_router,
    cashflow_router,
    # Contas a Receber
    customer_router,
    # Fiscal
    fiscal_router,
    # Estoque
    inventory_router,
    payable_router,
    # Compras
    purchase_router,
    receivable_category_router,
    receivable_router,
    # Contas a Pagar
    supplier_router,
)
from modules.financial.costing import router as costing_router

# Models do Custeio
from modules.financial.costing.models import (
    CostActivity,
    CostAllocation,
    CostAnalysis,
    CostDriver,
    CostObject,
    CostPool,
)

# Repositories do Custeio
from modules.financial.costing.repositories import (
    CostActivityRepository,
    CostAllocationRepository,
    CostAnalysisRepository,
    CostDriverRepository,
    CostObjectRepository,
    CostPoolRepository,
)

# Services do Custeio
from modules.financial.costing.services import (
    ABCService,
    AllocationService,
    CostAIService,
)

# =============================================================================
# MODELS PRINCIPAIS (Re-exports para acesso direto)
# =============================================================================
from modules.financial.models import (
    CFOP,
    NCM,
    AccountingAccount,
    AccountingPeriod,
    # === Fluxo de Caixa ===
    BankAccount,
    BankAccountStatus,
    BankAccountType,
    BankReconciliation,
    BankTransaction,
    BillingRule,
    CashFlowEntry,
    CashFlowForecast,
    # === Contabilidade ===
    ChartOfAccounts,
    CostCenter,
    # === Contas a Receber ===
    Customer,
    CustomerStatus,
    CustomerType,
    FiscalObligation,
    GoodsReceipt,
    JournalEntry,
    NFe,
    NFSe,
    PayableAccount,
    PayableInstallment,
    PayablePayment,
    PayableStatus,
    PayableType,
    PaymentMethod,
    # === Compras ===
    Product,
    ProductCategory,
    PurchaseApproval,
    PurchaseOrder,
    PurchaseQuotation,
    PurchaseRequisition,
    ReceivableAccount,
    ReceivableInstallment,
    ReceivablePayment,
    ReceivableStatus,
    ReceivableType,
    SPEDFile,
    StockInventory,
    StockItem,
    StockMovement,
    StockReservation,
    # === Contas a Pagar ===
    Supplier,
    SupplierStatus,
    SupplierType,
    # === Fiscal ===
    TaxConfiguration,
    TransactionType,
    TrialBalance,
    # === Estoque ===
    Warehouse,
)

# =============================================================================
# REPOSITORIES PRINCIPAIS (Re-exports para acesso direto)
# =============================================================================
from modules.financial.repositories import (
    AccountingAccountRepository,
    AccountingPeriodRepository,
    # Fluxo de Caixa
    BankAccountRepository,
    BankReconciliationRepository,
    BankTransactionRepository,
    BillingRuleRepository,
    CashFlowEntryRepository,
    CashFlowForecastRepository,
    # Contabilidade
    ChartOfAccountsRepository,
    CostCenterRepository,
    # Contas a Receber
    CustomerRepository,
    # Fiscal
    FiscalRepository,
    GoodsReceiptRepository,
    JournalEntryRepository,
    PayableAccountRepository,
    PayableInstallmentRepository,
    PayablePaymentRepository,
    # Compras
    ProductCategoryRepository,
    ProductRepository,
    PurchaseApprovalRepository,
    PurchaseOrderRepository,
    PurchaseQuotationRepository,
    PurchaseRequisitionRepository,
    ReceivableAccountRepository,
    ReceivableCategoryRepository,
    ReceivableInstallmentRepository,
    ReceivablePaymentRepository,
    StockInventoryRepository,
    StockItemRepository,
    StockMovementRepository,
    StockReservationRepository,
    # Contas a Pagar
    SupplierRepository,
    TrialBalanceRepository,
    # Estoque
    WarehouseRepository,
)

# =============================================================================
# SERVICES PRINCIPAIS (Re-exports para acesso direto)
# =============================================================================
from modules.financial.services import (
    # Contabilidade
    AccountingAIService,
    CashFlowAIService,
    # Fluxo de Caixa
    CashFlowService,
    # Fiscal
    FiscalAIService,
    PayableAIService,
    # Contas a Pagar
    PayableService,
    # Compras
    PurchaseAIService,
    SupplierService,
)

# =============================================================================
# ROUTER PRINCIPAL AGREGADOR
# =============================================================================

# Cria router principal que agrega todos os sub-routers
financial_router = APIRouter(prefix="/financial", tags=["Financial"])

# === Contas a Pagar ===
financial_router.include_router(supplier_router)
financial_router.include_router(payable_router)

# === Contas a Receber ===
financial_router.include_router(customer_router)
financial_router.include_router(receivable_category_router)
financial_router.include_router(receivable_router)
financial_router.include_router(billing_rule_router)

# === Fluxo de Caixa ===
financial_router.include_router(bank_account_router)
financial_router.include_router(bank_transaction_router)
financial_router.include_router(bank_reconciliation_router)
financial_router.include_router(cashflow_router)

# === Compras ===
financial_router.include_router(purchase_router)

# === Estoque ===
financial_router.include_router(inventory_router)

# === Contabilidade ===
financial_router.include_router(accounting_router)

# === Fiscal ===
financial_router.include_router(fiscal_router)

# === BI/Dashboard ===
financial_router.include_router(bi_dashboard_router)

# === Custeio ABC ===
financial_router.include_router(costing_router)

# Alias para compatibilidade
router = financial_router

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # =========================================================================
    # ROUTERS
    # =========================================================================
    "financial_router",
    "router",
    # Routers individuais - Contas a Pagar
    "supplier_router",
    "payable_router",
    # Routers individuais - Contas a Receber
    "customer_router",
    "receivable_category_router",
    "receivable_router",
    "billing_rule_router",
    # Routers individuais - Fluxo de Caixa
    "bank_account_router",
    "bank_transaction_router",
    "bank_reconciliation_router",
    "cashflow_router",
    # Routers individuais - Compras/Estoque
    "purchase_router",
    "inventory_router",
    # Routers individuais - Contabilidade/Fiscal
    "accounting_router",
    "fiscal_router",
    # Routers submodulos
    "bi_dashboard_router",
    "costing_router",
    # =========================================================================
    # MODELS - Contas a Pagar
    # =========================================================================
    "Supplier",
    "SupplierType",
    "SupplierStatus",
    "PayableAccount",
    "PayableStatus",
    "PayableType",
    "PayableInstallment",
    "PayablePayment",
    "PaymentMethod",
    # =========================================================================
    # MODELS - Contas a Receber
    # =========================================================================
    "Customer",
    "CustomerType",
    "CustomerStatus",
    "ReceivableAccount",
    "ReceivableStatus",
    "ReceivableType",
    "ReceivableInstallment",
    "ReceivablePayment",
    "BillingRule",
    # =========================================================================
    # MODELS - Fluxo de Caixa
    # =========================================================================
    "BankAccount",
    "BankAccountType",
    "BankAccountStatus",
    "BankTransaction",
    "TransactionType",
    "BankReconciliation",
    "CashFlowEntry",
    "CashFlowForecast",
    # =========================================================================
    # MODELS - Compras
    # =========================================================================
    "Product",
    "ProductCategory",
    "PurchaseRequisition",
    "PurchaseQuotation",
    "PurchaseOrder",
    "GoodsReceipt",
    "PurchaseApproval",
    # =========================================================================
    # MODELS - Estoque
    # =========================================================================
    "Warehouse",
    "StockItem",
    "StockMovement",
    "StockInventory",
    "StockReservation",
    # =========================================================================
    # MODELS - Contabilidade
    # =========================================================================
    "ChartOfAccounts",
    "AccountingAccount",
    "CostCenter",
    "AccountingPeriod",
    "JournalEntry",
    "TrialBalance",
    # =========================================================================
    # MODELS - Fiscal
    # =========================================================================
    "TaxConfiguration",
    "NFe",
    "NFSe",
    "SPEDFile",
    "FiscalObligation",
    "CFOP",
    "NCM",
    # =========================================================================
    # MODELS - BI Dashboard
    # =========================================================================
    "FinancialDashboard",
    "FinancialWidget",
    "FinancialKPI",
    "ScheduledReport",
    "AnalyticsCache",
    # =========================================================================
    # MODELS - Custeio ABC
    # =========================================================================
    "CostDriver",
    "CostActivity",
    "CostPool",
    "CostObject",
    "CostAllocation",
    "CostAnalysis",
    # =========================================================================
    # SERVICES - Principais
    # =========================================================================
    "PayableService",
    "SupplierService",
    "PayableAIService",
    "CashFlowService",
    "CashFlowAIService",
    "PurchaseAIService",
    "AccountingAIService",
    "FiscalAIService",
    # =========================================================================
    # SERVICES - BI Dashboard
    # =========================================================================
    "BIService",
    "AnalyticsService",
    "ForecastService",
    # =========================================================================
    # SERVICES - Custeio ABC
    # =========================================================================
    "ABCService",
    "AllocationService",
    "CostAIService",
    # =========================================================================
    # REPOSITORIES - Contas a Pagar
    # =========================================================================
    "SupplierRepository",
    "PayableAccountRepository",
    "PayableInstallmentRepository",
    "PayablePaymentRepository",
    # =========================================================================
    # REPOSITORIES - Contas a Receber
    # =========================================================================
    "CustomerRepository",
    "ReceivableCategoryRepository",
    "ReceivableAccountRepository",
    "ReceivableInstallmentRepository",
    "ReceivablePaymentRepository",
    "BillingRuleRepository",
    # =========================================================================
    # REPOSITORIES - Fluxo de Caixa
    # =========================================================================
    "BankAccountRepository",
    "BankTransactionRepository",
    "BankReconciliationRepository",
    "CashFlowEntryRepository",
    "CashFlowForecastRepository",
    # =========================================================================
    # REPOSITORIES - Compras
    # =========================================================================
    "ProductCategoryRepository",
    "ProductRepository",
    "PurchaseRequisitionRepository",
    "PurchaseQuotationRepository",
    "PurchaseOrderRepository",
    "GoodsReceiptRepository",
    "PurchaseApprovalRepository",
    # =========================================================================
    # REPOSITORIES - Estoque
    # =========================================================================
    "WarehouseRepository",
    "StockItemRepository",
    "StockMovementRepository",
    "StockInventoryRepository",
    "StockReservationRepository",
    # =========================================================================
    # REPOSITORIES - Contabilidade
    # =========================================================================
    "ChartOfAccountsRepository",
    "AccountingAccountRepository",
    "CostCenterRepository",
    "AccountingPeriodRepository",
    "JournalEntryRepository",
    "TrialBalanceRepository",
    # =========================================================================
    # REPOSITORIES - Fiscal
    # =========================================================================
    "FiscalRepository",
    # =========================================================================
    # REPOSITORIES - BI Dashboard
    # =========================================================================
    "DashboardRepository",
    "WidgetRepository",
    "KPIRepository",
    "ReportRepository",
    "CacheRepository",
    # =========================================================================
    # REPOSITORIES - Custeio ABC
    # =========================================================================
    "CostDriverRepository",
    "CostActivityRepository",
    "CostPoolRepository",
    "CostObjectRepository",
    "CostAllocationRepository",
    "CostAnalysisRepository",
]

__version__ = "1.0.0"
