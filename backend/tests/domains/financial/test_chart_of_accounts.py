"""
tests/domains/financial/test_chart_of_accounts.py
Testes unitarios para plano de contas e entidade AccountEntity.
"""

import sys
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend")
from domains.financial import (
    AccountBalance,
    AccountEntity,
    AccountStatus,
    AccountType,
    ChartOfAccountsEntity,
)

TENANT_ID = uuid4()
CREATED_BY = "test-user"


@pytest.fixture
def active_account():
    return AccountEntity(
        account_code="1.1.1.01",
        account_name="Caixa Geral",
        account_type=AccountType.CHECKING,
        status=AccountStatus.ACTIVE,
        level=4,
        is_analytical=True,
        tenant_id=TENANT_ID,
        created_by=CREATED_BY,
    )


@pytest.fixture
def synthetic_account():
    return AccountEntity(
        account_code="1.1",
        account_name="Ativo Circulante",
        account_type=AccountType.CHECKING,
        status=AccountStatus.ACTIVE,
        level=2,
        is_analytical=False,
        tenant_id=TENANT_ID,
        created_by=CREATED_BY,
    )


@pytest.fixture
def revenue_account():
    return AccountEntity(
        account_code="3.1.1.01",
        account_name="Receita Operacional",
        account_type=AccountType.CHECKING,
        status=AccountStatus.ACTIVE,
        level=4,
        is_analytical=True,
        tenant_id=TENANT_ID,
        created_by=CREATED_BY,
    )


@pytest.fixture
def chart_of_accounts():
    return ChartOfAccountsEntity(
        chart_name="Plano Padrao", fiscal_year=2024, tenant_id=TENANT_ID, created_by=CREATED_BY
    )


class TestAccountBalance:
    def test_net_balance_positive(self):
        b = AccountBalance(
            debit_balance=Decimal("5000"),
            credit_balance=Decimal("3000"),
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
        )
        assert b.net_balance == Decimal("2000")

    def test_net_balance_negative(self):
        b = AccountBalance(
            debit_balance=Decimal("1000"),
            credit_balance=Decimal("4000"),
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
        )
        assert b.net_balance == Decimal("-3000")

    def test_balance_for_debit_nature(self):
        b = AccountBalance(
            debit_balance=Decimal("10000"),
            credit_balance=Decimal("3000"),
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 12, 31),
        )
        assert b.balance_for_debit_nature == Decimal("7000")

    def test_balance_for_credit_nature(self):
        b = AccountBalance(
            debit_balance=Decimal("2000"),
            credit_balance=Decimal("8000"),
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 12, 31),
        )
        assert b.balance_for_credit_nature == Decimal("6000")

    def test_frozen_immutable(self):
        b = AccountBalance(
            debit_balance=Decimal("1000"),
            credit_balance=Decimal("500"),
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
        )
        with pytest.raises(Exception):
            b.debit_balance = Decimal("9999")


class TestAccountEntity:
    def test_analytical_allows_posting(self, active_account):
        assert active_account.allows_posting is True

    def test_synthetic_no_posting(self, synthetic_account):
        assert synthetic_account.allows_posting is False

    def test_debit_nature_asset(self, active_account):
        assert active_account.is_debit_nature is True
        assert active_account.is_credit_nature is False

    def test_credit_nature_revenue(self, revenue_account):
        assert revenue_account.is_credit_nature is True

    def test_balance_sheet_vs_income(self, active_account, revenue_account):
        assert active_account.is_balance_sheet is True
        assert revenue_account.is_income_statement is True

    def test_apply_debit_debit_nature(self, active_account):
        result = active_account.apply_debit(Decimal("1000"))
        assert result == Decimal("1000")

    def test_apply_credit_debit_nature(self, active_account):
        active_account.apply_debit(Decimal("5000"))
        result = active_account.apply_credit(Decimal("2000"))
        assert result == Decimal("3000")

    def test_apply_credit_credit_nature(self, revenue_account):
        assert revenue_account.apply_credit(Decimal("3000")) == Decimal("3000")

    def test_reject_posting_synthetic(self, synthetic_account):
        with pytest.raises(ValueError, match="nao permite lancamentos"):
            synthetic_account.apply_debit(Decimal("1000"))

    def test_reject_posting_inactive(self, active_account):
        active_account.deactivate("admin")
        with pytest.raises(ValueError, match="nao permite lancamentos"):
            active_account.apply_debit(Decimal("1000"))

    def test_deactivate_zero_balance(self, active_account):
        active_account.deactivate("admin")
        assert active_account.status == AccountStatus.INACTIVE

    def test_reject_deactivate_with_balance(self, active_account):
        active_account.apply_debit(Decimal("1000"))
        with pytest.raises(ValueError, match="conta com saldo"):
            active_account.deactivate("admin")

    def test_block_account(self, active_account):
        active_account.block("admin")
        assert active_account.status == AccountStatus.ACTIVE

    def test_activate_after_deactivate(self, active_account):
        active_account.deactivate("admin")
        active_account.activate("admin")
        assert active_account.status == AccountStatus.ACTIVE

    def test_calculate_balance_debit_nature(self, active_account):
        active_account.opening_balance = Decimal("1000")
        balance = active_account.calculate_balance(Decimal("5000"), Decimal("2000"))
        assert balance == Decimal("4000")

    def test_get_account_hierarchy(self, active_account):
        assert active_account.get_account_hierarchy() == ["1", "1.1", "1.1.1", "1.1.1.01"]

    def test_generate_child_code(self):
        assert AccountEntity.generate_child_code("1.1", 3) == "1.1.03"

    def test_reject_invalid_level(self):
        with pytest.raises(ValueError, match="Nivel"):
            AccountEntity(
                account_code="1.1.1.01",
                account_name="Conta Invalida",
                account_type=AccountType.CHECKING,
                level=2,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )


class TestChartOfAccounts:
    def test_create_empty(self, chart_of_accounts):
        assert len(chart_of_accounts.accounts) == 0

    def test_add_and_get(self, chart_of_accounts, active_account):
        chart_of_accounts.add_account(active_account)
        assert chart_of_accounts.get_account("1.1.1.01") is not None

    def test_get_by_id(self, chart_of_accounts, active_account):
        chart_of_accounts.add_account(active_account)
        assert chart_of_accounts.get_account_by_id(active_account.account_id) is not None

    def test_reject_duplicate(self, chart_of_accounts, active_account):
        chart_of_accounts.add_account(active_account)
        dup = AccountEntity(
            account_code="1.1.1.01",
            account_name="Duplicado",
            account_type=AccountType.CHECKING,
            level=4,
            is_analytical=True,
            tenant_id=TENANT_ID,
            created_by=CREATED_BY,
        )
        with pytest.raises(ValueError, match="ja existe"):
            chart_of_accounts.add_account(dup)

    def test_reject_wrong_tenant(self, chart_of_accounts):
        acc = AccountEntity(
            account_code="1.1.1.01",
            account_name="Outro Tenant",
            account_type=AccountType.CHECKING,
            level=4,
            is_analytical=True,
            tenant_id=uuid4(),
            created_by=CREATED_BY,
        )
        with pytest.raises(ValueError, match="outro tenant"):
            chart_of_accounts.add_account(acc)

    def test_reject_exceeding_max_level(self, chart_of_accounts):
        # Pydantic valida level <= 5 antes da criação da entidade
        from pydantic import ValidationError
        with pytest.raises(ValidationError) as exc_info:
            AccountEntity(
                account_code="1.1.1.01",
                account_name="Nivel Seis Invalido",
                account_type=AccountType.CHECKING,
                level=6,
                is_analytical=True,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        assert "less than or equal to 5" in str(exc_info.value)

    def test_get_children(self, chart_of_accounts):
        parent = AccountEntity(
            account_code="1.1",
            account_name="Ativo Circ",
            account_type=AccountType.CHECKING,
            level=2,
            is_analytical=False,
            tenant_id=TENANT_ID,
            created_by=CREATED_BY,
        )
        chart_of_accounts.add_account(parent)
        chart_of_accounts.add_account(
            AccountEntity(
                account_code="1.1.01",
                account_name="Caixa",
                account_type=AccountType.CHECKING,
                level=3,
                is_analytical=True,
                parent_account_id=parent.account_id,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        )
        chart_of_accounts.add_account(
            AccountEntity(
                account_code="1.1.02",
                account_name="Banco",
                account_type=AccountType.CHECKING,
                level=3,
                is_analytical=True,
                parent_account_id=parent.account_id,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        )
        assert len(chart_of_accounts.get_children("1.1")) == 2

    def test_calculate_synthetic_balances(self, chart_of_accounts):
        parent = AccountEntity(
            account_code="1.1",
            account_name="Ativo Circ",
            account_type=AccountType.CHECKING,
            level=2,
            is_analytical=False,
            tenant_id=TENANT_ID,
            created_by=CREATED_BY,
        )
        chart_of_accounts.add_account(parent)
        chart_of_accounts.add_account(
            AccountEntity(
                account_code="1.1.01",
                account_name="Caixa",
                account_type=AccountType.CHECKING,
                level=3,
                is_analytical=True,
                current_balance=Decimal("5000"),
                parent_account_id=parent.account_id,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        )
        chart_of_accounts.add_account(
            AccountEntity(
                account_code="1.1.02",
                account_name="Banco",
                account_type=AccountType.CHECKING,
                level=3,
                is_analytical=True,
                current_balance=Decimal("15000"),
                parent_account_id=parent.account_id,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        )
        assert chart_of_accounts.calculate_synthetic_balances()["1.1"] == Decimal("20000")

    def test_validate_hierarchy_missing_parent(self, chart_of_accounts):
        chart_of_accounts.add_account(
            AccountEntity(
                account_code="1.1",
                account_name="Circulante",
                account_type=AccountType.CHECKING,
                level=2,
                is_analytical=True,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        )
        errors = chart_of_accounts.validate_hierarchy()
        assert len(errors) == 1

    def test_export_structure(self, chart_of_accounts):
        chart_of_accounts.add_account(
            AccountEntity(
                account_code="1.1",
                account_name="Ativo Circulante",
                account_type=AccountType.CHECKING,
                level=2,
                is_analytical=False,
                tenant_id=TENANT_ID,
                created_by=CREATED_BY,
            )
        )
        exported = chart_of_accounts.export_structure()
        assert len(exported) == 1
        assert exported[0]["code"] == "1.1"
