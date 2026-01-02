"""Schemas Pydantic para DocumentTag."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from modules.ged.models.document_tag import TagType


class DocumentTagBase(BaseModel):
    """Schema base de DocumentTag."""

    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    tag_type: TagType = Field(default=TagType.USUARIO)
    parent_id: Optional[str] = None
    color: str = Field(default="#6B7280", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    condominium_id: Optional[str] = None
    is_global: bool = False
    order: int = Field(default=0, ge=0)


class DocumentTagCreate(DocumentTagBase):
    """Schema para criar DocumentTag."""

    created_by: str


class DocumentTagUpdate(BaseModel):
    """Schema para atualizar DocumentTag."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    tag_type: Optional[TagType] = None
    parent_id: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    is_global: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)


class DocumentTagResponse(BaseModel):
    """Schema de resposta de DocumentTag."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: Optional[str]
    tag_type: TagType
    parent_id: Optional[str]
    color: str
    icon: Optional[str]
    condominium_id: Optional[str]
    is_global: bool
    is_active: bool
    is_system: bool
    usage_count: int
    last_used_at: Optional[datetime]
    order: int
    created_at: datetime
    updated_at: datetime
    created_by: str

    # Computed
    is_category: bool
    has_children: bool
    full_path: str


class DocumentTagListResponse(BaseModel):
    """Schema de lista de DocumentTags."""

    items: List[DocumentTagResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentTagFilter(BaseModel):
    """Schema de filtro de DocumentTags."""

    tag_type: Optional[TagType] = None
    parent_id: Optional[str] = None
    condominium_id: Optional[str] = None
    is_global: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


class DocumentTagTreeNode(BaseModel):
    """Schema de nó da árvore de tags."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    color: str
    icon: Optional[str]
    usage_count: int
    children: List["DocumentTagTreeNode"] = []


class DocumentTagAssignment(BaseModel):
    """Schema para atribuir tags a documentos."""

    document_ids: List[str]
    tag_ids: List[str]


class DocumentTagBulkCreate(BaseModel):
    """Schema para criar múltiplas tags."""

    tags: List[DocumentTagCreate]


class DocumentTagStats(BaseModel):
    """Estatísticas de tags."""

    total_tags: int = 0
    active_tags: int = 0
    by_type: dict = {}
    most_used: List[dict] = []
    recently_used: List[dict] = []
