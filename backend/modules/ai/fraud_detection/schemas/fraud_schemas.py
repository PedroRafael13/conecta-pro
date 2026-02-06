"""
Fraud Detection Schemas - Sprint 45

Schemas Pydantic para API de deteccao de fraudes.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from modules.ai.fraud_detection.models.fraud_alert import (
    FraudCategory,
    AlertSeverity,
    AlertStatus,
)
from modules.ai.fraud_detection.models.fraud_rule import (
    RuleType,
    RuleOperator,
    RuleAction,
)
from modules.ai.fraud_detection.models.fraud_pattern import (
    PatternType,
    PatternStatus,
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
    subcategory: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = Field(..., min_length=5, max_length=300)
    description: Optional[str] = None

    entity_type: str = Field(..., min_length=1)
    entity_id: UUID
    entity_name: Optional[str] = None

    transaction_id: Optional[UUID] = None
    transaction_type: Optional[str] = None
    transaction_value: Optional[float] = None

    rule_id: Optional[UUID] = None
    pattern_id: Optional[UUID] = None

    risk_score: float = Field(default=0, ge=0, le=100)
    confidence_score: Optional[float] = Field(default=None, ge=0, le=100)

    evidence: List[Dict[str, Any]] = []
    indicators: List[str] = []

    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None

    potential_loss: Optional[float] = None
    requires_immediate_action: bool = False


class FraudAlertUpdate(BaseModel):
    """Schema para atualizar alerta."""

    severity: Optional[AlertSeverity] = None
    status: Optional[AlertStatus] = None
    description: Optional[str] = None
    investigation_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class FraudAlertResponse(BaseModel):
    """Schema de resposta de alerta."""

    id: UUID
    alert_number: str
    category: FraudCategory
    subcategory: Optional[str] = None
    severity: AlertSeverity
    status: AlertStatus

    title: str
    description: Optional[str] = None
    summary: Optional[str] = None

    entity_type: str
    entity_id: UUID
    entity_name: Optional[str] = None

    transaction_id: Optional[UUID] = None
    transaction_value: Optional[float] = None

    rule_id: Optional[UUID] = None
    rule_name: Optional[str] = None
    pattern_id: Optional[UUID] = None
    pattern_name: Optional[str] = None

    risk_score: float
    confidence_score: Optional[float] = None

    evidence: List[Dict[str, Any]] = []
    indicators: List[str] = []

    ip_address: Optional[str] = None
    location: Optional[str] = None

    potential_loss: Optional[float] = None
    actual_loss: Optional[float] = None

    assigned_to: Optional[UUID] = None
    assigned_at: Optional[datetime] = None

    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    resolution_type: Optional[str] = None

    created_at: datetime
    detected_at: Optional[datetime] = None

    is_active: bool
    requires_immediate_action: bool
    days_open: Optional[int] = None

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema para lista de alertas."""

    items: List[FraudAlertResponse]
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
    resolution_notes: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = []
    actual_loss: Optional[float] = None
    recovered_amount: Optional[float] = None


class AlertEscalateRequest(BaseModel):
    """Schema para escalar alerta."""

    escalate_to: UUID
    reason: str = Field(..., min_length=10)


class AlertFeedbackRequest(BaseModel):
    """Schema para feedback de alerta."""

    is_correct: bool
    notes: Optional[str] = None


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
    description: Optional[str] = None

    rule_type: RuleType
    category: str
    subcategory: Optional[str] = None

    default_severity: str = "medium"
    risk_weight: float = Field(default=1.0, ge=0.1, le=10.0)

    conditions: List[RuleCondition] = []

    threshold_value: Optional[float] = None
    threshold_count: Optional[int] = None
    threshold_period_minutes: Optional[int] = None

    velocity_count: Optional[int] = None
    velocity_period_minutes: Optional[int] = None
    velocity_field: Optional[str] = None

    primary_action: RuleAction = RuleAction.ALERT
    secondary_actions: List[str] = []

    notify_channels: List[str] = []

    applies_to_entities: List[str] = []
    applies_to_transactions: List[str] = []

    is_active: bool = True
    is_test_mode: bool = False


class FraudRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: Optional[str] = None
    description: Optional[str] = None
    default_severity: Optional[str] = None
    risk_weight: Optional[float] = None
    conditions: Optional[List[RuleCondition]] = None
    primary_action: Optional[RuleAction] = None
    is_active: Optional[bool] = None


class FraudRuleResponse(BaseModel):
    """Schema de resposta de regra."""

    id: UUID
    code: str
    name: str
    description: Optional[str] = None

    rule_type: RuleType
    category: str
    subcategory: Optional[str] = None

    default_severity: str
    risk_weight: float

    conditions: List[Dict[str, Any]]

    primary_action: RuleAction
    secondary_actions: List[str]

    total_triggers: int
    true_positives: int
    false_positives: int
    precision_rate: Optional[float] = None
    last_triggered_at: Optional[datetime] = None

    is_active: bool
    is_system: bool
    is_test_mode: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RuleTestRequest(BaseModel):
    """Schema para testar regra."""

    rule_id: UUID
    test_data: Dict[str, Any]


class RuleTestResponse(BaseModel):
    """Schema de resposta de teste de regra."""

    matched: bool
    score: float
    reasons: List[str]
    conditions_evaluated: int
    conditions_matched: int


# =============================================================================
# Pattern Schemas
# =============================================================================


class FraudPatternCreate(BaseModel):
    """Schema para criar padrao."""

    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None

    pattern_type: PatternType
    category: str
    subcategory: Optional[str] = None

    severity: str = "medium"
    risk_score: float = Field(default=50.0, ge=0, le=100)

    pattern_definition: Dict[str, Any] = {}
    features: List[Dict[str, Any]] = []
    indicators: List[str] = []

    detection_threshold: float = Field(default=0.7, ge=0, le=1)
    confidence_threshold: float = Field(default=0.8, ge=0, le=1)

    prevention_tips: List[str] = []
    recommended_actions: List[str] = []

    is_active: bool = True
    is_ml_based: bool = False


class FraudPatternUpdate(BaseModel):
    """Schema para atualizar padrao."""

    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    risk_score: Optional[float] = None
    pattern_definition: Optional[Dict[str, Any]] = None
    indicators: Optional[List[str]] = None
    detection_threshold: Optional[float] = None
    status: Optional[PatternStatus] = None
    is_active: Optional[bool] = None


class FraudPatternResponse(BaseModel):
    """Schema de resposta de padrao."""

    id: UUID
    code: str
    name: str
    description: Optional[str] = None

    pattern_type: PatternType
    category: str
    status: PatternStatus

    severity: str
    risk_score: float

    pattern_definition: Dict[str, Any]
    features: List[Dict[str, Any]]
    indicators: List[str]

    detection_threshold: float
    confidence_threshold: float

    total_detections: int
    confirmed_cases: int
    false_positives: int
    detection_rate: Optional[float] = None
    last_detected_at: Optional[datetime] = None

    is_active: bool
    is_ml_based: bool

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatternMatchRequest(BaseModel):
    """Schema para verificar padrao."""

    pattern_id: Optional[UUID] = None
    data: Dict[str, Any]
    indicators: List[str] = []


class PatternMatchResponse(BaseModel):
    """Schema de resposta de match de padrao."""

    matched: bool
    pattern_id: Optional[UUID] = None
    pattern_name: Optional[str] = None
    confidence: float
    indicators_found: List[str]
    risk_score: float


# =============================================================================
# Risk Profile Schemas
# =============================================================================


class RiskProfileCreate(BaseModel):
    """Schema para criar perfil de risco."""

    entity_type: EntityType
    entity_id: UUID
    entity_identifier: Optional[str] = None
    entity_name: Optional[str] = None

    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = Field(default=0, ge=0, le=100)

    behavior_score: float = Field(default=0, ge=0, le=100)
    transaction_score: float = Field(default=0, ge=0, le=100)

    risk_factors: List[Dict[str, Any]] = []
    trust_indicators: List[Dict[str, Any]] = []

    transaction_limit_daily: Optional[float] = None
    transaction_limit_monthly: Optional[float] = None


