"""Email Tracking Model - Rastreamento de Emails.

Sprint 32 - Automacoes Email.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class TrackingEventType(str, enum.Enum):
    """Tipo de evento de tracking."""

    SENT = "SENT"  # Email enviado
    DELIVERED = "DELIVERED"  # Email entregue
    OPENED = "OPENED"  # Email aberto
    CLICKED = "CLICKED"  # Link clicado
    BOUNCED = "BOUNCED"  # Email retornado
    UNSUBSCRIBED = "UNSUBSCRIBED"  # Descadastro
    COMPLAINED = "COMPLAINED"  # Marcado como spam
    CONVERTED = "CONVERTED"  # Conversao (compra, cadastro, etc)


class EmailTracking(Base):
    """Evento de tracking de email."""

    __tablename__ = "email_tracking"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relacionamentos
    queue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_queue.id"),
        nullable=False,
        index=True,
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_campaigns.id"),
        nullable=True,
        index=True,
    )

    # Destinatario
    recipient_email = Column(String(255), nullable=False, index=True)

    # Tipo de evento
    event_type = Column(
        Enum(TrackingEventType, name="trackingeventtype", create_type=True),
        nullable=False,
        index=True,
    )

    # Dados do evento
    event_data = Column(JSONB, nullable=True)

    # Para cliques - URL clicada
    clicked_url = Column(Text, nullable=True)
    link_id = Column(String(100), nullable=True)  # ID do link rastreado

    # Informacoes do dispositivo/cliente
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    browser_name = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)
    email_client = Column(String(100), nullable=True)  # Gmail, Outlook, etc

    # Geolocalizacao (baseada no IP)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Provider message ID
    provider_event_id = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    queue = relationship("EmailQueue", lazy="joined")
    campaign = relationship("EmailCampaign", lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EmailTracking {self.event_type.value} - {self.recipient_email}>"

    @property
    def is_engagement(self) -> bool:
        """Verifica se e evento de engajamento."""
        return self.event_type in (
            TrackingEventType.OPENED,
            TrackingEventType.CLICKED,
            TrackingEventType.CONVERTED,
        )

    @property
    def is_negative(self) -> bool:
        """Verifica se e evento negativo."""
        return self.event_type in (
            TrackingEventType.BOUNCED,
            TrackingEventType.UNSUBSCRIBED,
            TrackingEventType.COMPLAINED,
        )

    @property
    def is_mobile(self) -> bool:
        """Verifica se foi em dispositivo movel."""
        return self.device_type == "mobile"

    @classmethod
    def from_open(
        cls,
        tenant_id,
        queue_id,
        recipient_email: str,
        ip_address: str = None,
        user_agent: str = None,
        campaign_id=None,
    ) -> "EmailTracking":
        """Cria evento de abertura.

        Args:
            tenant_id: ID do tenant.
            queue_id: ID do email na fila.
            recipient_email: Email do destinatario.
            ip_address: IP do cliente.
            user_agent: User agent.
            campaign_id: ID da campanha.

        Returns:
            EmailTracking.
        """
        return cls(
            tenant_id=tenant_id,
            queue_id=queue_id,
            campaign_id=campaign_id,
            recipient_email=recipient_email,
            event_type=TrackingEventType.OPENED,
            ip_address=ip_address,
            user_agent=user_agent,
            event_timestamp=datetime.utcnow(),
        )

    @classmethod
    def from_click(
        cls,
        tenant_id,
        queue_id,
        recipient_email: str,
        clicked_url: str,
        ip_address: str = None,
        user_agent: str = None,
        campaign_id=None,
        link_id: str = None,
    ) -> "EmailTracking":
        """Cria evento de clique.

        Args:
            tenant_id: ID do tenant.
            queue_id: ID do email na fila.
            recipient_email: Email do destinatario.
            clicked_url: URL clicada.
            ip_address: IP do cliente.
            user_agent: User agent.
            campaign_id: ID da campanha.
            link_id: ID do link.

        Returns:
            EmailTracking.
        """
        return cls(
            tenant_id=tenant_id,
            queue_id=queue_id,
            campaign_id=campaign_id,
            recipient_email=recipient_email,
            event_type=TrackingEventType.CLICKED,
            clicked_url=clicked_url,
            link_id=link_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_timestamp=datetime.utcnow(),
        )

    @classmethod
    def from_unsubscribe(
        cls,
        tenant_id,
        queue_id,
        recipient_email: str,
        campaign_id=None,
    ) -> "EmailTracking":
        """Cria evento de descadastro.

        Args:
            tenant_id: ID do tenant.
            queue_id: ID do email na fila.
            recipient_email: Email do destinatario.
            campaign_id: ID da campanha.

        Returns:
            EmailTracking.
        """
        return cls(
            tenant_id=tenant_id,
            queue_id=queue_id,
            campaign_id=campaign_id,
            recipient_email=recipient_email,
            event_type=TrackingEventType.UNSUBSCRIBED,
            event_timestamp=datetime.utcnow(),
        )

    def parse_user_agent(self) -> None:  # pylint: disable=too-many-branches
        """Extrai informacoes do user agent."""
        if not self.user_agent:
            return

        ua_lower = self.user_agent.lower()

        # Detecta tipo de dispositivo
        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            self.device_type = "mobile"
        elif "tablet" in ua_lower or "ipad" in ua_lower:
            self.device_type = "tablet"
        else:
            self.device_type = "desktop"

        # Detecta OS
        if "windows" in ua_lower:
            self.os_name = "Windows"
        elif "mac os" in ua_lower or "macos" in ua_lower:
            self.os_name = "macOS"
        elif "linux" in ua_lower:
            self.os_name = "Linux"
        elif "android" in ua_lower:
            self.os_name = "Android"
        elif "ios" in ua_lower or "iphone" in ua_lower or "ipad" in ua_lower:
            self.os_name = "iOS"

        # Detecta navegador
        if "chrome" in ua_lower and "edg" not in ua_lower:
            self.browser_name = "Chrome"
        elif "firefox" in ua_lower:
            self.browser_name = "Firefox"
        elif "safari" in ua_lower and "chrome" not in ua_lower:
            self.browser_name = "Safari"
        elif "edg" in ua_lower:
            self.browser_name = "Edge"

        # Detecta cliente de email
        if "googleimageproxy" in ua_lower:
            self.email_client = "Gmail"
        elif "outlook" in ua_lower:
            self.email_client = "Outlook"
        elif "yahoo" in ua_lower:
            self.email_client = "Yahoo Mail"
        elif "thunderbird" in ua_lower:
            self.email_client = "Thunderbird"
