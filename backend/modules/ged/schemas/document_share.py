"""Schemas Pydantic para DocumentShare."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.ged.models.document_share import ShareStatus, ShareType


class DocumentShareBase(BaseModel):
    """Schema base de DocumentShare."""

    share_type: ShareType = Field(default=ShareType.USUARIO)
    permissions: list[str] = Field(default=["visualizar"])
    can_reshare: bool = False
    max_downloads: int | None = Field(None, ge=1)
    max_views: int | None = Field(None, ge=1)
    expires_at: datetime | None = None
    is_perpetual: bool = False
    message: str | None = Field(None, max_length=1000)
    password_protected: bool = False


class DocumentShareCreate(DocumentShareBase):
    """Schema para criar DocumentShare."""

    document_id: str
    shared_with_id: str | None = None
    shared_with_email: EmailStr | None = None
    shared_with_name: str | None = Field(None, max_length=255)
    shared_by: str
    password: str | None = Field(None, min_length=4, max_length=50)


class DocumentShareUpdate(BaseModel):
    """Schema para atualizar DocumentShare."""

    permissions: list[str] | None = None
    can_reshare: bool | None = None
    max_downloads: int | None = Field(None, ge=1)
    max_views: int | None = Field(None, ge=1)
    expires_at: datetime | None = None
    is_perpetual: bool | None = None
    message: str | None = Field(None, max_length=1000)


class DocumentShareResponse(BaseModel):
    """Schema de resposta de DocumentShare."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    share_type: ShareType
    shared_with_id: str | None
    shared_with_email: str | None
    shared_with_name: str | None
    permissions: list[str]
    can_reshare: bool
    status: ShareStatus
    share_link: str | None
    share_token: str | None
    password_protected: bool
    max_downloads: int | None
    download_count: int
    max_views: int | None
    view_count: int
    expires_at: datetime | None
    is_perpetual: bool
    message: str | None
    notification_sent: bool
    notification_sent_at: datetime | None
    first_accessed_at: datetime | None
    last_accessed_at: datetime | None
    access_count: int
    created_at: datetime
    updated_at: datetime
    revoked_at: datetime | None
    shared_by: str
    revoked_by: str | None

    # Computed
    is_active: bool
    is_expired: bool
    is_download_limit_reached: bool
    is_view_limit_reached: bool
    remaining_downloads: int | None
    remaining_views: int | None


class DocumentShareListResponse(BaseModel):
    """Schema de lista de DocumentShares."""

    items: list[DocumentShareResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentShareFilter(BaseModel):
    """Schema de filtro de DocumentShares."""

    document_id: str | None = None
    share_type: ShareType | None = None
    status: ShareStatus | None = None
    shared_with_id: str | None = None
    shared_by: str | None = None
    is_expired: bool | None = None


class DocumentShareLinkRequest(BaseModel):
    """Schema para gerar link de compartilhamento."""

    expires_in_hours: int = Field(default=72, ge=1, le=8760)  # Max 1 ano
    max_downloads: int | None = Field(None, ge=1)
    max_views: int | None = Field(None, ge=1)
    password: str | None = Field(None, min_length=4, max_length=50)
    message: str | None = Field(None, max_length=1000)


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
    password: str | None = None


class DocumentShareStats(BaseModel):
    """Estatísticas de compartilhamentos."""

    total_shares: int = 0
    active_shares: int = 0
    expired_shares: int = 0
    revoked_shares: int = 0
    by_type: dict = {}
    total_accesses: int = 0
    total_downloads: int = 0
