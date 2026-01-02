"""Schemas Pydantic para o módulo de Estoque."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.financial.models.stock_inventory import (
    InventoryItemStatus,
    InventoryStatus,
    InventoryType,
)
from modules.financial.models.stock_item import CostingMethod, StockItemStatus
from modules.financial.models.stock_movement import MovementReason, MovementStatus, MovementType
from modules.financial.models.stock_reservation import (
    ReservationPriority,
    ReservationStatus,
    ReservationType,
)
from modules.financial.models.warehouse import StorageType, WarehouseStatus, WarehouseType

# =============================================================================
# Warehouse Schemas
# =============================================================================


class WarehouseBase(BaseModel):
    """Base schema para Warehouse."""

    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    short_name: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = None
    warehouse_type: WarehouseType = WarehouseType.PRINCIPAL
    storage_type: StorageType = StorageType.NORMAL

    # Localização
    address: Optional[str] = Field(None, max_length=300)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # Contato
    manager_name: Optional[str] = Field(None, max_length=100)
    manager_email: Optional[str] = Field(None, max_length=200)
    manager_phone: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)

    # Capacidade
    total_area_m2: Optional[Decimal] = None
    storage_area_m2: Optional[Decimal] = None
    total_positions: Optional[str] = "0"
    max_weight_kg: Optional[Decimal] = None

    # Estrutura de endereçamento
    has_addressing: bool = False
    addressing_format: Optional[str] = None

    # Configurações de temperatura
    min_temperature: Optional[Decimal] = None
    max_temperature: Optional[Decimal] = None

    # Segurança
    has_cctv: bool = False
    has_alarm: bool = False
    has_fire_system: bool = False

    # Horários
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    works_24h: bool = False

    # Custos
    monthly_cost: Optional[Decimal] = Field(default=Decimal("0"))
    cost_center: Optional[str] = None

    # Configurações
    allows_negative_stock: bool = False
    fifo_enabled: bool = True
    auto_reorder: bool = False

    # Observações
    notes: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    """Schema para criar Warehouse."""


class WarehouseUpdate(BaseModel):
    """Schema para atualizar Warehouse."""

    name: Optional[str] = Field(None, max_length=100)
    short_name: Optional[str] = Field(None, max_length=30)
    description: Optional[str] = None
    warehouse_type: Optional[WarehouseType] = None
    storage_type: Optional[StorageType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    manager_name: Optional[str] = None
    manager_email: Optional[str] = None
    manager_phone: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    total_area_m2: Optional[Decimal] = None
    storage_area_m2: Optional[Decimal] = None
    total_positions: Optional[str] = None
    has_addressing: Optional[bool] = None
    addressing_format: Optional[str] = None
    min_temperature: Optional[Decimal] = None
    max_temperature: Optional[Decimal] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    works_24h: Optional[bool] = None
    monthly_cost: Optional[Decimal] = None
    cost_center: Optional[str] = None
    allows_negative_stock: Optional[bool] = None
    fifo_enabled: Optional[bool] = None
    auto_reorder: Optional[bool] = None
    notes: Optional[str] = None


class WarehouseResponse(WarehouseBase):
    """Schema de resposta para Warehouse."""

    id: UUID
    condominio_id: UUID
    status: WarehouseStatus
    occupied_positions: Optional[str] = "0"
    current_weight_kg: Optional[Decimal] = None
    current_temperature: Optional[Decimal] = None
    total_items: Optional[str] = "0"
    total_quantity: Optional[Decimal] = None
    total_value: Optional[Decimal] = None
    last_movement_at: Optional[datetime] = None
    last_inventory_at: Optional[datetime] = None
    is_blocked: bool = False
    blocked_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    ativo: bool = True

    # Propriedades calculadas
    is_active: bool = True
    is_main: bool = False
    occupancy_rate: Optional[float] = None
    is_full: bool = False
    available_positions: int = 0
    is_climate_controlled: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class WarehouseListResponse(BaseModel):
    """Schema para listagem de Warehouses."""

    id: UUID
    code: str
    name: str
    warehouse_type: str
    status: str
    storage_type: str
    city: Optional[str] = None
    total_items: Optional[str] = "0"
    total_value: Optional[Decimal] = None
    occupancy_rate: Optional[float] = None
    is_active: bool = True

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


# =============================================================================
# StockItem Schemas
# =============================================================================


class StockItemBase(BaseModel):
    """Base schema para StockItem."""

    product_id: UUID
    warehouse_id: UUID
    batch_number: Optional[str] = Field(None, max_length=50)
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    serial_number: Optional[str] = Field(None, max_length=100)

    # Localização
    location_code: Optional[str] = Field(None, max_length=50)
    aisle: Optional[str] = Field(None, max_length=10)
    rack: Optional[str] = Field(None, max_length=10)
    shelf: Optional[str] = Field(None, max_length=10)
    bin: Optional[str] = Field(None, max_length=10)

    # Parâmetros de estoque
    min_quantity: Optional[Decimal] = None
    max_quantity: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    safety_stock: Optional[Decimal] = None

    # Custeio
    costing_method: CostingMethod = CostingMethod.CUSTO_MEDIO

    # Classificação
    abc_class: Optional[str] = Field(None, max_length=1)
    xyz_class: Optional[str] = Field(None, max_length=1)

    notes: Optional[str] = None


class StockItemCreate(StockItemBase):
    """Schema para criar StockItem."""

    quantity_on_hand: Decimal = Field(default=Decimal("0"))
    unit_cost: Decimal = Field(default=Decimal("0"))


class StockItemUpdate(BaseModel):
    """Schema para atualizar StockItem."""

    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    location_code: Optional[str] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None
    min_quantity: Optional[Decimal] = None
    max_quantity: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    safety_stock: Optional[Decimal] = None
    abc_class: Optional[str] = None
    xyz_class: Optional[str] = None
    notes: Optional[str] = None


class StockItemResponse(StockItemBase):
    """Schema de resposta para StockItem."""

    id: UUID
    condominio_id: UUID
    status: StockItemStatus
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_committed: Decimal
    quantity_on_order: Decimal
    quantity_in_transit: Decimal
    unit_cost: Decimal
    average_cost: Decimal
    last_cost: Decimal
    total_cost: Decimal
    last_receipt_date: Optional[datetime] = None
    last_issue_date: Optional[datetime] = None
    last_count_date: Optional[datetime] = None
    receipt_count: Optional[str] = "0"
    issue_count: Optional[str] = "0"
    is_blocked: bool = False
    blocked_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    ativo: bool = True

    # Propriedades calculadas
    quantity_available: float = 0
    is_available: bool = True
    is_low_stock: bool = False
    is_below_reorder_point: bool = False
    is_overstocked: bool = False
    is_expired: bool = False
    days_to_expiry: Optional[int] = None
    is_expiring_soon: bool = False
    full_location: str = ""
    classification: str = "--"

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class StockItemListResponse(BaseModel):
    """Schema para listagem de StockItems."""

    id: UUID
    product_id: UUID
    warehouse_id: UUID
    batch_number: Optional[str] = None
    status: str
    quantity_on_hand: float
    quantity_available: float
    unit_cost: float
    total_cost: float
    expiry_date: Optional[date] = None
    full_location: str = ""
    is_low_stock: bool = False
    is_expired: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


# =============================================================================
# StockMovement Schemas
# =============================================================================


class StockMovementBase(BaseModel):
    """Base schema para StockMovement."""

    movement_type: MovementType
    reason: MovementReason = MovementReason.OUTRO
    product_id: UUID
    warehouse_id: UUID
    destination_warehouse_id: Optional[UUID] = None
    movement_date: date
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    serial_number: Optional[str] = Field(None, max_length=100)
    quantity: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(default="un", max_length=10)
    unit_cost: Decimal = Field(default=Decimal("0"))

    # Localização origem
    source_location: Optional[str] = None
    source_aisle: Optional[str] = None
    source_rack: Optional[str] = None
    source_shelf: Optional[str] = None
    source_bin: Optional[str] = None

    # Localização destino
    dest_location: Optional[str] = None
    dest_aisle: Optional[str] = None
    dest_rack: Optional[str] = None
    dest_shelf: Optional[str] = None
    dest_bin: Optional[str] = None

    # Referências
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    reference_number: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_series: Optional[str] = None
    invoice_key: Optional[str] = None

    supplier_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    requisition_number: Optional[str] = None

    requires_approval: bool = False
    description: Optional[str] = None
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    """Schema para criar StockMovement."""


class StockMovementUpdate(BaseModel):
    """Schema para atualizar StockMovement."""

    movement_date: Optional[date] = None
    batch_number: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class StockMovementResponse(StockMovementBase):
    """Schema de resposta para StockMovement."""

    id: UUID
    condominio_id: UUID
    number: str
    status: MovementStatus
    total_cost: Decimal
    balance_before: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    confirmed_by: Optional[UUID] = None
    confirmed_at: Optional[datetime] = None
    is_reversal: bool = False
    reversal_of: Optional[UUID] = None
    reversed_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    ativo: bool = True

    # Propriedades calculadas
    is_entry: bool = False
    is_exit: bool = False
    is_transfer: bool = False
    is_adjustment: bool = False
    is_pending: bool = False
    is_confirmed: bool = False
    can_confirm: bool = True
    can_cancel: bool = True
    can_reverse: bool = False
    source_full_location: str = ""
    dest_full_location: str = ""
    signed_quantity: float = 0

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class StockMovementListResponse(BaseModel):
    """Schema para listagem de StockMovements."""

    id: UUID
    number: str
    movement_type: str
    reason: str
    status: str
    product_id: UUID
    warehouse_id: UUID
    movement_date: date
    quantity: float
    unit_cost: float
    total_cost: float
    reference_number: Optional[str] = None
    is_confirmed: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


# =============================================================================
# StockInventory Schemas
# =============================================================================


class StockInventoryBase(BaseModel):
    """Base schema para StockInventory."""

    warehouse_id: UUID
    description: Optional[str] = Field(None, max_length=200)
    inventory_type: InventoryType = InventoryType.GERAL
    planned_date: Optional[date] = None
    deadline: Optional[datetime] = None

    # Filtros
    filter_categories: Optional[list] = None
    filter_locations: Optional[list] = None
    filter_abc_class: Optional[list] = None
    filter_products: Optional[list] = None

    # Responsável
    supervisor_id: Optional[UUID] = None
    team_members: Optional[list] = None

    # Configurações
    requires_approval: bool = True
    allow_recount: bool = True
    require_double_count: bool = False
    blind_count: bool = False
    auto_adjust: bool = False

    notes: Optional[str] = None


class StockInventoryCreate(StockInventoryBase):
    """Schema para criar StockInventory."""


class StockInventoryUpdate(BaseModel):
    """Schema para atualizar StockInventory."""

    description: Optional[str] = None
    planned_date: Optional[date] = None
    deadline: Optional[datetime] = None
    supervisor_id: Optional[UUID] = None
    team_members: Optional[list] = None
    notes: Optional[str] = None


class StockInventoryResponse(StockInventoryBase):
    """Schema de resposta para StockInventory."""

    id: UUID
    condominio_id: UUID
    number: str
    status: InventoryStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_items: int = 0
    counted_items: int = 0
    verified_items: int = 0
    divergent_items: int = 0
    adjusted_items: int = 0
    expected_value: Decimal = Decimal("0")
    counted_value: Decimal = Decimal("0")
    difference_value: Decimal = Decimal("0")
    expected_quantity: Decimal = Decimal("0")
    counted_quantity: Decimal = Decimal("0")
    difference_quantity: Decimal = Decimal("0")
    accuracy_rate: Optional[Decimal] = None
    hit_rate: Optional[Decimal] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    ativo: bool = True

    # Propriedades calculadas
    is_in_progress: bool = False
    is_finalized: bool = False
    is_cancelled: bool = False
    progress_percentage: float = 0
    has_divergences: bool = False
    can_start: bool = True
    can_finish: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class StockInventoryListResponse(BaseModel):
    """Schema para listagem de StockInventories."""

    id: UUID
    number: str
    description: Optional[str] = None
    inventory_type: str
    status: str
    warehouse_id: UUID
    planned_date: Optional[date] = None
    total_items: int = 0
    counted_items: int = 0
    divergent_items: int = 0
    progress_percentage: float = 0
    accuracy_rate: Optional[float] = None

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


# =============================================================================
# StockInventoryItem Schemas
# =============================================================================


class StockInventoryItemBase(BaseModel):
    """Base schema para StockInventoryItem."""

    product_id: UUID
    stock_item_id: Optional[UUID] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    location_code: Optional[str] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin_loc: Optional[str] = None
    expected_quantity: Decimal = Decimal("0")
    unit_cost: Decimal = Decimal("0")


class StockInventoryItemCreate(StockInventoryItemBase):
    """Schema para criar StockInventoryItem."""

    inventory_id: UUID


class StockInventoryItemCount(BaseModel):
    """Schema para registrar contagem."""

    counted_quantity: Decimal = Field(..., ge=0)
    notes: Optional[str] = None


class StockInventoryItemResponse(StockInventoryItemBase):
    """Schema de resposta para StockInventoryItem."""

    id: UUID
    inventory_id: UUID
    status: InventoryItemStatus
    expected_value: Decimal = Decimal("0")
    counted_quantity: Optional[Decimal] = None
    recount_quantity: Optional[Decimal] = None
    difference_quantity: Optional[Decimal] = None
    adjusted_quantity: Optional[Decimal] = None
    counted_value: Optional[Decimal] = None
    difference_value: Optional[Decimal] = None
    counted_at: Optional[datetime] = None
    counted_by: Optional[UUID] = None
    recounted_at: Optional[datetime] = None
    recounted_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[UUID] = None
    adjustment_reason: Optional[str] = None
    adjusted_at: Optional[datetime] = None
    adjusted_by: Optional[UUID] = None
    notes: Optional[str] = None
    created_at: datetime
    ativo: bool = True

    # Propriedades calculadas
    is_counted: bool = False
    is_recounted: bool = False
    is_verified: bool = False
    is_adjusted: bool = False
    has_divergence: bool = False
    divergence_percentage: Optional[float] = None
    full_location: str = ""

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


# =============================================================================
# StockReservation Schemas
# =============================================================================


class StockReservationBase(BaseModel):
    """Base schema para StockReservation."""

    description: Optional[str] = Field(None, max_length=200)
    reservation_type: ReservationType
    priority: ReservationPriority = ReservationPriority.MEDIA
    product_id: UUID
    warehouse_id: UUID
    stock_item_id: Optional[UUID] = None
    batch_number: Optional[str] = None
    quantity_requested: Decimal = Field(..., gt=0)
    unit_of_measure: str = Field(default="un", max_length=10)
    required_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

    # Referência
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    reference_number: Optional[str] = None

    # Solicitante
    requester_id: Optional[UUID] = None
    requester_name: Optional[str] = None
    department: Optional[str] = None
    cost_center: Optional[str] = None

    # Configurações
    requires_approval: bool = False
    auto_release: bool = False
    auto_expire: bool = True
    allow_partial: bool = True

    notes: Optional[str] = None


class StockReservationCreate(StockReservationBase):
    """Schema para criar StockReservation."""


class StockReservationUpdate(BaseModel):
    """Schema para atualizar StockReservation."""

    description: Optional[str] = None
    priority: Optional[ReservationPriority] = None
    required_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None


class StockReservationRelease(BaseModel):
    """Schema para liberar reserva."""

    quantity: Decimal = Field(..., gt=0)
    notes: Optional[str] = None


class StockReservationResponse(StockReservationBase):
    """Schema de resposta para StockReservation."""

    id: UUID
    condominio_id: UUID
    number: str
    status: ReservationStatus
    quantity_reserved: Decimal = Decimal("0")
    quantity_released: Decimal = Decimal("0")
    quantity_pending: Decimal = Decimal("0")
    reservation_date: datetime
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    released_by: Optional[UUID] = None
    released_at: Optional[datetime] = None
    release_notes: Optional[str] = None
    cancelled_by: Optional[UUID] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    ativo: bool = True

    # Propriedades calculadas
    is_active: bool = True
    is_fulfilled: bool = False
    is_partial: bool = False
    is_expired: bool = False
    is_cancelled: bool = False
    is_released: bool = False
    fulfillment_percentage: float = 0
    is_overdue: bool = False
    days_until_required: Optional[int] = None
    days_until_expiry: Optional[int] = None
    is_high_priority: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


class StockReservationListResponse(BaseModel):
    """Schema para listagem de StockReservations."""

    id: UUID
    number: str
    reservation_type: str
    status: str
    priority: str
    product_id: UUID
    warehouse_id: UUID
    quantity_requested: float
    quantity_reserved: float
    quantity_pending: float
    required_date: Optional[datetime] = None
    reference_number: Optional[str] = None
    is_overdue: bool = False

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do schema."""

        from_attributes = True


