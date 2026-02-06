"""Message Log Model - Log de Mensagens WhatsApp.

Sprint 31 - Automacoes WhatsApp.
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class MessageDirection(str, enum.Enum):
    """Direcao da mensagem."""

    OUTBOUND = "OUTBOUND"  # Enviada
    INBOUND = "INBOUND"  # Recebida


class ConversationType(str, enum.Enum):
    """Tipo de conversa (para billing do WhatsApp)."""

    BUSINESS_INITIATED = "BUSINESS_INITIATED"  # Iniciada pela empresa
    USER_INITIATED = "USER_INITIATED"  # Iniciada pelo usuario
    REFERRAL_CONVERSION = "REFERRAL_CONVERSION"  # Conversao de referencia


class MessageLog(Base):
    """Log de mensagens WhatsApp (historico completo)."""

    __tablename__ = "wa_message_logs"

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
    queue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wa_message_queue.id"),
        nullable=True,
        index=True,
    )

    # Direcao
    direction = Column(
        Enum(MessageDirection, name="messagedirection", create_type=True),
        nullable=False,
        index=True,
    )

    # Identificadores WhatsApp
    external_id = Column(String(100), nullable=True, index=True)  # WAMID
    conversation_id = Column(String(100), nullable=True)

    # Participantes
    from_phone = Column(String(20), nullable=False)
    to_phone = Column(String(20), nullable=False)
    contact_name = Column(String(100), nullable=True)

    # Conteudo
    message_type = Column(String(50), nullable=False)  # text, image, template, etc
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    media_mime_type = Column(String(100), nullable=True)
    template_name = Column(String(100), nullable=True)
    template_data = Column(JSONB, nullable=True)

    # Status
    status = Column(String(50), nullable=False)  # sent, delivered, read, failed
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps do WhatsApp
    timestamp_sent = Column(DateTime(timezone=True), nullable=True)
    timestamp_delivered = Column(DateTime(timezone=True), nullable=True)
    timestamp_read = Column(DateTime(timezone=True), nullable=True)

    # Conversa e Billing
    conversation_type = Column(
        Enum(ConversationType, name="conversationtype", create_type=True),
        nullable=True,
    )
    billable = Column(Integer, default=1, nullable=False)  # 1 = cobravel
    cost = Column(Numeric(10, 4), default=Decimal("0"), nullable=False)

    # Contexto
    context_message_id = Column(String(100), nullable=True)  # Reply to
    context_data = Column(JSONB, nullable=True)

    # Webhook data (raw)
    webhook_data = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    config = relationship("WhatsAppConfig", lazy="joined")
    queue = relationship("MessageQueue", lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        direction_str = "->" if self.direction == MessageDirection.OUTBOUND else "<-"
        return f"<MessageLog {self.from_phone} {direction_str} {self.to_phone}>"

    @property
    def is_outbound(self) -> bool:
        """Verifica se e mensagem enviada."""
        return self.direction == MessageDirection.OUTBOUND

    @property
    def is_inbound(self) -> bool:
        """Verifica se e mensagem recebida."""
        return self.direction == MessageDirection.INBOUND

    @property
    def is_delivered(self) -> bool:
        """Verifica se foi entregue."""
        return self.status in ("delivered", "read")

    @property
    def is_read(self) -> bool:
        """Verifica se foi lida."""
        return self.status == "read"

    @property
    def has_error(self) -> bool:
        """Verifica se teve erro."""
        return self.status == "failed" or self.error_code is not None

    @classmethod
    def from_outbound(
        cls,
        tenant_id,
        config_id,
        from_phone: str,
        to_phone: str,
        message_type: str,
        content: str,
        external_id: str = None,
        queue_id=None,
    ) -> "MessageLog":
        """Cria log de mensagem enviada."""
        return cls(
            tenant_id=tenant_id,
            config_id=config_id,
            queue_id=queue_id,
            direction=MessageDirection.OUTBOUND,
            external_id=external_id,
            from_phone=from_phone,
            to_phone=to_phone,
            message_type=message_type,
            content=content,
            status="sent",
            timestamp_sent=datetime.utcnow(),
        )

    @classmethod
    def from_inbound(
        cls,
        tenant_id,
        config_id,
        from_phone: str,
        to_phone: str,
        message_type: str,
        content: str,
        external_id: str,
        contact_name: str = None,
        webhook_data: dict = None,
    ) -> "MessageLog":
        """Cria log de mensagem recebida."""
        return cls(
            tenant_id=tenant_id,
            config_id=config_id,
            direction=MessageDirection.INBOUND,
            external_id=external_id,
            from_phone=from_phone,
            to_phone=to_phone,
            contact_name=contact_name,
            message_type=message_type,
            content=content,
            status="received",
            webhook_data=webhook_data,
        )
