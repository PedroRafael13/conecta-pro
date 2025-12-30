"""Schemas Pydantic para DocumentVersion."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from modules.ged.models.document_version import VersionType, VersionStatus


class DocumentVersionBase(BaseModel):
    """Schema base de DocumentVersion."""

    version_label: Optional[str] = Field(None, max_length=50)
    version_type: VersionType = Field(default=VersionType.MINOR)
    change_summary: Optional[str] = Field(None, max_length=500)
    change_notes: Optional[str] = Field(None, max_length=5000)
    metadata: Optional[dict] = None


class DocumentVersionCreate(DocumentVersionBase):
    """Schema para criar DocumentVersion."""

    document_id: str
    version_number: int = Field(..., ge=1)
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=1000)
    file_size_bytes: int = Field(..., ge=1)
    mime_type: str = Field(..., min_length=1, max_length=100)
    checksum: str = Field(..., min_length=64, max_length=64)
    created_by: str
    thumbnail_path: Optional[str] = None
    changes_from_previous: Optional[dict] = None


class DocumentVersionResponse(BaseModel):
    """Schema de resposta de DocumentVersion."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    version_label: Optional[str]
    version_type: VersionType
    status: VersionStatus
    is_current: bool
    file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    checksum: str
    thumbnail_path: Optional[str]
    change_summary: Optional[str]
    change_notes: Optional[str]
    changes_from_previous: Optional[dict]
    ocr_text: Optional[str]
    ocr_confidence: Optional[float]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    view_count: int
    download_count: int
    created_at: datetime
    archived_at: Optional[datetime]
    created_by: str

    # Computed
    is_active: bool
    file_size_mb: float
    display_version: str


class DocumentVersionListResponse(BaseModel):
    """Schema de lista de DocumentVersions."""

    items: List[DocumentVersionResponse]
    total: int


class DocumentVersionCompare(BaseModel):
    """Schema de comparação de versões."""

    version_from: int
    version_to: int
    size_diff: int
    same_content: bool
    changes: Optional[dict]


class DocumentVersionRestoreRequest(BaseModel):
    """Schema para restaurar versão."""

    create_backup: bool = True
    change_notes: Optional[str] = Field(None, max_length=500)
