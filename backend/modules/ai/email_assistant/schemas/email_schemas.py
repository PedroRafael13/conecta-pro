"""
Email Assistant Schemas - Sprint 54.

Pydantic schemas para validacao e serializacao.
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# =============================================================================
# Enums
# =============================================================================


class EmailStatusEnum(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    RESPONDED = "responded"
    ARCHIVED = "archived"
    SPAM = "spam"
    DELETED = "deleted"


class EmailCategoryEnum(str, Enum):
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


class EmailPriorityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class EmailSentimentEnum(str, Enum):
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
    thread_id: Optional[str] = Field(None, max_length=500)
    from_address: str = Field(..., max_length=500)
    from_name: Optional[str] = Field(None, max_length=200)
    to_addresses: List[str] = Field(default_factory=list)
    cc_addresses: List[str] = Field(default_factory=list)
    subject: Optional[str] = Field(None, max_length=1000)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    received_at: datetime
    headers: Dict[str, Any] = Field(default_factory=dict)
    account_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None


class EmailUpdate(BaseModel):
    """Schema para atualizar email."""

    status: Optional[EmailStatusEnum] = None
    category: Optional[EmailCategoryEnum] = None
    priority: Optional[EmailPriorityEnum] = None
    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = None
    is_spam: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class EmailResponse(BaseModel):
    """Schema de resposta para email."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    message_id: str
    thread_id: Optional[str]
    from_address: str
    from_name: Optional[str]
    to_addresses: List[str]
    cc_addresses: List[str]
    subject: Optional[str]
    body_preview: Optional[str]
    has_attachments: bool
    attachment_count: int
    status: str
    category: Optional[str]
    category_confidence: float
    priority: str
    priority_score: float
    sentiment: Optional[str]
    sentiment_score: float
    language: str
    keywords: List[str]
    intent: Optional[str]
    is_spam: bool
    spam_score: float
    is_phishing: bool
    security_score: float
    auto_reply_sent: bool
    suggested_reply: Optional[str]
    assigned_to: Optional[UUID]
    assigned_team: Optional[str]
    received_at: datetime
    processed_at: Optional[datetime]
    created_at: datetime
    ativo: bool


class EmailListResponse(BaseModel):
    """Schema para listagem de emails."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_address: str
    from_name: Optional[str]
    subject: Optional[str]
    status: str
    category: Optional[str]
    priority: str
    is_spam: bool
    received_at: datetime


class EmailClassificationResult(BaseModel):
    """Schema para resultado de classificacao."""

    category: str
    category_confidence: float
    subcategory: Optional[str]
    priority: str
    priority_score: float
    priority_factors: Dict[str, float]
    sentiment: str
    sentiment_score: float
    emotions: Dict[str, float]
    intent: Optional[str]
    intent_confidence: float
    keywords: List[str]
    entities: List[Dict[str, Any]]
    topics: List[str]
    action_items: List[Dict[str, Any]]
    questions: List[Dict[str, Any]]
    is_spam: bool
    spam_score: float
    is_phishing: bool
    phishing_indicators: List[str]
    security_score: float
    processing_time_ms: int


class EmailAnalysisRequest(BaseModel):
    """Schema para request de analise."""

    subject: Optional[str] = None
    body: str = Field(..., min_length=1)
    from_address: Optional[str] = None
    headers: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Response Schemas
# =============================================================================


class EmailResponseCreate(BaseModel):
    """Schema para criar resposta."""

    email_id: UUID
    subject: Optional[str] = Field(None, max_length=1000)
    body_text: str = Field(..., min_length=1)
    body_html: Optional[str] = None
    response_type: str = Field(default="manual")
    template_id: Optional[UUID] = None


class EmailResponseOut(BaseModel):
    """Schema de resposta para resposta de email."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email_id: UUID
    subject: Optional[str]
    body_text: str
    response_type: str
    is_draft: bool
    is_sent: bool
    sent_at: Optional[datetime]
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
    context: Dict[str, Any] = Field(default_factory=dict)


class GenerateReplyResponse(BaseModel):
    """Schema para resposta de geracao."""

    reply_text: str
    reply_html: Optional[str]
    confidence: float
    tone_used: str
    template_used: Optional[str]
    variables_filled: Dict[str, Any]
    suggestions: List[str]
    processing_time_ms: int


# =============================================================================
# Template Schemas
# =============================================================================


class EmailTemplateCreate(BaseModel):
    """Schema para criar template."""

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    subject_template: Optional[str] = Field(None, max_length=1000)
    body_template: str = Field(..., min_length=1)
    body_html_template: Optional[str] = None
    category: Optional[EmailCategoryEnum] = None
    language: str = Field(default="pt-BR")
    tags: List[str] = Field(default_factory=list)
    trigger_keywords: List[str] = Field(default_factory=list)
    trigger_intents: List[str] = Field(default_factory=list)
    variables: List[Dict[str, Any]] = Field(default_factory=list)


class EmailTemplateUpdate(BaseModel):
    """Schema para atualizar template."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    subject_template: Optional[str] = Field(None, max_length=1000)
    body_template: Optional[str] = None
    body_html_template: Optional[str] = None
    category: Optional[EmailCategoryEnum] = None
    tags: Optional[List[str]] = None
    trigger_keywords: Optional[List[str]] = None
    trigger_intents: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    """Schema de resposta para template."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: Optional[str]
    subject_template: Optional[str]
    body_template: str
    category: Optional[str]
    language: str
    tags: List[str]
    trigger_keywords: List[str]
    variables: List[Dict[str, Any]]
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
    description: Optional[str] = None
    priority: int = Field(default=0)
    conditions: List[Dict[str, Any]] = Field(..., min_length=1)
    condition_logic: str = Field(default="AND")
    actions: List[Dict[str, Any]] = Field(..., min_length=1)
    stop_processing: bool = False
    condominio_id: Optional[UUID] = None


class EmailRuleUpdate(BaseModel):
    """Schema para atualizar regra."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    condition_logic: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    stop_processing: Optional[bool] = None


class EmailRuleResponse(BaseModel):
    """Schema de resposta para regra."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    priority: int
    conditions: List[Dict[str, Any]]
    condition_logic: str
    actions: List[Dict[str, Any]]
    is_active: bool
    stop_processing: bool
    match_count: int
    last_match_at: Optional[datetime]
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
    emails_by_status: Dict[str, int]

    # Por categoria
    emails_by_category: Dict[str, int]

    # Por prioridade
    emails_by_priority: Dict[str, int]

    # Metricas
    avg_processing_time_ms: float
    avg_response_time_minutes: float
    auto_reply_rate: float
    classification_accuracy: float

    # Sentimento
    sentiment_distribution: Dict[str, int]

    # Templates
    top_templates: List[Dict[str, Any]]

    # Tendencias
    emails_trend: List[Dict[str, Any]]
    response_time_trend: List[Dict[str, Any]]
