"""
Sentiment Analysis Schemas - Sprint 46

Schemas Pydantic para validacao de dados de analise de sentimento.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# ============================================================
# Enums
# ============================================================


class SentimentTypeEnum(StrEnum):
    """Tipos de sentimento."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"


class EmotionTypeEnum(StrEnum):
    """Tipos de emocao."""

    JOY = "joy"
    SATISFACTION = "satisfaction"
    GRATITUDE = "gratitude"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"
    CONCERN = "concern"
    FRUSTRATION = "frustration"
    DISAPPOINTMENT = "disappointment"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    DISGUST = "disgust"
    URGENCY = "urgency"


class SourceTypeEnum(StrEnum):
    """Tipo de fonte."""

    TICKET = "ticket"
    EMAIL = "email"
    CHAT = "chat"
    REVIEW = "review"
    SURVEY = "survey"
    SOCIAL_MEDIA = "social_media"
    CALL_TRANSCRIPT = "call_transcript"
    FEEDBACK_FORM = "feedback_form"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    COMMENT = "comment"
    NPS_RESPONSE = "nps_response"
    WHATSAPP = "whatsapp"
    OTHER = "other"


class AnalysisStatusEnum(StrEnum):
    """Status da analise."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class TrendPeriodEnum(StrEnum):
    """Periodo de tendencia."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirectionEnum(StrEnum):
    """Direcao da tendencia."""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


class InsightTypeEnum(StrEnum):
    """Tipos de insight."""

    SENTIMENT_DROP = "sentiment_drop"
    SENTIMENT_SPIKE = "sentiment_spike"
    SENTIMENT_ANOMALY = "sentiment_anomaly"
    EMERGING_TOPIC = "emerging_topic"
    TRENDING_TOPIC = "trending_topic"
    RECURRING_ISSUE = "recurring_issue"
    CHURN_RISK = "churn_risk"
    CUSTOMER_CHAMPION = "customer_champion"
    CUSTOMER_RECOVERY = "customer_recovery"
    SERVICE_ISSUE = "service_issue"
    PRODUCT_ISSUE = "product_issue"
    PROCESS_BOTTLENECK = "process_bottleneck"
    UPSELL_OPPORTUNITY = "upsell_opportunity"
    IMPROVEMENT_SUGGESTION = "improvement_suggestion"
    FEATURE_REQUEST = "feature_request"
    BENCHMARK_DEVIATION = "benchmark_deviation"
    COMPETITOR_MENTION = "competitor_mention"
    URGENT_ATTENTION = "urgent_attention"
    COMPLIANCE_RISK = "compliance_risk"
    SUCCESS_STORY = "success_story"
    TEAM_RECOGNITION = "team_recognition"


