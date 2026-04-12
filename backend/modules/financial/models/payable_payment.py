"""Model para pagamentos de contas a pagar."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.payable_installment import PayableInstallment


class PaymentStatus(StrEnum):
    """Status do pagamento."""

    PENDENTE = "pendente"  # Aguardando processamento
    PROCESSANDO = "processando"  # Em processamento
    CONFIRMADO = "confirmado"  # Confirmado/Efetivado
    REJEITADO = "rejeitado"  # Rejeitado pelo banco
    ESTORNADO = "estornado"  # Estornado
    CANCELADO = "cancelado"  # Cancelado


class PaymentOrigin(StrEnum):
    """Origem do pagamento."""

    MANUAL = "manual"  # Lançamento manual
    IMPORTACAO = "importacao"  # Importação de extrato
    INTEGRACAO = "integracao"  # Integração bancária
    API = "api"  # Via API


class PayablePayment(Base):
    """Pagamento de conta a pagar."""

    __tablename__ = "payable_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    installment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payable_installments.id"),
        nullable=False,
        index=True,
    )
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    code = Column(String(30), nullable=True)  # Código interno
    status = Column(String(20), nullable=False, default=PaymentStatus.PENDENTE.value)
    origin = Column(String(20), default=PaymentOrigin.MANUAL.value)

    # Valores
    paid_value = Column(Numeric(15, 2), nullable=False)  # Valor pago
    discount_value = Column(Numeric(15, 2), default=0)  # Desconto obtido
    interest_value = Column(Numeric(15, 2), default=0)  # Juros pagos
    penalty_value = Column(Numeric(15, 2), default=0)  # Multa paga
    fee_value = Column(Numeric(15, 2), default=0)  # Taxas bancárias
    net_value = Column(Numeric(15, 2), nullable=False)  # Valor líquido debitado

    # Datas
    payment_date = Column(Date, nullable=False)  # Data do pagamento
    processing_date = Column(Date, nullable=True)  # Data processamento banco
    confirmation_date = Column(Date, nullable=True)  # Data confirmação

    # Forma de pagamento
    payment_method_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_methods.id"),
        nullable=True,
    )
    payment_method_name = Column(String(100), nullable=True)  # Snapshot do nome

    # Conta bancária
    bank_account_id = Column(UUID(as_uuid=True), nullable=True)
    bank_account_name = Column(String(100), nullable=True)  # Snapshot

    # Comprovante
    receipt_number = Column(String(50), nullable=True)  # Número comprovante
    receipt_url = Column(String(500), nullable=True)  # URL do comprovante
    authentication_code = Column(String(100), nullable=True)  # Código autenticação

    # Dados bancários do pagamento
    bank_transaction_id = Column(String(100), nullable=True)  # ID transação banco
    bank_return_code = Column(String(20), nullable=True)  # Código retorno
    bank_return_message = Column(String(500), nullable=True)  # Mensagem retorno

    # Estorno
    is_reversed = Column(Boolean, default=False)
    reversed_at = Column(DateTime, nullable=True)
    reversed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reversal_reason = Column(Text, nullable=True)
    reversal_receipt = Column(String(500), nullable=True)

    # Conciliação
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reconciliation_notes = Column(Text, nullable=True)

    # Dados adicionais
    extra_data = Column(JSONB, default=dict)
    # {"banco": "001", "agencia": "1234", "conta": "12345-6", ...}

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    installment: "PayableInstallment" = relationship("PayableInstallment", back_populates="payments")

    __table_args__ = (
        Index("ix_payable_payments_date", "payment_date"),
        Index("ix_payable_payments_status", "status"),
        Index("ix_payable_payments_installment", "installment_id"),
        Index("ix_payable_payments_reconciled", "is_reconciled"),
        Index(
            "ix_payable_payments_condominio_date",
            "condominio_id",
            "payment_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<PayablePayment {self.code or self.id} - {self.paid_value}>"

    @property
    def is_confirmed(self) -> bool:
        """Verifica se está confirmado."""
        return self.status == PaymentStatus.CONFIRMADO.value

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
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
        """Total de acréscimos (juros + multa + taxas)."""
        return self.interest_value + self.penalty_value + self.fee_value

    def calculate_net_value(self) -> Decimal:
        """Calcula valor líquido."""
        return self.paid_value - self.discount_value + self.interest_value + self.penalty_value + self.fee_value

    def confirm(self, confirmation_date: date | None = None) -> None:
        """Confirma o pagamento."""
        self.status = PaymentStatus.CONFIRMADO.value
        self.confirmation_date = confirmation_date or date.today()

    def reject(self, return_code: str, return_message: str) -> None:
        """Rejeita o pagamento."""
        self.status = PaymentStatus.REJEITADO.value
        self.bank_return_code = return_code
        self.bank_return_message = return_message

    def reverse(
        self,
        user_id: uuid.UUID,
        reason: str,
        receipt: str | None = None,
    ) -> None:
        """Estorna o pagamento."""
        self.is_reversed = True
        self.reversed_at = datetime.utcnow()
        self.reversed_by = user_id
        self.reversal_reason = reason
        self.reversal_receipt = receipt
        self.status = PaymentStatus.ESTORNADO.value

    def reconcile(
        self,
        user_id: uuid.UUID,
        notes: str | None = None,
    ) -> None:
        """Marca como conciliado."""
        self.is_reconciled = True
        self.reconciled_at = datetime.utcnow()
        self.reconciled_by = user_id
        self.reconciliation_notes = notes

    def cancel(self) -> None:
        """Cancela o pagamento."""
        self.status = PaymentStatus.CANCELADO.value
        self.ativo = False

    def to_dict(self) -> dict:
        """Converte para dicionário."""
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
            "confirmation_date": (self.confirmation_date.isoformat() if self.confirmation_date else None),
            "payment_method_name": self.payment_method_name,
            "receipt_number": self.receipt_number,
            "is_confirmed": self.is_confirmed,
            "is_reconciled": self.is_reconciled,
            "is_reversed": self.is_reversed,
        }
