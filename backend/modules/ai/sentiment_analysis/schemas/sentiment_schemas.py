"""
Sentiment Analysis Schemas - Sprint 46

Schemas Pydantic para validacao de dados de analise de sentimento.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, validator


# ============================================================
# Enums
# ============================================================

class SentimentTypeEnum(str, Enum):
    """Tipos de sentimento."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"


class EmotionTypeEnum(str, Enum):
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


class SourceTypeEnum(str, Enum):
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


class AnalysisStatusEnum(str, Enum):
    """Status da analise."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class TrendPeriodEnum(str, Enum):
    """Periodo de tendencia."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TrendDirectionEnum(str, Enum):
    """Direcao da tendencia."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


class InsightTypeEnum(str, Enum):
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


class InsightPriorityEnum(str, Enum):
    """Prioridade do insight."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InsightStatusEnum(str, Enum):
    """Status do insight."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class RuleCategoryEnum(str, Enum):
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


class RuleActionEnum(str, Enum):
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
    details: Optional[Dict[str, Any]] = None


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
    source_id: Optional[UUID] = None
    source_reference: Optional[str] = Field(None, max_length=255)

    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    entity_name: Optional[str] = Field(None, max_length=255)

    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_segment: Optional[str] = Field(None, max_length=100)

    language: str = Field("pt", max_length=10)
    nps_score: Optional[int] = Field(None, ge=0, le=10)

    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    # Opcoes de analise
    detect_emotions: bool = True
    extract_aspects: bool = True
    extract_keywords: bool = True
    check_urgency: bool = True
    apply_rules: bool = True

    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Texto nao pode ser vazio')
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
    primary_emotion: Optional[EmotionTypeEnum]
    secondary_emotion: Optional[EmotionTypeEnum]
    emotion_scores: Dict[str, float]

    # Aspectos e keywords
    aspects: List[AspectSchema]
    keywords: List[KeywordSchema]
    topics: List[str]

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
    key_phrases: List[str]
    negative_phrases: List[str]
    positive_phrases: List[str]

    # NPS
    nps_score: Optional[int]
    nps_category: Optional[str]

    # Regras
    triggered_rules: List[Dict[str, Any]]
    alert_generated: bool

    # Meta
    processing_time_ms: int
    model_version: str
    analyzed_at: datetime

    class Config:
        from_attributes = True


class BatchAnalyzeRequest(BaseModel):
    """Request para analise em lote."""
    texts: List[AnalyzeTextRequest] = Field(..., min_items=1, max_items=100)

    # Opcoes globais
    async_processing: bool = False
    callback_url: Optional[str] = None


class BatchAnalyzeResponse(BaseModel):
    """Response da analise em lote."""
    total: int
    processed: int
    failed: int
    results: List[AnalyzeTextResponse]
    errors: List[Dict[str, Any]]
    processing_time_ms: int


class SentimentAnalysisCreate(BaseModel):
    """Schema para criar analise."""
    original_text: str = Field(..., min_length=1)
    source_type: SourceTypeEnum
    source_id: Optional[UUID] = None
    source_reference: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    language: str = "pt"
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class SentimentAnalysisUpdate(BaseModel):
    """Schema para atualizar analise."""
    is_reviewed: Optional[bool] = None
    corrected_sentiment: Optional[SentimentTypeEnum] = None
    review_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SentimentAnalysisResponse(BaseModel):
    """Response completo da analise."""
    id: UUID

    # Texto
    original_text: str
    normalized_text: Optional[str]
    language: str
    word_count: Optional[int]
    char_count: Optional[int]

    # Fonte
    source_type: SourceTypeEnum
    source_id: Optional[UUID]
    source_reference: Optional[str]

    # Entidade
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    entity_name: Optional[str]

    # Cliente
    customer_id: Optional[UUID]
    customer_name: Optional[str]
    customer_segment: Optional[str]

    # Sentimento
    sentiment_type: SentimentTypeEnum
    sentiment_score: float
    confidence_score: float
    positive_score: float
    negative_score: float
    neutral_score: float

    # Emocoes
    primary_emotion: Optional[EmotionTypeEnum]
    secondary_emotion: Optional[EmotionTypeEnum]
    emotion_scores: Dict[str, float]

    # Aspectos
    aspects: List[Dict[str, Any]]
    topics: List[str]
    keywords: List[Dict[str, Any]]

    # Entidades
    entities_mentioned: List[str]
    products_mentioned: List[str]
    services_mentioned: List[str]

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
    key_phrases: List[str]
    negative_phrases: List[str]
    positive_phrases: List[str]

    # NPS
    nps_score: Optional[int]
    nps_category: Optional[str]

    # Status
    status: AnalysisStatusEnum
    processing_time_ms: Optional[int]
    model_version: Optional[str]

    # Revisao
    is_reviewed: bool
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    corrected_sentiment: Optional[SentimentTypeEnum]

    # Regras
    triggered_rules: List[Dict[str, Any]]
    alert_generated: bool
    alert_id: Optional[UUID]

    # Meta
    metadata: Dict[str, Any]
    tags: List[str]

    # Timestamps
    analyzed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SentimentAnalysisSummary(BaseModel):
    """Resumo da analise."""
    id: UUID
    sentiment: SentimentTypeEnum
    sentiment_label: str
    score: float
    confidence: float
    primary_emotion: Optional[str]
    is_critical: bool
    requires_action: bool
    key_aspects: List[Dict[str, Any]]
    source_type: SourceTypeEnum
    analyzed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SentimentAnalysisListResponse(BaseModel):
    """Response de lista de analises."""
    items: List[SentimentAnalysisSummary]
    total: int
    page: int
    page_size: int
    pages: int


class SentimentAnalysisFilter(BaseModel):
    """Filtros para analises."""
    sentiment_types: Optional[List[SentimentTypeEnum]] = None
    source_types: Optional[List[SourceTypeEnum]] = None
    emotions: Optional[List[EmotionTypeEnum]] = None
    customer_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None

    min_score: Optional[float] = Field(None, ge=-100, le=100)
    max_score: Optional[float] = Field(None, ge=-100, le=100)
    min_confidence: Optional[float] = Field(None, ge=0, le=100)

    has_urgency: Optional[bool] = None
    has_complaint: Optional[bool] = None
    has_intent_to_leave: Optional[bool] = None
    requires_action: Optional[bool] = None
    is_critical: Optional[bool] = None
    is_reviewed: Optional[bool] = None

    keywords: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# ============================================================
# Sentiment Rule Schemas
# ============================================================

class SentimentRuleCreate(BaseModel):
    """Schema para criar regra."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    category: RuleCategoryEnum
    subcategory: Optional[str] = Field(None, max_length=100)
    priority: int = Field(50, ge=1, le=100)
    weight: float = Field(1.0, ge=0, le=10)

    # Condicoes
    conditions: Optional[List[RuleConditionSchema]] = None
    sentiment_threshold: Optional[float] = Field(None, ge=-100, le=100)
    sentiment_types: Optional[List[SentimentTypeEnum]] = None
    emotion_types: Optional[List[EmotionTypeEnum]] = None
    emotion_threshold: Optional[float] = Field(None, ge=0, le=100)

    # Keywords
    keywords_include: Optional[List[str]] = None
    keywords_exclude: Optional[List[str]] = None
    keywords_match_all: bool = False

    # Aspectos
    aspects_include: Optional[List[str]] = None
    aspects_sentiment: Optional[str] = None

    # Fontes
    source_types: Optional[List[SourceTypeEnum]] = None
    exclude_sources: Optional[List[SourceTypeEnum]] = None

    # Clientes
    customer_segments: Optional[List[str]] = None
    customer_tiers: Optional[List[str]] = None

    # Acoes
    primary_action: RuleActionEnum = RuleActionEnum.ALERT
    secondary_actions: Optional[List[RuleActionEnum]] = None
    action_config: Optional[Dict[str, Any]] = None

    # Notificacoes
    notify_channels: Optional[List[str]] = None
    notify_recipients: Optional[List[str]] = None
    notify_template: Optional[str] = None

    # Cooldown
    cooldown_minutes: int = Field(60, ge=0)
    cooldown_per_customer: bool = True
    max_triggers_per_day: Optional[int] = Field(None, ge=1)

    # Horarios
    active_hours_start: Optional[int] = Field(None, ge=0, le=23)
    active_hours_end: Optional[int] = Field(None, ge=0, le=23)
    active_days: Optional[List[int]] = None  # 0-6

    is_active: bool = True
    is_test_mode: bool = False


