"""Testes do CashFlowBankingService.

Testa integracao do fluxo de caixa com Open Banking.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.financial.services.cashflow_banking_service import (
    BankAccountConfig,
    CashFlowBankingService,
    CashFlowWithBalance,
    ConsolidatedBalance,
)
from modules.financial.services.cashflow_service import CashFlowProjection
from modules.integrations.banking import (
    AccountBalance,
    BankCredentials,
    BankingAdapterError,
    BankingService,
)


class TestConsolidatedBalance:
    """Testes da classe ConsolidatedBalance."""

    def test_consolidated_balance_default(self) -> None:
        """Testa criacao com valores default."""
        balance = ConsolidatedBalance()

        assert balance.total_available == Decimal("0")
        assert balance.total_blocked == Decimal("0")
        assert balance.total_balance == Decimal("0")
        assert balance.accounts == {}
        assert balance.errors == {}

    def test_consolidated_balance_to_dict(self) -> None:
        """Testa conversao para dicionario."""
        account_balance = AccountBalance(
            available=Decimal("1000.00"),
            blocked=Decimal("100.00"),
            total=Decimal("1100.00"),
        )

        balance = ConsolidatedBalance(
            total_available=Decimal("1000.00"),
            total_blocked=Decimal("100.00"),
            total_balance=Decimal("1100.00"),
            accounts={"conta_bb": account_balance},
        )

        result = balance.to_dict()

        assert result["total_available"] == 1000.00
        assert result["total_blocked"] == 100.00
        assert "conta_bb" in result["accounts"]
        assert result["accounts"]["conta_bb"]["available"] == 1000.00


class TestCashFlowWithBalance:
    """Testes da classe CashFlowWithBalance."""

    def test_cashflow_with_balance_to_dict(self) -> None:
        """Testa conversao para dicionario."""
        balance = ConsolidatedBalance(
            total_available=Decimal("5000.00"),
            total_balance=Decimal("5000.00"),
        )

        projection = CashFlowProjection(
            date=date.today(),
            payables=Decimal("1000.00"),
            balance=Decimal("-1000.00"),
        )

        cashflow = CashFlowWithBalance(
            current_balance=balance,
            projections=[projection],
            alerts=[{"type": "LOW_BALANCE"}],
        )

        result = cashflow.to_dict()

        assert result["current_balance"]["total_available"] == 5000.00
        assert len(result["projections"]) == 1
        assert len(result["alerts"]) == 1

    def test_cashflow_with_balance_empty_projections(self) -> None:
        """Testa com lista vazia de projecoes."""
        balance = ConsolidatedBalance(total_available=Decimal("10000.00"))

        cashflow = CashFlowWithBalance(
            current_balance=balance,
            projections=[],
            alerts=[],
        )

        result = cashflow.to_dict()

        assert result["projections"] == []
        assert result["alerts"] == []


class TestBankAccountConfig:
    """Testes da classe BankAccountConfig."""

    def test_bank_account_config_creation(self) -> None:
        """Testa criacao de configuracao."""
        credentials = BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
            agency="1234",
            account="56789-0",
        )

        config = BankAccountConfig(
            account_id="conta_bb",
            bank_code="001",
            credentials=credentials,
            is_primary=True,
        )

        assert config.account_id == "conta_bb"
        assert config.bank_code == "001"
        assert config.is_primary is True

    def test_bank_account_config_default_primary(self) -> None:
        """Testa valor default de is_primary."""
        credentials = BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
        )

        config = BankAccountConfig(
            account_id="conta_itau",
            bank_code="341",
            credentials=credentials,
        )

        assert config.is_primary is False


class TestCashFlowBankingServiceBasic:
    """Testes basicos do CashFlowBankingService."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        return MagicMock(spec=BankingService)

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture para credenciais."""
        return BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
            agency="1234",
            account="56789-0",
        )

    def test_service_creation(
        self, mock_session: MagicMock, mock_banking_service: MagicMock
    ) -> None:
        """Testa criacao do servico."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        assert service is not None
        assert service.banking_service is mock_banking_service

    def test_register_bank_account(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa registro de conta bancaria."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        service.register_bank_account(
            account_id="conta_bb",
            bank_code="001",
            credentials=credentials,
            is_primary=True,
        )

        assert "conta_bb" in service._account_configs  # pylint: disable=protected-access
        mock_banking_service.register_account.assert_called_once()

    def test_unregister_bank_account(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa remocao de conta bancaria."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        service.register_bank_account(
            account_id="conta_bb",
            bank_code="001",
            credentials=credentials,
        )

        service.unregister_bank_account("conta_bb")

        configs = service._account_configs  # pylint: disable=protected-access
        assert "conta_bb" not in configs
        mock_banking_service.unregister_account.assert_called_once()


