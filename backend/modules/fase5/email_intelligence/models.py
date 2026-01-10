"""
modules/fase5/email_intelligence/models.py - Email Intelligence Models
======================================================================
Modelos de dados para analise de emails
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from .enums import (
    EmailCategory,
    EmailPriority,
    EmailIntent,
    SentimentType,
    EmailStatus,
    ActionType
)


class EmailAttachment(BaseModel):
    """Anexo de email."""

    model_config = ConfigDict(frozen=True)

    attachment_id: UUID = Field(default_factory=uuid4)
    filename: str
    content_type: str
    size_bytes: int
    storage_path: Optional[str] = None


class EmailMessage(BaseModel):
    """Mensagem de email."""

    message_id: UUID = Field(default_factory=uuid4)
    external_id: Optional[str] = None

    # Headers
    from_address: EmailStr
    from_name: Optional[str] = None
    to_addresses: List[EmailStr]
    cc_addresses: List[EmailStr] = Field(default_factory=list)
    bcc_addresses: List[EmailStr] = Field(default_factory=list)
    reply_to: Optional[EmailStr] = None

    # Content
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None

    # Attachments
    attachments: List[EmailAttachment] = Field(default_factory=list)

    # Metadata
    received_at: datetime = Field(default_factory=datetime.utcnow)
    status: EmailStatus = Field(default=EmailStatus.NAO_LIDO)

    # Thread info
    thread_id: Optional[UUID] = None
    in_reply_to: Optional[str] = None
    references: List[str] = Field(default_factory=list)

    # Tenant
    tenant_id: UUID


class EmailThread(BaseModel):
    """Thread de emails (conversacao)."""

    thread_id: UUID = Field(default_factory=uuid4)
    subject: str
    participants: List[EmailStr]

    # Messages
    messages: List[EmailMessage] = Field(default_factory=list)
    message_count: int = 0

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    is_active: bool = True

    # Classification
    category: Optional[EmailCategory] = None
    priority: Optional[EmailPriority] = None

    # Context
    related_entity_type: Optional[str] = None  # cliente, proposta, contrato
    related_entity_id: Optional[UUID] = None

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
    secondary_intents: List[EmailIntent] = Field(default_factory=list)
    intent_confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    # Sentiment
    sentiment: SentimentType
    sentiment_score: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))

    # Entities extracted
    entities: Dict[str, Any] = Field(default_factory=dict)
    # cnpj, cpf, valores, datas, nomes, enderecos, telefones

    # Keywords
    keywords: List[str] = Field(default_factory=list)

    # Summary
    summary: Optional[str] = None

    # Flags
    is_urgent: bool = False
    requires_response: bool = True
    is_spam: bool = False

    # Related records
    related_cliente_id: Optional[UUID] = None
    related_proposta_id: Optional[UUID] = None
    related_contrato_id: Optional[UUID] = None


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
    suggested_response: Optional[str] = None
    response_template_id: Optional[UUID] = None

    # Assignment
    suggested_assignee: Optional[str] = None
    suggested_department: Optional[str] = None

    # Deadline
    suggested_deadline: Optional[datetime] = None

    # Confidence
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))

    # Status
    accepted: Optional[bool] = None
    executed_at: Optional[datetime] = None


class EmailContext(BaseModel):
    """Contexto historico do email/cliente."""

    context_id: UUID = Field(default_factory=uuid4)
    email_address: EmailStr

    # History stats
    total_emails_received: int = 0
    total_emails_sent: int = 0
    first_contact: Optional[datetime] = None
    last_contact: Optional[datetime] = None

    # Relationship
    is_cliente: bool = False
    cliente_id: Optional[UUID] = None
    cliente_nome: Optional[str] = None

    # Communication patterns
    average_response_time_hours: Optional[Decimal] = None
    preferred_contact_time: Optional[str] = None

    # Sentiment history
    average_sentiment: Decimal = Field(default=Decimal("0"))
    sentiment_trend: str = "stable"  # improving, stable, declining

    # Topics
    common_topics: List[str] = Field(default_factory=list)
    pending_issues: List[str] = Field(default_factory=list)

    # Notes
    notes: List[str] = Field(default_factory=list)

    # Last interactions
    recent_interactions: List[Dict[str, Any]] = Field(default_factory=list)


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
    variables: List[str] = Field(default_factory=list)

    # Metadata
    is_active: bool = True
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Tenant
    tenant_id: UUID
