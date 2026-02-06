"""Schemas Pydantic para DocumentShare."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from modules.ged.models.document_share import ShareType, ShareStatus


class DocumentShareBase(BaseModel):
    """Schema base de DocumentShare."""

    share_type: ShareType = Field(default=ShareType.USUARIO)
    permissions: List[str] = Field(default=["visualizar"])
    can_reshare: bool = False
    max_downloads: Optional[int] = Field(None, ge=1)
    max_views: Optional[int] = Field(None, ge=1)
    expires_at: Optional[datetime] = None
    is_perpetual: bool = False
    message: Optional[str] = Field(None, max_length=1000)
    password_protected: bool = False


class DocumentShareCreate(DocumentShareBase):
    """Schema para criar DocumentShare."""

    document_id: str
    shared_with_id: Optional[str] = None
    shared_with_email: Optional[EmailStr] = None
    shared_with_name: Optional[str] = Field(None, max_length=255)
    shared_by: str
    password: Optional[str] = Field(None, min_length=4, max_length=50)


class DocumentShareUpdate(BaseModel):
    """Schema para atualizar DocumentShare."""

    permissions: Optional[List[str]] = None
    can_reshare: Optional[bool] = None
    max_downloads: Optional[int] = Field(None, ge=1)
    max_views: Optional[int] = Field(None, ge=1)
    expires_at: Optional[datetime] = None
    is_perpetual: Optional[bool] = None
    message: Optional[str] = Field(None, max_length=1000)


class DocumentShareResponse(BaseModel):
    """Schema de resposta de DocumentShare."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    share_type: ShareType
    shared_with_id: Optional[str]
    shared_with_email: Optional[str]
    shared_with_name: Optional[str]
    permissions: List[str]
    can_reshare: bool
    status: ShareStatus
    share_link: Optional[str]
    share_token: Optional[str]
    password_protected: bool
    max_downloads: Optional[int]
    download_count: int
    max_views: Optional[int]
    view_count: int
    expires_at: Optional[datetime]
    is_perpetual: bool
    message: Optional[str]
    notification_sent: bool
    notification_sent_at: Optional[datetime]
    first_accessed_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    access_count: int
    created_at: datetime
    updated_at: datetime
    revoked_at: Optional[datetime]
    shared_by: str
    revoked_by: Optional[str]

    # Computed
    is_active: bool
    is_expired: bool
    is_download_limit_reached: bool
    is_view_limit_reached: bool
    remaining_downloads: Optional[int]
    remaining_views: Optional[int]


class DocumentShareListResponse(BaseModel):
    """Schema de lista de DocumentShares."""

    items: List[DocumentShareResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentShareFilter(BaseModel):
    """Schema de filtro de DocumentShares."""

    document_id: Optional[str] = None
    share_type: Optional[ShareType] = None
    status: Optional[ShareStatus] = None
    shared_with_id: Optional[str] = None
    shared_by: Optional[str] = None
    is_expired: Optional[bool] = None


class DocumentShareLinkRequest(BaseModel):
    """Schema para gerar link de compartilhamento."""

    expires_in_hours: int = Field(default=72, ge=1, le=8760)  # Max 1 ano
    max_downloads: Optional[int] = Field(None, ge=1)
    max_views: Optional[int] = Field(None, ge=1)
    password: Optional[str] = Field(None, min_length=4, max_length=50)
    message: Optional[str] = Field(None, max_length=1000)


class DocumentShareLinkResponse(BaseModel):
    """Resposta de link de compartilhamento."""

    share_id: str
    share_link: str
    share_token: str
    expires_at: datetime
    password_protected: bool


class DocumentShareAccessRequest(BaseModel):
    """Schema para acessar compartilhamento."""

    token: str
    password: Optional[str] = None


class DocumentShareStats(BaseModel):
    """Estatísticas de compartilhamentos."""

    total_shares: int = 0
    active_shares: int = 0
    expired_shares: int = 0
    revoked_shares: int = 0
    by_type: dict = {}
    total_accesses: int = 0
    total_downloads: int = 0
