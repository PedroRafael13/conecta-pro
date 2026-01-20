"""Model de Documento para GED."""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4
import hashlib

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Date,
    Text,
    ForeignKey,
    Integer,
    Float,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from modules.ged.models.folder import Folder
    from modules.ged.models.document_version import DocumentVersion
    from modules.ged.models.document_share import DocumentShare
    from modules.ged.models.document_tag import DocumentTag
    from modules.ged.models.document_signature import DocumentSignature


class DocumentType(str, Enum):
    """Tipos de documento."""

    CONTRATO = "contrato"
    PROPOSTA = "proposta"
    NOTA_FISCAL = "nota_fiscal"
    BOLETO = "boleto"
    COMPROVANTE = "comprovante"
    CERTIDAO = "certidao"
    PROCURACAO = "procuracao"
    ATA = "ata"
    REGULAMENTO = "regulamento"
    MANUAL = "manual"
    RELATORIO = "relatorio"
    PLANILHA = "planilha"
    APRESENTACAO = "apresentacao"
    IMAGEM = "imagem"
    PLANTA = "planta"
    PROJETO = "projeto"
    LAUDO = "laudo"
    ORCAMENTO = "orcamento"
    CORRESPONDENCIA = "correspondencia"
    OUTRO = "outro"


class DocumentStatus(str, Enum):
    """Status do documento."""

    RASCUNHO = "rascunho"
    PENDENTE_APROVACAO = "pendente_aprovacao"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    PUBLICADO = "publicado"
    ARQUIVADO = "arquivado"
    EXPIRADO = "expirado"
    EXCLUIDO = "excluido"


class DocumentCategory(str, Enum):
    """Categorias de documento."""

    ADMINISTRATIVO = "administrativo"
    FINANCEIRO = "financeiro"
    JURIDICO = "juridico"
    OPERACIONAL = "operacional"
    RH = "rh"
    COMERCIAL = "comercial"
    TECNICO = "tecnico"
    FISCAL = "fiscal"
    SEGURANCA = "seguranca"
    OUTRO = "outro"


class DocumentConfidentiality(str, Enum):
    """Níveis de confidencialidade."""

    PUBLICO = "publico"
    INTERNO = "interno"
    CONFIDENCIAL = "confidencial"
    RESTRITO = "restrito"
    SECRETO = "secreto"


class FileType(str, Enum):
    """Tipos de arquivo."""

    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"
    PPT = "ppt"
    PPTX = "pptx"
    TXT = "txt"
    CSV = "csv"
    XML = "xml"
    JSON = "json"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    MP4 = "mp4"
    AVI = "avi"
    MP3 = "mp3"
    WAV = "wav"
    ZIP = "zip"
    RAR = "rar"
    OUTRO = "outro"


