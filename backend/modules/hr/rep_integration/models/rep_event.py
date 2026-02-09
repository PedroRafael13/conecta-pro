"""Modelo REPEvent - Eventos de Registro de Ponto.

Armazena eventos brutos recebidos dos dispositivos REP.
Conformidade com Portaria 671 MTE - formato AFD.
"""

import uuid
from datetime import date, datetime, time
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    pass


class EventType(StrEnum):
    """Tipos de evento conforme Portaria 671."""

    ENTRY = "entry"  # Entrada (código 1)
    EXIT = "exit"  # Saída (código 2)
    BREAK_START = "break_start"  # Início intervalo (código 3)
    BREAK_END = "break_end"  # Fim intervalo (código 4)
    EXTRA_ENTRY = "extra_entry"  # Entrada extra (código 5)
    EXTRA_EXIT = "extra_exit"  # Saída extra (código 6)


class IdentificationMethod(StrEnum):
    """Métodos de identificação."""

    BIOMETRIC = "biometric"
    FACIAL = "facial"
    RFID = "rfid"
    PASSWORD = "password"  # noqa: S105
    QRCODE = "qrcode"
    MANUAL = "manual"
    NFC = "nfc"


class EventStatus(StrEnum):
    """Status do evento."""

    RECEIVED = "received"  # Recebido do REP
    VALIDATED = "validated"  # Validado
    PROCESSED = "processed"  # Processado (criou TimeEntry)
    ERROR = "error"  # Erro no processamento
    DUPLICATE = "duplicate"  # Duplicado (ignorado)
    REJECTED = "rejected"  # Rejeitado (funcionário não cadastrado, etc.)


class REPEvent(Base):
    """Modelo de Evento do REP."""

    __tablename__ = "rep_events"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rep_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # NSR - Número Sequencial de Registro (obrigatório Portaria 671)
    nsr: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Número Sequencial de Registro no REP",
    )

    # Dados do evento
    event_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )
    event_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    event_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=EventType.ENTRY.value,
    )

    # Identificação do funcionário
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID do funcionário no sistema",
    )
    pis_number: Mapped[str | None] = mapped_column(
        String(11),
        nullable=True,
        index=True,
        comment="Número PIS/PASEP",
    )
    employee_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Código do funcionário no REP",
    )
    employee_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nome recebido do REP",
    )

    # Método de identificação
    identification_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=IdentificationMethod.BIOMETRIC.value,
    )
    identification_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Score de confiança (0-100) para biometria/facial",
    )

    # Dados biométricos (hash, não o template)
    biometric_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="Hash SHA-256 do template biométrico",
    )
    finger_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Índice do dedo (1-10)",
    )

    # Dados de cartão RFID
    card_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    card_facility_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Foto capturada (se disponível)
    photo_captured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    photo_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Geolocalização (se disponível)
    latitude: Mapped[float | None] = mapped_column(
        nullable=True,
    )
    longitude: Mapped[float | None] = mapped_column(
        nullable=True,
    )
    location_accuracy: Mapped[float | None] = mapped_column(
        nullable=True,
        comment="Precisão em metros",
    )

    # Status e processamento
    status: Mapped[str] = mapped_column(
        String(20),
        default=EventStatus.RECEIVED.value,
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    time_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID do TimeEntry gerado",
    )

    # Erros
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    error_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )

    # Dados brutos do REP
    raw_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Dados brutos recebidos do REP",
    )
    afd_line: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Linha AFD gerada",
    )

    # Validações
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    validation_errors: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # Sync tracking
    sync_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID da sincronização que trouxe este evento",
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    __table_args__ = (
        Index("ix_rep_events_device_nsr", "device_id", "nsr", unique=True),
        Index("ix_rep_events_device_datetime", "device_id", "event_datetime"),
        Index("ix_rep_events_employee_date", "employee_id", "event_date"),
        Index("ix_rep_events_pis_date", "pis_number", "event_date"),
        Index("ix_rep_events_status_pending", "status", postgresql_where="status IN ('received', 'validated')"),
    )

    def __repr__(self) -> str:
        return f"<REPEvent {self.nsr} @ {self.event_datetime}>"

    @property
    def is_processed(self) -> bool:
        """Verifica se evento foi processado."""
        return self.status == EventStatus.PROCESSED.value

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar reprocessar."""
        return self.status == EventStatus.ERROR.value and self.retry_count < self.max_retries

    def generate_afd_line(self) -> str:
        """Gera linha AFD conforme Portaria 671.

        Formato AFD Tipo 3 (marcação):
        Posição 01-09: NSR (9 dígitos)
        Posição 10: Tipo de registro (3)
        Posição 11-18: Data (ddmmaaaa)
        Posição 19-22: Hora (hhmm)
        Posição 23-34: PIS (12 dígitos)
        """
        nsr_str = str(self.nsr).zfill(9)
        tipo = "3"
        data_str = self.event_date.strftime("%d%m%Y")
        hora_str = self.event_time.strftime("%H%M")
        pis_str = (self.pis_number or "").zfill(12)[:12]

        return f"{nsr_str}{tipo}{data_str}{hora_str}{pis_str}"

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "device_id": str(self.device_id),
            "nsr": self.nsr,
            "event_datetime": self.event_datetime.isoformat(),
            "event_type": self.event_type,
            "employee_id": str(self.employee_id) if self.employee_id else None,
            "pis_number": self.pis_number,
            "employee_name": self.employee_name,
            "identification_method": self.identification_method,
            "status": self.status,
            "is_valid": self.is_valid,
        }
