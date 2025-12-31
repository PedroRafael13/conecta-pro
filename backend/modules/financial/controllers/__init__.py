"""Controllers do modulo financeiro - Contas a Pagar, Contas a Receber, Fluxo de Caixa, Compras, Estoque e Contabilidade."""

# Contabilidade
from modules.financial.controllers.accounting_controller import router as accounting_router

# Contas a Pagar
# Fluxo de Caixa
from modules.financial.controllers.bank_account_controller import router as bank_account_router
from modules.financial.controllers.bank_reconciliation_controller import (
    router as bank_reconciliation_router,
)
from modules.financial.controllers.bank_transaction_controller import (
    router as bank_transaction_router,
)

# Contas a Receber
from modules.financial.controllers.billing_rule_controller import router as billing_rule_router
from modules.financial.controllers.cashflow_controller import router as cashflow_router
from modules.financial.controllers.customer_controller import router as customer_router

# Estoque
from modules.financial.controllers.inventory_controller import router as inventory_router
from modules.financial.controllers.payable_controller import router as payable_router

# Compras
from modules.financial.controllers.purchase_controller import router as purchase_router
from modules.financial.controllers.receivable_category_controller import (
    router as receivable_category_router,
)
from modules.financial.controllers.receivable_controller import router as receivable_router
from modules.financial.controllers.supplier_controller import router as supplier_router

__all__ = [
    # Contas a Pagar
    "supplier_router",
    "payable_router",
    # Contas a Receber
    "customer_router",
    "receivable_category_router",
    "receivable_router",
    "billing_rule_router",
    # Fluxo de Caixa
    "bank_account_router",
    "bank_transaction_router",
    "bank_reconciliation_router",
    "cashflow_router",
    # Compras
    "purchase_router",
    # Estoque
    "inventory_router",
    # Contabilidade
    "accounting_router",
]
