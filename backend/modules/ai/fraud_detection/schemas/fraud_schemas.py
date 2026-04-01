"""
Fraud Detection Schemas - Sprint 45

Schemas Pydantic para API de deteccao de fraudes.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from modules.ai.fraud_detection.models.fraud_alert import (
    AlertSeverity,
    AlertStatus,
    FraudCategory,
)
from modules.ai.fraud_detection.models.fraud_pattern import (
    PatternStatus,
    PatternType,
)
from modules.ai.fraud_detection.models.fraud_rule import (
    RuleAction,
    RuleOperator,
    RuleType,
)
from modules.ai.fraud_detection.models.risk_profile import (
    EntityType,
    RiskLevel,
)

# =============================================================================
# Alert Schemas
# =============================================================================


class FraudAlertCreate(BaseModel):
    """Schema para criar alerta de fraude."""

    category: FraudCategory
    subcategory: str | None = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = Field(..., min_length=5, max_length=300)
    description: str | None = None

    entity_type: str = Field(..., min_length=1)
    entity_id: UUID
    entity_name: str | None = None

    transaction_id: UUID | None = None
    transaction_type: str | None = None
    transaction_value: float | None = None

    rule_id: UUID | None = None
    pattern_id: UUID | None = None

    risk_score: float = Field(default=0, ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=100)

    evidence: list[dict[str, Any]] = []
    indicators: list[str] = []

    ip_address: str | None = None
    device_id: str | None = None
    location: str | None = None

    potential_loss: float | None = None
    requires_immediate_action: bool = False


class FraudAlertUpdate(BaseModel):
    """Schema para atualizar alerta."""

    severity: AlertSeverity | None = None
    status: AlertStatus | None = None
    description: str | None = None
    investigation_notes: str | None = None
    tags: list[str] | None = None


class FraudAlertResponse(BaseModel):
    """Schema de resposta de alerta."""

    id: UUID
    alert_number: str
    category: FraudCategory
    subcategory: str | None = None
    severity: AlertSeverity
    status: AlertStatus

    title: str
    description: str | None = None
    summary: str | None = None

    entity_type: str
    entity_id: UUID
    entity_name: str | None = None

    transaction_id: UUID | None = None
    transaction_value: float | None = None

    rule_id: UUID | None = None
    rule_name: str | None = None
    pattern_id: UUID | None = None
    pattern_name: str | None = None

    risk_score: float
    confidence_score: float | None = None

    evidence: list[dict[str, Any]] = []
    indicators: list[str] = []

    ip_address: str | None = None
    location: str | None = None

    potential_loss: float | None = None
    actual_loss: float | None = None

    assigned_to: UUID | None = None
    assigned_at: datetime | None = None

    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    resolution_type: str | None = None

    created_at: datetime
    detected_at: datetime | None = None

    is_active: bool
    requires_immediate_action: bool
    days_open: int | None = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema para lista de alertas."""

    items: list[FraudAlertResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AlertAssignRequest(BaseModel):
    """Schema para atribuir alerta."""

    assigned_to: UUID


class AlertResolveRequest(BaseModel):
    """Schema para resolver alerta."""

    resolution_type: str = Field(..., min_length=1)
    resolution_notes: str | None = None
    actions_taken: list[dict[str, Any]] = []
    actual_loss: float | None = None
    recovered_amount: float | None = None


class AlertEscalateRequest(BaseModel):
    """Schema para escalar alerta."""

    escalate_to: UUID
    reason: str = Field(..., min_length=10)


class AlertFeedbackRequest(BaseModel):
    """Schema para feedback de alerta."""

    is_correct: bool
    notes: str | None = None


# =============================================================================
# Rule Schemas
# =============================================================================


class RuleCondition(BaseModel):
    """Schema para condicao de regra."""

    field: str
    operator: RuleOperator
    value: Any
    logic: str = "AND"
    weight: float = 1.0


class FraudRuleCreate(BaseModel):
    """Schema para criar regra."""

    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=3, max_length=200)
    description: str | None = None

    rule_type: RuleType
    category: str
    subcategory: str | None = None

    default_severity: str = "medium"
    risk_weight: float = Field(default=1.0, ge=0.1, le=10.0)

    conditions: list[RuleCondition] = []

    threshold_value: float | None = None
    threshold_count: int | None = None
    threshold_period_minutes: int | None = None

    velocity_count: int | None = None
    velocity_period_minutes: int | None = None
    velocity_field: str | None = None

    primary_action: RuleAction = RuleAction.ALERT
    secondary_actions: list[str] = []

    notify_channels: list[str] = []

    applies_to_entities: list[str] = []
    applies_to_transactions: list[str] = []

    is_active: bool = True
    is_test_mode: bool = False


class FraudRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: str | None = None
    description: str | None = None
    default_severity: str | None = None
    risk_weight: float | None = None
    conditions: list[RuleCondition] | None = None
    primary_action: RuleAction | None = None
    is_active: bool | None = None


