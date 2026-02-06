"""
Knowledge Base Schemas - Sprint 53.

Pydantic schemas para validacao e serializacao.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# =============================================================================
# Enums (espelham os modelos)
# =============================================================================


class KnowledgeBaseStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    MAINTENANCE = "maintenance"


class KnowledgeBaseTypeEnum(str, Enum):
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


class KnowledgeBaseVisibilityEnum(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"


class ArticleStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    OUTDATED = "outdated"
    NEEDS_UPDATE = "needs_update"


class ArticleTypeEnum(str, Enum):
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


class FAQStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    NEEDS_UPDATE = "needs_update"


class FAQSourceEnum(str, Enum):
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
    slug: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    kb_type: KnowledgeBaseTypeEnum = KnowledgeBaseTypeEnum.GENERAL
    visibility: KnowledgeBaseVisibilityEnum = KnowledgeBaseVisibilityEnum.INTERNAL
    default_language: str = Field(default="pt-BR", max_length=10)
    supported_languages: List[str] = Field(default=["pt-BR"])
    enable_ai_answers: bool = True
    enable_semantic_search: bool = True
    enable_auto_suggestions: bool = True
    enable_feedback: bool = True
    condominio_id: Optional[UUID] = None
    settings: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeBaseUpdate(BaseModel):
    """Schema para atualizar base de conhecimento."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    kb_type: Optional[KnowledgeBaseTypeEnum] = None
    status: Optional[KnowledgeBaseStatusEnum] = None
    visibility: Optional[KnowledgeBaseVisibilityEnum] = None
    default_language: Optional[str] = None
    supported_languages: Optional[List[str]] = None
    enable_ai_answers: Optional[bool] = None
    enable_semantic_search: Optional[bool] = None
    enable_auto_suggestions: Optional[bool] = None
    enable_feedback: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    custom_prompts: Optional[Dict[str, Any]] = None
    synonyms: Optional[Dict[str, Any]] = None


class KnowledgeBaseResponse(BaseModel):
    """Schema de resposta para base de conhecimento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str]
    kb_type: str
    status: str
    visibility: str
    default_language: str
    supported_languages: List[str]
    enable_ai_answers: bool
    enable_semantic_search: bool
    enable_auto_suggestions: bool
    enable_feedback: bool
    index_status: str
    last_indexed_at: Optional[datetime]
    total_articles: int
    total_faqs: int
    total_categories: int
    total_searches: int
    total_views: int
    average_rating: int
    condominio_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
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
    slug: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[UUID] = None
    order: int = 0
    knowledge_base_id: UUID


class KBCategoryUpdate(BaseModel):
    """Schema para atualizar categoria."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[UUID] = None
    order: Optional[int] = None


class KBCategoryResponse(BaseModel):
    """Schema de resposta para categoria."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    parent_id: Optional[UUID]
    level: int
    path: Optional[str]
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
    slug: Optional[str] = Field(None, max_length=500)
    subtitle: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    article_type: ArticleTypeEnum = ArticleTypeEnum.GUIDE
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    language: str = Field(default="pt-BR", max_length=10)
    knowledge_base_id: UUID
    category_id: Optional[UUID] = None
    related_articles: List[UUID] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArticleUpdate(BaseModel):
    """Schema para atualizar artigo."""

    title: Optional[str] = Field(None, max_length=500)
    subtitle: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    excerpt: Optional[str] = Field(None, max_length=500)
    article_type: Optional[ArticleTypeEnum] = None
    status: Optional[ArticleStatusEnum] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    category_id: Optional[UUID] = None
    related_articles: Optional[List[UUID]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ArticleResponse(BaseModel):
    """Schema de resposta para artigo."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    subtitle: Optional[str]
    content: str
    content_html: Optional[str]
    summary: Optional[str]
    excerpt: Optional[str]
    article_type: str
    status: str
    priority: str
    tags: List[str]
    keywords: List[str]
    language: str
    version: int
    view_count: int
    helpful_count: int
    not_helpful_count: int
    average_rating: float
    knowledge_base_id: UUID
    category_id: Optional[UUID]
    author_id: Optional[UUID]
    published_at: Optional[datetime]
    related_articles: List[UUID]
    attachments: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
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
    category_id: Optional[UUID]
    published_at: Optional[datetime]
    created_at: datetime


class ArticleSearchResult(BaseModel):
    """Schema para resultado de busca de artigo."""

    id: UUID
    title: str
    excerpt: Optional[str]
    article_type: str
    relevance_score: float
    matched_keywords: List[str]
    highlights: List[str]


# =============================================================================
# FAQ Schemas
# =============================================================================


