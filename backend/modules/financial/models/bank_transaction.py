"""Model para movimentacoes bancarias."""

import uuid
from datetime import datetime
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
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.bank_account import BankAccount


class TransactionType(str, Enum):
    """Tipo de movimentacao."""

    CREDITO = "credito"  # Entrada de dinheiro
    DEBITO = "debito"  # Saida de dinheiro
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"  # Recebimento de transferencia
    TRANSFERENCIA_SAIDA = "transferencia_saida"  # Envio de transferencia
    ESTORNO = "estorno"  # Estorno de operacao


class TransactionCategory(str, Enum):
    """Categoria da movimentacao."""

    # Receitas
    TAXA_CONDOMINIAL = "taxa_condominial"
    TAXA_EXTRA = "taxa_extra"
    ALUGUEL = "aluguel"
    RESERVA = "reserva"
    MULTA = "multa"
    JUROS_RECEBIDOS = "juros_recebidos"
    RENDIMENTO = "rendimento"
    OUTRAS_RECEITAS = "outras_receitas"

    # Despesas
    FORNECEDOR = "fornecedor"
    FUNCIONARIO = "funcionario"
    TRIBUTO = "tributo"
    SERVICO = "servico"
    MANUTENCAO = "manutencao"
    TARIFA_BANCARIA = "tarifa_bancaria"
    IOF = "iof"
    JUROS_PAGOS = "juros_pagos"
    OUTRAS_DESPESAS = "outras_despesas"

    # Transferencias
    TRANSFERENCIA_ENTRE_CONTAS = "transferencia_entre_contas"
    APLICACAO = "aplicacao"
    RESGATE = "resgate"

    # Outros
    AJUSTE = "ajuste"
    SALDO_INICIAL = "saldo_inicial"
    NAO_IDENTIFICADO = "nao_identificado"


class TransactionStatus(str, Enum):
    """Status da movimentacao."""

    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    ESTORNADA = "estornada"


class ReconciliationStatus(str, Enum):
    """Status de conciliacao."""

    PENDENTE = "pendente"
    CONCILIADA = "conciliada"
    DIVERGENTE = "divergente"
    IGNORADA = "ignorada"


class TransactionOrigin(str, Enum):
    """Origem da movimentacao."""

    MANUAL = "manual"  # Lancamento manual
    PAGAMENTO_CONTA = "pagamento_conta"  # Pagamento de conta a pagar
    RECEBIMENTO = "recebimento"  # Recebimento de conta a receber
    IMPORTACAO = "importacao"  # Importado de extrato
    API = "api"  # Via integracao bancaria
    PIX = "pix"
    BOLETO = "boleto"
    TED = "ted"
    DOC = "doc"
    TRANSFERENCIA = "transferencia"