class TestCashFlowBankingServiceBalance:
    """Testes de consulta de saldo consolidado."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        mock = MagicMock(spec=BankingService)
        mock.get_balance = AsyncMock()
        mock.close_all = AsyncMock()
        return mock

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture para credenciais."""
        return BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
            agency="1234",
            account="56789-0",
        )

    @pytest.mark.asyncio
    async def test_get_consolidated_balance_single_account(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa saldo consolidado com uma conta."""
        mock_banking_service.get_balance.return_value = AccountBalance(
            available=Decimal("10000.00"),
            blocked=Decimal("500.00"),
            total=Decimal("10500.00"),
        )

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )
        service.register_bank_account("conta_bb", "001", credentials)

        balance = await service.get_consolidated_balance()

        assert balance.total_available == Decimal("10000.00")
        assert balance.total_blocked == Decimal("500.00")
        assert "conta_bb" in balance.accounts

    @pytest.mark.asyncio
    async def test_get_consolidated_balance_multiple_accounts(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa saldo consolidado com multiplas contas."""
        mock_banking_service.get_balance.side_effect = [
            AccountBalance(
                available=Decimal("10000.00"),
                blocked=Decimal("0"),
                total=Decimal("10000.00"),
            ),
            AccountBalance(
                available=Decimal("5000.00"),
                blocked=Decimal("1000.00"),
                total=Decimal("6000.00"),
            ),
        ]

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )
        service.register_bank_account("conta_bb", "001", credentials)
        service.register_bank_account("conta_itau", "341", credentials)

        balance = await service.get_consolidated_balance()

        assert balance.total_available == Decimal("15000.00")
        assert balance.total_blocked == Decimal("1000.00")
        assert len(balance.accounts) == 2

    @pytest.mark.asyncio
    async def test_get_consolidated_balance_with_error(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa saldo consolidado com erro em uma conta."""
        mock_banking_service.get_balance.side_effect = [
            AccountBalance(
                available=Decimal("10000.00"),
                blocked=Decimal("0"),
                total=Decimal("10000.00"),
            ),
            BankingAdapterError("Erro de conexao"),
        ]

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )
        service.register_bank_account("conta_bb", "001", credentials)
        service.register_bank_account("conta_itau", "341", credentials)

        balance = await service.get_consolidated_balance()

        assert balance.total_available == Decimal("10000.00")
        assert len(balance.accounts) == 1
        assert "conta_itau" in balance.errors


class TestCashFlowBankingServiceAlerts:
    """Testes de geracao de alertas."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        mock = MagicMock(spec=BankingService)
        mock.get_balance = AsyncMock()
        return mock

    def test_generate_alerts_low_balance(
        self, mock_session: MagicMock, mock_banking_service: MagicMock
    ) -> None:
        """Testa alerta de saldo baixo."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        current_balance = ConsolidatedBalance(
            total_available=Decimal("8000.00"),  # Abaixo do threshold de 10000
        )

        alerts = service._generate_alerts(  # pylint: disable=protected-access
            current_balance=current_balance,
            projections=[],
            threshold=Decimal("10000.00"),
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == "LOW_BALANCE"
        assert alerts[0]["severity"] == "warning"

    def test_generate_alerts_critical_balance(
        self, mock_session: MagicMock, mock_banking_service: MagicMock
    ) -> None:
        """Testa alerta de saldo critico."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        current_balance = ConsolidatedBalance(
            total_available=Decimal("3000.00"),  # Abaixo do critico (5000)
        )

        alerts = service._generate_alerts(  # pylint: disable=protected-access
            current_balance=current_balance,
            projections=[],
            threshold=Decimal("10000.00"),
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == "CRITICAL_BALANCE"
        assert alerts[0]["severity"] == "critical"

    def test_generate_alerts_projected_low(
        self, mock_session: MagicMock, mock_banking_service: MagicMock
    ) -> None:
        """Testa alerta de saldo projetado baixo."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        current_balance = ConsolidatedBalance(
            total_available=Decimal("20000.00"),  # Saldo atual OK
        )

        projection = CashFlowProjection(
            date=date.today(),
        )
        projection.cumulative_balance = Decimal("8000.00")  # Projetado baixo

        alerts = service._generate_alerts(  # pylint: disable=protected-access
            current_balance=current_balance,
            projections=[projection],
            threshold=Decimal("10000.00"),
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == "PROJECTED_LOW"

    def test_generate_alerts_connection_error(
        self, mock_session: MagicMock, mock_banking_service: MagicMock
    ) -> None:
        """Testa alerta de erro de conexao."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        current_balance = ConsolidatedBalance(
            total_available=Decimal("20000.00"),
            errors={"conta_bb": "Timeout ao conectar"},
        )

        alerts = service._generate_alerts(  # pylint: disable=protected-access
            current_balance=current_balance,
            projections=[],
            threshold=Decimal("10000.00"),
        )

        assert len(alerts) == 1
        assert alerts[0]["type"] == "CONNECTION_ERROR"
        assert "conta_bb" in alerts[0]["account_id"]


