"""
AI Knowledge Base Schemas - Sprint 53.
"""

from modules.ai.knowledge_base.schemas.kb_schemas import (
    # Enums
    KnowledgeBaseStatusEnum,
    KnowledgeBaseTypeEnum,
    KnowledgeBaseVisibilityEnum,
    ArticleStatusEnum,
    ArticleTypeEnum,
    FAQStatusEnum,
    FAQSourceEnum,
    # Knowledge Base
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    # Category
    KBCategoryCreate,
    KBCategoryUpdate,
    KBCategoryResponse,
    # Article
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticleSearchResult,
    # FAQ
    FAQCreate,
    FAQUpdate,
    FAQResponse,
    FAQListResponse,
    FAQSearchResult,
    # QA
    QAQuestionRequest,
    QAAnswerResponse,
    QAFeedbackRequest,
    QASessionResponse,
    QAInteractionResponse,
    # Search
    SemanticSearchRequest,
    SemanticSearchResponse,
    # Dashboard
    KnowledgeBaseDashboard,
)

__all__ = [
    # Enums
    "KnowledgeBaseStatusEnum",
    "KnowledgeBaseTypeEnum",
    "KnowledgeBaseVisibilityEnum",
    "ArticleStatusEnum",
    "ArticleTypeEnum",
    "FAQStatusEnum",
    "FAQSourceEnum",
    # Knowledge Base
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate",
    "KnowledgeBaseResponse",
    "KnowledgeBaseListResponse",
    # Category
    "KBCategoryCreate",
    "KBCategoryUpdate",
    "KBCategoryResponse",
    # Article
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleResponse",
    "ArticleListResponse",
    "ArticleSearchResult",
    # FAQ
    "FAQCreate",
    "FAQUpdate",
    "FAQResponse",
    "FAQListResponse",
    "FAQSearchResult",
    # QA
    "QAQuestionRequest",
    "QAAnswerResponse",
    "QAFeedbackRequest",
    "QASessionResponse",
    "QAInteractionResponse",
    # Search
    "SemanticSearchRequest",
    "SemanticSearchResponse",
    # Dashboard
    "KnowledgeBaseDashboard",
]
