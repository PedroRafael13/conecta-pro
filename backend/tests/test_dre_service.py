"""Testes do DREService.

Testa geracao de DRE e calculos contabeis.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from modules.financial.models.accounting_account import AccountingAccount, AccountType
from modules.financial.services.dre_service import (
    DREGroupType,
    DRELineItem,
    DREPeriodType,
    DREReport,
    DREService,
)


class TestDRELineItem:
    """Testes da classe DRELineItem."""

    def test_line_item_default_values(self) -> None:
        """Testa valores default."""
        line = DRELineItem()

        assert line.account_id is None
        assert line.account_code == ""
        assert line.current_value == Decimal("0")
        assert line.is_total is False

    def test_line_item_with_values(self) -> None:
        """Testa criacao com valores."""
        line = DRELineItem(
            account_code="3.1.01",
            account_name="Receita de Servicos",
            group_type=DREGroupType.RECEITA_BRUTA,
            current_value=Decimal("10000.00"),
            previous_value=Decimal("8000.00"),
        )

        assert line.account_code == "3.1.01"
        assert line.current_value == Decimal("10000.00")
        assert line.group_type == DREGroupType.RECEITA_BRUTA

    def test_line_item_to_dict(self) -> None:
        """Testa conversao para dicionario."""
        line = DRELineItem(
            account_code="3.1.01",
            account_name="Receita",
            current_value=Decimal("5000.00"),
            variation_percent=Decimal("10.5"),
        )

        result = line.to_dict()

        assert result["account_code"] == "3.1.01"
        assert result["current_value"] == 5000.00
        assert result["variation_percent"] == 10.5

    def test_line_item_cost_center_breakdown(self) -> None:
        """Testa breakdown por centro de custo."""
        line = DRELineItem(
            account_code="4.1.01",
            cost_center_breakdown={
                "CC01": Decimal("3000.00"),
                "CC02": Decimal("2000.00"),
            },
        )

        result = line.to_dict()

        assert result["cost_center_breakdown"]["CC01"] == 3000.00
        assert result["cost_center_breakdown"]["CC02"] == 2000.00


class TestDREReport:
    """Testes da classe DREReport."""

    def test_report_creation(self) -> None:
        """Testa criacao de relatorio."""
        condominio_id = uuid4()
        report = DREReport(
            condominio_id=condominio_id,
            period_type=DREPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert report.condominio_id == condominio_id
        assert report.period_type == DREPeriodType.MONTHLY

    def test_report_to_dict(self) -> None:
        """Testa conversao para dicionario."""
        report = DREReport(
            condominio_id=uuid4(),
            period_type=DREPeriodType.ANNUAL,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            totals={"lucro_liquido": Decimal("50000.00")},
        )

        result = report.to_dict()

        assert result["period_type"] == "annual"
        assert result["totals"]["lucro_liquido"] == 50000.00

    def test_report_with_lines(self) -> None:
        """Testa relatorio com linhas."""
        line = DRELineItem(
            account_name="Receita",
            current_value=Decimal("10000.00"),
        )

        report = DREReport(
            condominio_id=uuid4(),
            period_type=DREPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            lines=[line],
        )

        result = report.to_dict()

        assert len(result["lines"]) == 1
        assert result["lines"][0]["current_value"] == 10000.00


class TestDREPeriodType:
    """Testes dos tipos de periodo."""

    def test_monthly_period(self) -> None:
        """Testa periodo mensal."""
        assert DREPeriodType.MONTHLY.value == "monthly"

    def test_quarterly_period(self) -> None:
        """Testa periodo trimestral."""
        assert DREPeriodType.QUARTERLY.value == "quarterly"

    def test_annual_period(self) -> None:
        """Testa periodo anual."""
        assert DREPeriodType.ANNUAL.value == "annual"


class TestDREGroupType:
    """Testes dos tipos de grupo."""

    def test_receita_bruta(self) -> None:
        """Testa grupo receita bruta."""
        assert DREGroupType.RECEITA_BRUTA.value == "receita_bruta"

    def test_lucro_liquido(self) -> None:
        """Testa grupo lucro liquido."""
        assert DREGroupType.LUCRO_LIQUIDO.value == "lucro_liquido"

    def test_despesas_operacionais(self) -> None:
        """Testa grupo despesas operacionais."""
        assert DREGroupType.DESPESAS_OPERACIONAIS.value == "despesas_operacionais"


class TestDREServiceBasic:
    """Testes basicos do DREService."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        session = MagicMock()
        session.execute = AsyncMock()
        return session

    def test_service_creation(self, mock_session: MagicMock) -> None:
        """Testa criacao do servico."""
        service = DREService(mock_session)

        assert service is not None
        assert service.session is mock_session

    def test_determine_period_monthly(self, mock_session: MagicMock) -> None:
        """Testa determinacao de periodo mensal."""
        service = DREService(mock_session)

        result = service._determine_period_type(  # pylint: disable=protected-access
            date(2024, 1, 1),
            date(2024, 1, 31),
        )

        assert result == DREPeriodType.MONTHLY

    def test_determine_period_quarterly(self, mock_session: MagicMock) -> None:
        """Testa determinacao de periodo trimestral."""
        service = DREService(mock_session)

        result = service._determine_period_type(  # pylint: disable=protected-access
            date(2024, 1, 1),
            date(2024, 3, 31),
        )

        assert result == DREPeriodType.QUARTERLY

    def test_determine_period_annual(self, mock_session: MagicMock) -> None:
        """Testa determinacao de periodo anual."""
        service = DREService(mock_session)

        result = service._determine_period_type(  # pylint: disable=protected-access
            date(2024, 1, 1),
            date(2024, 12, 31),
        )

        assert result == DREPeriodType.ANNUAL


