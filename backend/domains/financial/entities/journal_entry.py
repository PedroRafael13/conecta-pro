"""
domains/financial/entities/journal_entry.py - JOURNAL ENTRY
===========================================================
Enterprise double-entry journal entry with full audit trail
"""

from typing import Dict, List, Optional, Any, NewType
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from .enums import (
    JournalEntryType,
    JournalEntryStatus,
    TransactionSource,
    ReconciliationStatus
)

# Strong typing for domain identifiers
JournalEntryId = NewType('JournalEntryId', UUID)
JournalLineId = NewType('JournalLineId', UUID)


class JournalLine(BaseModel):
    """
    Linha de lancamento contabil - Value Object.

    Representa uma partida (debito ou credito) de um lancamento.
    """

    model_config = ConfigDict(frozen=True)

    line_id: UUID = Field(default_factory=uuid4)
    account_id: UUID
    account_code: str = Field(..., pattern=r"^(\d{1,4})(\.\d{1,2}){0,4}$")
    account_name: str = Field(..., min_length=3, max_length=100)

    # Amounts - um dos dois deve ser preenchido
    debit_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    credit_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))

    # Details
    description: str = Field(..., min_length=3, max_length=500)
    cost_center_id: Optional[UUID] = None
    cost_center_code: Optional[str] = None
    project_id: Optional[UUID] = None
    project_code: Optional[str] = None

    # Reconciliation
    reconciliation_status: ReconciliationStatus = Field(
        default=ReconciliationStatus.NOT_RECONCILED
    )
    reconciled_at: Optional[datetime] = None
    reconciled_by: Optional[str] = None
    bank_statement_id: Optional[UUID] = None

    @model_validator(mode='after')
    def validate_line(self) -> 'JournalLine':
        """Valida que linha tem debito OU credito (nao ambos)."""
        has_debit = self.debit_amount > 0
        has_credit = self.credit_amount > 0

        if has_debit and has_credit:
            raise ValueError("Linha deve ter debito OU credito, nao ambos")

        if not has_debit and not has_credit:
            raise ValueError("Linha deve ter debito ou credito")

        return self

    @property
    def is_debit(self) -> bool:
        """Verifica se e linha de debito."""
        return self.debit_amount > 0

    @property
    def is_credit(self) -> bool:
        """Verifica se e linha de credito."""
        return self.credit_amount > 0

    @property
    def amount(self) -> Decimal:
        """Retorna valor da linha."""
        return self.debit_amount if self.is_debit else self.credit_amount

    @property
    def signed_amount(self) -> Decimal:
        """Retorna valor com sinal (debito +, credito -)."""
        return self.debit_amount - self.credit_amount


