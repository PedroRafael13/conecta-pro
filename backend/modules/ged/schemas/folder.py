"""Schemas Pydantic para Folder."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.ged.models.folder import FolderStatus, FolderType


class FolderBase(BaseModel):
    """Schema base de Folder."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    folder_type: FolderType = Field(default=FolderType.CONDOMINIO)
    parent_id: str | None = None
    condominium_id: str | None = None
    contract_id: str | None = None
    employee_id: str | None = None
    client_id: str | None = None
    is_public: bool = False
    inherit_permissions: bool = True
    max_file_size_mb: int | None = Field(None, ge=1, le=1000)
    allowed_extensions: list[str] | None = None
    require_approval: bool = False
    auto_versioning: bool = True
    retention_days: int | None = Field(None, ge=1)
    retention_policy: str | None = Field(None, max_length=100)
    delete_after_retention: bool = False
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int = Field(default=0, ge=0)
    tags: list[str] | None = None
    metadata: dict | None = None


class FolderCreate(FolderBase):
    """Schema para criar Folder."""

    owner_id: str | None = None
    created_by: str | None = None


class FolderUpdate(BaseModel):
    """Schema para atualizar Folder."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    folder_type: FolderType | None = None
    parent_id: str | None = None
    is_public: bool | None = None
    inherit_permissions: bool | None = None
    max_file_size_mb: int | None = Field(None, ge=1, le=1000)
    allowed_extensions: list[str] | None = None
    require_approval: bool | None = None
    auto_versioning: bool | None = None
    retention_days: int | None = Field(None, ge=1)
    retention_policy: str | None = Field(None, max_length=100)
    delete_after_retention: bool | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int | None = Field(None, ge=0)
    tags: list[str] | None = None
    metadata: dict | None = None


class FolderResponse(BaseModel):
    """Schema de resposta de Folder."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: str | None
    parent_id: str | None
    path: str
    level: int
    folder_type: FolderType
    status: FolderStatus
    condominium_id: str | None
    contract_id: str | None
    employee_id: str | None
    client_id: str | None
    owner_id: str
    is_public: bool
    inherit_permissions: bool
    permissions: dict | None
    max_file_size_mb: int | None
    allowed_extensions: list[str] | None
    require_approval: bool
    auto_versioning: bool
    retention_days: int | None
    retention_policy: str | None
    delete_after_retention: bool
    icon: str | None
    color: str | None
    order: int
    tags: list[str] | None
    document_count: int
    subfolder_count: int
    total_size_bytes: int
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    created_by: str

    # Computed
    is_active: bool
    is_archived: bool
    is_system: bool
    is_root: bool
    full_path: str
    total_size_mb: float


class FolderListResponse(BaseModel):
    """Schema de lista de Folders."""

    items: list[FolderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class FolderFilter(BaseModel):
    """Schema de filtro de Folders."""

    folder_type: FolderType | None = None
    status: FolderStatus | None = None
    parent_id: str | None = None
    condominium_id: str | None = None
    owner_id: str | None = None
    is_public: bool | None = None
    is_root: bool | None = None
    search: str | None = None


class FolderTreeNode(BaseModel):
    """Schema de nó da árvore de pastas."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    path: str
    folder_type: FolderType
    status: FolderStatus
    icon: str | None
    color: str | None
    document_count: int
    subfolder_count: int
    children: list["FolderTreeNode"] = []


class FolderPermissionRequest(BaseModel):
    """Schema para gerenciar permissões."""

    user_id: str
    permissions: list[str]  # ["leitura", "escrita", "exclusao", "admin"]


class FolderStats(BaseModel):
    """Estatísticas de pastas."""

    total_folders: int = 0
    active_folders: int = 0
    archived_folders: int = 0
    by_type: dict = {}
    total_documents: int = 0
    total_size_bytes: int = 0
    total_size_mb: float = 0
