"""Model de Push Notification."""

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class NotificationStatus(StrEnum):
    """Status da notificação."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(StrEnum):
    """Tipo de notificação."""

    SYSTEM = "system"
    ALERT = "alert"
    INFO = "info"
    MARKETING = "marketing"
    REMINDER = "reminder"
    TRANSACTION = "transaction"
    MESSAGE = "message"
    ACTION_REQUIRED = "action_required"


class NotificationPriority(StrEnum):
    """Prioridade da notificação."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MobileNotificationLog(Base):
    """
    Log de notificações push enviadas (módulo mobile).

    Armazena histórico de todas as notificações enviadas,
    incluindo status de entrega e leitura.

    Renomeado de MobilePushNotification para evitar conflito com
    modules.notifications.push.models.push_notification.PushNotification
    """

    __tablename__ = "mobile_notification_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    device_token_id = Column(
        UUID(as_uuid=True),
        ForeignKey("device_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )
    title = Column(
        String(200),
        nullable=False,
    )
    body = Column(
        Text,
        nullable=False,
    )
    notification_type = Column(
        String(30),
        default=NotificationType.INFO.value,
        nullable=False,
    )
    priority = Column(
        String(20),
        default=NotificationPriority.NORMAL.value,
        nullable=False,
    )
    data_payload = Column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Dados adicionais enviados na notificação",
    )
    image_url = Column(
        String(500),
        nullable=True,
        comment="URL da imagem para notificação rich",
    )
    action_url = Column(
        String(500),
        nullable=True,
        comment="URL de ação ao clicar na notificação",
    )
    category = Column(
        String(50),
        nullable=True,
        comment="Categoria para agrupamento",
    )
    thread_id = Column(
        String(100),
        nullable=True,
        comment="ID para agrupar notificações relacionadas",
    )
    collapse_key = Column(
        String(100),
        nullable=True,
        comment="Chave para colapsar notificações similares",
    )
    ttl_seconds = Column(
        Integer,
        nullable=True,
        comment="Tempo de vida da notificação em segundos",
    )
    status = Column(
        String(20),
        default=NotificationStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Mensagem de erro se falhou",
    )
    external_id = Column(
        String(200),
        nullable=True,
        comment="ID retornado pelo FCM/APNs",
    )
    scheduled_for = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Agendamento para envio futuro",
    )
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    clicked_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    extra_metadata = Column(
        JSONB,
        default=dict,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relacionamentos
    user = relationship("User")
    device_token_ref = relationship("DeviceToken")

    def __repr__(self) -> str:
        return f"<MobilePushNotification {self.id} status={self.status}>"

    def mark_as_sent(self, external_id: str | None = None) -> None:
        """Marca como enviada."""
        self.status = NotificationStatus.SENT.value
        self.sent_at = datetime.now(UTC)
        if external_id:
            self.external_id = external_id

    def mark_as_delivered(self) -> None:
        """Marca como entregue."""
        self.status = NotificationStatus.DELIVERED.value
        self.delivered_at = datetime.now(UTC)

    def mark_as_read(self) -> None:
        """Marca como lida."""
        self.status = NotificationStatus.READ.value
        self.read_at = datetime.now(UTC)

    def mark_as_clicked(self) -> None:
        """Marca como clicada."""
        self.clicked_at = datetime.now(UTC)

    def mark_as_failed(self, error_message: str) -> None:
        """Marca como falha."""
        self.status = NotificationStatus.FAILED.value
        self.error_message = error_message

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "title": self.title,
            "body": self.body,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "data_payload": self.data_payload,
            "image_url": self.image_url,
            "action_url": self.action_url,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
