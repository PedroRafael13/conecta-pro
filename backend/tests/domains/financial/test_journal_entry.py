"""
tests/domains/financial/test_journal_entry.py - JOURNAL ENTRY TESTS
===================================================================
Enterprise tests for double-entry accounting
"""

import sys
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend")

from domains.financial import JournalEntryEntity, JournalEntryStatus, JournalEntryType, JournalLine, TransactionSource


class TestJournalLine:
    """Testes para linha de lancamento."""

    def test_create_debit_line(self):
        """Testa criacao de linha de debito."""
        line = JournalLine(
            account_id=uuid4(),
            account_code="1.1.1.01",
            account_name="Caixa",
            debit_amount=Decimal("1000.00"),
            credit_amount=Decimal("0"),
            description="Recebimento",
        )

        assert line.is_debit is True
        assert line.is_credit is False
        assert line.amount == Decimal("1000.00")
        assert line.signed_amount == Decimal("1000.00")

    def test_create_credit_line(self):
        """Testa criacao de linha de credito."""
        line = JournalLine(
            account_id=uuid4(),
            account_code="3.1.1.01",
            account_name="Receita",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("1000.00"),
            description="Venda",
        )

        assert line.is_debit is False
        assert line.is_credit is True
        assert line.amount == Decimal("1000.00")
        assert line.signed_amount == Decimal("-1000.00")

    def test_reject_line_with_both_debit_and_credit(self):
        """Testa rejeicao de linha com debito e credito."""
        with pytest.raises(ValueError, match="debito OU credito"):
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.01",
                account_name="Caixa",
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("500.00"),
                description="Invalido",
            )

    def test_reject_line_with_zero_amounts(self):
        """Testa rejeicao de linha sem valores."""
        with pytest.raises(ValueError, match="debito ou credito"):
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.01",
                account_name="Caixa",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("0"),
                description="Invalido",
            )


class TestJournalEntry:
    """Testes para lancamento contabil."""

    @pytest.fixture
    def balanced_lines(self) -> list:
        """Fixture para linhas balanceadas."""
        return [
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.01",
                account_name="Caixa",
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("0"),
                description="Recebimento",
            ),
            JournalLine(
                account_id=uuid4(),
                account_code="3.1.1.01",
                account_name="Receita",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("1000.00"),
                description="Venda",
            ),
        ]

    @pytest.fixture
    def sample_entry(self, balanced_lines: list) -> JournalEntryEntity:
        """Fixture para lancamento de exemplo."""
        return JournalEntryEntity(
            entry_number="LC-2024-00000001",
            entry_type=JournalEntryType.STANDARD,
            source=TransactionSource.MANUAL,
            entry_date=date.today(),
            period_month=date.today().month,
            period_year=date.today().year,
            description="Lancamento de teste",
            lines=balanced_lines,
            tenant_id=uuid4(),
            created_by="test-user",
        )

    def test_create_balanced_entry(self, sample_entry: JournalEntryEntity):
        """Testa criacao de lancamento balanceado."""
        assert sample_entry.is_balanced is True
        assert sample_entry.total_debits == Decimal("1000.00")
        assert sample_entry.total_credits == Decimal("1000.00")
        assert sample_entry.status == JournalEntryStatus.DRAFT

    def test_reject_unbalanced_entry(self):
        """Testa rejeicao de lancamento desbalanceado."""
        unbalanced_lines = [
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.01",
                account_name="Caixa",
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("0"),
                description="Recebimento",
            ),
            JournalLine(
                account_id=uuid4(),
                account_code="3.1.1.01",
                account_name="Receita",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("800.00"),  # Desbalanceado
                description="Venda",
            ),
        ]

        with pytest.raises(ValueError, match="desbalanceado"):
            JournalEntryEntity(
                entry_number="LC-2024-00000001",
                entry_type=JournalEntryType.STANDARD,
                entry_date=date.today(),
                period_month=date.today().month,
                period_year=date.today().year,
                description="Teste desbalanceado",
                lines=unbalanced_lines,
                tenant_id=uuid4(),
                created_by="test-user",
            )

    def test_submit_for_approval(self, sample_entry: JournalEntryEntity):
        """Testa submissao para aprovacao."""
        result = sample_entry.submit_for_approval("test-user")

        assert result is True
        assert sample_entry.status == JournalEntryStatus.PENDING_APPROVAL
        assert len(sample_entry.audit_trail) == 1
        assert sample_entry.audit_trail[0].action == "submitted_for_approval"

    def test_approve_entry(self, sample_entry: JournalEntryEntity):
        """Testa aprovacao de lancamento."""
        sample_entry.submit_for_approval("creator-user")
        result = sample_entry.approve("approver-user", "Aprovador")

        assert result is True
        assert sample_entry.status == JournalEntryStatus.APPROVED
        assert sample_entry.approved_by == "approver-user"
        assert sample_entry.approved_at is not None

    def test_reject_self_approval(self, sample_entry: JournalEntryEntity):
        """Testa rejeicao de auto-aprovacao."""
        sample_entry.submit_for_approval("same-user")

        with pytest.raises(ValueError, match="diferente do criador"):
            sample_entry.approve("test-user", "Mesmo Usuario")

    def test_post_entry(self, sample_entry: JournalEntryEntity):
        """Testa contabilizacao de lancamento."""
        sample_entry.submit_for_approval("creator")
        sample_entry.approve("approver", "Aprovador")
        result = sample_entry.post("poster", "Contabilista")

        assert result is True
        assert sample_entry.status == JournalEntryStatus.POSTED
        assert sample_entry.posting_date is not None
        assert sample_entry.can_be_edited is False
        assert sample_entry.can_be_reversed is True

    def test_create_reversal(self, sample_entry: JournalEntryEntity):
        """Testa criacao de estorno."""
        # Fluxo completo ate contabilizacao
        sample_entry.submit_for_approval("creator")
        sample_entry.approve("approver", "Aprovador")
        sample_entry.post("poster", "Contabilista")

        # Cria estorno
        reversal = sample_entry.create_reversal(
            user_id="reverser", reason="Lancamento incorreto", reversal_date=date.today()
        )

        assert reversal.is_reversal is True
        assert reversal.reversed_entry_id == sample_entry.entry_id
        assert reversal.entry_type == JournalEntryType.REVERSAL
        # Debitos e creditos invertidos
        assert reversal.total_debits == sample_entry.total_credits
        assert reversal.total_credits == sample_entry.total_debits


