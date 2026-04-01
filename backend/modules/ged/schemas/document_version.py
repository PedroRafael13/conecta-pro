"""Schemas Pydantic para DocumentVersion."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.ged.models.document_version import VersionStatus, VersionType


class DocumentVersionBase(BaseModel):
    """Schema base de DocumentVersion."""

    version_label: str | None = Field(None, max_length=50)
    version_type: VersionType = Field(default=VersionType.MINOR)
    change_summary: str | None = Field(None, max_length=500)
    change_notes: str | None = Field(None, max_length=5000)
    metadata: dict | None = None


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
    thumbnail_path: str | None = None
    changes_from_previous: dict | None = None


class DocumentVersionResponse(BaseModel):
    """Schema de resposta de DocumentVersion."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    version_label: str | None
    version_type: VersionType
    status: VersionStatus
    is_current: bool
    file_name: str
    file_path: str
    file_size_bytes: int
    mime_type: str
    checksum: str
    thumbnail_path: str | None
    change_summary: str | None
    change_notes: str | None
    changes_from_previous: dict | None
    ocr_text: str | None
    ocr_confidence: float | None
    approved_by: str | None
    approved_at: datetime | None
    view_count: int
    download_count: int
    created_at: datetime
    archived_at: datetime | None
    created_by: str

    # Computed
    is_active: bool
    file_size_mb: float
    display_version: str


class DocumentVersionListResponse(BaseModel):
    """Schema de lista de DocumentVersions."""

    items: list[DocumentVersionResponse]
    total: int


class DocumentVersionCompare(BaseModel):
    """Schema de comparação de versões."""

    version_from: int
    version_to: int
    size_diff: int
    same_content: bool
    changes: dict | None


class DocumentVersionRestoreRequest(BaseModel):
    """Schema para restaurar versão."""

    create_backup: bool = True
    change_notes: str | None = Field(None, max_length=500)
