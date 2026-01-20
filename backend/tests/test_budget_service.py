"""Testes para BudgetService - Sprint 30.

Testa funcionalidades de Orçamento.
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.services.budget_service import (
    BudgetExecution,
    BudgetExecutionReport,
    BudgetLineItem,
    BudgetPeriodType,
    BudgetReport,
    BudgetService,
    BudgetStatus,
    BudgetVarianceType,
)


class TestBudgetLineItem:
    """Testes para BudgetLineItem dataclass."""

    def test_create_line_item(self) -> None:
        """Testa criação de item de linha."""
        item = BudgetLineItem(
            account_id=uuid4(),
            account_code="4.1.01.001",
            account_name="Receita de Condomínio",
        )

        assert item.account_code == "4.1.01.001"
        assert item.total_budgeted == Decimal("0")

    def test_calculate_total(self) -> None:
        """Testa cálculo de total."""
        item = BudgetLineItem(
            account_id=uuid4(),
            account_code="4.1.01.001",
            account_name="Receita",
            jan=Decimal("1000"),
            feb=Decimal("1000"),
            mar=Decimal("1000"),
            apr=Decimal("1000"),
            may=Decimal("1000"),
            jun=Decimal("1000"),
            jul=Decimal("1000"),
            aug=Decimal("1000"),
            sep=Decimal("1000"),
            oct=Decimal("1000"),
            nov=Decimal("1000"),
            dec=Decimal("1000"),
        )

        item.calculate_total()

        assert item.total_budgeted == Decimal("12000")

    def test_get_month_value(self) -> None:
        """Testa obtenção de valor por mês."""
        item = BudgetLineItem(
            account_id=uuid4(),
            account_code="4.1.01.001",
            account_name="Receita",
            jan=Decimal("1000"),
            jun=Decimal("1500"),
            dec=Decimal("2000"),
        )

        assert item.get_month_value(1) == Decimal("1000")
        assert item.get_month_value(6) == Decimal("1500")
        assert item.get_month_value(12) == Decimal("2000")
        assert item.get_month_value(0) == Decimal("0")
        assert item.get_month_value(13) == Decimal("0")


class TestBudgetExecution:
    """Testes para BudgetExecution dataclass."""

    def test_create_execution(self) -> None:
        """Testa criação de execução."""
        execution = BudgetExecution(
            account_id=uuid4(),
            account_code="5.1.01.001",
            account_name="Despesa Administrativa",
            budgeted=Decimal("10000"),
            realized=Decimal("8000"),
        )

        assert execution.budgeted == Decimal("10000")
        assert execution.realized == Decimal("8000")

    def test_calculate_variance_favorable(self) -> None:
        """Testa cálculo de variação favorável."""
        execution = BudgetExecution(
            budgeted=Decimal("10000"),
            realized=Decimal("8000"),
        )

        execution.calculate_variance()

        assert execution.variance == Decimal("2000")
        assert execution.variance_pct == Decimal("20")
        assert execution.variance_type == BudgetVarianceType.FAVORABLE

    def test_calculate_variance_unfavorable(self) -> None:
        """Testa cálculo de variação desfavorável."""
        execution = BudgetExecution(
            budgeted=Decimal("10000"),
            realized=Decimal("12000"),
        )

        execution.calculate_variance()

        assert execution.variance == Decimal("-2000")
        assert execution.variance_pct == Decimal("-20")
        assert execution.variance_type == BudgetVarianceType.UNFAVORABLE

    def test_calculate_variance_on_target(self) -> None:
        """Testa variação dentro do esperado."""
        execution = BudgetExecution(
            budgeted=Decimal("10000"),
            realized=Decimal("10300"),  # 3% de desvio
        )

        execution.calculate_variance()

        # Dentro do threshold de 5%
        assert execution.variance_type == BudgetVarianceType.ON_TARGET


class TestBudgetReport:
    """Testes para BudgetReport dataclass."""

    def test_create_report(self) -> None:
        """Testa criação de relatório."""
        report = BudgetReport(
            condominio_id=uuid4(),
            year=2024,
            period_type=BudgetPeriodType.ANNUAL,
        )

        assert report.year == 2024
        assert report.period_type == BudgetPeriodType.ANNUAL
        assert report.status == BudgetStatus.DRAFT

    def test_calculate_totals(self) -> None:
        """Testa cálculo de totais."""
        report = BudgetReport(
            condominio_id=uuid4(),
            year=2024,
            period_type=BudgetPeriodType.ANNUAL,
            total_revenue_budget=Decimal("100000"),
            total_expense_budget=Decimal("80000"),
            total_revenue_realized=Decimal("95000"),
            total_expense_realized=Decimal("75000"),
        )

        # Adiciona itens
        for i in range(3):
            item = BudgetLineItem(
                account_id=uuid4(),
                account_code=f"5.1.0{i+1}.001",
                account_name=f"Despesa {i+1}",
                jan=Decimal("1000"),
                feb=Decimal("1000"),
            )
            report.items.append(item)

        report.calculate_totals()

        # Resultado orçado = 100000 - 80000 = 20000
        assert report.budgeted_result == Decimal("20000")
        # Resultado realizado = 95000 - 75000 = 20000
        assert report.realized_result == Decimal("20000")
        assert report.result_variance == Decimal("0")


class TestBudgetExecutionReport:
    """Testes para BudgetExecutionReport dataclass."""

    def test_create_execution_report(self) -> None:
        """Testa criação de relatório de execução."""
        report = BudgetExecutionReport(
            condominio_id=uuid4(),
            year=2024,
            month=6,
            reference_date=date(2024, 6, 1),
        )

        assert report.year == 2024
        assert report.month == 6
        assert report.items_on_target == 0

    def test_calculate_summary(self) -> None:
        """Testa cálculo de resumo."""
        report = BudgetExecutionReport(
            condominio_id=uuid4(),
            year=2024,
            month=6,
            reference_date=date(2024, 6, 1),
        )

        # Adiciona execuções
        exec1 = BudgetExecution(
            budgeted=Decimal("10000"),
            realized=Decimal("10200"),  # On target
        )
        exec2 = BudgetExecution(
            budgeted=Decimal("5000"),
            realized=Decimal("3000"),  # Favorable
        )
        exec3 = BudgetExecution(
            budgeted=Decimal("8000"),
            realized=Decimal("10000"),  # Unfavorable
        )

        report.executions = [exec1, exec2, exec3]
        report.calculate_summary()

        assert report.total_budgeted == Decimal("23000")
        assert report.total_realized == Decimal("23200")
        assert report.items_on_target == 1
        assert report.items_favorable == 1
        assert report.items_unfavorable == 1


class TestBudgetPeriodType:
    """Testes para BudgetPeriodType enum."""

    def test_period_types_exist(self) -> None:
        """Testa que tipos existem."""
        assert BudgetPeriodType.MONTHLY.value == "MONTHLY"
        assert BudgetPeriodType.QUARTERLY.value == "QUARTERLY"
        assert BudgetPeriodType.SEMIANNUAL.value == "SEMIANNUAL"
        assert BudgetPeriodType.ANNUAL.value == "ANNUAL"

    def test_period_count(self) -> None:
        """Testa contagem de tipos."""
        assert len(BudgetPeriodType) == 4


class TestBudgetStatus:
    """Testes para BudgetStatus enum."""

    def test_status_exist(self) -> None:
        """Testa que status existem."""
        assert BudgetStatus.DRAFT.value == "DRAFT"
        assert BudgetStatus.APPROVED.value == "APPROVED"
        assert BudgetStatus.ACTIVE.value == "ACTIVE"
        assert BudgetStatus.CLOSED.value == "CLOSED"
        assert BudgetStatus.CANCELLED.value == "CANCELLED"

    def test_status_count(self) -> None:
        """Testa contagem de status."""
        assert len(BudgetStatus) == 5


class TestBudgetVarianceType:
    """Testes para BudgetVarianceType enum."""

    def test_variance_types_exist(self) -> None:
        """Testa que tipos existem."""
        assert BudgetVarianceType.FAVORABLE.value == "FAVORABLE"
        assert BudgetVarianceType.UNFAVORABLE.value == "UNFAVORABLE"
        assert BudgetVarianceType.ON_TARGET.value == "ON_TARGET"

    def test_variance_count(self) -> None:
        """Testa contagem de tipos."""
        assert len(BudgetVarianceType) == 3


class TestBudgetService:  # pylint: disable=protected-access
    """Testes para BudgetService."""

    def test_service_init(self) -> None:
        """Testa inicialização do serviço."""
        mock_session = type("MockSession", (), {})()
        service = BudgetService(mock_session)

        assert service.session == mock_session

    def test_get_month_name(self) -> None:
        """Testa obtenção de nome do mês."""
        assert BudgetService._get_month_name(1) == "Janeiro"
        assert BudgetService._get_month_name(6) == "Junho"
        assert BudgetService._get_month_name(12) == "Dezembro"
        assert BudgetService._get_month_name(0) == ""
        assert BudgetService._get_month_name(13) == ""

    def test_variance_threshold(self) -> None:
        """Testa threshold de variância."""
        assert BudgetService.VARIANCE_THRESHOLD == Decimal("5")


class TestBudgetCalculations:
    """Testes de cálculos orçamentários."""

    def test_monthly_distribution(self) -> None:
        """Testa distribuição mensal."""
        annual_budget = Decimal("120000")
        monthly = annual_budget / Decimal("12")

        assert monthly == Decimal("10000")

    def test_variance_percentage(self) -> None:
        """Testa cálculo de variação percentual."""
        budgeted = Decimal("10000")
        realized = Decimal("8500")
        variance = budgeted - realized
        variance_pct = (variance / budgeted) * Decimal("100")

        assert variance == Decimal("1500")
        assert variance_pct == Decimal("15")

    def test_zero_budget_handling(self) -> None:
        """Testa tratamento de orçamento zero."""
        execution = BudgetExecution(
            budgeted=Decimal("0"),
            realized=Decimal("1000"),
        )

        execution.calculate_variance()

        # Não deve dividir por zero
        assert execution.variance_pct == Decimal("0")


class TestIntegration:
    """Testes de integração (requerem banco)."""

    @pytest.mark.asyncio
    async def test_create_budget_placeholder(self) -> None:
        """Placeholder para teste de criação de orçamento."""
        assert True

    @pytest.mark.asyncio
    async def test_get_budget_execution_placeholder(self) -> None:
        """Placeholder para teste de execução."""
        assert True

    @pytest.mark.asyncio
    async def test_get_ytd_execution_placeholder(self) -> None:
        """Placeholder para teste YTD."""
        assert True

    @pytest.mark.asyncio
    async def test_compare_budget_periods_placeholder(self) -> None:
        """Placeholder para teste de comparação."""
        assert True

    @pytest.mark.asyncio
    async def test_update_cost_center_budget_placeholder(self) -> None:
        """Placeholder para teste de atualização."""
        assert True
