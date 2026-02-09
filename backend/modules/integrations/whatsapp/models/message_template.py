"""Message Template Model - Templates de Mensagem WhatsApp.

Sprint 31 - Automacoes WhatsApp.
"""

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

    MARKETING = "MARKETING"  # Marketing e promocoes
    UTILITY = "UTILITY"  # Utilitario (lembretes, confirmacoes)
    AUTHENTICATION = "AUTHENTICATION"  # Autenticacao (OTP)
    SERVICE = "SERVICE"  # Servico ao cliente
    TRANSACTIONAL = "TRANSACTIONAL"  # Transacional (boletos, notas)


class TemplateStatus(StrEnum):
    """Status do template."""

    DRAFT = "DRAFT"  # Rascunho
    PENDING = "PENDING"  # Pendente aprovacao Meta
    APPROVED = "APPROVED"  # Aprovado
    REJECTED = "REJECTED"  # Rejeitado
    DISABLED = "DISABLED"  # Desabilitado


class TemplateType(StrEnum):
    """Tipo de conteudo do template."""

    TEXT = "TEXT"  # Apenas texto
    IMAGE = "IMAGE"  # Imagem com texto
    VIDEO = "VIDEO"  # Video com texto
    DOCUMENT = "DOCUMENT"  # Documento (PDF, etc)
    LOCATION = "LOCATION"  # Localizacao
    INTERACTIVE = "INTERACTIVE"  # Botoes interativos


class MessageTemplate(Base):
    """Template de mensagem WhatsApp."""

    __tablename__ = "wa_templates"

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
        ForeignKey("wa_configs.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(100), nullable=False, index=True)
    template_id = Column(String(100), nullable=True)  # ID no Meta
    description = Column(Text, nullable=True)

    # Categoria e Tipo
    category = Column(
        Enum(TemplateCategory, name="templatecategory", create_type=True),
        nullable=False,
        default=TemplateCategory.UTILITY,
    )
    template_type = Column(
        Enum(TemplateType, name="templatetype", create_type=True),
        nullable=False,
        default=TemplateType.TEXT,
    )

    # Status
    status = Column(
        Enum(TemplateStatus, name="templatestatus", create_type=True),
        nullable=False,
        default=TemplateStatus.DRAFT,
    )
    rejection_reason = Column(Text, nullable=True)

    # Conteudo
    language = Column(String(10), default="pt_BR", nullable=False)
    header_text = Column(String(60), nullable=True)  # Cabecalho (opcional)
    body_text = Column(Text, nullable=False)  # Corpo da mensagem
    footer_text = Column(String(60), nullable=True)  # Rodape (opcional)

    # Variaveis/Placeholders
    # Ex: ["{{1}}", "{{2}}"] para "Ola {{1}}, seu boleto {{2}}"
    variables = Column(ARRAY(String), nullable=True)
    variable_examples = Column(JSONB, nullable=True)  # Exemplos para aprovacao

    # Midia (para templates com imagem/video/documento)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)

    # Botoes (para templates interativos)
    # Ex: [{"type": "QUICK_REPLY", "text": "Sim"}, {"type": "URL", ...}]
    buttons = Column(JSONB, nullable=True)

    # Uso e Metricas
    use_count = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Tags para organizacao
    tags = Column(ARRAY(String), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # Template do sistema

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    config = relationship("WhatsAppConfig", lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<MessageTemplate {self.name} ({self.status.value})>"

    @property
    def is_approved(self) -> bool:
        """Verifica se esta aprovado."""
        return self.status == TemplateStatus.APPROVED and self.active

    @property
    def is_ready_to_send(self) -> bool:
        """Verifica se pode ser usado para envio."""
        return self.is_approved and self.config.is_connected if self.config else False

    @property
    def variable_count(self) -> int:
        """Retorna quantidade de variaveis."""
        return len(self.variables) if self.variables else 0

    def render(self, variables: dict) -> str:
        """Renderiza template com variaveis.

        Args:
            variables: Dicionario com valores das variaveis.
                       Ex: {"1": "João", "2": "R$ 150,00"}

        Returns:
            Texto renderizado.
        """
        text = self.body_text
        for key, value in variables.items():
            placeholder = "{{" + str(key) + "}}"
            text = text.replace(placeholder, str(value))
        return text

    def increment_use(self) -> None:
        """Incrementa contador de uso."""
        self.use_count += 1
        self.last_used_at = datetime.utcnow()

    def mark_approved(self, template_id: str) -> None:
        """Marca como aprovado pelo Meta."""
        self.status = TemplateStatus.APPROVED
        self.template_id = template_id
        self.approved_at = datetime.utcnow()
        self.rejection_reason = None

    def mark_rejected(self, reason: str) -> None:
        """Marca como rejeitado."""
        self.status = TemplateStatus.REJECTED
        self.rejection_reason = reason