class InsightPriorityEnum(StrEnum):
    """Prioridade do insight."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InsightStatusEnum(StrEnum):
    """Status do insight."""

    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class RuleCategoryEnum(StrEnum):
    """Categorias de regras."""

    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    KEYWORD = "keyword"
    ASPECT = "aspect"
    URGENCY = "urgency"
    CHURN = "churn"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    CLASSIFICATION = "classification"
    CUSTOM = "custom"


class RuleActionEnum(StrEnum):
    """Acoes da regra."""

    ALERT = "alert"
    ESCALATE = "escalate"
    NOTIFY_EMAIL = "notify_email"
    NOTIFY_SMS = "notify_sms"
    NOTIFY_SLACK = "notify_slack"
    CREATE_TICKET = "create_ticket"
    ASSIGN_AGENT = "assign_agent"
    TAG = "tag"
    PRIORITY_BOOST = "priority_boost"
    AUTO_RESPOND = "auto_respond"
    TRIGGER_WORKFLOW = "trigger_workflow"
    LOG = "log"


# ============================================================
# Base Schemas
# ============================================================


class AspectSchema(BaseModel):
    """Schema para aspecto identificado."""

    aspect: str
    sentiment: str
    score: float
    mentions: int = 1


class KeywordSchema(BaseModel):
    """Schema para keyword."""

    word: str
    frequency: int = 1


class EmotionScoreSchema(BaseModel):
    """Schema para score de emocao."""

    emotion: EmotionTypeEnum
    score: float = Field(..., ge=0, le=100)


class RecommendationSchema(BaseModel):
    """Schema para recomendacao."""

    action: str
    expected_impact: str
    effort: str = "medium"
    priority: int = 1
    details: dict[str, Any] | None = None


class RuleConditionSchema(BaseModel):
    """Schema para condicao de regra."""

    field: str
    operator: str
    value: Any


# ============================================================
# Sentiment Analysis Schemas
# ============================================================


class AnalyzeTextRequest(BaseModel):
    """Request para analise de texto."""

    text: str = Field(..., min_length=1, max_length=50000)
    source_type: SourceTypeEnum = SourceTypeEnum.OTHER
    source_id: UUID | None = None
    source_reference: str | None = Field(None, max_length=255)

    entity_type: str | None = Field(None, max_length=50)
    entity_id: UUID | None = None
    entity_name: str | None = Field(None, max_length=255)

    customer_id: UUID | None = None
    customer_name: str | None = Field(None, max_length=255)
    customer_segment: str | None = Field(None, max_length=100)

    language: str = Field("pt", max_length=10)
    nps_score: int | None = Field(None, ge=0, le=10)

    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None

    # Opcoes de analise
    detect_emotions: bool = True
    extract_aspects: bool = True
    extract_keywords: bool = True
    check_urgency: bool = True
    apply_rules: bool = True

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Texto nao pode ser vazio")
        return v.strip()


class AnalyzeTextResponse(BaseModel):
    """Response da analise de texto."""

    id: UUID

    # Sentimento
    sentiment_type: SentimentTypeEnum
    sentiment_label: str
    sentiment_score: float
    confidence_score: float

    # Polaridade
    positive_score: float
    negative_score: float
    neutral_score: float

    # Emocoes
    primary_emotion: EmotionTypeEnum | None
    secondary_emotion: EmotionTypeEnum | None
    emotion_scores: dict[str, float]

    # Aspectos e keywords
    aspects: list[AspectSchema]
    keywords: list[KeywordSchema]
    topics: list[str]

    # Indicadores
    has_urgency: bool
    urgency_level: int
    has_complaint: bool
    has_praise: bool
    has_question: bool
    has_suggestion: bool
    has_intent_to_leave: bool
    requires_action: bool
    is_critical: bool

    # Frases
    key_phrases: list[str]
    negative_phrases: list[str]
    positive_phrases: list[str]

    # NPS
    nps_score: int | None
    nps_category: str | None

    # Regras
    triggered_rules: list[dict[str, Any]]
    alert_generated: bool

    # Meta
    processing_time_ms: int
    model_version: str
    analyzed_at: datetime

    class Config:
        from_attributes = True


class BatchAnalyzeRequest(BaseModel):
    """Request para analise em lote."""

    texts: list[AnalyzeTextRequest] = Field(..., min_items=1, max_items=100)

    # Opcoes globais
    async_processing: bool = False
    callback_url: str | None = None


class BatchAnalyzeResponse(BaseModel):
    """Response da analise em lote."""

    total: int
    processed: int
    failed: int
    results: list[AnalyzeTextResponse]
    errors: list[dict[str, Any]]
    processing_time_ms: int


class SentimentAnalysisCreate(BaseModel):
    """Schema para criar analise."""

    original_text: str = Field(..., min_length=1)
    source_type: SourceTypeEnum
    source_id: UUID | None = None
    source_reference: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    customer_id: UUID | None = None
    customer_name: str | None = None
    language: str = "pt"
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None


class SentimentAnalysisUpdate(BaseModel):
    """Schema para atualizar analise."""

    is_reviewed: bool | None = None
    corrected_sentiment: SentimentTypeEnum | None = None
    review_notes: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class SentimentAnalysisResponse(BaseModel):
    """Response completo da analise."""

    id: UUID

    # Texto
    original_text: str
    normalized_text: str | None
    language: str
    word_count: int | None
    char_count: int | None

    # Fonte
    source_type: SourceTypeEnum
    source_id: UUID | None
    source_reference: str | None

    # Entidade
    entity_type: str | None
    entity_id: UUID | None
    entity_name: str | None

    # Cliente
    customer_id: UUID | None
    customer_name: str | None
    customer_segment: str | None

    # Sentimento
    sentiment_type: SentimentTypeEnum
    sentiment_score: float
    confidence_score: float
    positive_score: float
    negative_score: float
    neutral_score: float

    # Emocoes
    primary_emotion: EmotionTypeEnum | None
    secondary_emotion: EmotionTypeEnum | None
    emotion_scores: dict[str, float]

    # Aspectos
    aspects: list[dict[str, Any]]
    topics: list[str]
    keywords: list[dict[str, Any]]

    # Entidades
    entities_mentioned: list[str]
    products_mentioned: list[str]
    services_mentioned: list[str]

    # Indicadores
    has_urgency: bool
    urgency_level: int
    has_complaint: bool
    has_praise: bool
    has_question: bool
    has_suggestion: bool
    has_intent_to_leave: bool
    requires_action: bool

    # Frases
    key_phrases: list[str]
    negative_phrases: list[str]
    positive_phrases: list[str]

    # NPS
    nps_score: int | None
    nps_category: str | None

    # Status
    status: AnalysisStatusEnum
    processing_time_ms: int | None
    model_version: str | None

    # Revisao
    is_reviewed: bool
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    corrected_sentiment: SentimentTypeEnum | None

    # Regras
    triggered_rules: list[dict[str, Any]]
    alert_generated: bool
    alert_id: UUID | None

    # Meta
    metadata: dict[str, Any]
    tags: list[str]

    # Timestamps
    analyzed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class SentimentAnalysisSummary(BaseModel):
    """Resumo da analise."""

    id: UUID
    sentiment: SentimentTypeEnum
    sentiment_label: str
    score: float
    confidence: float
    primary_emotion: str | None
    is_critical: bool
    requires_action: bool
    key_aspects: list[dict[str, Any]]
    source_type: SourceTypeEnum
    analyzed_at: datetime | None

    class Config:
        from_attributes = True


class SentimentAnalysisListResponse(BaseModel):
    """Response de lista de analises."""

    items: list[SentimentAnalysisSummary]
    total: int
    page: int
    page_size: int
    pages: int


class SentimentAnalysisFilter(BaseModel):
    """Filtros para analises."""

    sentiment_types: list[SentimentTypeEnum] | None = None
    source_types: list[SourceTypeEnum] | None = None
    emotions: list[EmotionTypeEnum] | None = None
    customer_id: UUID | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None

    min_score: float | None = Field(None, ge=-100, le=100)
    max_score: float | None = Field(None, ge=-100, le=100)
    min_confidence: float | None = Field(None, ge=0, le=100)

    has_urgency: bool | None = None
    has_complaint: bool | None = None
    has_intent_to_leave: bool | None = None
    requires_action: bool | None = None
    is_critical: bool | None = None
    is_reviewed: bool | None = None

    keywords: list[str] | None = None
    topics: list[str] | None = None
    tags: list[str] | None = None

    date_from: datetime | None = None
    date_to: datetime | None = None


# ============================================================
# Sentiment Rule Schemas
# ============================================================


class SentimentRuleCreate(BaseModel):
    """Schema para criar regra."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None

    category: RuleCategoryEnum
    subcategory: str | None = Field(None, max_length=100)
    priority: int = Field(50, ge=1, le=100)
    weight: float = Field(1.0, ge=0, le=10)

    # Condicoes
    conditions: list[RuleConditionSchema] | None = None
    sentiment_threshold: float | None = Field(None, ge=-100, le=100)
    sentiment_types: list[SentimentTypeEnum] | None = None
    emotion_types: list[EmotionTypeEnum] | None = None
    emotion_threshold: float | None = Field(None, ge=0, le=100)

    # Keywords
    keywords_include: list[str] | None = None
    keywords_exclude: list[str] | None = None
    keywords_match_all: bool = False

    # Aspectos
    aspects_include: list[str] | None = None
    aspects_sentiment: str | None = None

    # Fontes
    source_types: list[SourceTypeEnum] | None = None
    exclude_sources: list[SourceTypeEnum] | None = None

    # Clientes
    customer_segments: list[str] | None = None
    customer_tiers: list[str] | None = None

    # Acoes
    primary_action: RuleActionEnum = RuleActionEnum.ALERT
    secondary_actions: list[RuleActionEnum] | None = None
    action_config: dict[str, Any] | None = None

    # Notificacoes
    notify_channels: list[str] | None = None
    notify_recipients: list[str] | None = None
    notify_template: str | None = None

    # Cooldown
    cooldown_minutes: int = Field(60, ge=0)
    cooldown_per_customer: bool = True
    max_triggers_per_day: int | None = Field(None, ge=1)

    # Horarios
    active_hours_start: int | None = Field(None, ge=0, le=23)
    active_hours_end: int | None = Field(None, ge=0, le=23)
    active_days: list[int] | None = None  # 0-6

    is_active: bool = True
    is_test_mode: bool = False


class SentimentRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    priority: int | None = Field(None, ge=1, le=100)
    weight: float | None = Field(None, ge=0, le=10)

    conditions: list[RuleConditionSchema] | None = None
    sentiment_threshold: float | None = None
    sentiment_types: list[SentimentTypeEnum] | None = None
    emotion_types: list[EmotionTypeEnum] | None = None

    keywords_include: list[str] | None = None
    keywords_exclude: list[str] | None = None

    primary_action: RuleActionEnum | None = None
    secondary_actions: list[RuleActionEnum] | None = None
    action_config: dict[str, Any] | None = None

    notify_channels: list[str] | None = None
    notify_recipients: list[str] | None = None

    cooldown_minutes: int | None = None
    max_triggers_per_day: int | None = None

    is_active: bool | None = None
    is_test_mode: bool | None = None


class SentimentRuleResponse(BaseModel):
    """Response da regra."""

    id: UUID
    code: str
    name: str
    description: str | None

    category: RuleCategoryEnum
    subcategory: str | None
    priority: int
    weight: float

    conditions: list[dict[str, Any]]
    sentiment_threshold: float | None
    sentiment_types: list[str]
    emotion_types: list[str]

    keywords_include: list[str]
    keywords_exclude: list[str]
    keywords_match_all: bool

    aspects_include: list[str]
    source_types: list[str]
    customer_segments: list[str]

    primary_action: RuleActionEnum
    secondary_actions: list[str]
    action_config: dict[str, Any]

    notify_channels: list[str]
    notify_recipients: list[str]

    cooldown_minutes: int
    max_triggers_per_day: int | None

    # Stats
    total_triggers: int
    total_actions: int
    true_positives: int
    false_positives: int
    precision_rate: float | None
    last_triggered_at: datetime | None

    is_active: bool
    is_system: bool
    is_test_mode: bool

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class SentimentRuleListResponse(BaseModel):
    """Response de lista de regras."""

    items: list[SentimentRuleResponse]
    total: int
    page: int
    page_size: int


