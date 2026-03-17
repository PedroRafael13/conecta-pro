"""
Modelo ClientTicket — Tickets de suporte do portal do cliente.

Clientes podem abrir chamados relacionados a kits documentais ou
questoes gerais. Os tickets sao gerenciados pela equipe interna.
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class TicketStatus(StrEnum):
    """Status do ticket de suporte."""

    ABERTO = "ABERTO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    RESPONDIDO = "RESPONDIDO"
    FECHADO = "FECHADO"


class TicketPriority(StrEnum):
    """Prioridade do ticket de suporte."""

    BAIXA = "BAIXA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


class ClientTicket(Base):
    """Ticket de suporte aberto pelo cliente no portal.

    Pode estar vinculado a um kit documental especifico ou ser
    uma solicitacao geral. Suporta mensagens bidirecionais.
    """

    __tablename__ = "client_portal_tickets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    client_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="FK para ged_clients.id",
    )
    kit_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="FK para ged_document_kits.id (opcional)",
    )
    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Assunto do ticket",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Descricao detalhada do problema ou solicitacao",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=TicketStatus.ABERTO,
        nullable=False,
        index=True,
        comment="Status: ABERTO, EM_ANDAMENTO, RESPONDIDO, FECHADO",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=TicketPriority.NORMAL,
        nullable=False,
        index=True,
        comment="Prioridade: BAIXA, NORMAL, ALTA, URGENTE",
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data/hora do fechamento do ticket",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    messages: Mapped[list["ClientTicketMessage"]] = relationship(  # noqa: F821
        "ClientTicketMessage",
        back_populates="ticket",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ClientTicketMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ClientTicket(id={self.id}, subject={self.subject}, status={self.status})>"