class TestDREServiceCalculations:
    """Testes de calculos do DRE."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        session = MagicMock()
        session.execute = AsyncMock()
        return session

    def test_calculate_totals_basic(self, mock_session: MagicMock) -> None:
        """Testa calculo de totais basico."""
        service = DREService(mock_session)

        lines = [
            DRELineItem(
                account_name="RECEITA BRUTA",
                group_type=DREGroupType.RECEITA_BRUTA,
                is_total=True,
            ),
            DRELineItem(
                account_code="3.1.01",
                account_name="Receita de Servicos",
                group_type=DREGroupType.RECEITA_BRUTA,
                current_value=Decimal("10000.00"),
            ),
            DRELineItem(
                account_name="CUSTOS",
                group_type=DREGroupType.CUSTO_PRODUTOS,
                is_total=True,
            ),
            DRELineItem(
                account_code="4.1.01",
                account_name="Custo de Servicos",
                group_type=DREGroupType.CUSTO_PRODUTOS,
                current_value=Decimal("3000.00"),
            ),
            DRELineItem(
                account_name="DESPESAS",
                group_type=DREGroupType.DESPESAS_OPERACIONAIS,
                is_total=True,
            ),
            DRELineItem(
                account_code="5.1.01",
                account_name="Despesas Administrativas",
                group_type=DREGroupType.DESPESAS_OPERACIONAIS,
                current_value=Decimal("2000.00"),
            ),
            DRELineItem(
                account_name="LUCRO BRUTO",
                group_type=DREGroupType.LUCRO_BRUTO,
                is_total=True,
            ),
            DRELineItem(
                account_name="LUCRO LIQUIDO",
                group_type=DREGroupType.LUCRO_LIQUIDO,
                is_total=True,
            ),
        ]

        totals = service._calculate_totals(lines)  # pylint: disable=protected-access

        assert totals["receita_bruta"] == Decimal("10000.00")
        assert totals["custos"] == Decimal("3000.00")
        assert totals["despesas"] == Decimal("2000.00")
        assert totals["lucro_bruto"] == Decimal("7000.00")  # 10000 - 3000
        assert totals["lucro_liquido"] == Decimal("5000.00")  # 7000 - 2000

    def test_calculate_totals_with_deductions(self, mock_session: MagicMock) -> None:
        """Testa calculo com deducoes."""
        service = DREService(mock_session)

        lines = [
            DRELineItem(
                account_name="RECEITA BRUTA",
                group_type=DREGroupType.RECEITA_BRUTA,
                is_total=True,
            ),
            DRELineItem(
                account_code="3.1.01",
                group_type=DREGroupType.RECEITA_BRUTA,
                current_value=Decimal("10000.00"),
            ),
            DRELineItem(
                account_name="DEDUCOES",
                group_type=DREGroupType.DEDUCOES,
                is_total=True,
            ),
            DRELineItem(
                account_code="3.2.01",
                group_type=DREGroupType.DEDUCOES,
                current_value=Decimal("500.00"),
            ),
            DRELineItem(
                account_name="LUCRO BRUTO",
                group_type=DREGroupType.LUCRO_BRUTO,
                is_total=True,
            ),
            DRELineItem(
                account_name="LUCRO LIQUIDO",
                group_type=DREGroupType.LUCRO_LIQUIDO,
                is_total=True,
            ),
        ]

        totals = service._calculate_totals(lines)  # pylint: disable=protected-access

        assert totals["receita_bruta"] == Decimal("10000.00")
        assert totals["deducoes"] == Decimal("500.00")
        assert totals["receita_liquida"] == Decimal("9500.00")

    def test_calculate_analysis(self, mock_session: MagicMock) -> None:
        """Testa calculo de analises."""
        service = DREService(mock_session)

        lines = [
            DRELineItem(
                account_name="Receita",
                current_value=Decimal("5000.00"),
                previous_value=Decimal("4000.00"),
            ),
        ]

        totals = {"receita_liquida": Decimal("10000.00")}

        service._calculate_analysis(lines, totals)  # pylint: disable=protected-access

        # AV = 5000 / 10000 * 100 = 50%
        assert lines[0].av_percent == Decimal("50.00")
        # Variacao = 5000 - 4000 = 1000
        assert lines[0].variation_value == Decimal("1000.00")
        # Variacao % = 1000 / 4000 * 100 = 25%
        assert lines[0].variation_percent == Decimal("25.00")


class TestDREServiceBuildLines:
    """Testes de construcao de linhas do DRE."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        session = MagicMock()
        session.execute = AsyncMock()
        return session

    def test_build_lines_empty(self, mock_session: MagicMock) -> None:
        """Testa construcao sem contas."""
        service = DREService(mock_session)

        lines = service._build_dre_lines(  # pylint: disable=protected-access
            accounts=[],
            current_balances={},
            previous_balances={},
            cost_center_breakdown={},
        )

        # Deve ter apenas as linhas de total
        total_lines = [line for line in lines if line.is_total]
        assert len(total_lines) >= 4  # Receita, Custos, Despesas, Lucro

    def test_build_lines_with_revenue(self, mock_session: MagicMock) -> None:
        """Testa construcao com receitas."""
        service = DREService(mock_session)

        account_id = uuid4()
        account = MagicMock(spec=AccountingAccount)
        account.id = account_id
        account.code = "3.1.01"
        account.name = "Receita de Servicos"
        account.account_type = AccountType.CHECKING
        account.dre_group = None

        lines = service._build_dre_lines(  # pylint: disable=protected-access
            accounts=[account],
            current_balances={account_id: Decimal("10000.00")},
            previous_balances={account_id: Decimal("8000.00")},
            cost_center_breakdown={},
        )

        revenue_lines = [line for line in lines if line.group_type == DREGroupType.RECEITA_BRUTA and not line.is_total]
        assert len(revenue_lines) == 1
        assert revenue_lines[0].current_value == Decimal("10000.00")
        assert revenue_lines[0].previous_value == Decimal("8000.00")


