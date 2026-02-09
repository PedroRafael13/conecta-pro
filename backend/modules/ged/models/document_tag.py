"""Model de Tag de Documento para GED."""

import re
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.ged.models.document import Document


class TagType(StrEnum):
    """Tipos de tag."""

    SISTEMA = "sistema"  # Tag do sistema (imutável)
    CATEGORIA = "categoria"  # Tag de categoria
    PROJETO = "projeto"  # Tag de projeto
    CLIENTE = "cliente"  # Tag de cliente
    DEPARTAMENTO = "departamento"  # Tag de departamento
    STATUS = "status"  # Tag de status
    PRIORIDADE = "prioridade"  # Tag de prioridade
    USUARIO = "usuario"  # Tag criada por usuário


class TagColor(StrEnum):
    """Cores predefinidas para tags."""

    VERMELHO = "#EF4444"
    LARANJA = "#F97316"
    AMARELO = "#EAB308"
    VERDE = "#22C55E"
    AZUL = "#3B82F6"
    INDIGO = "#6366F1"
    ROXO = "#A855F7"
    ROSA = "#EC4899"
    CINZA = "#6B7280"


# Tabela de associação Document-Tag (many-to-many)
document_tag_association = Table(
    "ged_document_tag_associations",
    Base.metadata,
    Column(
        "document_id",
        UUID(as_uuid=False),
        ForeignKey("ged_documents.id"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        UUID(as_uuid=False),
        ForeignKey("ged_document_tags.id"),
        primary_key=True,
    ),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("created_by", UUID(as_uuid=False), nullable=False),
)


class DocumentTag(Base):
    """Model de Tag de Documento."""

    __tablename__ = "ged_document_tags"

    # Identificação
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classificação
    tag_type: Mapped[TagType] = mapped_column(SQLEnum(TagType), default=TagType.USUARIO)

    # Hierarquia (para tags de categoria)
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("ged_document_tags.id"), nullable=True
    )

    # Visual
    color: Mapped[str] = mapped_column(String(7), default="#6B7280")
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Escopo
    condominium_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True, index=True)
    is_global: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    # Estatísticas
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Ordem
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Auditoria
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    # Relacionamentos
    parent: Mapped[Optional["DocumentTag"]] = relationship("DocumentTag", remote_side=[id], back_populates="children")  # noqa: A003
    children: Mapped[list["DocumentTag"]] = relationship("DocumentTag", back_populates="parent")
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="ged_document_tag_associations",
        back_populates="tags",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<DocumentTag {self.slug}: {self.name}>"

    @property
    def is_category(self) -> bool:
        """Verifica se é tag de categoria."""
        return self.tag_type == TagType.CATEGORIA

    @property
    def has_children(self) -> bool:
        """Verifica se tem tags filhas."""
        return len(self.children) > 0 if self.children else False

    @property
    def full_path(self) -> str:
        """Retorna caminho completo da tag."""
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return self.name

    def increment_usage(self) -> None:
        """Incrementa uso da tag."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()

    def decrement_usage(self) -> None:
        """Decrementa uso da tag."""
        if self.usage_count > 0:
            self.usage_count -= 1

    def deactivate(self) -> None:
        """Desativa a tag."""
        self.is_active = False

    def activate(self) -> None:
        """Ativa a tag."""
        self.is_active = True

    def set_color(self, color: str) -> None:
        """Define cor da tag."""
        if color.startswith("#") and len(color) == 7:
            self.color = color

    @staticmethod
    def generate_slug(name: str) -> str:
        """Gera slug a partir do nome."""
        slug = name.lower()
        slug = re.sub(r"[àáâãäå]", "a", slug)
        slug = re.sub(r"[èéêë]", "e", slug)
        slug = re.sub(r"[ìíîï]", "i", slug)
        slug = re.sub(r"[òóôõö]", "o", slug)
        slug = re.sub(r"[ùúûü]", "u", slug)
        slug = re.sub(r"[ç]", "c", slug)
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug
