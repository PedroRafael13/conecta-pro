"""Model de mensagem de chat."""

from datetime import datetime, UTC
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.ai.conversation.models.chat_session import ChatSession


class MessageType(str, Enum):
    """Tipo de mensagem."""

    USER = "user"
    AI = "ai"
    SYSTEM = "system"
    ERROR = "error"
    ACTION = "action"  # Mensagem de acao executada
    SUGGESTION = "suggestion"  # Sugestoes da IA


class MessageStatus(str, Enum):
    """Status da mensagem."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IntentCategory(str, Enum):
    """Categorias de intencao."""

    HELP_NAVIGATION = "help_navigation"
    DATA_QUERY = "data_query"
    ACTION_REQUEST = "action_request"
    ANALYSIS_REQUEST = "analysis_request"
    SYSTEM_INFO = "system_info"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL_CONVERSATION = "general_conversation"
    FEEDBACK = "feedback"
    GREETING = "greeting"
    FAREWELL = "farewell"


class ChatMessage(Base):
    """Mensagem individual de chat."""

    __tablename__ = "chat_messages"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Conteudo
    message_type = Column(String(20), nullable=False, default=MessageType.USER.value)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)  # Versao formatada

    # Classificacao
    intent = Column(String(50), nullable=True)
    intent_confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    entities = Column(JSONB, nullable=True)  # Entidades extraidas
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral

    # Contexto
    context_data = Column(JSONB, nullable=True)
    referenced_module = Column(String(50), nullable=True)  # Modulo referenciado
    referenced_entity_id = Column(String(100), nullable=True)  # ID da entidade

    # Resposta da IA
    response_extra_metadata = Column(JSONB, nullable=True)
    suggestions = Column(JSONB, nullable=True)  # Lista de sugestoes
    actions = Column(JSONB, nullable=True)  # Acoes sugeridas/executadas
    related_links = Column(JSONB, nullable=True)  # Links relacionados

    # Performance
    processing_time_ms = Column(Integer, nullable=True)  # Tempo de processamento
    tokens_used = Column(Integer, nullable=True)  # Tokens consumidos
    model_used = Column(String(50), nullable=True)  # gpt-4, claude-3, etc.

    # Feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 estrelas
    user_feedback = Column(Text, nullable=True)
    was_helpful = Column(Boolean, nullable=True)

    # Status
    status = Column(String(20), default=MessageStatus.COMPLETED.value)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Controle
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    original_content = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Relacionamentos
    session: "ChatSession" = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        """Representacao string."""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"<ChatMessage(id={self.id}, type={self.message_type}, content='{content_preview}')>"

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "message_type": self.message_type,
            "content": self.content,
            "content_html": self.content_html,
            "intent": self.intent,
            "intent_confidence": self.intent_confidence,
            "sentiment": self.sentiment,
            "suggestions": self.suggestions,
            "actions": self.actions,
            "processing_time_ms": self.processing_time_ms,
            "model_used": self.model_used,
            "user_rating": self.user_rating,
            "was_helpful": self.was_helpful,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def mark_as_helpful(self, rating: int = 5, feedback: Optional[str] = None) -> None:
        """Marca mensagem como util."""
        self.was_helpful = True
        self.user_rating = min(max(rating, 1), 5)  # Clamp 1-5
        if feedback:
            self.user_feedback = feedback

    def mark_as_not_helpful(
        self, rating: int = 1, feedback: Optional[str] = None
    ) -> None:
        """Marca mensagem como nao util."""
        self.was_helpful = False
        self.user_rating = min(max(rating, 1), 5)
        if feedback:
            self.user_feedback = feedback

    def edit_content(self, new_content: str) -> None:
        """Edita conteudo da mensagem."""
        if not self.is_edited:
            self.original_content = self.content
        self.content = new_content
        self.is_edited = True
        self.edited_at = datetime.now(UTC)
