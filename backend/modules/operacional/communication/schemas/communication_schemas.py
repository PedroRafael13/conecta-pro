"""
Schemas Pydantic para Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.operacional.communication.models.announcement import (
    AnnouncementCategory,
    AnnouncementPriority,
    AnnouncementStatus,
    AnnouncementTargetType,
)
from modules.operacional.communication.models.notification import (
    NotificationChannel,
    NotificationType,
)
from modules.operacional.communication.models.alert import (
    AlertSeverity,
    AlertType,
)


# =============================================================================
# ANNOUNCEMENT SCHEMAS
# =============================================================================


class AttachmentSchema(BaseModel):
    """Schema para anexo de comunicado."""

    url: str = Field(..., description="URL do anexo")
    name: str = Field(..., max_length=255, description="Nome do arquivo")
    type: str = Field(..., max_length=50, description="Tipo MIME")
    size: int = Field(..., ge=0, description="Tamanho em bytes")


class AnnouncementBase(BaseModel):
    """Schema base para Comunicado."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Titulo do comunicado",
    )
    content: str = Field(
        ...,
        min_length=10,
        description="Conteudo do comunicado",
    )
    target_type: AnnouncementTargetType = Field(
        default=AnnouncementTargetType.ALL,
        description="Tipo de destinatario",
    )
    target_ids: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs dos destinatarios especificos",
    )
    target_roles: Optional[List[str]] = Field(
        default=None,
        description="Lista de roles destinatarias",
    )
    priority: AnnouncementPriority = Field(
        default=AnnouncementPriority.NORMAL,
        description="Prioridade do comunicado",
    )
    category: AnnouncementCategory = Field(
        default=AnnouncementCategory.INFORMATIVO,
        description="Categoria do comunicado",
    )
    requires_acknowledgment: bool = Field(
        default=False,
        description="Se requer confirmacao de leitura",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Valida e limpa o titulo."""
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Valida e limpa o conteudo."""
        return v.strip()


class AnnouncementCreate(AnnouncementBase):
    """Schema para criacao de Comunicado."""

    publish_at: Optional[datetime] = Field(
        default=None,
        description="Data/hora para publicacao agendada",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Data/hora de expiracao",
    )
    attachments: Optional[List[AttachmentSchema]] = Field(
        default=None,
        description="Lista de anexos",
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(
        cls, v: Optional[datetime], info
    ) -> Optional[datetime]:
        """Valida que expiracao e posterior a publicacao."""
        if v is None:
            return v
        publish_at = info.data.get("publish_at")
        if publish_at and v <= publish_at:
            raise ValueError("Data de expiracao deve ser posterior a publicacao")
        return v


class AnnouncementUpdate(BaseModel):
    """Schema para atualizacao parcial de Comunicado."""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    target_type: Optional[AnnouncementTargetType] = None
    target_ids: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    priority: Optional[AnnouncementPriority] = None
    category: Optional[AnnouncementCategory] = None
    publish_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    requires_acknowledgment: Optional[bool] = None
    attachments: Optional[List[AttachmentSchema]] = None
    is_active: Optional[bool] = None


class AnnouncementResponse(BaseModel):
    """Schema de resposta para Comunicado."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    target_type: str
    target_ids: Optional[List[str]]
    target_roles: Optional[List[str]]
    title: str
    content: str
    priority: str
    category: str
    publish_at: Optional[datetime]
    expires_at: Optional[datetime]
    requires_acknowledgment: bool
    attachments: Optional[List[Dict[str, Any]]]
    status: str
    published_by: Optional[str]
    published_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    # Propriedades calculadas
    is_published: bool
    is_expired: bool
    is_scheduled: bool
    read_count: int
    acknowledgment_count: int
    read_percentage: float


class AnnouncementListResponse(BaseModel):
    """Schema para listagem paginada de Comunicados."""

    items: List[AnnouncementResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AnnouncementFilter(BaseModel):
    """Schema para filtros de busca de Comunicados."""

    status: Optional[AnnouncementStatus] = None
    priority: Optional[AnnouncementPriority] = None
    category: Optional[AnnouncementCategory] = None
    target_type: Optional[AnnouncementTargetType] = None
    requires_acknowledgment: Optional[bool] = None
    is_active: Optional[bool] = Field(default=True)
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Busca por titulo ou conteudo",
    )
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class AnnouncementPublishRequest(BaseModel):
    """Schema para solicitacao de publicacao."""

    schedule_at: Optional[datetime] = Field(
        default=None,
        description="Data/hora para agendar publicacao (None = publicar agora)",
    )


class AnnouncementReadResponse(BaseModel):
    """Schema de resposta para registro de leitura."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    announcement_id: str
    user_id: str
    read_at: datetime
    acknowledged_at: Optional[datetime]
    is_acknowledged: bool


class AnnouncementReadStats(BaseModel):
    """Estatisticas de leitura de comunicado."""

    total_recipients: int
    total_reads: int
    total_acknowledgments: int
    read_percentage: float
    acknowledgment_percentage: float
    reads: List[AnnouncementReadResponse]


class AnnouncementAcknowledgeRequest(BaseModel):
    """Schema para confirmacao de leitura."""

    ip_address: Optional[str] = Field(
        None,
        max_length=45,
        description="Endereco IP do usuario",
    )
    user_agent: Optional[str] = Field(
        None,
        max_length=500,
        description="User-Agent do navegador",
    )


# =============================================================================
# NOTIFICATION SCHEMAS
# =============================================================================


class NotificationCreate(BaseModel):
    """Schema para criacao de Notificacao."""

    user_id: str = Field(..., description="ID do usuario destinatario")
    title: str = Field(..., min_length=1, max_length=100, description="Titulo")
    body: str = Field(..., min_length=1, max_length=500, description="Corpo")
    type: NotificationType = Field(
        default=NotificationType.SISTEMA,
        description="Tipo da notificacao",
    )
    channels: List[NotificationChannel] = Field(
        default=[NotificationChannel.IN_APP],
        description="Canais de envio",
    )
    reference_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Tipo da entidade referenciada",
    )
    reference_id: Optional[str] = Field(
        None,
        description="ID da entidade referenciada",
    )
    action_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL de acao",
    )
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Dados adicionais",
    )

    @field_validator("title", "body")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Remove espacos em branco extras."""
        return v.strip()


class NotificationResponse(BaseModel):
    """Schema de resposta para Notificacao."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    user_id: str
    title: str
    body: str
    type: str
    reference_type: Optional[str]
    reference_id: Optional[str]
    channels: List[str]
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    clicked_at: Optional[datetime]
    action_url: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime

    # Propriedades calculadas
    is_sent: bool
    is_read: bool
    is_clicked: bool


