"""
Fraud Rule Model - AI Fraud Detection

Modelo para regras de deteccao de fraude configuraveis.
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


class RuleType(str, enum.Enum):
    """Tipo de regra."""

    THRESHOLD = "threshold"
    VELOCITY = "velocity"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"
    COMBINATION = "combination"
    BEHAVIORAL = "behavioral"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    DEVICE = "device"
    NETWORK = "network"
    CUSTOM = "custom"


class RuleOperator(str, enum.Enum):
    """Operador de comparacao."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class RuleAction(str, enum.Enum):
    """Acao da regra quando acionada."""

    ALERT = "alert"
    BLOCK = "block"
    FLAG = "flag"
    REVIEW = "review"
    NOTIFY = "notify"
    ESCALATE = "escalate"
    LOG = "log"
    CHALLENGE = "challenge"
    LIMIT = "limit"
    DELAY = "delay"


class FraudRule(Base):
    """
    Modelo de regra de deteccao de fraude.

    Define regras configuraveis para deteccao automatica
    de fraudes e comportamentos suspeitos.
    """

    __tablename__ = "fraud_rules"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Tipo e categoria
    rule_type = Column(
        Enum(RuleType),
        default=RuleType.THRESHOLD,
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(50))

    # Severidade padrao
    default_severity = Column(String(20), default="medium")
    risk_weight = Column(Float, default=1.0)

    # Condicoes
    conditions = Column(JSONB, default=[], nullable=False)
    """
    Formato das condicoes:
    [
        {
            "field": "transaction_value",
            "operator": "greater_than",
            "value": 10000,
            "type": "number"
        },
        {
            "logic": "AND",
            "field": "transaction_count_1h",
            "operator": "greater_than",
            "value": 5
        }
    ]
    """

    # Thresholds
    threshold_value = Column(Float)
    threshold_count = Column(Integer)
    threshold_period_minutes = Column(Integer)

    # Velocity (frequencia)
    velocity_count = Column(Integer)
    velocity_period_minutes = Column(Integer)
    velocity_field = Column(String(100))

    # Acoes
    primary_action = Column(
        Enum(RuleAction),
        default=RuleAction.ALERT,
        nullable=False,
    )
    secondary_actions = Column(ARRAY(String), default=[])

    # Notificacoes
    notify_channels = Column(ARRAY(String), default=[])
    notify_recipients = Column(JSONB, default=[])
    notification_template = Column(String(100))

    # Escopo
    applies_to_entities = Column(ARRAY(String), default=[])
    applies_to_transactions = Column(ARRAY(String), default=[])
    excluded_entities = Column(JSONB, default=[])
    excluded_ips = Column(ARRAY(String), default=[])

    # Horarios
    active_days = Column(ARRAY(Integer), default=[0, 1, 2, 3, 4, 5, 6])
    active_hours_start = Column(Integer)
    active_hours_end = Column(Integer)
    timezone = Column(String(50), default="America/Sao_Paulo")

    # Limites
    max_alerts_per_entity = Column(Integer)
    max_alerts_per_day = Column(Integer)
    cooldown_minutes = Column(Integer)

    # ML/Score
    use_ml_scoring = Column(Boolean, default=False)
    ml_model_id = Column(String(100))
    ml_threshold = Column(Float)
    min_confidence = Column(Float, default=0.7)

    # Metricas
    total_triggers = Column(Integer, default=0)
    true_positives = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    precision_rate = Column(Float)
    last_triggered_at = Column(DateTime)

    # Versao
    version = Column(Integer, default=1)
    previous_version_id = Column(UUID(as_uuid=True))

    # Metadados
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True))

    # Flags
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    is_test_mode = Column(Boolean, default=False)

    # Notas
    notes = Column(Text)
    tags = Column(ARRAY(String), default=[])

    # Relationships
    alerts = relationship("FraudAlert", back_populates="rule")

    def __repr__(self) -> str:
        return f"<FraudRule {self.code} [{self.rule_type.value}]>"

    @property
    def effectiveness(self) -> float:
        """Calcula taxa de efetividade."""
        total = self.true_positives + self.false_positives
        if total == 0:
            return 0.0
        return (self.true_positives / total) * 100

    @property
    def is_effective(self) -> bool:
        """Verifica se regra e efetiva (>70% precision)."""
        return self.effectiveness >= 70.0

    def increment_trigger(self, is_true_positive: Optional[bool] = None) -> None:
        """Incrementa contador de triggers."""
        self.total_triggers += 1
        self.last_triggered_at = datetime.utcnow()
        if is_true_positive is True:
            self.true_positives += 1
        elif is_true_positive is False:
            self.false_positives += 1
        self._update_precision()

    def _update_precision(self) -> None:
        """Atualiza taxa de precisao."""
        total = self.true_positives + self.false_positives
        if total > 0:
            self.precision_rate = self.true_positives / total

    def evaluate(self, data: Dict[str, Any]) -> tuple[bool, float, List[str]]:
        """
        Avalia dados contra a regra.

        Args:
            data: Dados a serem avaliados

        Returns:
            Tuple (matched, score, reasons)
        """
        if not self.is_active:
            return False, 0.0, []

        matched = True
        reasons = []
        score = 0.0

        for condition in self.conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            expected = condition.get("value")
            logic = condition.get("logic", "AND")

            actual = data.get(field)
            condition_met = self._evaluate_condition(actual, operator, expected)

            if logic == "AND":
                matched = matched and condition_met
            else:  # OR
                matched = matched or condition_met

            if condition_met:
                reasons.append(f"{field} {operator} {expected}")
                score += condition.get("weight", 1.0)

        # Aplicar peso de risco
        score *= self.risk_weight

        return matched, min(score, 100.0), reasons

    def _evaluate_condition(
        self,
        actual: Any,
        operator: str,
        expected: Any,
    ) -> bool:
        """Avalia uma condicao individual."""
        if actual is None and operator != RuleOperator.IS_NULL.value:
            return False

        if operator == RuleOperator.EQUALS.value:
            return actual == expected
        elif operator == RuleOperator.NOT_EQUALS.value:
            return actual != expected
        elif operator == RuleOperator.GREATER_THAN.value:
            return actual > expected
        elif operator == RuleOperator.LESS_THAN.value:
            return actual < expected
        elif operator == RuleOperator.GREATER_OR_EQUAL.value:
            return actual >= expected
        elif operator == RuleOperator.LESS_OR_EQUAL.value:
            return actual <= expected
        elif operator == RuleOperator.BETWEEN.value:
            return expected[0] <= actual <= expected[1]
        elif operator == RuleOperator.IN.value:
            return actual in expected
        elif operator == RuleOperator.NOT_IN.value:
            return actual not in expected
        elif operator == RuleOperator.CONTAINS.value:
            return expected in str(actual)
        elif operator == RuleOperator.IS_NULL.value:
            return actual is None
        elif operator == RuleOperator.IS_NOT_NULL.value:
            return actual is not None

        return False