class Document(Base):
    """Model de Documento."""

    __tablename__ = "ged_documents"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pasta
    folder_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("ged_folders.id"), nullable=False, index=True
    )

    # Classificação
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType), default=DocumentType.OUTRO
    )
    category: Mapped[DocumentCategory] = mapped_column(
        SQLEnum(DocumentCategory), default=DocumentCategory.OUTRO
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus), default=DocumentStatus.RASCUNHO
    )
    confidentiality: Mapped[DocumentConfidentiality] = mapped_column(
        SQLEnum(DocumentConfidentiality), default=DocumentConfidentiality.INTERNO
    )

    # Arquivo
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    file_type: Mapped[FileType] = mapped_column(
        SQLEnum(FileType), default=FileType.OUTRO
    )
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256

    # Thumbnail (para imagens e PDFs)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    preview_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Versionamento
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    version_count: Mapped[int] = mapped_column(Integer, default=1)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)

    # Vínculo com entidades
    condominium_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True, index=True
    )
    contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    employee_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    client_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)
    resident_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    occurrence_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )

    # Proprietário e permissões
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    inherit_folder_permissions: Mapped[bool] = mapped_column(Boolean, default=True)
    permissions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Validade
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_perpetual: Mapped[bool] = mapped_column(Boolean, default=False)

    # Aprovação
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Assinatura digital
    is_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    signature_count: Mapped[int] = mapped_column(Integer, default=0)
    requires_signature: Mapped[bool] = mapped_column(Boolean, default=False)
    signature_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # OCR e Indexação
    is_ocr_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ocr_processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    search_keywords: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String), nullable=True
    )

    # Metadados
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    external_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Estatísticas
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_downloaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Auditoria
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    updated_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )
    archived_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )

    # Relacionamentos
    folder: Mapped["Folder"] = relationship("Folder", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion", back_populates="document", cascade="all, delete-orphan"
    )
    shares: Mapped[List["DocumentShare"]] = relationship(
        "DocumentShare", back_populates="document", cascade="all, delete-orphan"
    )
    tags: Mapped[List["DocumentTag"]] = relationship(
        "DocumentTag",
        secondary="ged_document_tag_associations",
        back_populates="documents",
    )
    signatures: Mapped[List["DocumentSignature"]] = relationship(
        "DocumentSignature", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<Document {self.code}: {self.title}>"

    @property
    def is_active(self) -> bool:
        """Verifica se documento está ativo."""
        return self.status not in [
            DocumentStatus.ARQUIVADO,
            DocumentStatus.EXCLUIDO,
            DocumentStatus.EXPIRADO,
        ]

    @property
    def is_expired(self) -> bool:
        """Verifica se documento expirou."""
        if self.is_perpetual or not self.valid_until:
            return False
        return date.today() > self.valid_until

    @property
    def is_valid(self) -> bool:
        """Verifica se documento está válido."""
        if self.is_perpetual:
            return True
        today = date.today()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True

    @property
    def is_pending_approval(self) -> bool:
        """Verifica se aguarda aprovação."""
        return self.status == DocumentStatus.PENDENTE_APROVACAO

    @property
    def is_pending_signature(self) -> bool:
        """Verifica se aguarda assinatura."""
        return self.requires_signature and not self.is_signed

    @property
    def file_size_mb(self) -> float:
        """Retorna tamanho em MB."""
        return round(self.file_size_bytes / (1024 * 1024), 2)

    @property
    def file_size_kb(self) -> float:
        """Retorna tamanho em KB."""
        return round(self.file_size_bytes / 1024, 2)

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Retorna dias até expiração."""
        if self.is_perpetual or not self.valid_until:
            return None
        delta = self.valid_until - date.today()
        return delta.days

    @property
    def display_name(self) -> str:
        """Nome de exibição com extensão."""
        return f"{self.file_name}.{self.file_extension}"

    def publish(self) -> None:
        """Publica o documento."""
        self.status = DocumentStatus.PUBLICADO
        self.published_at = datetime.utcnow()

    def archive(self, archived_by: str) -> None:
        """Arquiva o documento."""
        self.status = DocumentStatus.ARQUIVADO
        self.archived_at = datetime.utcnow()
        self.archived_by = archived_by

    def unarchive(self) -> None:
        """Desarquiva o documento."""
        self.status = DocumentStatus.PUBLICADO
        self.archived_at = None
        self.archived_by = None

    def soft_delete(self) -> None:
        """Marca documento como excluído."""
        self.status = DocumentStatus.EXCLUIDO
        self.deleted_at = datetime.utcnow()

    def submit_for_approval(self) -> None:
        """Submete para aprovação."""
        self.status = DocumentStatus.PENDENTE_APROVACAO
        self.requires_approval = True

    def approve(self, approved_by: str) -> None:
        """Aprova o documento."""
        self.status = DocumentStatus.APROVADO
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.rejection_reason = None

    def reject(self, reason: str) -> None:
        """Rejeita o documento."""
        self.status = DocumentStatus.REJEITADO
        self.rejection_reason = reason

    def mark_as_signed(self) -> None:
        """Marca como assinado."""
        self.is_signed = True
        self.signature_count += 1

    def increment_view(self) -> None:
        """Incrementa visualizações."""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()

    def increment_download(self) -> None:
        """Incrementa downloads."""
        self.download_count += 1
        self.last_downloaded_at = datetime.utcnow()

    def increment_share(self) -> None:
        """Incrementa compartilhamentos."""
        self.share_count += 1

    def set_ocr_result(self, text: str, confidence: float) -> None:
        """Define resultado do OCR."""
        self.ocr_text = text
        self.ocr_confidence = confidence
        self.is_ocr_processed = True
        self.ocr_processed_at = datetime.utcnow()

    def mark_as_indexed(self, keywords: List[str] = None) -> None:
        """Marca como indexado."""
        self.is_indexed = True
        self.indexed_at = datetime.utcnow()
        if keywords:
            self.search_keywords = keywords

    def create_new_version(self) -> int:
        """Cria nova versão e retorna o número."""
        self.version_count += 1
        self.current_version = self.version_count
        return self.current_version

    def check_expiry(self) -> bool:
        """Verifica e atualiza status de expiração."""
        if self.is_expired and self.status != DocumentStatus.EXPIRADO:
            self.status = DocumentStatus.EXPIRADO
            return True
        return False

    @staticmethod
    def calculate_checksum(content: bytes) -> str:
        """Calcula checksum SHA-256."""
        return hashlib.sha256(content).hexdigest()

    def verify_checksum(self, content: bytes) -> bool:
        """Verifica integridade do arquivo."""
        return self.checksum == self.calculate_checksum(content)
