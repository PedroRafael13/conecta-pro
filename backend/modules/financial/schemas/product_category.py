"""Schemas para categorias de produtos."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.product_category import ProductCategoryStatus, ProductCategoryType


class ProductCategoryBase(BaseModel):
    """Schema base para categoria de produto."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category_type: ProductCategoryType = ProductCategoryType.PRODUTO
    code: str | None = Field(None, max_length=20)
    parent_id: UUID | None = None
    requires_approval: bool = False
    approval_limit: str | None = Field(None, max_length=20)
    default_account_code: str | None = Field(None, max_length=20)
    default_cost_center: str | None = Field(None, max_length=50)
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=20)
    sort_order: int = 0


class ProductCategoryCreate(ProductCategoryBase):
    """Schema para criar categoria."""

    condominio_id: UUID


class ProductCategoryUpdate(BaseModel):
    """Schema para atualizar categoria."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category_type: ProductCategoryType | None = None
    code: str | None = Field(None, max_length=20)
    parent_id: UUID | None = None
    status: ProductCategoryStatus | None = None
    requires_approval: bool | None = None
    approval_limit: str | None = None
    default_account_code: str | None = None
    default_cost_center: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None


class ProductCategoryResponse(ProductCategoryBase):
    """Schema de resposta para categoria."""

    id: UUID
    condominio_id: UUID
    status: ProductCategoryStatus
    path: str | None = None
    depth: int = 0
    product_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class ProductCategoryTreeResponse(ProductCategoryResponse):
    """Schema de resposta com árvore de categorias."""

    children: list["ProductCategoryTreeResponse"] = []


class ProductCategoryListResponse(BaseModel):
    """Schema de resposta para lista de categorias."""

    items: list[ProductCategoryResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ProductCategoryStats(BaseModel):
    """Estatísticas de categorias."""

    total_categories: int = 0
    active_categories: int = 0
    total_products: int = 0
    by_type: dict = {}
