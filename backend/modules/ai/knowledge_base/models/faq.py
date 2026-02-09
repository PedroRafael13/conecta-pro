"""
FAQ Model - Sprint 53.

Modelo para perguntas frequentes da base de conhecimento.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class FAQStatusEnum(StrEnum):
    """Status da FAQ."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    NEEDS_UPDATE = "needs_update"


class FAQSourceEnum(StrEnum):
    """Origem da FAQ."""

    MANUAL = "manual"
    IMPORTED = "imported"
    AI_GENERATED = "ai_generated"
    FROM_TICKET = "from_ticket"
    FROM_CHAT = "from_chat"
    FROM_CALL = "from_call"
    COMMUNITY = "community"


class FAQ(Base):
    """
    Modelo de FAQ.

    Representa uma pergunta frequente com resposta
    na base de conhecimento.
    """

    __tablename__ = "ai_kb_faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Pergunta
    question = Column(Text, nullable=False)
    question_normalized = Column(Text, nullable=True)  # Versao normalizada
    question_variations = Column(ARRAY(String), default=[])  # Variacoes

    # Resposta
    answer = Column(Text, nullable=False)
    answer_html = Column(Text, nullable=True)
    answer_short = Column(String(500), nullable=True)  # Resposta curta

    # Classificacao
    status = Column(
        SQLEnum(FAQStatusEnum, name="faq_status_enum"),
        default=FAQStatusEnum.DRAFT,
        nullable=False,
    )
    source = Column(
        SQLEnum(FAQSourceEnum, name="faq_source_enum"),
        default=FAQSourceEnum.MANUAL,
        nullable=False,
    )

    # Organizacao
    tags = Column(ARRAY(String), default=[])
    keywords = Column(ARRAY(String), default=[])
    language = Column(String(10), default="pt-BR")
    order = Column(Integer, default=0)  # Ordem de exibicao
    priority = Column(Integer, default=0)  # Prioridade nos resultados

    # Busca
    search_vector = Column(TSVECTOR, nullable=True)

    # Embeddings para busca semantica
    question_embedding = Column(ARRAY(Float), nullable=True)
    answer_embedding = Column(ARRAY(Float), nullable=True)
    embedding_model = Column(String(100), nullable=True)
    embedding_updated_at = Column(DateTime, nullable=True)

    # Estatisticas
    view_count = Column(Integer, default=0)
    search_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    helpfulness_score = Column(Float, default=0.0)  # 0-1

    # Uso em IA
    ai_used_count = Column(Integer, default=0)  # Vezes usada em respostas IA
    ai_confidence_avg = Column(Float, default=0.0)  # Confianca media
    last_ai_used_at = Column(DateTime, nullable=True)

    # Contexto
    applicable_scenarios = Column(ARRAY(String), default=[])
    preconditions = Column(Text, nullable=True)
    related_questions = Column(ARRAY(UUID(as_uuid=True)), default=[])

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
    related_article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_articles.id"),
        nullable=True,
    )
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Origem (quando criada de ticket/chat)
    source_ticket_id = Column(UUID(as_uuid=True), nullable=True)
    source_chat_id = Column(UUID(as_uuid=True), nullable=True)
    source_call_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadados
    extra_metadata = Column(JSONB, default={})

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="faqs")
    feedback = relationship(
        "FAQFeedback",
        back_populates="faq",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<FAQ {self.question[:50]}>"


class FAQFeedback(Base):
    """
    Feedback da FAQ.

    Armazena avaliacoes dos usuarios sobre a FAQ.
    """

    __tablename__ = "ai_kb_faq_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Avaliacao
    is_helpful = Column(Boolean, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5
    comment = Column(Text, nullable=True)
    improvement_suggestion = Column(Text, nullable=True)

    # Contexto
    search_query = Column(String(500), nullable=True)
    matched_confidence = Column(Float, nullable=True)
    was_ai_response = Column(Boolean, default=False)

    # Relacionamentos
    faq_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_faqs.id"),
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
    faq = relationship("FAQ", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<FAQFeedback {self.faq_id}>"
