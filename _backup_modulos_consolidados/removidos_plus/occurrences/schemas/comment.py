"""Schemas para OccurrenceComment."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from modules.occurrences.models.comment import CommentVisibility


class CommentCreate(BaseModel):
    """Schema para criação de comentário."""

    model_config = ConfigDict(use_enum_values=True)

    occurrence_id: str
    content: str = Field(..., min_length=1)
    visibility: CommentVisibility = CommentVisibility.PUBLIC
    parent_id: Optional[str] = None

    # Autor
    author_id: str
    author_name: str
    author_email: Optional[str] = None
    author_role: Optional[str] = None
    is_staff: bool = False

    # Menções
    mentions: Optional[list[dict]] = None

    # Anexos
    attachments: Optional[list[dict]] = None

    # Flags
    is_first_response: bool = False


class CommentUpdate(BaseModel):
    """Schema para atualização de comentário."""

    model_config = ConfigDict(use_enum_values=True)

    content: Optional[str] = Field(None, min_length=1)
    visibility: Optional[CommentVisibility] = None


class CommentResponse(BaseModel):
    """Schema de resposta de comentário."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: str
    occurrence_id: str
    content: str
    content_html: Optional[str] = None
    visibility: str

    # Autor
    author_id: str
    author_name: str
    author_email: Optional[str] = None
    author_role: Optional[str] = None
    author_avatar: Optional[str] = None
    is_staff: bool

    # Resposta
    parent_id: Optional[str] = None
    reply_count: int

    # Menções
    mentions: Optional[list] = None

    # Anexos
    attachments: Optional[list] = None

    # Métricas
    like_count: int

    # Flags
    is_solution: bool
    is_pinned: bool
    is_first_response: bool

    # Edição
    is_edited: bool
    edited_at: Optional[datetime] = None

    # IA
    ai_sentiment: Optional[str] = None

    # Controle
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    """Schema de lista de comentários."""

    items: list[CommentResponse]
    total: int
    page: int = 1
    page_size: int = 50
