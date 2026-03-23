"""Schemas Pydantic para DocumentTag."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.ged.models.document_tag import TagType


class DocumentTagBase(BaseModel):
    """Schema base de DocumentTag."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    tag_type: TagType = Field(default=TagType.USUARIO)
    parent_id: str | None = None
    color: str = Field(default="#6B7280", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(None, max_length=50)
    condominium_id: str | None = None
    is_global: bool = False
    order: int = Field(default=0, ge=0)


class DocumentTagCreate(DocumentTagBase):
    """Schema para criar DocumentTag."""

    created_by: str


class DocumentTagUpdate(BaseModel):
    """Schema para atualizar DocumentTag."""

    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    tag_type: TagType | None = None
    parent_id: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(None, max_length=50)
    is_global: bool | None = None
    order: int | None = Field(None, ge=0)


class DocumentTagResponse(BaseModel):
    """Schema de resposta de DocumentTag."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str | None
    tag_type: TagType
    parent_id: str | None
    color: str
    icon: str | None
    condominium_id: str | None
    is_global: bool
    is_active: bool
    is_system: bool
    usage_count: int
    last_used_at: datetime | None
    order: int
    created_at: datetime
    updated_at: datetime
    created_by: str

    # Computed (optional to avoid lazy-loading issues in async)
    is_category: bool = False
    has_children: bool = False
    full_path: str = ""
    document_count: int = 0


class DocumentTagListResponse(BaseModel):
    """Schema de lista de DocumentTags."""

    items: list[DocumentTagResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentTagFilter(BaseModel):
    """Schema de filtro de DocumentTags."""

    tag_type: TagType | None = None
    parent_id: str | None = None
    condominium_id: str | None = None
    is_global: bool | None = None
    is_active: bool | None = None
    search: str | None = None


class DocumentTagTreeNode(BaseModel):
    """Schema de nó da árvore de tags."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    tag_type: TagType | None = None
    color: str = "blue"
    icon: str | None = None
    document_count: int = 0
    usage_count: int = 0
    children: list["DocumentTagTreeNode"] = []


class DocumentTagAssignment(BaseModel):
    """Schema para atribuir tags a documentos."""

    document_ids: list[str]
    tag_ids: list[str]


class DocumentTagBulkCreate(BaseModel):
    """Schema para criar múltiplas tags."""

    tags: list[DocumentTagCreate]


class DocumentTagStats(BaseModel):
    """Estatísticas de tags."""

    total_tags: int = 0
    active_tags: int = 0
    by_type: dict = {}
    most_used: list[dict] = []
    recently_used: list[dict] = []
