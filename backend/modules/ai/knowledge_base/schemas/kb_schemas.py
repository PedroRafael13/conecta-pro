"""
Knowledge Base Schemas - Sprint 53.

Pydantic schemas para validacao e serializacao.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Enums (espelham os modelos)
# =============================================================================


class KnowledgeBaseStatusEnum(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    MAINTENANCE = "maintenance"


class KnowledgeBaseTypeEnum(StrEnum):
    GENERAL = "general"
    TECHNICAL = "technical"
    SUPPORT = "support"
    FAQ = "faq"
    PROCEDURES = "procedures"
    POLICIES = "policies"
    TRAINING = "training"
    PRODUCT = "product"
    INTERNAL = "internal"
    EXTERNAL = "external"


class KnowledgeBaseVisibilityEnum(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"


class ArticleStatusEnum(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    OUTDATED = "outdated"
    NEEDS_UPDATE = "needs_update"


class ArticleTypeEnum(StrEnum):
    HOW_TO = "how_to"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    REFERENCE = "reference"
    TROUBLESHOOTING = "troubleshooting"
    ANNOUNCEMENT = "announcement"
    POLICY = "policy"
    PROCEDURE = "procedure"
    BEST_PRACTICE = "best_practice"
    GLOSSARY = "glossary"


class FAQStatusEnum(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    NEEDS_UPDATE = "needs_update"


class FAQSourceEnum(StrEnum):
    MANUAL = "manual"
    IMPORTED = "imported"
    AI_GENERATED = "ai_generated"
    FROM_TICKET = "from_ticket"
    FROM_CHAT = "from_chat"
    FROM_CALL = "from_call"
    COMMUNITY = "community"


# =============================================================================
# Knowledge Base Schemas
# =============================================================================


class KnowledgeBaseCreate(BaseModel):
    """Schema para criar base de conhecimento."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str | None = Field(None, max_length=200)
    description: str | None = None
    kb_type: KnowledgeBaseTypeEnum = KnowledgeBaseTypeEnum.GENERAL
    visibility: KnowledgeBaseVisibilityEnum = KnowledgeBaseVisibilityEnum.INTERNAL
    default_language: str = Field(default="pt-BR", max_length=10)
    supported_languages: list[str] = Field(default=["pt-BR"])
    enable_ai_answers: bool = True
    enable_semantic_search: bool = True
    enable_auto_suggestions: bool = True
    enable_feedback: bool = True
    condominio_id: UUID | None = None
    settings: dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseUpdate(BaseModel):
    """Schema para atualizar base de conhecimento."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    kb_type: KnowledgeBaseTypeEnum | None = None
    status: KnowledgeBaseStatusEnum | None = None
    visibility: KnowledgeBaseVisibilityEnum | None = None
    default_language: str | None = None
    supported_languages: list[str] | None = None
    enable_ai_answers: bool | None = None
    enable_semantic_search: bool | None = None
    enable_auto_suggestions: bool | None = None
    enable_feedback: bool | None = None
    settings: dict[str, Any] | None = None
    custom_prompts: dict[str, Any] | None = None
    synonyms: dict[str, Any] | None = None


class KnowledgeBaseResponse(BaseModel):
    """Schema de resposta para base de conhecimento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    kb_type: str
    status: str
    visibility: str
    default_language: str
    supported_languages: list[str]
    enable_ai_answers: bool
    enable_semantic_search: bool
    enable_auto_suggestions: bool
    enable_feedback: bool
    index_status: str
    last_indexed_at: datetime | None
    total_articles: int
    total_faqs: int
    total_categories: int
    total_searches: int
    total_views: int
    average_rating: int
    condominio_id: UUID | None
    created_at: datetime
    updated_at: datetime | None
    ativo: bool


class KnowledgeBaseListResponse(BaseModel):
    """Schema para listagem de bases de conhecimento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    kb_type: str
    status: str
    total_articles: int
    total_faqs: int
    created_at: datetime


# =============================================================================
# Category Schemas
# =============================================================================


class KBCategoryCreate(BaseModel):
    """Schema para criar categoria."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str | None = Field(None, max_length=200)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    parent_id: UUID | None = None
    order: int = 0
    knowledge_base_id: UUID