# =============================================================================
# Stats e Filters
# =============================================================================


class WarehouseStats(BaseModel):
    """Estatísticas de armazéns."""

    total_warehouses: int = 0
    active_warehouses: int = 0
    total_items: int = 0
    total_value: float = 0
    average_occupancy: float = 0
    warehouses_near_capacity: int = 0


class StockStats(BaseModel):
    """Estatísticas de estoque."""

    total_items: int = 0
    total_quantity: float = 0
    total_value: float = 0
    low_stock_items: int = 0
    expired_items: int = 0
    expiring_soon_items: int = 0
    blocked_items: int = 0


class MovementStats(BaseModel):
    """Estatísticas de movimentações."""

    total_movements: int = 0
    entries_count: int = 0
    exits_count: int = 0
    transfers_count: int = 0
    adjustments_count: int = 0
    entries_value: float = 0
    exits_value: float = 0
    pending_movements: int = 0


class InventoryStats(BaseModel):
    """Estatísticas de inventários."""

    total_inventories: int = 0
    in_progress: int = 0
    finalized: int = 0
    average_accuracy: float = 0
    total_adjustments: int = 0
    adjustment_value: float = 0


class ReservationStats(BaseModel):
    """Estatísticas de reservas."""

    total_reservations: int = 0
    active_reservations: int = 0
    fulfilled_reservations: int = 0
    expired_reservations: int = 0
    overdue_reservations: int = 0
    reserved_value: float = 0


class StockFilter(BaseModel):
    """Filtros para consulta de estoque."""

    warehouse_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    status: Optional[StockItemStatus] = None
    batch_number: Optional[str] = None
    location_code: Optional[str] = None
    abc_class: Optional[str] = None
    is_low_stock: Optional[bool] = None
    is_expired: Optional[bool] = None
    is_expiring_soon: Optional[bool] = None
    min_quantity: Optional[Decimal] = None
    max_quantity: Optional[Decimal] = None


class MovementFilter(BaseModel):
    """Filtros para consulta de movimentações."""

    warehouse_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    movement_type: Optional[MovementType] = None
    reason: Optional[MovementReason] = None
    status: Optional[MovementStatus] = None
    reference_type: Optional[str] = None
    reference_number: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    batch_number: Optional[str] = None
