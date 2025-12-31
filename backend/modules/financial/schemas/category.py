"""Schemas para categorias de contas a pagar."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.payable_category import CategoryNature, CategoryType


class PayableCategoryBase(BaseModel):
    """Base para categoria."""

    name: str = Field(..., min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    category_type: CategoryType = CategoryType.DESPESA
    nature: Optional[CategoryNature] = None

    parent_id: Optional[UUID] = None

    allows_children: bool = True
    requires_cost_center: bool = False
    requires_project: bool = False

    accounting_code: Optional[str] = Field(None, max_length=20)
    cost_center_default: Optional[str] = Field(None, max_length=50)

    budget_monthly: Optional[str] = None
    budget_yearly: Optional[str] = None
    alert_percentage: int = Field(default=80, ge=0, le=100)

    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    display_order: int = Field(default=0, ge=0)


class PayableCategoryCreate(PayableCategoryBase):
    """Schema para criação de categoria."""

    condominio_id: UUID


class PayableCategoryUpdate(BaseModel):
    """Schema para atualização de categoria."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    category_type: Optional[CategoryType] = None
    nature: Optional[CategoryNature] = None

    parent_id: Optional[UUID] = None

    allows_children: Optional[bool] = None
    requires_cost_center: Optional[bool] = None
    requires_project: Optional[bool] = None

    accounting_code: Optional[str] = Field(None, max_length=20)
    cost_center_default: Optional[str] = Field(None, max_length=50)

    budget_monthly: Optional[str] = None
    budget_yearly: Optional[str] = None
    alert_percentage: Optional[int] = Field(None, ge=0, le=100)

    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    display_order: Optional[int] = Field(None, ge=0)

    is_active: Optional[bool] = None


class PayableCategoryResponse(PayableCategoryBase):
    """Schema de resposta para categoria."""

    id: UUID
    condominio_id: UUID
    path: Optional[str] = None
    depth: int
    full_name: str
    is_leaf: bool
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayableCategoryTreeResponse(BaseModel):
    """Schema de árvore de categorias."""

    id: UUID
    code: Optional[str] = None
    name: str
    full_name: str
    category_type: str
    nature: Optional[str] = None
    depth: int
    is_leaf: bool
    is_active: bool
    icon: Optional[str] = None
    color: Optional[str] = None
    children: List["PayableCategoryTreeResponse"] = Field(default_factory=list)

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayableCategoryListResponse(BaseModel):
    """Schema de lista de categorias."""

    id: UUID
    code: Optional[str] = None
    name: str
    full_name: str
    category_type: str
    nature: Optional[str] = None
    depth: int
    is_leaf: bool
    is_active: bool
    parent_id: Optional[UUID] = None

    class Config:
        """Configuração do schema."""

        from_attributes = True


class PayableCategoryFilter(BaseModel):
    """Filtros para busca de categorias."""

    search: Optional[str] = None
    category_type: Optional[CategoryType] = None
    nature: Optional[CategoryNature] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    is_leaf: Optional[bool] = None
