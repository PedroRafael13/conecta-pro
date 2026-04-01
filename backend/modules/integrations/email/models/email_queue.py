"""Email Queue Model - Fila de Emails.

Sprint 32 - Automacoes Email.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class EmailStatus(StrEnum):
    """Status do email na fila."""

    QUEUED = "QUEUED"  # Na fila
    PROCESSING = "PROCESSING"  # Processando
    SENT = "SENT"  # Enviado
    DELIVERED = "DELIVERED"  # Entregue
    OPENED = "OPENED"  # Aberto
    CLICKED = "CLICKED"  # Clicado
    BOUNCED = "BOUNCED"  # Retornado
    FAILED = "FAILED"  # Falhou
    CANCELLED = "CANCELLED"  # Cancelado
    UNSUBSCRIBED = "UNSUBSCRIBED"  # Descadastrado


class BounceType(StrEnum):
    """Tipo de bounce."""

    HARD = "HARD"  # Bounce permanente (email invalido)
    SOFT = "SOFT"  # Bounce temporario (caixa cheia, etc)
    COMPLAINT = "COMPLAINT"  # Marcado como spam


class EmailPriority(StrEnum):
    """Prioridade do email."""

    LOW = "LOW"  # Baixa (newsletters)
    NORMAL = "NORMAL"  # Normal
    HIGH = "HIGH"  # Alta (transacional)
    URGENT = "URGENT"  # Urgente (OTP, alertas)


class EmailQueue(Base):
    """Fila de envio de emails."""

    __tablename__ = "email_queue"

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
        ForeignKey("email_configs.id"),
        nullable=False,
        index=True,
    )
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_templates.id"),
        nullable=True,
    )
    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_campaigns.id"),
        nullable=True,
        index=True,
    )

    # Destinatario
    to_email = Column(String(255), nullable=False, index=True)
    to_name = Column(String(100), nullable=True)

    # Remetente
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(100), nullable=True)
    reply_to = Column(String(255), nullable=True)

    # Conteudo
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)

    # Variaveis usadas na renderizacao
    variables = Column(JSONB, nullable=True)

    # Headers customizados
    custom_headers = Column(JSONB, nullable=True)

    # Anexos (referencias)
    attachments = Column(JSONB, nullable=True)

    # Status e Prioridade
    status = Column(
        Enum(EmailStatus, name="emailstatus", create_type=True),
        nullable=False,
        default=EmailStatus.QUEUED,
    )
    priority = Column(
        Enum(EmailPriority, name="emailpriority", create_type=True),
        nullable=False,
        default=EmailPriority.NORMAL,
    )

    # Agendamento
    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    # Retry
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    # Resposta do provedor
    provider_message_id = Column(String(255), nullable=True, index=True)
    provider_response = Column(JSONB, nullable=True)

    # Bounce
    bounce_type = Column(
        Enum(BounceType, name="bouncetype", create_type=True),
        nullable=True,
    )
    bounce_reason = Column(Text, nullable=True)

    # Erro
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    bounced_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    config = relationship("EmailConfig", lazy="joined")
    template = relationship("EmailTemplate", lazy="joined")
    campaign = relationship("EmailCampaign", lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EmailQueue {self.to_email} ({self.status.value})>"

    @property
    def is_pending(self) -> bool:
        """Verifica se esta pendente."""
        return self.status in (EmailStatus.QUEUED, EmailStatus.PROCESSING)

    @property
    def is_sent(self) -> bool:
        """Verifica se foi enviado."""
        return self.status in (
            EmailStatus.SENT,
            EmailStatus.DELIVERED,
            EmailStatus.OPENED,
            EmailStatus.CLICKED,
        )

    @property
    def is_failed(self) -> bool:
        """Verifica se falhou."""
        return self.status in (EmailStatus.BOUNCED, EmailStatus.FAILED)

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        if self.status != EmailStatus.FAILED:
            return False
        return (self.retry_count or 0) < (self.max_retries or 3)

    @property
    def is_scheduled(self) -> bool:
        """Verifica se e agendado."""
        if not self.scheduled_at:
            return False
        return self.scheduled_at > datetime.utcnow()

    def mark_processing(self) -> None:
        """Marca como processando."""
        self.status = EmailStatus.PROCESSING

    def mark_sent(self, message_id: str | None = None) -> None:
        """Marca como enviado."""
        self.status = EmailStatus.SENT
        self.sent_at = datetime.utcnow()
        if message_id:
            self.provider_message_id = message_id

    def mark_delivered(self) -> None:
        """Marca como entregue."""
        self.status = EmailStatus.DELIVERED
        self.delivered_at = datetime.utcnow()

    def mark_opened(self) -> None:
        """Marca como aberto."""
        if self.status not in (EmailStatus.OPENED, EmailStatus.CLICKED):
            self.status = EmailStatus.OPENED
            self.opened_at = datetime.utcnow()

    def mark_clicked(self) -> None:
        """Marca como clicado."""
        self.status = EmailStatus.CLICKED
        self.clicked_at = datetime.utcnow()
        if not self.opened_at:
            self.opened_at = datetime.utcnow()

    def mark_bounced(
        self,
        bounce_type: BounceType,
        reason: str | None = None,
    ) -> None:
        """Marca como retornado."""
        self.status = EmailStatus.BOUNCED
        self.bounce_type = bounce_type
        self.bounce_reason = reason
        self.bounced_at = datetime.utcnow()

    def mark_failed(self, error_code: str, error_message: str) -> None:
        """Marca como falha."""
        self.status = EmailStatus.FAILED
        self.error_code = error_code
        self.error_message = error_message
        self.failed_at = datetime.utcnow()
        self.retry_count = (self.retry_count or 0) + 1

    def schedule_retry(self, next_retry: datetime | None = None) -> None:
        """Agenda retentativa."""
        if not self.can_retry:
            return
        self.status = EmailStatus.QUEUED
        self.next_retry_at = next_retry or datetime.utcnow()

    def cancel(self) -> None:
        """Cancela o email."""
        if self.is_pending:
            self.status = EmailStatus.CANCELLED
