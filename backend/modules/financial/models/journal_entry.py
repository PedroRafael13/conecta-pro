"""Journal Entry model - Lançamento Contábil."""

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.accounting_account import AccountingAccount
    from modules.financial.models.accounting_period import AccountingPeriod
    from modules.financial.models.cost_center import CostCenter


class EntryType(str, enum.Enum):
    """Tipo do lançamento contábil."""

    MANUAL = "MANUAL"  # Manual
    AUTOMATIC = "AUTOMATIC"  # Automático (integração)
    IMPORT = "IMPORT"  # Importação
    ADJUSTMENT = "ADJUSTMENT"  # Ajuste
    OPENING = "OPENING"  # Abertura
    CLOSING = "CLOSING"  # Encerramento
    REVERSAL = "REVERSAL"  # Estorno
    PROVISION = "PROVISION"  # Provisão
    DEPRECIATION = "DEPRECIATION"  # Depreciação
    RECLASSIFICATION = "RECLASSIFICATION"  # Reclassificação


class EntryStatus(str, enum.Enum):
    """Status do lançamento contábil."""

    DRAFT = "DRAFT"  # Rascunho
    PENDING = "PENDING"  # Pendente de aprovação
    APPROVED = "APPROVED"  # Aprovado
    POSTED = "POSTED"  # Contabilizado
    REVERSED = "REVERSED"  # Estornado
    CANCELLED = "CANCELLED"  # Cancelado


class EntryOrigin(str, enum.Enum):
    """Origem do lançamento."""

    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"  # Contas a Pagar
    ACCOUNTS_RECEIVABLE = "ACCOUNTS_RECEIVABLE"  # Contas a Receber
    CASH_FLOW = "CASH_FLOW"  # Fluxo de Caixa
    INVENTORY = "INVENTORY"  # Estoque
    PURCHASE = "PURCHASE"  # Compras
    SALES = "SALES"  # Vendas
    PAYROLL = "PAYROLL"  # Folha de Pagamento
    FIXED_ASSETS = "FIXED_ASSETS"  # Ativo Imobilizado
    TAX = "TAX"  # Fiscal
    MANUAL = "MANUAL"  # Manual
    OTHER = "OTHER"  # Outros