class KBCategoryUpdate(BaseModel):
    """Schema para atualizar categoria."""

    name: str | None = Field(None, max_length=200)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    parent_id: UUID | None = None
    order: int | None = None


class KBCategoryResponse(BaseModel):
    """Schema de resposta para categoria."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    icon: str | None
    color: str | None
    parent_id: UUID | None
    level: int
    path: str | None
    order: int
    article_count: int
    faq_count: int
    knowledge_base_id: UUID
    created_at: datetime
    ativo: bool


# =============================================================================
# Article Schemas
# =============================================================================


class ArticleCreate(BaseModel):
    """Schema para criar artigo."""

    title: str = Field(..., min_length=1, max_length=500)
    slug: str | None = Field(None, max_length=500)
    subtitle: str | None = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    excerpt: str | None = Field(None, max_length=500)
    article_type: ArticleTypeEnum = ArticleTypeEnum.GUIDE
    tags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    language: str = Field(default="pt-BR", max_length=10)
    knowledge_base_id: UUID
    category_id: UUID | None = None
    related_articles: list[UUID] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArticleUpdate(BaseModel):
    """Schema para atualizar artigo."""

    title: str | None = Field(None, max_length=500)
    subtitle: str | None = Field(None, max_length=500)
    content: str | None = None
    excerpt: str | None = Field(None, max_length=500)
    article_type: ArticleTypeEnum | None = None
    status: ArticleStatusEnum | None = None
    tags: list[str] | None = None
    keywords: list[str] | None = None
    category_id: UUID | None = None
    related_articles: list[UUID] | None = None
    attachments: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None
    meta_title: str | None = None
    meta_description: str | None = None


class ArticleResponse(BaseModel):
    """Schema de resposta para artigo."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    subtitle: str | None
    content: str
    content_html: str | None
    summary: str | None
    excerpt: str | None
    article_type: str
    status: str
    priority: str
    tags: list[str]
    keywords: list[str]
    language: str
    version: int
    view_count: int
    helpful_count: int
    not_helpful_count: int
    average_rating: float
    knowledge_base_id: UUID
    category_id: UUID | None
    author_id: UUID | None
    published_at: datetime | None
    related_articles: list[UUID]
    attachments: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime | None
    ativo: bool


class ArticleListResponse(BaseModel):
    """Schema para listagem de artigos."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    article_type: str
    status: str
    view_count: int
    average_rating: float
    category_id: UUID | None
    published_at: datetime | None
    created_at: datetime


class ArticleSearchResult(BaseModel):
    """Schema para resultado de busca de artigo."""

    id: UUID
    title: str
    excerpt: str | None
    article_type: str
    relevance_score: float
    matched_keywords: list[str]
    highlights: list[str]


# =============================================================================
# FAQ Schemas
# =============================================================================


class FAQCreate(BaseModel):
    """Schema para criar FAQ."""

    question: str = Field(..., min_length=5, max_length=1000)
    answer: str = Field(..., min_length=1)
    answer_short: str | None = Field(None, max_length=500)
    question_variations: list[str] = Field(default_factory=list)
    source: FAQSourceEnum = FAQSourceEnum.MANUAL
    tags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    language: str = Field(default="pt-BR", max_length=10)
    order: int = 0
    priority: int = 0
    knowledge_base_id: UUID
    category_id: UUID | None = None
    related_article_id: UUID | None = None
    applicable_scenarios: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FAQUpdate(BaseModel):
    """Schema para atualizar FAQ."""

    question: str | None = Field(None, max_length=1000)
    answer: str | None = None
    answer_short: str | None = Field(None, max_length=500)
    question_variations: list[str] | None = None
    status: FAQStatusEnum | None = None
    tags: list[str] | None = None
    keywords: list[str] | None = None
    order: int | None = None
    priority: int | None = None
    category_id: UUID | None = None
    related_article_id: UUID | None = None
    applicable_scenarios: list[str] | None = None
    metadata: dict[str, Any] | None = None


class FAQResponse(BaseModel):
    """Schema de resposta para FAQ."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    answer: str
    answer_short: str | None
    question_variations: list[str]
    status: str
    source: str
    tags: list[str]
    keywords: list[str]
    language: str
    order: int
    priority: int
    view_count: int
    helpful_count: int
    not_helpful_count: int
    helpfulness_score: float
    knowledge_base_id: UUID
    category_id: UUID | None
    related_article_id: UUID | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    ativo: bool


