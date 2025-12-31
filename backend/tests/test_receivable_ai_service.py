"""Testes para o ReceivableAIService."""

import uuid
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.financial.models.customer import Customer, CustomerStatus
from modules.financial.models.receivable_account import ReceivableAccount, ReceivableStatus
from modules.financial.services.receivable_ai_service import ReceivableAIService


class TestReceivableAIService:
    """Testes para o ReceivableAIService."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para mock do session."""
        session = MagicMock()
        session.commit = AsyncMock()
        return session

    @pytest.fixture
    def ai_service(self, mock_session):
        """Fixture para instancia do AI service."""
        return ReceivableAIService(mock_session)

    @pytest.fixture
    def sample_customer(self):
        """Fixture para cliente de exemplo."""
        return Customer(
            id=uuid.uuid4(),
            condominio_id=uuid.uuid4(),
            cpf_cnpj="123.456.789-00",
            name="Cliente Teste",
            status=CustomerStatus.ATIVO.value,
            total_debt=Decimal("1500.00"),
            overdue_debt=Decimal("500.00"),
        )

    @pytest.fixture
    def sample_accounts(self, sample_customer):
        """Fixture para contas de exemplo."""
        condominio_id = sample_customer.condominio_id
        customer_id = sample_customer.id

        return [
            ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=condominio_id,
                customer_id=customer_id,
                description="Taxa Jan/2025",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("850.00"),
                issue_date=date.today() - timedelta(days=60),
                due_date=date.today() - timedelta(days=50),
                payment_date=date.today() - timedelta(days=48),
                status=ReceivableStatus.PAGA.value,
            ),
            ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=condominio_id,
                customer_id=customer_id,
                description="Taxa Fev/2025",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("850.00"),
                issue_date=date.today() - timedelta(days=30),
                due_date=date.today() - timedelta(days=20),
                payment_date=date.today() - timedelta(days=15),
                status=ReceivableStatus.PAGA.value,
            ),
            ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=condominio_id,
                customer_id=customer_id,
                description="Taxa Mar/2025",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("0"),
                issue_date=date.today() - timedelta(days=10),
                due_date=date.today() - timedelta(days=5),
                status=ReceivableStatus.VENCIDA.value,
            ),
        ]

    @pytest.mark.asyncio
    async def test_calculate_customer_risk_low(self, ai_service, sample_customer):
        """Testa calculo de risco baixo."""
        sample_customer.total_debt = Decimal("0")
        sample_customer.overdue_debt = Decimal("0")

        accounts = [
            ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=sample_customer.condominio_id,
                customer_id=sample_customer.id,
                description="Taxa Jan/2025",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("850.00"),
                issue_date=date.today() - timedelta(days=30),
                due_date=date.today() - timedelta(days=20),
                payment_date=date.today() - timedelta(days=22),
                status=ReceivableStatus.PAGA.value,
            )
            for _ in range(12)
        ]

        with patch.object(ai_service.customer_repo, "get_by_id") as mock_cust:
            with patch.object(ai_service.account_repo, "get_by_customer") as mock_acc:
                mock_cust.return_value = sample_customer
                mock_acc.return_value = accounts

                risk = await ai_service.calculate_customer_risk(sample_customer.id)

                assert risk.risk_level == "baixo"
                assert risk.risk_score < 30
                assert "Excelente" in risk.recommendations[0] or len(risk.recommendations) > 0

    @pytest.mark.asyncio
    async def test_calculate_customer_risk_high(
        self, ai_service, sample_customer, sample_accounts
    ):
        """Testa calculo de risco alto."""
        sample_customer.total_debt = Decimal("5000.00")
        sample_customer.overdue_debt = Decimal("4000.00")

        # Cria contas com historico ruim
        bad_accounts = []
        for i in range(6):
            acc = ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=sample_customer.condominio_id,
                customer_id=sample_customer.id,
                description=f"Taxa {i}/2025",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("0"),
                issue_date=date.today() - timedelta(days=30 * (i + 1)),
                due_date=date.today() - timedelta(days=30 * i + 20),
                status=ReceivableStatus.VENCIDA.value,
            )
            bad_accounts.append(acc)

        with patch.object(ai_service.customer_repo, "get_by_id") as mock_cust:
            with patch.object(ai_service.account_repo, "get_by_customer") as mock_acc:
                mock_cust.return_value = sample_customer
                mock_acc.return_value = bad_accounts

                risk = await ai_service.calculate_customer_risk(sample_customer.id)

                assert risk.risk_level in ["alto", "critico"]
                assert risk.risk_score >= 60

    @pytest.mark.asyncio
    async def test_calculate_customer_risk_not_found(self, ai_service):
        """Testa calculo de risco para cliente inexistente."""
        customer_id = uuid.uuid4()

        with patch.object(ai_service.customer_repo, "get_by_id") as mock_get:
            mock_get.return_value = None

            risk = await ai_service.calculate_customer_risk(customer_id)

            assert risk.risk_score == 0
            assert risk.risk_level == "desconhecido"

    @pytest.mark.asyncio
    async def test_get_collection_priorities(
        self, ai_service, sample_customer, sample_accounts
    ):
        """Testa priorizacao de cobrancas."""
        condominio_id = sample_customer.condominio_id

        overdue_accounts = [a for a in sample_accounts if a.status == ReceivableStatus.VENCIDA.value]

        with patch.object(ai_service.account_repo, "get_overdue") as mock_overdue:
            with patch.object(ai_service.customer_repo, "get_by_id") as mock_cust:
                mock_overdue.return_value = overdue_accounts
                mock_cust.return_value = sample_customer

                priorities = await ai_service.get_collection_priorities(
                    condominio_id, limit=10
                )

                assert len(priorities) > 0
                # Deve ter prioridades ordenadas
                for p in priorities:
                    assert p.priority_score >= 0
                    assert p.priority_level in ["baixa", "media", "alta", "urgente"]
                    assert p.recommended_action is not None

    @pytest.mark.asyncio
    async def test_get_collection_priorities_empty(self, ai_service):
        """Testa priorizacao sem contas vencidas."""
        condominio_id = uuid.uuid4()

        with patch.object(ai_service.account_repo, "get_overdue") as mock_overdue:
            mock_overdue.return_value = []

            priorities = await ai_service.get_collection_priorities(
                condominio_id, limit=10
            )

            assert len(priorities) == 0

    @pytest.mark.asyncio
    async def test_forecast_cash_flow(self, ai_service, sample_accounts):
        """Testa previsao de fluxo de caixa."""
        condominio_id = sample_accounts[0].condominio_id

        # Cria contas pendentes para previsao
        pending_accounts = []
        for i in range(6):
            acc = ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=condominio_id,
                customer_id=uuid.uuid4(),
                description=f"Taxa {i}/2025",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("0"),
                issue_date=date.today(),
                due_date=date.today() + timedelta(days=30 * i),
                status=ReceivableStatus.PENDENTE.value,
            )
            pending_accounts.append(acc)

        with patch.object(ai_service.account_repo, "get_pending") as mock_pending:
            mock_pending.return_value = pending_accounts

            forecast = await ai_service.forecast_cash_flow(condominio_id, months=6)

            assert forecast.condominio_id == condominio_id
            assert forecast.expected_income > Decimal("0")
            assert forecast.probable_income >= Decimal("0")
            assert len(forecast.monthly_breakdown) > 0
            assert forecast.confidence_level >= 0
            assert forecast.confidence_level <= 100

    @pytest.mark.asyncio
    async def test_forecast_cash_flow_empty(self, ai_service):
        """Testa previsao sem contas pendentes."""
        condominio_id = uuid.uuid4()

        with patch.object(ai_service.account_repo, "get_pending") as mock_pending:
            mock_pending.return_value = []

            forecast = await ai_service.forecast_cash_flow(condominio_id, months=6)

            assert forecast.expected_income == Decimal("0")
            assert forecast.probable_income == Decimal("0")

    @pytest.mark.asyncio
    async def test_analyze_delinquency(self, ai_service, sample_customer):
        """Testa analise de inadimplencia."""
        condominio_id = sample_customer.condominio_id

        customers = [
            Customer(
                id=uuid.uuid4(),
                condominio_id=condominio_id,
                cpf_cnpj=f"123.456.789-0{i}",
                name=f"Cliente {i}",
                status=CustomerStatus.ATIVO.value,
                total_debt=Decimal(str(1000 * i)) if i > 5 else Decimal("0"),
                overdue_debt=Decimal(str(500 * i)) if i > 7 else Decimal("0"),
            )
            for i in range(10)
        ]

        overdue_accounts = [
            ReceivableAccount(
                id=uuid.uuid4(),
                condominio_id=condominio_id,
                customer_id=customers[8].id,
                description="Taxa Vencida",
                gross_value=Decimal("850.00"),
                net_value=Decimal("850.00"),
                paid_value=Decimal("0"),
                issue_date=date.today() - timedelta(days=60),
                due_date=date.today() - timedelta(days=30),
                status=ReceivableStatus.VENCIDA.value,
            )
            for _ in range(3)
        ]

        with patch.object(ai_service.customer_repo, "list") as mock_list:
            with patch.object(ai_service.account_repo, "get_overdue") as mock_overdue:
                mock_list.return_value = customers
                mock_overdue.return_value = overdue_accounts

                analysis = await ai_service.analyze_delinquency(condominio_id)

                assert analysis.condominio_id == condominio_id
                assert analysis.total_customers == 10
                assert analysis.delinquency_rate >= 0
                assert analysis.delinquency_rate <= 100
                assert len(analysis.aging_breakdown) > 0
                assert analysis.trend in ["melhorando", "estavel", "piorando"]
                assert len(analysis.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_delinquency_no_customers(self, ai_service):
        """Testa analise sem clientes."""
        condominio_id = uuid.uuid4()

        with patch.object(ai_service.customer_repo, "list") as mock_list:
            with patch.object(ai_service.account_repo, "get_overdue") as mock_overdue:
                mock_list.return_value = []
                mock_overdue.return_value = []

                analysis = await ai_service.analyze_delinquency(condominio_id)

                assert analysis.total_customers == 0
                assert analysis.delinquent_customers == 0
                assert analysis.delinquency_rate == 0

    @pytest.mark.asyncio
    async def test_risk_factors(self, ai_service, sample_customer, sample_accounts):
        """Testa fatores de risco retornados."""
        with patch.object(ai_service.customer_repo, "get_by_id") as mock_cust:
            with patch.object(ai_service.account_repo, "get_by_customer") as mock_acc:
                mock_cust.return_value = sample_customer
                mock_acc.return_value = sample_accounts

                risk = await ai_service.calculate_customer_risk(sample_customer.id)

                assert isinstance(risk.factors, list)
                # Deve ter pelo menos um fator de risco
                assert len(risk.factors) > 0 or risk.risk_score == 0

    @pytest.mark.asyncio
    async def test_collection_recommended_actions(
        self, ai_service, sample_customer, sample_accounts
    ):
        """Testa acoes recomendadas para cobranca."""
        condominio_id = sample_customer.condominio_id
        overdue_accounts = [a for a in sample_accounts if a.status == ReceivableStatus.VENCIDA.value]

        with patch.object(ai_service.account_repo, "get_overdue") as mock_overdue:
            with patch.object(ai_service.customer_repo, "get_by_id") as mock_cust:
                mock_overdue.return_value = overdue_accounts
                mock_cust.return_value = sample_customer

                priorities = await ai_service.get_collection_priorities(
                    condominio_id, limit=10
                )

                for p in priorities:
                    assert p.recommended_action in [
                        "lembrete",
                        "notificacao",
                        "cobranca_telefone",
                        "carta_cobranca",
                        "negativacao",
                        "protesto",
                        "acao_judicial",
                    ]
