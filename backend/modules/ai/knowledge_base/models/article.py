"""
Article Model - Sprint 53.

Modelo para artigos da base de conhecimento.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Integer,
    Float,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.models.base import Base


class ArticleStatusEnum(str, enum.Enum):
    """Status do artigo."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    OUTDATED = "outdated"
    NEEDS_UPDATE = "needs_update"


class ArticleTypeEnum(str, enum.Enum):
    """Tipo de artigo."""

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


class ArticlePriorityEnum(str, enum.Enum):
    """Prioridade do artigo nos resultados."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    FEATURED = "featured"


class Article(Base):
    """
    Modelo de Artigo.

    Representa um artigo na base de conhecimento com
    suporte a versionamento e busca semantica.
    """

    __tablename__ = "ai_kb_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False)
    subtitle = Column(String(500), nullable=True)

    # Conteudo
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)  # Versao renderizada
    content_plain = Column(Text, nullable=True)  # Versao texto puro
    summary = Column(Text, nullable=True)  # Resumo automatico
    excerpt = Column(String(500), nullable=True)  # Trecho para preview

    # Classificacao
    article_type = Column(
        SQLEnum(ArticleTypeEnum, name="article_type_enum"),
        default=ArticleTypeEnum.GUIDE,
        nullable=False,
    )
    status = Column(
        SQLEnum(ArticleStatusEnum, name="article_status_enum"),
        default=ArticleStatusEnum.DRAFT,
        nullable=False,
    )
    priority = Column(
        SQLEnum(ArticlePriorityEnum, name="article_priority_enum"),
        default=ArticlePriorityEnum.NORMAL,
        nullable=False,
    )

    # Organizacao
    tags = Column(ARRAY(String), default=[])
    keywords = Column(ARRAY(String), default=[])
    related_topics = Column(ARRAY(String), default=[])
    language = Column(String(10), default="pt-BR")

    # SEO e Busca
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)
    search_vector = Column(TSVECTOR, nullable=True)

    # Embeddings para busca semantica
    embedding = Column(ARRAY(Float), nullable=True)
    embedding_model = Column(String(100), nullable=True)
    embedding_updated_at = Column(DateTime, nullable=True)

    # Versionamento
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    parent_article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_articles.id"),
        nullable=True,
    )

    # Estatisticas
    view_count = Column(Integer, default=0)
    search_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    rating_sum = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    average_time_on_page = Column(Integer, default=0)  # segundos

    # Datas
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    review_at = Column(DateTime, nullable=True)
    last_viewed_at = Column(DateTime, nullable=True)

    # Relacionamentos
    knowledge_base_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_knowledge_bases.id"),
        nullable=False,
    )
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_categories.id"),
        nullable=True,
    )
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    reviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Conteudo relacionado
    related_articles = Column(ARRAY(UUID(as_uuid=True)), default=[])
    related_faqs = Column(ARRAY(UUID(as_uuid=True)), default=[])
    attachments = Column(JSONB, default=[])  # [{name, url, type, size}]
    media = Column(JSONB, default=[])  # [{type, url, caption}]

    # Metadados
    extra_metadata = Column(JSONB, default={})
    custom_fields = Column(JSONB, default={})

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="articles")
    versions = relationship(
        "ArticleVersion",
        back_populates="article",
        cascade="all, delete-orphan",
    )
    feedback = relationship(
        "ArticleFeedback",
        back_populates="article",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Article {self.title[:50]}>"


class ArticleVersion(Base):
    """
    Versao do Artigo.

    Armazena versoes anteriores do artigo para historico.
    """

    __tablename__ = "ai_kb_article_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    version_number = Column(Integer, nullable=False)
    version_label = Column(String(100), nullable=True)  # ex: "v1.0", "Draft 2"

    # Conteudo versionado
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Mudancas
    change_summary = Column(Text, nullable=True)
    changed_fields = Column(ARRAY(String), default=[])

    # Relacionamentos
    article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_articles.id"),
        nullable=False,
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="versions")

    def __repr__(self) -> str:
        return f"<ArticleVersion {self.article_id} v{self.version_number}>"


class ArticleFeedback(Base):
    """
    Feedback do Artigo.

    Armazena avaliacoes e comentarios dos usuarios.
    """

    __tablename__ = "ai_kb_article_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Avaliacao
    is_helpful = Column(Boolean, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)

    # Contexto
    search_query = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Relacionamentos
    article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_articles.id"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<ArticleFeedback {self.article_id}>"
