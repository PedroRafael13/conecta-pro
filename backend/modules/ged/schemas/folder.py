"""Schemas Pydantic para Folder."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from modules.ged.models.folder import FolderType, FolderStatus


class FolderBase(BaseModel):
    """Schema base de Folder."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    folder_type: FolderType = Field(default=FolderType.CONDOMINIO)
    parent_id: Optional[str] = None
    condominium_id: Optional[str] = None
    contract_id: Optional[str] = None
    employee_id: Optional[str] = None
    client_id: Optional[str] = None
    is_public: bool = False
    inherit_permissions: bool = True
    max_file_size_mb: Optional[int] = Field(None, ge=1, le=1000)
    allowed_extensions: Optional[List[str]] = None
    require_approval: bool = False
    auto_versioning: bool = True
    retention_days: Optional[int] = Field(None, ge=1)
    retention_policy: Optional[str] = Field(None, max_length=100)
    delete_after_retention: bool = False
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: int = Field(default=0, ge=0)
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class FolderCreate(FolderBase):
    """Schema para criar Folder."""

    owner_id: str
    created_by: str


class FolderUpdate(BaseModel):
    """Schema para atualizar Folder."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    folder_type: Optional[FolderType] = None
    parent_id: Optional[str] = None
    is_public: Optional[bool] = None
    inherit_permissions: Optional[bool] = None
    max_file_size_mb: Optional[int] = Field(None, ge=1, le=1000)
    allowed_extensions: Optional[List[str]] = None
    require_approval: Optional[bool] = None
    auto_versioning: Optional[bool] = None
    retention_days: Optional[int] = Field(None, ge=1)
    retention_policy: Optional[str] = Field(None, max_length=100)
    delete_after_retention: Optional[bool] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    order: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class FolderResponse(BaseModel):
    """Schema de resposta de Folder."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    path: str
    level: int
    folder_type: FolderType
    status: FolderStatus
    condominium_id: Optional[str]
    contract_id: Optional[str]
    employee_id: Optional[str]
    client_id: Optional[str]
    owner_id: str
    is_public: bool
    inherit_permissions: bool
    permissions: Optional[dict]
    max_file_size_mb: Optional[int]
    allowed_extensions: Optional[List[str]]
    require_approval: bool
    auto_versioning: bool
    retention_days: Optional[int]
    retention_policy: Optional[str]
    delete_after_retention: bool
    icon: Optional[str]
    color: Optional[str]
    order: int
    tags: Optional[List[str]]
    document_count: int
    subfolder_count: int
    total_size_bytes: int
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]
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

    items: List[FolderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class FolderFilter(BaseModel):
    """Schema de filtro de Folders."""

    folder_type: Optional[FolderType] = None
    status: Optional[FolderStatus] = None
    parent_id: Optional[str] = None
    condominium_id: Optional[str] = None
    owner_id: Optional[str] = None
    is_public: Optional[bool] = None
    is_root: Optional[bool] = None
    search: Optional[str] = None


class FolderTreeNode(BaseModel):
    """Schema de nó da árvore de pastas."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    path: str
    folder_type: FolderType
    status: FolderStatus
    icon: Optional[str]
    color: Optional[str]
    document_count: int
    subfolder_count: int
    children: List["FolderTreeNode"] = []


class FolderPermissionRequest(BaseModel):
    """Schema para gerenciar permissões."""

    user_id: str
    permissions: List[str]  # ["leitura", "escrita", "exclusao", "admin"]


class FolderStats(BaseModel):
    """Estatísticas de pastas."""

    total_folders: int = 0
    active_folders: int = 0
    archived_folders: int = 0
    by_type: dict = {}
    total_documents: int = 0
    total_size_bytes: int = 0
    total_size_mb: float = 0
