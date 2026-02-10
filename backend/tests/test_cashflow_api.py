"""Testes para API de Fluxo de Caixa - Sprint 24."""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from modules.financial.models import (
    BankAccount,
    BankAccountStatus,
    BankAccountType,
    BankReconciliation,
    BankTransaction,
    CashFlowEntry,
    CashFlowEntryStatus,
    CashFlowEntryType,
    CashFlowForecast,
    CashFlowSourceType,
    ForecastConfidence,
    ForecastPeriodType,
    ForecastStatus,
    ReconciliationPeriodType,
    ReconciliationStatus,
    TransactionCategory,
    TransactionStatus,
    TransactionType,
)
from modules.financial.schemas import (
    AIForecastRequest,
    AnomalyDetectionRequest,
    AnomalyDetectionResponse,
    BankAccountCreate,
    BankTransactionCreate,
    CashFlowEntryCreate,
    CashFlowForecastCreate,
    OptimizationSuggestion,
)

# ==================== FIXTURES ====================


@pytest.fixture
def mock_current_user():
    """Mock do usuário autenticado."""
    return {"id": str(uuid4()), "email": "admin@test.com", "role": "admin"}


@pytest.fixture
def sample_bank_account():
    """Conta bancária de exemplo."""
    return BankAccount(
        id=uuid4(),
        condominio_id=uuid4(),
        name="Conta Principal",
        account_type=BankAccountType.CORRENTE,
        status=BankAccountStatus.ATIVA,
        bank_code="001",
        bank_name="Banco do Brasil",
        agency="1234",
        account_number="12345",
        opening_balance=Decimal("10000.00"),
        current_balance=Decimal("15000.00"),
        blocked_balance=Decimal("0.00"),
        is_main_account=True,
    )


@pytest.fixture
def sample_bank_transaction(sample_bank_account):
    """Transação bancária de exemplo."""
    return BankTransaction(
        id=uuid4(),
        bank_account_id=sample_bank_account.id,
        transaction_type=TransactionType.CREDITO,
        category=TransactionCategory.TAXA_CONDOMINIAL,
        amount=Decimal("500.00"),
        description="Recebimento taxa",
        transaction_date=date.today(),
        status=TransactionStatus.CONFIRMADA,
    )


@pytest.fixture
def sample_reconciliation(sample_bank_account):
    """Conciliação de exemplo."""
    return BankReconciliation(
        id=uuid4(),
        bank_account_id=sample_bank_account.id,
        period_type=ReconciliationPeriodType.MENSAL,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        system_opening_balance=Decimal("10000.00"),
        status=ReconciliationStatus.RASCUNHO,
    )


@pytest.fixture
def sample_cashflow_entry():
    """Entrada de fluxo de caixa de exemplo."""
    return CashFlowEntry(
        id=uuid4(),
        condominio_id=uuid4(),
        entry_type=CashFlowEntryType.ENTRADA,
        source_type=CashFlowSourceType.CONTA_RECEBER,
        description="Receita prevista",
        entry_date=date.today() + timedelta(days=30),
        expected_amount=Decimal("5000.00"),
        status=CashFlowEntryStatus.PREVISTO,
    )


@pytest.fixture
def sample_forecast():
    """Previsão de exemplo."""
    return CashFlowForecast(
        id=uuid4(),
        condominio_id=uuid4(),
        name="Previsão Janeiro",
        period_type=ForecastPeriodType.MENSAL,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        status=ForecastStatus.ATIVA,
        confidence_category=ForecastConfidence.ALTA.value,
        expected_inflows=Decimal("50000.00"),
        expected_outflows=Decimal("35000.00"),
        expected_closing_balance=Decimal("15000.00"),
    )


# ==================== TESTES BANK ACCOUNT ====================


