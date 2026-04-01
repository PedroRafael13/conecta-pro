"""Email Template Model - Templates de Email HTML.

Sprint 32 - Automacoes Email.
"""

import re
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class TemplateCategory(StrEnum):
    """Categoria do template."""

    TRANSACTIONAL = "TRANSACTIONAL"  # Transacional (confirmacoes, recibos)
    MARKETING = "MARKETING"  # Marketing e promocoes
    NOTIFICATION = "NOTIFICATION"  # Notificacoes do sistema
    NEWSLETTER = "NEWSLETTER"  # Newsletter
    ONBOARDING = "ONBOARDING"  # Onboarding de usuarios
    BILLING = "BILLING"  # Cobranca e financeiro
    SUPPORT = "SUPPORT"  # Suporte ao cliente


class TemplateStatus(StrEnum):
    """Status do template."""

    DRAFT = "DRAFT"  # Rascunho
    ACTIVE = "ACTIVE"  # Ativo
    INACTIVE = "INACTIVE"  # Inativo
    ARCHIVED = "ARCHIVED"  # Arquivado


class EmailTemplate(Base):
    """Template de email HTML."""

    __tablename__ = "email_templates"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relacionamento com Config
    config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_configs.id"),
        nullable=True,
        index=True,
    )

    # Identificacao
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)  # Identificador unico
    description = Column(Text, nullable=True)

    # Categoria e Status
    category = Column(
        Enum(TemplateCategory, name="email_templatecategory", create_type=True),
        nullable=False,
        default=TemplateCategory.TRANSACTIONAL,
    )
    status = Column(
        Enum(TemplateStatus, name="email_templatestatus", create_type=True),
        nullable=False,
        default=TemplateStatus.DRAFT,
    )

    # Conteudo
    subject = Column(String(255), nullable=False)  # Assunto
    preheader = Column(String(255), nullable=True)  # Texto preview
    html_content = Column(Text, nullable=False)  # Conteudo HTML
    text_content = Column(Text, nullable=True)  # Versao texto puro

    # Variaveis/Placeholders
    # Ex: ["{{nome}}", "{{valor}}", "{{link}}"]
    variables = Column(ARRAY(String), nullable=True)
    variable_defaults = Column(JSONB, nullable=True)  # Valores default

    # Design
    header_image_url = Column(String(500), nullable=True)
    footer_html = Column(Text, nullable=True)
    css_inline = Column(Boolean, default=True, nullable=False)

    # A/B Testing
    is_variant = Column(Boolean, default=False, nullable=False)
    parent_template_id = Column(UUID(as_uuid=True), nullable=True)
    variant_name = Column(String(50), nullable=True)  # A, B, C, etc
    variant_weight = Column(Integer, default=50, nullable=True)  # Peso %

    # Metricas
    send_count = Column(Integer, default=0, nullable=False)
    open_count = Column(Integer, default=0, nullable=False)
    click_count = Column(Integer, default=0, nullable=False)
    unsubscribe_count = Column(Integer, default=0, nullable=False)

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    config = relationship("EmailConfig", lazy="joined", foreign_keys=[config_id])

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EmailTemplate {self.name} ({self.category.value})>"

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativo."""
        return self.status == TemplateStatus.ACTIVE and self.active

    @property
    def open_rate(self) -> float:
        """Calcula taxa de abertura."""
        if not self.send_count:
            return 0.0
        return ((self.open_count or 0) / self.send_count) * 100

    @property
    def click_rate(self) -> float:
        """Calcula taxa de cliques."""
        if not self.send_count:
            return 0.0
        return ((self.click_count or 0) / self.send_count) * 100

    @property
    def unsubscribe_rate(self) -> float:
        """Calcula taxa de descadastro."""
        if not self.send_count:
            return 0.0
        return ((self.unsubscribe_count or 0) / self.send_count) * 100

    @property
    def variable_count(self) -> int:
        """Retorna quantidade de variaveis."""
        return len(self.variables) if self.variables else 0

    def render(self, variables: dict) -> tuple[str, str]:
        """Renderiza template com variaveis.

        Args:
            variables: Dicionario com valores das variaveis.

        Returns:
            Tuple (subject, html_content).
        """
        subject = self.subject
        html = self.html_content
        text = self.text_content or ""

        for key, value in variables.items():
            placeholder = "{{" + str(key) + "}}"
            subject = subject.replace(placeholder, str(value))
            html = html.replace(placeholder, str(value))
            text = text.replace(placeholder, str(value))

        return subject, html, text

    def render_subject(self, variables: dict) -> str:
        """Renderiza apenas o assunto.

        Args:
            variables: Dicionario com valores.

        Returns:
            Assunto renderizado.
        """
        subject = self.subject
        for key, value in variables.items():
            placeholder = "{{" + str(key) + "}}"
            subject = subject.replace(placeholder, str(value))
        return subject

    def extract_variables(self) -> list[str]:
        """Extrai variaveis do template.

        Returns:
            Lista de nomes de variaveis.
        """
        pattern = r"\{\{(\w+)\}\}"
        found = set()

        # Busca no assunto
        found.update(re.findall(pattern, self.subject))

        # Busca no HTML
        found.update(re.findall(pattern, self.html_content))

        # Busca no texto
        if self.text_content:
            found.update(re.findall(pattern, self.text_content))

        return sorted(found)

    def increment_send(self) -> None:
        """Incrementa contador de envio."""
        self.send_count = (self.send_count or 0) + 1
        self.last_used_at = datetime.utcnow()

    def increment_open(self) -> None:
        """Incrementa contador de abertura."""
        self.open_count = (self.open_count or 0) + 1

    def increment_click(self) -> None:
        """Incrementa contador de clique."""
        self.click_count = (self.click_count or 0) + 1

    def activate(self) -> None:
        """Ativa o template."""
        self.status = TemplateStatus.ACTIVE
        self.active = True

    def deactivate(self) -> None:
        """Desativa o template."""
        self.status = TemplateStatus.INACTIVE
