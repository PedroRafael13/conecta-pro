"""
Módulo FINANCEIRO — Agregador
Unifica: financial (completo)

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Financial Core ---
# --- Financial BI Dashboard ---
from modules.financial.bi_dashboard.controllers import router as bi_dashboard_router
from modules.financial.controllers import (
    accounting_router,
    bank_account_router,
    bank_reconciliation_router,
    bank_transaction_router,
    billing_rule_router,
    cashflow_router,
    customer_router,
    financial_ai_router,
    fiscal_router,
    inventory_router,
    payable_router,
    purchase_router,
    receivable_category_router,
    receivable_router,
    relatorios_router,
    supplier_router,
)

__all__ = [
    "accounting_router",
    "supplier_router",
    "payable_router",
    "customer_router",
    "receivable_category_router",
    "receivable_router",
    "billing_rule_router",
    "bank_account_router",
    "bank_transaction_router",
    "bank_reconciliation_router",
    "cashflow_router",
    "purchase_router",
    "inventory_router",
    "fiscal_router",
    "financial_ai_router",
    "relatorios_router",
    "bi_dashboard_router",
]