class JournalEntry(Base):
    """Lançamento Contábil - cabeçalho do lançamento no diário."""

    __tablename__ = "fin_journal_entries"
    __table_args__ = (
        UniqueConstraint("condominio_id", "entry_number", name="uq_journal_entry_number"),
    )

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Período Contábil
    period_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounting_periods.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    entry_number = Column(String(30), nullable=False, index=True)
    batch_number = Column(String(30), nullable=True)  # Lote de lançamentos
    description = Column(String(500), nullable=False)
    complement = Column(Text, nullable=True)

    # Tipo e Status
    entry_type = Column(
        Enum(EntryType, name="entrytype", create_type=True),
        nullable=False,
        default=EntryType.MANUAL,
    )
    status = Column(
        Enum(EntryStatus, name="entrystatus", create_type=True),
        nullable=False,
        default=EntryStatus.DRAFT,
    )
    origin = Column(
        Enum(EntryOrigin, name="entryorigin", create_type=True),
        nullable=False,
        default=EntryOrigin.MANUAL,
    )

    # Datas
    entry_date = Column(Date, nullable=False, index=True)
    competence_date = Column(Date, nullable=False)  # Data de competência
    posting_date = Column(DateTime(timezone=True), nullable=True)  # Data da contabilização

    # Totais (devem ser iguais)
    total_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    line_count = Column(Integer, default=0, nullable=False)

    # Documento de Origem
    source_type = Column(String(50), nullable=True)  # Tipo do documento origem
    source_id = Column(UUID(as_uuid=True), nullable=True)  # ID do documento origem
    source_number = Column(String(50), nullable=True)  # Número do documento

    # Estorno
    is_reversal = Column(Boolean, default=False, nullable=False)
    reversed_entry_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_entries.id"),
        nullable=True,
    )
    reversal_entry_id = Column(UUID(as_uuid=True), nullable=True)  # ID do lançamento de estorno
    reversal_reason = Column(String(200), nullable=True)
    reversal_date = Column(DateTime(timezone=True), nullable=True)

    # Aprovação
    requires_approval = Column(Boolean, default=False, nullable=False)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    rejected_by = Column(UUID(as_uuid=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Contabilização
    posted_by = Column(UUID(as_uuid=True), nullable=True)

    # SPED
    sped_included = Column(Boolean, default=False, nullable=False)
    sped_record_type = Column(String(10), nullable=True)

    # Integração
    external_reference = Column(String(100), nullable=True)
    integration_data = Column(JSONB, nullable=True)

    # Anexos
    attachments = Column(JSONB, nullable=True)  # Lista de arquivos anexos

    # Flags
    is_template = Column(Boolean, default=False, nullable=False)  # É template
    is_recurring = Column(Boolean, default=False, nullable=False)  # É recorrente
    is_balanced = Column(Boolean, default=True, nullable=False)  # Está balanceado
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    period: "AccountingPeriod" = relationship(
        "AccountingPeriod",
        back_populates="journal_entries",
    )
    reversed_entry: Optional["JournalEntry"] = relationship(
        "JournalEntry",
        remote_side="JournalEntry.id",
        foreign_keys=[reversed_entry_id],
    )
    lines: list["JournalEntryLine"] = relationship(
        "JournalEntryLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<JournalEntry {self.entry_number} - {self.status.value}>"

    @property
    def is_balanced(self) -> bool:
        """Verifica se o lançamento está balanceado."""
        return self.total_debit == self.total_credit

    @property
    def can_post(self) -> bool:
        """Verifica se pode ser contabilizado."""
        return (
            self.status in [EntryStatus.DRAFT, EntryStatus.APPROVED]
            and self.is_balanced
            and self.line_count > 0
        )

    @property
    def can_reverse(self) -> bool:
        """Verifica se pode ser estornado."""
        return self.status == EntryStatus.POSTED and not self.is_reversal

    @property
    def can_edit(self) -> bool:
        """Verifica se pode ser editado."""
        return self.status in [EntryStatus.DRAFT, EntryStatus.PENDING]


class JournalEntryLine(Base):
    """Partida do Lançamento - linha de débito ou crédito."""

    __tablename__ = "fin_journal_entry_lines"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Referência ao Lançamento
    journal_entry_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Conta Contábil
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounting_accounts.id"),
        nullable=False,
        index=True,
    )

    # Centro de Custo (opcional)
    cost_center_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_centers.id"),
        nullable=True,
        index=True,
    )

    # Número da linha
    line_number = Column(Integer, nullable=False)

    # Valores (um deve ser zero)
    debit_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    credit_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Histórico da partida
    description = Column(String(500), nullable=True)
    history_code = Column(String(10), nullable=True)  # Código de histórico padrão

    # Documento
    document_type = Column(String(30), nullable=True)
    document_number = Column(String(50), nullable=True)
    document_date = Column(Date, nullable=True)

    # Contrapartida (para facilitar consultas)
    counterpart_account_id = Column(UUID(as_uuid=True), nullable=True)
    counterpart_account_code = Column(String(30), nullable=True)

    # Rateio
    allocation_key = Column(String(50), nullable=True)
    allocation_percentage = Column(Numeric(5, 2), nullable=True)

    # Projeto (opcional)
    project_id = Column(UUID(as_uuid=True), nullable=True)
    project_code = Column(String(30), nullable=True)

    # Reconciliação
    is_reconciled = Column(Boolean, default=False, nullable=False)
    reconciliation_id = Column(UUID(as_uuid=True), nullable=True)
    reconciliation_date = Column(DateTime(timezone=True), nullable=True)

    # SPED
    sped_account_code = Column(String(30), nullable=True)
    sped_cost_center_code = Column(String(30), nullable=True)

    # Integração
    external_reference = Column(String(100), nullable=True)
    integration_data = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    journal_entry: "JournalEntry" = relationship(
        "JournalEntry",
        back_populates="lines",
    )
    account: "AccountingAccount" = relationship(
        "AccountingAccount",
        back_populates="journal_lines",
    )
    cost_center: Optional["CostCenter"] = relationship(
        "CostCenter",
        back_populates="journal_lines",
    )

    def __repr__(self) -> str:
        """Representação string."""
        entry_type = "D" if self.debit_amount > 0 else "C"
        amount = self.debit_amount if self.debit_amount > 0 else self.credit_amount
        return f"<JournalEntryLine {self.line_number} {entry_type} {amount}>"

    @property
    def is_debit(self) -> bool:
        """Verifica se é partida de débito."""
        return self.debit_amount > 0

    @property
    def is_credit(self) -> bool:
        """Verifica se é partida de crédito."""
        return self.credit_amount > 0

    @property
    def amount(self) -> Decimal:
        """Retorna o valor da partida."""
        return self.debit_amount if self.is_debit else self.credit_amount

    @property
    def entry_type(self) -> str:
        """Retorna o tipo da partida (D/C)."""
        return "D" if self.is_debit else "C"
