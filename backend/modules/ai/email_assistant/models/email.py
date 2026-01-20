"""
Email Model - Sprint 54.

Modelo para emails processados pelo assistente de IA.
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


class EmailStatusEnum(str, enum.Enum):
    """Status do email."""

    RECEIVED = "received"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    RESPONDED = "responded"
    ARCHIVED = "archived"
    SPAM = "spam"
    DELETED = "deleted"


class EmailCategoryEnum(str, enum.Enum):
    """Categoria do email."""

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


class EmailPriorityEnum(str, enum.Enum):
    """Prioridade do email."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class EmailSentimentEnum(str, enum.Enum):
    """Sentimento do email."""

    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class Email(Base):
    """
    Modelo de Email.

    Representa um email processado pelo assistente de IA.
    """

    __tablename__ = "ai_emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    message_id = Column(String(500), unique=True, nullable=False)
    thread_id = Column(String(500), nullable=True)
    in_reply_to = Column(String(500), nullable=True)

    # Remetente/Destinatario
    from_address = Column(String(500), nullable=False)
    from_name = Column(String(200), nullable=True)
    to_addresses = Column(ARRAY(String), default=[])
    cc_addresses = Column(ARRAY(String), default=[])
    bcc_addresses = Column(ARRAY(String), default=[])
    reply_to = Column(String(500), nullable=True)

    # Conteudo
    subject = Column(String(1000), nullable=True)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    body_preview = Column(String(500), nullable=True)

    # Anexos
    has_attachments = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    attachments = Column(JSONB, default=[])  # [{name, size, type, url}]

    # Classificacao IA
    status = Column(
        SQLEnum(EmailStatusEnum, name="email_status_enum"),
        default=EmailStatusEnum.RECEIVED,
        nullable=False,
    )
    category = Column(
        SQLEnum(EmailCategoryEnum, name="email_category_enum"),
        nullable=True,
    )
    category_confidence = Column(Float, default=0.0)
    subcategory = Column(String(100), nullable=True)

    # Prioridade
    priority = Column(
        SQLEnum(EmailPriorityEnum, name="email_priority_enum"),
        default=EmailPriorityEnum.MEDIUM,
    )
    priority_score = Column(Float, default=0.5)
    priority_factors = Column(JSONB, default={})

    # Sentimento
    sentiment = Column(
        SQLEnum(EmailSentimentEnum, name="email_sentiment_enum"),
        nullable=True,
    )
    sentiment_score = Column(Float, default=0.0)
    emotions = Column(JSONB, default={})  # {emotion: score}

    # Analise de conteudo
    language = Column(String(10), default="pt-BR")
    keywords = Column(ARRAY(String), default=[])
    entities = Column(JSONB, default=[])  # [{type, value, confidence}]
    topics = Column(ARRAY(String), default=[])
    intent = Column(String(100), nullable=True)
    intent_confidence = Column(Float, default=0.0)

    # Acoes detectadas
    action_items = Column(JSONB, default=[])  # [{action, deadline, assignee}]
    questions = Column(JSONB, default=[])  # [{question, answered}]
    requests = Column(JSONB, default=[])  # [{type, description, status}]

    # Seguranca
    is_spam = Column(Boolean, default=False)
    spam_score = Column(Float, default=0.0)
    is_phishing = Column(Boolean, default=False)
    phishing_indicators = Column(JSONB, default=[])
    security_score = Column(Float, default=1.0)  # 1.0 = safe

    # Resposta automatica
    auto_reply_sent = Column(Boolean, default=False)
    auto_reply_id = Column(UUID(as_uuid=True), nullable=True)
    suggested_reply = Column(Text, nullable=True)
    reply_confidence = Column(Float, default=0.0)

    # Roteamento
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_team = Column(String(100), nullable=True)
    routing_reason = Column(String(500), nullable=True)

    # Datas
    received_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    # Metricas
    processing_time_ms = Column(Integer, default=0)
    response_time_minutes = Column(Integer, nullable=True)

    # Relacionamentos
    account_id = Column(UUID(as_uuid=True), nullable=True)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=True,
    )
    contact_id = Column(UUID(as_uuid=True), nullable=True)
    ticket_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadados
    headers = Column(JSONB, default={})
    email_extra_metadata = Column(JSONB, default={})

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    ativo = Column(Boolean, default=True, nullable=False)

    # Relationships
    responses = relationship(
        "EmailResponse",
        back_populates="email",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Email {self.subject[:50] if self.subject else 'No Subject'}>"


class EmailResponse(Base):
    """
    Modelo de Resposta de Email.

    Representa uma resposta gerada ou enviada.
    """

    __tablename__ = "ai_email_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Conteudo
    subject = Column(String(1000), nullable=True)
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)

    # Tipo
    response_type = Column(String(50), default="manual")  # auto, suggested, manual
    template_id = Column(UUID(as_uuid=True), nullable=True)
    template_name = Column(String(200), nullable=True)

    # Status
    is_draft = Column(Boolean, default=True)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)

    # IA
    ai_generated = Column(Boolean, default=False)
    generation_confidence = Column(Float, default=0.0)
    modifications = Column(JSONB, default=[])  # Historico de edicoes

    # Relacionamentos
    email_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_emails.id"),
        nullable=False,
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    email = relationship("Email", back_populates="responses")

    def __repr__(self) -> str:
        return f"<EmailResponse {self.id}>"


class EmailTemplate(Base):
    """
    Modelo de Template de Email.

    Templates para respostas automaticas.
    """

    __tablename__ = "ai_email_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    name = Column(String(200), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # Conteudo
    subject_template = Column(String(1000), nullable=True)
    body_template = Column(Text, nullable=False)
    body_html_template = Column(Text, nullable=True)

    # Classificacao
    category = Column(
        SQLEnum(EmailCategoryEnum, name="email_category_enum_template"),
        nullable=True,
    )
    language = Column(String(10), default="pt-BR")
    tags = Column(ARRAY(String), default=[])

    # Condicoes de uso
    trigger_keywords = Column(ARRAY(String), default=[])
    trigger_intents = Column(ARRAY(String), default=[])
    min_confidence = Column(Float, default=0.7)

    # Variaveis
    variables = Column(JSONB, default=[])  # [{name, type, required, default}]

    # Estatisticas
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)

    # Config
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<EmailTemplate {self.name}>"


class EmailRule(Base):
    """
    Modelo de Regra de Email.

    Regras para processamento automatico.
    """

    __tablename__ = "ai_email_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=0)  # Ordem de execucao

    # Condicoes
    conditions = Column(JSONB, nullable=False)  # [{field, operator, value}]
    condition_logic = Column(String(10), default="AND")  # AND, OR

    # Acoes
    actions = Column(JSONB, nullable=False)  # [{type, params}]

    # Tipos de acao:
    # - categorize: {category}
    # - prioritize: {priority}
    # - assign: {user_id, team}
    # - auto_reply: {template_id}
    # - tag: {tags}
    # - move: {folder}
    # - notify: {channels, users}
    # - create_ticket: {params}

    # Config
    is_active = Column(Boolean, default=True)
    stop_processing = Column(Boolean, default=False)  # Para de processar outras regras

    # Estatisticas
    match_count = Column(Integer, default=0)
    last_match_at = Column(DateTime, nullable=True)

    # Relacionamentos
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=True,
    )

    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<EmailRule {self.name}>"
