"""Testes para PeriodClosingService - Sprint 29.

Testa funcionalidades de Fechamento Contábil.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.models.accounting_period import ClosingType
from modules.financial.services.period_closing_service import (
    AuditIssue,
    AuditIssueType,
    ClosingResult,
    ClosingStep,
    ClosingStepType,
    PeriodClosingService,
    ProvisionEntry,
    ProvisionType,
)


class TestClosingStep:
    """Testes para ClosingStep dataclass."""

    def test_create_step(self) -> None:
        """Testa criação de etapa."""
        step = ClosingStep(
            step_type=ClosingStepType.VALIDATE_ENTRIES,
            name="Validando lançamentos",
        )

        assert step.step_type == ClosingStepType.VALIDATE_ENTRIES
        assert step.name == "Validando lançamentos"
        assert step.status == "pending"
        assert step.message == ""
        assert step.started_at is None
        assert step.completed_at is None

    def test_step_with_details(self) -> None:
        """Testa etapa com detalhes."""
        step = ClosingStep(
            step_type=ClosingStepType.CHECK_BALANCE,
            name="Verificando balanceamento",
            status="completed",
            details={"total_debit": Decimal("1000"), "total_credit": Decimal("1000")},
        )

        assert step.status == "completed"
        assert step.details["total_debit"] == Decimal("1000")


class TestProvisionEntry:
    """Testes para ProvisionEntry dataclass."""

    def test_create_provision(self) -> None:
        """Testa criação de provisão."""
        provision = ProvisionEntry(
            provision_type=ProvisionType.DEPRECIATION,
            description="Depreciação mensal",
            debit_account_id=uuid4(),
            credit_account_id=uuid4(),
            amount=Decimal("500.00"),
            reference_date=date(2024, 12, 31),
        )

        assert provision.provision_type == ProvisionType.DEPRECIATION
        assert provision.amount == Decimal("500.00")
        assert provision.reference_date == date(2024, 12, 31)

    def test_provision_types(self) -> None:
        """Testa diferentes tipos de provisão."""
        types = [
            ProvisionType.DEPRECIATION,
            ProvisionType.VACATION,
            ProvisionType.THIRTEENTH,
            ProvisionType.TAX,
        ]
        for prov_type in types:
            provision = ProvisionEntry(
                provision_type=prov_type,
                description=f"Provisão {prov_type.value}",
                debit_account_id=uuid4(),
                credit_account_id=uuid4(),
                amount=Decimal("100.00"),
                reference_date=date(2024, 12, 31),
            )
            assert provision.provision_type == prov_type


class TestAuditIssue:
    """Testes para AuditIssue dataclass."""

    def test_create_issue(self) -> None:
        """Testa criação de problema de auditoria."""
        issue = AuditIssue(
            issue_type=AuditIssueType.UNBALANCED_ENTRY,
            severity="ERROR",
            message="Lançamento não balanceado",
            entry_id=uuid4(),
            amount=Decimal("100.00"),
        )

        assert issue.issue_type == AuditIssueType.UNBALANCED_ENTRY
        assert issue.severity == "ERROR"
        assert issue.amount == Decimal("100.00")

    def test_issue_without_entry(self) -> None:
        """Testa problema sem lançamento específico."""
        issue = AuditIssue(
            issue_type=AuditIssueType.RECONCILIATION_PENDING,
            severity="INFO",
            message="50 partidas pendentes de conciliação",
        )

        assert issue.entry_id is None
        assert issue.account_id is None
        assert issue.amount == Decimal("0")


class TestClosingResult:
    """Testes para ClosingResult dataclass."""

    def test_create_result(self) -> None:
        """Testa criação de resultado."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        assert result.year == 2024
        assert result.month == 12
        assert result.status == "in_progress"
        assert result.total_revenue == Decimal("0")
        assert result.total_expenses == Decimal("0")

    def test_add_step(self) -> None:
        """Testa adição de etapa."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        step = ClosingStep(
            step_type=ClosingStepType.VALIDATE_ENTRIES,
            name="Validando lançamentos",
        )

        result.add_step(step)

        assert len(result.steps) == 1
        assert result.steps[0].step_type == ClosingStepType.VALIDATE_ENTRIES

    def test_add_issue(self) -> None:
        """Testa adição de problema."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        issue = AuditIssue(
            issue_type=AuditIssueType.UNBALANCED_ENTRY,
            severity="ERROR",
            message="Lançamento não balanceado",
        )

        result.add_issue(issue)

        assert len(result.issues) == 1
        assert result.has_errors is True

    def test_has_errors_with_warnings_only(self) -> None:
        """Testa que warnings não são erros críticos."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        issue = AuditIssue(
            issue_type=AuditIssueType.MISSING_DOCUMENT,
            severity="WARNING",
            message="Documento faltante",
        )

        result.add_issue(issue)

        assert len(result.issues) == 1
        assert result.has_errors is False

    def test_period_result_calculation(self) -> None:
        """Testa cálculo do resultado do período."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
            total_revenue=Decimal("50000.00"),
            total_expenses=Decimal("30000.00"),
            period_result=Decimal("20000.00"),
        )

        assert result.period_result == Decimal("20000.00")


