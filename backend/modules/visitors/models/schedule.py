"""Modelo de Agendamento de Visita."""

import random
import string
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from core.database import Base


class ScheduleStatus(str, Enum):
    """Status do agendamento."""

    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    REALIZADO = "realizado"
    NAO_COMPARECEU = "nao_compareceu"
    REAGENDADO = "reagendado"
    EXPIRADO = "expirado"


class SchedulePriority(str, Enum):
    """Prioridade do agendamento."""

    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class VisitorSchedule(Base):
    """Modelo de Agendamento de Visita."""

    __tablename__ = "visitor_schedules"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Visitante (pode ser null para pré-agendamento)
    visitor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("visitors.id")
    )

    # Dados do visitante (para pré-agendamento)
    visitor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    visitor_document: Mapped[Optional[str]] = mapped_column(String(50))
    visitor_phone: Mapped[Optional[str]] = mapped_column(String(20))
    visitor_email: Mapped[Optional[str]] = mapped_column(String(200))
    visitor_company: Mapped[Optional[str]] = mapped_column(String(200))

    # Status e prioridade
    status: Mapped[ScheduleStatus] = mapped_column(
        String(20), default=ScheduleStatus.PENDENTE
    )
    priority: Mapped[SchedulePriority] = mapped_column(
        String(20), default=SchedulePriority.NORMAL
    )

    # Condomínio e Unidade
    condominium_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))
    unit_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    unit_number: Mapped[Optional[str]] = mapped_column(String(20))
    block: Mapped[Optional[str]] = mapped_column(String(20))

    # Morador que agendou
    resident_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    resident_name: Mapped[Optional[str]] = mapped_column(String(200))
    resident_phone: Mapped[Optional[str]] = mapped_column(String(20))
    resident_email: Mapped[Optional[str]] = mapped_column(String(200))

    # Data e hora agendada
    scheduled_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    scheduled_time_from: Mapped[Optional[datetime]] = mapped_column(Time)
    scheduled_time_until: Mapped[Optional[datetime]] = mapped_column(Time)
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    # Motivo e observações
    purpose: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Veículo
    has_vehicle: Mapped[bool] = mapped_column(Boolean, default=False)
    vehicle_plate: Mapped[Optional[str]] = mapped_column(String(10))
    vehicle_model: Mapped[Optional[str]] = mapped_column(String(100))
    needs_parking: Mapped[bool] = mapped_column(Boolean, default=False)

    # Acompanhantes
    companions_count: Mapped[int] = mapped_column(Integer, default=0)
    companions_names: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Confirmação
    confirmation_required: Mapped[bool] = mapped_column(Boolean, default=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    confirmed_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    confirmed_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    confirmation_code: Mapped[Optional[str]] = mapped_column(String(20))

    # Cancelamento
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelled_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    cancelled_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Reagendamento
    rescheduled_from_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    reschedule_count: Mapped[int] = mapped_column(Integer, default=0)

    # Realização
    realized_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    check_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    check_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    log_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # Notificações
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    notification_channels: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Aprovação (se necessário)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    approved_by_name: Mapped[Optional[str]] = mapped_column(String(200))

    # QR Code
    qr_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True)

    # Controle
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    created_by_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    def __init__(self, **kwargs):
        """Inicializa o agendamento."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()
        if not self.confirmation_code:
            self.confirmation_code = self._generate_confirmation_code()
        if not self.qr_code:
            self.qr_code = self._generate_qr_code()

    def _generate_code(self) -> str:
        """Gera código único."""
        chars = string.ascii_uppercase + string.digits
        random_part = "".join(random.choices(chars, k=8))
        return f"AGD-{random_part}"

    def _generate_confirmation_code(self) -> str:
        """Gera código de confirmação."""
        return "".join(random.choices(string.digits, k=6))

    def _generate_qr_code(self) -> str:
        """Gera QR Code único."""
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=20))

    def confirm(
        self, confirmed_by_id: str = None, confirmed_by_name: str = None
    ) -> None:
        """Confirma o agendamento."""
        self.status = ScheduleStatus.CONFIRMADO
        self.confirmed_at = datetime.utcnow()
        self.confirmed_by_id = confirmed_by_id
        self.confirmed_by_name = confirmed_by_name

    def cancel(
        self,
        reason: str = None,
        cancelled_by_id: str = None,
        cancelled_by_name: str = None,
    ) -> None:
        """Cancela o agendamento."""
        self.status = ScheduleStatus.CANCELADO
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by_id = cancelled_by_id
        self.cancelled_by_name = cancelled_by_name
        self.cancellation_reason = reason

    def reschedule(self, new_date: datetime, new_time_from: datetime = None) -> None:
        """Reagenda."""
        self.status = ScheduleStatus.REAGENDADO
        self.rescheduled_from_id = self.id
        self.reschedule_count += 1
        self.scheduled_date = new_date
        if new_time_from:
            self.scheduled_time_from = new_time_from

    def realize(self, log_id: uuid.UUID = None) -> None:
        """Marca como realizado."""
        self.status = ScheduleStatus.REALIZADO
        self.realized_at = datetime.utcnow()
        self.log_id = log_id

    def check_in(self) -> None:
        """Registra check-in."""
        self.check_in_at = datetime.utcnow()
        self.status = ScheduleStatus.REALIZADO

    def check_out(self) -> None:
        """Registra check-out."""
        self.check_out_at = datetime.utcnow()

    def no_show(self) -> None:
        """Marca como não compareceu."""
        self.status = ScheduleStatus.NAO_COMPARECEU

    def expire(self) -> None:
        """Marca como expirado."""
        self.status = ScheduleStatus.EXPIRADO

    def approve(
        self, approved_by_id: str = None, approved_by_name: str = None
    ) -> None:
        """Aprova o agendamento."""
        self.approved_at = datetime.utcnow()
        self.approved_by_id = approved_by_id
        self.approved_by_name = approved_by_name
        if self.status == ScheduleStatus.PENDENTE:
            self.status = ScheduleStatus.CONFIRMADO

    def send_reminder(self) -> None:
        """Marca lembrete como enviado."""
        self.reminder_sent = True
        self.reminder_sent_at = datetime.utcnow()

    def add_companions(self, count: int, names: list = None) -> None:
        """Adiciona acompanhantes."""
        self.companions_count = count
        if names:
            self.companions_names = names

    def add_vehicle(self, plate: str, model: str = None, needs_parking: bool = False):
        """Adiciona veículo."""
        self.has_vehicle = True
        self.vehicle_plate = plate
        self.vehicle_model = model
        self.needs_parking = needs_parking

    def soft_delete(self) -> None:
        """Soft delete."""
        self.is_deleted = True

    @property
    def is_past(self) -> bool:
        """Verifica se é data passada."""
        return self.scheduled_date < datetime.utcnow().date()

    @property
    def is_today(self) -> bool:
        """Verifica se é hoje."""
        return self.scheduled_date == datetime.utcnow().date()

    @property
    def is_future(self) -> bool:
        """Verifica se é data futura."""
        return self.scheduled_date > datetime.utcnow().date()

    @property
    def is_confirmed(self) -> bool:
        """Verifica se está confirmado."""
        return self.status == ScheduleStatus.CONFIRMADO

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == ScheduleStatus.PENDENTE

    @property
    def is_cancelled(self) -> bool:
        """Verifica se foi cancelado."""
        return self.status == ScheduleStatus.CANCELADO

    @property
    def is_realized(self) -> bool:
        """Verifica se foi realizado."""
        return self.status == ScheduleStatus.REALIZADO

    @property
    def can_check_in(self) -> bool:
        """Verifica se pode fazer check-in."""
        return (
            self.status in [ScheduleStatus.CONFIRMADO, ScheduleStatus.PENDENTE]
            and self.is_today
            and not self.check_in_at
        )

    @property
    def days_until(self) -> int:
        """Dias até a visita."""
        delta = self.scheduled_date - datetime.utcnow().date()
        return delta.days

    @property
    def time_display(self) -> str:
        """Horário formatado."""
        if self.scheduled_time_from and self.scheduled_time_until:
            return (
                f"{self.scheduled_time_from.strftime('%H:%M')} - "
                f"{self.scheduled_time_until.strftime('%H:%M')}"
            )
        if self.scheduled_time_from:
            return self.scheduled_time_from.strftime("%H:%M")
        return "Horário flexível"

    @property
    def status_display(self) -> str:
        """Status para exibição."""
        status_map = {
            ScheduleStatus.PENDENTE: "Aguardando confirmação",
            ScheduleStatus.CONFIRMADO: "Confirmado",
            ScheduleStatus.CANCELADO: "Cancelado",
            ScheduleStatus.REALIZADO: "Realizado",
            ScheduleStatus.NAO_COMPARECEU: "Não compareceu",
            ScheduleStatus.REAGENDADO: "Reagendado",
            ScheduleStatus.EXPIRADO: "Expirado",
        }
        return status_map.get(self.status, self.status.value)