class RiskProfileUpdate(BaseModel):
    """Schema para atualizar perfil."""

    risk_level: Optional[RiskLevel] = None
    risk_factors: Optional[List[Dict[str, Any]]] = None
    trust_indicators: Optional[List[Dict[str, Any]]] = None
    transaction_limit_daily: Optional[float] = None
    transaction_limit_monthly: Optional[float] = None
    is_blocked: Optional[bool] = None
    is_whitelisted: Optional[bool] = None
    is_watchlisted: Optional[bool] = None
    notes: Optional[str] = None


class RiskProfileResponse(BaseModel):
    """Schema de resposta de perfil."""

    id: UUID
    entity_type: EntityType
    entity_id: UUID
    entity_identifier: Optional[str] = None
    entity_name: Optional[str] = None

    risk_level: RiskLevel
    risk_score: float
    risk_score_change: float

    behavior_score: float
    transaction_score: float
    velocity_score: float
    identity_score: float

    risk_factors: List[Dict[str, Any]]
    trust_indicators: List[Dict[str, Any]]

    total_alerts: int
    confirmed_frauds: int
    false_positives: int
    fraud_rate: Optional[float] = None

    total_transactions: int
    total_transaction_value: float
    avg_transaction_value: float

    is_blocked: bool
    is_whitelisted: bool
    is_watchlisted: bool

    verification_level: int
    identity_verified: bool

    created_at: datetime
    last_calculated_at: Optional[datetime] = None

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
    previous_score: Optional[float] = None
    score_change: float
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]


# =============================================================================
# Detection Schemas
# =============================================================================


class DetectionRequest(BaseModel):
    """Schema generico para deteccao."""

    entity_type: str
    entity_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    context: Dict[str, Any] = {}
    real_time: bool = True


class DetectionResponse(BaseModel):
    """Schema de resposta de deteccao."""

    is_fraudulent: bool
    risk_score: float
    risk_level: RiskLevel
    alerts_generated: int
    alert_ids: List[UUID]
    matched_rules: List[str]
    matched_patterns: List[str]
    recommendations: List[str]
    processing_time_ms: int


class TransactionCheckRequest(BaseModel):
    """Schema para verificar transacao."""

    transaction_id: UUID
    transaction_type: str
    amount: float
    currency: str = "BRL"

    payer_id: UUID
    payer_type: str
    payer_account: Optional[str] = None

    payee_id: Optional[UUID] = None
    payee_type: Optional[str] = None
    payee_account: Optional[str] = None

    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    user_agent: Optional[str] = None

    metadata: Dict[str, Any] = {}


class TransactionCheckResponse(BaseModel):
    """Schema de resposta de verificacao de transacao."""

    transaction_id: UUID
    is_allowed: bool
    risk_score: float
    risk_level: RiskLevel

    decision: str  # approve, review, block, challenge
    decision_reasons: List[str]

    matched_rules: List[str]
    matched_patterns: List[str]

    alerts_generated: List[UUID]

    recommendations: List[str]
    required_actions: List[str]

    processing_time_ms: int


class AccessCheckRequest(BaseModel):
    """Schema para verificar acesso."""

    user_id: UUID
    session_id: Optional[str] = None

    ip_address: str
    device_id: Optional[str] = None
    user_agent: Optional[str] = None

    location: Optional[str] = None
    geo_coordinates: Optional[Dict[str, float]] = None

    action: str  # login, password_reset, data_export, etc
    resource: Optional[str] = None

    metadata: Dict[str, Any] = {}


class AccessCheckResponse(BaseModel):
    """Schema de resposta de verificacao de acesso."""

    user_id: UUID
    is_allowed: bool
    risk_score: float
    risk_level: RiskLevel

    decision: str  # allow, challenge, block
    challenge_type: Optional[str] = None  # mfa, captcha, email

    anomalies_detected: List[str]
    risk_factors: List[str]

    is_new_device: bool
    is_new_location: bool
    is_unusual_time: bool

    alerts_generated: List[UUID]

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

    by_severity: Dict[str, int]
    by_category: Dict[str, int]

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
    most_triggered_rules: List[Dict[str, Any]]

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
    alerts_trend: List[Dict[str, Any]]
    fraud_trend: List[Dict[str, Any]]
