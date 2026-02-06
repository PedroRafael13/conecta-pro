"""
tests/domains/financial/test_cashflow_projection.py
Testes unitarios para CashFlowProjection e CashFlowService.
"""

import sys
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, "/opt/conecta-pro/backend")

from modules.financial.services.cashflow_service import CashFlowProjection


class TestCashFlowProjectionCreation:
    """Testes de criacao de projecao."""

    def test_create_default_values(self):
        proj = CashFlowProjection(date=date(2026, 2, 1))
        assert proj.date == date(2026, 2, 1)
        assert proj.payables == Decimal("0")
        assert proj.receivables == Decimal("0")
        assert proj.balance == Decimal("0")
        assert proj.cumulative_balance == Decimal("0")
        assert proj.details == []

    def test_create_with_values(self):
        proj = CashFlowProjection(
            date=date(2026, 3, 1),
            payables=Decimal("5000"),
            receivables=Decimal("8000"),
            balance=Decimal("3000"),
        )
        assert proj.payables == Decimal("5000")
        assert proj.receivables == Decimal("8000")
        assert proj.balance == Decimal("3000")


class TestCashFlowProjectionToDict:
    """Testes de conversao para dicionario."""

    def test_to_dict_structure(self):
        proj = CashFlowProjection(
            date=date(2026, 2, 15),
            payables=Decimal("1500.50"),
            receivables=Decimal("3200.75"),
            balance=Decimal("1700.25"),
        )
        proj.cumulative_balance = Decimal("10000")

        d = proj.to_dict()

        assert d["date"] == "2026-02-15"
        assert d["payables"] == 1500.50
        assert d["receivables"] == 3200.75
        assert d["balance"] == 1700.25
        assert d["cumulative_balance"] == 10000.0
        assert d["details"] == []

    def test_to_dict_with_details(self):
        proj = CashFlowProjection(date=date(2026, 2, 1))
        proj.details = [
            {"description": "Conta luz", "value": -500},
            {"description": "Recebimento taxa", "value": 1200},
        ]

        d = proj.to_dict()

        assert len(d["details"]) == 2
        assert d["details"][0]["description"] == "Conta luz"

    def test_to_dict_zero_values(self):
        proj = CashFlowProjection(date=date(2026, 1, 1))
        d = proj.to_dict()

        assert d["payables"] == 0.0
        assert d["receivables"] == 0.0
        assert d["balance"] == 0.0
        assert d["cumulative_balance"] == 0.0


class TestCashFlowProjectionBalance:
    """Testes de calculo de saldo."""

    def test_positive_balance(self):
        proj = CashFlowProjection(
            date=date(2026, 2, 1),
            receivables=Decimal("10000"),
            payables=Decimal("7000"),
            balance=Decimal("3000"),
        )
        assert float(proj.balance) > 0

    def test_negative_balance(self):
        proj = CashFlowProjection(
            date=date(2026, 2, 1),
            receivables=Decimal("3000"),
            payables=Decimal("7000"),
            balance=Decimal("-4000"),
        )
        assert float(proj.balance) < 0

    def test_zero_balance(self):
        proj = CashFlowProjection(
            date=date(2026, 2, 1),
            receivables=Decimal("5000"),
            payables=Decimal("5000"),
            balance=Decimal("0"),
        )
        assert float(proj.balance) == 0

    def test_cumulative_balance_tracking(self):
        projections = []
        cumulative = Decimal("0")

        for i in range(5):
            proj = CashFlowProjection(
                date=date(2026, 2, 1) + timedelta(days=i),
                balance=Decimal("1000") if i % 2 == 0 else Decimal("-500"),
            )
            cumulative += proj.balance
            proj.cumulative_balance = cumulative
            projections.append(proj)

        # 1000, -500, 1000, -500, 1000 = 2000
        assert projections[-1].cumulative_balance == Decimal("2000")
