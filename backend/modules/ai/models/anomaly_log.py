"""AnomalyLog Model - Logs de Anomalias Detectadas.

Sprint 34 - AI Predictions.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models import Base


class AnomalyType(str, enum.Enum):
    """Tipo de anomalia."""

    OUTLIER = "OUTLIER"  # Valor fora do padrao
    SPIKE = "SPIKE"  # Pico subito
    DROP = "DROP"  # Queda subita
    TREND_CHANGE = "TREND_CHANGE"  # Mudanca de tendencia
    SEASONAL_DEVIATION = "SEASONAL_DEVIATION"  # Desvio sazonal
    MISSING_DATA = "MISSING_DATA"  # Dados ausentes
    DUPLICATE = "DUPLICATE"  # Dados duplicados
    PATTERN_BREAK = "PATTERN_BREAK"  # Quebra de padrao
    FRAUD = "FRAUD"  # Possivel fraude
    ERROR = "ERROR"  # Erro de dados
    OTHER = "OTHER"  # Outro tipo


class AnomalySeverity(str, enum.Enum):
    """Severidade da anomalia."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyStatus(str, enum.Enum):
    """Status da anomalia."""

    DETECTED = "DETECTED"  # Detectada
    INVESTIGATING = "INVESTIGATING"  # Em investigacao
    CONFIRMED = "CONFIRMED"  # Confirmada
    FALSE_POSITIVE = "FALSE_POSITIVE"  # Falso positivo
    RESOLVED = "RESOLVED"  # Resolvida
    IGNORED = "IGNORED"  # Ignorada


class AnomalyLog(Base):
    """Log de anomalia detectada."""

    __tablename__ = "ai_anomaly_logs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tipo e Status
    anomaly_type = Column(
        Enum(AnomalyType, name="anomalytype", create_type=True),
        nullable=False,
        index=True,
    )
    severity = Column(
        Enum(AnomalySeverity, name="anomalyseverity", create_type=True),
        nullable=False,
        default=AnomalySeverity.MEDIUM,
        index=True,
    )
    status = Column(
        Enum(AnomalyStatus, name="anomalystatus", create_type=True),
        nullable=False,
        default=AnomalyStatus.DETECTED,
        index=True,
    )

    # Entidade afetada
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    entity_field = Column(String(100), nullable=True)
    # Ex: "revenue", "transaction_count", "login_attempts"

    # Deteccao
    detector_name = Column(String(100), nullable=True)
    # Ex: "IsolationForest", "LOF", "ARIMA", "Prophet"
    model_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Valores
    observed_value = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    expected_range_min = Column(Float, nullable=True)
    expected_range_max = Column(Float, nullable=True)

    # Scores
    anomaly_score = Column(Float, nullable=True)  # 0-1
    confidence_score = Column(Float, nullable=True)  # 0-1
    deviation_score = Column(Float, nullable=True)  # Quantos desvios padrao

    # Contexto temporal
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    data_timestamp = Column(DateTime(timezone=True), nullable=True)
    # Quando o dado anomalo ocorreu
    window_start = Column(DateTime(timezone=True), nullable=True)
    window_end = Column(DateTime(timezone=True), nullable=True)

    # Descricao
    title = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    # Dados adicionais
    context_data = Column(JSONB, nullable=True)
    # Ex: {"previous_values": [100, 102, 98], "related_metrics": {...}}
    contributing_factors = Column(JSONB, nullable=True)
    # Ex: {"factor1": 0.4, "factor2": 0.3, "factor3": 0.2}

    # Impacto
    impact_score = Column(Float, nullable=True)  # 0-100
    affected_entities_count = Column(Integer, nullable=True)
    estimated_impact_value = Column(Float, nullable=True)
    # Ex: valor monetario do impacto

    # Acoes
    recommended_actions = Column(JSONB, nullable=True)
    # Ex: [{"action": "investigate", "priority": "high"}, ...]
    actions_taken = Column(JSONB, nullable=True)
    # Ex: [{"action": "notified_admin", "at": "2024-01-01T00:00:00"}]

    # Resolucao
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    root_cause = Column(Text, nullable=True)

    # Alertas
    alert_sent = Column(Boolean, default=False, nullable=False)
    alert_channels = Column(ARRAY(String), nullable=True)
    # Ex: ["email", "slack", "sms"]
    alert_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_count = Column(Integer, default=0, nullable=False)

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<AnomalyLog {self.anomaly_type.value} on {self.entity_type}>"

    @property
    def is_resolved(self) -> bool:
        """Verifica se esta resolvida."""
        return self.status in [
            AnomalyStatus.RESOLVED,
            AnomalyStatus.FALSE_POSITIVE,
            AnomalyStatus.IGNORED,
        ]

    @property
    def is_critical(self) -> bool:
        """Verifica se e critica."""
        return self.severity == AnomalySeverity.CRITICAL

    @property
    def deviation_percent(self) -> Optional[float]:
        """Calcula desvio percentual."""
        if self.observed_value is None or self.expected_value is None:
            return None
        if self.expected_value == 0:
            return None
        return abs((self.observed_value - self.expected_value) / self.expected_value) * 100

    def investigate(self) -> None:
        """Marca como em investigacao."""
        self.status = AnomalyStatus.INVESTIGATING

    def confirm(self, root_cause: Optional[str] = None) -> None:
        """Confirma a anomalia.

        Args:
            root_cause: Causa raiz identificada.
        """
        self.status = AnomalyStatus.CONFIRMED
        if root_cause:
            self.root_cause = root_cause

    def mark_false_positive(self, resolution: Optional[str] = None) -> None:
        """Marca como falso positivo.

        Args:
            resolution: Explicacao.
        """
        self.status = AnomalyStatus.FALSE_POSITIVE
        self.resolved_at = datetime.utcnow()
        if resolution:
            self.resolution = resolution

    def resolve(
        self,
        resolution: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Resolve a anomalia.

        Args:
            resolution: Descricao da resolucao.
            user_id: ID do usuario que resolveu.
        """
        self.status = AnomalyStatus.RESOLVED
        self.resolution = resolution
        self.resolved_at = datetime.utcnow()
        if user_id:
            self.resolved_by = user_id

    def ignore(self, reason: Optional[str] = None) -> None:
        """Ignora a anomalia.

        Args:
            reason: Motivo para ignorar.
        """
        self.status = AnomalyStatus.IGNORED
        self.resolved_at = datetime.utcnow()
        if reason:
            self.resolution = f"Ignored: {reason}"

    def record_alert(self, channels: list) -> None:
        """Registra envio de alerta.

        Args:
            channels: Canais de alerta utilizados.
        """
        self.alert_sent = True
        self.alert_channels = channels
        self.alert_sent_at = datetime.utcnow()

    def increment_recurrence(self) -> None:
        """Incrementa contador de recorrencia."""
        self.is_recurring = True
        self.recurrence_count = (self.recurrence_count or 0) + 1
