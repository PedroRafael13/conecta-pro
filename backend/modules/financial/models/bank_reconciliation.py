"""Model para conciliacao bancaria."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class ReconciliationPeriodType(str, Enum):
    """Tipo de periodo de conciliacao."""

    DIARIO = "diario"
    SEMANAL = "semanal"
    QUINZENAL = "quinzenal"
    MENSAL = "mensal"
    PERSONALIZADO = "personalizado"


class ReconciliationStatus(str, Enum):
    """Status da conciliacao."""

    RASCUNHO = "rascunho"
    EM_ANDAMENTO = "em_andamento"
    PARCIAL = "parcial"
    CONCLUIDA = "concluida"
    DIVERGENTE = "divergente"
    CANCELADA = "cancelada"


class BankReconciliation(Base):
    """Conciliacao bancaria."""

    __tablename__ = "bank_reconciliations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bank_accounts.id"),
        nullable=False,
        index=True,
    )
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    reference = Column(String(50), nullable=True)  # Referencia (ex: "2025/01")
    description = Column(Text, nullable=True)

    # Periodo
    period_type = Column(
        String(20),
        nullable=False,
        default=ReconciliationPeriodType.MENSAL.value,
    )
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Saldos do sistema
    system_opening_balance = Column(Numeric(15, 2), nullable=False)  # Saldo inicial sistema
    system_closing_balance = Column(Numeric(15, 2), nullable=True)  # Saldo final sistema
    system_credits = Column(Numeric(15, 2), default=Decimal("0"))  # Total creditos sistema
    system_debits = Column(Numeric(15, 2), default=Decimal("0"))  # Total debitos sistema

    # Saldos do extrato bancario
    bank_opening_balance = Column(Numeric(15, 2), nullable=True)  # Saldo inicial extrato
    bank_closing_balance = Column(Numeric(15, 2), nullable=True)  # Saldo final extrato
    bank_credits = Column(Numeric(15, 2), default=Decimal("0"))  # Total creditos extrato
    bank_debits = Column(Numeric(15, 2), default=Decimal("0"))  # Total debitos extrato

    # Diferencas
    opening_difference = Column(Numeric(15, 2), default=Decimal("0"))  # Diferenca saldo inicial
    closing_difference = Column(Numeric(15, 2), default=Decimal("0"))  # Diferenca saldo final
    credits_difference = Column(Numeric(15, 2), default=Decimal("0"))  # Diferenca creditos
    debits_difference = Column(Numeric(15, 2), default=Decimal("0"))  # Diferenca debitos

    # Contadores
    total_system_transactions = Column(Integer, default=0)
    total_bank_transactions = Column(Integer, default=0)
    reconciled_count = Column(Integer, default=0)  # Conciliadas
    pending_system_count = Column(Integer, default=0)  # Pendentes no sistema
    pending_bank_count = Column(Integer, default=0)  # Pendentes no extrato
    divergent_count = Column(Integer, default=0)  # Divergentes

    # Status
    status = Column(
        String(20),
        nullable=False,
        default=ReconciliationStatus.RASCUNHO.value,
    )

    # Progresso
    reconciliation_progress = Column(Numeric(5, 2), default=Decimal("0"))  # 0-100%
    auto_reconciled_count = Column(Integer, default=0)  # Conciliadas automaticamente
    manual_reconciled_count = Column(Integer, default=0)  # Conciliadas manualmente

    # Importacao de extrato
    statement_imported = Column(Boolean, default=False)
    statement_file_name = Column(String(255), nullable=True)
    statement_file_path = Column(String(500), nullable=True)
    statement_format = Column(String(20), nullable=True)  # ofx, cnab, csv, pdf
    statement_imported_at = Column(DateTime, nullable=True)
    statement_imported_by = Column(UUID(as_uuid=True), nullable=True)

    # Datas de execucao
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Responsaveis
    started_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Ajustes
    adjustments = Column(JSONB, default=list)
    # [{"type": "credito/debito", "amount": 100, "description": "...", "created_at": "..."}]
    total_adjustments = Column(Numeric(15, 2), default=Decimal("0"))

    # Itens pendentes/divergentes
    pending_items = Column(JSONB, default=list)  # IDs de transacoes pendentes
    divergent_items = Column(JSONB, default=list)  # IDs de transacoes divergentes

    # Observacoes
    notes = Column(Text, nullable=True)
    review_notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_bank_reconciliations_account", "bank_account_id"),
        Index("ix_bank_reconciliations_condominio", "condominio_id"),
        Index("ix_bank_reconciliations_period", "period_start", "period_end"),
        Index("ix_bank_reconciliations_status", "status"),
        Index(
            "ix_bank_reconciliations_unique",
            "bank_account_id",
            "period_start",
            "period_end",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return f"<BankReconciliation {self.reference} - {self.status}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se esta concluida."""
        return self.status == ReconciliationStatus.CONCLUIDA.value

    @property
    def is_in_progress(self) -> bool:
        """Verifica se esta em andamento."""
        return self.status == ReconciliationStatus.EM_ANDAMENTO.value

    @property
    def has_differences(self) -> bool:
        """Verifica se ha diferencas."""
        return self.closing_difference != Decimal("0") or self.divergent_count > 0

    @property
    def is_balanced(self) -> bool:
        """Verifica se esta balanceada (sem diferencas)."""
        return (
            self.closing_difference == Decimal("0")
            and self.divergent_count == 0
            and self.pending_system_count == 0
            and self.pending_bank_count == 0
        )

    @property
    def total_pending(self) -> int:
        """Total de itens pendentes."""
        return self.pending_system_count + self.pending_bank_count

    def calculate_differences(self) -> None:
        """Calcula diferencas entre sistema e extrato."""
        self.opening_difference = (self.bank_opening_balance or Decimal("0")) - (
            self.system_opening_balance or Decimal("0")
        )
        self.closing_difference = (self.bank_closing_balance or Decimal("0")) - (
            self.system_closing_balance or Decimal("0")
        )
        self.credits_difference = (self.bank_credits or Decimal("0")) - (
            self.system_credits or Decimal("0")
        )
        self.debits_difference = (self.bank_debits or Decimal("0")) - (
            self.system_debits or Decimal("0")
        )

    def calculate_progress(self) -> None:
        """Calcula progresso da conciliacao."""
        total = self.total_system_transactions + self.total_bank_transactions
        if total == 0:
            self.reconciliation_progress = Decimal("100")
            return
        reconciled = self.reconciled_count * 2  # Cada conciliacao casa 2 itens
        self.reconciliation_progress = Decimal(str(min(100, (reconciled / total) * 100)))

    def start(self, user_id: uuid.UUID) -> None:
        """Inicia a conciliacao."""
        self.status = ReconciliationStatus.EM_ANDAMENTO.value
        self.started_at = datetime.utcnow()
        self.started_by = user_id

    def complete(self, user_id: uuid.UUID) -> None:
        """Conclui a conciliacao."""
        if self.has_differences:
            self.status = ReconciliationStatus.DIVERGENTE.value
        else:
            self.status = ReconciliationStatus.CONCLUIDA.value
        self.completed_at = datetime.utcnow()
        self.completed_by = user_id
        self.calculate_progress()

    def mark_as_partial(self) -> None:
        """Marca como parcialmente concluida."""
        self.status = ReconciliationStatus.PARCIAL.value
        self.calculate_progress()

    def cancel(self) -> None:
        """Cancela a conciliacao."""
        self.status = ReconciliationStatus.CANCELADA.value

    def add_adjustment(
        self,
        adjustment_type: str,
        amount: Decimal,
        description: str,
        user_id: uuid.UUID,
    ) -> None:
        """Adiciona ajuste a conciliacao."""
        if self.adjustments is None:
            self.adjustments = []

        adjustment = {
            "id": str(uuid.uuid4()),
            "type": adjustment_type,
            "amount": float(amount),
            "description": description,
            "created_by": str(user_id),
            "created_at": datetime.utcnow().isoformat(),
        }
        self.adjustments.append(adjustment)

        # Atualiza total de ajustes
        if adjustment_type == "credito":
            self.total_adjustments = (self.total_adjustments or Decimal("0")) + amount
        else:
            self.total_adjustments = (self.total_adjustments or Decimal("0")) - amount

    def review(self, user_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Marca como revisada."""
        self.reviewed_by = user_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes

    def import_statement(
        self,
        file_name: str,
        file_path: str,
        format_type: str,
        user_id: uuid.UUID,
    ) -> None:
        """Registra importacao de extrato."""
        self.statement_imported = True
        self.statement_file_name = file_name
        self.statement_file_path = file_path
        self.statement_format = format_type
        self.statement_imported_at = datetime.utcnow()
        self.statement_imported_by = user_id

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "bank_account_id": str(self.bank_account_id),
            "condominio_id": str(self.condominio_id),
            "reference": self.reference,
            "period_type": self.period_type,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "system_opening_balance": float(self.system_opening_balance or 0),
            "system_closing_balance": float(self.system_closing_balance or 0),
            "bank_opening_balance": float(self.bank_opening_balance or 0),
            "bank_closing_balance": float(self.bank_closing_balance or 0),
            "closing_difference": float(self.closing_difference or 0),
            "status": self.status,
            "reconciliation_progress": float(self.reconciliation_progress or 0),
            "reconciled_count": self.reconciled_count,
            "pending_system_count": self.pending_system_count,
            "pending_bank_count": self.pending_bank_count,
            "divergent_count": self.divergent_count,
            "is_completed": self.is_completed,
            "is_balanced": self.is_balanced,
            "has_differences": self.has_differences,
            "statement_imported": self.statement_imported,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
