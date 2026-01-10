"""
application/dto/inventory.py - INVENTORY DTOs
=============================================
Data Transfer Objects for inventory use cases
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Product DTOs
# =============================================================================

class CreateProductDTO(BaseModel):
    """DTO para criacao de produto."""

    model_config = ConfigDict(frozen=True)

    sku: str = Field(..., pattern=r"^[A-Z0-9\-]{3,30}$")
    barcode: Optional[str] = Field(None, pattern=r"^\d{8,14}$")
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    product_type: str
    category_id: UUID
    unit_of_measure: str

    # Pricing
    cost_price: Decimal = Field(..., ge=Decimal("0"))
    sale_price: Decimal = Field(..., ge=Decimal("0"))

    # Stock levels
    minimum_stock: Decimal = Field(default=Decimal("0"))
    maximum_stock: Decimal = Field(default=Decimal("0"))
    reorder_point: Decimal = Field(default=Decimal("0"))

    # Tax
    ncm: str = Field(..., pattern=r"^\d{8}$")

    # Context
    tenant_id: UUID
    created_by: str


class UpdateProductDTO(BaseModel):
    """DTO para atualizacao de produto."""

    model_config = ConfigDict(frozen=True)

    product_id: UUID
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    sale_price: Optional[Decimal] = Field(None, ge=Decimal("0"))
    minimum_stock: Optional[Decimal] = None
    maximum_stock: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    updated_by: str


class ProductResponseDTO(BaseModel):
    """DTO de resposta de produto."""

    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    sku: str
    name: str
    description: Optional[str]
    product_type: str
    status: str
    category_id: UUID
    category_name: str
    unit_of_measure: str

    # Pricing
    cost_price: Decimal
    average_cost: Decimal
    sale_price: Decimal

    # Stock
    current_stock: Decimal
    available_stock: Decimal
    reserved_stock: Decimal
    stock_status: str
    stock_value: Decimal

    # Audit
    created_at: datetime
    updated_at: datetime


class ProductListDTO(BaseModel):
    """DTO para listagem de produtos."""

    model_config = ConfigDict(frozen=True)

    items: List[ProductResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Stock Movement DTOs
# =============================================================================

class MovementLineDTO(BaseModel):
    """DTO para linha de movimento."""

    model_config = ConfigDict(frozen=True)

    product_id: UUID
    quantity: Decimal = Field(..., gt=Decimal("0"))
    unit_cost: Decimal = Field(..., ge=Decimal("0"))
    batch_number: Optional[str] = None
    serial_numbers: List[str] = Field(default_factory=list)


class CreateStockMovementDTO(BaseModel):
    """DTO para criacao de movimentacao."""

    model_config = ConfigDict(frozen=True)

    movement_type: str
    warehouse_id: UUID
    destination_warehouse_id: Optional[UUID] = None
    description: str = Field(..., min_length=5, max_length=500)
    lines: List[MovementLineDTO] = Field(..., min_length=1)

    # Document
    source_document_type: Optional[str] = None
    source_document_id: Optional[UUID] = None
    source_document_number: Optional[str] = None

    # Context
    tenant_id: UUID
    created_by: str


class StockMovementResponseDTO(BaseModel):
    """DTO de resposta de movimentacao."""

    model_config = ConfigDict(from_attributes=True)

    movement_id: UUID
    movement_number: str
    movement_type: str
    movement_date: datetime
    warehouse_id: UUID
    warehouse_code: str
    description: str
    total_quantity: Decimal
    total_cost: Decimal
    is_posted: bool
    is_cancelled: bool

    # Lines
    lines_count: int

    # Audit
    created_at: datetime
    created_by: str


# =============================================================================
# Inventory Report DTOs
# =============================================================================

class StockPositionDTO(BaseModel):
    """DTO para posicao de estoque."""

    model_config = ConfigDict(frozen=True)

    product_id: UUID
    sku: str
    name: str
    category: str
    current_stock: Decimal
    available_stock: Decimal
    reserved_stock: Decimal
    average_cost: Decimal
    stock_value: Decimal
    stock_status: str
    last_movement_date: Optional[datetime]


class StockValuationDTO(BaseModel):
    """DTO para valorizacao de estoque."""

    model_config = ConfigDict(frozen=True)

    warehouse_id: UUID
    warehouse_name: str
    valuation_date: datetime
    total_items: int
    total_quantity: Decimal
    total_value: Decimal
    currency: str


class StockMovementSummaryDTO(BaseModel):
    """DTO para resumo de movimentacoes."""

    model_config = ConfigDict(frozen=True)

    period_start: date
    period_end: date
    entries_count: int
    entries_quantity: Decimal
    entries_value: Decimal
    exits_count: int
    exits_quantity: Decimal
    exits_value: Decimal
    adjustments_count: int
    adjustments_value: Decimal