class RuleEvaluationResult(BaseModel):
    """Resultado da avaliacao de regra."""

    rule_id: UUID
    rule_code: str
    rule_name: str
    matched: bool
    conditions_matched: int
    conditions_total: int
    reasons: list[str]
    actions_to_execute: list[dict[str, Any]]


# ============================================================
# Sentiment Trend Schemas
# ============================================================


class TrendFilter(BaseModel):
    """Filtros para tendencias."""

    period_type: TrendPeriodEnum | None = None
    category: str | None = None
    category_value: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class SentimentTrendResponse(BaseModel):
    """Response de tendencia."""

    id: UUID

    # Periodo
    period_type: TrendPeriodEnum
    period_start: datetime
    period_end: datetime
    period_label: str

    # Categoria
    category: str
    category_value: str | None
    entity_type: str | None
    entity_id: UUID | None

    # Metricas
    avg_sentiment_score: float
    min_sentiment_score: float | None
    max_sentiment_score: float | None
    std_sentiment_score: float | None

    # Distribuicao
    very_positive_count: int
    positive_count: int
    neutral_count: int
    negative_count: int
    very_negative_count: int
    mixed_count: int

    very_positive_pct: float
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    very_negative_pct: float

    total_analyses: int

    # Emocoes e aspectos
    emotion_distribution: dict[str, int]
    primary_emotion: str | None
    aspect_sentiments: dict[str, float]
    top_positive_aspects: list[str]
    top_negative_aspects: list[str]
    top_keywords: list[dict[str, Any]]

    # NPS
    nps_score: float | None
    promoters_count: int
    passives_count: int
    detractors_count: int

    # Indicadores
    complaints_count: int
    complaints_rate: float
    urgency_count: int
    churn_risk_count: int

    # Comparacao
    prev_avg_score: float | None
    score_change: float
    score_change_pct: float
    volume_change: int
    volume_change_pct: float

    # Tendencia
    trend_direction: TrendDirectionEnum
    trend_strength: float
    trend_confidence: float

    # Previsao
    predicted_next_score: float | None
    prediction_confidence: float | None

    # Insights
    insights: list[dict[str, Any]]
    alerts_generated: int

    # Taxas calculadas
    satisfaction_rate: float
    dissatisfaction_rate: float
    needs_attention: bool

    calculated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TrendSummary(BaseModel):
    """Resumo de tendencia."""

    period: str
    period_type: str
    category: str
    avg_score: float
    total_analyses: int
    satisfaction_rate: float
    dissatisfaction_rate: float
    trend: str
    score_change: float
    nps_score: float | None
    needs_attention: bool


