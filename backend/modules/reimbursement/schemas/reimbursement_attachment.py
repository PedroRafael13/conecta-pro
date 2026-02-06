"""Schemas Pydantic para anexos de reembolso."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReimbursementAttachmentCreate(BaseModel):
    """Schema para criação de anexo de reembolso."""

    item_id: Optional[UUID] = None  # Se vinculado a um item específico
    attachment_type: str = Field(default="outros", max_length=30)
    description: Optional[str] = Field(None, max_length=500)


class ReimbursementAttachmentUpdate(BaseModel):
    """Schema para atualização de anexo."""

    attachment_type: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = Field(None, max_length=500)
    is_valid: Optional[bool] = None
    validation_notes: Optional[str] = None


class ReimbursementAttachmentResponse(BaseModel):
    """Schema de resposta para anexo de reembolso."""

    id: UUID
    request_id: UUID
    item_id: Optional[UUID]
    attachment_type: str
    type_label: str = ""
    file_name: str
    file_path: str
    file_size_bytes: Optional[int]
    file_size_formatted: str = ""
    mime_type: Optional[str]
    thumbnail_path: Optional[str]
    is_valid: bool
    validation_notes: Optional[str]
    original_name: Optional[str]
    description: Optional[str]
    is_image: bool = False
    is_pdf: bool = False
    uploaded_by: Optional[UUID]
    uploaded_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class ReimbursementAttachmentValidate(BaseModel):
    """Schema para validação de anexo."""

    is_valid: bool
    notes: Optional[str] = Field(None, max_length=500)
