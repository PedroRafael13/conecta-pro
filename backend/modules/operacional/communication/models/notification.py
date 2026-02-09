"""
Modelo Notification (Notificacao) para Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class NotificationType(StrEnum):
    """Tipo de notificacao."""

    OCORRENCIA = "ocorrencia"  # Notificacao de ocorrencia
    MEDIDA = "medida"  # Medida disciplinar
    COMUNICADO = "comunicado"  # Novo comunicado
    ESCALA = "escala"  # Mudanca em escala
    ALERTA = "alerta"  # Alerta do sistema
    SUBSTITUICAO = "substituicao"  # Solicitacao de substituicao
    BANCO_HORAS = "banco_horas"  # Banco de horas
    TAREFA = "tarefa"  # Tarefa atribuida
    APROVACAO = "aprovacao"  # Aprovacao pendente
    SISTEMA = "sistema"  # Notificacao do sistema


class NotificationChannel(StrEnum):
    """Canal de envio da notificacao."""

    PUSH = "push"  # Push notification
    EMAIL = "email"  # Email
    SMS = "sms"  # SMS
    WHATSAPP = "whatsapp"  # WhatsApp
    IN_APP = "in_app"  # Dentro do app


class Notification(Base):
    """
    Modelo de Notificacao.

    Representa notificacoes enviadas para usuarios via multiplos canais.
    Suporta rastreamento de envio, leitura e cliques.

    Attributes:
        id: Identificador unico (UUID)
        tenant_id: ID do tenant (multi-tenancy)
        user_id: ID do usuario destinatario
        title: Titulo da notificacao
        body: Corpo/conteudo da notificacao
        type: Tipo da notificacao
        reference_type: Tipo da entidade referenciada
        reference_id: ID da entidade referenciada
        channels: Canais de envio utilizados
        sent_at: Data/hora do envio
        read_at: Data/hora da leitura
        clicked_at: Data/hora do clique na acao
        action_url: URL de acao/redirecionamento
        extra_data: Dados adicionais (JSON)
        is_active: Se a notificacao esta ativa
        created_at: Data de criacao

    Example:
        >>> notification = Notification(
        ...     tenant_id="tenant-123",
        ...     user_id="user-456",
        ...     title="Nova Ocorrencia",
        ...     body="Uma ocorrencia foi registrada no seu posto.",
        ...     type=NotificationType.OCORRENCIA,
        ...     reference_type="occurrence",
        ...     reference_id="occurrence-789",
        ...     channels=[NotificationChannel.PUSH, NotificationChannel.EMAIL],
        ...     action_url="/ocorrencias/occurrence-789",
        ... )
    """

    __tablename__ = "communication_notifications"

    # Identificacao
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # Destinatario
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # Conteudo
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Classificacao
    type: Mapped[str] = mapped_column(
        String(30),
        default=NotificationType.SISTEMA.value,
        nullable=False,
        index=True,
    )

    # Referencia (entidade relacionada)
    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Tipo da entidade referenciada (occurrence, shift, etc)",
    )
    reference_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="ID da entidade referenciada",
    )

    # Canais de Envio
    channels: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: [NotificationChannel.IN_APP.value],
        comment="Lista de canais utilizados para envio",
    )

    # Rastreamento
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data/hora em que foi enviada",
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data/hora em que foi lida",
    )
    clicked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data/hora em que o usuario clicou na acao",
    )

    # Acao
    action_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="URL para redirecionamento ao clicar",
    )

    # Dados Adicionais
    extra_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Dados adicionais da notificacao",
    )

    # Controle
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representacao string da notificacao."""
        return f"<Notification {self.id[:8]}... - {self.title[:30]}>"

    @property
    def is_sent(self) -> bool:
        """Verifica se a notificacao foi enviada."""
        return self.sent_at is not None

    @property
    def is_read(self) -> bool:
        """Verifica se a notificacao foi lida."""
        return self.read_at is not None

    @property
    def is_clicked(self) -> bool:
        """Verifica se o usuario clicou na acao."""
        return self.clicked_at is not None

    @property
    def time_to_read(self) -> float | None:
        """
        Calcula tempo entre envio e leitura (em segundos).

        Returns:
            Tempo em segundos ou None se nao lida.
        """
        if not self.sent_at or not self.read_at:
            return None
        delta = self.read_at - self.sent_at
        return delta.total_seconds()

    @property
    def time_to_click(self) -> float | None:
        """
        Calcula tempo entre leitura e clique (em segundos).

        Returns:
            Tempo em segundos ou None se nao clicada.
        """
        if not self.read_at or not self.clicked_at:
            return None
        delta = self.clicked_at - self.read_at
        return delta.total_seconds()

    def mark_as_sent(self) -> None:
        """Marca a notificacao como enviada."""
        if self.sent_at is None:
            self.sent_at = datetime.utcnow()

    def mark_as_read(self) -> None:
        """Marca a notificacao como lida."""
        if self.read_at is None:
            self.read_at = datetime.utcnow()

    def mark_as_clicked(self) -> None:
        """Marca a notificacao como clicada."""
        if self.clicked_at is None:
            self.clicked_at = datetime.utcnow()
        # Se clicou, tambem marca como lida
        self.mark_as_read()

    def add_channel(self, channel: NotificationChannel) -> None:
        """
        Adiciona um canal de envio.

        Args:
            channel: Canal a ser adicionado
        """
        if self.channels is None:
            self.channels = []
        if channel.value not in self.channels:
            self.channels.append(channel.value)

    def has_channel(self, channel: NotificationChannel) -> bool:
        """
        Verifica se a notificacao usa um canal especifico.

        Args:
            channel: Canal a verificar

        Returns:
            True se o canal esta configurado
        """
        return self.channels is not None and channel.value in self.channels

    @classmethod
    def create(
        cls,
        tenant_id: str,
        user_id: str,
        title: str,
        body: str,
        notification_type: NotificationType = NotificationType.SISTEMA,
        channels: list[NotificationChannel] | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
        action_url: str | None = None,
        extra_data: dict | None = None,
    ) -> Notification:
        """
        Factory method para criar notificacao.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            title: Titulo
            body: Corpo
            notification_type: Tipo da notificacao
            channels: Canais de envio
            reference_type: Tipo da referencia
            reference_id: ID da referencia
            action_url: URL de acao
            extra_data: Dados adicionais

        Returns:
            Nova instancia de Notification
        """
        if channels is None:
            channels = [NotificationChannel.IN_APP]

        return cls(
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            body=body,
            type=notification_type.value,
            channels=[c.value for c in channels],
            reference_type=reference_type,
            reference_id=reference_id,
            action_url=action_url,
            extra_data=extra_data or {},
        )
