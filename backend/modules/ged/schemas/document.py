"""Schemas Pydantic para Document."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.ged.models.document import (
    DocumentCategory,
    DocumentConfidentiality,
    DocumentStatus,
    DocumentType,
    FileType,
)


class DocumentBase(BaseModel):
    """Schema base de Document."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    folder_id: str
    document_type: DocumentType = Field(default=DocumentType.OUTRO)
    category: DocumentCategory = Field(default=DocumentCategory.OUTRO)
    confidentiality: DocumentConfidentiality = Field(default=DocumentConfidentiality.INTERNO)
    condominium_id: str | None = None
    contract_id: str | None = None
    employee_id: str | None = None
    client_id: str | None = None
    resident_id: str | None = None
    occurrence_id: str | None = None
    is_public: bool = False
    inherit_folder_permissions: bool = True
    valid_from: date | None = None
    valid_until: date | None = None
    is_perpetual: bool = False
    requires_approval: bool = False
    requires_signature: bool = False
    signature_deadline: datetime | None = None
    external_reference: str | None = Field(None, max_length=100)
    metadata: dict | None = None
    custom_fields: dict | None = None


class DocumentCreate(DocumentBase):
    """Schema para criar Document."""

    file_name: str = Field(..., min_length=1, max_length=255)
    file_extension: str = Field(..., min_length=1, max_length=20)
    file_type: FileType = Field(default=FileType.OUTRO)
    file_path: str = Field(..., min_length=1, max_length=1000)
    file_size_bytes: int = Field(..., ge=1)
    mime_type: str = Field(..., min_length=1, max_length=100)
    checksum: str = Field(..., min_length=64, max_length=64)
    owner_id: str
    created_by: str
    thumbnail_path: str | None = None
    preview_path: str | None = None


class DocumentUpdate(BaseModel):
    """Schema para atualizar Document."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    document_type: DocumentType | None = None
    category: DocumentCategory | None = None
    confidentiality: DocumentConfidentiality | None = None
    is_public: bool | None = None
    inherit_folder_permissions: bool | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    is_perpetual: bool | None = None
    requires_approval: bool | None = None
    requires_signature: bool | None = None
    signature_deadline: datetime | None = None
    external_reference: str | None = Field(None, max_length=100)
    metadata: dict | None = None
    custom_fields: dict | None = None


class DocumentResponse(BaseModel):
    """Schema de resposta de Document."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: str | None
    folder_id: str
    document_type: DocumentType
    category: DocumentCategory
    status: DocumentStatus
    confidentiality: DocumentConfidentiality
    file_name: str
    file_extension: str
    file_type: FileType
    file_path: str
    file_size_bytes: int
    mime_type: str
    checksum: str
    thumbnail_path: str | None
    preview_path: str | None
    current_version: int
    version_count: int
    is_latest: bool
    condominium_id: str | None
    contract_id: str | None
    employee_id: str | None
    client_id: str | None
    resident_id: str | None
    occurrence_id: str | None
    owner_id: str
    is_public: bool
    inherit_folder_permissions: bool
    valid_from: date | None
    valid_until: date | None
    is_perpetual: bool
    requires_approval: bool
    approved_by: str | None
    approved_at: datetime | None
    rejection_reason: str | None
    is_signed: bool
    signature_count: int
    requires_signature: bool
    signature_deadline: datetime | None
    is_ocr_processed: bool
    ocr_confidence: float | None
    is_indexed: bool
    search_keywords: list[str] | None
    external_reference: str | None
    view_count: int
    download_count: int
    share_count: int
    last_viewed_at: datetime | None
    last_downloaded_at: datetime | None
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None
    archived_at: datetime | None
    created_by: str

    # Computed
    is_active: bool
    is_expired: bool
    is_valid: bool
    is_pending_approval: bool
    is_pending_signature: bool
    file_size_mb: float
    file_size_kb: float
    days_until_expiry: int | None
    display_name: str


class DocumentListResponse(BaseModel):
    """Schema de lista de Documents."""

    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentFilter(BaseModel):
    """Schema de filtro de Documents."""

    folder_id: str | None = None
    document_type: DocumentType | None = None
    category: DocumentCategory | None = None
    status: DocumentStatus | None = None
    confidentiality: DocumentConfidentiality | None = None
    file_type: FileType | None = None
    condominium_id: str | None = None
    contract_id: str | None = None
    owner_id: str | None = None
    is_public: bool | None = None
    is_signed: bool | None = None
    is_expired: bool | None = None
    requires_approval: bool | None = None
    requires_signature: bool | None = None
    search: str | None = None
    tags: list[str] | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None


class DocumentMoveRequest(BaseModel):
    """Schema para mover documento."""

    folder_id: str


class DocumentApprovalRequest(BaseModel):
    """Schema para aprovar/rejeitar documento."""

    approved: bool
    reason: str | None = Field(None, max_length=1000)


class DocumentSearchRequest(BaseModel):
    """Schema para busca avançada."""

    query: str = Field(..., min_length=1, max_length=500)
    folder_id: str | None = None
    document_types: list[DocumentType] | None = None
    categories: list[DocumentCategory] | None = None
    file_types: list[FileType] | None = None
    include_ocr: bool = True
    include_metadata: bool = True
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = Field(default=20, ge=1, le=100)


class DocumentStats(BaseModel):
    """Estatísticas de documentos."""

    total_documents: int = 0
    by_status: dict = {}
    by_type: dict = {}
    by_category: dict = {}
    by_confidentiality: dict = {}
    total_size_bytes: int = 0
    total_size_mb: float = 0
    pending_approval: int = 0
    pending_signature: int = 0
    expired: int = 0
    expiring_soon: int = 0
    avg_views: float = 0
    avg_downloads: float = 0


class DocumentUploadRequest(BaseModel):
    """Schema para upload de documento."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    folder_id: str
    document_type: DocumentType = Field(default=DocumentType.OUTRO)
    category: DocumentCategory = Field(default=DocumentCategory.OUTRO)
    confidentiality: DocumentConfidentiality = Field(default=DocumentConfidentiality.INTERNO)
    tags: list[str] | None = None
    metadata: dict | None = None


class DocumentOCRResult(BaseModel):
    """Resultado de OCR."""

    text: str
    confidence: float
    keywords: list[str]
    language: str | None
    pages_processed: int
