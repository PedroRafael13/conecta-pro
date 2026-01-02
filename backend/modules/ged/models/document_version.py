"""Model de Versão de Documento para GED."""

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
    Float,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from modules.ged.models.document import Document


class VersionType(str, Enum):
    """Tipos de versão."""

    MAJOR = "major"  # Mudança significativa
    MINOR = "minor"  # Pequena alteração
    PATCH = "patch"  # Correção
    REVISION = "revision"  # Revisão


class VersionStatus(str, Enum):
    """Status da versão."""

    ATIVA = "ativa"
    ARQUIVADA = "arquivada"
    OBSOLETA = "obsoleta"


class DocumentVersion(Base):
    """Model de Versão de Documento."""

    __tablename__ = "ged_document_versions"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("ged_documents.id"), nullable=False, index=True
    )

    # Versão
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_label: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Ex: "1.0.0", "v2"
    version_type: Mapped[VersionType] = mapped_column(
        SQLEnum(VersionType), default=VersionType.MINOR
    )
    status: Mapped[VersionStatus] = mapped_column(
        SQLEnum(VersionStatus), default=VersionStatus.ATIVA
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)

    # Arquivo
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    # Thumbnail
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Mudanças
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    change_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changes_from_previous: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # {"added": [], "removed": [], "modified": []}

    # OCR
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Aprovação
    approved_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Estatísticas
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Auditoria
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    # Relacionamentos
    document: Mapped["Document"] = relationship("Document", back_populates="versions")

    def __repr__(self) -> str:
        """Representação string."""
        return f"<DocumentVersion {self.document_id} v{self.version_number}>"

    @property
    def is_active(self) -> bool:
        """Verifica se versão está ativa."""
        return self.status == VersionStatus.ATIVA

    @property
    def file_size_mb(self) -> float:
        """Retorna tamanho em MB."""
        return round(self.file_size_bytes / (1024 * 1024), 2)

    @property
    def display_version(self) -> str:
        """Retorna versão para exibição."""
        if self.version_label:
            return self.version_label
        return f"v{self.version_number}"

    def set_as_current(self) -> None:
        """Define como versão atual."""
        self.is_current = True
        self.status = VersionStatus.ATIVA

    def archive(self) -> None:
        """Arquiva a versão."""
        self.status = VersionStatus.ARQUIVADA
        self.is_current = False
        self.archived_at = datetime.utcnow()

    def mark_as_obsolete(self) -> None:
        """Marca como obsoleta."""
        self.status = VersionStatus.OBSOLETA
        self.is_current = False

    def approve(self, approved_by: str) -> None:
        """Aprova a versão."""
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()

    def increment_view(self) -> None:
        """Incrementa visualizações."""
        self.view_count += 1

    def increment_download(self) -> None:
        """Incrementa downloads."""
        self.download_count += 1

    def compare_with(self, other: "DocumentVersion") -> dict:
        """Compara com outra versão."""
        return {
            "version_from": other.version_number,
            "version_to": self.version_number,
            "size_diff": self.file_size_bytes - other.file_size_bytes,
            "same_content": self.checksum == other.checksum,
            "changes": self.changes_from_previous,
        }
