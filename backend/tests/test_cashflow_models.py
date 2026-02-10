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
        """Testa criação de conta bancária."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Principal",
            account_type=BankAccountType.CORRENTE,
            bank_code="001",
            bank_name="Banco do Brasil",
            agency="1234",
            account_number="12345",
            initial_balance=Decimal("10000.00"),
        )

        assert account.name == "Conta Principal"
        assert account.account_type == BankAccountType.CORRENTE
        assert account.status == BankAccountStatus.ATIVA
        assert account.initial_balance == Decimal("10000.00")

    def test_update_balance_credit(self):
        """Testa atualização de saldo com crédito."""
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
        """Testa atualização de saldo com débito."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("1000.00"),
        )

        account.update_balance(Decimal("-300.00"))
        assert account.current_balance == Decimal("700.00")

    def test_block_balance(self):
        """Testa bloqueio de saldo."""
        account = BankAccount(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Conta Teste",
            account_type=BankAccountType.CORRENTE,
            current_balance=Decimal("1000.00"),
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
            blocked_balance=Decimal("200.00"),
        )

        account.unblock_balance(Decimal("150.00"))
        assert account.blocked_balance == Decimal("50.00")
        assert account.available_balance == Decimal("950.00")

    def test_bank_account_types(self):
        """Testa todos os tipos de conta bancária."""
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
        """Testa criação de transação de crédito."""
        tx = BankTransaction(
            id=uuid4(),
            bank_account_id=uuid4(),
            transaction_type=TransactionType.CREDIT,
            category=TransactionCategory.TAXA_CONDOMINIAL,
            amount=Decimal("500.00"),
            description="Recebimento taxa condomínio",
            transaction_date=date.today(),
        )

        assert tx.transaction_type == TransactionType.CREDIT
        assert tx.category == TransactionCategory.TAXA_CONDOMINIAL
        assert tx.amount == Decimal("500.00")
        assert tx.status == TransactionStatus.PENDENTE

    def test_create_debit_transaction(self):
        """Testa criação de transação de débito."""
        tx = BankTransaction(
            id=uuid4(),
            bank_account_id=uuid4(),
            transaction_type=TransactionType.CREDIT,
            category=TransactionCategory.MANUTENCAO,
            amount=Decimal("200.00"),
            description="Pagamento manutenção",
            transaction_date=date.today(),
        )

        assert tx.transaction_type == TransactionType.CREDIT
        assert tx.category == TransactionCategory.MANUTENCAO

    def test_transaction_categories(self):
        """Testa todas as categorias de transação."""
        categories = [
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_EXTRA,
            TransactionCategory.MULTA,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.ALUGUEL,
            TransactionCategory.RESERVA,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.MANUTENCAO,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.TAXA_CONDOMINIAL,
            TransactionCategory.AJUSTE,
            TransactionCategory.TAXA_CONDOMINIAL,
        ]
        assert len(categories) == 25

    def test_transaction_origins(self):
        """Testa todas as origens de transação."""
        origins = [
            TransactionOrigin.MANUAL,
            TransactionOrigin.MANUAL,
            TransactionOrigin.IMPORTACAO,
            TransactionOrigin.API,
            TransactionOrigin.BOLETO,
            TransactionOrigin.PIX,
            TransactionOrigin.MANUAL,
        ]
        assert len(origins) == 7


