"""Controllers do modulo financeiro - Contas a Pagar e Contas a Receber."""

# Contas a Pagar
from modules.financial.controllers.cashflow_controller import router as cashflow_router
from modules.financial.controllers.payable_controller import router as payable_router
from modules.financial.controllers.supplier_controller import router as supplier_router

# Contas a Receber
from modules.financial.controllers.billing_rule_controller import router as billing_rule_router
from modules.financial.controllers.customer_controller import router as customer_router
from modules.financial.controllers.receivable_category_controller import (
    router as receivable_category_router,
)
from modules.financial.controllers.receivable_controller import router as receivable_router

__all__ = [
    # Contas a Pagar
    "supplier_router",
    "payable_router",
    "cashflow_router",
    # Contas a Receber
    "customer_router",
    "receivable_category_router",
    "receivable_router",
    "billing_rule_router",
]
