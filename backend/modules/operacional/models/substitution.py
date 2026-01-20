"""
Modelo Substitution (Substituição de Funcionário) para Operações.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class SubstitutionStatus(str, Enum):
    """Status da substituição."""

    PENDING = "pending"  # Aguardando confirmação
    CONFIRMED = "confirmed"  # Confirmada pelo substituto
    IN_PROGRESS = "in_progress"  # Em andamento
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    REJECTED = "rejected"  # Rejeitada pelo substituto


class SubstitutionReason(str, Enum):
    """Motivo da substituição."""

    SICK_LEAVE = "sick_leave"  # Atestado médico
    VACATION = "vacation"  # Férias
    PERSONAL = "personal"  # Motivo pessoal
    TRAINING = "training"  # Treinamento
    NO_SHOW = "no_show"  # Falta sem justificativa
    EMERGENCY = "emergency"  # Emergência
    OTHER = "other"  # Outro


class Substitution(Base):
    """
    Modelo de Substituição de Funcionário.

    Registra quando um funcionário precisa ser substituído em um turno.

    Attributes:
        id: Identificador único
        shift_id: Turno original
        original_employee_id: Funcionário que faltou
        substitute_employee_id: Funcionário substituto
        reason: Motivo da substituição
        status: Status da substituição
        substitution_date: Data da substituição
        requested_at: Quando foi solicitada
        confirmed_at: Quando foi confirmada
        additional_cost: Custo adicional (hora extra)
    """

    __tablename__ = "substitutions"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Relacionamentos
    shift_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("shifts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # Funcionários
    original_employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    substitute_employee_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Motivo e Status
    reason: Mapped[str] = mapped_column(
        String(50),
        default=SubstitutionReason.OTHER.value,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=SubstitutionStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    # Datas
    substitution_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Custos
    additional_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_overtime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reason_details: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Notificações
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notification_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Quem solicitou/aprovou
    requested_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    approved_by: Mapped[Optional[str]] = mapped_column(
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

    def __repr__(self) -> str:
        return f"<Substitution {self.substitution_date} - {self.status}>"

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == SubstitutionStatus.PENDING.value

    @property
    def is_confirmed(self) -> bool:
        """Verifica se foi confirmada."""
        return self.status in (
            SubstitutionStatus.CONFIRMED.value,
            SubstitutionStatus.IN_PROGRESS.value,
            SubstitutionStatus.COMPLETED.value,
        )

    @property
    def has_substitute(self) -> bool:
        """Verifica se tem substituto definido."""
        return self.substitute_employee_id is not None

    @property
    def response_time_hours(self) -> Optional[float]:
        """Calcula tempo de resposta em horas."""
        if not self.confirmed_at:
            return None
        delta = self.confirmed_at - self.requested_at
        return delta.total_seconds() / 3600