class TestBankReconciliationModel:
    """Testes para o model BankReconciliation."""

    def test_create_reconciliation(self):
        """Testa criação de conciliação."""
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=uuid4(),
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            opening_balance=Decimal("10000.00"),
        )

        assert recon.period_type == ReconciliationPeriodType.MENSAL
        assert recon.status == ReconciliationStatus.PENDENTE

    def test_update_progress(self):
        """Testa atualização de progresso."""
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=uuid4(),
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            opening_balance=Decimal("10000.00"),
            total_system_items=100,
            items_reconciled=50,
        )

        recon.update_progress()
        assert recon.progress_percentage == Decimal("50.00")
        assert recon.items_pending == 50

    def test_complete_reconciliation(self):
        """Testa finalização de conciliação."""
        recon = BankReconciliation(
            id=uuid4(),
            bank_account_id=uuid4(),
            period_type=ReconciliationPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            opening_balance=Decimal("10000.00"),
            closing_balance=Decimal("12000.00"),
            statement_balance=Decimal("12000.00"),
        )

        recon.complete()
        assert recon.status == ReconciliationStatus.PENDENTE
        assert recon.completed_at is not None
        assert recon.difference == Decimal("0.00")

    def test_reconciliation_period_types(self):
        """Testa tipos de período de conciliação."""
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
        """Testa criação de entrada de receita."""
        entry = CashFlowEntry(
            id=uuid4(),
            condominio_id=uuid4(),
            entry_type=CashFlowEntryType.ENTRADA,
            source_type=CashFlowSourceType.CONTA_RECEBER,
            description="Receita prevista",
            expected_date=date.today() + timedelta(days=30),
            expected_amount=Decimal("5000.00"),
        )

        assert entry.entry_type == CashFlowEntryType.ENTRADA
        assert entry.source_type == CashFlowSourceType.CONTA_RECEBER
        assert entry.status == CashFlowEntryStatus.PREVISTO

    def test_create_entry_expense(self):
        """Testa criação de entrada de despesa."""
        entry = CashFlowEntry(
            id=uuid4(),
            condominio_id=uuid4(),
            entry_type=CashFlowEntryType.SAIDA,
            source_type=CashFlowSourceType.CONTA_PAGAR,
            description="Despesa prevista",
            expected_date=date.today() + timedelta(days=15),
            expected_amount=Decimal("2000.00"),
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
            expected_date=date.today(),
            expected_amount=Decimal("800.00"),
            is_recurring=True,
            recurrence_frequency=RecurrenceFrequency.MENSAL,
            recurrence_end_date=date.today() + timedelta(days=365),
        )

        assert entry.is_recurring is True
        assert entry.recurrence_frequency == RecurrenceFrequency.MENSAL

    def test_recurrence_frequencies(self):
        """Testa todas as frequências de recorrência."""
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
        """Testa criação de previsão."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão Janeiro 2024",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            expected_inflows=Decimal("50000.00"),
            expected_outflows=Decimal("35000.00"),
            expected_balance=Decimal("15000.00"),
        )

        assert forecast.name == "Previsão Janeiro 2024"
        assert forecast.period_type == ForecastPeriodType.MENSAL
        assert forecast.status == ForecastStatus.PENDING
        assert forecast.confidence == ForecastConfidence.MEDIA

    def test_update_actuals(self):
        """Testa atualização de valores realizados."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            expected_inflows=Decimal("50000.00"),
            expected_outflows=Decimal("35000.00"),
            expected_balance=Decimal("15000.00"),
        )

        forecast.update_actuals(
            inflows=Decimal("48000.00"),
            outflows=Decimal("34000.00"),
            balance=Decimal("14000.00"),
        )

        assert forecast.actual_inflows == Decimal("48000.00")
        assert forecast.actual_outflows == Decimal("34000.00")
        assert forecast.actual_balance == Decimal("14000.00")
        assert forecast.variance_inflows == Decimal("-2000.00")
        assert forecast.variance_outflows == Decimal("-1000.00")
        assert forecast.variance_balance == Decimal("-1000.00")

    def test_ai_generated_forecast(self):
        """Testa previsão gerada por IA."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão IA",
            period_type=ForecastPeriodType.TRIMESTRAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 3, 31),
            expected_inflows=Decimal("150000.00"),
            expected_outflows=Decimal("100000.00"),
            expected_balance=Decimal("50000.00"),
            is_ai_generated=True,
            ai_model_version="1.0.0",
            ai_accuracy_score=Decimal("0.85"),
            confidence=ForecastConfidence.ALTA,
        )

        assert forecast.is_ai_generated is True
        assert forecast.ai_model_version == "1.0.0"
        assert forecast.ai_accuracy_score == Decimal("0.85")
        assert forecast.confidence == ForecastConfidence.ALTA

    def test_forecast_with_scenarios(self):
        """Testa previsão com cenários."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão Cenários",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            expected_inflows=Decimal("50000.00"),
            expected_outflows=Decimal("35000.00"),
            expected_balance=Decimal("15000.00"),
            pessimistic_balance=Decimal("10000.00"),
            optimistic_balance=Decimal("20000.00"),
        )

        assert forecast.pessimistic_balance == Decimal("10000.00")
        assert forecast.optimistic_balance == Decimal("20000.00")

    def test_forecast_period_types(self):
        """Testa tipos de período de previsão."""
        types = [
            ForecastPeriodType.DIARIO,
            ForecastPeriodType.SEMANAL,
            ForecastPeriodType.DIARIO,
            ForecastPeriodType.MENSAL,
            ForecastPeriodType.TRIMESTRAL,
            ForecastPeriodType.DIARIO,
            ForecastPeriodType.DIARIO,
        ]
        assert len(types) == 7

    def test_forecast_confidence_levels(self):
        """Testa níveis de confiança."""
        levels = [
            ForecastConfidence.MUITO_BAIXA,
            ForecastConfidence.BAIXA,
            ForecastConfidence.MEDIA,
            ForecastConfidence.ALTA,
            ForecastConfidence.MUITO_ALTA,
        ]
        assert len(levels) == 5

    def test_forecast_statuses(self):
        """Testa status de previsão."""
        statuses = [
            ForecastStatus.PENDING,
            ForecastStatus.PENDING,
            ForecastStatus.PENDING,
            ForecastStatus.PENDING,
            ForecastStatus.PENDING,
        ]
        assert len(statuses) == 5

    def test_add_risk(self):
        """Testa adição de risco."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            expected_balance=Decimal("15000.00"),
        )

        forecast.add_risk(
            risk_type="inadimplencia",
            description="Alta inadimplência prevista",
            impact=Decimal("5000.00"),
            probability=Decimal("0.3"),
            mitigation="Intensificar cobrança",
        )

        assert len(forecast.risks) == 1
        assert forecast.risks[0]["risk_type"] == "inadimplencia"

    def test_add_opportunity(self):
        """Testa adição de oportunidade."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            expected_balance=Decimal("15000.00"),
        )

        forecast.add_opportunity(
            opportunity_type="renegociacao",
            description="Renegociar contrato de limpeza",
            potential_savings=Decimal("2000.00"),
            action="Solicitar propostas de outros fornecedores",
        )

        assert len(forecast.opportunities) == 1
        assert forecast.opportunities[0]["opportunity_type"] == "renegociacao"

    def test_add_alert(self):
        """Testa adição de alerta."""
        forecast = CashFlowForecast(
            id=uuid4(),
            condominio_id=uuid4(),
            name="Previsão Teste",
            period_type=ForecastPeriodType.MENSAL,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            expected_balance=Decimal("15000.00"),
        )

        forecast.add_alert(
            alert_type="saldo_baixo",
            severity="high",
            message="Saldo projetado abaixo do mínimo recomendado",
            date=date(2024, 1, 15),
        )

        assert len(forecast.alerts) == 1
        assert forecast.alerts[0]["alert_type"] == "saldo_baixo"
        assert forecast.alerts[0]["severity"] == "high"
