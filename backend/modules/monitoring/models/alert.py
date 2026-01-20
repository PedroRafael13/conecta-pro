"""
Modelo de Alertas para Early Warning System.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base, BaseModel


class AlertLevel(str, enum.Enum):
    """Niveis de alerta do Early Warning System."""

    GREEN = "green"  # Operacao normal
    YELLOW = "yellow"  # Atencao necessaria
    ORANGE = "orange"  # Acao corretiva em 24-48h
    RED = "red"  # Intervencao imediata


class AlertStatus(str, enum.Enum):
    """Status do alerta."""

    ACTIVE = "active"  # Alerta ativo
    ACKNOWLEDGED = "acknowledged"  # Reconhecido por operador
    RESOLVED = "resolved"  # Resolvido
    ESCALATED = "escalated"  # Escalado para nivel superior
    SUPPRESSED = "suppressed"  # Suprimido temporariamente


class Alert(BaseModel):
    """
    Modelo de alerta do sistema.

    Representa um alerta gerado pelo Early Warning System
    quando uma metrica ultrapassa um threshold definido.
    """

    __tablename__ = "monitoring_alerts"

    # Identificacao
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="system",
    )

    # Niveis e status
    level: Mapped[AlertLevel] = mapped_column(
        Enum(AlertLevel),
        nullable=False,
        default=AlertLevel.YELLOW,
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus),
        nullable=False,
        default=AlertStatus.ACTIVE,
    )

    # Valores
    current_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    threshold_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Detalhes
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    details: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Usuario que resolveu/reconheceu
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Notas de resolucao
    resolution_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Threshold relacionado
    threshold_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monitoring_thresholds.id"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, metric={self.metric_name}, level={self.level})>"

    @property
    def is_critical(self) -> bool:
        """Verifica se alerta e critico."""
        return self.level in (AlertLevel.ORANGE, AlertLevel.RED)

    @property
    def duration_seconds(self) -> float:
        """Duracao do alerta em segundos."""
        end_time = self.resolved_at or datetime.utcnow()
        return (end_time - self.triggered_at).total_seconds()

    def acknowledge(self, user_id: uuid.UUID) -> None:
        """Reconhece o alerta."""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id

    def resolve(self, user_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Resolve o alerta."""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes

    def escalate(self) -> None:
        """Escala o alerta."""
        self.status = AlertStatus.ESCALATED

    def suppress(self) -> None:
        """Suprime o alerta temporariamente."""
        self.status = AlertStatus.SUPPRESSED
