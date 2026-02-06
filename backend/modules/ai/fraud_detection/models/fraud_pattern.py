"""
Fraud Pattern Model - AI Fraud Detection

Modelo para padroes de fraude conhecidos e detectados.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from core.database import Base


class PatternType(str, enum.Enum):
    """Tipo de padrao de fraude."""

    # Financeiros
    SPLIT_TRANSACTION = "split_transaction"
    ROUND_TRIP = "round_trip"
    LAYERING = "layering"
    SMURFING = "smurfing"
    STRUCTURING = "structuring"

    # Acesso
    CREDENTIAL_STUFFING = "credential_stuffing"
    BRUTE_FORCE = "brute_force"
    ACCOUNT_TAKEOVER = "account_takeover"
    SESSION_HIJACKING = "session_hijacking"
    PRIVILEGE_ESCALATION = "privilege_escalation"

    # Identidade
    SYNTHETIC_IDENTITY = "synthetic_identity"
    IDENTITY_THEFT = "identity_theft"
    GHOST_EMPLOYEE = "ghost_employee"
    FICTITIOUS_VENDOR = "fictitious_vendor"

    # Documental
    DOCUMENT_FORGERY = "document_forgery"
    DUPLICATE_INVOICE = "duplicate_invoice"
    FAKE_RECEIPT = "fake_receipt"

    # Operacional
    INVENTORY_THEFT = "inventory_theft"
    TIME_THEFT = "time_theft"
    EXPENSE_FRAUD = "expense_fraud"
    KICKBACK = "kickback"
    BID_RIGGING = "bid_rigging"

    # Comportamental
    UNUSUAL_TIMING = "unusual_timing"
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_DEVICE = "unusual_device"
    VELOCITY_ABUSE = "velocity_abuse"
    BURST_ACTIVITY = "burst_activity"

    # Outros
    ANOMALY = "anomaly"
    COLLUSION = "collusion"
    CUSTOM = "custom"


class PatternStatus(str, enum.Enum):
    """Status do padrao."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LEARNING = "learning"
    TESTING = "testing"
    DEPRECATED = "deprecated"


