"""Modelo de Anexo de Ocorrência."""

import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.occurrences.models.occurrence import Occurrence


class AttachmentType(str, enum.Enum):
    """Tipo de anexo."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PDF = "pdf"
    ARCHIVE = "archive"
    OTHER = "other"


class OccurrenceAttachment(Base):
    """Modelo de Anexo de Ocorrência."""

    __tablename__ = "occurrence_attachments"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento
    occurrence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("occurrences.id"), nullable=False, index=True
    )

    # Arquivo
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[AttachmentType] = mapped_column(
        Enum(AttachmentType), default=AttachmentType.OTHER
    )
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    extension: Mapped[Optional[str]] = mapped_column(String(20))
    file_size: Mapped[int] = mapped_column(Integer, default=0)

    # Storage
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_bucket: Mapped[Optional[str]] = mapped_column(String(100))
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # Metadados
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Upload
    uploaded_by_id: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_by_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Verificação
    is_scanned: Mapped[bool] = mapped_column(Boolean, default=False)
    scan_result: Mapped[Optional[str]] = mapped_column(String(50))
    is_safe: Mapped[bool] = mapped_column(Boolean, default=True)

    # Hash
    file_hash: Mapped[Optional[str]] = mapped_column(String(64))
    hash_algorithm: Mapped[Optional[str]] = mapped_column(String(20))

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relacionamentos
    occurrence: Mapped["Occurrence"] = relationship(
        "Occurrence", back_populates="attachments"
    )

    def __init__(self, **kwargs):
        """Inicializa o anexo."""
        super().__init__(**kwargs)
        if self.original_filename and not self.extension:
            self._extract_extension()
        if self.original_filename and not self.file_type:
            self._detect_file_type()

    def _extract_extension(self) -> None:
        """Extrai extensão do nome do arquivo."""
        if "." in self.original_filename:
            self.extension = self.original_filename.rsplit(".", 1)[-1].lower()

    def _detect_file_type(self) -> None:
        """Detecta tipo do arquivo pela extensão."""
        if not self.extension:
            self.file_type = AttachmentType.OTHER
            return

        image_exts = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"}
        video_exts = {"mp4", "avi", "mov", "wmv", "flv", "webm", "mkv"}
        audio_exts = {"mp3", "wav", "ogg", "flac", "aac", "wma"}
        doc_exts = {"doc", "docx", "txt", "rtf", "odt"}
        sheet_exts = {"xls", "xlsx", "csv", "ods"}
        archive_exts = {"zip", "rar", "7z", "tar", "gz"}

        ext = self.extension.lower()
        if ext in image_exts:
            self.file_type = AttachmentType.IMAGE
        elif ext in video_exts:
            self.file_type = AttachmentType.VIDEO
        elif ext in audio_exts:
            self.file_type = AttachmentType.AUDIO
        elif ext == "pdf":
            self.file_type = AttachmentType.PDF
        elif ext in doc_exts:
            self.file_type = AttachmentType.DOCUMENT
        elif ext in sheet_exts:
            self.file_type = AttachmentType.SPREADSHEET
        elif ext in archive_exts:
            self.file_type = AttachmentType.ARCHIVE
        else:
            self.file_type = AttachmentType.OTHER

    def mark_as_scanned(self, is_safe: bool, result: str = None) -> None:
        """Marca como escaneado."""
        self.is_scanned = True
        self.is_safe = is_safe
        self.scan_result = result

    def soft_delete(self) -> None:
        """Deleta o anexo (soft delete)."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def set_hash(self, file_hash: str, algorithm: str = "sha256") -> None:
        """Define hash do arquivo."""
        self.file_hash = file_hash
        self.hash_algorithm = algorithm

    def set_dimensions(self, width: int, height: int) -> None:
        """Define dimensões (para imagens/vídeos)."""
        self.width = width
        self.height = height

    def set_duration(self, seconds: int) -> None:
        """Define duração (para áudio/vídeo)."""
        self.duration_seconds = seconds

    @property
    def file_size_mb(self) -> float:
        """Retorna tamanho em MB."""
        return self.file_size / (1024 * 1024)

    @property
    def file_size_kb(self) -> float:
        """Retorna tamanho em KB."""
        return self.file_size / 1024

    @property
    def file_size_formatted(self) -> str:
        """Retorna tamanho formatado."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size_kb:.1f} KB"
        else:
            return f"{self.file_size_mb:.1f} MB"

    @property
    def is_image(self) -> bool:
        """Verifica se é imagem."""
        return self.file_type == AttachmentType.IMAGE

    @property
    def is_video(self) -> bool:
        """Verifica se é vídeo."""
        return self.file_type == AttachmentType.VIDEO

    @property
    def is_audio(self) -> bool:
        """Verifica se é áudio."""
        return self.file_type == AttachmentType.AUDIO

    @property
    def is_document(self) -> bool:
        """Verifica se é documento."""
        return self.file_type in [
            AttachmentType.DOCUMENT,
            AttachmentType.SPREADSHEET,
            AttachmentType.PDF,
        ]

    @property
    def is_media(self) -> bool:
        """Verifica se é mídia."""
        return self.file_type in [
            AttachmentType.IMAGE,
            AttachmentType.VIDEO,
            AttachmentType.AUDIO,
        ]

    @property
    def duration_formatted(self) -> Optional[str]:
        """Retorna duração formatada."""
        if not self.duration_seconds:
            return None
        minutes, seconds = divmod(self.duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