class JournalEntryAudit(BaseModel):
    """Entrada de auditoria do lancamento."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    user_id: str
    user_name: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None


class JournalEntryEntity(BaseModel):
    """
    Entidade de lancamento contabil.

    Implementa partida dobrada com validacao completa
    e trilha de auditoria.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )

    # Identity
    entry_id: UUID = Field(default_factory=uuid4)
    entry_number: str = Field(..., pattern=r"^LC-\d{4}-\d{8}$")
    batch_id: Optional[UUID] = None

    # Classification
    entry_type: JournalEntryType
    status: JournalEntryStatus = Field(default=JournalEntryStatus.DRAFT)
    source: TransactionSource = Field(default=TransactionSource.MANUAL)
    source_document_id: Optional[UUID] = None
    source_document_number: Optional[str] = None

    # Dates
    entry_date: date
    posting_date: Optional[date] = None
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2020, le=2035)

    # Header
    description: str = Field(..., min_length=10, max_length=1000)
    reference: Optional[str] = Field(None, max_length=100)
    memo: Optional[str] = Field(None, max_length=2000)

    # Lines
    lines: List[JournalLine] = Field(..., min_length=2)

    # Totals (calculated)
    total_debits: Decimal = Field(default=Decimal("0"))
    total_credits: Decimal = Field(default=Decimal("0"))
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")

    # Reversal
    is_reversal: bool = Field(default=False)
    reversed_entry_id: Optional[UUID] = None
    reversal_entry_id: Optional[UUID] = None
    reversal_reason: Optional[str] = None

    # Multi-tenant
    tenant_id: UUID

    # Audit
    audit_trail: List[JournalEntryAudit] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    posted_by: Optional[str] = None
    posted_at: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_entry(self) -> 'JournalEntryEntity':
        """Valida regras da partida dobrada."""
        # Calcula totais (usando object.__setattr__ para evitar recursao)
        total_d = sum(line.debit_amount for line in self.lines)
        total_c = sum(line.credit_amount for line in self.lines)
        object.__setattr__(self, 'total_debits', total_d)
        object.__setattr__(self, 'total_credits', total_c)

        # Valida balanceamento (partida dobrada)
        if self.total_debits != self.total_credits:
            raise ValueError(
                f"Lancamento desbalanceado: Debitos ({self.total_debits}) != "
                f"Creditos ({self.total_credits})"
            )

        # Valida minimo de linhas
        if len(self.lines) < 2:
            raise ValueError("Lancamento deve ter no minimo 2 linhas")

        # Valida que tem pelo menos um debito e um credito
        has_debit = any(line.is_debit for line in self.lines)
        has_credit = any(line.is_credit for line in self.lines)

        if not has_debit or not has_credit:
            raise ValueError("Lancamento deve ter pelo menos um debito e um credito")

        # Valida data vs periodo
        if self.entry_date.month != self.period_month or \
           self.entry_date.year != self.period_year:
            raise ValueError("Data do lancamento deve estar no periodo informado")

        # Valida estorno
        if self.is_reversal and not self.reversed_entry_id:
            raise ValueError("Lancamento de estorno deve referenciar lancamento original")

        return self

    # ==========================================================================
    # Business Methods
    # ==========================================================================

    def submit_for_approval(self, user_id: str) -> bool:
        """Submete para aprovacao."""
        if self.status != JournalEntryStatus.DRAFT:
            raise ValueError("Apenas lancamentos em rascunho podem ser submetidos")

        previous_status = self.status
        self.status = JournalEntryStatus.PENDING_APPROVAL
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        self._add_audit_entry(
            action="submitted_for_approval",
            user_id=user_id,
            previous_status=previous_status.value if isinstance(previous_status, JournalEntryStatus) else previous_status,
            new_status=self.status.value if isinstance(self.status, JournalEntryStatus) else self.status
        )

        return True

    def approve(self, approver_id: str, approver_name: str) -> bool:
        """Aprova o lancamento."""
        if self.status != JournalEntryStatus.PENDING_APPROVAL:
            raise ValueError("Apenas lancamentos pendentes podem ser aprovados")

        # Verifica se aprovador e diferente do criador
        if approver_id == self.created_by:
            raise ValueError("Aprovador deve ser diferente do criador")

        previous_status = self.status
        self.status = JournalEntryStatus.APPROVED
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.updated_by = approver_id

        self._add_audit_entry(
            action="approved",
            user_id=approver_id,
            user_name=approver_name,
            previous_status=previous_status.value if isinstance(previous_status, JournalEntryStatus) else previous_status,
            new_status=self.status.value if isinstance(self.status, JournalEntryStatus) else self.status
        )

        return True

    def reject(self, rejector_id: str, reason: str) -> bool:
        """Rejeita o lancamento."""
        if self.status != JournalEntryStatus.PENDING_APPROVAL:
            raise ValueError("Apenas lancamentos pendentes podem ser rejeitados")

        previous_status = self.status
        self.status = JournalEntryStatus.REJECTED
        self.updated_at = datetime.utcnow()
        self.updated_by = rejector_id

        self._add_audit_entry(
            action="rejected",
            user_id=rejector_id,
            previous_status=previous_status.value if isinstance(previous_status, JournalEntryStatus) else previous_status,
            new_status=self.status.value if isinstance(self.status, JournalEntryStatus) else self.status,
            details={"reason": reason}
        )

        return True

    def post(self, poster_id: str, poster_name: str) -> bool:
        """Contabiliza o lancamento."""
        if self.status != JournalEntryStatus.APPROVED:
            raise ValueError("Apenas lancamentos aprovados podem ser contabilizados")

        previous_status = self.status
        self.status = JournalEntryStatus.POSTED
        self.posting_date = date.today()
        self.posted_by = poster_id
        self.posted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.updated_by = poster_id

        self._add_audit_entry(
            action="posted",
            user_id=poster_id,
            user_name=poster_name,
            previous_status=previous_status.value if isinstance(previous_status, JournalEntryStatus) else previous_status,
            new_status=self.status.value if isinstance(self.status, JournalEntryStatus) else self.status
        )

        return True

    def create_reversal(
        self,
        user_id: str,
        reason: str,
        reversal_date: date
    ) -> 'JournalEntryEntity':
        """Cria lancamento de estorno."""
        if self.status != JournalEntryStatus.POSTED:
            raise ValueError("Apenas lancamentos contabilizados podem ser estornados")

        if self.reversal_entry_id:
            raise ValueError("Lancamento ja foi estornado")

        # Inverte debitos e creditos
        reversed_lines = []
        for line in self.lines:
            reversed_line = JournalLine(
                account_id=line.account_id,
                account_code=line.account_code,
                account_name=line.account_name,
                debit_amount=line.credit_amount,  # Inverte
                credit_amount=line.debit_amount,  # Inverte
                description=f"Estorno: {line.description}",
                cost_center_id=line.cost_center_id,
                cost_center_code=line.cost_center_code,
                project_id=line.project_id,
                project_code=line.project_code
            )
            reversed_lines.append(reversed_line)

        # Gera numero sequencial usando parte do UUID convertido para int
        seq = int(uuid4().hex[:8], 16) % 100000000
        reversal_entry = JournalEntryEntity(
            entry_number=f"LC-{reversal_date.year}-{seq:08d}",
            entry_type=JournalEntryType.REVERSAL,
            source=self.source,
            source_document_id=self.source_document_id,
            entry_date=reversal_date,
            period_month=reversal_date.month,
            period_year=reversal_date.year,
            description=f"Estorno de {self.entry_number}: {reason}",
            reference=self.entry_number,
            memo=reason,
            lines=reversed_lines,
            is_reversal=True,
            reversed_entry_id=self.entry_id,
            tenant_id=self.tenant_id,
            created_by=user_id
        )

        return reversal_entry

    def add_line(self, line: JournalLine) -> None:
        """Adiciona linha ao lancamento."""
        if not JournalEntryStatus(self.status).can_edit():
            raise ValueError("Lancamento nao pode ser editado")

        self.lines.append(line)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()

    def remove_line(self, line_id: UUID) -> bool:
        """Remove linha do lancamento."""
        if not JournalEntryStatus(self.status).can_edit():
            raise ValueError("Lancamento nao pode ser editado")

        original_count = len(self.lines)
        self.lines = [line for line in self.lines if line.line_id != line_id]

        if len(self.lines) == original_count:
            return False

        self._recalculate_totals()
        self.updated_at = datetime.utcnow()
        return True

    def _recalculate_totals(self) -> None:
        """Recalcula totais do lancamento."""
        self.total_debits = sum(line.debit_amount for line in self.lines)
        self.total_credits = sum(line.credit_amount for line in self.lines)

    def _add_audit_entry(
        self,
        action: str,
        user_id: str,
        user_name: str = "",
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Adiciona entrada no audit trail."""
        entry = JournalEntryAudit(
            action=action,
            user_id=user_id,
            user_name=user_name,
            previous_status=previous_status,
            new_status=new_status,
            details=details or {}
        )
        self.audit_trail.append(entry)

    @property
    def is_balanced(self) -> bool:
        """Verifica se lancamento esta balanceado."""
        return self.total_debits == self.total_credits

    @property
    def can_be_edited(self) -> bool:
        """Verifica se pode ser editado."""
        return JournalEntryStatus(self.status).can_edit()

    @property
    def can_be_posted(self) -> bool:
        """Verifica se pode ser contabilizado."""
        return JournalEntryStatus(self.status).can_post()

    @property
    def can_be_reversed(self) -> bool:
        """Verifica se pode ser estornado."""
        return (
            JournalEntryStatus(self.status).can_reverse() and
            self.reversal_entry_id is None
        )

    def get_debit_lines(self) -> List[JournalLine]:
        """Retorna linhas de debito."""
        return [line for line in self.lines if line.is_debit]

    def get_credit_lines(self) -> List[JournalLine]:
        """Retorna linhas de credito."""
        return [line for line in self.lines if line.is_credit]

    def get_accounts_affected(self) -> List[UUID]:
        """Retorna IDs das contas afetadas."""
        return list(set(line.account_id for line in self.lines))

    @staticmethod
    def generate_entry_number(year: int, sequence: int) -> str:
        """Gera numero do lancamento."""
        return f"LC-{year}-{sequence:08d}"

    def to_summary(self) -> Dict[str, Any]:
        """Retorna resumo do lancamento."""
        return {
            "entry_id": str(self.entry_id),
            "entry_number": self.entry_number,
            "entry_date": self.entry_date.isoformat(),
            "description": self.description,
            "total_debits": str(self.total_debits),
            "total_credits": str(self.total_credits),
            "status": self.status,
            "lines_count": len(self.lines),
            "is_balanced": self.is_balanced
        }
