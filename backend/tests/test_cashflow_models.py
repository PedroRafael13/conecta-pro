"""Testes para models de Fluxo de Caixa - Sprint 24."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

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
    PixKeyType,
    ReconciliationPeriodType,
    ReconciliationStatus,
    RecurrenceFrequency,
    TransactionCategory,
    TransactionOrigin,
    TransactionStatus,
    TransactionType,
)


class TestBankAccountModel:
    """Testes para o model BankAccount."""

    def test_create_bank_account(self):
        """Testa criacao de conta bancaria."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Principal",
            account_type=BankAccountType.CORRENTE,
            bank_code="001",
            bank_name="Banco do Brasil",
            agency="1234",
            account_number="12345",
            account_digit="0",
            opening_balance=Decimal("10000.00"),
            status=BankAccountStatus.ATIVA,
        )

        assert account.name == "Conta Principal"
        assert account.account_type == BankAccountType.CORRENTE
        assert account.status == BankAccountStatus.ATIVA
        assert account.opening_balance == Decimal("10000.00")

    def test_update_balance_credit(self):
        """Testa atualizacao de saldo com credito."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("1000.00"),
        )

        account.update_balance(Decimal("500.00"))
        assert account.current_balance == Decimal("1500.00")

    def test_update_balance_debit(self):
        """Testa atualizacao de saldo com debito."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("1000.00"),
        )

        account.update_balance(Decimal("300.00"), is_credit=False)
        assert account.current_balance == Decimal("700.00")

    def test_block_balance(self):
        """Testa bloqueio de saldo."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            blocked_balance=Decimal("0.00"),
        )

        result = account.block_balance(Decimal("200.00"))
        assert result is True
        assert account.blocked_balance == Decimal("200.00")
        assert account.available_balance == Decimal("800.00")

    def test_block_balance_insufficient(self):
        """Testa bloqueio com saldo insuficiente."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("100.00"),
            blocked_balance=Decimal("0.00"),
        )

        result = account.block_balance(Decimal("200.00"))
        assert result is False
        assert account.blocked_balance == Decimal("0.00")

    def test_unblock_balance(self):
        """Testa desbloqueio de saldo."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("800.00"),
            blocked_balance=Decimal("200.00"),
        )

        account.unblock_balance(Decimal("150.00"))
        assert account.blocked_balance == Decimal("50.00")
        assert account.available_balance == Decimal("950.00")

    def test_bank_account_types(self):
        """Testa todos os tipos de conta bancaria."""
        types = [
            BankAccountType.CORRENTE,
            BankAccountType.POUPANCA,
            BankAccountType.APLICACAO,
            BankAccountType.INVESTIMENTO,
            BankAccountType.CAIXA,
            BankAccountType.DIGITAL,
        ]
        assert len(types) == 6

    def test_pix_key_types(self):
        """Testa tipos de chave PIX."""
        types = [
            PixKeyType.CPF,
            PixKeyType.CNPJ,
            PixKeyType.EMAIL,
            PixKeyType.TELEFONE,
            PixKeyType.ALEATORIA,
        ]
        assert len(types) == 5


class TestBankTransactionModel:
    """Testes para o model BankTransaction."""

    def test_create_credit_transaction(self):
        """Testa criacao de transacao de credito."""
        tx = BankTransaction(
            id=uuid4(),
            bank_account_id=uuid4(),
            transaction_type=TransactionType.CREDITO,
            category=TransactionCategory.TAXA_CONDOMINIAL,
            amount=Decimal("500.00"),
            description="Recebimento taxa condominio",
            transaction_date=date.today(),
            status=TransactionStatus.PENDENTE,
        )

        assert tx.transaction_type == TransactionType.CREDITO
        assert tx.category == TransactionCategory.TAXA_CONDOMINIAL
        assert tx.amount == Decimal("500.00")
        assert tx.status == TransactionStatus.PENDENTE

    def test_create_debit_transaction(self):
        """Testa criacao de transacao de debito."""
        tx = BankTransaction(
            id=uuid4(),
            bank_account_id=uuid4(),
            transaction_type=TransactionType.DEBITO,
            category=TransactionCategory.MANUTENCAO,
            amount=Decimal("200.00"),
            description="Pagamento manutencao",
            transaction_date=date.today(),
        )

        assert tx.transaction_type == TransactionType.DEBITO
        assert tx.category == TransactionCategory.MANUTENCAO

    def test_transaction_categories(self):
        """Testa todas as categorias de transacao."""
        categories = [
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_EXTRA,
            TransactionCategory.ALUGUEL,
            TransactionCategory.RESERVA,
            TransactionCategory.MULTA,
            TransactionCategory.JUROS_RECEBIDOS,
            TransactionCategory.RENDIMENTO,
            TransactionCategory.OUTRAS_RECEITAS,
            TransactionCategory.FORNECEDOR,
            TransactionCategory.FUNCIONARIO,
            TransactionCategory.TRIBUTO,
            TransactionCategory.SERVICO,
            TransactionCategory.MANUTENCAO,
            TransactionCategory.TARIFA_BANCARIA,
            TransactionCategory.IOF,
            TransactionCategory.JUROS_PAGOS,
            TransactionCategory.OUTRAS_DESPESAS,
            TransactionCategory.TRANSFERENCIA_ENTRE_CONTAS,
            TransactionCategory.APLICACAO,
            TransactionCategory.RESGATE,
            TransactionCategory.AJUSTE,
            TransactionCategory.SALDO_INICIAL,
            TransactionCategory.NAO_IDENTIFICADO,
        ]
        assert len(categories) == 23

    def test_transaction_origins(self):
        """Testa todas as origens de transacao."""
        origins = [
            TransactionOrigin.MANUAL,
            TransactionOrigin.PAGAMENTO_CONTA,
            TransactionOrigin.RECEBIMENTO,
            TransactionOrigin.IMPORTACAO,
            TransactionOrigin.API,
            TransactionOrigin.PIX,
            TransactionOrigin.BOLETO,
            TransactionOrigin.TED,
            TransactionOrigin.DOC,
            TransactionOrigin.TRANSFERENCIA,
        ]
        assert len(origins) == 10


class TestBankReconciliationModel:
    """Testes para o model BankReconciliation."""

    def test_create_reconciliation(self):
        """Testa criacao de conciliacao."""
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=uuid4(),
            condominio_id=uuid4(),
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            system_opening_balance=Decimal("10000.00"),
            status=ReconciliationStatus.RASCUNHO,
        )

        assert recon.period_type == ReconciliationPeriodType.MENSAL
        assert recon.status == ReconciliationStatus.RASCUNHO

    def test_calculate_progress(self):
        """Testa calculo de progresso."""
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=uuid4(),
            condominio_id=uuid4(),
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            system_opening_balance=Decimal("10000.00"),
            total_system_transactions=50,
            total_bank_transactions=50,
            reconciled_count=50,
        )

        recon.calculate_progress()
        assert recon.reconciliation_progress == Decimal("100")

    def test_complete_reconciliation(self):
        """Testa finalizacao de conciliacao."""
        user_id = uuid4()
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=uuid4(),
            condominio_id=uuid4(),
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            system_opening_balance=Decimal("10000.00"),
            system_closing_balance=Decimal("12000.00"),
            bank_closing_balance=Decimal("12000.00"),
            closing_difference=Decimal("0"),
            divergent_count=0,
            pending_system_count=0,
            pending_bank_count=0,
            total_system_transactions=0,
            total_bank_transactions=0,
            reconciled_count=0,
        )

        recon.complete(user_id)
        assert recon.status == ReconciliationStatus.CONCLUIDA
        assert recon.completed_at is not None
        assert recon.completed_by == user_id

    def test_reconciliation_period_types(self):
        """Testa tipos de periodo de conciliacao."""
        types = [
            ReconciliationPeriodType.DIARIO,
            ReconciliationPeriodType.SEMANAL,
            ReconciliationPeriodType.QUINZENAL,
            ReconciliationPeriodType.MENSAL,
        ]
        assert len(types) == 4


class TestCashFlowEntryModel:
    """Testes para o model CashFlowEntry."""

    def test_create_entry_income(self):
        """Testa criacao de entrada de receita."""
        entry = CashFlowEntry(
            id=uuid4(),
            condominio_id=uuid4(),
            entry_type=CashFlowEntryType.ENTRADA,
            source_type=CashFlowSourceType.CONTA_RECEBER,
            description="Receita prevista",
            entry_date=date.today() + timedelta(days=30),
            expected_amount=Decimal("5000.00"),
            status=CashFlowEntryStatus.PREVISTO,
        )

        assert entry.entry_type == CashFlowEntryType.ENTRADA
        assert entry.source_type == CashFlowSourceType.CONTA_RECEBER
        assert entry.status == CashFlowEntryStatus.PREVISTO

    def test_create_entry_expense(self):
        """Testa criacao de entrada de despesa."""
        entry = CashFlowEntry(
            id=uuid4(),
            condominio_id=uuid4(),
            entry_type=CashFlowEntryType.SAIDA,
            source_type=CashFlowSourceType.CONTA_PAGAR,
            description="Despesa prevista",
            entry_date=date.today() + timedelta(days=15),
            expected_amount=Decimal("2000.00"),
            status=CashFlowEntryStatus.PREVISTO,
        )

        assert entry.entry_type == CashFlowEntryType.SAIDA
        assert entry.source_type == CashFlowSourceType.CONTA_PAGAR

    def test_recurring_entry(self):
        """Testa entrada recorrente."""
        entry = CashFlowEntry(
            id=uuid4(),
            condominio_id=uuid4(),
            entry_type=CashFlowEntryType.SAIDA,
            source_type=CashFlowSourceType.RECORRENTE,
            description="Conta de luz mensal",
            entry_date=date.today(),
            expected_amount=Decimal("800.00"),
            is_recurring=True,
            recurrence_frequency=RecurrenceFrequency.MENSAL,
            recurrence_end=date.today() + timedelta(days=365),
        )

        assert entry.is_recurring is True
        assert entry.recurrence_frequency == RecurrenceFrequency.MENSAL

    def test_recurrence_frequencies(self):
        """Testa todas as frequencias de recorrencia."""
        frequencies = [
            RecurrenceFrequency.DIARIA,
            RecurrenceFrequency.SEMANAL,
            RecurrenceFrequency.QUINZENAL,
            RecurrenceFrequency.MENSAL,
            RecurrenceFrequency.BIMESTRAL,
            RecurrenceFrequency.TRIMESTRAL,
            RecurrenceFrequency.SEMESTRAL,
            RecurrenceFrequency.ANUAL,
        ]
        assert len(frequencies) == 8

    def test_cashflow_entry_statuses(self):
        """Testa todos os status de entrada."""
        statuses = [
            CashFlowEntryStatus.PREVISTO,
            CashFlowEntryStatus.CONFIRMADO,
            CashFlowEntryStatus.REALIZADO,
            CashFlowEntryStatus.CANCELADO,
        ]
        assert len(statuses) == 4


class TestCashFlowForecastModel:
    """Testes para o model CashFlowForecast."""

    def test_create_forecast(self):
        """Testa criacao de previsao."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao Janeiro 2024",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_inflows=Decimal("50000.00"),
            expected_outflows=Decimal("35000.00"),
            expected_closing_balance=Decimal("15000.00"),
            status=ForecastStatus.RASCUNHO,
            confidence_category=ForecastConfidence.MEDIA,
        )

        assert forecast.name == "Previsao Janeiro 2024"
        assert forecast.period_type == ForecastPeriodType.MENSAL
        assert forecast.status == ForecastStatus.RASCUNHO
        assert forecast.confidence_category == ForecastConfidence.MEDIA

    def test_update_actuals(self):
        """Testa atualizacao de valores realizados."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_inflows=Decimal("50000.00"),
            expected_outflows=Decimal("35000.00"),
            expected_closing_balance=Decimal("15000.00"),
        )

        # Set actuals and calculate variances
        forecast.actual_inflows = Decimal("48000.00")
        forecast.actual_outflows = Decimal("34000.00")
        forecast.actual_closing_balance = Decimal("14000.00")
        forecast.calculate_variances()

        assert forecast.actual_inflows == Decimal("48000.00")
        assert forecast.actual_outflows == Decimal("34000.00")
        assert forecast.actual_closing_balance == Decimal("14000.00")
        assert forecast.inflows_variance == Decimal("-2000.00")
        assert forecast.outflows_variance == Decimal("-1000.00")
        assert forecast.balance_variance == Decimal("-1000.00")

    def test_ai_generated_forecast(self):
        """Testa previsao gerada por IA."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao IA",
            period_type=ForecastPeriodType.TRIMESTRAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            forecast_date=date(2024, 1, 1),
            expected_inflows=Decimal("150000.00"),
            expected_outflows=Decimal("100000.00"),
            expected_closing_balance=Decimal("50000.00"),
            ai_generated=True,
            ai_model_version="1.0.0",
            confidence_category=ForecastConfidence.ALTA,
        )

        assert forecast.ai_generated is True
        assert forecast.ai_model_version == "1.0.0"
        assert forecast.confidence_category == ForecastConfidence.ALTA

    def test_forecast_with_scenarios(self):
        """Testa previsao com cenarios."""
        scenarios = {
            "pessimista": {"inflows": 45000, "outflows": 55000, "balance": -10000},
            "realista": {"inflows": 50000, "outflows": 50000, "balance": 0},
            "otimista": {"inflows": 55000, "outflows": 45000, "balance": 10000},
        }

        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao Cenarios",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_inflows=Decimal("50000.00"),
            expected_outflows=Decimal("35000.00"),
            expected_closing_balance=Decimal("15000.00"),
            scenarios=scenarios,
        )

        assert forecast.scenarios["pessimista"]["balance"] == -10000
        assert forecast.scenarios["otimista"]["balance"] == 10000

    def test_forecast_period_types(self):
        """Testa tipos de periodo de previsao."""
        types = [
            ForecastPeriodType.DIARIO,
            ForecastPeriodType.SEMANAL,
            ForecastPeriodType.MENSAL,
            ForecastPeriodType.TRIMESTRAL,
        ]
        assert len(types) == 4

    def test_forecast_confidence_levels(self):
        """Testa niveis de confianca."""
        levels = [
            ForecastConfidence.MUITO_BAIXA,
            ForecastConfidence.BAIXA,
            ForecastConfidence.MEDIA,
            ForecastConfidence.ALTA,
            ForecastConfidence.MUITO_ALTA,
        ]
        assert len(levels) == 5

    def test_forecast_statuses(self):
        """Testa status de previsao."""
        statuses = [
            ForecastStatus.RASCUNHO,
            ForecastStatus.ATIVA,
            ForecastStatus.REVISADA,
            ForecastStatus.CONCLUIDA,
            ForecastStatus.ARQUIVADA,
        ]
        assert len(statuses) == 5

    def test_add_risk(self):
        """Testa adicao de risco."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_closing_balance=Decimal("15000.00"),
            risks=[],
        )

        forecast.add_risk(
            risk_type="inadimplencia",
            probability=0.3,
            impact=Decimal("5000.00"),
            mitigation="Intensificar cobranca",
        )

        assert len(forecast.risks) == 1
        assert forecast.risks[0]["type"] == "inadimplencia"

    def test_add_opportunity(self):
        """Testa adicao de oportunidade."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_closing_balance=Decimal("15000.00"),
            opportunities=[],
        )

        forecast.add_opportunity(
            opportunity_type="renegociacao",
            probability=0.6,
            value=Decimal("2000.00"),
            action="Solicitar propostas de outros fornecedores",
        )

        assert len(forecast.opportunities) == 1
        assert forecast.opportunities[0]["type"] == "renegociacao"

    def test_add_alert(self):
        """Testa adicao de alerta."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsao Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            forecast_date=date(2024, 1, 1),
            expected_closing_balance=Decimal("15000.00"),
            alerts=[],
        )

        forecast.add_alert(
            alert_type="saldo_baixo",
            severity="high",
            message="Saldo projetado abaixo do minimo recomendado",
            alert_date=date(2024, 1, 15),
            amount=Decimal("5000.00"),
        )

        assert len(forecast.alerts) == 1
        assert forecast.alerts[0]["type"] == "saldo_baixo"
        assert forecast.alerts[0]["severity"] == "high"
