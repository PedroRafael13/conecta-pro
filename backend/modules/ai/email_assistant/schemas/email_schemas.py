"""
Email Assistant Schemas - Sprint 54.

Pydantic schemas para validacao e serializacao.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Enums
# =============================================================================


class EmailStatusEnum(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    RESPONDED = "responded"
    ARCHIVED = "archived"
    SPAM = "spam"
    DELETED = "deleted"


class EmailCategoryEnum(StrEnum):
    SUPPORT = "support"
    SALES = "sales"
    BILLING = "billing"
    COMPLAINT = "complaint"
    INFORMATION = "information"
    SCHEDULING = "scheduling"
    FEEDBACK = "feedback"
    NEWSLETTER = "newsletter"
    SPAM = "spam"
    PHISHING = "phishing"
    INTERNAL = "internal"
    OTHER = "other"


class EmailPriorityEnum(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class EmailSentimentEnum(StrEnum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


# =============================================================================
# Email Schemas
# =============================================================================


class EmailCreate(BaseModel):
    """Schema para criar email."""

    message_id: str = Field(..., max_length=500)
    thread_id: str | None = Field(None, max_length=500)
    from_address: str = Field(..., max_length=500)
    from_name: str | None = Field(None, max_length=200)
    to_addresses: list[str] = Field(default_factory=list)
    cc_addresses: list[str] = Field(default_factory=list)
    subject: str | None = Field(None, max_length=1000)
    body_text: str | None = None
    body_html: str | None = None
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    received_at: datetime
    headers: dict[str, Any] = Field(default_factory=dict)
    account_id: UUID | None = None
    condominio_id: UUID | None = None


class EmailUpdate(BaseModel):
    """Schema para atualizar email."""

    status: EmailStatusEnum | None = None
    category: EmailCategoryEnum | None = None
    priority: EmailPriorityEnum | None = None
    assigned_to: UUID | None = None
    assigned_team: str | None = None
    is_spam: bool | None = None
    metadata: dict[str, Any] | None = None


class EmailResponse(BaseModel):
    """Schema de resposta para email."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    message_id: str
    thread_id: str | None
    from_address: str
    from_name: str | None
    to_addresses: list[str]
    cc_addresses: list[str]
    subject: str | None
    body_preview: str | None
    has_attachments: bool
    attachment_count: int
    status: str
    category: str | None
    category_confidence: float
    priority: str
    priority_score: float
    sentiment: str | None
    sentiment_score: float
    language: str
    keywords: list[str]
    intent: str | None
    is_spam: bool
    spam_score: float
    is_phishing: bool
    security_score: float
    auto_reply_sent: bool
    suggested_reply: str | None
    assigned_to: UUID | None
    assigned_team: str | None
    received_at: datetime
    processed_at: datetime | None
    created_at: datetime
    ativo: bool


class EmailListResponse(BaseModel):
    """Schema para listagem de emails."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_address: str
    from_name: str | None
    subject: str | None
    status: str
    category: str | None
    priority: str
    is_spam: bool
    received_at: datetime


class EmailClassificationResult(BaseModel):
    """Schema para resultado de classificacao."""

    category: str
    category_confidence: float
    subcategory: str | None
    priority: str
    priority_score: float
    priority_factors: dict[str, float]
    sentiment: str
    sentiment_score: float
    emotions: dict[str, float]
    intent: str | None
    intent_confidence: float
    keywords: list[str]
    entities: list[dict[str, Any]]
    topics: list[str]
    action_items: list[dict[str, Any]]
    questions: list[dict[str, Any]]
    is_spam: bool
    spam_score: float
    is_phishing: bool
    phishing_indicators: list[str]
    security_score: float
    processing_time_ms: int


class EmailAnalysisRequest(BaseModel):
    """Schema para request de analise."""

    subject: str | None = None
    body: str = Field(..., min_length=1)
    from_address: str | None = None
    headers: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Response Schemas
# =============================================================================


class EmailResponseCreate(BaseModel):
    """Schema para criar resposta."""

    email_id: UUID
    subject: str | None = Field(None, max_length=1000)
    body_text: str = Field(..., min_length=1)
    body_html: str | None = None
    response_type: str = Field(default="manual")
    template_id: UUID | None = None


class EmailResponseOut(BaseModel):
    """Schema de resposta para resposta de email."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email_id: UUID
    subject: str | None
    body_text: str
    response_type: str
    is_draft: bool
    is_sent: bool
    sent_at: datetime | None
    ai_generated: bool
    generation_confidence: float
    created_at: datetime