class FAQCreate(BaseModel):
    """Schema para criar FAQ."""

    question: str = Field(..., min_length=5, max_length=1000)
    answer: str = Field(..., min_length=1)
    answer_short: Optional[str] = Field(None, max_length=500)
    question_variations: List[str] = Field(default_factory=list)
    source: FAQSourceEnum = FAQSourceEnum.MANUAL
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    language: str = Field(default="pt-BR", max_length=10)
    order: int = 0
    priority: int = 0
    knowledge_base_id: UUID
    category_id: Optional[UUID] = None
    related_article_id: Optional[UUID] = None
    applicable_scenarios: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FAQUpdate(BaseModel):
    """Schema para atualizar FAQ."""

    question: Optional[str] = Field(None, max_length=1000)
    answer: Optional[str] = None
    answer_short: Optional[str] = Field(None, max_length=500)
    question_variations: Optional[List[str]] = None
    status: Optional[FAQStatusEnum] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    order: Optional[int] = None
    priority: Optional[int] = None
    category_id: Optional[UUID] = None
    related_article_id: Optional[UUID] = None
    applicable_scenarios: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class FAQResponse(BaseModel):
    """Schema de resposta para FAQ."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    answer: str
    answer_short: Optional[str]
    question_variations: List[str]
    status: str
    source: str
    tags: List[str]
    keywords: List[str]
    language: str
    order: int
    priority: int
    view_count: int
    helpful_count: int
    not_helpful_count: int
    helpfulness_score: float
    knowledge_base_id: UUID
    category_id: Optional[UUID]
    related_article_id: Optional[UUID]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    ativo: bool


class FAQListResponse(BaseModel):
    """Schema para listagem de FAQs."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    status: str
    view_count: int
    helpfulness_score: float
    category_id: Optional[UUID]
    created_at: datetime


class FAQSearchResult(BaseModel):
    """Schema para resultado de busca de FAQ."""

    id: UUID
    question: str
    answer_short: Optional[str]
    relevance_score: float
    confidence: float
    matched_variation: Optional[str]


# =============================================================================
# QA Session Schemas
# =============================================================================


class QAQuestionRequest(BaseModel):
    """Schema para fazer uma pergunta."""

    question: str = Field(..., min_length=2, max_length=2000)
    session_id: Optional[UUID] = None
    knowledge_base_id: Optional[UUID] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    max_results: int = Field(default=5, ge=1, le=20)
    include_articles: bool = True
    include_faqs: bool = True
    language: str = Field(default="pt-BR")


class QAAnswerResponse(BaseModel):
    """Schema de resposta para pergunta."""

    session_id: UUID
    interaction_id: UUID
    question: str
    answer: Optional[str]
    answer_formatted: Optional[str]
    response_type: str
    confidence_score: float
    sources: List[Dict[str, Any]]
    matched_faqs: List[FAQSearchResult]
    matched_articles: List[ArticleSearchResult]
    suggestions: List[str]
    follow_up_questions: List[str]
    processing_time_ms: int


class QAFeedbackRequest(BaseModel):
    """Schema para feedback de interacao."""

    interaction_id: UUID
    is_helpful: Optional[bool] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = Field(None, max_length=1000)


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
    overall_rating: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]
    total_duration_seconds: int


class QAInteractionResponse(BaseModel):
    """Schema de resposta para interacao Q&A."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    interaction_type: str
    question: str
    response_type: Optional[str]
    response: Optional[str]
    confidence_score: float
    is_helpful: Optional[bool]
    rating: Optional[int]
    created_at: datetime


# =============================================================================
# Search Schemas
# =============================================================================


class SemanticSearchRequest(BaseModel):
    """Schema para busca semantica."""

    query: str = Field(..., min_length=2, max_length=500)
    knowledge_base_id: Optional[UUID] = None
    search_type: str = Field(default="hybrid")  # semantic, keyword, hybrid
    max_results: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)
    include_articles: bool = True
    include_faqs: bool = True
    category_ids: List[UUID] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    language: str = Field(default="pt-BR")


class SemanticSearchResponse(BaseModel):
    """Schema de resposta para busca semantica."""

    query: str
    total_results: int
    articles: List[ArticleSearchResult]
    faqs: List[FAQSearchResult]
    suggestions: List[str]
    related_queries: List[str]
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
    articles_by_status: Dict[str, int]
    faqs_by_status: Dict[str, int]

    # Top items
    top_articles: List[ArticleListResponse]
    top_faqs: List[FAQListResponse]
    recent_questions: List[str]

    # Tendencias
    searches_trend: List[Dict[str, Any]]
    questions_trend: List[Dict[str, Any]]
