"""
Modelo TimeBank (Banco de Horas) para Operações.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class TimeBankEntryType(str, Enum):
    """Tipo de entrada no banco de horas."""

    CREDIT = "credit"  # Crédito (horas a favor do empregador)
    DEBIT = "debit"  # Débito (horas a favor do empregado)
    COMPENSATION = "compensation"  # Compensação (uso do saldo)
    ADJUSTMENT = "adjustment"  # Ajuste manual
    EXPIRATION = "expiration"  # Expiração de horas


class TimeBankStatus(str, Enum):
    """Status da entrada no banco de horas."""

    PENDING = "pending"  # Pendente aprovação
    APPROVED = "approved"  # Aprovada
    REJECTED = "rejected"  # Rejeitada
    USED = "used"  # Utilizada (compensada)
    EXPIRED = "expired"  # Expirada


class TimeBank(Base):
    """
    Modelo de Banco de Horas.

    Controla o saldo de horas extras/compensação por funcionário.

    Attributes:
        id: Identificador único
        employee_id: Funcionário
        entry_type: Tipo de entrada (crédito/débito)
        status: Status da entrada
        hours: Quantidade de horas
        reference_date: Data de referência
        shift_id: Turno relacionado (se houver)
        description: Descrição
        balance_before: Saldo antes da entrada
        balance_after: Saldo após a entrada
    """

    __tablename__ = "time_bank"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Funcionário
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # Tipo e Status
    entry_type: Mapped[str] = mapped_column(
        String(50),
        default=TimeBankEntryType.CREDIT.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=TimeBankStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    # Horas
    hours: Mapped[float] = mapped_column(Float, nullable=False)
    balance_before: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Datas
    reference_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relacionamentos opcionais
    shift_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    post_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Descrição
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Aprovação
    approved_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Compensação (quando usado)
    compensated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    compensation_shift_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Campos de controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<TimeBank {self.employee_id} - {self.entry_type}: {self.hours}h>"

    @property
    def is_credit(self) -> bool:
        """Verifica se é crédito (horas a mais)."""
        return self.entry_type == TimeBankEntryType.CREDIT.value

    @property
    def is_debit(self) -> bool:
        """Verifica se é débito (horas a compensar)."""
        return self.entry_type == TimeBankEntryType.DEBIT.value

    @property
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou."""
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == TimeBankStatus.PENDING.value

    @property
    def signed_hours(self) -> float:
        """Retorna horas com sinal (+ crédito, - débito)."""
        if self.entry_type in (
            TimeBankEntryType.CREDIT.value,
            TimeBankEntryType.ADJUSTMENT.value,
        ):
            return abs(self.hours)
        return -abs(self.hours)

    @property
    def days_until_expiration(self) -> Optional[int]:
        """Dias até expiração."""
        if not self.expiration_date:
            return None
        return (self.expiration_date - date.today()).days
