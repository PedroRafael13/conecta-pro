"""
modules/fase5/email_intelligence/models.py - Email Intelligence Models
======================================================================
Modelos de dados para analise de emails
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .enums import ActionType, EmailCategory, EmailIntent, EmailPriority, EmailStatus, SentimentType


class EmailAttachment(BaseModel):
    """Anexo de email."""

    model_config = ConfigDict(frozen=True)

    attachment_id: UUID = Field(default_factory=uuid4)
    filename: str
    content_type: str
    size_bytes: int
    storage_path: str | None = None


class EmailMessage(BaseModel):
    """Mensagem de email."""

    message_id: UUID = Field(default_factory=uuid4)
    external_id: str | None = None

    # Headers
    from_address: EmailStr
    from_name: str | None = None
    to_addresses: list[EmailStr]
    cc_addresses: list[EmailStr] = Field(default_factory=list)
    bcc_addresses: list[EmailStr] = Field(default_factory=list)
    reply_to: EmailStr | None = None

    # Content
    subject: str
    body_text: str | None = None
    body_html: str | None = None

    # Attachments
    attachments: list[EmailAttachment] = Field(default_factory=list)

    # Metadata
    received_at: datetime = Field(default_factory=datetime.utcnow)
    status: EmailStatus = Field(default=EmailStatus.NAO_LIDO)

    # Thread info
    thread_id: UUID | None = None
    in_reply_to: str | None = None
    references: list[str] = Field(default_factory=list)

    # Tenant
    tenant_id: UUID


class EmailThread(BaseModel):
    """Thread de emails (conversacao)."""

    thread_id: UUID = Field(default_factory=uuid4)
    subject: str
    participants: list[EmailStr]

    # Messages
    messages: list[EmailMessage] = Field(default_factory=list)
    message_count: int = 0

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime | None = None
    is_active: bool = True

    # Classification
    category: EmailCategory | None = None
    priority: EmailPriority | None = None

    # Context
    related_entity_type: str | None = None  # cliente, proposta, contrato
    related_entity_id: UUID | None = None

    # Tenant
    tenant_id: UUID


class EmailAnalysis(BaseModel):
    """Resultado da analise de email."""

    analysis_id: UUID = Field(default_factory=uuid4)
    message_id: UUID
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    # Classification
    category: EmailCategory
    category_confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    priority: EmailPriority
    priority_confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    # Intent
    primary_intent: EmailIntent
    secondary_intents: list[EmailIntent] = Field(default_factory=list)
    intent_confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    # Sentiment
    sentiment: SentimentType
    sentiment_score: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))

    # Entities extracted
    entities: dict[str, Any] = Field(default_factory=dict)
    # cnpj, cpf, valores, datas, nomes, enderecos, telefones

    # Keywords
    keywords: list[str] = Field(default_factory=list)

    # Summary
    summary: str | None = None

    # Flags
    is_urgent: bool = False
    requires_response: bool = True
    is_spam: bool = False

    # Related records
    related_cliente_id: UUID | None = None
    related_proposta_id: UUID | None = None
    related_contrato_id: UUID | None = None


class EmailSuggestion(BaseModel):
    """Sugestao de acao para email."""

    suggestion_id: UUID = Field(default_factory=uuid4)
    message_id: UUID
    analysis_id: UUID

    # Action
    action_type: ActionType
    action_description: str
    action_priority: int = Field(ge=1, le=10)

    # Response suggestion
    suggested_response: str | None = None
    response_template_id: UUID | None = None

    # Assignment
    suggested_assignee: str | None = None
    suggested_department: str | None = None

    # Deadline
    suggested_deadline: datetime | None = None

    # Confidence
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    # Status
    accepted: bool | None = None
    executed_at: datetime | None = None


class EmailContext(BaseModel):
    """Contexto historico do email/cliente."""

    context_id: UUID = Field(default_factory=uuid4)
    email_address: EmailStr

    # History stats
    total_emails_received: int = 0
    total_emails_sent: int = 0
    first_contact: datetime | None = None
    last_contact: datetime | None = None

    # Relationship
    is_cliente: bool = False
    cliente_id: UUID | None = None
    cliente_nome: str | None = None

    # Communication patterns
    average_response_time_hours: Decimal | None = None
    preferred_contact_time: str | None = None

    # Sentiment history
    average_sentiment: Decimal = Field(default=Decimal("0"))
    sentiment_trend: str = "stable"  # improving, stable, declining

    # Topics
    common_topics: list[str] = Field(default_factory=list)
    pending_issues: list[str] = Field(default_factory=list)

    # Notes
    notes: list[str] = Field(default_factory=list)

    # Last interactions
    recent_interactions: list[dict[str, Any]] = Field(default_factory=list)


class EmailTemplate(BaseModel):
    """Template de resposta de email."""

    template_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str

    # Content
    subject_template: str
    body_template: str

    # Classification
    category: EmailCategory
    intent: EmailIntent

    # Variables
    variables: list[str] = Field(default_factory=list)

    # Metadata
    is_active: bool = True
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Tenant
    tenant_id: UUID
