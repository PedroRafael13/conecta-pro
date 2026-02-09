"""Model de Pasta/Diretório para GED."""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.ged.models.document import Document


class FolderType(StrEnum):
    """Tipos de pasta."""

    SISTEMA = "sistema"  # Pasta do sistema (não pode ser deletada)
    CONDOMINIO = "condominio"  # Pasta de condomínio
    CONTRATO = "contrato"  # Pasta de contrato
    FUNCIONARIO = "funcionario"  # Pasta de funcionário
    CLIENTE = "cliente"  # Pasta de cliente
    PROJETO = "projeto"  # Pasta de projeto
    DEPARTAMENTO = "departamento"  # Pasta de departamento
    PESSOAL = "pessoal"  # Pasta pessoal do usuário
    COMPARTILHADA = "compartilhada"  # Pasta compartilhada
    ARQUIVO = "arquivo"  # Pasta de arquivo morto


class FolderStatus(StrEnum):
    """Status da pasta."""

    ATIVA = "ativa"
    ARQUIVADA = "arquivada"
    BLOQUEADA = "bloqueada"
    EXCLUIDA = "excluida"


class FolderPermission(StrEnum):
    """Permissões de pasta."""

    LEITURA = "leitura"
    ESCRITA = "escrita"
    EXCLUSAO = "exclusao"
    ADMIN = "admin"


class Folder(Base):
    """Model de Pasta para organização de documentos."""

    __tablename__ = "ged_folders"

    # Identificação
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Hierarquia
    parent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("ged_folders.id"), nullable=True)
    path: Mapped[str] = mapped_column(String(1000), nullable=False, default="/")
    level: Mapped[int] = mapped_column(Integer, default=0)

    # Classificação
    folder_type: Mapped[FolderType] = mapped_column(
        SQLEnum(FolderType, native_enum=False, create_constraint=False), default=FolderType.CONDOMINIO
    )
    status: Mapped[FolderStatus] = mapped_column(
        SQLEnum(FolderStatus, native_enum=False, create_constraint=False), default=FolderStatus.ATIVA
    )

    # Vínculo com entidades
    condominium_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True, index=True)
    contract_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    employee_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    client_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)

    # Permissões
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    inherit_permissions: Mapped[bool] = mapped_column(Boolean, default=True)
    permissions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {"user_id": ["leitura", "escrita"], "role": ["leitura"]}

    # Configurações
    max_file_size_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allowed_extensions: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    # ["pdf", "doc", "docx", "xls", "xlsx"]
    require_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_versioning: Mapped[bool] = mapped_column(Boolean, default=True)

    # Retenção
    retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retention_policy: Mapped[str | None] = mapped_column(String(100), nullable=True)
    delete_after_retention: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadados
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Estatísticas
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    subfolder_count: Mapped[int] = mapped_column(Integer, default=0)
    total_size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Auditoria
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    updated_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    archived_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)

    # Relacionamentos
    parent: Mapped[Optional["Folder"]] = relationship("Folder", remote_side=[id], back_populates="children")  # noqa: A003
    children: Mapped[list["Folder"]] = relationship("Folder", back_populates="parent", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="folder", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<Folder {self.code}: {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se pasta está ativa."""
        return self.status == FolderStatus.ATIVA

    @property
    def is_archived(self) -> bool:
        """Verifica se pasta está arquivada."""
        return self.status == FolderStatus.ARQUIVADA

    @property
    def is_system(self) -> bool:
        """Verifica se é pasta do sistema."""
        return self.folder_type == FolderType.SISTEMA

    @property
    def is_root(self) -> bool:
        """Verifica se é pasta raiz."""
        return self.parent_id is None

    @property
    def full_path(self) -> str:
        """Retorna caminho completo."""
        return f"{self.path}/{self.name}" if self.path != "/" else f"/{self.name}"

    @property
    def total_size_mb(self) -> float:
        """Retorna tamanho total em MB."""
        return round(self.total_size_bytes / (1024 * 1024), 2)

    def update_path(self, parent_path: str = "/") -> None:
        """Atualiza o caminho baseado no pai."""
        self.path = parent_path
        self.level = len(parent_path.split("/")) - 1 if parent_path != "/" else 0

    def archive(self, archived_by: str) -> None:
        """Arquiva a pasta."""
        self.status = FolderStatus.ARQUIVADA
        self.archived_at = datetime.utcnow()
        self.archived_by = archived_by

    def unarchive(self) -> None:
        """Desarquiva a pasta."""
        self.status = FolderStatus.ATIVA
        self.archived_at = None
        self.archived_by = None

    def block(self) -> None:
        """Bloqueia a pasta."""
        self.status = FolderStatus.BLOQUEADA

    def unblock(self) -> None:
        """Desbloqueia a pasta."""
        self.status = FolderStatus.ATIVA

    def soft_delete(self) -> None:
        """Marca pasta como excluída."""
        self.status = FolderStatus.EXCLUIDA
        self.deleted_at = datetime.utcnow()

    def increment_document_count(self, size_bytes: int = 0) -> None:
        """Incrementa contagem de documentos."""
        self.document_count += 1
        self.total_size_bytes += size_bytes

    def decrement_document_count(self, size_bytes: int = 0) -> None:
        """Decrementa contagem de documentos."""
        if self.document_count > 0:
            self.document_count -= 1
        if self.total_size_bytes >= size_bytes:
            self.total_size_bytes -= size_bytes

    def increment_subfolder_count(self) -> None:
        """Incrementa contagem de subpastas."""
        self.subfolder_count += 1

    def decrement_subfolder_count(self) -> None:
        """Decrementa contagem de subpastas."""
        if self.subfolder_count > 0:
            self.subfolder_count -= 1

    def has_permission(self, user_id: str, permission: FolderPermission) -> bool:
        """Verifica se usuário tem permissão."""
        if self.owner_id == user_id:
            return True
        if self.is_public and permission == FolderPermission.LEITURA:
            return True
        if not self.permissions:
            return False
        user_perms = self.permissions.get(user_id, [])
        return permission.value in user_perms or "admin" in user_perms

    def grant_permission(self, user_id: str, permission: FolderPermission) -> None:
        """Concede permissão ao usuário."""
        if not self.permissions:
            self.permissions = {}
        if user_id not in self.permissions:
            self.permissions[user_id] = []
        if permission.value not in self.permissions[user_id]:
            self.permissions[user_id].append(permission.value)

    def revoke_permission(self, user_id: str, permission: FolderPermission) -> None:
        """Revoga permissão do usuário."""
        if self.permissions and user_id in self.permissions:
            if permission.value in self.permissions[user_id]:
                self.permissions[user_id].remove(permission.value)

    def is_extension_allowed(self, extension: str) -> bool:
        """Verifica se extensão é permitida."""
        if not self.allowed_extensions:
            return True
        return extension.lower().lstrip(".") in [ext.lower() for ext in self.allowed_extensions]

    def is_size_allowed(self, size_bytes: int) -> bool:
        """Verifica se tamanho é permitido."""
        if not self.max_file_size_mb:
            return True
        return size_bytes <= (self.max_file_size_mb * 1024 * 1024)
