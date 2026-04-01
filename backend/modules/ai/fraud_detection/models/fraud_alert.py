"""
Fraud Alert Model - AI Fraud Detection

Modelo para alertas de fraude detectados.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class FraudCategory(StrEnum):
    """Categoria de fraude."""

    FINANCIAL = "financial"
    ACCESS = "access"
    IDENTITY = "identity"
    DOCUMENT = "document"
    OPERATIONAL = "operational"
    TRANSACTION = "transaction"
    ACCOUNT = "account"
    PAYMENT = "payment"
    INVENTORY = "inventory"
    PAYROLL = "payroll"
    VENDOR = "vendor"
    BILLING = "billing"
    OTHER = "other"


class AlertSeverity(StrEnum):
    """Severidade do alerta."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    """Status do alerta."""

    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    DISMISSED = "dismissed"


class FraudAlert(Base):
    """
    Modelo de alerta de fraude.

    Armazena alertas de fraudes detectadas pelo sistema,
    incluindo detalhes, evidencias e status de investigacao.
    """

    __tablename__ = "fraud_alerts"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_number = Column(String(50), unique=True, nullable=False)

    # Classificacao
    category = Column(
        Enum(FraudCategory),
        default=FraudCategory.OTHER,
        nullable=False,
        index=True,
    )
    subcategory = Column(String(100))
    severity = Column(
        Enum(AlertSeverity),
        default=AlertSeverity.MEDIUM,
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(AlertStatus),
        default=AlertStatus.NEW,
        nullable=False,
        index=True,
    )

    # Descricao
    title = Column(String(300), nullable=False)
    description = Column(Text)
    summary = Column(Text)

    # Entidade afetada
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entity_name = Column(String(300))
    entity_document = Column(String(20))

    # Transacao/Evento relacionado
    transaction_id = Column(UUID(as_uuid=True), index=True)
    transaction_type = Column(String(50))
    transaction_value = Column(Float)
    transaction_date = Column(DateTime)

    # Regra que disparou
    rule_id = Column(UUID(as_uuid=True), ForeignKey("fraud_rules.id"), index=True)
    rule_name = Column(String(200))
    pattern_id = Column(UUID(as_uuid=True), ForeignKey("fraud_patterns.id"))
    pattern_name = Column(String(200))

    # Score e confianca
    risk_score = Column(Float, default=0, nullable=False)
    confidence_score = Column(Float, default=0)
    anomaly_score = Column(Float, default=0)

    # Evidencias
    evidence = Column(JSONB, default=[])
    indicators = Column(JSONB, default=[])
    related_entities = Column(JSONB, default=[])
    related_alerts = Column(JSONB, default=[])

    # Contexto
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_id = Column(String(100))
    location = Column(String(200))
    geo_coordinates = Column(JSONB)
    session_id = Column(String(100))

    # Deteccao
    detection_method = Column(String(50))
    detection_model = Column(String(100))
    model_version = Column(String(50))
    processing_time_ms = Column(Integer)

    # Impacto
    potential_loss = Column(Float)
    actual_loss = Column(Float)
    recovered_amount = Column(Float)
    affected_accounts = Column(Integer, default=0)

    # Investigacao
    assigned_to = Column(UUID(as_uuid=True))
    assigned_at = Column(DateTime)
    investigation_notes = Column(Text)
    investigation_findings = Column(JSONB, default=[])

    # Resolucao
    resolved_by = Column(UUID(as_uuid=True))
    resolved_at = Column(DateTime)
    resolution_type = Column(String(50))
    resolution_notes = Column(Text)
    resolution_actions = Column(JSONB, default=[])

    # Escalacao
    escalated_to = Column(UUID(as_uuid=True))
    escalated_at = Column(DateTime)
    escalation_level = Column(Integer, default=0)
    escalation_reason = Column(Text)

    # Feedback
    feedback_correct = Column(Boolean)
    feedback_notes = Column(Text)
    feedback_by = Column(UUID(as_uuid=True))
    feedback_at = Column(DateTime)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    detected_at = Column(DateTime, default=datetime.utcnow)

    # Flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False)
    requires_immediate_action = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)

    # Extras
    tags = Column(JSONB, default=[])
    extra_metadata = Column(JSONB, default={})
    notes = Column(Text)

    # Relationships
    rule = relationship("FraudRule", back_populates="alerts")
    pattern = relationship("FraudPattern", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<FraudAlert {self.alert_number} [{self.category.value}] {self.severity.value}>"

    @property
    def is_resolved(self) -> bool:
        """Verifica se alerta esta resolvido."""
        return self.status in (
            AlertStatus.RESOLVED,
            AlertStatus.FALSE_POSITIVE,
            AlertStatus.DISMISSED,
        )

    @property
    def is_critical(self) -> bool:
        """Verifica se alerta e critico."""
        return self.severity == AlertSeverity.CRITICAL

    @property
    def is_high_priority(self) -> bool:
        """Verifica se alerta e de alta prioridade."""
        return self.severity in (AlertSeverity.HIGH, AlertSeverity.CRITICAL)

    @property
    def days_open(self) -> int:
        """Dias desde a criacao."""
        if self.is_resolved:
            return 0
        delta = datetime.utcnow() - self.created_at
        return delta.days

    @property
    def needs_escalation(self) -> bool:
        """Verifica se precisa escalar."""
        if self.is_resolved or self.status == AlertStatus.ESCALATED:
            return False
        # Escalar se critico e aberto por mais de 1 dia
        if self.is_critical and self.days_open >= 1:
            return True
        # Escalar se alto e aberto por mais de 3 dias
        if self.severity == AlertSeverity.HIGH and self.days_open >= 3:
            return True
        return False

    def assign(self, user_id: uuid.UUID) -> None:
        """Atribui alerta a um usuario."""
        self.assigned_to = user_id
        self.assigned_at = datetime.utcnow()
        if self.status == AlertStatus.NEW:
            self.status = AlertStatus.INVESTIGATING
        self.updated_at = datetime.utcnow()

    def confirm(self, user_id: uuid.UUID, notes: str | None = None) -> None:
        """Confirma fraude."""
        self.status = AlertStatus.CONFIRMED
        self.resolved_by = user_id
        self.resolved_at = datetime.utcnow()
        self.resolution_type = "confirmed"
        if notes:
            self.resolution_notes = notes
        self.updated_at = datetime.utcnow()

    def mark_false_positive(self, user_id: uuid.UUID, notes: str | None = None) -> None:
        """Marca como falso positivo."""
        self.status = AlertStatus.FALSE_POSITIVE
        self.feedback_correct = False
        self.feedback_by = user_id
        self.feedback_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolved_at = datetime.utcnow()
        self.resolution_type = "false_positive"
        if notes:
            self.feedback_notes = notes
            self.resolution_notes = notes
        self.updated_at = datetime.utcnow()

    def escalate(
        self,
        escalated_to: uuid.UUID,
        reason: str | None = None,
    ) -> None:
        """Escala alerta."""
        self.status = AlertStatus.ESCALATED
        self.escalated_to = escalated_to
        self.escalated_at = datetime.utcnow()
        self.escalation_level += 1
        if reason:
            self.escalation_reason = reason
        self.updated_at = datetime.utcnow()

    def resolve(
        self,
        user_id: uuid.UUID,
        resolution_type: str,
        notes: str | None = None,
        actions: list[dict] | None = None,
    ) -> None:
        """Resolve alerta."""
        self.status = AlertStatus.RESOLVED
        self.resolved_by = user_id
        self.resolved_at = datetime.utcnow()
        self.resolution_type = resolution_type
        if notes:
            self.resolution_notes = notes
        if actions:
            self.resolution_actions = actions
        self.updated_at = datetime.utcnow()