class FraudRuleResponse(BaseModel):
    """Schema de resposta de regra."""

    id: UUID
    code: str
    name: str
    description: str | None = None

    rule_type: RuleType
    category: str
    subcategory: str | None = None

    default_severity: str
    risk_weight: float

    conditions: list[dict[str, Any]]

    primary_action: RuleAction
    secondary_actions: list[str]

    total_triggers: int
    true_positives: int
    false_positives: int
    precision_rate: float | None = None
    last_triggered_at: datetime | None = None

    is_active: bool
    is_system: bool
    is_test_mode: bool

    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class RuleTestRequest(BaseModel):
    """Schema para testar regra."""

    rule_id: UUID
    test_data: dict[str, Any]


class RuleTestResponse(BaseModel):
    """Schema de resposta de teste de regra."""

    matched: bool
    score: float
    reasons: list[str]
    conditions_evaluated: int
    conditions_matched: int


# =============================================================================
# Pattern Schemas
# =============================================================================


class FraudPatternCreate(BaseModel):
    """Schema para criar padrao."""

    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=3, max_length=200)
    description: str | None = None

    pattern_type: PatternType
    category: str
    subcategory: str | None = None

    severity: str = "medium"
    risk_score: float = Field(default=50.0, ge=0, le=100)

    pattern_definition: dict[str, Any] = {}
    features: list[dict[str, Any]] = []
    indicators: list[str] = []

    detection_threshold: float = Field(default=0.7, ge=0, le=1)
    confidence_threshold: float = Field(default=0.8, ge=0, le=1)

    prevention_tips: list[str] = []
    recommended_actions: list[str] = []

    is_active: bool = True
    is_ml_based: bool = False


class FraudPatternUpdate(BaseModel):
    """Schema para atualizar padrao."""

    name: str | None = None
    description: str | None = None
    severity: str | None = None
    risk_score: float | None = None
    pattern_definition: dict[str, Any] | None = None
    indicators: list[str] | None = None
    detection_threshold: float | None = None
    status: PatternStatus | None = None
    is_active: bool | None = None


class FraudPatternResponse(BaseModel):
    """Schema de resposta de padrao."""

    id: UUID
    code: str
    name: str
    description: str | None = None

    pattern_type: PatternType
    category: str
    status: PatternStatus

    severity: str
    risk_score: float

    pattern_definition: dict[str, Any]
    features: list[dict[str, Any]]
    indicators: list[str]

    detection_threshold: float
    confidence_threshold: float

    total_detections: int
    confirmed_cases: int
    false_positives: int
    detection_rate: float | None = None
    last_detected_at: datetime | None = None

    is_active: bool
    is_ml_based: bool

    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PatternMatchRequest(BaseModel):
    """Schema para verificar padrao."""

    pattern_id: UUID | None = None
    data: dict[str, Any]
    indicators: list[str] = []


class PatternMatchResponse(BaseModel):
    """Schema de resposta de match de padrao."""

    matched: bool
    pattern_id: UUID | None = None
    pattern_name: str | None = None
    confidence: float
    indicators_found: list[str]
    risk_score: float


# =============================================================================
# Risk Profile Schemas
# =============================================================================


class RiskProfileCreate(BaseModel):
    """Schema para criar perfil de risco."""

    entity_type: EntityType
    entity_id: UUID
    entity_identifier: str | None = None
    entity_name: str | None = None

    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = Field(default=0, ge=0, le=100)

    behavior_score: float = Field(default=0, ge=0, le=100)
    transaction_score: float = Field(default=0, ge=0, le=100)

    risk_factors: list[dict[str, Any]] = []
    trust_indicators: list[dict[str, Any]] = []

    transaction_limit_daily: float | None = None
    transaction_limit_monthly: float | None = None


class RiskProfileUpdate(BaseModel):
    """Schema para atualizar perfil."""

    risk_level: RiskLevel | None = None
    risk_factors: list[dict[str, Any]] | None = None
    trust_indicators: list[dict[str, Any]] | None = None
    transaction_limit_daily: float | None = None
    transaction_limit_monthly: float | None = None
    is_blocked: bool | None = None
    is_whitelisted: bool | None = None
    is_watchlisted: bool | None = None
    notes: str | None = None


class RiskProfileResponse(BaseModel):
    """Schema de resposta de perfil."""

    id: UUID
    entity_type: EntityType
    entity_id: UUID
    entity_identifier: str | None = None
    entity_name: str | None = None

    risk_level: RiskLevel
    risk_score: float
    risk_score_change: float

    behavior_score: float
    transaction_score: float
    velocity_score: float
    identity_score: float

    risk_factors: list[dict[str, Any]]
    trust_indicators: list[dict[str, Any]]

    total_alerts: int
    confirmed_frauds: int
    false_positives: int
    fraud_rate: float | None = None

    total_transactions: int
    total_transaction_value: float
    avg_transaction_value: float

    is_blocked: bool
    is_whitelisted: bool
    is_watchlisted: bool

    verification_level: int
    identity_verified: bool

    created_at: datetime
    last_calculated_at: datetime | None = None

    class Config:
        from_attributes = True


