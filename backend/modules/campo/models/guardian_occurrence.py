"""
Modelo GuardianOccurrence para ocorrências do Guardian.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class OccurrenceType(StrEnum):
    """Tipo de ocorrência."""

    ALARM = "alarm"  # Alarme
    INTRUSION = "intrusion"  # Invasão
    FIRE = "fire"  # Incêndio
    PANIC = "panic"  # Pânico
    MEDICAL = "medical"  # Emergência médica
    EQUIPMENT_FAILURE = "equipment_failure"  # Falha de equipamento
    POWER_OUTAGE = "power_outage"  # Queda de energia
    SUSPICIOUS_ACTIVITY = "suspicious_activity"  # Atividade suspeita
    VANDALISM = "vandalism"  # Vandalismo
    THEFT = "theft"  # Furto/roubo
    VISITOR_INCIDENT = "visitor_incident"  # Incidente com visitante
    INTERCOM_EMERGENCY = "intercom_emergency"  # Emergência pelo interfone
    VEHICLE_INCIDENT = "vehicle_incident"  # Incidente com veículo
    OTHER = "other"  # Outros


class OccurrenceSeverity(StrEnum):
    """Gravidade da ocorrência."""

    LOW = "low"  # Baixa
    MEDIUM = "medium"  # Média
    HIGH = "high"  # Alta
    CRITICAL = "critical"  # Crítica


class OccurrenceStatus(StrEnum):
    """Status da ocorrência."""

    OPEN = "open"  # Aberta
    ACKNOWLEDGED = "acknowledged"  # Reconhecida
    IN_PROGRESS = "in_progress"  # Em atendimento
    RESOLVED = "resolved"  # Resolvida
    ESCALATED = "escalated"  # Escalada
    CLOSED = "closed"  # Fechada
    CANCELLED = "cancelled"  # Cancelada (falso alarme)


class GuardianOccurrence(Base):
    """
    Modelo de Ocorrência do Guardian.

    Armazena ocorrências recebidas do Conecta Guardian, incluindo
    alarmes, incidentes, emergências e eventos de segurança.

    Attributes:
        id: Identificador único
        guardian_id: ID original no Guardian
        occurrence_code: Código da ocorrência
        occurrence_type: Tipo de ocorrência
        severity: Gravidade
        status: Status atual
        client_id: ID do cliente
        contract_id: ID do contrato
        post_id: ID do posto
        title: Título da ocorrência
        description: Descrição detalhada
        location: Local exato
        action_taken: Ação tomada
        involved_persons: Pessoas envolvidas
        witnesses: Testemunhas
        images: URLs de imagens
        videos: URLs de vídeos
        police_report: Número do BO
        event_timestamp: Data/hora do evento
        resolved_at: Data/hora de resolução
    """

    __tablename__ = "guardian_occurrences"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    guardian_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    occurrence_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Classificação
    occurrence_type: Mapped[str] = mapped_column(
        String(30),
        default=OccurrenceType.OTHER.value,
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        default=OccurrenceSeverity.MEDIUM.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=OccurrenceStatus.OPEN.value,
        nullable=False,
        index=True,
    )

    # Referências
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )
    contract_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    post_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Descrição
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ações
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_required: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pessoas
    involved_persons: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    witnesses: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    reported_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reported_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Atendimento
    operator_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    operator_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    response_time_seconds: Mapped[int | None] = mapped_column(nullable=True)
    resolution_time_seconds: Mapped[int | None] = mapped_column(nullable=True)

    # Escalação
    escalated_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Serviços externos
    police_notified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    police_report_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    fire_department_notified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    ambulance_notified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Mídia
    images: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    videos: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    audio_recordings: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    attachments: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Timestamps
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    # Controle
    is_false_alarm: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_followup: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    followup_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    # Metadados
    guardian_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sync_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        """Representação textual."""
        return f"<GuardianOccurrence {self.occurrence_code} {self.occurrence_type}>"

    @property
    def is_open(self) -> bool:
        """Verifica se está aberta."""
        return self.status in (
            OccurrenceStatus.OPEN.value,
            OccurrenceStatus.ACKNOWLEDGED.value,
            OccurrenceStatus.IN_PROGRESS.value,
        )

    @property
    def is_resolved(self) -> bool:
        """Verifica se foi resolvida."""
        return self.status in (
            OccurrenceStatus.RESOLVED.value,
            OccurrenceStatus.CLOSED.value,
        )

    @property
    def is_critical(self) -> bool:
        """Verifica se é crítica."""
        return self.severity == OccurrenceSeverity.CRITICAL.value

    @property
    def is_high_severity(self) -> bool:
        """Verifica se tem alta gravidade."""
        return self.severity in (
            OccurrenceSeverity.HIGH.value,
            OccurrenceSeverity.CRITICAL.value,
        )

    @property
    def has_media(self) -> bool:
        """Verifica se tem mídia anexada."""
        return bool(self.images) or bool(self.videos)

    @property
    def involved_external_services(self) -> bool:
        """Verifica se envolveu serviços externos."""
        return self.police_notified or self.fire_department_notified or self.ambulance_notified

    def acknowledge(self, operator_id: str, operator_name: str) -> None:
        """Reconhece a ocorrência."""
        self.status = OccurrenceStatus.ACKNOWLEDGED.value
        self.operator_id = operator_id
        self.operator_name = operator_name
        self.acknowledged_at = datetime.utcnow()
        if self.event_timestamp:
            delta = datetime.utcnow() - self.event_timestamp
            self.response_time_seconds = int(delta.total_seconds())

    def start_progress(self) -> None:
        """Inicia o atendimento."""
        self.status = OccurrenceStatus.IN_PROGRESS.value

    def resolve(self, resolution: str) -> None:
        """Resolve a ocorrência."""
        self.status = OccurrenceStatus.RESOLVED.value
        self.resolution = resolution
        self.resolved_at = datetime.utcnow()
        if self.acknowledged_at:
            delta = datetime.utcnow() - self.acknowledged_at
            self.resolution_time_seconds = int(delta.total_seconds())

    def escalate(self, to: str, reason: str) -> None:
        """Escala a ocorrência."""
        self.status = OccurrenceStatus.ESCALATED.value
        self.escalated_to = to
        self.escalation_reason = reason
        self.escalated_at = datetime.utcnow()

    def close(self) -> None:
        """Fecha a ocorrência."""
        self.status = OccurrenceStatus.CLOSED.value
        self.closed_at = datetime.utcnow()

    def mark_as_false_alarm(self) -> None:
        """Marca como falso alarme."""
        self.is_false_alarm = True
        self.status = OccurrenceStatus.CANCELLED.value
        self.closed_at = datetime.utcnow()
