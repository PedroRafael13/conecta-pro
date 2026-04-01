"""Schemas Pydantic para anexos de reembolso."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReimbursementAttachmentCreate(BaseModel):
    """Schema para criação de anexo de reembolso."""

    item_id: UUID | None = None  # Se vinculado a um item específico
    attachment_type: str = Field(default="outros", max_length=30)
    description: str | None = Field(None, max_length=500)


class ReimbursementAttachmentUpdate(BaseModel):
    """Schema para atualização de anexo."""

    attachment_type: str | None = Field(None, max_length=30)
    description: str | None = Field(None, max_length=500)
    is_valid: bool | None = None
    validation_notes: str | None = None


class ReimbursementAttachmentResponse(BaseModel):
    """Schema de resposta para anexo de reembolso."""

    id: UUID
    request_id: UUID
    item_id: UUID | None
    attachment_type: str
    type_label: str = ""
    file_name: str
    file_path: str
    file_size_bytes: int | None
    file_size_formatted: str = ""
    mime_type: str | None
    thumbnail_path: str | None
    is_valid: bool
    validation_notes: str | None
    original_name: str | None
    description: str | None
    is_image: bool = False
    is_pdf: bool = False
    uploaded_by: UUID | None
    uploaded_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class ReimbursementAttachmentValidate(BaseModel):
    """Schema para validação de anexo."""

    is_valid: bool
    notes: str | None = Field(None, max_length=500)
