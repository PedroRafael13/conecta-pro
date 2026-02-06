"""Model para recebimentos de contas a receber."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.receivable_installment import ReceivableInstallment


class PaymentStatus(str, Enum):
    """Status do recebimento."""

    PENDENTE = "pendente"  # Aguardando confirmacao
    PROCESSANDO = "processando"  # Em processamento
    CONFIRMADO = "confirmado"  # Confirmado/Efetivado
    REJEITADO = "rejeitado"  # Rejeitado pelo banco
    ESTORNADO = "estornado"  # Estornado
    CANCELADO = "cancelado"  # Cancelado


class PaymentOrigin(str, Enum):
    """Origem do recebimento."""

    MANUAL = "manual"  # Lancamento manual
    BOLETO = "boleto"  # Pagamento de boleto
    PIX = "pix"  # Pagamento via PIX
    CARTAO = "cartao"  # Pagamento via cartao
    TRANSFERENCIA = "transferencia"  # Transferencia bancaria
    DINHEIRO = "dinheiro"  # Dinheiro/Caixa
    CHEQUE = "cheque"  # Cheque
    DEBITO_AUTOMATICO = "debito_automatico"  # Debito automatico
    IMPORTACAO = "importacao"  # Importacao de extrato
    INTEGRACAO = "integracao"  # Integracao bancaria
    API = "api"  # Via API


class ReceivablePayment(Base):
    """Recebimento de conta a receber."""

    __tablename__ = "receivable_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("receivable_installments.id"),
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
    code = Column(String(30), nullable=True)  # Codigo interno
    status = Column(String(20), nullable=False, default=PaymentStatus.PENDENTE.value)
    origin = Column(String(30), default=PaymentOrigin.MANUAL.value)

    # Valores
    paid_value = Column(Numeric(15, 2), nullable=False)  # Valor recebido
    discount_value = Column(Numeric(15, 2), default=0)  # Desconto concedido
    interest_value = Column(Numeric(15, 2), default=0)  # Juros recebidos
    penalty_value = Column(Numeric(15, 2), default=0)  # Multa recebida
    fee_value = Column(Numeric(15, 2), default=0)  # Taxas bancarias
    net_value = Column(Numeric(15, 2), nullable=False)  # Valor liquido creditado

    # Datas
    payment_date = Column(Date, nullable=False)  # Data do recebimento
    processing_date = Column(Date, nullable=True)  # Data processamento banco
    confirmation_date = Column(Date, nullable=True)  # Data confirmacao
    credit_date = Column(Date, nullable=True)  # Data de credito na conta

    # Forma de pagamento
    payment_method_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_methods.id"),
        nullable=True,
    )
    payment_method_name = Column(String(100), nullable=True)  # Snapshot

    # Conta bancaria
    bank_account_id = Column(UUID(as_uuid=True), nullable=True)
    bank_account_name = Column(String(100), nullable=True)  # Snapshot

    # Comprovante
    receipt_number = Column(String(50), nullable=True)
    receipt_url = Column(String(500), nullable=True)
    authentication_code = Column(String(100), nullable=True)

    # Dados bancarios do recebimento
    bank_transaction_id = Column(String(100), nullable=True)  # ID transacao banco
    bank_return_code = Column(String(20), nullable=True)
    bank_return_message = Column(String(500), nullable=True)

    # Boleto
    boleto_nosso_numero = Column(String(50), nullable=True)
    boleto_payment_date = Column(Date, nullable=True)
    boleto_payment_value = Column(Numeric(15, 2), nullable=True)

    # PIX
    pix_txid = Column(String(100), nullable=True)
    pix_end_to_end_id = Column(String(100), nullable=True)

    # Cheque
    cheque_number = Column(String(20), nullable=True)
    cheque_bank = Column(String(10), nullable=True)
    cheque_agency = Column(String(10), nullable=True)
    cheque_account = Column(String(20), nullable=True)
    cheque_date = Column(Date, nullable=True)  # Data do cheque

    # Estorno
    is_reversed = Column(Boolean, default=False)
    reversed_at = Column(DateTime, nullable=True)
    reversed_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    reversal_reason = Column(Text, nullable=True)
    reversal_receipt = Column(String(500), nullable=True)

    # Conciliacao
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    reconciliation_notes = Column(Text, nullable=True)

    # Dados adicionais
    extra_data = Column(JSONB, default=dict)
    # {"banco": "001", "agencia": "1234", "conta": "12345-6", ...}

    # Observacoes
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    installment: "ReceivableInstallment" = relationship(
        "ReceivableInstallment", back_populates="payments"
    )

    __table_args__ = (
        Index("ix_receivable_payments_date", "payment_date"),
        Index("ix_receivable_payments_status", "status"),
        Index("ix_receivable_payments_installment", "installment_id"),
        Index("ix_receivable_payments_reconciled", "is_reconciled"),
        Index("ix_receivable_payments_origin", "origin"),
        Index(
            "ix_receivable_payments_condominio_date",
            "condominio_id",
            "payment_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<ReceivablePayment {self.code or self.id} - {self.paid_value}>"

    @property
    def is_confirmed(self) -> bool:
        """Verifica se esta confirmado."""
        return self.status == PaymentStatus.CONFIRMADO.value

    @property
    def is_pending(self) -> bool:
        """Verifica se esta pendente."""
        return self.status in [
            PaymentStatus.PENDENTE.value,
            PaymentStatus.PROCESSANDO.value,
        ]

    @property
    def can_reverse(self) -> bool:
        """Verifica se pode ser estornado."""
        return self.status == PaymentStatus.CONFIRMADO.value and not self.is_reversed

    @property
    def total_additions(self) -> Decimal:
        """Total de acrescimos (juros + multa)."""
        return self.interest_value + self.penalty_value

    @property
    def total_deductions(self) -> Decimal:
        """Total de deducoes (desconto + taxas)."""
        return self.discount_value + self.fee_value

    def calculate_net_value(self) -> Decimal:
        """Calcula valor liquido."""
        return (
            self.paid_value
            - self.discount_value
            - self.fee_value
            + self.interest_value
            + self.penalty_value
        )

    def confirm(self, confirmation_date: Optional[date] = None) -> None:
        """Confirma o recebimento."""
        self.status = PaymentStatus.CONFIRMADO.value
        self.confirmation_date = confirmation_date or date.today()

    def reject(self, return_code: str, return_message: str) -> None:
        """Rejeita o recebimento."""
        self.status = PaymentStatus.REJEITADO.value
        self.bank_return_code = return_code
        self.bank_return_message = return_message

    def reverse(
        self,
        user_id: uuid.UUID,
        reason: str,
        receipt: Optional[str] = None,
    ) -> None:
        """Estorna o recebimento."""
        self.is_reversed = True
        self.reversed_at = datetime.utcnow()
        self.reversed_by = user_id
        self.reversal_reason = reason
        self.reversal_receipt = receipt
        self.status = PaymentStatus.ESTORNADO.value

    def reconcile(
        self,
        user_id: uuid.UUID,
        notes: Optional[str] = None,
    ) -> None:
        """Marca como conciliado."""
        self.is_reconciled = True
        self.reconciled_at = datetime.utcnow()
        self.reconciled_by = user_id
        self.reconciliation_notes = notes

    def cancel(self) -> None:
        """Cancela o recebimento."""
        self.status = PaymentStatus.CANCELADO.value
        self.ativo = False

    def set_boleto_data(
        self,
        nosso_numero: str,
        payment_date: date,
        payment_value: Decimal,
    ) -> None:
        """Define dados do boleto pago."""
        self.boleto_nosso_numero = nosso_numero
        self.boleto_payment_date = payment_date
        self.boleto_payment_value = payment_value
        self.origin = PaymentOrigin.BOLETO.value

    def set_pix_data(
        self,
        txid: str,
        end_to_end_id: str,
    ) -> None:
        """Define dados do PIX recebido."""
        self.pix_txid = txid
        self.pix_end_to_end_id = end_to_end_id
        self.origin = PaymentOrigin.PIX.value

    def set_cheque_data(
        self,
        number: str,
        bank: str,
        agency: str,
        account: str,
        cheque_date: date,
    ) -> None:
        """Define dados do cheque."""
        self.cheque_number = number
        self.cheque_bank = bank
        self.cheque_agency = agency
        self.cheque_account = account
        self.cheque_date = cheque_date
        self.origin = PaymentOrigin.CHEQUE.value

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "installment_id": str(self.installment_id),
            "code": self.code,
            "status": self.status,
            "origin": self.origin,
            "paid_value": float(self.paid_value),
            "discount_value": float(self.discount_value),
            "interest_value": float(self.interest_value),
            "penalty_value": float(self.penalty_value),
            "fee_value": float(self.fee_value),
            "net_value": float(self.net_value),
            "payment_date": self.payment_date.isoformat(),
            "confirmation_date": (
                self.confirmation_date.isoformat() if self.confirmation_date else None
            ),
            "payment_method_name": self.payment_method_name,
            "receipt_number": self.receipt_number,
            "is_confirmed": self.is_confirmed,
            "is_reconciled": self.is_reconciled,
            "is_reversed": self.is_reversed,
        }
