"""Testes para BalanceSheetService - Sprint 29.

Testa funcionalidades de Balancete e Balanço Patrimonial.
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.models.accounting_account import AccountNature, AccountType
from modules.financial.services.balance_sheet_service import (
    AccountBalance,
    BalanceSheetGroup,
    BalanceSheetGroupType,
    BalanceSheetReport,
    BalanceSheetService,
    TrialBalanceReport,
    TrialBalanceType,
)


class TestAccountBalance:
    """Testes para AccountBalance dataclass."""

    def test_create_account_balance(self) -> None:
        """Testa criação de AccountBalance."""
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
        )

        assert balance.account_code == "1.1.01.001"
        assert balance.account_name == "Caixa"
        assert balance.account_type == AccountType.CHECKING
        assert balance.account_nature == AccountNature.DEBIT
        assert balance.is_analytical is True
        assert balance.current_balance == Decimal("0")

    def test_calculate_balance_debit_nature(self) -> None:
        """Testa cálculo de saldo para conta de natureza devedora."""
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            previous_debit=Decimal("1000.00"),
            previous_credit=Decimal("200.00"),
            period_debit=Decimal("500.00"),
            period_credit=Decimal("100.00"),
        )

        balance.calculate_balance()

        # Saldo anterior: 1000 - 200 = 800
        assert balance.previous_balance == Decimal("800.00")
        # Saldo atual: (1000 + 500) - (200 + 100) = 1200
        assert balance.current_balance == Decimal("1200.00")

    def test_calculate_balance_credit_nature(self) -> None:
        """Testa cálculo de saldo para conta de natureza credora."""
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="2.1.01.001",
            account_name="Fornecedores",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.CREDIT,
            level=4,
            is_analytical=True,
            previous_debit=Decimal("200.00"),
            previous_credit=Decimal("1000.00"),
            period_debit=Decimal("100.00"),
            period_credit=Decimal("500.00"),
        )

        balance.calculate_balance()

        # Saldo anterior: 1000 - 200 = 800
        assert balance.previous_balance == Decimal("800.00")
        # Saldo atual: (1000 + 500) - (200 + 100) = 1200
        assert balance.current_balance == Decimal("1200.00")

    def test_calculate_variation(self) -> None:
        """Testa cálculo de variação."""
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            previous_debit=Decimal("1000.00"),
            previous_credit=Decimal("0"),
            period_debit=Decimal("500.00"),
            period_credit=Decimal("0"),
        )

        balance.calculate_balance()

        # Variação: 1500 - 1000 = 500 (50%)
        assert balance.variation_absolute == Decimal("500.00")
        assert balance.variation_percentage == Decimal("50.00")

    def test_variation_from_zero(self) -> None:
        """Testa variação quando saldo anterior é zero."""
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            previous_debit=Decimal("0"),
            previous_credit=Decimal("0"),
            period_debit=Decimal("1000.00"),
            period_credit=Decimal("0"),
        )

        balance.calculate_balance()

        # Sem variação percentual quando anterior é zero
        assert balance.variation_percentage == Decimal("0")


class TestTrialBalanceReport:
    """Testes para TrialBalanceReport dataclass."""

    def test_create_trial_balance(self) -> None:
        """Testa criação de balancete."""
        report = TrialBalanceReport(
            condominio_id=uuid4(),
            report_date=date(2024, 12, 31),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            balance_type=TrialBalanceType.VERIFICATION,
        )

        assert report.report_date == date(2024, 12, 31)
        assert report.balance_type == TrialBalanceType.VERIFICATION
        assert report.total_accounts == 0
        assert report.is_balanced is True

    def test_calculate_totals(self) -> None:
        """Testa cálculo de totais do balancete."""
        report = TrialBalanceReport(
            condominio_id=uuid4(),
            report_date=date(2024, 12, 31),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            balance_type=TrialBalanceType.VERIFICATION,
        )

        # Adiciona contas
        for i in range(3):
            balance = AccountBalance(
                account_id=uuid4(),
                account_code=f"1.1.01.00{i + 1}",
                account_name=f"Conta {i + 1}",
                account_type=AccountType.CHECKING,
                account_nature=AccountNature.DEBIT,
                level=4,
                is_analytical=True,
                current_debit=Decimal("1000.00"),
                current_credit=Decimal("1000.00"),
            )
            report.items.append(balance)

        report.calculate_totals()

        assert report.total_accounts == 3
        assert report.total_analytical == 3
        assert report.total_current_debit == Decimal("3000.00")
        assert report.total_current_credit == Decimal("3000.00")
        assert report.is_balanced is True
        assert report.difference == Decimal("0")

    def test_unbalanced_report(self) -> None:
        """Testa balancete não balanceado."""
        report = TrialBalanceReport(
            condominio_id=uuid4(),
            report_date=date(2024, 12, 31),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            balance_type=TrialBalanceType.VERIFICATION,
        )

        # Conta com diferença
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            current_debit=Decimal("1000.00"),
            current_credit=Decimal("900.00"),  # Diferença de 100
        )
        report.items.append(balance)

        report.calculate_totals()

        assert report.is_balanced is False
        assert report.difference == Decimal("100.00")


class TestBalanceSheetGroup:
    """Testes para BalanceSheetGroup dataclass."""

    def test_create_group(self) -> None:
        """Testa criação de grupo do balanço."""
        group = BalanceSheetGroup(
            group_type=BalanceSheetGroupType.ATIVO_CIRCULANTE,
            name="Ativo Circulante",
        )

        assert group.group_type == BalanceSheetGroupType.ATIVO_CIRCULANTE
        assert group.name == "Ativo Circulante"
        assert group.total == Decimal("0")

    def test_calculate_total(self) -> None:
        """Testa cálculo de total do grupo."""
        group = BalanceSheetGroup(
            group_type=BalanceSheetGroupType.ATIVO_CIRCULANTE,
            name="Ativo Circulante",
        )

        # Adiciona contas
        for i in range(3):
            balance = AccountBalance(
                account_id=uuid4(),
                account_code=f"1.1.01.00{i + 1}",
                account_name=f"Conta {i + 1}",
                account_type=AccountType.CHECKING,
                account_nature=AccountNature.DEBIT,
                level=4,
                is_analytical=True,
                current_balance=Decimal("1000.00"),
            )
            group.items.append(balance)

        group.calculate_total()

        assert group.total == Decimal("3000.00")


class TestBalanceSheetReport:
    """Testes para BalanceSheetReport dataclass."""

    def test_create_balance_sheet(self) -> None:
        """Testa criação de balanço patrimonial."""
        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        assert report.reference_date == date(2024, 12, 31)
        assert report.total_ativo == Decimal("0")
        assert report.total_passivo == Decimal("0")
        assert report.total_patrimonio == Decimal("0")
        assert report.is_balanced is True

    def test_calculate_totals(self) -> None:
        """Testa cálculo de totais do balanço."""
        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        # Adiciona ativo circulante
        asset_balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("10000.00"),
        )
        report.ativo_circulante.items.append(asset_balance)

        # Adiciona passivo circulante
        liability_balance = AccountBalance(
            account_id=uuid4(),
            account_code="2.1.01.001",
            account_name="Fornecedores",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.CREDIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("3000.00"),
        )
        report.passivo_circulante.items.append(liability_balance)

        # Adiciona patrimônio líquido
        equity_balance = AccountBalance(
            account_id=uuid4(),
            account_code="3.1.01.001",
            account_name="Capital Social",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.CREDIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("7000.00"),
        )
        report.patrimonio_liquido.items.append(equity_balance)

        report.calculate_totals()

        assert report.total_ativo == Decimal("10000.00")
        assert report.total_passivo == Decimal("3000.00")
        assert report.total_patrimonio == Decimal("7000.00")
        assert report.total_passivo_patrimonio == Decimal("10000.00")
        assert report.is_balanced is True

    def test_unbalanced_balance_sheet(self) -> None:
        """Testa balanço não balanceado."""
        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        # Adiciona apenas ativo
        asset_balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("10000.00"),
        )
        report.ativo_circulante.items.append(asset_balance)

        report.calculate_totals()

        assert report.total_ativo == Decimal("10000.00")
        assert report.total_passivo_patrimonio == Decimal("0")
        assert report.is_balanced is False
        assert report.difference == Decimal("10000.00")

    def test_vertical_analysis(self) -> None:
        """Testa análise vertical do balanço."""
        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        # Adiciona ativos
        circulante = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("6000.00"),
        )
        report.ativo_circulante.items.append(circulante)

        nao_circulante = AccountBalance(
            account_id=uuid4(),
            account_code="1.2.01.001",
            account_name="Imóveis",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("4000.00"),
        )
        report.ativo_nao_circulante.items.append(nao_circulante)

        report.calculate_totals()

        # Ativo circulante = 60%, não circulante = 40%
        assert report.ativo_circulante.percentage == Decimal("60")
        assert report.ativo_nao_circulante.percentage == Decimal("40")


class TestTrialBalanceType:
    """Testes para TrialBalanceType enum."""

    def test_types_exist(self) -> None:
        """Testa que tipos existem."""
        assert TrialBalanceType.VERIFICATION.value == "VERIFICATION"
        assert TrialBalanceType.ANALYTICAL.value == "ANALYTICAL"
        assert TrialBalanceType.SYNTHETIC.value == "SYNTHETIC"

    def test_type_count(self) -> None:
        """Testa contagem de tipos."""
        assert len(TrialBalanceType) == 3


class TestBalanceSheetGroupType:
    """Testes para BalanceSheetGroupType enum."""

    def test_groups_exist(self) -> None:
        """Testa que grupos existem."""
        assert BalanceSheetGroupType.ATIVO_CIRCULANTE.value == "ATIVO_CIRCULANTE"
        assert BalanceSheetGroupType.ATIVO_NAO_CIRCULANTE.value == "ATIVO_NAO_CIRCULANTE"
        assert BalanceSheetGroupType.PASSIVO_CIRCULANTE.value == "PASSIVO_CIRCULANTE"
        assert BalanceSheetGroupType.PASSIVO_NAO_CIRCULANTE.value == "PASSIVO_NAO_CIRCULANTE"
        assert BalanceSheetGroupType.PATRIMONIO_LIQUIDO.value == "PATRIMONIO_LIQUIDO"

    def test_group_count(self) -> None:
        """Testa contagem de grupos."""
        assert len(BalanceSheetGroupType) == 5


class TestBalanceSheetService:  # pylint: disable=protected-access
    """Testes para BalanceSheetService."""

    def test_service_init(self) -> None:
        """Testa inicialização do serviço."""
        # Mock session
        mock_session = type("MockSession", (), {})()
        service = BalanceSheetService(mock_session)

        assert service.session == mock_session

    def test_calc_variation_pct(self) -> None:
        """Testa cálculo de variação percentual."""
        mock_session = type("MockSession", (), {})()
        service = BalanceSheetService(mock_session)

        # Aumento de 100%
        result = service._calc_variation_pct(Decimal("200"), Decimal("100"))
        assert result == Decimal("100")

        # Redução de 50%
        result = service._calc_variation_pct(Decimal("50"), Decimal("100"))
        assert result == Decimal("-50")

        # Sem base (divisão por zero evitada)
        result = service._calc_variation_pct(Decimal("100"), Decimal("0"))
        assert result == Decimal("0")

    def test_classify_account_asset(self) -> None:
        """Testa classificação de conta de ativo."""
        mock_session = type("MockSession", (), {})()
        service = BalanceSheetService(mock_session)

        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        # Conta de ativo circulante (código começa com 1.1)
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="1.1.01.001",
            account_name="Caixa",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.DEBIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("1000.00"),
        )

        service._classify_account_in_balance_sheet(report, balance)

        assert len(report.ativo_circulante.items) == 1
        assert len(report.ativo_nao_circulante.items) == 0

    def test_classify_account_liability(self) -> None:
        """Testa classificação de conta de passivo."""
        mock_session = type("MockSession", (), {})()
        service = BalanceSheetService(mock_session)

        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        # Conta de passivo circulante (código começa com 2.1)
        balance = AccountBalance(
            account_id=uuid4(),
            account_code="2.1.01.001",
            account_name="Fornecedores",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.CREDIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("1000.00"),
        )

        service._classify_account_in_balance_sheet(report, balance)

        assert len(report.passivo_circulante.items) == 1
        assert len(report.passivo_nao_circulante.items) == 0

    def test_classify_account_equity(self) -> None:
        """Testa classificação de conta de PL."""
        mock_session = type("MockSession", (), {})()
        service = BalanceSheetService(mock_session)

        report = BalanceSheetReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 12, 31),
        )

        balance = AccountBalance(
            account_id=uuid4(),
            account_code="3.1.01.001",
            account_name="Capital Social",
            account_type=AccountType.CHECKING,
            account_nature=AccountNature.CREDIT,
            level=4,
            is_analytical=True,
            current_balance=Decimal("1000.00"),
        )

        service._classify_account_in_balance_sheet(report, balance)

        assert len(report.patrimonio_liquido.items) == 1


class TestIntegration:
    """Testes de integração (requerem banco)."""

    @pytest.mark.asyncio
    async def test_generate_trial_balance_placeholder(self) -> None:
        """Placeholder para teste de geração de balancete."""
        # Este teste requer banco de dados configurado
        # Em ambiente de teste completo, usar fixtures de banco
        assert True

    @pytest.mark.asyncio
    async def test_generate_balance_sheet_placeholder(self) -> None:
        """Placeholder para teste de geração de balanço."""
        assert True

    @pytest.mark.asyncio
    async def test_validate_balance_placeholder(self) -> None:
        """Placeholder para teste de validação."""
        assert True