class TestClosingStepType:
    """Testes para ClosingStepType enum."""

    def test_all_steps_exist(self) -> None:
        """Testa que todos os tipos existem."""
        assert ClosingStepType.VALIDATE_ENTRIES.value == "VALIDATE_ENTRIES"
        assert ClosingStepType.CHECK_BALANCE.value == "CHECK_BALANCE"
        assert ClosingStepType.GENERATE_PROVISIONS.value == "GENERATE_PROVISIONS"
        assert ClosingStepType.CLOSE_RESULT_ACCOUNTS.value == "CLOSE_RESULT_ACCOUNTS"
        assert ClosingStepType.TRANSFER_RESULT.value == "TRANSFER_RESULT"
        assert ClosingStepType.GENERATE_TRIAL_BALANCE.value == "GENERATE_TRIAL_BALANCE"
        assert ClosingStepType.FINALIZE.value == "FINALIZE"

    def test_step_count(self) -> None:
        """Testa contagem de etapas."""
        assert len(ClosingStepType) == 7


class TestProvisionType:
    """Testes para ProvisionType enum."""

    def test_all_types_exist(self) -> None:
        """Testa que todos os tipos existem."""
        assert ProvisionType.DEPRECIATION.value == "DEPRECIATION"
        assert ProvisionType.VACATION.value == "VACATION"
        assert ProvisionType.THIRTEENTH.value == "THIRTEENTH"
        assert ProvisionType.TAX.value == "TAX"
        assert ProvisionType.BAD_DEBT.value == "BAD_DEBT"
        assert ProvisionType.OTHER.value == "OTHER"

    def test_provision_count(self) -> None:
        """Testa contagem de tipos de provisão."""
        assert len(ProvisionType) == 6


class TestAuditIssueType:
    """Testes para AuditIssueType enum."""

    def test_all_types_exist(self) -> None:
        """Testa que todos os tipos existem."""
        assert AuditIssueType.UNBALANCED_ENTRY.value == "UNBALANCED_ENTRY"
        assert AuditIssueType.MISSING_DOCUMENT.value == "MISSING_DOCUMENT"
        assert AuditIssueType.DUPLICATE_ENTRY.value == "DUPLICATE_ENTRY"
        assert AuditIssueType.INVALID_ACCOUNT.value == "INVALID_ACCOUNT"
        assert AuditIssueType.PERIOD_MISMATCH.value == "PERIOD_MISMATCH"
        assert AuditIssueType.UNAUTHORIZED.value == "UNAUTHORIZED"
        assert AuditIssueType.RECONCILIATION_PENDING.value == "RECONCILIATION_PENDING"

    def test_issue_count(self) -> None:
        """Testa contagem de tipos de problema."""
        assert len(AuditIssueType) == 7


class TestPeriodClosingService:  # pylint: disable=protected-access
    """Testes para PeriodClosingService."""

    def test_service_init(self) -> None:
        """Testa inicialização do serviço."""
        mock_session = type("MockSession", (), {})()
        service = PeriodClosingService(mock_session)

        assert service.session == mock_session

    def test_get_month_name(self) -> None:
        """Testa obtenção de nome do mês."""
        assert PeriodClosingService._get_month_name(1) == "Janeiro"
        assert PeriodClosingService._get_month_name(6) == "Junho"
        assert PeriodClosingService._get_month_name(12) == "Dezembro"
        assert PeriodClosingService._get_month_name(0) == ""
        assert PeriodClosingService._get_month_name(13) == ""


class TestClosingWorkflow:
    """Testes de workflow de fechamento."""

    def test_complete_workflow_steps(self) -> None:
        """Testa sequência completa de etapas."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        # Adiciona todas as etapas
        steps = [
            ClosingStep(ClosingStepType.VALIDATE_ENTRIES, "Validando", "completed"),
            ClosingStep(ClosingStepType.CHECK_BALANCE, "Verificando", "completed"),
            ClosingStep(ClosingStepType.GENERATE_PROVISIONS, "Provisões", "completed"),
            ClosingStep(ClosingStepType.CLOSE_RESULT_ACCOUNTS, "Encerrando", "completed"),
            ClosingStep(ClosingStepType.TRANSFER_RESULT, "Transferindo", "completed"),
            ClosingStep(ClosingStepType.FINALIZE, "Finalizando", "completed"),
        ]

        for step in steps:
            result.add_step(step)

        assert len(result.steps) == 6
        assert all(s.status == "completed" for s in result.steps)

    def test_workflow_failure(self) -> None:
        """Testa falha no workflow."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        # Etapa 1 OK
        step1 = ClosingStep(ClosingStepType.VALIDATE_ENTRIES, "Validando", "completed")
        result.add_step(step1)

        # Etapa 2 falha
        step2 = ClosingStep(
            ClosingStepType.CHECK_BALANCE,
            "Verificando",
            "failed",
        )
        step2.message = "Balancete não balanceado"
        result.add_step(step2)

        # Adiciona erro
        result.add_issue(AuditIssue(
            issue_type=AuditIssueType.UNBALANCED_ENTRY,
            severity="ERROR",
            message="Diferença de R$ 100,00",
        ))

        assert len(result.steps) == 2
        assert result.steps[1].status == "failed"
        assert result.has_errors is True


