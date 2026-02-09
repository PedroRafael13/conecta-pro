"""Model de sessao de chat."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from core.models.user import User
    from modules.ai.conversation.models.chat_message import ChatMessage


class ChatSession(Base):
    """Sessao de chat com IA."""

    __tablename__ = "chat_sessions"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Informacoes da sessao
    title = Column(String(200), nullable=False, default="Nova Conversa")
    description = Column(Text, nullable=True)

    # Contexto
    module_context = Column(String(50), nullable=True)  # crm, financial, hr, etc.
    initial_context = Column(JSONB, nullable=True)
    current_context = Column(JSONB, nullable=True)

    # Estatisticas
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    metadata_ = Column("metadata", JSONB, nullable=True)
    tags = Column(JSONB, nullable=True)  # ["importante", "pendente"]

    # Controle
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    archived_at = Column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    user: "User" = relationship("User")
    messages: list["ChatMessage"] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<ChatSession(id={self.id}, title='{self.title}', user_id={self.user_id})>"

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "module_context": self.module_context,
            "message_count": self.message_count,
            "last_message_at": (self.last_message_at.isoformat() if self.last_message_at else None),
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def archive(self) -> None:
        """Arquiva a sessao."""
        self.is_archived = True
        self.is_active = False
        self.archived_at = datetime.now(UTC)

    def unarchive(self) -> None:
        """Desarquiva a sessao."""
        self.is_archived = False
        self.is_active = True
        self.archived_at = None

    def increment_message_count(self) -> None:
        """Incrementa contador de mensagens."""
        self.message_count = (self.message_count or 0) + 1
        self.last_message_at = datetime.now(UTC)
