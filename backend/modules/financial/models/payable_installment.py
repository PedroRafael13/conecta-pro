"""Model para parcelas de contas a pagar."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.payable_account import PayableAccount
    from modules.financial.models.payable_payment import PayablePayment


class InstallmentStatus(StrEnum):
    """Status da parcela."""

    PENDENTE = "pendente"
    VENCIDA = "vencida"
    PARCIAL = "parcial"
    PAGA = "paga"
    CANCELADA = "cancelada"
    AGENDADA = "agendada"
    RENEGOCIADA = "renegociada"


class PayableInstallment(Base):
    """Parcela de conta a pagar."""

    __tablename__ = "payable_installments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payable_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payable_accounts.id"),
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
    installment_number = Column(Integer, nullable=False)  # Número da parcela
    total_installments = Column(Integer, nullable=False)  # Total de parcelas
    status = Column(String(20), nullable=False, default=InstallmentStatus.PENDENTE.value)

    # Valores
    original_value = Column(Numeric(15, 2), nullable=False)  # Valor original
    discount_value = Column(Numeric(15, 2), default=0)  # Desconto
    interest_value = Column(Numeric(15, 2), default=0)  # Juros
    penalty_value = Column(Numeric(15, 2), default=0)  # Multa
    addition_value = Column(Numeric(15, 2), default=0)  # Acréscimos
    current_value = Column(Numeric(15, 2), nullable=False)  # Valor atual
    paid_value = Column(Numeric(15, 2), default=0)  # Valor pago

    # Datas
    due_date = Column(Date, nullable=False, index=True)
    original_due_date = Column(Date, nullable=True)  # Data original (se renegociada)
    payment_date = Column(Date, nullable=True)

    # Juros e multa configurados
    interest_rate = Column(Numeric(8, 4), default=0)  # % juros ao mês
    penalty_rate = Column(Numeric(8, 4), default=0)  # % multa

    # Forma de pagamento
    payment_method_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_methods.id"),
        nullable=True,
    )

    # Boleto/PIX
    barcode = Column(String(100), nullable=True)  # Código de barras
    digitable_line = Column(String(100), nullable=True)  # Linha digitável
    pix_qrcode = Column(Text, nullable=True)  # QR Code PIX
    pix_copy_paste = Column(String(500), nullable=True)  # PIX copia e cola
    boleto_url = Column(String(500), nullable=True)  # URL do boleto

    # Agendamento
    scheduled_payment_date = Column(Date, nullable=True)
    scheduled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Renegociação
    is_renegotiated = Column(Boolean, default=False)
    renegotiated_from_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payable_installments.id"),
        nullable=True,
    )
    renegotiation_reason = Column(Text, nullable=True)

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    payable_account: "PayableAccount" = relationship("PayableAccount", back_populates="installments")
    payments: list["PayablePayment"] = relationship(
        "PayablePayment",
        back_populates="installment",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_payable_installments_due_date", "due_date"),
        Index("ix_payable_installments_status", "status"),
        Index("ix_payable_installments_account", "payable_account_id"),
        Index(
            "ix_payable_installments_condominio_status",
            "condominio_id",
            "status",
            "due_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<PayableInstallment {self.installment_number}/{self.total_installments}>"

    @property
    def display_number(self) -> str:
        """Retorna número formatado."""
        return f"{self.installment_number}/{self.total_installments}"

    @property
    def is_overdue(self) -> bool:
        """Verifica se está vencida."""
        if self.status in [InstallmentStatus.PAGA.value, InstallmentStatus.CANCELADA.value]:
            return False
        return self.due_date < date.today()

    @property
    def days_overdue(self) -> int:
        """Dias de atraso."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    @property
    def days_until_due(self) -> int:
        """Dias até vencimento."""
        return (self.due_date - date.today()).days

    @property
    def balance(self) -> Decimal:
        """Saldo a pagar."""
        return self.current_value - self.paid_value

    @property
    def is_paid(self) -> bool:
        """Verifica se está paga."""
        return self.status == InstallmentStatus.PAGA.value

    @property
    def is_partially_paid(self) -> bool:
        """Verifica se está parcialmente paga."""
        return self.paid_value > 0 and self.paid_value < self.current_value

    def calculate_current_value(self) -> Decimal:
        """Calcula valor atual com juros e multa se vencido."""
        value = self.original_value - self.discount_value + self.addition_value

        if self.is_overdue and not self.is_paid:
            # Aplica multa
            if self.penalty_rate > 0:
                self.penalty_value = value * (self.penalty_rate / 100)

            # Aplica juros (proporcional aos dias de atraso)
            if self.interest_rate > 0:
                daily_rate = self.interest_rate / 30
                self.interest_value = value * (daily_rate / 100) * self.days_overdue

        value += self.penalty_value + self.interest_value
        return value

    def update_status(self) -> None:
        """Atualiza status baseado nos pagamentos."""
        if self.paid_value >= self.current_value:
            self.status = InstallmentStatus.PAGA.value
        elif self.paid_value > 0:
            self.status = InstallmentStatus.PARCIAL.value
        elif self.is_overdue:
            self.status = InstallmentStatus.VENCIDA.value
        else:
            self.status = InstallmentStatus.PENDENTE.value

    def register_payment(
        self,
        value: Decimal,
        payment_date: date,
    ) -> None:
        """Registra pagamento na parcela."""
        self.paid_value += value
        self.payment_date = payment_date
        self.update_status()

    def renegotiate(
        self,
        new_due_date: date,
        new_value: Decimal | None = None,
        reason: str = "",
    ) -> None:
        """Renegocia a parcela."""
        self.original_due_date = self.due_date
        self.due_date = new_due_date
        if new_value:
            self.current_value = new_value
        self.is_renegotiated = True
        self.renegotiation_reason = reason
        self.status = InstallmentStatus.RENEGOCIADA.value

    def cancel(self) -> None:
        """Cancela a parcela."""
        self.status = InstallmentStatus.CANCELADA.value
        self.ativo = False

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "payable_account_id": str(self.payable_account_id),
            "installment_number": self.installment_number,
            "total_installments": self.total_installments,
            "display_number": self.display_number,
            "status": self.status,
            "original_value": float(self.original_value),
            "current_value": float(self.current_value),
            "paid_value": float(self.paid_value),
            "balance": float(self.balance),
            "due_date": self.due_date.isoformat(),
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "is_overdue": self.is_overdue,
            "days_overdue": self.days_overdue,
            "barcode": self.barcode,
            "pix_copy_paste": self.pix_copy_paste,
        }
