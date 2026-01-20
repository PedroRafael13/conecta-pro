"""
QA Session Model - Sprint 53.

Modelo para sessoes de perguntas e respostas com IA.
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
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from core.models.base import Base


class QASessionStatusEnum(str, enum.Enum):
    """Status da sessao Q&A."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ESCALATED = "escalated"


class QASourceEnum(str, enum.Enum):
    """Origem da sessao Q&A."""

    WEB_WIDGET = "web_widget"
    MOBILE_APP = "mobile_app"
    API = "api"
    CHAT = "chat"
    VOICE = "voice"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    INTERNAL = "internal"


class QAInteractionTypeEnum(str, enum.Enum):
    """Tipo de interacao."""

    QUESTION = "question"
    CLARIFICATION = "clarification"
    FOLLOW_UP = "follow_up"
    FEEDBACK = "feedback"
    ESCALATION = "escalation"


class QAResponseTypeEnum(str, enum.Enum):
    """Tipo de resposta."""

    DIRECT_ANSWER = "direct_answer"
    ARTICLE_MATCH = "article_match"
    FAQ_MATCH = "faq_match"
    GENERATED = "generated"
    NO_ANSWER = "no_answer"
    ESCALATED = "escalated"
    CLARIFICATION_NEEDED = "clarification_needed"


class QASession(Base):
    """
    Modelo de Sessao Q&A.

    Representa uma sessao de perguntas e respostas
    com o sistema de IA.
    """

    __tablename__ = "ai_qa_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    session_key = Column(String(100), unique=True, nullable=False)

    # Status
    status = Column(
        SQLEnum(QASessionStatusEnum, name="qa_session_status_enum"),
        default=QASessionStatusEnum.ACTIVE,
        nullable=False,
    )
    source = Column(
        SQLEnum(QASourceEnum, name="qa_source_enum"),
        default=QASourceEnum.WEB_WIDGET,
        nullable=False,
    )

    # Contexto
    context = Column(JSONB, default={})  # Contexto da sessao
    user_context = Column(JSONB, default={})  # Info do usuario
    page_context = Column(JSONB, default={})  # Pagina de origem

    # Estatisticas da sessao
    interaction_count = Column(Integer, default=0)
    question_count = Column(Integer, default=0)
    answered_count = Column(Integer, default=0)
    unanswered_count = Column(Integer, default=0)
    average_confidence = Column(Float, default=0.0)
    average_response_time_ms = Column(Integer, default=0)

    # Feedback
    overall_rating = Column(Integer, nullable=True)  # 1-5
    overall_helpful = Column(Boolean, nullable=True)
    feedback_comment = Column(Text, nullable=True)

    # Resolucao
    resolved = Column(Boolean, default=False)
    resolution_type = Column(String(50), nullable=True)
    escalated = Column(Boolean, default=False)
    escalated_to = Column(String(100), nullable=True)
    escalation_reason = Column(Text, nullable=True)

    # Tempos
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    last_interaction_at = Column(DateTime, nullable=True)
    total_duration_seconds = Column(Integer, default=0)

    # Relacionamentos
    knowledge_base_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_knowledge_bases.id"),
        nullable=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=True,
    )

    # Cliente info (quando nao logado)
    client_id = Column(String(100), nullable=True)
    client_ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Metadados
    extra_metadata = Column(JSONB, default={})

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    interactions = relationship(
        "QAInteraction",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="QAInteraction.created_at",
    )

    def __repr__(self) -> str:
        return f"<QASession {self.session_key}>"


class QAInteraction(Base):
    """
    Modelo de Interacao Q&A.

    Representa uma interacao individual (pergunta/resposta)
    dentro de uma sessao.
    """

    __tablename__ = "ai_qa_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tipo
    interaction_type = Column(
        SQLEnum(QAInteractionTypeEnum, name="qa_interaction_type_enum"),
        default=QAInteractionTypeEnum.QUESTION,
        nullable=False,
    )

    # Pergunta
    question = Column(Text, nullable=False)
    question_normalized = Column(Text, nullable=True)
    question_intent = Column(String(100), nullable=True)
    question_entities = Column(JSONB, default=[])
    question_embedding = Column(ARRAY(Float), nullable=True)

    # Resposta
    response_type = Column(
        SQLEnum(QAResponseTypeEnum, name="qa_response_type_enum"),
        nullable=True,
    )
    response = Column(Text, nullable=True)
    response_formatted = Column(Text, nullable=True)  # HTML/Markdown
    response_sources = Column(JSONB, default=[])  # Fontes usadas

    # Confianca e metricas
    confidence_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    response_time_ms = Column(Integer, default=0)

    # Matches encontrados
    matched_articles = Column(JSONB, default=[])  # [{id, score, title}]
    matched_faqs = Column(JSONB, default=[])  # [{id, score, question}]
    search_results = Column(JSONB, default=[])  # Resultados brutos

    # Feedback da interacao
    is_helpful = Column(Boolean, nullable=True)
    rating = Column(Integer, nullable=True)
    feedback_text = Column(Text, nullable=True)
    feedback_at = Column(DateTime, nullable=True)

    # Acao tomada
    action_taken = Column(String(100), nullable=True)
    clicked_article_id = Column(UUID(as_uuid=True), nullable=True)
    clicked_faq_id = Column(UUID(as_uuid=True), nullable=True)

    # Contexto da interacao
    context_used = Column(JSONB, default={})
    previous_context = Column(JSONB, default={})

    # Relacionamentos
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_qa_sessions.id"),
        nullable=False,
    )
    parent_interaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_qa_interactions.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    session = relationship("QASession", back_populates="interactions")
    follow_ups = relationship(
        "QAInteraction",
        backref="parent_interaction",
        remote_side=[id],
    )

    def __repr__(self) -> str:
        return f"<QAInteraction {self.question[:30]}>"


class QASuggestion(Base):
    """
    Modelo de Sugestao Q&A.

    Armazena sugestoes de perguntas baseadas em contexto.
    """

    __tablename__ = "ai_qa_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Sugestao
    suggestion_text = Column(String(500), nullable=False)
    suggestion_type = Column(String(50), default="related")  # related, popular, recent

    # Contexto
    context_page = Column(String(200), nullable=True)
    context_category = Column(String(100), nullable=True)
    context_keywords = Column(ARRAY(String), default=[])

    # Estatisticas
    shown_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    click_rate = Column(Float, default=0.0)

    # Validade
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relacionamentos
    knowledge_base_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_knowledge_bases.id"),
        nullable=False,
    )
    target_faq_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_faqs.id"),
        nullable=True,
    )
    target_article_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_kb_articles.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    ativo = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<QASuggestion {self.suggestion_text[:30]}>"
