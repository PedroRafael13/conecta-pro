"""Message Queue Model - Fila de Mensagens WhatsApp.

Sprint 31 - Automacoes WhatsApp.
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class MessageStatus(str, enum.Enum):
    """Status da mensagem na fila."""

    QUEUED = "QUEUED"  # Na fila aguardando
    PROCESSING = "PROCESSING"  # Sendo processada
    SENT = "SENT"  # Enviada para API
    DELIVERED = "DELIVERED"  # Entregue ao destinatario
    READ = "READ"  # Lida pelo destinatario
    FAILED = "FAILED"  # Falha no envio
    CANCELLED = "CANCELLED"  # Cancelada
    EXPIRED = "EXPIRED"  # Expirada


class MessagePriority(str, enum.Enum):
    """Prioridade da mensagem."""

    LOW = "LOW"  # Baixa prioridade
    NORMAL = "NORMAL"  # Normal
    HIGH = "HIGH"  # Alta prioridade
    URGENT = "URGENT"  # Urgente


class MessageType(str, enum.Enum):
    """Tipo de mensagem."""

    TEMPLATE = "TEMPLATE"  # Mensagem via template
    TEXT = "TEXT"  # Texto livre (24h window)
    MEDIA = "MEDIA"  # Midia
    INTERACTIVE = "INTERACTIVE"  # Interativa
    REACTION = "REACTION"  # Reacao a mensagem


class MessagePurpose(str, enum.Enum):
    """Proposito da mensagem."""

    BILLING = "BILLING"  # Cobranca
    REMINDER = "REMINDER"  # Lembrete
    NOTIFICATION = "NOTIFICATION"  # Notificacao
    MARKETING = "MARKETING"  # Marketing
    SUPPORT = "SUPPORT"  # Suporte
    TRANSACTIONAL = "TRANSACTIONAL"  # Transacional
    AUTHENTICATION = "AUTHENTICATION"  # Autenticacao (OTP)
    OTHER = "OTHER"  # Outros


class MessageQueue(Base):
    """Fila de mensagens WhatsApp."""

    __tablename__ = "wa_message_queue"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relacionamentos
    config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wa_configs.id"),
        nullable=False,
        index=True,
    )
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wa_templates.id"),
        nullable=True,
        index=True,
    )

    # Destinatario
    recipient_phone = Column(String(20), nullable=False, index=True)
    recipient_name = Column(String(100), nullable=True)
    recipient_id = Column(UUID(as_uuid=True), nullable=True)  # ID do cliente/morador

    # Tipo e Proposito
    message_type = Column(
        Enum(MessageType, name="messagetype", create_type=True),
        nullable=False,
        default=MessageType.TEMPLATE,
    )
    purpose = Column(
        Enum(MessagePurpose, name="messagepurpose", create_type=True),
        nullable=False,
        default=MessagePurpose.NOTIFICATION,
    )

    # Conteudo
    content = Column(Text, nullable=True)  # Texto renderizado ou livre
    template_variables = Column(JSONB, nullable=True)  # Variaveis do template
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)

    # Contexto (dados relacionados)
    context_type = Column(String(50), nullable=True)  # Ex: "boleto", "os"
    context_id = Column(UUID(as_uuid=True), nullable=True)  # ID do objeto relacionado
    context_data = Column(JSONB, nullable=True)  # Dados extras

    # Status e Fila
    status = Column(
        Enum(MessageStatus, name="messagestatus", create_type=True),
        nullable=False,
        default=MessageStatus.QUEUED,
        index=True,
    )
    priority = Column(
        Enum(MessagePriority, name="messagepriority", create_type=True),
        nullable=False,
        default=MessagePriority.NORMAL,
    )

    # Agendamento
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Resultado do Envio
    external_id = Column(String(100), nullable=True)  # ID na API do WhatsApp
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Retentativas
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    # Custo (alguns provedores cobram por mensagem)
    cost = Column(Numeric(10, 4), default=Decimal("0"), nullable=False)

    # Flags
    is_automated = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    config = relationship("WhatsAppConfig", lazy="joined")
    template = relationship("MessageTemplate", lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<MessageQueue {self.id} -> {self.recipient_phone} ({self.status.value})>"

    @property
    def is_pending(self) -> bool:
        """Verifica se esta pendente de envio."""
        return self.status in (MessageStatus.QUEUED, MessageStatus.PROCESSING)

    @property
    def is_completed(self) -> bool:
        """Verifica se foi completada (enviada ou entregue)."""
        return self.status in (
            MessageStatus.SENT,
            MessageStatus.DELIVERED,
            MessageStatus.READ,
        )

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        if self.status != MessageStatus.FAILED:
            return False
        return (self.retry_count or 0) < (self.max_retries or 3)

    @property
    def is_scheduled(self) -> bool:
        """Verifica se e agendada."""
        if not self.scheduled_at:
            return False
        return self.scheduled_at > datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        """Verifica se expirou."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def mark_sent(self, external_id: str) -> None:
        """Marca como enviada."""
        self.status = MessageStatus.SENT
        self.external_id = external_id
        self.sent_at = datetime.utcnow()
        self.error_code = None
        self.error_message = None

    def mark_delivered(self) -> None:
        """Marca como entregue."""
        self.status = MessageStatus.DELIVERED
        self.delivered_at = datetime.utcnow()

    def mark_read(self) -> None:
        """Marca como lida."""
        self.status = MessageStatus.READ
        self.read_at = datetime.utcnow()

    def mark_failed(self, error_code: str, error_message: str) -> None:
        """Marca como falha."""
        self.status = MessageStatus.FAILED
        self.failed_at = datetime.utcnow()
        self.error_code = error_code
        self.error_message = error_message
        self.retry_count = (self.retry_count or 0) + 1

    def schedule_retry(self, next_retry: Optional[datetime] = None) -> None:
        """Agenda retentativa."""
        if not self.can_retry:
            return
        self.status = MessageStatus.QUEUED
        self.next_retry_at = next_retry or datetime.utcnow()

    def cancel(self) -> None:
        """Cancela a mensagem."""
        if self.is_pending:
            self.status = MessageStatus.CANCELLED

    def expire(self) -> None:
        """Marca como expirada."""
        if self.is_pending:
            self.status = MessageStatus.EXPIRED
