"""Controllers do módulo financeiro - Contas a Pagar."""

from modules.financial.controllers.cashflow_controller import router as cashflow_router
from modules.financial.controllers.payable_controller import router as payable_router
from modules.financial.controllers.supplier_controller import router as supplier_router

__all__ = [
    "supplier_router",
    "payable_router",
    "cashflow_router",
]
