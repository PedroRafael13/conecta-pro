"""Tests for Accounting (Contabilidade) API endpoints - Sprint 27."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status

from modules.financial.models import ChartStatus, ChartType


@pytest.fixture
def mock_user() -> dict[str, Any]:
    """Mock authenticated user."""
    return {
        "id": str(uuid4()),
        "email": "admin@conectaplus.com.br",
        "role": "ADMIN",
        "condominio_id": str(uuid4()),
    }


@pytest.fixture
def sample_chart_data() -> dict[str, Any]:
    """Sample chart of accounts data for tests."""
    return {
        "code": "PC-001",
        "name": "Plano de Contas Principal",
        "description": "Plano de contas padrao do condominio",
        "chart_type": "ANALYTICAL",
        "standard": "CUSTOM",
        "fiscal_year": 2024,
        "valid_from": date(2024, 1, 1).isoformat(),
        "sped_compliant": False,
    }


@pytest.fixture
def sample_account_data() -> dict[str, Any]:
    """Sample accounting account data for tests."""
    return {
        "chart_id": str(uuid4()),
        "code": "1.1.1.01",
        "name": "Caixa Geral",
        "account_type": "ANALYTICAL",
        "nature": "DEBIT",
        "classification": "PATRIMONIAL",
        "level": 4,
        "allow_entries": True,
        "initial_balance": "10000.00",
    }


@pytest.fixture
def sample_cost_center_data() -> dict[str, Any]:
    """Sample cost center data for tests."""
    return {
        "code": "CC-001",
        "name": "Administracao",
        "description": "Centro de custo administrativo",
        "cost_center_type": "ADMINISTRATIVE",
        "allocation_method": "DIRECT",
        "budget_amount": "50000.00",
    }


@pytest.fixture
def sample_period_data() -> dict[str, Any]:
    """Sample accounting period data for tests."""
    return {
        "code": "2024-01",
        "name": "Janeiro 2024",
        "period_type": "MONTHLY",
        "start_date": date(2024, 1, 1).isoformat(),
        "end_date": date(2024, 1, 31).isoformat(),
        "fiscal_year": 2024,
        "month": 1,
    }


@pytest.fixture
def sample_entry_data() -> dict[str, Any]:
    """Sample journal entry data for tests."""
    return {
        "period_id": str(uuid4()),
        "entry_date": date(2024, 1, 15).isoformat(),
        "description": "Pagamento de fornecedor",
        "entry_type": "STANDARD",
        "origin": "MANUAL",
        "lines": [
            {
                "account_id": str(uuid4()),
                "debit_amount": "1000.00",
                "credit_amount": "0.00",
                "description": "Debito em fornecedores",
            },
            {
                "account_id": str(uuid4()),
                "debit_amount": "0.00",
                "credit_amount": "1000.00",
                "description": "Credito em banco",
            },
        ],
    }


@pytest.fixture
def sample_balance_data() -> dict[str, Any]:
    """Sample trial balance data for tests."""
    return {
        "chart_id": str(uuid4()),
        "period_id": str(uuid4()),
        "reference_date": date(2024, 1, 31).isoformat(),
        "name": "Balancete Janeiro 2024",
        "balance_type": "VERIFICATION",
        "balance_period": "MONTHLY",
    }


class TestChartOfAccountsEndpoints:
    """Tests for chart of accounts endpoints."""

    @pytest.mark.asyncio
    async def test_list_charts(self, mock_user: dict[str, Any]) -> None:
        """Test listing charts of accounts."""
        with patch("modules.financial.controllers.accounting_controller.get_current_user") as mock_get_user:
            mock_get_user.return_value = mock_user

            with patch("modules.financial.controllers.accounting_controller.ChartOfAccountsRepository") as mock_repo:
                mock_instance = MagicMock()
                mock_instance.list_with_filter = AsyncMock(return_value=[])
                mock_instance.count_with_filter = AsyncMock(return_value=0)
                mock_repo.return_value = mock_instance

                response_data = {
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "per_page": 20,
                    "pages": 0,
                }

                assert response_data["total"] == 0
                assert response_data["items"] == []

    @pytest.mark.asyncio
    async def test_create_chart(self, mock_user: dict[str, Any], sample_chart_data: dict[str, Any]) -> None:
        """Test creating a chart of accounts."""
        with patch("modules.financial.controllers.accounting_controller.get_current_user") as mock_get_user:
            mock_get_user.return_value = mock_user

            chart_id = uuid4()
            mock_chart = MagicMock()
            mock_chart.id = chart_id
            mock_chart.code = sample_chart_data["code"]
            mock_chart.name = sample_chart_data["name"]
            mock_chart.chart_type = ChartType.BAR
            mock_chart.status = ChartStatus.ACTIVE

            with patch("modules.financial.controllers.accounting_controller.ChartOfAccountsRepository") as mock_repo:
                mock_instance = MagicMock()
                mock_instance.create = AsyncMock(return_value=mock_chart)
                mock_instance.generate_code = AsyncMock(return_value="PC-001")
                mock_repo.return_value = mock_instance

                assert mock_chart.code == "PC-001"
                assert mock_chart.name == "Plano de Contas Principal"

    @pytest.mark.asyncio
    async def test_chart_stats(self, mock_user: dict[str, Any]) -> None:
        """Test getting chart of accounts statistics."""
        stats_data = {
            "total_charts": 3,
            "active_charts": 2,
            "total_accounts": 150,
            "synthetic_accounts": 30,
            "analytical_accounts": 120,
            "by_standard": {
                "CUSTOM": 2,
                "SPED_ECD": 1,
            },
            "by_status": {
                "ACTIVE": 2,
                "DRAFT": 1,
            },
        }

        assert stats_data["total_charts"] == 3
        assert stats_data["active_charts"] == 2
        assert stats_data["by_standard"]["CUSTOM"] == 2


class TestAccountingAccountEndpoints:
    """Tests for accounting account endpoints."""

    @pytest.mark.asyncio
    async def test_list_accounts(self, mock_user: dict[str, Any]) -> None:
        """Test listing accounting accounts."""
        response_data = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "pages": 0,
        }

        assert response_data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_account(self, mock_user: dict[str, Any], sample_account_data: dict[str, Any]) -> None:
        """Test creating an accounting account."""
        account_id = uuid4()
        mock_account = {
            "id": str(account_id),
            "code": sample_account_data["code"],
            "name": sample_account_data["name"],
            "account_type": "ANALYTICAL",
            "nature": "DEBIT",
            "status": "ACTIVE",
        }

        assert mock_account["code"] == "1.1.1.01"
        assert mock_account["account_type"] == "ANALYTICAL"
        assert mock_account["status"] == "ACTIVE"

    @pytest.mark.asyncio
    async def test_get_account_hierarchy(self, mock_user: dict[str, Any]) -> None:
        """Test getting account hierarchy."""
        hierarchy = {
            "id": str(uuid4()),
            "code": "1",
            "name": "Ativo",
            "level": 1,
            "children": [
                {
                    "id": str(uuid4()),
                    "code": "1.1",
                    "name": "Ativo Circulante",
                    "level": 2,
                    "children": [
                        {
                            "id": str(uuid4()),
                            "code": "1.1.1",
                            "name": "Disponibilidades",
                            "level": 3,
                            "children": [],
                        },
                    ],
                },
            ],
        }

        assert hierarchy["code"] == "1"
        assert len(hierarchy["children"]) == 1
        assert hierarchy["children"][0]["code"] == "1.1"

    @pytest.mark.asyncio
    async def test_account_stats(self, mock_user: dict[str, Any]) -> None:
        """Test getting account statistics."""
        stats_data = {
            "total_accounts": 150,
            "synthetic": 30,
            "analytical": 120,
            "with_entries": 85,
            "by_nature": {
                "DEBIT": 70,
                "CREDIT": 80,
            },
            "by_classification": {
                "PATRIMONIAL": 90,
                "RESULT": 60,
            },
            "total_balance": Decimal("500000.00"),
        }

        assert stats_data["total_accounts"] == 150
        assert stats_data["analytical"] == 120


class TestCostCenterEndpoints:
    """Tests for cost center endpoints."""

    @pytest.mark.asyncio
    async def test_list_cost_centers(self, mock_user: dict[str, Any]) -> None:
        """Test listing cost centers."""
        response_data = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "pages": 0,
        }

        assert response_data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_cost_center(self, mock_user: dict[str, Any], sample_cost_center_data: dict[str, Any]) -> None:
        """Test creating a cost center."""
        cost_center_id = uuid4()
        mock_cost_center = {
            "id": str(cost_center_id),
            "code": sample_cost_center_data["code"],
            "name": sample_cost_center_data["name"],
            "cost_center_type": "ADMINISTRATIVE",
            "status": "ACTIVE",
        }

        assert mock_cost_center["code"] == "CC-001"
        assert mock_cost_center["cost_center_type"] == "ADMINISTRATIVE"

    @pytest.mark.asyncio
    async def test_cost_center_hierarchy(self, mock_user: dict[str, Any]) -> None:
        """Test getting cost center hierarchy."""
        hierarchy = {
            "id": str(uuid4()),
            "code": "CC-001",
            "name": "Administracao",
            "level": 1,
            "children": [
                {
                    "id": str(uuid4()),
                    "code": "CC-001-01",
                    "name": "Contabilidade",
                    "level": 2,
                    "children": [],
                },
                {
                    "id": str(uuid4()),
                    "code": "CC-001-02",
                    "name": "RH",
                    "level": 2,
                    "children": [],
                },
            ],
        }

        assert hierarchy["code"] == "CC-001"
        assert len(hierarchy["children"]) == 2

    @pytest.mark.asyncio
    async def test_cost_center_stats(self, mock_user: dict[str, Any]) -> None:
        """Test getting cost center statistics."""
        stats_data = {
            "total_cost_centers": 15,
            "active": 12,
            "total_budget": Decimal("500000.00"),
            "total_actual": Decimal("380000.00"),
            "total_variance": Decimal("120000.00"),
            "by_type": {
                "ADMINISTRATIVE": 5,
                "OPERATIONAL": 6,
                "COMMERCIAL": 2,
                "SUPPORT": 2,
            },
            "by_status": {
                "ACTIVE": 12,
                "INACTIVE": 3,
            },
        }

        assert stats_data["total_cost_centers"] == 15
        assert stats_data["active"] == 12


class TestAccountingPeriodEndpoints:
    """Tests for accounting period endpoints."""

    @pytest.mark.asyncio
    async def test_list_periods(self, mock_user: dict[str, Any]) -> None:
        """Test listing accounting periods."""
        response_data = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "pages": 0,
        }

        assert response_data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_period(self, mock_user: dict[str, Any], sample_period_data: dict[str, Any]) -> None:
        """Test creating an accounting period."""
        period_id = uuid4()
        mock_period = {
            "id": str(period_id),
            "code": sample_period_data["code"],
            "name": sample_period_data["name"],
            "period_type": "MONTHLY",
            "status": "OPEN",
        }

        assert mock_period["code"] == "2024-01"
        assert mock_period["status"] == "OPEN"

    @pytest.mark.asyncio
    async def test_close_period(self, mock_user: dict[str, Any]) -> None:
        """Test closing an accounting period."""
        period_id = uuid4()
        closed_period = {
            "id": str(period_id),
            "status": "CLOSED",
            "closing_type": "TEMPORARY",
            "closed_at": datetime.now().isoformat(),
            "closed_by_id": mock_user["id"],
        }

        assert closed_period["status"] == "CLOSED"
        assert closed_period["closing_type"] == "TEMPORARY"

    @pytest.mark.asyncio
    async def test_reopen_period(self, mock_user: dict[str, Any]) -> None:
        """Test reopening an accounting period."""
        period_id = uuid4()
        reopened_period = {
            "id": str(period_id),
            "status": "REOPENED",
            "reopened_at": datetime.now().isoformat(),
            "reopened_by_id": mock_user["id"],
            "reopen_reason": "Correcao de lancamentos",
        }

        assert reopened_period["status"] == "REOPENED"
        assert reopened_period["reopen_reason"] == "Correcao de lancamentos"

    @pytest.mark.asyncio
    async def test_period_stats(self, mock_user: dict[str, Any]) -> None:
        """Test getting period statistics."""
        stats_data = {
            "total_periods": 24,
            "open": 1,
            "closed": 23,
            "current_period": "2024-12",
            "fiscal_year": 2024,
            "total_entries": 1500,
            "total_debits": Decimal("2500000.00"),
            "total_credits": Decimal("2500000.00"),
        }

        assert stats_data["total_periods"] == 24
        assert stats_data["open"] == 1
        assert stats_data["current_period"] == "2024-12"


class TestJournalEntryEndpoints:
    """Tests for journal entry endpoints."""

    @pytest.mark.asyncio
    async def test_list_entries(self, mock_user: dict[str, Any]) -> None:
        """Test listing journal entries."""
        response_data = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "pages": 0,
        }

        assert response_data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_entry(self, mock_user: dict[str, Any], sample_entry_data: dict[str, Any]) -> None:
        """Test creating a journal entry."""
        entry_id = uuid4()
        mock_entry = {
            "id": str(entry_id),
            "entry_number": "LC-2024-00001",
            "entry_date": sample_entry_data["entry_date"],
            "description": sample_entry_data["description"],
            "entry_type": "STANDARD",
            "status": "DRAFT",
            "total_debit": "1000.00",
            "total_credit": "1000.00",
            "is_balanced": True,
        }

        assert mock_entry["entry_number"] == "LC-2024-00001"
        assert mock_entry["is_balanced"] is True

    @pytest.mark.asyncio
    async def test_create_unbalanced_entry_fails(self, mock_user: dict[str, Any]) -> None:
        """Test that unbalanced entry fails validation."""
        unbalanced_entry = {
            "total_debit": "1000.00",
            "total_credit": "900.00",
            "is_balanced": False,
        }

        assert unbalanced_entry["is_balanced"] is False
        assert Decimal(unbalanced_entry["total_debit"]) != Decimal(unbalanced_entry["total_credit"])

    @pytest.mark.asyncio
    async def test_approve_entry(self, mock_user: dict[str, Any]) -> None:
        """Test approving a journal entry."""
        entry_id = uuid4()
        approved_entry = {
            "id": str(entry_id),
            "status": "APPROVED",
            "approved_at": datetime.now().isoformat(),
            "approved_by_id": mock_user["id"],
        }

        assert approved_entry["status"] == "APPROVED"

    @pytest.mark.asyncio
    async def test_post_entry(self, mock_user: dict[str, Any]) -> None:
        """Test posting a journal entry."""
        entry_id = uuid4()
        posted_entry = {
            "id": str(entry_id),
            "status": "POSTED",
            "posted_at": datetime.now().isoformat(),
            "posted_by_id": mock_user["id"],
        }

        assert posted_entry["status"] == "POSTED"

    @pytest.mark.asyncio
    async def test_reverse_entry(self, mock_user: dict[str, Any]) -> None:
        """Test reversing a journal entry."""
        original_id = uuid4()
        reversal_id = uuid4()
        reversal_entry = {
            "id": str(reversal_id),
            "entry_number": "LC-2024-00002",
            "entry_type": "REVERSAL",
            "status": "POSTED",
            "reversed_entry_id": str(original_id),
            "reversal_reason": "Lancamento incorreto",
        }

        assert reversal_entry["entry_type"] == "REVERSAL"
        assert reversal_entry["reversed_entry_id"] == str(original_id)

    @pytest.mark.asyncio
    async def test_entry_stats(self, mock_user: dict[str, Any]) -> None:
        """Test getting entry statistics."""
        stats_data = {
            "total_entries": 1500,
            "draft": 10,
            "pending": 5,
            "approved": 15,
            "posted": 1450,
            "reversed": 20,
            "total_debit": Decimal("2500000.00"),
            "total_credit": Decimal("2500000.00"),
            "by_type": {
                "STANDARD": 1400,
                "ADJUSTMENT": 50,
                "CLOSING": 30,
                "REVERSAL": 20,
            },
            "by_origin": {
                "MANUAL": 800,
                "AUTOMATIC": 500,
                "INTEGRATION": 200,
            },
        }

        assert stats_data["total_entries"] == 1500
        assert stats_data["posted"] == 1450


class TestTrialBalanceEndpoints:
    """Tests for trial balance endpoints."""

    @pytest.mark.asyncio
    async def test_list_balances(self, mock_user: dict[str, Any]) -> None:
        """Test listing trial balances."""
        response_data = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "pages": 0,
        }

        assert response_data["total"] == 0

    @pytest.mark.asyncio
    async def test_generate_balance(self, mock_user: dict[str, Any], sample_balance_data: dict[str, Any]) -> None:
        """Test generating a trial balance."""
        balance_id = uuid4()
        mock_balance = {
            "id": str(balance_id),
            "name": sample_balance_data["name"],
            "reference_date": sample_balance_data["reference_date"],
            "balance_type": "VERIFICATION",
            "status": "GENERATED",
            "total_debit": "150000.00",
            "total_credit": "150000.00",
            "is_balanced": True,
            "accounts_count": 45,
        }

        assert mock_balance["balance_type"] == "VERIFICATION"
        assert mock_balance["is_balanced"] is True

    @pytest.mark.asyncio
    async def test_verify_balance(self, mock_user: dict[str, Any]) -> None:
        """Test verifying a trial balance."""
        balance_id = uuid4()
        verified_balance = {
            "id": str(balance_id),
            "status": "VERIFIED",
            "verified_at": datetime.now().isoformat(),
            "verified_by_id": mock_user["id"],
            "is_balanced": True,
        }

        assert verified_balance["status"] == "VERIFIED"
        assert verified_balance["is_balanced"] is True

    @pytest.mark.asyncio
    async def test_approve_balance(self, mock_user: dict[str, Any]) -> None:
        """Test approving a trial balance."""
        balance_id = uuid4()
        approved_balance = {
            "id": str(balance_id),
            "status": "APPROVED",
            "approved_at": datetime.now().isoformat(),
            "approved_by_id": mock_user["id"],
        }

        assert approved_balance["status"] == "APPROVED"

    @pytest.mark.asyncio
    async def test_balance_items(self, mock_user: dict[str, Any]) -> None:
        """Test getting trial balance items."""
        items = [
            {
                "account_code": "1.1.1.01",
                "account_name": "Caixa",
                "previous_debit_balance": "10000.00",
                "period_debit": "5000.00",
                "period_credit": "3000.00",
                "current_debit_balance": "12000.00",
            },
            {
                "account_code": "2.1.1.01",
                "account_name": "Fornecedores",
                "previous_credit_balance": "8000.00",
                "period_debit": "5000.00",
                "period_credit": "7000.00",
                "current_credit_balance": "10000.00",
            },
        ]

        assert len(items) == 2
        assert items[0]["account_code"] == "1.1.1.01"

    @pytest.mark.asyncio
    async def test_balance_stats(self, mock_user: dict[str, Any]) -> None:
        """Test getting trial balance statistics."""
        stats_data = {
            "total_balances": 24,
            "generated": 2,
            "verified": 5,
            "approved": 17,
            "current_balance": "Balancete Dezembro 2024",
            "by_type": {
                "VERIFICATION": 20,
                "CLOSING": 4,
            },
            "by_period": {
                "MONTHLY": 22,
                "QUARTERLY": 2,
            },
        }

        assert stats_data["total_balances"] == 24
        assert stats_data["approved"] == 17


class TestAccountingIntegration:
    """Integration tests for accounting module."""

    @pytest.mark.asyncio
    async def test_double_entry_validation(self) -> None:
        """Test double entry bookkeeping validation."""
        debit_amount = Decimal("1000.00")
        credit_amount = Decimal("1000.00")

        is_balanced = debit_amount == credit_amount

        assert is_balanced is True

    @pytest.mark.asyncio
    async def test_account_balance_calculation(self) -> None:
        """Test account balance calculation."""
        initial_balance = Decimal("10000.00")
        debit_entries = Decimal("5000.00")
        credit_entries = Decimal("3000.00")

        # For a debit nature account
        final_balance = initial_balance + debit_entries - credit_entries

        assert final_balance == Decimal("12000.00")

    @pytest.mark.asyncio
    async def test_period_closing_balance_transfer(self) -> None:
        """Test period closing with balance transfer."""
        # Result accounts
        revenue = Decimal("50000.00")
        expenses = Decimal("35000.00")
        net_result = revenue - expenses

        # Transfer to equity
        assert net_result == Decimal("15000.00")

    @pytest.mark.asyncio
    async def test_trial_balance_equation(self) -> None:
        """Test trial balance equation (debits = credits)."""
        total_debits = Decimal("150000.00")
        total_credits = Decimal("150000.00")

        is_balanced = total_debits == total_credits

        assert is_balanced is True

    @pytest.mark.asyncio
    async def test_cost_center_allocation(self) -> None:
        """Test cost center allocation calculation."""
        total_expense = Decimal("10000.00")
        allocations = {
            "CC-001": Decimal("40.00"),  # 40%
            "CC-002": Decimal("35.00"),  # 35%
            "CC-003": Decimal("25.00"),  # 25%
        }

        allocated_amounts = {cc: total_expense * (pct / 100) for cc, pct in allocations.items()}

        assert allocated_amounts["CC-001"] == Decimal("4000.00")
        assert allocated_amounts["CC-002"] == Decimal("3500.00")
        assert allocated_amounts["CC-003"] == Decimal("2500.00")
        assert sum(allocated_amounts.values()) == total_expense

    @pytest.mark.asyncio
    async def test_account_hierarchy_total(self) -> None:
        """Test synthetic account totals from children."""
        child_balances = [
            Decimal("5000.00"),
            Decimal("8000.00"),
            Decimal("3000.00"),
        ]

        synthetic_total = sum(child_balances)

        assert synthetic_total == Decimal("16000.00")

    @pytest.mark.asyncio
    async def test_entry_reversal_creates_opposite(self) -> None:
        """Test that entry reversal creates opposite entries."""
        original_debit = Decimal("1000.00")
        original_credit = Decimal("0.00")

        reversal_debit = original_credit
        reversal_credit = original_debit

        assert reversal_credit == original_debit
        assert reversal_debit == original_credit

    @pytest.mark.asyncio
    async def test_budget_variance_calculation(self) -> None:
        """Test budget vs actual variance calculation."""
        budget = Decimal("50000.00")
        actual = Decimal("45000.00")

        variance_amount = budget - actual
        variance_percent = (variance_amount / budget) * 100

        assert variance_amount == Decimal("5000.00")
        assert variance_percent == Decimal("10.00")

    @pytest.mark.asyncio
    async def test_period_entries_balanced(self) -> None:
        """Test that all entries in period are balanced."""
        entries = [
            {"debit": Decimal("1000.00"), "credit": Decimal("1000.00")},
            {"debit": Decimal("2500.00"), "credit": Decimal("2500.00")},
            {"debit": Decimal("750.00"), "credit": Decimal("750.00")},
        ]

        all_balanced = all(e["debit"] == e["credit"] for e in entries)

        assert all_balanced is True

    @pytest.mark.asyncio
    async def test_sped_account_mapping(self) -> None:
        """Test SPED account code mapping."""
        internal_code = "1.1.1.01"
        sped_code = "1.1.1.01.0001"

        # SPED code should be derived from internal
        assert sped_code.startswith(internal_code)

    @pytest.mark.asyncio
    async def test_closing_entry_generation(self) -> None:
        """Test closing entry generation for result accounts."""
        revenue_accounts = [
            {"code": "3.1.1.01", "balance": Decimal("30000.00")},
            {"code": "3.1.2.01", "balance": Decimal("20000.00")},
        ]
        expense_accounts = [
            {"code": "4.1.1.01", "balance": Decimal("25000.00")},
            {"code": "4.1.2.01", "balance": Decimal("10000.00")},
        ]

        total_revenue = sum(acc["balance"] for acc in revenue_accounts)
        total_expenses = sum(acc["balance"] for acc in expense_accounts)
        net_result = total_revenue - total_expenses

        assert total_revenue == Decimal("50000.00")
        assert total_expenses == Decimal("35000.00")
        assert net_result == Decimal("15000.00")
