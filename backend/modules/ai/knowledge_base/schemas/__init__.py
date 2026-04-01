"""
AI Knowledge Base Schemas - Sprint 53.
"""

from modules.ai.knowledge_base.schemas.kb_schemas import (
    # Article
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleSearchResult,
    ArticleStatusEnum,
    ArticleTypeEnum,
    ArticleUpdate,
    # FAQ
    FAQCreate,
    FAQListResponse,
    FAQResponse,
    FAQSearchResult,
    FAQSourceEnum,
    FAQStatusEnum,
    FAQUpdate,
    # Category
    KBCategoryCreate,
    KBCategoryResponse,
    KBCategoryUpdate,
    # Knowledge Base
    KnowledgeBaseCreate,
    # Dashboard
    KnowledgeBaseDashboard,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
    # Enums
    KnowledgeBaseStatusEnum,
    KnowledgeBaseTypeEnum,
    KnowledgeBaseUpdate,
    KnowledgeBaseVisibilityEnum,
    QAAnswerResponse,
    QAFeedbackRequest,
    QAInteractionResponse,
    # QA
    QAQuestionRequest,
    QASessionResponse,
    # Search
    SemanticSearchRequest,
    SemanticSearchResponse,
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
