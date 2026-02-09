"""Model para parcelas de contas a receber."""

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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.receivable_account import ReceivableAccount
    from modules.financial.models.receivable_payment import ReceivablePayment


class InstallmentStatus(StrEnum):
    """Status da parcela."""

    PENDENTE = "pendente"
    VENCIDA = "vencida"
    PARCIAL = "parcial"
    PAGA = "paga"
    CANCELADA = "cancelada"
    AGENDADA = "agendada"
    RENEGOCIADA = "renegociada"


class ReceivableInstallment(Base):
    """Parcela de conta a receber."""

    __tablename__ = "receivable_installments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receivable_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("receivable_accounts.id"),
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
    installment_number = Column(Integer, nullable=False)
    total_installments = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default=InstallmentStatus.PENDENTE.value)

    # Valores
    original_value = Column(Numeric(15, 2), nullable=False)  # Valor original
    discount_value = Column(Numeric(15, 2), default=0)  # Desconto
    interest_value = Column(Numeric(15, 2), default=0)  # Juros
    penalty_value = Column(Numeric(15, 2), default=0)  # Multa
    addition_value = Column(Numeric(15, 2), default=0)  # Acrescimos
    current_value = Column(Numeric(15, 2), nullable=False)  # Valor atual
    paid_value = Column(Numeric(15, 2), default=0)  # Valor recebido

    # Datas
    due_date = Column(Date, nullable=False, index=True)
    original_due_date = Column(Date, nullable=True)  # Se renegociada
    payment_date = Column(Date, nullable=True)

    # Configuracoes de juros e multa
    interest_rate = Column(Numeric(8, 4), default=1)  # % juros ao mes
    penalty_rate = Column(Numeric(8, 4), default=2)  # % multa
    grace_days = Column(Integer, default=0)  # Dias de carencia

    # Boleto
    boleto_generated = Column(Boolean, default=False)
    boleto_number = Column(String(50), nullable=True)
    boleto_barcode = Column(String(100), nullable=True)
    boleto_digitable_line = Column(String(100), nullable=True)
    boleto_url = Column(String(500), nullable=True)
    boleto_generated_at = Column(DateTime, nullable=True)
    boleto_expires_at = Column(Date, nullable=True)

    # PIX
    pix_generated = Column(Boolean, default=False)
    pix_qrcode = Column(Text, nullable=True)
    pix_copy_paste = Column(String(500), nullable=True)
    pix_txid = Column(String(100), nullable=True)
    pix_expires_at = Column(DateTime, nullable=True)

    # Cobranca
    collection_attempts = Column(Integer, default=0)
    last_collection_date = Column(DateTime, nullable=True)
    last_collection_method = Column(String(30), nullable=True)  # email, sms, whatsapp

    # Notificacoes enviadas
    notifications_sent = Column(JSONB, default=list)
    # [{"type": "email", "date": "2024-01-01", "template": "vencimento"}]

    # Renegociacao
    is_renegotiated = Column(Boolean, default=False)
    renegotiated_from_id = Column(
        UUID(as_uuid=True),
        ForeignKey("receivable_installments.id"),
        nullable=True,
    )
    renegotiation_reason = Column(Text, nullable=True)

    # Observacoes
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    receivable_account: "ReceivableAccount" = relationship("ReceivableAccount", back_populates="installments")
    payments: list["ReceivablePayment"] = relationship(
        "ReceivablePayment",
        back_populates="installment",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_receivable_installments_due_date", "due_date"),
        Index("ix_receivable_installments_status", "status"),
        Index("ix_receivable_installments_account", "receivable_account_id"),
        Index(
            "ix_receivable_installments_condominio_status",
            "condominio_id",
            "status",
            "due_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<ReceivableInstallment {self.installment_number}/{self.total_installments}>"

    @property
    def display_number(self) -> str:
        """Numero formatado."""
        return f"{self.installment_number}/{self.total_installments}"

    @property
    def is_overdue(self) -> bool:
        """Verifica se esta vencida."""
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
        """Dias ate vencimento."""
        return (self.due_date - date.today()).days

    @property
    def balance(self) -> Decimal:
        """Saldo a receber."""
        return self.current_value - self.paid_value

    @property
    def is_paid(self) -> bool:
        """Verifica se esta paga."""
        return self.status == InstallmentStatus.PAGA.value

    @property
    def is_partially_paid(self) -> bool:
        """Verifica se esta parcialmente paga."""
        return self.paid_value > 0 and self.paid_value < self.current_value

    @property
    def can_generate_boleto(self) -> bool:
        """Verifica se pode gerar boleto."""
        return not self.is_paid and self.status != InstallmentStatus.CANCELADA.value and self.balance > 0

    def calculate_current_value(self) -> Decimal:
        """Calcula valor atual com juros e multa se vencido."""
        value = self.original_value - self.discount_value + self.addition_value

        if self.is_overdue and not self.is_paid:
            days_late = self.days_overdue - self.grace_days
            if days_late > 0:
                # Aplica multa
                if self.penalty_rate > 0:
                    self.penalty_value = value * (self.penalty_rate / 100)

                # Aplica juros proporcionais
                if self.interest_rate > 0:
                    daily_rate = self.interest_rate / 30
                    self.interest_value = value * (daily_rate / 100) * days_late

        value += self.penalty_value + self.interest_value
        return value

    def update_status(self) -> None:
        """Atualiza status baseado nos recebimentos."""
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
        """Registra recebimento na parcela."""
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

    def generate_boleto(
        self,
        number: str,
        barcode: str,
        digitable_line: str,
        url: str | None = None,
        expires_at: date | None = None,
    ) -> None:
        """Registra geracao de boleto."""
        self.boleto_generated = True
        self.boleto_number = number
        self.boleto_barcode = barcode
        self.boleto_digitable_line = digitable_line
        self.boleto_url = url
        self.boleto_generated_at = datetime.utcnow()
        self.boleto_expires_at = expires_at

    def generate_pix(
        self,
        qrcode: str,
        copy_paste: str,
        txid: str,
        expires_at: datetime | None = None,
    ) -> None:
        """Registra geracao de PIX."""
        self.pix_generated = True
        self.pix_qrcode = qrcode
        self.pix_copy_paste = copy_paste
        self.pix_txid = txid
        self.pix_expires_at = expires_at

    def register_collection_attempt(self, method: str) -> None:
        """Registra tentativa de cobranca."""
        self.collection_attempts += 1
        self.last_collection_date = datetime.utcnow()
        self.last_collection_method = method

    def add_notification(self, notification_type: str, template: str) -> None:
        """Adiciona notificacao enviada."""
        notification = {
            "type": notification_type,
            "date": datetime.utcnow().isoformat(),
            "template": template,
        }
        if not self.notifications_sent:
            self.notifications_sent = []
        self.notifications_sent.append(notification)

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "receivable_account_id": str(self.receivable_account_id),
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
            "boleto_generated": self.boleto_generated,
            "boleto_barcode": self.boleto_barcode,
            "boleto_digitable_line": self.boleto_digitable_line,
            "boleto_url": self.boleto_url,
            "pix_generated": self.pix_generated,
            "pix_copy_paste": self.pix_copy_paste,
        }
