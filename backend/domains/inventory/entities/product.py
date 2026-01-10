"""
domains/inventory/entities/product.py - PRODUCT ENTITY
======================================================
Enterprise product entity with inventory management
"""

from typing import Dict, List, Optional, Any, NewType
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from .enums import (
    ProductType,
    ProductStatus,
    UnitOfMeasure,
    InventoryValuationMethod,
    ReorderPointStatus
)

# Strong typing for domain identifiers
ProductId = NewType('ProductId', UUID)
CategoryId = NewType('CategoryId', UUID)
SupplierId = NewType('SupplierId', UUID)


class ProductDimensions(BaseModel):
    """Dimensoes do produto - Value Object."""

    model_config = ConfigDict(frozen=True)

    weight_kg: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    length_cm: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    width_cm: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    height_cm: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    cubic_weight: Optional[Decimal] = None

    @property
    def volume_cm3(self) -> Decimal:
        """Calcula volume em cm3."""
        return self.length_cm * self.width_cm * self.height_cm

    @property
    def volume_m3(self) -> Decimal:
        """Calcula volume em m3."""
        return self.volume_cm3 / Decimal("1000000")


class ProductPricing(BaseModel):
    """Precificacao do produto - Value Object."""

    model_config = ConfigDict(frozen=True)

    cost_price: Decimal = Field(..., ge=Decimal("0"))
    average_cost: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    last_purchase_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    sale_price: Decimal = Field(..., ge=Decimal("0"))
    minimum_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")

    @property
    def markup_percent(self) -> Decimal:
        """Calcula markup percentual."""
        if self.cost_price == 0:
            return Decimal("0")
        return ((self.sale_price - self.cost_price) / self.cost_price * 100).quantize(Decimal("0.01"))

    @property
    def margin_percent(self) -> Decimal:
        """Calcula margem percentual."""
        if self.sale_price == 0:
            return Decimal("0")
        return ((self.sale_price - self.cost_price) / self.sale_price * 100).quantize(Decimal("0.01"))


class StockLevel(BaseModel):
    """Niveis de estoque - Value Object."""

    model_config = ConfigDict(frozen=True)

    minimum_stock: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    maximum_stock: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    reorder_point: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    reorder_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    safety_stock: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    lead_time_days: int = Field(default=0, ge=0)

    @model_validator(mode='after')
    def validate_levels(self) -> 'StockLevel':
        """Valida niveis de estoque."""
        if self.maximum_stock > 0 and self.minimum_stock > self.maximum_stock:
            raise ValueError("Estoque minimo nao pode exceder estoque maximo")
        if self.reorder_point < self.minimum_stock:
            raise ValueError("Ponto de reposicao deve ser maior ou igual ao estoque minimo")
        return self


class TaxClassification(BaseModel):
    """Classificacao fiscal - Value Object."""

    model_config = ConfigDict(frozen=True)

    ncm: str = Field(..., pattern=r"^\d{8}$")  # Nomenclatura Comum do Mercosul
    cest: Optional[str] = Field(None, pattern=r"^\d{7}$")  # Codigo Especificador ST
    cfop_sale: str = Field(default="5102", pattern=r"^\d{4}$")
    cfop_purchase: str = Field(default="1102", pattern=r"^\d{4}$")
    origin: str = Field(default="0", pattern=r"^[0-8]$")  # Origem da mercadoria
    icms_cst: str = Field(default="00", pattern=r"^\d{2,3}$")
    pis_cst: str = Field(default="01", pattern=r"^\d{2}$")
    cofins_cst: str = Field(default="01", pattern=r"^\d{2}$")
    ipi_cst: Optional[str] = Field(None, pattern=r"^\d{2}$")


