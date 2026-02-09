"""Schemas para documentos do funcionário."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.employee_portal.models import DocumentStatus, DocumentType


class DocumentCreate(BaseModel):
    """Schema para criação de documento."""

    employee_id: UUID
    document_type: DocumentType
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=50)
    tags: list[str] = Field(default_factory=list)

    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int | None = Field(None, ge=0)
    file_type: str | None = Field(None, max_length=50)
    file_hash: str | None = Field(None, max_length=64)

    reference_date: date | None = None
    reference_month: int | None = Field(None, ge=1, le=12)
    reference_year: int | None = Field(None, ge=2000, le=2100)

    valid_from: date | None = None
    valid_until: date | None = None
    is_perpetual: bool = False

    is_visible: bool = True
    requires_acknowledgement: bool = False
    is_confidential: bool = False
    is_mandatory: bool = False
    requires_signature: bool = False

    parent_document_id: UUID | None = None
    related_documents: list[UUID] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    """Schema para atualização de documento."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    category: str | None = Field(None, max_length=50)
    tags: list[str] | None = None

    valid_from: date | None = None
    valid_until: date | None = None
    is_perpetual: bool | None = None

    is_visible: bool | None = None
    requires_acknowledgement: bool | None = None
    is_confidential: bool | None = None
    is_mandatory: bool | None = None
    requires_signature: bool | None = None

    related_documents: list[UUID] | None = None
    metadata: dict | None = None


class DocumentResponse(BaseModel):
    """Schema de resposta para documento."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    document_code: str
    document_type: str
    status: str

    title: str
    description: str | None
    category: str | None
    tags: list[str]

    file_name: str
    file_path: str
    file_size: int | None
    file_type: str | None
    file_hash: str | None

    reference_date: date | None
    reference_month: int | None
    reference_year: int | None

    valid_from: date | None
    valid_until: date | None
    is_perpetual: bool
    is_expired: bool
    days_until_expiry: int

    is_visible: bool
    requires_acknowledgement: bool
    is_confidential: bool
    is_mandatory: bool
    requires_signature: bool

    first_viewed_at: datetime | None
    view_count: int
    last_viewed_at: datetime | None
    downloaded_at: datetime | None
    download_count: int

    acknowledged_at: datetime | None
    acknowledgement_ip: str | None
    acknowledgement_device: str | None

    signed_at: datetime | None
    signed_by: UUID | None

    notification_sent: bool
    notification_sent_at: datetime | None

    parent_document_id: UUID | None
    related_documents: list[UUID]
    metadata: dict

    is_published: bool
    needs_acknowledgement: bool
    needs_signature: bool

    created_at: datetime
    updated_at: datetime | None
    published_at: datetime | None

    model_config = {"from_attributes": True}


class DocumentSummary(BaseModel):
    """Resumo do documento para listagem."""

    id: UUID
    document_code: str
    document_type: str
    title: str
    status: str
    file_type: str | None
    file_size: int | None
    reference_date: date | None
    is_visible: bool
    requires_acknowledgement: bool
    acknowledged: bool
    requires_signature: bool
    signed: bool
    is_expired: bool
    created_at: datetime


class DocumentListResponse(BaseModel):
    """Lista paginada de documentos."""

    items: list[DocumentSummary]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentAcknowledgeRequest(BaseModel):
    """Request para dar ciência no documento."""

    ip_address: str | None = None
    device_info: str | None = None


class DocumentSignRequest(BaseModel):
    """Request para assinar documento."""

    signature_data: str = Field(..., min_length=1)
    signature_type: str = Field(default="digital")  # digital, biometric
    certificate_data: str | None = None
    ip_address: str | None = None
    device_info: str | None = None


class DocumentFilterRequest(BaseModel):
    """Filtros para busca de documentos."""

    employee_id: UUID | None = None
    document_type: DocumentType | None = None
    status: DocumentStatus | None = None
    category: str | None = None
    reference_year: int | None = Field(None, ge=2000, le=2100)
    reference_month: int | None = Field(None, ge=1, le=12)
    valid_from: date | None = None
    valid_until: date | None = None
    is_visible: bool | None = None
    requires_acknowledgement: bool | None = None
    requires_signature: bool | None = None
    only_unread: bool = False
    only_pending_ack: bool = False
    only_pending_signature: bool = False
    only_expired: bool = False
    tags: list[str] | None = None
    search: str | None = Field(None, max_length=100)


class DocumentUploadResponse(BaseModel):
    """Resposta do upload de documento."""

    document_id: UUID
    document_code: str
    file_name: str
    file_path: str
    file_size: int
    file_hash: str
    uploaded_at: datetime


class DocumentDownloadResponse(BaseModel):
    """Resposta para download de documento."""

    document_id: UUID
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    download_url: str
    expires_at: datetime


class DocumentBulkActionRequest(BaseModel):
    """Request para ação em lote de documentos."""

    document_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    action: str = Field(..., pattern="^(archive|delete|publish|acknowledge)$")


class DocumentBulkActionResponse(BaseModel):
    """Resposta de ação em lote."""

    total: int
    success: int
    failed: int
    errors: list[dict]
