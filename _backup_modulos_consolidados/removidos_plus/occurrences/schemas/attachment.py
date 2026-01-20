"""Schemas para OccurrenceAttachment."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from modules.occurrences.models.attachment import AttachmentType


class AttachmentCreate(BaseModel):
    """Schema para criação de anexo."""

    model_config = ConfigDict(use_enum_values=True)

    occurrence_id: str
    filename: str
    original_filename: str
    file_type: Optional[AttachmentType] = None
    mime_type: Optional[str] = None
    file_size: int = 0

    # Storage
    storage_path: str
    storage_bucket: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    # Metadados
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None
    metadata: Optional[dict] = None

    # Upload
    uploaded_by_id: str
    uploaded_by_name: str

    # Hash
    file_hash: Optional[str] = None
    hash_algorithm: Optional[str] = None


class AttachmentResponse(BaseModel):
    """Schema de resposta de anexo."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: str
    occurrence_id: str
    filename: str
    original_filename: str
    file_type: str
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    file_size: int

    # Storage
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    # Metadados
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None

    # Upload
    uploaded_by_id: str
    uploaded_by_name: str

    # Verificação
    is_scanned: bool
    is_safe: bool

    # Computed
    file_size_formatted: Optional[str] = None
    duration_formatted: Optional[str] = None
    is_image: Optional[bool] = None
    is_video: Optional[bool] = None
    is_document: Optional[bool] = None

    # Controle
    is_active: bool
    created_at: datetime


class AttachmentListResponse(BaseModel):
    """Schema de lista de anexos."""

    items: list[AttachmentResponse]
    total: int