class NotificationListResponse(BaseModel):
    """Schema para listagem paginada de Notificacoes."""

    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class NotificationFilter(BaseModel):
    """Schema para filtros de busca de Notificacoes."""

    type: Optional[NotificationType] = None
    is_read: Optional[bool] = None
    is_sent: Optional[bool] = None
    reference_type: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class MarkNotificationReadRequest(BaseModel):
    """Schema para marcar notificacao como lida."""

    notification_ids: Optional[List[str]] = Field(
        default=None,
        description="IDs especificos (None = todas)",
    )


class NotificationUnreadCount(BaseModel):
    """Schema para contagem de nao lidas."""

    total: int
    by_type: Dict[str, int]


# =============================================================================
# ALERT SCHEMAS
# =============================================================================


class AlertCreate(BaseModel):
    """Schema para criacao de Alerta."""

    alert_type: AlertType = Field(
        default=AlertType.SISTEMA,
        description="Tipo do alerta",
    )
    severity: AlertSeverity = Field(
        default=AlertSeverity.INFO,
        description="Severidade do alerta",
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Titulo do alerta",
    )
    message: str = Field(
        ...,
        min_length=10,
        description="Mensagem detalhada",
    )
    reference_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Tipo da entidade referenciada",
    )
    reference_id: Optional[str] = Field(
        None,
        description="ID da entidade referenciada",
    )
    target_users: Optional[List[str]] = Field(
        default=None,
        description="Lista de IDs de usuarios destinatarios",
    )
    target_roles: Optional[List[str]] = Field(
        default=None,
        description="Lista de roles destinatarias",
    )
    expires_in_minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Minutos ate expirar (1 a 1440)",
    )

    @field_validator("title", "message")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Remove espacos em branco extras."""
        return v.strip()


class AlertResponse(BaseModel):
    """Schema de resposta para Alerta."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    reference_type: Optional[str]
    reference_id: Optional[str]
    target_users: Optional[List[str]]
    target_roles: Optional[List[str]]
    acknowledged_by: Optional[List[str]]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime

    # Propriedades calculadas
    is_critical: bool
    is_expired: bool
    acknowledgment_count: int
    is_fully_acknowledged: bool


class AlertListResponse(BaseModel):
    """Schema para listagem de Alertas."""

    items: List[AlertResponse]
    total: int


class AlertAcknowledgeRequest(BaseModel):
    """Schema para confirmacao de alerta."""

    pass  # Apenas confirma, sem dados adicionais


class AlertFilter(BaseModel):
    """Schema para filtros de busca de Alertas."""

    alert_type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    is_active: Optional[bool] = Field(default=True)
    is_expired: Optional[bool] = None
    reference_type: Optional[str] = None
    created_after: Optional[datetime] = None


# =============================================================================
# WEBSOCKET SCHEMAS
# =============================================================================


class WebSocketMessage(BaseModel):
    """Schema base para mensagem WebSocket."""

    type: str = Field(..., description="Tipo da mensagem")
    data: Dict[str, Any] = Field(..., description="Dados da mensagem")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp da mensagem",
    )


class WebSocketAlertMessage(BaseModel):
    """Schema para mensagem de alerta via WebSocket."""

    type: str = Field(default="alert", description="Tipo da mensagem")
    data: AlertResponse = Field(..., description="Dados do alerta")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp da mensagem",
    )


class WebSocketNotificationMessage(BaseModel):
    """Schema para mensagem de notificacao via WebSocket."""

    type: str = Field(default="notification", description="Tipo da mensagem")
    data: NotificationResponse = Field(..., description="Dados da notificacao")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp da mensagem",
    )


class WebSocketConnectionInfo(BaseModel):
    """Schema para informacoes de conexao WebSocket."""

    connection_id: str = Field(..., description="ID da conexao")
    user_id: str = Field(..., description="ID do usuario")
    tenant_id: str = Field(..., description="ID do tenant")
    roles: List[str] = Field(default=[], description="Roles do usuario")
    connected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp da conexao",
    )
