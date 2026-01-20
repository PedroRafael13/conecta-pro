"""
Modelo AnnouncementRead (Confirmacao de Leitura) para Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .announcement import Announcement


class AnnouncementRead(Base):
    """
    Modelo de Confirmacao de Leitura de Comunicado.

    Registra quando um usuario leu e/ou confirmou um comunicado.
    Inclui metadados de rastreamento como IP e User-Agent.

    Attributes:
        id: Identificador unico (UUID)
        announcement_id: ID do comunicado (FK)
        user_id: ID do usuario que leu
        read_at: Data/hora da leitura
        acknowledged_at: Data/hora da confirmacao (se requerida)
        ip_address: Endereco IP do usuario
        user_agent: User-Agent do navegador/app

    Example:
        >>> read = AnnouncementRead(
        ...     announcement_id="announcement-123",
        ...     user_id="user-456",
        ...     read_at=datetime.utcnow(),
        ...     ip_address="192.168.1.100",
        ...     user_agent="Mozilla/5.0...",
        ... )
    """

    __tablename__ = "communication_announcement_reads"

    # Identificacao
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Relacionamento com Comunicado
    announcement_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey(
            "communication_announcements.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Usuario
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # Timestamps de Leitura/Confirmacao
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Data/hora em que o usuario visualizou o comunicado",
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data/hora em que o usuario confirmou a leitura",
    )

    # Metadados de Rastreamento
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Endereco IP do usuario (IPv4 ou IPv6)",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent do navegador/aplicativo",
    )

    # Relacionamento
    announcement: Mapped["Announcement"] = relationship(
        "Announcement",
        back_populates="reads",
    )

    def __repr__(self) -> str:
        """Representacao string da leitura."""
        return (
            f"<AnnouncementRead announcement={self.announcement_id[:8]}... "
            f"user={self.user_id[:8]}...>"
        )

    @property
    def is_acknowledged(self) -> bool:
        """Verifica se o comunicado foi confirmado."""
        return self.acknowledged_at is not None

    @property
    def time_to_read(self) -> Optional[float]:
        """
        Calcula tempo entre criacao do comunicado e leitura (em segundos).

        Returns:
            Tempo em segundos ou None se nao houver dados suficientes.
        """
        if not self.announcement or not self.announcement.published_at:
            return None
        delta = self.read_at - self.announcement.published_at
        return delta.total_seconds()

    @property
    def time_to_acknowledge(self) -> Optional[float]:
        """
        Calcula tempo entre leitura e confirmacao (em segundos).

        Returns:
            Tempo em segundos ou None se nao confirmado.
        """
        if not self.acknowledged_at:
            return None
        delta = self.acknowledged_at - self.read_at
        return delta.total_seconds()

    def acknowledge(self) -> None:
        """Marca o comunicado como confirmado."""
        if self.acknowledged_at is None:
            self.acknowledged_at = datetime.utcnow()

    @classmethod
    def create_read(
        cls,
        announcement_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "AnnouncementRead":
        """
        Factory method para criar registro de leitura.

        Args:
            announcement_id: ID do comunicado
            user_id: ID do usuario
            ip_address: Endereco IP (opcional)
            user_agent: User-Agent (opcional)

        Returns:
            Nova instancia de AnnouncementRead
        """
        return cls(
            announcement_id=announcement_id,
            user_id=user_id,
            read_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
        )