class GenerateReplyRequest(BaseModel):
    """Schema para request de geracao de resposta."""

    email_id: UUID
    tone: str = Field(default="professional")  # professional, friendly, formal
    max_length: int = Field(default=500, ge=50, le=2000)
    include_greeting: bool = True
    include_signature: bool = True
    context: dict[str, Any] = Field(default_factory=dict)


class GenerateReplyResponse(BaseModel):
    """Schema para resposta de geracao."""

    reply_text: str
    reply_html: str | None
    confidence: float
    tone_used: str
    template_used: str | None
    variables_filled: dict[str, Any]
    suggestions: list[str]
    processing_time_ms: int


# =============================================================================
# Template Schemas
# =============================================================================


class EmailTemplateCreate(BaseModel):
    """Schema para criar template."""

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    subject_template: str | None = Field(None, max_length=1000)
    body_template: str = Field(..., min_length=1)
    body_html_template: str | None = None
    category: EmailCategoryEnum | None = None
    language: str = Field(default="pt-BR")
    tags: list[str] = Field(default_factory=list)
    trigger_keywords: list[str] = Field(default_factory=list)
    trigger_intents: list[str] = Field(default_factory=list)
    variables: list[dict[str, Any]] = Field(default_factory=list)


class EmailTemplateUpdate(BaseModel):
    """Schema para atualizar template."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    subject_template: str | None = Field(None, max_length=1000)
    body_template: str | None = None
    body_html_template: str | None = None
    category: EmailCategoryEnum | None = None
    tags: list[str] | None = None
    trigger_keywords: list[str] | None = None
    trigger_intents: list[str] | None = None
    is_active: bool | None = None


class EmailTemplateResponse(BaseModel):
    """Schema de resposta para template."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: str | None
    subject_template: str | None
    body_template: str
    category: str | None
    language: str
    tags: list[str]
    trigger_keywords: list[str]
    variables: list[dict[str, Any]]
    usage_count: int
    success_rate: float
    is_active: bool
    created_at: datetime


# =============================================================================
# Rule Schemas
# =============================================================================


class EmailRuleCreate(BaseModel):
    """Schema para criar regra."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int = Field(default=0)
    conditions: list[dict[str, Any]] = Field(..., min_length=1)
    condition_logic: str = Field(default="AND")
    actions: list[dict[str, Any]] = Field(..., min_length=1)
    stop_processing: bool = False
    condominio_id: UUID | None = None


class EmailRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    priority: int | None = None
    conditions: list[dict[str, Any]] | None = None
    condition_logic: str | None = None
    actions: list[dict[str, Any]] | None = None
    is_active: bool | None = None
    stop_processing: bool | None = None


class EmailRuleResponse(BaseModel):
    """Schema de resposta para regra."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    priority: int
    conditions: list[dict[str, Any]]
    condition_logic: str
    actions: list[dict[str, Any]]
    is_active: bool
    stop_processing: bool
    match_count: int
    last_match_at: datetime | None
    created_at: datetime


# =============================================================================
# Dashboard Schemas
# =============================================================================


class EmailAssistantDashboard(BaseModel):
    """Schema para dashboard do assistente."""

    # Totais
    total_emails: int
    total_processed: int
    total_unprocessed: int
    total_spam: int
    total_phishing: int

    # Por status
    emails_by_status: dict[str, int]

    # Por categoria
    emails_by_category: dict[str, int]

    # Por prioridade
    emails_by_priority: dict[str, int]

    # Metricas
    avg_processing_time_ms: float
    avg_response_time_minutes: float
    auto_reply_rate: float
    classification_accuracy: float

    # Sentimento
    sentiment_distribution: dict[str, int]

    # Templates
    top_templates: list[dict[str, Any]]

    # Tendencias
    emails_trend: list[dict[str, Any]]
    response_time_trend: list[dict[str, Any]]