class TestBankAccountController:
    """Testes para BankAccountController."""

    @pytest.mark.asyncio
    async def test_create_bank_account(self, mock_current_user, sample_bank_account):
        """Testa criação de conta bancária."""
        with patch("modules.financial.repositories.BankAccountRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.create = AsyncMock(return_value=sample_bank_account)

            # Simula request
            data = BankAccountCreate(
                condominio_id=sample_bank_account.condominio_id,
                name="Conta Principal",
                account_type=BankAccountType.CORRENTE,
                bank_code="001",
                bank_name="Banco do Brasil",
                agency="1234",
                account_number="12345",
                account_digit="6",
            )

            result = await mock_instance.create(data.model_dump())
            assert result.name == "Conta Principal"
            assert result.account_type == BankAccountType.CORRENTE

    @pytest.mark.asyncio
    async def test_get_main_account(self, mock_current_user, sample_bank_account):
        """Testa obtenção da conta principal."""
        with patch("modules.financial.repositories.BankAccountRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_main_account = AsyncMock(return_value=sample_bank_account)

            result = await mock_instance.get_main_account(sample_bank_account.condominio_id)
            assert result.is_main_account is True

    @pytest.mark.asyncio
    async def test_get_total_balance(self, mock_current_user, sample_bank_account):
        """Testa obtenção do saldo total."""
        with patch("modules.financial.repositories.BankAccountRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_total_balance = AsyncMock(return_value=Decimal("25000.00"))

            result = await mock_instance.get_total_balance(sample_bank_account.condominio_id)
            assert result == Decimal("25000.00")

    @pytest.mark.asyncio
    async def test_update_bank_account(self, mock_current_user, sample_bank_account):
        """Testa atualização de conta bancária."""
        with patch("modules.financial.repositories.BankAccountRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            updated_account = MagicMock()
            updated_account.name = "Conta Atualizada"
            mock_instance.get_by_id = AsyncMock(return_value=sample_bank_account)
            mock_instance.update = AsyncMock(return_value=updated_account)

            result = await mock_instance.update(sample_bank_account.id, {"name": "Conta Atualizada"})
            assert result.name == "Conta Atualizada"


# ==================== TESTES BANK TRANSACTION ====================


class TestBankTransactionController:
    """Testes para BankTransactionController."""

    @pytest.mark.asyncio
    async def test_create_transaction(self, mock_current_user, sample_bank_account, sample_bank_transaction):
        """Testa criação de transação."""
        with patch("modules.financial.repositories.BankTransactionRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.create = AsyncMock(return_value=sample_bank_transaction)

            data = BankTransactionCreate(
                bank_account_id=sample_bank_account.id,
                transaction_type=TransactionType.CREDITO,
                category=TransactionCategory.TAXA_CONDOMINIAL,
                amount=Decimal("500.00"),
                description="Recebimento taxa",
                transaction_date=date.today(),
            )

            result = await mock_instance.create(data.model_dump())
            assert result.amount == Decimal("500.00")
            assert result.transaction_type == TransactionType.CREDITO

    @pytest.mark.asyncio
    async def test_get_pending_reconciliation(self, mock_current_user, sample_bank_account, sample_bank_transaction):
        """Testa obtenção de transações pendentes de conciliação."""
        with patch("modules.financial.repositories.BankTransactionRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_pending_reconciliation = AsyncMock(return_value=[sample_bank_transaction])

            result = await mock_instance.get_pending_reconciliation(sample_bank_account.id, 100)
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_by_period(self, mock_current_user, sample_bank_account, sample_bank_transaction):
        """Testa obtenção de transações por período."""
        with patch("modules.financial.repositories.BankTransactionRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_by_period = AsyncMock(return_value=[sample_bank_transaction])

            result = await mock_instance.get_by_period(
                sample_bank_account.id,
                date.today() - timedelta(days=30),
                date.today(),
            )
            assert len(result) == 1


# ==================== TESTES BANK RECONCILIATION ====================


class TestBankReconciliationController:
    """Testes para BankReconciliationController."""

    @pytest.mark.asyncio
    async def test_create_reconciliation(self, mock_current_user, sample_bank_account, sample_reconciliation):
        """Testa criação de conciliação."""
        with patch("modules.financial.repositories.BankReconciliationRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.create = AsyncMock(return_value=sample_reconciliation)
            mock_instance.get_in_progress = AsyncMock(return_value=None)

            result = await mock_instance.create(
                {
                    "bank_account_id": sample_bank_account.id,
                    "period_type": ReconciliationPeriodType.MENSAL,
                    "period_start": date(2024, 1, 1),
                    "period_end": date(2024, 1, 31),
                    "system_opening_balance": Decimal("10000.00"),
                }
            )
            assert result.period_type == ReconciliationPeriodType.MENSAL

    @pytest.mark.asyncio
    async def test_get_in_progress(self, mock_current_user, sample_bank_account, sample_reconciliation):
        """Testa obtenção de conciliação em andamento."""
        with patch("modules.financial.repositories.BankReconciliationRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            sample_reconciliation.status = ReconciliationStatus.EM_ANDAMENTO
            mock_instance.get_in_progress = AsyncMock(return_value=sample_reconciliation)

            result = await mock_instance.get_in_progress(sample_bank_account.id)
            assert result.status == ReconciliationStatus.EM_ANDAMENTO


# ==================== TESTES CASHFLOW ENTRY ====================


class TestCashFlowEntryController:
    """Testes para endpoints de CashFlowEntry."""

    @pytest.mark.asyncio
    async def test_create_entry(self, mock_current_user, sample_cashflow_entry):
        """Testa criação de entrada de fluxo de caixa."""
        with patch("modules.financial.repositories.CashFlowEntryRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.create = AsyncMock(return_value=sample_cashflow_entry)

            data = CashFlowEntryCreate(
                condominio_id=sample_cashflow_entry.condominio_id,
                entry_type=CashFlowEntryType.ENTRADA,
                description="Receita prevista",
                entry_date=date.today() + timedelta(days=30),
                expected_amount=Decimal("5000.00"),
            )

            result = await mock_instance.create(data.model_dump())
            assert result.expected_amount == Decimal("5000.00")

    @pytest.mark.asyncio
    async def test_get_pending_entries(self, mock_current_user, sample_cashflow_entry):
        """Testa obtenção de entradas pendentes."""
        with patch("modules.financial.repositories.CashFlowEntryRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_pending = AsyncMock(return_value=[sample_cashflow_entry])

            result = await mock_instance.get_pending(sample_cashflow_entry.condominio_id, 30)
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_totals_by_type(self, mock_current_user, sample_cashflow_entry):
        """Testa obtenção de totais por tipo."""
        with patch("modules.financial.repositories.CashFlowEntryRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_totals_by_type = AsyncMock(
                return_value={
                    "entrada": Decimal("50000.00"),
                    "saida": Decimal("35000.00"),
                    "net": Decimal("15000.00"),
                }
            )

            result = await mock_instance.get_totals_by_type(
                sample_cashflow_entry.condominio_id,
                date.today(),
                date.today() + timedelta(days=30),
            )
            assert result["entrada"] == Decimal("50000.00")
            assert result["net"] == Decimal("15000.00")


# ==================== TESTES CASHFLOW FORECAST ====================


class TestCashFlowForecastController:
    """Testes para endpoints de CashFlowForecast."""

    @pytest.mark.asyncio
    async def test_create_forecast(self, mock_current_user, sample_forecast):
        """Testa criação de previsão."""
        with patch("modules.financial.repositories.CashFlowForecastRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.create = AsyncMock(return_value=sample_forecast)

            data = CashFlowForecastCreate(
                condominio_id=sample_forecast.condominio_id,
                name="Previsão Janeiro",
                period_type=ForecastPeriodType.MENSAL,
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                forecast_date=date(2024, 1, 1),
                expected_receivables=Decimal("50000.00"),
                expected_payables=Decimal("35000.00"),
            )

            result = await mock_instance.create(data.model_dump())
            assert result.expected_closing_balance == Decimal("15000.00")

    @pytest.mark.asyncio
    async def test_get_active_forecasts(self, mock_current_user, sample_forecast):
        """Testa obtenção de previsões ativas."""
        with patch("modules.financial.repositories.CashFlowForecastRepository") as mock_repo:
            mock_instance = mock_repo.return_value
            mock_instance.get_active = AsyncMock(return_value=[sample_forecast])

            result = await mock_instance.get_active(sample_forecast.condominio_id)
            assert len(result) == 1
            assert result[0].status == ForecastStatus.ATIVA


# ==================== TESTES AI SERVICE ====================


class TestCashFlowAIService:
    """Testes para CashFlowAIService."""

    @pytest.mark.asyncio
    async def test_generate_forecast(self, mock_current_user):
        """Testa geração de previsão com IA."""
        with patch("modules.financial.services.CashFlowAIService") as mock_service:
            mock_instance = mock_service.return_value
            mock_response = MagicMock()
            mock_response.scenarios = {
                "pessimista": {"balance": Decimal("10000.00")},
                "realista": {"balance": Decimal("15000.00")},
                "otimista": {"balance": Decimal("20000.00")},
            }
            mock_response.recommendations = ["Aumentar reserva de emergência"]
            mock_response.risks = [{"type": "inadimplencia", "impact": "alto"}]
            mock_response.opportunities = [{"type": "renegociacao"}]
            mock_instance.generate_forecast = AsyncMock(return_value=mock_response)

            request = AIForecastRequest(condominio_id=uuid4(), months_ahead=3)
            result = await mock_instance.generate_forecast(request)

            assert result.scenarios["realista"]["balance"] == Decimal("15000.00")
            assert len(result.recommendations) == 1

    @pytest.mark.asyncio
    async def test_detect_anomalies(self, mock_current_user):
        """Testa detecção de anomalias."""
        with patch("modules.financial.services.CashFlowAIService") as mock_service:
            mock_instance = mock_service.return_value
            mock_response = AnomalyDetectionResponse(
                anomalies=[
                    {
                        "type": "valor_alto",
                        "description": "Pagamento acima do esperado",
                        "amount": "5000.00",
                        "severity": "high",
                        "date": str(date.today()),
                    }
                ],
                total=1,
                by_severity={"high": 1, "medium": 0, "low": 0},
                by_category={"valor_alto": 1},
            )
            mock_instance.detect_anomalies = AsyncMock(return_value=mock_response)

            request = AnomalyDetectionRequest(condominio_id=uuid4(), period_months=6)
            result = await mock_instance.detect_anomalies(request)

            assert result.total == 1
            assert result.by_severity["high"] == 1

    @pytest.mark.asyncio
    async def test_suggest_optimizations(self, mock_current_user):
        """Testa sugestões de otimização."""
        with patch("modules.financial.services.CashFlowAIService") as mock_service:
            mock_instance = mock_service.return_value
            mock_suggestions = [
                OptimizationSuggestion(
                    id="opt-001",
                    type="renegociacao",
                    title="Renegociar contrato de limpeza",
                    description="O valor atual está 20% acima da média de mercado",
                    potential_savings=Decimal("2000.00"),
                    implementation_effort="medio",
                    priority="high",
                    action_items=["Solicitar propostas de outros fornecedores"],
                ),
                OptimizationSuggestion(
                    id="opt-002",
                    type="antecipacao",
                    title="Antecipar recebíveis",
                    description="Oferecer desconto para pagamento antecipado",
                    potential_savings=Decimal("1500.00"),
                    implementation_effort="baixo",
                    priority="medium",
                    action_items=["Enviar comunicado aos moradores"],
                ),
            ]
            mock_instance.suggest_optimizations = AsyncMock(return_value=mock_suggestions)

            result = await mock_instance.suggest_optimizations(uuid4())

            assert len(result) == 2
            assert result[0].potential_savings == Decimal("2000.00")
            assert result[0].priority == "high"


# ==================== TESTES INTEGRAÇÃO ====================


class TestCashFlowIntegration:
    """Testes de integração de fluxo de caixa."""

    @pytest.mark.asyncio
    async def test_transfer_between_accounts(self):
        """Testa transferência entre contas."""
        account_from = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Origem",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("10000.00"),
        )
        account_to = BankAccount(
            id=uuid4(),
            condominio_id=account_from.condominio_id,
            name="Conta Destino",
            account_type=BankAccountType.POUPANCA,
            current_balance=Decimal("5000.00"),
        )

        # Simula transferência
        transfer_amount = Decimal("3000.00")

        # Debita origem
        account_from.update_balance(-transfer_amount)
        # Credita destino
        account_to.update_balance(transfer_amount)

        assert account_from.current_balance == Decimal("7000.00")
        assert account_to.current_balance == Decimal("8000.00")

    @pytest.mark.asyncio
    async def test_reconciliation_flow(self, sample_bank_account, sample_bank_transaction):
        """Testa fluxo completo de conciliação."""
        # Cria conciliação
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=sample_bank_account.id,
            condominio_id=sample_bank_account.condominio_id,
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            system_opening_balance=Decimal("10000.00"),
            total_system_transactions=10,
            total_bank_transactions=10,
            reconciled_count=0,
        )

        # Simula conciliação de itens
        recon.reconciled_count = 5
        recon.calculate_progress()
        assert recon.reconciliation_progress == Decimal("50.0")

        recon.reconciled_count = 10
        recon.calculate_progress()
        assert recon.reconciliation_progress == Decimal("100")

        # Finaliza - sem diferenças
        recon.bank_closing_balance = Decimal("15000.00")
        recon.system_closing_balance = Decimal("15000.00")
        recon.closing_difference = Decimal("0")
        recon.divergent_count = 0
        recon.pending_system_count = 0
        recon.pending_bank_count = 0
        recon.complete(uuid4())

        assert recon.status == ReconciliationStatus.CONCLUIDA
        assert recon.closing_difference == Decimal("0")

    @pytest.mark.asyncio
    async def test_cashflow_entry_realization(self, sample_cashflow_entry):
        """Testa realização de entrada de fluxo de caixa."""
        entry = sample_cashflow_entry

        # Estado inicial
        assert entry.status == CashFlowEntryStatus.PREVISTO
        assert entry.realized_amount is None

        # Realiza entrada
        entry.status = CashFlowEntryStatus.REALIZADO
        entry.realized_date = date.today()
        entry.realized_amount = Decimal("4800.00")  # Valor diferente do previsto

        # Verifica
        assert entry.status == CashFlowEntryStatus.REALIZADO
        assert entry.realized_amount == Decimal("4800.00")
        # Diferença
        difference = entry.realized_amount - entry.expected_amount
        assert difference == Decimal("-200.00")

    @pytest.mark.asyncio
    async def test_forecast_variance_calculation(self, sample_forecast):
        """Testa cálculo de variação de previsão."""
        forecast = sample_forecast

        # Valores esperados
        assert forecast.expected_inflows == Decimal("50000.00")
        assert forecast.expected_outflows == Decimal("35000.00")
        assert forecast.expected_closing_balance == Decimal("15000.00")

        # Atualiza com valores realizados
        forecast.actual_inflows = Decimal("48000.00")
        forecast.actual_outflows = Decimal("36000.00")
        forecast.actual_closing_balance = Decimal("12000.00")
        forecast.calculate_variances()

        # Verifica variações
        assert forecast.inflows_variance == Decimal("-2000.00")
        assert forecast.outflows_variance == Decimal("1000.00")
        assert forecast.balance_variance == Decimal("-3000.00")

        # Verifica percentual
        expected_pct = (Decimal("-3000.00") / Decimal("15000.00")) * 100
        assert forecast.balance_variance_pct == expected_pct


# ==================== TESTES DE VALIDAÇÃO ====================


class TestCashFlowValidation:
    """Testes de validação de dados."""

    def test_bank_account_create_validation(self):
        """Testa validação de criação de conta."""
        # Dados válidos
        data = BankAccountCreate(
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            bank_code="001",
            bank_name="Banco Teste",
            agency="0001",
            account_number="12345",
            account_digit="6",
        )
        assert data.name == "Conta Teste"

    def test_transaction_create_validation(self):
        """Testa validação de criação de transação."""
        data = BankTransactionCreate(
            bank_account_id=uuid4(),
            transaction_type=TransactionType.CREDITO,
            category=TransactionCategory.TAXA_CONDOMINIAL,
            amount=Decimal("500.00"),
            description="Teste",
            transaction_date=date.today(),
        )
        assert data.amount > 0

    def test_cashflow_entry_create_validation(self):
        """Testa validação de criação de entrada."""
        data = CashFlowEntryCreate(
            condominio_id=uuid4(),
            entry_type=CashFlowEntryType.ENTRADA,
            description="Entrada teste",
            entry_date=date.today() + timedelta(days=1),
            expected_amount=Decimal("1000.00"),
        )
        assert data.entry_date > date.today()

    def test_forecast_create_validation(self):
        """Testa validação de criação de previsão."""
        data = CashFlowForecastCreate(
            condominio_id=uuid4(),
            name="Previsão Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_receivables=Decimal("50000.00"),
            expected_payables=Decimal("35000.00"),
        )
        assert data.period_end > data.period_start
