"""Modelo de Comentário de Ocorrência."""

import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.occurrences.models.occurrence import Occurrence


class CommentVisibility(str, enum.Enum):
    """Visibilidade do comentário."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"


class OccurrenceComment(Base):
    """Modelo de Comentário de Ocorrência."""

    __tablename__ = "occurrence_comments"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento
    occurrence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("occurrences.id"), nullable=False, index=True
    )

    # Conteúdo
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    visibility: Mapped[CommentVisibility] = mapped_column(
        Enum(CommentVisibility), default=CommentVisibility.PUBLIC
    )

    # Autor
    author_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)
    author_email: Mapped[Optional[str]] = mapped_column(String(200))
    author_role: Mapped[Optional[str]] = mapped_column(String(50))
    author_avatar: Mapped[Optional[str]] = mapped_column(String(500))
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)

    # Resposta
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("occurrence_comments.id"), nullable=True
    )
    reply_count: Mapped[int] = mapped_column(Integer, default=0)

    # Menções
    mentions: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Anexos
    attachments: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Métricas
    like_count: Mapped[int] = mapped_column(Integer, default=0)

    # Flags
    is_solution: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_first_response: Mapped[bool] = mapped_column(Boolean, default=False)

    # Edição
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    edit_count: Mapped[int] = mapped_column(Integer, default=0)
    original_content: Mapped[Optional[str]] = mapped_column(Text)

    # IA
    ai_sentiment: Mapped[Optional[str]] = mapped_column(String(20))
    ai_is_spam: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deleted_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relacionamentos
    occurrence: Mapped["Occurrence"] = relationship(
        "Occurrence", back_populates="comments"
    )
    replies: Mapped[list["OccurrenceComment"]] = relationship(
        "OccurrenceComment", back_populates="parent", remote_side=[id]
    )
    parent: Mapped[Optional["OccurrenceComment"]] = relationship(
        "OccurrenceComment", back_populates="replies", remote_side=[parent_id]
    )

    def edit(self, new_content: str) -> None:
        """Edita o comentário."""
        if not self.is_edited:
            self.original_content = self.content
        self.content = new_content
        self.is_edited = True
        self.edited_at = datetime.utcnow()
        self.edit_count += 1

    def soft_delete(self, deleted_by_id: str) -> None:
        """Deleta o comentário (soft delete)."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by_id = deleted_by_id
        self.content = "[Comentário removido]"

    def mark_as_solution(self) -> None:
        """Marca como solução."""
        self.is_solution = True

    def unmark_as_solution(self) -> None:
        """Remove marcação de solução."""
        self.is_solution = False

    def pin(self) -> None:
        """Fixa o comentário."""
        self.is_pinned = True

    def unpin(self) -> None:
        """Desfixa o comentário."""
        self.is_pinned = False

    def add_like(self) -> None:
        """Adiciona like."""
        self.like_count += 1

    def remove_like(self) -> None:
        """Remove like."""
        if self.like_count > 0:
            self.like_count -= 1

    def increment_replies(self) -> None:
        """Incrementa contador de respostas."""
        self.reply_count += 1

    def add_mention(self, user_id: str, user_name: str) -> None:
        """Adiciona menção."""
        if self.mentions is None:
            self.mentions = []
        self.mentions.append({
            "user_id": user_id,
            "user_name": user_name,
        })

    def add_attachment(self, attachment_id: str, filename: str, url: str) -> None:
        """Adiciona anexo."""
        if self.attachments is None:
            self.attachments = []
        self.attachments.append({
            "id": attachment_id,
            "filename": filename,
            "url": url,
        })

    @property
    def is_reply(self) -> bool:
        """Verifica se é resposta."""
        return self.parent_id is not None

    @property
    def has_replies(self) -> bool:
        """Verifica se tem respostas."""
        return self.reply_count > 0

    @property
    def is_visible(self) -> bool:
        """Verifica se está visível."""
        return self.is_active and not self.is_deleted
