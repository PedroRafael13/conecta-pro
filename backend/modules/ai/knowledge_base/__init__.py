"""
AI Knowledge Base Module - Sprint 53.

Sistema de base de conhecimento com busca semantica e Q&A.

Funcionalidades:
- Bases de conhecimento organizacionais
- Artigos com versionamento e busca
- FAQs com variacoes de perguntas
- Busca semantica com embeddings
- Motor de Q&A com IA
- Geracao automatica de conteudo
- Dashboard de metricas
"""

from modules.ai.knowledge_base.controllers import kb_router
from modules.ai.knowledge_base.models import (
    FAQ,
    Article,
    ArticleFeedback,
    ArticlePriorityEnum,
    ArticleStatusEnum,
    ArticleTypeEnum,
    ArticleVersion,
    FAQFeedback,
    FAQSourceEnum,
    FAQStatusEnum,
    KBCategory,
    KnowledgeBase,
    KnowledgeBaseStatusEnum,
    KnowledgeBaseTypeEnum,
    KnowledgeBaseVisibilityEnum,
    QAInteraction,
    QAInteractionTypeEnum,
    QAResponseTypeEnum,
    QASession,
    QASessionStatusEnum,
    QASourceEnum,
    QASuggestion,
)
from modules.ai.knowledge_base.repositories import KnowledgeBaseRepository
from modules.ai.knowledge_base.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleSearchResult,
    ArticleUpdate,
    FAQCreate,
    FAQListResponse,
    FAQResponse,
    FAQSearchResult,
    FAQUpdate,
    KBCategoryCreate,
    KBCategoryResponse,
    KBCategoryUpdate,
    KnowledgeBaseCreate,
    KnowledgeBaseDashboard,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    QAAnswerResponse,
    QAFeedbackRequest,
    QAInteractionResponse,
    QAQuestionRequest,
    QASessionResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from modules.ai.knowledge_base.services import (
    ArticleGenerator,
    QAEngine,
    SemanticSearchEngine,
)

__all__ = [
    # Models
    "KnowledgeBase",
    "KnowledgeBaseStatusEnum",
    "KnowledgeBaseTypeEnum",
    "KnowledgeBaseVisibilityEnum",
    "KBCategory",
    "Article",
    "ArticleStatusEnum",
    "ArticleTypeEnum",
    "ArticlePriorityEnum",
    "ArticleVersion",
    "ArticleFeedback",
    "FAQ",
    "FAQStatusEnum",
    "FAQSourceEnum",
    "FAQFeedback",
    "QASession",
    "QASessionStatusEnum",
    "QASourceEnum",
    "QAInteraction",
    "QAInteractionTypeEnum",
    "QAResponseTypeEnum",
    "QASuggestion",
    # Schemas
    "KnowledgeBaseCreate",
    "KnowledgeBaseUpdate",
    "KnowledgeBaseResponse",
    "KnowledgeBaseListResponse",
    "KBCategoryCreate",
    "KBCategoryUpdate",
    "KBCategoryResponse",
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleResponse",
    "ArticleListResponse",
    "ArticleSearchResult",
    "FAQCreate",
    "FAQUpdate",
    "FAQResponse",
    "FAQListResponse",
    "FAQSearchResult",
    "QAQuestionRequest",
    "QAAnswerResponse",
    "QAFeedbackRequest",
    "QASessionResponse",
    "QAInteractionResponse",
    "SemanticSearchRequest",
    "SemanticSearchResponse",
    "KnowledgeBaseDashboard",
    # Repository
    "KnowledgeBaseRepository",
    # Services
    "SemanticSearchEngine",
    "QAEngine",
    "ArticleGenerator",
    # Router
    "kb_router",
]
