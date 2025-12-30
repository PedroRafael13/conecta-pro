"""Schemas para OccurrenceCategory."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Schema para criação de categoria."""

    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int = 0
    parent_id: Optional[str] = None

    # SLA Padrão
    default_sla_response_hours: Optional[int] = None
    default_sla_resolution_hours: Optional[int] = None
    default_priority: Optional[str] = None

    # Atribuição automática
    auto_assign_to_id: Optional[str] = None
    auto_assign_to_name: Optional[str] = None
    auto_assign_department: Optional[str] = None

    # Configurações
    requires_approval: bool = False
    requires_attachment: bool = False
    allows_anonymous: bool = True
    is_public: bool = True
    notify_on_create: bool = True
    notify_on_update: bool = True
    notify_on_resolve: bool = True

    # Notificação
    notification_emails: Optional[list[str]] = None
    notification_template: Optional[str] = None


class CategoryUpdate(BaseModel):
    """Schema para atualização de categoria."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None
    parent_id: Optional[str] = None
    default_sla_response_hours: Optional[int] = None
    default_sla_resolution_hours: Optional[int] = None
    default_priority: Optional[str] = None
    auto_assign_to_id: Optional[str] = None
    auto_assign_to_name: Optional[str] = None
    auto_assign_department: Optional[str] = None
    requires_approval: Optional[bool] = None
    requires_attachment: Optional[bool] = None
    allows_anonymous: Optional[bool] = None
    is_public: Optional[bool] = None
    notify_on_create: Optional[bool] = None
    notify_on_update: Optional[bool] = None
    notify_on_resolve: Optional[bool] = None
    notification_emails: Optional[list[str]] = None
    notification_template: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Schema de resposta de categoria."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int
    parent_id: Optional[str] = None
    level: int
    path: Optional[str] = None

    # SLA
    default_sla_response_hours: Optional[int] = None
    default_sla_resolution_hours: Optional[int] = None
    default_priority: Optional[str] = None

    # Atribuição
    auto_assign_to_id: Optional[str] = None
    auto_assign_to_name: Optional[str] = None
    auto_assign_department: Optional[str] = None

    # Configurações
    requires_approval: bool
    requires_attachment: bool
    allows_anonymous: bool
    is_public: bool

    # Estatísticas
    occurrence_count: int
    avg_resolution_hours: Optional[float] = None

    # Controle
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    """Schema de lista de categorias."""

    items: list[CategoryResponse]
    total: int


class CategoryTree(BaseModel):
    """Schema de árvore de categorias."""

    id: str
    code: str
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    level: int
    occurrence_count: int
    children: list["CategoryTree"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Necessário para referência recursiva
CategoryTree.model_rebuild()