class TestDREServiceAsync:
    """Testes asincronos do DREService."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        session = MagicMock()
        session.execute = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_get_result_accounts(self, mock_session: MagicMock) -> None:
        """Testa busca de contas de resultado."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        service = DREService(mock_session)
        accounts = await service._get_result_accounts(  # pylint: disable=protected-access
            condominio_id=uuid4()
        )

        assert accounts == []
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_period_balances(self, mock_session: MagicMock) -> None:
        """Testa busca de saldos do periodo."""
        mock_session.execute.return_value = iter([])

        service = DREService(mock_session)
        balances = await service._get_period_balances(  # pylint: disable=protected-access
            condominio_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert balances == {}

    @pytest.mark.asyncio
    async def test_get_cost_centers(self, mock_session: MagicMock) -> None:
        """Testa busca de centros de custo."""
        mock_session.execute.return_value = iter([])

        service = DREService(mock_session)
        cost_centers = await service._get_cost_centers(  # pylint: disable=protected-access
            condominio_id=uuid4()
        )

        assert cost_centers == []

    @pytest.mark.asyncio
    async def test_generate_dre_complete(self, mock_session: MagicMock) -> None:
        """Testa geracao completa do DRE."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        service = DREService(mock_session)

        report = await service.generate_dre(
            condominio_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            include_previous=False,
        )

        assert isinstance(report, DREReport)
        assert report.period_type == DREPeriodType.MONTHLY


class TestDREServiceComparison:
    """Testes de comparativos."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        session = MagicMock()
        session.execute = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_get_monthly_comparison(self, mock_session: MagicMock) -> None:
        """Testa comparativo mensal."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        service = DREService(mock_session)

        comparison = await service.get_monthly_comparison(
            condominio_id=uuid4(),
            year=2024,
            months=3,
        )

        assert "months" in comparison
        assert len(comparison["months"]) == 3
        assert "2024-01" in comparison["months"]
        assert "2024-02" in comparison["months"]
        assert "2024-03" in comparison["months"]

    @pytest.mark.asyncio
    async def test_get_cost_center_dre(self, mock_session: MagicMock) -> None:
        """Testa DRE por centro de custo."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        service = DREService(mock_session)

        report = await service.get_cost_center_dre(
            condominio_id=uuid4(),
            cost_center_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert isinstance(report, DREReport)
