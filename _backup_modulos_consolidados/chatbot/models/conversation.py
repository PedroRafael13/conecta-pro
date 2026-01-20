"""Conversation Models - Conversas do Chatbot.

Sprint 38 - Chatbot IA.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class ConversationStatus(str, enum.Enum):
    """Status da conversa."""

    ACTIVE = "active"
    WAITING_USER = "waiting_user"
    WAITING_BOT = "waiting_bot"
    HANDOFF = "handoff"  # Transferida para humano
    RESOLVED = "resolved"
    ABANDONED = "abandoned"
    EXPIRED = "expired"
    CLOSED = "closed"


class ConversationChannel(str, enum.Enum):
    """Canal da conversa."""

    WEB = "web"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    SMS = "sms"
    VOICE = "voice"
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    API = "api"


class MessageType(str, enum.Enum):
    """Tipo de mensagem."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    BUTTON_RESPONSE = "button_response"
    QUICK_REPLY = "quick_reply"
    CARD = "card"
    CAROUSEL = "carousel"
    LIST = "list"
    FORM = "form"
    SYSTEM = "system"


class MessageSender(str, enum.Enum):
    """Remetente da mensagem."""

    USER = "user"
    BOT = "bot"
    AGENT = "agent"  # Atendente humano
    SYSTEM = "system"


