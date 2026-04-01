"""Email Config Model - Configuracao de Email.

Sprint 32 - Automacoes Email.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class EmailProvider(StrEnum):
    """Provedor de email."""

    SMTP = "SMTP"  # SMTP generico
    SENDGRID = "SENDGRID"  # SendGrid
    MAILGUN = "MAILGUN"  # Mailgun
    AWS_SES = "AWS_SES"  # Amazon SES
    POSTMARK = "POSTMARK"  # Postmark
    MAILCHIMP = "MAILCHIMP"  # Mailchimp Transactional
    SPARKPOST = "SPARKPOST"  # SparkPost


class EmailConfigStatus(StrEnum):
    """Status da configuracao."""

    PENDING = "PENDING"  # Pendente verificacao
    VERIFIED = "VERIFIED"  # Verificado e ativo
    FAILED = "FAILED"  # Falha na verificacao
    SUSPENDED = "SUSPENDED"  # Suspenso
    DISABLED = "DISABLED"  # Desabilitado


class EmailConfig(Base):
    """Configuracao de provedor de email."""

    __tablename__ = "email_configs"

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

    # Provedor
    provider = Column(
        Enum(EmailProvider, name="emailprovider", create_type=True),
        nullable=False,
        default=EmailProvider.SMTP,
    )

    # Status
    status = Column(
        Enum(EmailConfigStatus, name="emailconfigstatus", create_type=True),
        nullable=False,
        default=EmailConfigStatus.PENDING,
    )

    # Configuracao SMTP
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587, nullable=True)
    smtp_username = Column(String(255), nullable=True)
    smtp_password = Column(String(500), nullable=True)  # Encriptado
    smtp_use_tls = Column(Boolean, default=True, nullable=True)
    smtp_use_ssl = Column(Boolean, default=False, nullable=True)

    # Configuracao API (SendGrid, Mailgun, etc)
    api_key = Column(String(500), nullable=True)  # Encriptado
    api_endpoint = Column(String(500), nullable=True)
    api_region = Column(String(50), nullable=True)  # Para AWS SES

    # Remetente padrao
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(100), nullable=True)
    reply_to = Column(String(255), nullable=True)

    # Dominio verificado
    domain = Column(String(255), nullable=True)
    domain_verified = Column(Boolean, default=False, nullable=False)
    dkim_enabled = Column(Boolean, default=False, nullable=False)
    spf_enabled = Column(Boolean, default=False, nullable=False)

    # Rate Limiting
    max_per_hour = Column(Integer, default=500, nullable=False)
    max_per_day = Column(Integer, default=10000, nullable=False)
    current_hour_count = Column(Integer, default=0, nullable=False)
    current_day_count = Column(Integer, default=0, nullable=False)
    last_rate_reset = Column(DateTime(timezone=True), nullable=True)

    # Metricas
    total_sent = Column(Integer, default=0, nullable=False)
    total_delivered = Column(Integer, default=0, nullable=False)
    total_bounced = Column(Integer, default=0, nullable=False)
    total_complaints = Column(Integer, default=0, nullable=False)

    # Configuracoes extras (JSON)
    settings = Column(JSONB, nullable=True)

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
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EmailConfig {self.name} ({self.provider.value})>"

    @property
    def is_verified(self) -> bool:
        """Verifica se esta verificado."""
        return self.status == EmailConfigStatus.VERIFIED and self.active

    @property
    def can_send(self) -> bool:
        """Verifica se pode enviar emails."""
        if not self.is_verified:
            return False
        hour_ok = (self.current_hour_count or 0) < (self.max_per_hour or 500)
        day_ok = (self.current_day_count or 0) < (self.max_per_day or 10000)
        return hour_ok and day_ok

    @property
    def bounce_rate(self) -> float:
        """Calcula taxa de bounce."""
        if not self.total_sent:
            return 0.0
        return ((self.total_bounced or 0) / self.total_sent) * 100

    @property
    def delivery_rate(self) -> float:
        """Calcula taxa de entrega."""
        if not self.total_sent:
            return 0.0
        return ((self.total_delivered or 0) / self.total_sent) * 100

    def increment_sent(self) -> None:
        """Incrementa contadores de envio."""
        self.total_sent = (self.total_sent or 0) + 1
        self.current_hour_count = (self.current_hour_count or 0) + 1
        self.current_day_count = (self.current_day_count or 0) + 1

    def reset_hourly_count(self) -> None:
        """Reseta contador horario."""
        self.current_hour_count = 0
        self.last_rate_reset = datetime.utcnow()

    def reset_daily_count(self) -> None:
        """Reseta contador diario."""
        self.current_day_count = 0
        self.current_hour_count = 0
        self.last_rate_reset = datetime.utcnow()

    def mark_verified(self) -> None:
        """Marca como verificado."""
        self.status = EmailConfigStatus.VERIFIED
        self.verified_at = datetime.utcnow()

    def mark_failed(self, reason: str | None = None) -> None:
        """Marca como falha."""
        self.status = EmailConfigStatus.FAILED
        if reason and self.settings is None:
            self.settings = {}
        if reason:
            self.settings["last_error"] = reason

    def get_masked_credentials(self) -> dict:
        """Retorna credenciais mascaradas para exibicao."""
        result = {}
        if self.smtp_password:
            result["smtp_password"] = "****"  # noqa: S105
        if self.api_key:
            key = self.api_key
            if len(key) > 8:
                result["api_key"] = f"{key[:4]}...{key[-4:]}"
            else:
                result["api_key"] = "****"
        return result