class BankTransaction(Base):
    """Movimentacao bancaria."""

    __tablename__ = "bank_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bank_accounts.id"),
        nullable=False,
        index=True,
    )

    # Tipo e categoria
    transaction_type = Column(String(30), nullable=False)
    category = Column(
        String(50), nullable=False, default=TransactionCategory.NAO_IDENTIFICADO.value
    )
    status = Column(String(20), nullable=False, default=TransactionStatus.CONFIRMADA.value)

    # Valores
    amount = Column(Numeric(15, 2), nullable=False)
    balance_before = Column(Numeric(15, 2), nullable=True)  # Saldo antes
    balance_after = Column(Numeric(15, 2), nullable=True)  # Saldo depois

    # Descricao
    description = Column(String(500), nullable=False)
    memo = Column(Text, nullable=True)  # Observacoes adicionais

    # Datas
    transaction_date = Column(Date, nullable=False)  # Data da movimentacao
    competence_date = Column(Date, nullable=True)  # Data de competencia (contabil)
    posting_date = Column(Date, nullable=True)  # Data de lancamento no sistema
    value_date = Column(Date, nullable=True)  # Data valor (efetivacao)

    # Identificacao externa
    external_id = Column(String(100), nullable=True)  # ID do banco
    document_number = Column(String(50), nullable=True)  # Numero do documento
    authentication = Column(String(100), nullable=True)  # Autenticacao bancaria
    reference = Column(String(100), nullable=True)  # Referencia

    # Origem e rastreabilidade
    origin = Column(String(30), nullable=False, default=TransactionOrigin.MANUAL.value)
    source_type = Column(String(30), nullable=True)  # payable, receivable, transfer
    source_id = Column(UUID(as_uuid=True), nullable=True)  # ID da origem (conta a pagar/receber)

    # Vinculo com contas a pagar/receber
    payable_payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payable_payments.id"),
        nullable=True,
    )
    receivable_payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("receivable_payments.id"),
        nullable=True,
    )

    # Transferencia entre contas
    is_transfer = Column(Boolean, default=False)
    transfer_pair_id = Column(UUID(as_uuid=True), nullable=True)  # ID da transacao par
    transfer_account_id = Column(UUID(as_uuid=True), nullable=True)  # Conta de destino/origem

    # Conciliacao
    reconciliation_status = Column(
        String(20),
        nullable=False,
        default=ReconciliationStatus.PENDENTE.value,
    )
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    reconciliation_note = Column(Text, nullable=True)

    # Dados do terceiro (favorecido/pagador)
    counterparty_name = Column(String(150), nullable=True)
    counterparty_document = Column(String(20), nullable=True)
    counterparty_bank = Column(String(100), nullable=True)
    counterparty_agency = Column(String(10), nullable=True)
    counterparty_account = Column(String(20), nullable=True)

    # PIX
    pix_key = Column(String(100), nullable=True)
    pix_end_to_end = Column(String(50), nullable=True)  # E2E ID

    # Boleto
    barcode = Column(String(50), nullable=True)
    boleto_number = Column(String(20), nullable=True)

    # Importacao
    imported_from = Column(String(50), nullable=True)  # ofx, cnab, api
    import_batch_id = Column(UUID(as_uuid=True), nullable=True)
    raw_data = Column(JSONB, default=dict)  # Dados brutos importados

    # Estorno
    is_reversal = Column(Boolean, default=False)
    reversed_transaction_id = Column(UUID(as_uuid=True), nullable=True)
    reversal_reason = Column(Text, nullable=True)

    # Anexos
    attachments = Column(JSONB, default=list)  # Lista de arquivos anexos

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    bank_account: "BankAccount" = relationship(
        "BankAccount",
        back_populates="transactions",
    )

    __table_args__ = (
        Index("ix_bank_transactions_account", "bank_account_id"),
        Index("ix_bank_transactions_date", "transaction_date"),
        Index("ix_bank_transactions_type", "transaction_type"),
        Index("ix_bank_transactions_category", "category"),
        Index("ix_bank_transactions_status", "status"),
        Index("ix_bank_transactions_reconciliation", "reconciliation_status"),
        Index("ix_bank_transactions_external", "external_id"),
        Index("ix_bank_transactions_source", "source_type", "source_id"),
        Index(
            "ix_bank_transactions_account_date",
            "bank_account_id",
            "transaction_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<BankTransaction {self.transaction_type} R${self.amount}>"

    @property
    def is_credit(self) -> bool:
        """Verifica se e credito."""
        return self.transaction_type in [
            TransactionType.CREDITO.value,
            TransactionType.TRANSFERENCIA_ENTRADA.value,
        ]

    @property
    def is_debit(self) -> bool:
        """Verifica se e debito."""
        return self.transaction_type in [
            TransactionType.DEBITO.value,
            TransactionType.TRANSFERENCIA_SAIDA.value,
        ]

    @property
    def is_reconciled(self) -> bool:
        """Verifica se esta conciliada."""
        return self.reconciliation_status == ReconciliationStatus.CONCILIADA.value

    @property
    def is_pending_reconciliation(self) -> bool:
        """Verifica se esta pendente de conciliacao."""
        return self.reconciliation_status == ReconciliationStatus.PENDENTE.value

    @property
    def signed_amount(self) -> Decimal:
        """Retorna valor com sinal (positivo para credito, negativo para debito)."""
        if self.is_credit:
            return self.amount
        return -self.amount

    def confirm(self) -> None:
        """Confirma a transacao."""
        self.status = TransactionStatus.CONFIRMADA.value

    def cancel(self) -> None:
        """Cancela a transacao."""
        self.status = TransactionStatus.CANCELADA.value

    def mark_as_reversed(self, reversal_id: uuid.UUID, reason: str) -> None:
        """Marca como estornada."""
        self.status = TransactionStatus.ESTORNADA.value
        self.reversed_transaction_id = reversal_id
        self.reversal_reason = reason

    def reconcile(self, user_id: uuid.UUID, note: Optional[str] = None) -> None:
        """Marca como conciliada."""
        self.reconciliation_status = ReconciliationStatus.CONCILIADA.value
        self.reconciled_at = datetime.utcnow()
        self.reconciled_by = user_id
        self.reconciliation_note = note

    def mark_as_divergent(self, note: str) -> None:
        """Marca como divergente."""
        self.reconciliation_status = ReconciliationStatus.DIVERGENTE.value
        self.reconciliation_note = note

    def ignore_reconciliation(self, note: str) -> None:
        """Ignora na conciliacao."""
        self.reconciliation_status = ReconciliationStatus.IGNORADA.value
        self.reconciliation_note = note

    def link_to_payable(self, payment_id: uuid.UUID) -> None:
        """Vincula a pagamento de conta a pagar."""
        self.payable_payment_id = payment_id
        self.source_type = "payable"
        self.source_id = payment_id

    def link_to_receivable(self, payment_id: uuid.UUID) -> None:
        """Vincula a recebimento de conta a receber."""
        self.receivable_payment_id = payment_id
        self.source_type = "receivable"
        self.source_id = payment_id

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "bank_account_id": str(self.bank_account_id),
            "transaction_type": self.transaction_type,
            "category": self.category,
            "status": self.status,
            "amount": float(self.amount),
            "signed_amount": float(self.signed_amount),
            "balance_before": float(self.balance_before) if self.balance_before else None,
            "balance_after": float(self.balance_after) if self.balance_after else None,
            "description": self.description,
            "transaction_date": self.transaction_date.isoformat(),
            "competence_date": (self.competence_date.isoformat() if self.competence_date else None),
            "origin": self.origin,
            "source_type": self.source_type,
            "reconciliation_status": self.reconciliation_status,
            "is_credit": self.is_credit,
            "is_debit": self.is_debit,
            "is_transfer": self.is_transfer,
            "counterparty_name": self.counterparty_name,
            "external_id": self.external_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
