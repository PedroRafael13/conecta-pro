"""
Modelo ClientTicketMessage — Mensagens de um ticket de suporte.

Cada ticket pode ter multiplas mensagens, enviadas pelo cliente
(CLIENT) ou pela equipe interna (INTERNAL).
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class SenderType(StrEnum):
    """Tipo de remetente da mensagem."""

    CLIENT = "CLIENT"
    INTERNAL = "INTERNAL"


class ClientTicketMessage(Base):
    """Mensagem dentro de um ticket de suporte.

    Registra comunicacao bidirecional entre o cliente externo
    e a equipe interna da empresa.
    """

    __tablename__ = "client_portal_ticket_messages"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    ticket_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("client_portal_tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK para client_portal_tickets.id",
    )
    sender_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo do remetente: CLIENT ou INTERNAL",
    )
    sender_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID do remetente (users.id para INTERNAL)",
    )
    sender_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nome legivel do remetente",
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Conteudo da mensagem",
    )
    attachments: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Lista de anexos [{name, size}]",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    ticket: Mapped["ClientTicket"] = relationship(  # noqa: F821
        "ClientTicket",
        back_populates="messages",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<ClientTicketMessage(id={self.id}, ticket_id={self.ticket_id}, sender={self.sender_name})>"
