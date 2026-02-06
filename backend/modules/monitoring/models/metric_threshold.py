"""
Modelo de Thresholds para metricas.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import BaseModel


class ThresholdType(str, enum.Enum):
    """Tipo de threshold."""

    UPPER = "upper"  # Valor maximo permitido
    LOWER = "lower"  # Valor minimo permitido
    RANGE = "range"  # Faixa de valores


class MetricThreshold(BaseModel):
    """
    Modelo de threshold para metricas.

    Define os limites para cada nivel de alerta
    (green, yellow, orange, red) para uma metrica especifica.
    """

    __tablename__ = "monitoring_thresholds"

    # Identificacao
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Categoria
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="general",
        index=True,
    )

    # Tipo de threshold
    threshold_type: Mapped[ThresholdType] = mapped_column(
        Enum(ThresholdType),
        nullable=False,
        default=ThresholdType.UPPER,
    )

    # Valores de threshold para cada nivel (para UPPER type)
    # Para UPPER: valor acima do threshold dispara o alerta
    # Para LOWER: valor abaixo do threshold dispara o alerta
    yellow_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    orange_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    red_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # Para RANGE type: limites inferiores
    yellow_lower: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    orange_lower: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    red_lower: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Unidade de medida
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
    )

    # Configuracoes de alerta
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    cooldown_seconds: Mapped[int] = mapped_column(
        Integer,
        default=300,  # 5 minutos
        nullable=False,
    )
    consecutive_breaches: Mapped[int] = mapped_column(
        Integer,
        default=1,  # Disparar no primeiro breach
        nullable=False,
    )

    # Notificacao
    notify_channels: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {"email": True, "slack": False, "sms": False},
    )

    # Metadata
    tags: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # Ultimo alerta gerado
    last_alert_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_value: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<MetricThreshold(metric={self.metric_name})>"

    def get_level_for_value(self, value: float) -> str:
        """
        Determina o nivel de alerta para um valor.

        Returns:
            'green', 'yellow', 'orange' ou 'red'
        """
        if self.threshold_type == ThresholdType.UPPER:
            if value >= self.red_threshold:
                return "red"
            elif value >= self.orange_threshold:
                return "orange"
            elif value >= self.yellow_threshold:
                return "yellow"
            return "green"

        elif self.threshold_type == ThresholdType.LOWER:
            if value <= self.red_threshold:
                return "red"
            elif value <= self.orange_threshold:
                return "orange"
            elif value <= self.yellow_threshold:
                return "yellow"
            return "green"

        else:  # RANGE
            # Verificar limites superiores
            if value >= self.red_threshold:
                return "red"
            elif value >= self.orange_threshold:
                return "orange"
            elif value >= self.yellow_threshold:
                return "yellow"

            # Verificar limites inferiores
            if self.red_lower is not None and value <= self.red_lower:
                return "red"
            if self.orange_lower is not None and value <= self.orange_lower:
                return "orange"
            if self.yellow_lower is not None and value <= self.yellow_lower:
                return "yellow"

            return "green"

    def should_alert(self, value: float, last_alert_time: Optional[datetime] = None) -> bool:
        """
        Verifica se deve gerar alerta.

        Considera:
        - Se threshold esta habilitado
        - Se valor ultrapassa threshold
        - Se cooldown foi respeitado
        """
        if not self.enabled:
            return False

        level = self.get_level_for_value(value)
        if level == "green":
            return False

        # Verificar cooldown
        if last_alert_time:
            elapsed = (datetime.utcnow() - last_alert_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False

        return True

    def get_threshold_for_level(self, level: str) -> float:
        """Retorna o threshold para um nivel especifico."""
        mapping = {
            "yellow": self.yellow_threshold,
            "orange": self.orange_threshold,
            "red": self.red_threshold,
        }
        return mapping.get(level, 0)
