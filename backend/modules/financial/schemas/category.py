"""Schemas para categorias de contas a pagar."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.payable_category import CategoryNature, CategoryType


class PayableCategoryBase(BaseModel):
    """Base para categoria."""

    name: str = Field(..., min_length=2, max_length=100)
    code: str | None = Field(None, max_length=20)
    description: str | None = None
    category_type: CategoryType = CategoryType.DESPESA
    nature: CategoryNature | None = None

    parent_id: UUID | None = None

    allows_children: bool = True
    requires_cost_center: bool = False
    requires_project: bool = False

    accounting_code: str | None = Field(None, max_length=20)
    cost_center_default: str | None = Field(None, max_length=50)

    budget_monthly: str | None = None
    budget_yearly: str | None = None
    alert_percentage: int = Field(default=80, ge=0, le=100)

    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)
    display_order: int = Field(default=0, ge=0)


class PayableCategoryCreate(PayableCategoryBase):
    """Schema para criação de categoria."""

    condominio_id: UUID


class PayableCategoryUpdate(BaseModel):
    """Schema para atualização de categoria."""

    name: str | None = Field(None, min_length=2, max_length=100)
    code: str | None = Field(None, max_length=20)
    description: str | None = None
    category_type: CategoryType | None = None
    nature: CategoryNature | None = None

    parent_id: UUID | None = None

    allows_children: bool | None = None
    requires_cost_center: bool | None = None
    requires_project: bool | None = None

    accounting_code: str | None = Field(None, max_length=20)
    cost_center_default: str | None = Field(None, max_length=50)

    budget_monthly: str | None = None
    budget_yearly: str | None = None
    alert_percentage: int | None = Field(None, ge=0, le=100)

    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)
    display_order: int | None = Field(None, ge=0)

    is_active: bool | None = None


class PayableCategoryResponse(PayableCategoryBase):
    """Schema de resposta para categoria."""

    id: UUID
    condominio_id: UUID
    path: str | None = None
    depth: int
    full_name: str
    is_leaf: bool
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True


class PayableCategoryTreeResponse(BaseModel):
    """Schema de árvore de categorias."""

    id: UUID
    code: str | None = None
    name: str
    full_name: str
    category_type: str
    nature: str | None = None
    depth: int
    is_leaf: bool
    is_active: bool
    icon: str | None = None
    color: str | None = None
    children: list["PayableCategoryTreeResponse"] = Field(default_factory=list)

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True


class PayableCategoryListResponse(BaseModel):
    """Schema de lista de categorias."""

    id: UUID
    code: str | None = None
    name: str
    full_name: str
    category_type: str
    nature: str | None = None
    depth: int
    is_leaf: bool
    is_active: bool
    parent_id: UUID | None = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuração do schema."""

        from_attributes = True


class PayableCategoryFilter(BaseModel):
    """Filtros para busca de categorias."""

    search: str | None = None
    category_type: CategoryType | None = None
    nature: CategoryNature | None = None
    parent_id: UUID | None = None
    is_active: bool | None = None
    is_leaf: bool | None = None