class SentimentRuleUpdate(BaseModel):
    """Schema para atualizar regra."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=100)
    weight: Optional[float] = Field(None, ge=0, le=10)

    conditions: Optional[List[RuleConditionSchema]] = None
    sentiment_threshold: Optional[float] = None
    sentiment_types: Optional[List[SentimentTypeEnum]] = None
    emotion_types: Optional[List[EmotionTypeEnum]] = None

    keywords_include: Optional[List[str]] = None
    keywords_exclude: Optional[List[str]] = None

    primary_action: Optional[RuleActionEnum] = None
    secondary_actions: Optional[List[RuleActionEnum]] = None
    action_config: Optional[Dict[str, Any]] = None

    notify_channels: Optional[List[str]] = None
    notify_recipients: Optional[List[str]] = None

    cooldown_minutes: Optional[int] = None
    max_triggers_per_day: Optional[int] = None

    is_active: Optional[bool] = None
    is_test_mode: Optional[bool] = None


class SentimentRuleResponse(BaseModel):
    """Response da regra."""
    id: UUID
    code: str
    name: str
    description: Optional[str]

    category: RuleCategoryEnum
    subcategory: Optional[str]
    priority: int
    weight: float

    conditions: List[Dict[str, Any]]
    sentiment_threshold: Optional[float]
    sentiment_types: List[str]
    emotion_types: List[str]

    keywords_include: List[str]
    keywords_exclude: List[str]
    keywords_match_all: bool

    aspects_include: List[str]
    source_types: List[str]
    customer_segments: List[str]

    primary_action: RuleActionEnum
    secondary_actions: List[str]
    action_config: Dict[str, Any]

    notify_channels: List[str]
    notify_recipients: List[str]

    cooldown_minutes: int
    max_triggers_per_day: Optional[int]

    # Stats
    total_triggers: int
    total_actions: int
    true_positives: int
    false_positives: int
    precision_rate: Optional[float]
    last_triggered_at: Optional[datetime]

    is_active: bool
    is_system: bool
    is_test_mode: bool

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SentimentRuleListResponse(BaseModel):
    """Response de lista de regras."""
    items: List[SentimentRuleResponse]
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
    reasons: List[str]
    actions_to_execute: List[Dict[str, Any]]


# ============================================================
# Sentiment Trend Schemas
# ============================================================

class TrendFilter(BaseModel):
    """Filtros para tendencias."""
    period_type: Optional[TrendPeriodEnum] = None
    category: Optional[str] = None
    category_value: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


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
    category_value: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[UUID]

    # Metricas
    avg_sentiment_score: float
    min_sentiment_score: Optional[float]
    max_sentiment_score: Optional[float]
    std_sentiment_score: Optional[float]

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
    emotion_distribution: Dict[str, int]
    primary_emotion: Optional[str]
    aspect_sentiments: Dict[str, float]
    top_positive_aspects: List[str]
    top_negative_aspects: List[str]
    top_keywords: List[Dict[str, Any]]

    # NPS
    nps_score: Optional[float]
    promoters_count: int
    passives_count: int
    detractors_count: int

    # Indicadores
    complaints_count: int
    complaints_rate: float
    urgency_count: int
    churn_risk_count: int

    # Comparacao
    prev_avg_score: Optional[float]
    score_change: float
    score_change_pct: float
    volume_change: int
    volume_change_pct: float

    # Tendencia
    trend_direction: TrendDirectionEnum
    trend_strength: float
    trend_confidence: float

    # Previsao
    predicted_next_score: Optional[float]
    prediction_confidence: Optional[float]

    # Insights
    insights: List[Dict[str, Any]]
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
    nps_score: Optional[float]
    needs_attention: bool


class SentimentTrendListResponse(BaseModel):
    """Response de lista de tendencias."""
    items: List[TrendSummary]
    total: int


class TrendComparisonResponse(BaseModel):
    """Comparacao de tendencias."""
    current_period: TrendSummary
    previous_period: Optional[TrendSummary]
    score_improvement: float
    volume_change: int
    satisfaction_change: float
    trend_direction: TrendDirectionEnum
    highlights: List[str]


# ============================================================
# Feedback Insight Schemas
# ============================================================

class FeedbackInsightCreate(BaseModel):
    """Schema para criar insight."""
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None

    insight_type: InsightTypeEnum
    priority: InsightPriorityEnum = InsightPriorityEnum.MEDIUM

    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None

    scope: Optional[str] = Field(None, max_length=50)
    scope_value: Optional[str] = Field(None, max_length=255)

    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    entity_name: Optional[str] = Field(None, max_length=255)

    # Scores
    impact_score: float = Field(0, ge=0, le=100)
    confidence_score: float = Field(0, ge=0, le=100)
    urgency_score: float = Field(0, ge=0, le=100)
    actionability_score: float = Field(0, ge=0, le=100)

    # Dados
    supporting_data: Optional[Dict[str, Any]] = None
    analysis_ids: Optional[List[UUID]] = None

    # Periodo
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    # Metricas
    avg_sentiment: Optional[float] = None
    sentiment_change: Optional[float] = None
    volume: Optional[int] = None
    affected_customers: Optional[int] = None

    # Topicos
    related_keywords: Optional[List[str]] = None
    related_topics: Optional[List[str]] = None
    related_aspects: Optional[List[str]] = None

    # Recomendacoes
    recommendations: Optional[List[RecommendationSchema]] = None

    # Previsao
    predicted_impact: Optional[str] = None
    predicted_revenue_impact: Optional[float] = None
    predicted_churn_impact: Optional[float] = None

    # Validade
    valid_until: Optional[datetime] = None
    is_recurring: bool = False

    # Notificacoes
    notify_recipients: Optional[List[str]] = None


class FeedbackInsightUpdate(BaseModel):
    """Schema para atualizar insight."""
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    priority: Optional[InsightPriorityEnum] = None
    status: Optional[InsightStatusEnum] = None

    tags: Optional[List[str]] = None

    impact_score: Optional[float] = Field(None, ge=0, le=100)
    urgency_score: Optional[float] = Field(None, ge=0, le=100)

    recommendations: Optional[List[RecommendationSchema]] = None
    actions_taken: Optional[List[Dict[str, Any]]] = None
    action_results: Optional[str] = None

    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = None

    valid_until: Optional[datetime] = None
    notify_recipients: Optional[List[str]] = None


class FeedbackInsightResponse(BaseModel):
    """Response do insight."""
    id: UUID
    insight_number: str
    title: str
    description: Optional[str]

    insight_type: InsightTypeEnum
    priority: InsightPriorityEnum
    priority_label: str
    status: InsightStatusEnum

    category: Optional[str]
    subcategory: Optional[str]
    tags: List[str]

    scope: Optional[str]
    scope_value: Optional[str]

    entity_type: Optional[str]
    entity_id: Optional[UUID]
    entity_name: Optional[str]

    # Scores
    impact_score: float
    confidence_score: float
    urgency_score: float
    actionability_score: float
    overall_score: float

    # Dados
    supporting_data: Dict[str, Any]
    analysis_ids: List[UUID]
    analysis_count: int

    # Periodo
    period_start: Optional[datetime]
    period_end: Optional[datetime]

    # Metricas
    avg_sentiment: Optional[float]
    sentiment_change: Optional[float]
    volume: Optional[int]
    affected_customers: Optional[int]

    # Topicos
    related_keywords: List[str]
    related_topics: List[str]
    related_aspects: List[str]

    # Recomendacoes
    recommendations: List[Dict[str, Any]]
    actions_taken: List[Dict[str, Any]]
    action_results: Optional[str]

    # Benchmark
    benchmark_value: Optional[float]
    deviation_from_benchmark: Optional[float]

    # Previsao
    predicted_impact: Optional[str]
    predicted_revenue_impact: Optional[float]
    predicted_churn_impact: Optional[float]

    # Estado
    is_actionable: bool
    is_critical: bool
    is_expired: bool
    is_recurring: bool
    valid_until: Optional[datetime]

    # Atribuicao
    assigned_to: Optional[UUID]
    assigned_at: Optional[datetime]
    assigned_team: Optional[str]

    # Resolucao
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    resolution_outcome: Optional[str]

    # Feedback
    was_useful: Optional[bool]
    usefulness_rating: Optional[int]
    feedback_notes: Optional[str]

    # Notificacoes
    notifications_sent: int
    last_notified_at: Optional[datetime]

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]

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
    affected_customers: Optional[int]
    recommendations_count: int
    created_at: Optional[datetime]


class FeedbackInsightListResponse(BaseModel):
    """Response de lista de insights."""
    items: List[InsightSummary]
    total: int
    page: int
    page_size: int


class InsightFilter(BaseModel):
    """Filtros para insights."""
    insight_types: Optional[List[InsightTypeEnum]] = None
    priorities: Optional[List[InsightPriorityEnum]] = None
    statuses: Optional[List[InsightStatusEnum]] = None

    category: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None

    min_impact_score: Optional[float] = Field(None, ge=0, le=100)
    min_urgency_score: Optional[float] = Field(None, ge=0, le=100)

    is_actionable: Optional[bool] = None
    is_critical: Optional[bool] = None
    is_expired: Optional[bool] = None

    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = None

    tags: Optional[List[str]] = None

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


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
    emotions: Dict[str, int]
    total: int
    primary_emotion: str
    primary_emotion_pct: float


class AspectAnalysisResponse(BaseModel):
    """Analise por aspectos."""
    aspects: List[Dict[str, Any]]
    top_positive: List[Dict[str, Any]]
    top_negative: List[Dict[str, Any]]
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
    top_keywords: List[Dict[str, Any]]
    trending_keywords: List[Dict[str, Any]]

    # Insights ativos
    active_insights: List[InsightSummary]
    critical_insights_count: int

    # Alertas
    pending_alerts: int
    alerts_today: int

    # Por fonte
    by_source: Dict[str, Dict[str, Any]]

    # Ultimas analises criticas
    recent_critical: List[SentimentAnalysisSummary]

    # NPS
    nps_score: Optional[float]
    nps_trend: Optional[str]

    # Periodo
    period_start: datetime
    period_end: datetime
    generated_at: datetime