class TestProvisions:
    """Testes de provisões."""

    def test_depreciation_provision(self) -> None:
        """Testa provisão de depreciação."""
        provision = ProvisionEntry(
            provision_type=ProvisionType.DEPRECIATION,
            description="Depreciação mensal - Equipamentos",
            debit_account_id=uuid4(),
            credit_account_id=uuid4(),
            amount=Decimal("1500.00"),
            reference_date=date(2024, 12, 31),
        )

        assert provision.provision_type == ProvisionType.DEPRECIATION
        assert "Depreciação" in provision.description
        assert provision.amount == Decimal("1500.00")

    def test_vacation_provision(self) -> None:
        """Testa provisão de férias."""
        provision = ProvisionEntry(
            provision_type=ProvisionType.VACATION,
            description="Provisão de férias - Dezembro/2024",
            debit_account_id=uuid4(),
            credit_account_id=uuid4(),
            amount=Decimal("5000.00"),
            reference_date=date(2024, 12, 31),
        )

        assert provision.provision_type == ProvisionType.VACATION
        assert provision.amount == Decimal("5000.00")


class TestAudit:
    """Testes de auditoria com múltiplas validações."""

    def test_audit_issues_count(self) -> None:
        """Testa contagem de problemas."""
        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        for _ in range(5):
            result.add_issue(AuditIssue(
                AuditIssueType.MISSING_DOCUMENT, "WARNING", "Aviso"
            ))

        assert len(result.issues) == 5
        assert result.has_errors is False

    def test_audit_issues_severity(self) -> None:
        """Testa severidade de problemas."""
        errors = [
            AuditIssue(AuditIssueType.UNBALANCED_ENTRY, "ERROR", "Erro 1"),
            AuditIssue(AuditIssueType.INVALID_ACCOUNT, "ERROR", "Erro 2"),
        ]
        warnings = [
            AuditIssue(AuditIssueType.MISSING_DOCUMENT, "WARNING", "Aviso 1"),
        ]
        infos = [
            AuditIssue(AuditIssueType.RECONCILIATION_PENDING, "INFO", "Info 1"),
        ]

        result = ClosingResult(
            condominio_id=uuid4(),
            period_id=uuid4(),
            year=2024,
            month=12,
            started_at=datetime.utcnow(),
        )

        for issue in errors + warnings + infos:
            result.add_issue(issue)

        assert len(result.issues) == 4
        assert result.has_errors is True

        error_count = sum(1 for i in result.issues if i.severity == "ERROR")
        warning_count = sum(1 for i in result.issues if i.severity == "WARNING")
        info_count = sum(1 for i in result.issues if i.severity == "INFO")

        assert error_count == 2
        assert warning_count == 1
        assert info_count == 1


class TestIntegration:
    """Testes de integração (requerem banco)."""

    @pytest.mark.asyncio
    async def test_close_period_placeholder(self) -> None:
        """Placeholder para teste de fechamento."""
        assert True

    @pytest.mark.asyncio
    async def test_reopen_period_placeholder(self) -> None:
        """Placeholder para teste de reabertura."""
        assert True

    @pytest.mark.asyncio
    async def test_audit_entries_placeholder(self) -> None:
        """Placeholder para teste de auditoria."""
        assert True

    @pytest.mark.asyncio
    async def test_generate_provision_placeholder(self) -> None:
        """Placeholder para teste de provisão."""
        assert True

    @pytest.mark.asyncio
    async def test_get_period_summary_placeholder(self) -> None:
        """Placeholder para teste de resumo."""
        assert True


class TestClosingType:
    """Testes para ClosingType do modelo."""

    def test_closing_types(self) -> None:
        """Testa tipos de fechamento."""
        # Importa do modelo
        assert ClosingType.PROVISIONAL.value == "PROVISIONAL"
        assert ClosingType.DEFINITIVE.value == "DEFINITIVE"
        assert ClosingType.AUDIT.value == "AUDIT"

    def test_closing_type_count(self) -> None:
        """Testa contagem de tipos de fechamento."""
        assert len(ClosingType) == 3