class FraudPattern(Base):
    """
    Modelo de padrao de fraude.

    Armazena padroes de fraude conhecidos e detectados
    pelo sistema de ML para identificacao futura.
    """

    __tablename__ = "fraud_patterns"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Tipo e categoria
    pattern_type = Column(
        Enum(PatternType),
        default=PatternType.ANOMALY,
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(50))

    # Status
    status = Column(
        Enum(PatternStatus),
        default=PatternStatus.LEARNING,
        nullable=False,
        index=True,
    )

    # Severidade
    severity = Column(String(20), default="medium")
    risk_score = Column(Float, default=50.0)

    # Definicao do padrao
    pattern_definition = Column(JSONB, default={}, nullable=False)
    """
    Formato:
    {
        "type": "sequence",
        "steps": [
            {"action": "login", "max_failures": 5, "window_minutes": 10},
            {"action": "password_reset", "within_minutes": 30},
            {"action": "large_withdrawal", "min_value": 10000}
        ],
        "conditions": {
            "same_ip": true,
            "different_device": true
        }
    }
    """

    # Caracteristicas (features)
    features = Column(JSONB, default=[])
    """
    Features usadas para detectar o padrao:
    [
        {"name": "transaction_value", "weight": 0.3},
        {"name": "transaction_frequency", "weight": 0.2},
        {"name": "time_of_day", "weight": 0.1}
    ]
    """

    # Thresholds
    detection_threshold = Column(Float, default=0.7)
    confidence_threshold = Column(Float, default=0.8)
    min_occurrences = Column(Integer, default=3)
    max_time_window_minutes = Column(Integer, default=60)

    # ML/Modelo
    ml_model_type = Column(String(50))
    ml_model_path = Column(String(500))
    ml_model_version = Column(String(50))
    ml_last_trained = Column(DateTime)
    ml_training_samples = Column(Integer, default=0)
    ml_accuracy = Column(Float)
    ml_precision = Column(Float)
    ml_recall = Column(Float)
    ml_f1_score = Column(Float)

    # Indicadores
    indicators = Column(JSONB, default=[])
    """
    Indicadores que caracterizam o padrao:
    [
        "multiple_failed_logins",
        "ip_address_change",
        "unusual_transaction_time"
    ]
    """

    # Exemplos
    example_cases = Column(JSONB, default=[])
    typical_victims = Column(JSONB, default=[])
    common_methods = Column(JSONB, default=[])

    # Mitigacao
    prevention_tips = Column(JSONB, default=[])
    recommended_actions = Column(JSONB, default=[])
    detection_rules = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Estatisticas
    total_detections = Column(Integer, default=0)
    confirmed_cases = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    total_loss_prevented = Column(Float, default=0)
    avg_detection_time_seconds = Column(Float)
    last_detected_at = Column(DateTime)

    # Origem
    source = Column(String(50), default="system")
    external_reference = Column(String(200))
    industry_code = Column(String(50))

    # Relacionamentos
    related_patterns = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Metadados
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))

    # Flags
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system = Column(Boolean, default=False)
    is_ml_based = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)

    # Notas
    notes = Column(Text)
    tags = Column(ARRAY(String), default=[])

    # Relationships
    alerts = relationship("FraudAlert", back_populates="pattern")

    def __repr__(self) -> str:
        return f"<FraudPattern {self.code} [{self.pattern_type.value}]>"

    @property
    def detection_rate(self) -> float:
        """Taxa de deteccao."""
        if self.total_detections == 0:
            return 0.0
        return (self.confirmed_cases / self.total_detections) * 100

    @property
    def false_positive_rate(self) -> float:
        """Taxa de falsos positivos."""
        if self.total_detections == 0:
            return 0.0
        return (self.false_positives / self.total_detections) * 100

    @property
    def is_effective(self) -> bool:
        """Verifica se padrao e efetivo."""
        return (
            self.total_detections >= 10
            and self.detection_rate >= 70.0
            and self.false_positive_rate <= 30.0
        )

    def record_detection(
        self,
        confirmed: bool,
        loss_prevented: float = 0,
        detection_time_seconds: float = 0,
    ) -> None:
        """Registra uma deteccao."""
        self.total_detections += 1
        self.last_detected_at = datetime.utcnow()

        if confirmed:
            self.confirmed_cases += 1
            self.total_loss_prevented += loss_prevented
        else:
            self.false_positives += 1

        # Atualizar media de tempo
        if detection_time_seconds > 0:
            if self.avg_detection_time_seconds:
                self.avg_detection_time_seconds = (
                    self.avg_detection_time_seconds + detection_time_seconds
                ) / 2
            else:
                self.avg_detection_time_seconds = detection_time_seconds

    def match(self, data: Dict[str, Any]) -> tuple[bool, float, List[str]]:
        """
        Verifica se dados correspondem ao padrao.

        Args:
            data: Dados a verificar

        Returns:
            Tuple (matched, confidence, indicators_found)
        """
        if not self.is_active or self.status != PatternStatus.ACTIVE:
            return False, 0.0, []

        indicators_found = []
        total_weight = 0.0
        matched_weight = 0.0

        # Verificar indicadores
        for indicator in self.indicators:
            indicator_name = indicator if isinstance(indicator, str) else indicator.get("name")
            indicator_weight = 1.0 if isinstance(indicator, str) else indicator.get("weight", 1.0)

            total_weight += indicator_weight

            if indicator_name in data.get("indicators", []):
                indicators_found.append(indicator_name)
                matched_weight += indicator_weight

        # Calcular confianca
        confidence = matched_weight / total_weight if total_weight > 0 else 0.0

        # Verificar threshold
        matched = confidence >= self.detection_threshold

        return matched, confidence, indicators_found