class TestCashFlowBankingServiceProjection:
    """Testes de projecao com saldo real."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        mock = MagicMock(spec=BankingService)
        mock.get_balance = AsyncMock()
        return mock

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture para credenciais."""
        return BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
        )

    @pytest.mark.asyncio
    async def test_get_projection_with_balance(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa projecao com saldo real."""
        mock_banking_service.get_balance.return_value = AccountBalance(
            available=Decimal("50000.00"),
            blocked=Decimal("0"),
            total=Decimal("50000.00"),
        )

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )
        service.register_bank_account("conta_bb", "001", credentials)

        # Mock do cashflow_service
        mock_projections = [
            CashFlowProjection(
                date=date.today(),
                payables=Decimal("10000.00"),
                balance=Decimal("-10000.00"),
            ),
        ]

        with patch.object(
            service.cashflow_service, "get_projection", new_callable=AsyncMock
        ) as mock_cf:
            mock_cf.return_value = mock_projections

            result = await service.get_projection_with_balance(
                condominio_id=uuid4(),
            )

            assert isinstance(result, CashFlowWithBalance)
            assert result.current_balance.total_available == Decimal("50000.00")
            # Saldo acumulado = 50000 - 10000 = 40000
            assert result.projections[0].cumulative_balance == Decimal("40000.00")


class TestCashFlowBankingServiceInvestment:
    """Testes de sugestoes de investimento."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        mock = MagicMock(spec=BankingService)
        mock.get_balance = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_investment_suggestions_no_surplus(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
    ) -> None:
        """Testa sugestoes sem excesso de saldo."""
        mock_banking_service.get_balance.return_value = AccountBalance(
            available=Decimal("5000.00"),
            blocked=Decimal("0"),
            total=Decimal("5000.00"),
        )

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        with patch.object(
            service.cashflow_service, "get_projection", new_callable=AsyncMock
        ) as mock_cf:
            mock_cf.return_value = []

            suggestions = await service.get_investment_suggestions(
                condominio_id=uuid4(),
            )

            assert suggestions == []

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture para credenciais."""
        return BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
        )

    @pytest.mark.asyncio
    async def test_get_investment_suggestions_with_surplus(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
        credentials: BankCredentials,
    ) -> None:
        """Testa sugestoes com excesso de saldo."""
        mock_banking_service.get_balance.return_value = AccountBalance(
            available=Decimal("100000.00"),  # Saldo alto
            blocked=Decimal("0"),
            total=Decimal("100000.00"),
        )

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )
        # Registra conta para obter saldo
        service.register_bank_account("conta_bb", "001", credentials)

        # Cria projecoes com saidas pequenas (saldo permanece alto)
        projections = []
        for _ in range(35):  # 35 dias
            proj = CashFlowProjection(
                date=date.today(),
                payables=Decimal("1000.00"),
                balance=Decimal("-1000.00"),  # Saida pequena
            )
            projections.append(proj)

        with patch.object(
            service.cashflow_service, "get_projection", new_callable=AsyncMock
        ) as mock_cf:
            mock_cf.return_value = projections

            suggestions = await service.get_investment_suggestions(
                condominio_id=uuid4(),
            )

            assert len(suggestions) >= 1
            types = [s["type"] for s in suggestions]
            assert "INVESTMENT_OPPORTUNITY" in types or "RECURRING_SURPLUS" in types


class TestCashFlowBankingServiceDashboard:
    """Testes de dados para dashboard."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        mock = MagicMock(spec=BankingService)
        mock.get_balance = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_get_dashboard_data(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
    ) -> None:
        """Testa obtencao de dados do dashboard."""
        mock_banking_service.get_balance.return_value = AccountBalance(
            available=Decimal("25000.00"),
            blocked=Decimal("0"),
            total=Decimal("25000.00"),
        )

        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        with (
            patch.object(
                service.cashflow_service, "get_projection", new_callable=AsyncMock
            ) as mock_proj,
            patch.object(
                service.cashflow_service, "get_summary", new_callable=AsyncMock
            ) as mock_sum,
            patch.object(
                service.cashflow_service, "get_category_breakdown", new_callable=AsyncMock
            ) as mock_cat,
            patch.object(
                service.cashflow_service, "get_supplier_breakdown", new_callable=AsyncMock
            ) as mock_sup,
            patch.object(
                service.cashflow_service, "get_monthly_trend", new_callable=AsyncMock
            ) as mock_trend,
        ):
            mock_proj.return_value = []
            mock_sum.return_value = {"period_days": 30}
            mock_cat.return_value = []
            mock_sup.return_value = []
            mock_trend.return_value = []

            result = await service.get_dashboard_data(condominio_id=uuid4())

            assert "current_balance" in result
            assert "projections" in result
            assert "alerts" in result
            assert "summary" in result
            assert "category_breakdown" in result
            assert "top_suppliers" in result
            assert "monthly_trend" in result
            assert "investment_suggestions" in result


class TestCashFlowBankingServiceCleanup:
    """Testes de limpeza de recursos."""

    @pytest.fixture
    def mock_session(self) -> MagicMock:
        """Fixture para sessao mock."""
        return MagicMock()

    @pytest.fixture
    def mock_banking_service(self) -> MagicMock:
        """Fixture para BankingService mock."""
        mock = MagicMock(spec=BankingService)
        mock.close_all = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_close(
        self,
        mock_session: MagicMock,
        mock_banking_service: MagicMock,
    ) -> None:
        """Testa fechamento de conexoes."""
        service = CashFlowBankingService(
            session=mock_session,
            banking_service=mock_banking_service,
        )

        await service.close()

        mock_banking_service.close_all.assert_called_once()
