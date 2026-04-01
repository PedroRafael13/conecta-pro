"""
Modelo KitAccessLog — Log de Acesso a Kits Documentais.

Registra toda ação sobre um kit: visualização, download,
impressão, aprovação, rejeição, assinatura e envio.
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class AccessAction(StrEnum):
    """Ação registrada no log de acesso."""

    VIEWED = "viewed"
    DOWNLOADED = "downloaded"
    PRINTED = "printed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SIGNED = "signed"
    SENT = "sent"


class ActorType(StrEnum):
    """Tipo do ator que executou a ação."""

    INTERNAL = "internal"
    CLIENT = "client"


class KitAccessLog(Base):
    """Registro de acesso/ação sobre um kit documental.

    Mantém auditoria completa de quem acessou, baixou, imprimiu,
    aprovou ou rejeitou um kit. Diferencia entre usuários internos
    e clientes externos (portal).
    """

    __tablename__ = "ged_kit_access_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    kit_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="FK para ged_document_kits.id",
    )
    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Ação realizada (viewed, downloaded, approved, etc.)",
    )
    actor_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Tipo do ator: internal (funcionário) ou client (portal)",
    )
    actor_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID do ator (user.id ou ged_clients.id)",
    )
    actor_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome legível do ator para exibição rápida",
    )
    actor_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Endereço IP do ator (IPv4 ou IPv6)",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent do navegador do ator",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Observações adicionais (ex: motivo da rejeição)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<KitAccessLog(id={self.id}, kit_id={self.kit_id}, action={self.action}, actor={self.actor_name})>"