class SentimentType(str, enum.Enum):
    """Tipo de sentimento."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class Conversation(Base):
    """Modelo de conversa do chatbot."""

    __tablename__ = "chatbot_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    conversation_id = Column(String(100), nullable=False, unique=True, index=True)
    external_id = Column(String(200), index=True)  # ID do canal externo

    # Usuario
    user_id = Column(UUID(as_uuid=True), index=True)  # Usuario do sistema (se autenticado)
    visitor_id = Column(String(200), index=True)  # ID do visitante (anonimo)
    user_name = Column(String(200))
    user_email = Column(String(200))
    user_phone = Column(String(50))
    user_avatar = Column(String(500))

    # Canal
    channel = Column(Enum(ConversationChannel), nullable=False, index=True)
    channel_user_id = Column(String(200))  # ID do usuario no canal
    channel_data = Column(JSONB, default={})  # Dados especificos do canal

    # Status
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE, index=True)
    status_reason = Column(String(200))
    status_changed_at = Column(DateTime)

    # Contexto
    current_context = Column(JSONB, default={})
    # Estrutura: {
    #   "active_contexts": ["greeting", "menu"],
    #   "slots": {"name": "Joao", "email": "joao@email.com"},
    #   "state": "collecting_info",
    #   "last_intent": "schedule_appointment"
    # }

    # Intencoes detectadas
    detected_intents = Column(JSONB, default=[])
    # Estrutura: [
    #   {"intent": "greeting", "confidence": 0.95, "timestamp": "..."},
    #   {"intent": "schedule", "confidence": 0.87, "timestamp": "..."}
    # ]

    # Entidades extraidas
    extracted_entities = Column(JSONB, default={})
    # Estrutura: {
    #   "date": {"value": "2026-01-10", "confidence": 0.92},
    #   "time": {"value": "14:00", "confidence": 0.88}
    # }

    # Sentimento
    overall_sentiment = Column(Enum(SentimentType), default=SentimentType.NEUTRAL)
    sentiment_score = Column(Float)  # -1 a 1
    sentiment_history = Column(JSONB, default=[])

    # Metricas de conversa
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    bot_messages = Column(Integer, default=0)
    agent_messages = Column(Integer, default=0)
    avg_response_time_ms = Column(Integer)
    max_response_time_ms = Column(Integer)

    # Duracao
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Handoff
    handoff_requested = Column(Boolean, default=False)
    handoff_at = Column(DateTime)
    handoff_reason = Column(String(500))
    assigned_agent_id = Column(UUID(as_uuid=True))
    assigned_queue_id = Column(UUID(as_uuid=True))

    # Resolucao
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(50))  # bot, agent, user
    resolution_notes = Column(Text)

    # Feedback
    satisfaction_rating = Column(Integer)  # 1-5
    satisfaction_comment = Column(Text)
    feedback_at = Column(DateTime)

    # Tags e categorias
    tags = Column(ARRAY(String), default=[])
    category = Column(String(100))
    priority = Column(String(20), default="normal")  # low, normal, high, urgent

    # Localizacao
    user_ip = Column(String(50))
    user_country = Column(String(2))
    user_city = Column(String(100))
    user_timezone = Column(String(50))
    user_language = Column(String(10))

    # Device info
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))
    os = Column(String(100))
    user_agent = Column(String(500))

    # Referencia
    referrer_url = Column(String(500))
    landing_page = Column(String(500))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))

    # Integracao
    crm_contact_id = Column(UUID(as_uuid=True))
    ticket_id = Column(UUID(as_uuid=True))
    order_id = Column(UUID(as_uuid=True))

    # Metadata
    extra_data = Column(JSONB, default={})

    # Controle
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        foreign_keys="ConversationMessage.conversation_id",
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.conversation_id[:8]}... ({self.status.value})>"

    def add_context(self, context_name: str, lifespan: int = 5) -> None:
        """Adiciona contexto ativo."""
        if not self.current_context:
            self.current_context = {"active_contexts": [], "slots": {}}

        contexts = self.current_context.get("active_contexts", [])
        if context_name not in contexts:
            contexts.append(context_name)
            self.current_context["active_contexts"] = contexts

    def set_slot(self, slot_name: str, value: any) -> None:
        """Define valor de um slot."""
        if not self.current_context:
            self.current_context = {"active_contexts": [], "slots": {}}

        self.current_context.setdefault("slots", {})[slot_name] = value

    def get_slot(self, slot_name: str) -> Optional[any]:
        """Obtem valor de um slot."""
        if not self.current_context:
            return None
        return self.current_context.get("slots", {}).get(slot_name)


class ConversationMessage(Base):
    """Modelo de mensagem da conversa."""

    __tablename__ = "chatbot_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chatbot_conversations.id"), nullable=False, index=True)

    # Identificacao
    message_id = Column(String(100), nullable=False, unique=True, index=True)
    external_id = Column(String(200))  # ID no canal externo

    # Remetente
    sender = Column(Enum(MessageSender), nullable=False, index=True)
    sender_id = Column(String(200))
    sender_name = Column(String(200))

    # Conteudo
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    text = Column(Text)
    normalized_text = Column(Text)  # Texto normalizado para NLU

    # Anexos
    attachments = Column(JSONB, default=[])
    # Estrutura: [
    #   {"type": "image", "url": "...", "filename": "...", "size": 1234}
    # ]

    # Resposta rica
    rich_content = Column(JSONB)
    # Estrutura variavel por tipo

    # Buttons
    buttons = Column(JSONB, default=[])
    quick_replies = Column(JSONB, default=[])

    # NLU
    intent = Column(String(100))
    intent_confidence = Column(Float)
    entities = Column(JSONB, default=[])
    # Estrutura: [
    #   {"entity": "date", "value": "amanha", "confidence": 0.9, "start": 10, "end": 16}
    # ]

    # Sentimento
    sentiment = Column(Enum(SentimentType))
    sentiment_score = Column(Float)

    # Resposta
    is_response_to = Column(UUID(as_uuid=True))  # ID da mensagem respondida
    response_time_ms = Column(Integer)

    # Fallback
    is_fallback = Column(Boolean, default=False)
    fallback_reason = Column(String(200))

    # Acao
    action_triggered = Column(String(100))
    action_result = Column(JSONB)

    # Contexto no momento
    context_snapshot = Column(JSONB)

    # Entrega
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    delivery_status = Column(String(20), default="sent")  # sent, delivered, read, failed

    # Erro
    error_code = Column(String(50))
    error_message = Column(Text)

    # Feedback
    was_helpful = Column(Boolean)
    feedback_text = Column(Text)

    # Edicao
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)
    original_text = Column(Text)

    # Metadata
    extra_metadata = Column("metadata", JSONB, default={})

    # Controle
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    conversation = relationship(
        "Conversation",
        back_populates="messages",
        foreign_keys=[conversation_id],
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage {self.message_id[:8]}... ({self.sender.value})>"


class ConversationContext(Base):
    """Modelo de contexto da conversa (para tracking)."""

    __tablename__ = "chatbot_conversation_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Contexto
    context_name = Column(String(100), nullable=False)
    parameters = Column(JSONB, default={})
    lifespan = Column(Integer, default=5)
    remaining_turns = Column(Integer)

    # Ciclo de vida
    activated_at = Column(DateTime, default=datetime.utcnow)
    deactivated_at = Column(DateTime)
    triggered_by = Column(String(100))  # intent que ativou

    # Controle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ConversationContext {self.context_name}>"

    def decrement_lifespan(self) -> bool:
        """Decrementa lifespan e retorna se ainda esta ativo."""
        if self.remaining_turns is None:
            self.remaining_turns = self.lifespan

        self.remaining_turns -= 1
        if self.remaining_turns <= 0:
            self.is_active = False
            self.deactivated_at = datetime.utcnow()
            return False
        return True
