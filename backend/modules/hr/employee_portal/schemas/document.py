"""Schemas para documentos do funcionário."""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from modules.hr.employee_portal.models import DocumentType, DocumentStatus


class DocumentCreate(BaseModel):
    """Schema para criação de documento."""

    employee_id: UUID
    document_type: DocumentType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    tags: List[str] = Field(default_factory=list)

    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    file_type: Optional[str] = Field(None, max_length=50)
    file_hash: Optional[str] = Field(None, max_length=64)

    reference_date: Optional[date] = None
    reference_month: Optional[int] = Field(None, ge=1, le=12)
    reference_year: Optional[int] = Field(None, ge=2000, le=2100)

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_perpetual: bool = False

    is_visible: bool = True
    requires_acknowledgement: bool = False
    is_confidential: bool = False
    is_mandatory: bool = False
    requires_signature: bool = False

    parent_document_id: Optional[UUID] = None
    related_documents: List[UUID] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    """Schema para atualização de documento."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_perpetual: Optional[bool] = None

    is_visible: Optional[bool] = None
    requires_acknowledgement: Optional[bool] = None
    is_confidential: Optional[bool] = None
    is_mandatory: Optional[bool] = None
    requires_signature: Optional[bool] = None

    related_documents: Optional[List[UUID]] = None
    metadata: Optional[dict] = None


class DocumentResponse(BaseModel):
    """Schema de resposta para documento."""

    id: UUID
    condominio_id: UUID
    employee_id: UUID
    document_code: str
    document_type: str
    status: str

    title: str
    description: Optional[str]
    category: Optional[str]
    tags: List[str]

    file_name: str
    file_path: str
    file_size: Optional[int]
    file_type: Optional[str]
    file_hash: Optional[str]

    reference_date: Optional[date]
    reference_month: Optional[int]
    reference_year: Optional[int]

    valid_from: Optional[date]
    valid_until: Optional[date]
    is_perpetual: bool
    is_expired: bool
    days_until_expiry: int

    is_visible: bool
    requires_acknowledgement: bool
    is_confidential: bool
    is_mandatory: bool
    requires_signature: bool

    first_viewed_at: Optional[datetime]
    view_count: int
    last_viewed_at: Optional[datetime]
    downloaded_at: Optional[datetime]
    download_count: int

    acknowledged_at: Optional[datetime]
    acknowledgement_ip: Optional[str]
    acknowledgement_device: Optional[str]

    signed_at: Optional[datetime]
    signed_by: Optional[UUID]

    notification_sent: bool
    notification_sent_at: Optional[datetime]

    parent_document_id: Optional[UUID]
    related_documents: List[UUID]
    metadata: dict

    is_published: bool
    needs_acknowledgement: bool
    needs_signature: bool

    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DocumentSummary(BaseModel):
    """Resumo do documento para listagem."""

    id: UUID
    document_code: str
    document_type: str
    title: str
    status: str
    file_type: Optional[str]
    file_size: Optional[int]
    reference_date: Optional[date]
    is_visible: bool
    requires_acknowledgement: bool
    acknowledged: bool
    requires_signature: bool
    signed: bool
    is_expired: bool
    created_at: datetime


class DocumentListResponse(BaseModel):
    """Lista paginada de documentos."""

    items: List[DocumentSummary]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentAcknowledgeRequest(BaseModel):
    """Request para dar ciência no documento."""

    ip_address: Optional[str] = None
    device_info: Optional[str] = None


class DocumentSignRequest(BaseModel):
    """Request para assinar documento."""

    signature_data: str = Field(..., min_length=1)
    signature_type: str = Field(default="digital")  # digital, biometric
    certificate_data: Optional[str] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None


class DocumentFilterRequest(BaseModel):
    """Filtros para busca de documentos."""

    employee_id: Optional[UUID] = None
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    category: Optional[str] = None
    reference_year: Optional[int] = Field(None, ge=2000, le=2100)
    reference_month: Optional[int] = Field(None, ge=1, le=12)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_visible: Optional[bool] = None
    requires_acknowledgement: Optional[bool] = None
    requires_signature: Optional[bool] = None
    only_unread: bool = False
    only_pending_ack: bool = False
    only_pending_signature: bool = False
    only_expired: bool = False
    tags: Optional[List[str]] = None
    search: Optional[str] = Field(None, max_length=100)


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

    document_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    action: str = Field(..., pattern="^(archive|delete|publish|acknowledge)$")


class DocumentBulkActionResponse(BaseModel):
    """Resposta de ação em lote."""

    total: int
    success: int
    failed: int
    errors: List[dict]
