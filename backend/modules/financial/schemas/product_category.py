"""Schemas para categorias de produtos."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.product_category import ProductCategoryStatus, ProductCategoryType


class ProductCategoryBase(BaseModel):
    """Schema base para categoria de produto."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category_type: ProductCategoryType = ProductCategoryType.PRODUTO
    code: Optional[str] = Field(None, max_length=20)
    parent_id: Optional[UUID] = None
    requires_approval: bool = False
    approval_limit: Optional[str] = Field(None, max_length=20)
    default_account_code: Optional[str] = Field(None, max_length=20)
    default_cost_center: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    sort_order: int = 0


class ProductCategoryCreate(ProductCategoryBase):
    """Schema para criar categoria."""

    condominio_id: UUID


class ProductCategoryUpdate(BaseModel):
    """Schema para atualizar categoria."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category_type: Optional[ProductCategoryType] = None
    code: Optional[str] = Field(None, max_length=20)
    parent_id: Optional[UUID] = None
    status: Optional[ProductCategoryStatus] = None
    requires_approval: Optional[bool] = None
    approval_limit: Optional[str] = None
    default_account_code: Optional[str] = None
    default_cost_center: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None


class ProductCategoryResponse(ProductCategoryBase):
    """Schema de resposta para categoria."""

    id: UUID
    condominio_id: UUID
    status: ProductCategoryStatus
    path: Optional[str] = None
    depth: int = 0
    product_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductCategoryTreeResponse(ProductCategoryResponse):
    """Schema de resposta com árvore de categorias."""

    children: List["ProductCategoryTreeResponse"] = []


class ProductCategoryListResponse(BaseModel):
    """Schema de resposta para lista de categorias."""

    items: List[ProductCategoryResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ProductCategoryStats(BaseModel):
    """Estatísticas de categorias."""

    total_categories: int = 0
    active_categories: int = 0
    total_products: int = 0
    by_type: dict = {}
