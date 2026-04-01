"""
Modelo ClientPortalSession — Sessoes de acesso ao portal do cliente.

Registra cada sessao autenticada de um cliente externo, incluindo
token JWT, IP, user-agent e validade.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ClientPortalSession(Base):
    """Sessao de autenticacao do portal do cliente.

    Cada login gera uma sessao com token JWT que expira em 24h.
    Sessoes podem ser invalidadas (logout) ou expirar naturalmente.
    """

    __tablename__ = "client_portal_sessions"

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
    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        comment="Token JWT da sessao",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Endereco IP do cliente (IPv4 ou IPv6)",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent do navegador do cliente",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Data/hora de expiracao do token",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se a sessao esta ativa (False apos logout)",
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

    def __repr__(self) -> str:
        return f"<ClientPortalSession(id={self.id}, client_id={self.client_id}, active={self.is_active})>"