class RiskScoreRequest(BaseModel):
    """Schema para calcular score de risco."""

    entity_type: EntityType
    entity_id: UUID
    recalculate: bool = True
    include_ml: bool = True


class RiskScoreResponse(BaseModel):
    """Schema de resposta de score."""

    entity_type: EntityType
    entity_id: UUID
    risk_level: RiskLevel
    risk_score: float
    previous_score: float | None = None
    score_change: float
    risk_factors: list[dict[str, Any]]
    recommendations: list[str]


# =============================================================================
# Detection Schemas
# =============================================================================


class DetectionRequest(BaseModel):
    """Schema generico para deteccao."""

    entity_type: str
    entity_id: UUID
    event_type: str
    event_data: dict[str, Any]
    context: dict[str, Any] = {}
    real_time: bool = True


class DetectionResponse(BaseModel):
    """Schema de resposta de deteccao."""

    is_fraudulent: bool
    risk_score: float
    risk_level: RiskLevel
    alerts_generated: int
    alert_ids: list[UUID]
    matched_rules: list[str]
    matched_patterns: list[str]
    recommendations: list[str]
    processing_time_ms: int


class TransactionCheckRequest(BaseModel):
    """Schema para verificar transacao."""

    transaction_id: UUID
    transaction_type: str
    amount: float
    currency: str = "BRL"

    payer_id: UUID
    payer_type: str
    payer_account: str | None = None

    payee_id: UUID | None = None
    payee_type: str | None = None
    payee_account: str | None = None

    ip_address: str | None = None
    device_id: str | None = None
    location: str | None = None
    user_agent: str | None = None

    metadata: dict[str, Any] = {}


class TransactionCheckResponse(BaseModel):
    """Schema de resposta de verificacao de transacao."""

    transaction_id: UUID
    is_allowed: bool
    risk_score: float
    risk_level: RiskLevel

    decision: str  # approve, review, block, challenge
    decision_reasons: list[str]

    matched_rules: list[str]
    matched_patterns: list[str]

    alerts_generated: list[UUID]

    recommendations: list[str]
    required_actions: list[str]

    processing_time_ms: int


class AccessCheckRequest(BaseModel):
    """Schema para verificar acesso."""

    user_id: UUID
    session_id: str | None = None

    ip_address: str
    device_id: str | None = None
    user_agent: str | None = None

    location: str | None = None
    geo_coordinates: dict[str, float] | None = None

    action: str  # login, password_reset, data_export, etc
    resource: str | None = None

    metadata: dict[str, Any] = {}


class AccessCheckResponse(BaseModel):
    """Schema de resposta de verificacao de acesso."""

    user_id: UUID
    is_allowed: bool
    risk_score: float
    risk_level: RiskLevel

    decision: str  # allow, challenge, block
    challenge_type: str | None = None  # mfa, captcha, email

    anomalies_detected: list[str]
    risk_factors: list[str]

    is_new_device: bool
    is_new_location: bool
    is_unusual_time: bool

    alerts_generated: list[UUID]

    processing_time_ms: int


# =============================================================================
# Dashboard Schemas
# =============================================================================


class AlertsSummary(BaseModel):
    """Resumo de alertas."""

    total_pending: int
    total_investigating: int
    total_confirmed: int
    total_resolved: int
    total_false_positives: int

    by_severity: dict[str, int]
    by_category: dict[str, int]

    avg_resolution_time_hours: float
    escalated_count: int
    overdue_count: int


class RiskDistribution(BaseModel):
    """Distribuicao de risco."""

    minimal: int
    low: int
    medium: int
    high: int
    critical: int
    blocked: int


class FraudDashboardStats(BaseModel):
    """Estatisticas do dashboard."""

    # Alertas
    alerts_summary: AlertsSummary

    # Deteccoes
    total_detections_today: int
    total_detections_week: int
    total_detections_month: int

    # Perdas
    total_loss_prevented: float
    actual_losses: float
    recovery_rate: float

    # Efetividade
    detection_rate: float
    false_positive_rate: float
    avg_detection_time_seconds: float

    # Regras
    active_rules: int
    rules_triggered_today: int
    most_triggered_rules: list[dict[str, Any]]

    # Padroes
    active_patterns: int
    patterns_detected_today: int

    # Perfis
    high_risk_profiles: int
    blocked_entities: int
    watchlisted_entities: int

    # Distribuicao
    risk_distribution: RiskDistribution

    # Tendencias
    alerts_trend: list[dict[str, Any]]
    fraud_trend: list[dict[str, Any]]