class SentimentTrendListResponse(BaseModel):
    """Response de lista de tendencias."""

    items: list[TrendSummary]
    total: int


class TrendComparisonResponse(BaseModel):
    """Comparacao de tendencias."""

    current_period: TrendSummary
    previous_period: TrendSummary | None
    score_improvement: float
    volume_change: int
    satisfaction_change: float
    trend_direction: TrendDirectionEnum
    highlights: list[str]


# ============================================================
# Feedback Insight Schemas
# ============================================================


class FeedbackInsightCreate(BaseModel):
    """Schema para criar insight."""

    title: str = Field(..., min_length=1, max_length=300)
    description: str | None = None

    insight_type: InsightTypeEnum
    priority: InsightPriorityEnum = InsightPriorityEnum.MEDIUM

    category: str | None = Field(None, max_length=100)
    subcategory: str | None = Field(None, max_length=100)
    tags: list[str] | None = None

    scope: str | None = Field(None, max_length=50)
    scope_value: str | None = Field(None, max_length=255)

    entity_type: str | None = Field(None, max_length=50)
    entity_id: UUID | None = None
    entity_name: str | None = Field(None, max_length=255)

    # Scores
    impact_score: float = Field(0, ge=0, le=100)
    confidence_score: float = Field(0, ge=0, le=100)
    urgency_score: float = Field(0, ge=0, le=100)
    actionability_score: float = Field(0, ge=0, le=100)

    # Dados
    supporting_data: dict[str, Any] | None = None
    analysis_ids: list[UUID] | None = None

    # Periodo
    period_start: datetime | None = None
    period_end: datetime | None = None

    # Metricas
    avg_sentiment: float | None = None
    sentiment_change: float | None = None
    volume: int | None = None
    affected_customers: int | None = None

    # Topicos
    related_keywords: list[str] | None = None
    related_topics: list[str] | None = None
    related_aspects: list[str] | None = None

    # Recomendacoes
    recommendations: list[RecommendationSchema] | None = None

    # Previsao
    predicted_impact: str | None = None
    predicted_revenue_impact: float | None = None
    predicted_churn_impact: float | None = None

    # Validade
    valid_until: datetime | None = None
    is_recurring: bool = False

    # Notificacoes
    notify_recipients: list[str] | None = None


class FeedbackInsightUpdate(BaseModel):
    """Schema para atualizar insight."""

    title: str | None = Field(None, max_length=300)
    description: str | None = None
    priority: InsightPriorityEnum | None = None
    status: InsightStatusEnum | None = None

    tags: list[str] | None = None

    impact_score: float | None = Field(None, ge=0, le=100)
    urgency_score: float | None = Field(None, ge=0, le=100)

    recommendations: list[RecommendationSchema] | None = None
    actions_taken: list[dict[str, Any]] | None = None
    action_results: str | None = None

    assigned_to: UUID | None = None
    assigned_team: str | None = None

    valid_until: datetime | None = None
    notify_recipients: list[str] | None = None


