"""Email Subscription Model - Gerenciamento de Inscricoes.

Sprint 32 - Automacoes Email.
"""

import enum
import hashlib
import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models import Base


class SubscriptionStatus(str, enum.Enum):
    """Status da inscricao."""

    PENDING = "PENDING"  # Pendente confirmacao
    ACTIVE = "ACTIVE"  # Ativo
    UNSUBSCRIBED = "UNSUBSCRIBED"  # Descadastrado
    BOUNCED = "BOUNCED"  # Email invalido
    COMPLAINED = "COMPLAINED"  # Marcou como spam
    CLEANED = "CLEANED"  # Removido por limpeza


class SubscriptionSource(str, enum.Enum):
    """Origem da inscricao."""

    SIGNUP = "SIGNUP"  # Cadastro no site
    IMPORT = "IMPORT"  # Importacao de lista
    API = "API"  # Via API
    MANUAL = "MANUAL"  # Cadastro manual
    PURCHASE = "PURCHASE"  # Compra
    LEAD = "LEAD"  # Conversao de lead
    REFERRAL = "REFERRAL"  # Indicacao


class EmailSubscription(Base):
    """Inscricao de email (lista de contatos)."""

    __tablename__ = "email_subscriptions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Email (unique por tenant)
    email = Column(String(255), nullable=False, index=True)
    email_hash = Column(String(64), nullable=False, index=True)  # SHA256

    # Dados do contato
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(200), nullable=True)

    # Status
    status = Column(
        Enum(SubscriptionStatus, name="subscriptionstatus", create_type=True),
        nullable=False,
        default=SubscriptionStatus.PENDING,
    )

    # Origem
    source = Column(
        Enum(SubscriptionSource, name="subscriptionsource", create_type=True),
        nullable=False,
        default=SubscriptionSource.SIGNUP,
    )
    source_details = Column(Text, nullable=True)  # Detalhes da origem

    # Confirmacao (double opt-in)
    confirmed = Column(Boolean, default=False, nullable=False)
    confirmation_token = Column(String(100), nullable=True)
    confirmation_sent_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)

    # Descadastro
    unsubscribe_token = Column(String(100), nullable=True, index=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribe_reason = Column(Text, nullable=True)

    # Preferencias
    # Ex: ["marketing", "newsletter", "product_updates"]
    subscribed_lists = Column(ARRAY(String), nullable=True)
    unsubscribed_lists = Column(ARRAY(String), nullable=True)

    # Preferencias de frequencia
    email_frequency = Column(String(50), default="normal", nullable=True)

    # Tags e segmentacao
    tags = Column(ARRAY(String), nullable=True)
    custom_fields = Column(JSONB, nullable=True)

    # Metricas de engajamento
    total_received = Column(DateTime(timezone=True), default=0, nullable=False)
    total_opened = Column(DateTime(timezone=True), default=0, nullable=False)
    total_clicked = Column(DateTime(timezone=True), default=0, nullable=False)
    last_email_at = Column(DateTime(timezone=True), nullable=True)
    last_open_at = Column(DateTime(timezone=True), nullable=True)
    last_click_at = Column(DateTime(timezone=True), nullable=True)

    # Score de engajamento (0-100)
    engagement_score = Column(DateTime(timezone=True), default=50, nullable=False)

    # IP e localizacao
    signup_ip = Column(String(45), nullable=True)
    country = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    gdpr_consent = Column(Boolean, default=False, nullable=False)
    gdpr_consent_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EmailSubscription {self.email} ({self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativo."""
        return self.status == SubscriptionStatus.ACTIVE and self.active

    @property
    def is_confirmed(self) -> bool:
        """Verifica se esta confirmado."""
        return self.confirmed and self.status == SubscriptionStatus.ACTIVE

    @property
    def can_receive_email(self) -> bool:
        """Verifica se pode receber emails."""
        return self.is_active and self.confirmed

    @property
    def full_name(self) -> str:
        """Retorna nome completo."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else ""

    @staticmethod
    def hash_email(email: str) -> str:
        """Gera hash do email.

        Args:
            email: Email a hashear.

        Returns:
            Hash SHA256.
        """
        return hashlib.sha256(email.lower().strip().encode()).hexdigest()

    def generate_confirmation_token(self) -> str:
        """Gera token de confirmacao.

        Returns:
            Token gerado.
        """
        token = secrets.token_urlsafe(32)
        self.confirmation_token = token
        self.confirmation_sent_at = datetime.utcnow()
        return token

    def generate_unsubscribe_token(self) -> str:
        """Gera token de descadastro.

        Returns:
            Token gerado.
        """
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
        return self.unsubscribe_token

    def confirm(self) -> None:
        """Confirma a inscricao."""
        self.confirmed = True
        self.confirmed_at = datetime.utcnow()
        self.status = SubscriptionStatus.ACTIVE
        self.confirmation_token = None

    def unsubscribe(self, reason: Optional[str] = None) -> None:
        """Descadastra o email.

        Args:
            reason: Motivo do descadastro.
        """
        self.status = SubscriptionStatus.UNSUBSCRIBED
        self.unsubscribed_at = datetime.utcnow()
        self.unsubscribe_reason = reason
        self.active = False

    def resubscribe(self) -> None:
        """Recadastra o email."""
        if self.status == SubscriptionStatus.UNSUBSCRIBED:
            self.status = SubscriptionStatus.ACTIVE
            self.active = True
            self.unsubscribed_at = None
            self.unsubscribe_reason = None

    def mark_bounced(self) -> None:
        """Marca como bounce."""
        self.status = SubscriptionStatus.BOUNCED
        self.active = False

    def mark_complained(self) -> None:
        """Marca como reclamacao (spam)."""
        self.status = SubscriptionStatus.COMPLAINED
        self.active = False

    def subscribe_to_list(self, list_name: str) -> None:
        """Inscreve em uma lista.

        Args:
            list_name: Nome da lista.
        """
        if self.subscribed_lists is None:
            self.subscribed_lists = []
        if list_name not in self.subscribed_lists:
            self.subscribed_lists = self.subscribed_lists + [list_name]

        # Remove da lista de descadastrados
        if self.unsubscribed_lists and list_name in self.unsubscribed_lists:
            self.unsubscribed_lists = [
                item for item in self.unsubscribed_lists if item != list_name
            ]

    def unsubscribe_from_list(self, list_name: str) -> None:
        """Descadastra de uma lista.

        Args:
            list_name: Nome da lista.
        """
        if self.unsubscribed_lists is None:
            self.unsubscribed_lists = []
        if list_name not in self.unsubscribed_lists:
            self.unsubscribed_lists = self.unsubscribed_lists + [list_name]

        # Remove da lista de inscritos
        if self.subscribed_lists and list_name in self.subscribed_lists:
            self.subscribed_lists = [
                item for item in self.subscribed_lists if item != list_name
            ]

    def is_subscribed_to(self, list_name: str) -> bool:
        """Verifica se esta inscrito em uma lista.

        Args:
            list_name: Nome da lista.

        Returns:
            True se inscrito.
        """
        if not self.subscribed_lists:
            return False
        if self.unsubscribed_lists and list_name in self.unsubscribed_lists:
            return False
        return list_name in self.subscribed_lists

    def add_tag(self, tag: str) -> None:
        """Adiciona tag.

        Args:
            tag: Tag a adicionar.
        """
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags = self.tags + [tag]

    def remove_tag(self, tag: str) -> None:
        """Remove tag.

        Args:
            tag: Tag a remover.
        """
        if self.tags and tag in self.tags:
            self.tags = [t for t in self.tags if t != tag]

    def record_engagement(self, opened: bool = False, clicked: bool = False) -> None:
        """Registra engajamento.

        Args:
            opened: Se abriu email.
            clicked: Se clicou em link.
        """
        now = datetime.utcnow()
        self.last_email_at = now

        if opened:
            self.last_open_at = now
        if clicked:
            self.last_click_at = now
