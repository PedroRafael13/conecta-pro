#!/usr/bin/env python3
"""
Diagnóstico detalhado dos imports do api/v1.
"""

import time


def test_import(name, import_statement, timeout=30):
    """Testa um import específico com timeout."""
    print(f"Testing: {name}...", end=" ", flush=True)
    start = time.time()
    try:
        exec(import_statement)  # noqa: S102
        duration = time.time() - start
        print(f"OK ({duration:.2f}s)")
        return True, duration
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False, 0


# Imports do api/v1/__init__.py em ordem
imports = [
    ("fastapi.APIRouter", "from fastapi import APIRouter"),
    ("api.v1.endpoints.auth", "from api.v1.endpoints.auth import router as auth_router"),
    (
        "modules.crm.controllers",
        """from modules.crm.controllers import (
        commission_router, contract_router, dashboard_router,
        lead_router, opportunity_router, proposal_router)""",
    ),
    (
        "modules.operations.controllers",
        """from modules.operacional.controllers import (
        allocation_router, post_router, scale_router, shift_router,
        substitution_router, time_bank_router)""",
    ),
    (
        "modules.financial.controllers",
        """from modules.financial.controllers import (
        accounting_router, supplier_router, payable_router, customer_router,
        receivable_category_router, receivable_router, billing_rule_router,
        bank_account_router, bank_transaction_router, bank_reconciliation_router,
        cashflow_router, purchase_router, inventory_router, fiscal_router)""",
    ),
    ("modules.monitoring", "from modules.monitoring import router as monitoring_router"),
    (
        "modules.automation.workflow.controllers",
        "from modules.automation.workflow.controllers import router as workflow_router",
    ),
    ("modules.fase5.controllers", "from modules.fase5.controllers import fase5_router"),
]

print("=" * 60)
print("DIAGNÓSTICO DETALHADO - api/v1 imports")
print("=" * 60)

for name, stmt in imports:
    success, duration = test_import(name, stmt)
    if not success:
        print(f"\n*** PROBLEMA ENCONTRADO em: {name} ***")
        break
    if duration > 10:
        print(f"*** LENTO: {name} levou {duration:.2f}s ***")

print("=" * 60)