class FeedbackInsightResponse(BaseModel):
    """Response do insight."""

    id: UUID
    insight_number: str
    title: str
    description: str | None

    insight_type: InsightTypeEnum
    priority: InsightPriorityEnum
    priority_label: str
    status: InsightStatusEnum

    category: str | None
    subcategory: str | None
    tags: list[str]

    scope: str | None
    scope_value: str | None

    entity_type: str | None
    entity_id: UUID | None
    entity_name: str | None

    # Scores
    impact_score: float
    confidence_score: float
    urgency_score: float
    actionability_score: float
    overall_score: float

    # Dados
    supporting_data: dict[str, Any]
    analysis_ids: list[UUID]
    analysis_count: int

    # Periodo
    period_start: datetime | None
    period_end: datetime | None

    # Metricas
    avg_sentiment: float | None
    sentiment_change: float | None
    volume: int | None
    affected_customers: int | None

    # Topicos
    related_keywords: list[str]
    related_topics: list[str]
    related_aspects: list[str]

    # Recomendacoes
    recommendations: list[dict[str, Any]]
    actions_taken: list[dict[str, Any]]
    action_results: str | None

    # Benchmark
    benchmark_value: float | None
    deviation_from_benchmark: float | None

    # Previsao
    predicted_impact: str | None
    predicted_revenue_impact: float | None
    predicted_churn_impact: float | None

    # Estado
    is_actionable: bool
    is_critical: bool
    is_expired: bool
    is_recurring: bool
    valid_until: datetime | None

    # Atribuicao
    assigned_to: UUID | None
    assigned_at: datetime | None
    assigned_team: str | None

    # Resolucao
    resolved_by: UUID | None
    resolved_at: datetime | None
    resolution_notes: str | None
    resolution_outcome: str | None

    # Feedback
    was_useful: bool | None
    usefulness_rating: int | None
    feedback_notes: str | None

    # Notificacoes
    notifications_sent: int
    last_notified_at: datetime | None

    # Timestamps
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class InsightSummary(BaseModel):
    """Resumo do insight."""

    id: UUID
    number: str
    type: str
    title: str
    priority: str
    priority_label: str
    status: str
    overall_score: float
    is_actionable: bool
    is_critical: bool
    affected_customers: int | None
    recommendations_count: int
    created_at: datetime | None


class FeedbackInsightListResponse(BaseModel):
    """Response de lista de insights."""

    items: list[InsightSummary]
    total: int
    page: int
    page_size: int


class InsightFilter(BaseModel):
    """Filtros para insights."""

    insight_types: list[InsightTypeEnum] | None = None
    priorities: list[InsightPriorityEnum] | None = None
    statuses: list[InsightStatusEnum] | None = None

    category: str | None = None
    entity_type: str | None = None
    entity_id: UUID | None = None

    min_impact_score: float | None = Field(None, ge=0, le=100)
    min_urgency_score: float | None = Field(None, ge=0, le=100)

    is_actionable: bool | None = None
    is_critical: bool | None = None
    is_expired: bool | None = None

    assigned_to: UUID | None = None
    assigned_team: str | None = None

    tags: list[str] | None = None

    date_from: datetime | None = None
    date_to: datetime | None = None


# ============================================================
# Dashboard Schemas
# ============================================================


class SentimentMetricsResponse(BaseModel):
    """Metricas de sentimento."""

    total_analyses: int
    avg_sentiment_score: float

    very_positive_count: int
    positive_count: int
    neutral_count: int
    negative_count: int
    very_negative_count: int

    satisfaction_rate: float
    dissatisfaction_rate: float

    critical_count: int
    requires_action_count: int

    avg_confidence: float

    # Comparacao
    score_change_24h: float
    score_change_7d: float
    volume_change_24h: int
    volume_change_7d: int


class EmotionDistributionResponse(BaseModel):
    """Distribuicao de emocoes."""

    emotions: dict[str, int]
    total: int
    primary_emotion: str
    primary_emotion_pct: float


class AspectAnalysisResponse(BaseModel):
    """Analise por aspectos."""

    aspects: list[dict[str, Any]]
    top_positive: list[dict[str, Any]]
    top_negative: list[dict[str, Any]]
    total_aspects: int


class SentimentDashboardResponse(BaseModel):
    """Dashboard completo de sentimento."""

    # Metricas gerais
    metrics: SentimentMetricsResponse

    # Distribuicao de emocoes
    emotions: EmotionDistributionResponse

    # Aspectos
    aspects: AspectAnalysisResponse

    # Tendencia recente
    trend: TrendSummary
    trend_direction: TrendDirectionEnum

    # Top keywords
    top_keywords: list[dict[str, Any]]
    trending_keywords: list[dict[str, Any]]

    # Insights ativos
    active_insights: list[InsightSummary]
    critical_insights_count: int

    # Alertas
    pending_alerts: int
    alerts_today: int

    # Por fonte
    by_source: dict[str, dict[str, Any]]

    # Ultimas analises criticas
    recent_critical: list[SentimentAnalysisSummary]

    # NPS
    nps_score: float | None
    nps_trend: str | None

    # Periodo
    period_start: datetime
    period_end: datetime
    generated_at: datetime
