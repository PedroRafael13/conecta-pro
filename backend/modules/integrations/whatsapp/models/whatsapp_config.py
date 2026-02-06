"""WhatsApp Configuration Model - Configuracao WhatsApp Business.

Sprint 31 - Automacoes WhatsApp.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class WhatsAppStatus(str, enum.Enum):
    """Status da configuracao WhatsApp."""

    PENDING = "PENDING"  # Pendente de configuracao
    CONNECTED = "CONNECTED"  # Conectado e funcionando
    DISCONNECTED = "DISCONNECTED"  # Desconectado
    ERROR = "ERROR"  # Erro de conexao
    SUSPENDED = "SUSPENDED"  # Suspenso pelo WhatsApp


class WhatsAppProvider(str, enum.Enum):
    """Provedor de API WhatsApp."""

    META_CLOUD = "META_CLOUD"  # Meta Cloud API (oficial)
    TWILIO = "TWILIO"  # Twilio
    MESSAGEBIRD = "MESSAGEBIRD"  # MessageBird
    ZENVIA = "ZENVIA"  # Zenvia
    TAKE_BLIP = "TAKE_BLIP"  # Take Blip
    GUPSHUP = "GUPSHUP"  # Gupshup


class WhatsAppConfig(Base):
    """Configuracao de conta WhatsApp Business."""

    __tablename__ = "wa_configs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Provedor e Credenciais
    provider = Column(
        Enum(WhatsAppProvider, name="whatsappprovider", create_type=True),
        nullable=False,
        default=WhatsAppProvider.META_CLOUD,
    )
    phone_number = Column(String(20), nullable=False)
    phone_number_id = Column(String(50), nullable=True)  # Meta Cloud API
    business_account_id = Column(String(50), nullable=True)  # Meta WABA ID
    access_token = Column(Text, nullable=True)  # Token de acesso (criptografado)
    api_key = Column(String(255), nullable=True)  # API Key alternativa
    api_secret = Column(String(255), nullable=True)  # API Secret

    # Webhook
    webhook_url = Column(String(500), nullable=True)
    webhook_verify_token = Column(String(100), nullable=True)
    webhook_secret = Column(String(255), nullable=True)

    # Status
    status = Column(
        Enum(WhatsAppStatus, name="whatsappstatus", create_type=True),
        nullable=False,
        default=WhatsAppStatus.PENDING,
    )
    last_connected_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0, nullable=False)

    # Rate Limiting
    messages_per_second = Column(Integer, default=30, nullable=False)
    messages_per_day_limit = Column(Integer, default=1000, nullable=False)
    messages_sent_today = Column(Integer, default=0, nullable=False)
    last_rate_reset = Column(DateTime(timezone=True), nullable=True)

    # Configuracoes
    default_template_language = Column(String(10), default="pt_BR", nullable=False)
    auto_reply_enabled = Column(Boolean, default=False, nullable=False)
    auto_reply_message = Column(Text, nullable=True)
    business_hours_only = Column(Boolean, default=False, nullable=False)
    business_hours_start = Column(String(5), default="08:00", nullable=False)
    business_hours_end = Column(String(5), default="18:00", nullable=False)

    # Integracao
    integration_data = Column(JSONB, nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

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
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WhatsAppConfig {self.name} ({self.phone_number})>"

    @property
    def is_connected(self) -> bool:
        """Verifica se esta conectado."""
        return self.status == WhatsAppStatus.CONNECTED and self.active

    @property
    def can_send_messages(self) -> bool:
        """Verifica se pode enviar mensagens."""
        if not self.is_connected:
            return False
        if self.messages_sent_today >= self.messages_per_day_limit:
            return False
        return True

    def increment_message_count(self) -> None:
        """Incrementa contador de mensagens enviadas."""
        self.messages_sent_today += 1

    def reset_daily_count(self) -> None:
        """Reseta contador diario."""
        self.messages_sent_today = 0
        self.last_rate_reset = datetime.utcnow()

    def mark_connected(self) -> None:
        """Marca como conectado."""
        self.status = WhatsAppStatus.CONNECTED
        self.last_connected_at = datetime.utcnow()
        self.error_count = 0
        self.last_error = None

    def mark_error(self, error_message: str) -> None:
        """Marca erro de conexao."""
        self.status = WhatsAppStatus.ERROR
        self.last_error = error_message
        self.error_count += 1

    def get_masked_token(self) -> Optional[str]:
        """Retorna token mascarado para exibicao."""
        if not self.access_token:
            return None
        if len(self.access_token) <= 8:
            return "****"
        return f"{self.access_token[:4]}...{self.access_token[-4:]}"
