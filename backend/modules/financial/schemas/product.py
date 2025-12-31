"""Schemas para produtos."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.product import ProductStatus, ProductType, UnitOfMeasure


class ProductBase(BaseModel):
    """Schema base para produto."""

    name: str = Field(..., min_length=1, max_length=200)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    technical_specs: Optional[str] = None
    product_type: ProductType = ProductType.PRODUTO
    code: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.UNIDADE
    conversion_factor: Decimal = Decimal("1")
    category_id: Optional[UUID] = None
    reference_price: Optional[Decimal] = Field(None, ge=0)
    min_stock: Decimal = Decimal("0")
    max_stock: Optional[Decimal] = Field(None, ge=0)
    reorder_point: Optional[Decimal] = Field(None, ge=0)
    lead_time_days: Optional[str] = None
    ncm: Optional[str] = Field(None, max_length=10)
    cest: Optional[str] = Field(None, max_length=10)
    origin: Optional[str] = Field(None, max_length=5)
    cfop_default: Optional[str] = Field(None, max_length=10)
    preferred_supplier_id: Optional[UUID] = None
    image_url: Optional[str] = Field(None, max_length=500)
    brand: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    tags: List[str] = []
    attributes: Dict[str, Any] = {}
    notes: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema para criar produto."""

    condominio_id: UUID


class ProductUpdate(BaseModel):
    """Schema para atualizar produto."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    short_name: Optional[str] = None
    description: Optional[str] = None
    technical_specs: Optional[str] = None
    product_type: Optional[ProductType] = None
    status: Optional[ProductStatus] = None
    code: Optional[str] = None
    barcode: Optional[str] = None
    unit_of_measure: Optional[UnitOfMeasure] = None
    category_id: Optional[UUID] = None
    reference_price: Optional[Decimal] = None
    min_stock: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    lead_time_days: Optional[str] = None
    ncm: Optional[str] = None
    preferred_supplier_id: Optional[UUID] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ProductResponse(ProductBase):
    """Schema de resposta para produto."""

    id: UUID
    condominio_id: UUID
    status: ProductStatus
    last_purchase_price: Optional[Decimal] = None
    average_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    total_purchases: str = "0"
    last_purchase_at: Optional[datetime] = None
    is_blocked: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema de resposta para lista de produtos."""

    items: List[ProductResponse]
    total: int
    page: int = 1
    page_size: int = 50


class ProductStats(BaseModel):
    """Estatísticas de produtos."""

    total_products: int = 0
    active_products: int = 0
    blocked_products: int = 0
    by_type: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    low_stock_count: int = 0


class ProductBlockRequest(BaseModel):
    """Request para bloquear produto."""

    reason: str = Field(..., min_length=5, max_length=500)


class ProductPriceHistory(BaseModel):
    """Histórico de preços do produto."""

    product_id: UUID
    prices: List[Dict[str, Any]] = []
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    average_price: Optional[Decimal] = None
    price_variation: Optional[Decimal] = None