class ProductEntity(BaseModel):
    """
    Entidade de produto.

    Implementa gestao completa de produtos com
    controle de estoque e precificacao.
    """

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )

    # Identity
    product_id: UUID = Field(default_factory=uuid4)
    sku: str = Field(..., pattern=r"^[A-Z0-9\-]{3,30}$")
    barcode: Optional[str] = Field(None, pattern=r"^\d{8,14}$")
    internal_code: Optional[str] = None

    # Basic Info
    name: str = Field(..., min_length=3, max_length=200)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=2000)
    product_type: ProductType
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)

    # Classification
    category_id: UUID
    category_name: str
    subcategory_id: Optional[UUID] = None
    subcategory_name: Optional[str] = None
    brand: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)

    # Units
    unit_of_measure: UnitOfMeasure
    purchase_unit: Optional[UnitOfMeasure] = None
    conversion_factor: Decimal = Field(default=Decimal("1"), gt=Decimal("0"))

    # Physical
    dimensions: ProductDimensions = Field(default_factory=lambda: ProductDimensions(
        weight_kg=Decimal("0"),
        length_cm=Decimal("0"),
        width_cm=Decimal("0"),
        height_cm=Decimal("0")
    ))

    # Pricing
    pricing: ProductPricing

    # Stock
    stock_level: StockLevel = Field(default_factory=lambda: StockLevel(
        minimum_stock=Decimal("0"),
        maximum_stock=Decimal("0"),
        reorder_point=Decimal("0"),
        reorder_quantity=Decimal("0"),
        safety_stock=Decimal("0"),
        lead_time_days=0
    ))
    valuation_method: InventoryValuationMethod = Field(
        default=InventoryValuationMethod.AVERAGE_COST
    )
    requires_batch: bool = Field(default=False)
    requires_serial: bool = Field(default=False)
    shelf_life_days: Optional[int] = Field(None, ge=0)

    # Current Stock (denormalized for performance)
    current_stock: Decimal = Field(default=Decimal("0"))
    reserved_stock: Decimal = Field(default=Decimal("0"))
    available_stock: Decimal = Field(default=Decimal("0"))

    # Tax
    tax_classification: TaxClassification

    # Supplier
    primary_supplier_id: Optional[UUID] = None
    primary_supplier_name: Optional[str] = None
    supplier_sku: Optional[str] = None

    # Multi-tenant
    tenant_id: UUID

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: Optional[str] = None

    # Images
    image_urls: List[str] = Field(default_factory=list)

    # Tags
    tags: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_product(self) -> 'ProductEntity':
        """Valida regras de negocio do produto."""
        # Valida que produto estocavel tem unidade de medida
        if ProductType(self.product_type).is_stockable():
            if self.unit_of_measure is None:
                raise ValueError("Produto estocavel deve ter unidade de medida")

        # Atualiza estoque disponivel (usando object.__setattr__ para evitar recursao)
        available = self.current_stock - self.reserved_stock
        object.__setattr__(self, 'available_stock', available)

        # Valida controle de lote por tipo
        if ProductType(self.product_type).requires_batch() and not self.requires_batch:
            # Warning apenas, nao bloqueia
            pass

        return self

    # ==========================================================================
    # Business Methods
    # ==========================================================================

    @property
    def is_active(self) -> bool:
        """Verifica se produto esta ativo."""
        return self.status == ProductStatus.ACTIVE

    @property
    def is_stockable(self) -> bool:
        """Verifica se pode ser estocado."""
        return ProductType(self.product_type).is_stockable()

    @property
    def stock_status(self) -> ReorderPointStatus:
        """Calcula status do ponto de reposicao."""
        if self.available_stock <= 0:
            return ReorderPointStatus.STOCKOUT
        if self.available_stock < self.stock_level.minimum_stock:
            return ReorderPointStatus.CRITICAL
        if self.available_stock < self.stock_level.reorder_point:
            return ReorderPointStatus.WARNING
        if self.stock_level.maximum_stock > 0 and \
           self.available_stock > self.stock_level.maximum_stock:
            return ReorderPointStatus.OVERSTOCK
        return ReorderPointStatus.NORMAL

    @property
    def stock_value(self) -> Decimal:
        """Calcula valor do estoque."""
        return (self.current_stock * self.pricing.average_cost).quantize(Decimal("0.01"))

    @property
    def needs_reorder(self) -> bool:
        """Verifica se precisa repor."""
        return self.available_stock <= self.stock_level.reorder_point

    def receive_stock(
        self,
        quantity: Decimal,
        unit_cost: Decimal,
        user_id: str
    ) -> Decimal:
        """Recebe estoque e atualiza custo medio."""
        if quantity <= 0:
            raise ValueError("Quantidade deve ser positiva")

        # Calcula novo custo medio
        if self.valuation_method == InventoryValuationMethod.AVERAGE_COST:
            total_current = self.current_stock * self.pricing.average_cost
            total_new = quantity * unit_cost
            new_total_qty = self.current_stock + quantity

            if new_total_qty > 0:
                new_avg_cost = ((total_current + total_new) / new_total_qty).quantize(Decimal("0.01"))
            else:
                new_avg_cost = unit_cost

            # Atualiza pricing com novo custo medio
            self.pricing = ProductPricing(
                cost_price=self.pricing.cost_price,
                average_cost=new_avg_cost,
                last_purchase_price=unit_cost,
                sale_price=self.pricing.sale_price,
                minimum_price=self.pricing.minimum_price,
                currency=self.pricing.currency
            )

        self.current_stock += quantity
        self.available_stock = self.current_stock - self.reserved_stock
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return self.current_stock

    def ship_stock(
        self,
        quantity: Decimal,
        user_id: str
    ) -> Decimal:
        """Expede estoque."""
        if quantity <= 0:
            raise ValueError("Quantidade deve ser positiva")

        if quantity > self.available_stock:
            raise ValueError(
                f"Estoque disponivel insuficiente. "
                f"Solicitado: {quantity}, Disponivel: {self.available_stock}"
            )

        self.current_stock -= quantity
        self.available_stock = self.current_stock - self.reserved_stock
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return self.current_stock

    def reserve_stock(
        self,
        quantity: Decimal,
        user_id: str
    ) -> bool:
        """Reserva estoque."""
        if quantity <= 0:
            raise ValueError("Quantidade deve ser positiva")

        if quantity > self.available_stock:
            raise ValueError("Estoque disponivel insuficiente para reserva")

        self.reserved_stock += quantity
        self.available_stock = self.current_stock - self.reserved_stock
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return True

    def release_reservation(
        self,
        quantity: Decimal,
        user_id: str
    ) -> bool:
        """Libera reserva de estoque."""
        if quantity <= 0:
            raise ValueError("Quantidade deve ser positiva")

        if quantity > self.reserved_stock:
            raise ValueError("Quantidade excede total reservado")

        self.reserved_stock -= quantity
        self.available_stock = self.current_stock - self.reserved_stock
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return True

    def adjust_stock(
        self,
        new_quantity: Decimal,
        user_id: str,
        reason: str
    ) -> Decimal:
        """Ajusta estoque (inventario)."""
        difference = new_quantity - self.current_stock

        self.current_stock = new_quantity
        self.available_stock = self.current_stock - self.reserved_stock
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return difference

    def update_pricing(
        self,
        cost_price: Optional[Decimal] = None,
        sale_price: Optional[Decimal] = None,
        minimum_price: Optional[Decimal] = None,
        user_id: str = ""
    ) -> None:
        """Atualiza precificacao."""
        new_pricing = ProductPricing(
            cost_price=cost_price or self.pricing.cost_price,
            average_cost=self.pricing.average_cost,
            last_purchase_price=self.pricing.last_purchase_price,
            sale_price=sale_price or self.pricing.sale_price,
            minimum_price=minimum_price or self.pricing.minimum_price,
            currency=self.pricing.currency
        )

        # Valida preco minimo
        if new_pricing.minimum_price > new_pricing.sale_price:
            raise ValueError("Preco minimo nao pode exceder preco de venda")

        self.pricing = new_pricing
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def update_stock_levels(
        self,
        minimum_stock: Optional[Decimal] = None,
        maximum_stock: Optional[Decimal] = None,
        reorder_point: Optional[Decimal] = None,
        reorder_quantity: Optional[Decimal] = None,
        safety_stock: Optional[Decimal] = None,
        lead_time_days: Optional[int] = None,
        user_id: str = ""
    ) -> None:
        """Atualiza niveis de estoque."""
        self.stock_level = StockLevel(
            minimum_stock=minimum_stock if minimum_stock is not None else self.stock_level.minimum_stock,
            maximum_stock=maximum_stock if maximum_stock is not None else self.stock_level.maximum_stock,
            reorder_point=reorder_point if reorder_point is not None else self.stock_level.reorder_point,
            reorder_quantity=reorder_quantity if reorder_quantity is not None else self.stock_level.reorder_quantity,
            safety_stock=safety_stock if safety_stock is not None else self.stock_level.safety_stock,
            lead_time_days=lead_time_days if lead_time_days is not None else self.stock_level.lead_time_days
        )
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def activate(self, user_id: str) -> None:
        """Ativa o produto."""
        self.status = ProductStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def deactivate(self, user_id: str) -> None:
        """Desativa o produto."""
        if self.current_stock > 0:
            raise ValueError("Nao e possivel desativar produto com estoque")
        self.status = ProductStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    def discontinue(self, user_id: str) -> None:
        """Descontinua o produto."""
        self.status = ProductStatus.DISCONTINUED
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

    @staticmethod
    def generate_sku(category_code: str, sequence: int) -> str:
        """Gera SKU do produto."""
        return f"{category_code.upper()}-{sequence:06d}"

    def to_summary(self) -> Dict[str, Any]:
        """Retorna resumo do produto."""
        return {
            "product_id": str(self.product_id),
            "sku": self.sku,
            "name": self.name,
            "category": self.category_name,
            "status": self.status,
            "current_stock": str(self.current_stock),
            "available_stock": str(self.available_stock),
            "stock_status": self.stock_status.value,
            "sale_price": str(self.pricing.sale_price),
            "stock_value": str(self.stock_value)
        }