class FAQListResponse(BaseModel):
    """Schema para listagem de FAQs."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    status: str
    view_count: int
    helpfulness_score: float
    category_id: UUID | None
    created_at: datetime


class FAQSearchResult(BaseModel):
    """Schema para resultado de busca de FAQ."""

    id: UUID
    question: str
    answer_short: str | None
    relevance_score: float
    confidence: float
    matched_variation: str | None


# =============================================================================
# QA Session Schemas
# =============================================================================


class QAQuestionRequest(BaseModel):
    """Schema para fazer uma pergunta."""

    question: str = Field(..., min_length=2, max_length=2000)
    session_id: UUID | None = None
    knowledge_base_id: UUID | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    max_results: int = Field(default=5, ge=1, le=20)
    include_articles: bool = True
    include_faqs: bool = True
    language: str = Field(default="pt-BR")


class QAAnswerResponse(BaseModel):
    """Schema de resposta para pergunta."""

    session_id: UUID
    interaction_id: UUID
    question: str
    answer: str | None
    answer_formatted: str | None
    response_type: str
    confidence_score: float
    sources: list[dict[str, Any]]
    matched_faqs: list[FAQSearchResult]
    matched_articles: list[ArticleSearchResult]
    suggestions: list[str]
    follow_up_questions: list[str]
    processing_time_ms: int


class QAFeedbackRequest(BaseModel):
    """Schema para feedback de interacao."""

    interaction_id: UUID
    is_helpful: bool | None = None
    rating: int | None = Field(None, ge=1, le=5)
    feedback_text: str | None = Field(None, max_length=1000)


class QASessionResponse(BaseModel):
    """Schema de resposta para sessao Q&A."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_key: str
    status: str
    source: str
    interaction_count: int
    question_count: int
    answered_count: int
    average_confidence: float
    resolved: bool
    escalated: bool
    overall_rating: int | None
    started_at: datetime
    ended_at: datetime | None
    total_duration_seconds: int


class QAInteractionResponse(BaseModel):
    """Schema de resposta para interacao Q&A."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    interaction_type: str
    question: str
    response_type: str | None
    response: str | None
    confidence_score: float
    is_helpful: bool | None
    rating: int | None
    created_at: datetime


# =============================================================================
# Search Schemas
# =============================================================================


class SemanticSearchRequest(BaseModel):
    """Schema para busca semantica."""

    query: str = Field(..., min_length=2, max_length=500)
    knowledge_base_id: UUID | None = None
    search_type: str = Field(default="hybrid")  # semantic, keyword, hybrid
    max_results: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)
    include_articles: bool = True
    include_faqs: bool = True
    category_ids: list[UUID] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    language: str = Field(default="pt-BR")


class SemanticSearchResponse(BaseModel):
    """Schema de resposta para busca semantica."""

    query: str
    total_results: int
    articles: list[ArticleSearchResult]
    faqs: list[FAQSearchResult]
    suggestions: list[str]
    related_queries: list[str]
    processing_time_ms: int


# =============================================================================
# Dashboard Schemas
# =============================================================================


class KnowledgeBaseDashboard(BaseModel):
    """Schema para dashboard da base de conhecimento."""

    # Totais
    total_knowledge_bases: int
    total_articles: int
    total_faqs: int
    total_categories: int

    # Estatisticas
    total_searches: int
    total_views: int
    total_qa_sessions: int
    total_questions_answered: int

    # Metricas
    average_confidence: float
    average_helpful_rate: float
    average_response_time_ms: int

    # Por status
    articles_by_status: dict[str, int]
    faqs_by_status: dict[str, int]

    # Top items
    top_articles: list[ArticleListResponse]
    top_faqs: list[FAQListResponse]
    recent_questions: list[str]

    # Tendencias
    searches_trend: list[dict[str, Any]]
    questions_trend: list[dict[str, Any]]
