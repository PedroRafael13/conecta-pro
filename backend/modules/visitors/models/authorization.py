"""Modelo de Autorização de Visitante."""

import random
import string
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from core.database import Base

if TYPE_CHECKING:
    from modules.visitors.models.visitor import Visitor


class AuthorizationType(str, Enum):
    """Tipos de autorização."""

    UNICA = "unica"
    PERIODO = "periodo"
    PERMANENTE = "permanente"
    RECORRENTE = "recorrente"
    EVENTO = "evento"
    EMERGENCIA = "emergencia"


class AuthorizationStatus(str, Enum):
    """Status da autorização."""

    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    EXPIRADA = "expirada"
    CANCELADA = "cancelada"
    UTILIZADA = "utilizada"
    SUSPENSA = "suspensa"


class RecurrenceType(str, Enum):
    """Tipos de recorrência."""

    DIARIA = "diaria"
    SEMANAL = "semanal"
    QUINZENAL = "quinzenal"
    MENSAL = "mensal"
    DIAS_ESPECIFICOS = "dias_especificos"


class VisitorAuthorization(Base):
    """Modelo de Autorização de Visitante."""

    __tablename__ = "visitor_authorizations"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Visitante
    visitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("visitors.id"), nullable=False
    )

    # Tipo e status
    authorization_type: Mapped[AuthorizationType] = mapped_column(
        String(20), default=AuthorizationType.UNICA
    )
    status: Mapped[AuthorizationStatus] = mapped_column(
        String(20), default=AuthorizationStatus.PENDENTE
    )

    # Condomínio e Unidade
    condominium_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))
    unit_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    unit_number: Mapped[Optional[str]] = mapped_column(String(20))
    block: Mapped[Optional[str]] = mapped_column(String(20))

    # Morador autorizador
    resident_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    resident_name: Mapped[Optional[str]] = mapped_column(String(200))
    resident_phone: Mapped[Optional[str]] = mapped_column(String(20))
    resident_email: Mapped[Optional[str]] = mapped_column(String(200))

    # Período de validade
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    valid_date: Mapped[Optional[datetime]] = mapped_column(Date)

    # Horário permitido
    time_from: Mapped[Optional[datetime]] = mapped_column(Time)
    time_until: Mapped[Optional[datetime]] = mapped_column(Time)
    allow_all_hours: Mapped[bool] = mapped_column(Boolean, default=False)

    # Recorrência
    recurrence_type: Mapped[Optional[RecurrenceType]] = mapped_column(String(20))
    recurrence_days: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    max_uses: Mapped[Optional[int]] = mapped_column(Integer)
    uses_count: Mapped[int] = mapped_column(Integer, default=0)

    # Áreas permitidas
    allowed_areas: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    allowed_parking: Mapped[bool] = mapped_column(Boolean, default=False)
    parking_spot: Mapped[Optional[str]] = mapped_column(String(20))

    # Motivo e observações
    purpose: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Aprovação
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    approved_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Notificações
    notify_on_entry: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_exit: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_resident: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Evento (para autorizações de evento)
    event_name: Mapped[Optional[str]] = mapped_column(String(200))
    event_description: Mapped[Optional[str]] = mapped_column(Text)
    expected_guests: Mapped[Optional[int]] = mapped_column(Integer)

    # QR Code e acesso
    qr_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    access_code: Mapped[Optional[str]] = mapped_column(String(20))
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)

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

    # Relacionamentos
    visitor: Mapped["Visitor"] = relationship(
        "Visitor", back_populates="authorizations"
    )

    def __init__(self, **kwargs):
        """Inicializa a autorização."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()
        if not self.qr_code:
            self.qr_code = self._generate_qr_code()
        if not self.access_code:
            self.access_code = self._generate_access_code()

    def _generate_code(self) -> str:
        """Gera código único."""
        chars = string.ascii_uppercase + string.digits
        random_part = "".join(random.choices(chars, k=8))
        return f"AUT-{random_part}"

    def _generate_qr_code(self) -> str:
        """Gera QR Code único."""
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=20))

    def _generate_access_code(self) -> str:
        """Gera código de acesso numérico."""
        return "".join(random.choices(string.digits, k=6))

    def approve(
        self, approved_by_id: str = None, approved_by_name: str = None
    ) -> None:
        """Aprova a autorização."""
        self.status = AuthorizationStatus.APROVADA
        self.approved_at = datetime.utcnow()
        self.approved_by_id = approved_by_id
        self.approved_by_name = approved_by_name

    def reject(self, reason: str = None) -> None:
        """Rejeita a autorização."""
        self.status = AuthorizationStatus.REJEITADA
        self.rejection_reason = reason

    def cancel(self, reason: str = None) -> None:
        """Cancela a autorização."""
        self.status = AuthorizationStatus.CANCELADA
        if reason:
            self.notes = f"{self.notes or ''}\nCancelado: {reason}".strip()

    def suspend(self, reason: str = None) -> None:
        """Suspende a autorização."""
        self.status = AuthorizationStatus.SUSPENSA
        if reason:
            self.notes = f"{self.notes or ''}\nSuspenso: {reason}".strip()

    def reactivate(self) -> None:
        """Reativa a autorização."""
        if self.status == AuthorizationStatus.SUSPENSA:
            self.status = AuthorizationStatus.APROVADA

    def use(self) -> bool:
        """Registra uso da autorização."""
        if not self.can_use:
            return False

        self.uses_count += 1

        if self.authorization_type == AuthorizationType.UNICA:
            self.status = AuthorizationStatus.UTILIZADA

        if self.max_uses and self.uses_count >= self.max_uses:
            self.status = AuthorizationStatus.UTILIZADA

        return True

    def expire(self) -> None:
        """Marca como expirada."""
        self.status = AuthorizationStatus.EXPIRADA

    def extend_validity(self, days: int) -> None:
        """Estende a validade."""
        if self.valid_until:
            self.valid_until = self.valid_until + timedelta(days=days)
        else:
            self.valid_until = datetime.utcnow() + timedelta(days=days)

    def soft_delete(self) -> None:
        """Soft delete."""
        self.is_deleted = True

    @property
    def is_valid(self) -> bool:
        """Verifica se está dentro da validade."""
        now = datetime.utcnow()
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True

    @property
    def is_within_allowed_time(self) -> bool:
        """Verifica se está dentro do horário permitido."""
        if self.allow_all_hours:
            return True
        if not self.time_from or not self.time_until:
            return True

        now = datetime.utcnow().time()
        return self.time_from <= now <= self.time_until

    @property
    def is_within_allowed_day(self) -> bool:
        """Verifica se está no dia permitido."""
        if self.authorization_type == AuthorizationType.PERMANENTE:
            return True
        if self.recurrence_type == RecurrenceType.DIAS_ESPECIFICOS:
            today = datetime.utcnow().weekday()
            return today in (self.recurrence_days or [])
        if self.valid_date:
            return self.valid_date == datetime.utcnow().date()
        return True

    @property
    def can_use(self) -> bool:
        """Verifica se pode ser utilizada."""
        if self.status != AuthorizationStatus.APROVADA:
            return False
        if not self.is_valid:
            return False
        if not self.is_within_allowed_time:
            return False
        if not self.is_within_allowed_day:
            return False
        if self.max_uses and self.uses_count >= self.max_uses:
            return False
        return True

    @property
    def remaining_uses(self) -> Optional[int]:
        """Usos restantes."""
        if not self.max_uses:
            return None
        return max(0, self.max_uses - self.uses_count)

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Dias até expirar."""
        if not self.valid_until:
            return None
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)

    @property
    def is_expired(self) -> bool:
        """Verifica se expirou."""
        if not self.valid_until:
            return False
        return self.valid_until < datetime.utcnow()

    @property
    def status_display(self) -> str:
        """Status para exibição."""
        status_map = {
            AuthorizationStatus.PENDENTE: "Aguardando aprovação",
            AuthorizationStatus.APROVADA: "Aprovada",
            AuthorizationStatus.REJEITADA: "Rejeitada",
            AuthorizationStatus.EXPIRADA: "Expirada",
            AuthorizationStatus.CANCELADA: "Cancelada",
            AuthorizationStatus.UTILIZADA: "Utilizada",
            AuthorizationStatus.SUSPENSA: "Suspensa",
        }
        return status_map.get(self.status, self.status.value)