class TestDoubleEntryValidation:
    """Testes especificos para validacao de partida dobrada."""

    def test_multiple_debits_single_credit(self):
        """Testa multiplos debitos com um credito."""
        lines = [
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.01",
                account_name="Caixa",
                debit_amount=Decimal("500.00"),
                credit_amount=Decimal("0"),
                description="Caixa 1",
            ),
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.02",
                account_name="Banco",
                debit_amount=Decimal("500.00"),
                credit_amount=Decimal("0"),
                description="Banco",
            ),
            JournalLine(
                account_id=uuid4(),
                account_code="3.1.1.01",
                account_name="Receita",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("1000.00"),
                description="Venda",
            ),
        ]

        entry = JournalEntryEntity(
            entry_number="LC-2024-00000002",
            entry_type=JournalEntryType.STANDARD,
            entry_date=date.today(),
            period_month=date.today().month,
            period_year=date.today().year,
            description="Multiplos debitos",
            lines=lines,
            tenant_id=uuid4(),
            created_by="test-user",
        )

        assert entry.is_balanced is True
        assert len(entry.get_debit_lines()) == 2
        assert len(entry.get_credit_lines()) == 1

    def test_compound_entry(self):
        """Testa lancamento composto (multiplos debitos e creditos)."""
        lines = [
            # Debitos
            JournalLine(
                account_id=uuid4(),
                account_code="4.1.1.01",
                account_name="CMV",
                debit_amount=Decimal("600.00"),
                credit_amount=Decimal("0"),
                description="Custo",
            ),
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.1.01",
                account_name="Caixa",
                debit_amount=Decimal("1000.00"),
                credit_amount=Decimal("0"),
                description="Recebimento",
            ),
            # Creditos
            JournalLine(
                account_id=uuid4(),
                account_code="1.1.3.01",
                account_name="Estoque",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("600.00"),
                description="Baixa estoque",
            ),
            JournalLine(
                account_id=uuid4(),
                account_code="3.1.1.01",
                account_name="Receita",
                debit_amount=Decimal("0"),
                credit_amount=Decimal("1000.00"),
                description="Venda",
            ),
        ]

        entry = JournalEntryEntity(
            entry_number="LC-2024-00000003",
            entry_type=JournalEntryType.STANDARD,
            entry_date=date.today(),
            period_month=date.today().month,
            period_year=date.today().year,
            description="Venda com baixa de estoque",
            lines=lines,
            tenant_id=uuid4(),
            created_by="test-user",
        )

        assert entry.is_balanced is True
        assert entry.total_debits == Decimal("1600.00")
        assert entry.total_credits == Decimal("1600.00")
        assert len(entry.get_accounts_affected()) == 4
