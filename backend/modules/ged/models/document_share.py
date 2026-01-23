"""Model de Compartilhamento de Documento para GED."""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from modules.ged.models.document import Document


class ShareType(str, Enum):
    """Tipos de compartilhamento."""

    USUARIO = "usuario"  # Compartilhado com usuário específico
    GRUPO = "grupo"  # Compartilhado com grupo
    DEPARTAMENTO = "departamento"  # Compartilhado com departamento
    CONDOMINIO = "condominio"  # Compartilhado com todo condomínio
    EXTERNO = "externo"  # Compartilhado externamente (link público)
    EMAIL = "email"  # Compartilhado por email


class SharePermission(str, Enum):
    """Permissões de compartilhamento."""

    VISUALIZAR = "visualizar"
    BAIXAR = "baixar"
    COMENTAR = "comentar"
    EDITAR = "editar"
    COMPARTILHAR = "compartilhar"


class ShareStatus(str, Enum):
    """Status do compartilhamento."""

    ATIVO = "ativo"
    EXPIRADO = "expirado"
    REVOGADO = "revogado"
    PENDENTE = "pendente"


class DocumentShare(Base):
    """Model de Compartilhamento de Documento."""

    __tablename__ = "ged_document_shares"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("ged_documents.id"), nullable=False, index=True
    )

    # Tipo e destinatário
    share_type: Mapped[ShareType] = mapped_column(
        SQLEnum(ShareType, native_enum=False, create_constraint=False),
        default=ShareType.USUARIO
    )
    shared_with_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )  # user_id, group_id, etc.
    shared_with_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    shared_with_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Permissões
    permissions: Mapped[list] = mapped_column(
        JSONB, default=["visualizar"]
    )  # Lista de SharePermission
    can_reshare: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    status: Mapped[ShareStatus] = mapped_column(
        SQLEnum(ShareStatus, native_enum=False, create_constraint=False),
        default=ShareStatus.ATIVO
    )

    # Link externo
    share_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    share_token: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True
    )
    password_protected: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Limites
    max_downloads: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    max_views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    # Validade
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_perpetual: Mapped[bool] = mapped_column(Boolean, default=False)

    # Mensagem
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Acesso
    first_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0)

    # Metadados
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Auditoria
    shared_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    revoked_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )

    # Relacionamentos
    document: Mapped["Document"] = relationship("Document", back_populates="shares")

    def __repr__(self) -> str:
        """Representação string."""
        return f"<DocumentShare {self.document_id} -> {self.share_type.value}>"

    @property
    def is_active(self) -> bool:
        """Verifica se compartilhamento está ativo."""
        return self.status == ShareStatus.ATIVO

    @property
    def is_expired(self) -> bool:
        """Verifica se expirou."""
        if self.is_perpetual or not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_download_limit_reached(self) -> bool:
        """Verifica se atingiu limite de downloads."""
        if not self.max_downloads:
            return False
        return self.download_count >= self.max_downloads

    @property
    def is_view_limit_reached(self) -> bool:
        """Verifica se atingiu limite de visualizações."""
        if not self.max_views:
            return False
        return self.view_count >= self.max_views

    @property
    def remaining_downloads(self) -> Optional[int]:
        """Retorna downloads restantes."""
        if not self.max_downloads:
            return None
        return max(0, self.max_downloads - self.download_count)

    @property
    def remaining_views(self) -> Optional[int]:
        """Retorna visualizações restantes."""
        if not self.max_views:
            return None
        return max(0, self.max_views - self.view_count)

    def has_permission(self, permission: SharePermission) -> bool:
        """Verifica se tem permissão específica."""
        return permission.value in self.permissions

    def grant_permission(self, permission: SharePermission) -> None:
        """Concede permissão."""
        if permission.value not in self.permissions:
            self.permissions = self.permissions + [permission.value]

    def revoke_permission(self, permission: SharePermission) -> None:
        """Revoga permissão."""
        if permission.value in self.permissions:
            self.permissions = [p for p in self.permissions if p != permission.value]

    def revoke(self, revoked_by: str) -> None:
        """Revoga o compartilhamento."""
        self.status = ShareStatus.REVOGADO
        self.revoked_at = datetime.utcnow()
        self.revoked_by = revoked_by

    def extend_expiry(self, new_expiry: datetime) -> None:
        """Estende a validade."""
        self.expires_at = new_expiry
        if self.status == ShareStatus.EXPIRADO:
            self.status = ShareStatus.ATIVO

    def record_access(self) -> None:
        """Registra acesso."""
        now = datetime.utcnow()
        if not self.first_accessed_at:
            self.first_accessed_at = now
        self.last_accessed_at = now
        self.access_count += 1

    def record_view(self) -> bool:
        """Registra visualização. Retorna False se limite atingido."""
        if self.is_view_limit_reached:
            return False
        self.view_count += 1
        self.record_access()
        return True

    def record_download(self) -> bool:
        """Registra download. Retorna False se limite atingido."""
        if self.is_download_limit_reached:
            return False
        self.download_count += 1
        self.record_access()
        return True

    def send_notification(self) -> None:
        """Marca notificação como enviada."""
        self.notification_sent = True
        self.notification_sent_at = datetime.utcnow()

    def check_and_expire(self) -> bool:
        """Verifica e atualiza status de expiração."""
        if self.is_expired and self.status == ShareStatus.ATIVO:
            self.status = ShareStatus.EXPIRADO
            return True
        return False

    def is_valid_for_access(self) -> bool:
        """Verifica se compartilhamento é válido para acesso."""
        if not self.is_active:
            return False
        if self.is_expired:
            return False
        if self.is_view_limit_reached and self.is_download_limit_reached:
            return False
        return True
