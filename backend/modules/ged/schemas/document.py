"""Schemas Pydantic para Document."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from modules.ged.models.document import (
    DocumentType,
    DocumentStatus,
    DocumentCategory,
    DocumentConfidentiality,
    FileType,
)


class DocumentBase(BaseModel):
    """Schema base de Document."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    folder_id: str
    document_type: DocumentType = Field(default=DocumentType.OUTRO)
    category: DocumentCategory = Field(default=DocumentCategory.OUTRO)
    confidentiality: DocumentConfidentiality = Field(
        default=DocumentConfidentiality.INTERNO
    )
    condominium_id: Optional[str] = None
    contract_id: Optional[str] = None
    employee_id: Optional[str] = None
    client_id: Optional[str] = None
    resident_id: Optional[str] = None
    occurrence_id: Optional[str] = None
    is_public: bool = False
    inherit_folder_permissions: bool = True
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_perpetual: bool = False
    requires_approval: bool = False
    requires_signature: bool = False
    signature_deadline: Optional[datetime] = None
    external_reference: Optional[str] = Field(None, max_length=100)
    metadata: Optional[dict] = None
    custom_fields: Optional[dict] = None


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
    thumbnail_path: Optional[str] = None
    preview_path: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema para atualizar Document."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    document_type: Optional[DocumentType] = None
    category: Optional[DocumentCategory] = None
    confidentiality: Optional[DocumentConfidentiality] = None
    is_public: Optional[bool] = None
    inherit_folder_permissions: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_perpetual: Optional[bool] = None
    requires_approval: Optional[bool] = None
    requires_signature: Optional[bool] = None
    signature_deadline: Optional[datetime] = None
    external_reference: Optional[str] = Field(None, max_length=100)
    metadata: Optional[dict] = None
    custom_fields: Optional[dict] = None


class DocumentResponse(BaseModel):
    """Schema de resposta de Document."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: Optional[str]
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
    thumbnail_path: Optional[str]
    preview_path: Optional[str]
    current_version: int
    version_count: int
    is_latest: bool
    condominium_id: Optional[str]
    contract_id: Optional[str]
    employee_id: Optional[str]
    client_id: Optional[str]
    resident_id: Optional[str]
    occurrence_id: Optional[str]
    owner_id: str
    is_public: bool
    inherit_folder_permissions: bool
    valid_from: Optional[date]
    valid_until: Optional[date]
    is_perpetual: bool
    requires_approval: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    is_signed: bool
    signature_count: int
    requires_signature: bool
    signature_deadline: Optional[datetime]
    is_ocr_processed: bool
    ocr_confidence: Optional[float]
    is_indexed: bool
    search_keywords: Optional[List[str]]
    external_reference: Optional[str]
    view_count: int
    download_count: int
    share_count: int
    last_viewed_at: Optional[datetime]
    last_downloaded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    archived_at: Optional[datetime]
    created_by: str

    # Computed
    is_active: bool
    is_expired: bool
    is_valid: bool
    is_pending_approval: bool
    is_pending_signature: bool
    file_size_mb: float
    file_size_kb: float
    days_until_expiry: Optional[int]
    display_name: str


class DocumentListResponse(BaseModel):
    """Schema de lista de Documents."""

    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentFilter(BaseModel):
    """Schema de filtro de Documents."""

    folder_id: Optional[str] = None
    document_type: Optional[DocumentType] = None
    category: Optional[DocumentCategory] = None
    status: Optional[DocumentStatus] = None
    confidentiality: Optional[DocumentConfidentiality] = None
    file_type: Optional[FileType] = None
    condominium_id: Optional[str] = None
    contract_id: Optional[str] = None
    owner_id: Optional[str] = None
    is_public: Optional[bool] = None
    is_signed: Optional[bool] = None
    is_expired: Optional[bool] = None
    requires_approval: Optional[bool] = None
    requires_signature: Optional[bool] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None


class DocumentMoveRequest(BaseModel):
    """Schema para mover documento."""

    folder_id: str


class DocumentApprovalRequest(BaseModel):
    """Schema para aprovar/rejeitar documento."""

    approved: bool
    reason: Optional[str] = Field(None, max_length=1000)


class DocumentSearchRequest(BaseModel):
    """Schema para busca avançada."""

    query: str = Field(..., min_length=1, max_length=500)
    folder_id: Optional[str] = None
    document_types: Optional[List[DocumentType]] = None
    categories: Optional[List[DocumentCategory]] = None
    file_types: Optional[List[FileType]] = None
    include_ocr: bool = True
    include_metadata: bool = True
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
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
    description: Optional[str] = Field(None, max_length=5000)
    folder_id: str
    document_type: DocumentType = Field(default=DocumentType.OUTRO)
    category: DocumentCategory = Field(default=DocumentCategory.OUTRO)
    confidentiality: DocumentConfidentiality = Field(
        default=DocumentConfidentiality.INTERNO
    )
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class DocumentOCRResult(BaseModel):
    """Resultado de OCR."""

    text: str
    confidence: float
    keywords: List[str]
    language: Optional[str]
    pages_processed: int
