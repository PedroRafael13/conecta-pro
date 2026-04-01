"""
Knowledge Base Model - Sprint 53.

Modelo para bases de conhecimento organizacional.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class KnowledgeBaseStatusEnum(StrEnum):
    """Status da base de conhecimento."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    MAINTENANCE = "maintenance"


class KnowledgeBaseTypeEnum(StrEnum):
    """Tipo de base de conhecimento."""

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
    """Visibilidade da base de conhecimento."""

    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"


class KnowledgeBase(Base):
    """
    Modelo de Base de Conhecimento.

    Representa uma base de conhecimento que agrupa artigos,
    FAQs e documentação relacionada.
    """

    __tablename__ = "ai_knowledge_bases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Classificacao
    kb_type = Column(
        SQLEnum(KnowledgeBaseTypeEnum, name="knowledge_base_type_enum"),
        default=KnowledgeBaseTypeEnum.GENERAL,
        nullable=False,
    )
    status = Column(
        SQLEnum(KnowledgeBaseStatusEnum, name="knowledge_base_status_enum"),
        default=KnowledgeBaseStatusEnum.DRAFT,
        nullable=False,
    )
    visibility = Column(
        SQLEnum(KnowledgeBaseVisibilityEnum, name="knowledge_base_visibility_enum"),
        default=KnowledgeBaseVisibilityEnum.INTERNAL,
        nullable=False,
    )

    # Configuracoes
    default_language = Column(String(10), default="pt-BR")
    supported_languages = Column(ARRAY(String), default=["pt-BR"])
    enable_ai_answers = Column(Boolean, default=True)
    enable_semantic_search = Column(Boolean, default=True)
    enable_auto_suggestions = Column(Boolean, default=True)
    enable_feedback = Column(Boolean, default=True)

    # Indexacao
    index_status = Column(String(50), default="pending")
    last_indexed_at = Column(DateTime, nullable=True)
    total_indexed_articles = Column(Integer, default=0)
    total_indexed_faqs = Column(Integer, default=0)
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    vector_dimension = Column(Integer, default=384)

    # Estatisticas
    total_articles = Column(Integer, default=0)
    total_faqs = Column(Integer, default=0)
    total_categories = Column(Integer, default=0)
    total_searches = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    average_rating = Column(Integer, default=0)  # 0-100

    # Acesso
    allowed_roles = Column(ARRAY(String), default=[])
    allowed_users = Column(ARRAY(UUID(as_uuid=True)), default=[])
    allowed_condominios = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Configuracoes avancadas
    settings = Column(JSONB, default={})
    custom_prompts = Column(JSONB, default={})
    synonyms = Column(JSONB, default={})
    stopwords = Column(ARRAY(String), default=[])

    # Relacionamentos
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=True,
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    articles = relationship(
        "Article",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    faqs = relationship(
        "FAQ",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    categories = relationship(
        "KBCategory",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeBase {self.name} ({self.kb_type})>"


class KBCategory(Base):
    """
    Categoria da Base de Conhecimento.

    Organiza artigos e FAQs em categorias hierarquicas.
    """

    __tablename__ = "ai_kb_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(20), nullable=True)

    # Hierarquia
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_categories.id"),
        nullable=True,
    )
    level = Column(Integer, default=0)
    path = Column(String(500), nullable=True)  # /parent/child/grandchild
    order = Column(Integer, default=0)

    # Estatisticas
    article_count = Column(Integer, default=0)
    faq_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    # Relacionamentos
    knowledge_base_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_knowledge_bases.id"),
        nullable=False,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="categories")
    parent = relationship("KBCategory", remote_side=[id], backref="children")  # noqa: A003

    def __repr__(self) -> str:
        return f"<KBCategory {self.name}>"
