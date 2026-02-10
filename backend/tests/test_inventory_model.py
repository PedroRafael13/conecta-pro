"""Tests for Inventory (Estoque) models - Sprint 26."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.models import (
    CostingMethod,
    InventoryItemStatus,
    InventoryStatus,
    InventoryType,
    MovementReason,
    MovementStatus,
    MovementType,
    ReservationPriority,
    ReservationStatus,
    ReservationType,
    StockInventory,
    StockInventoryItem,
    StockItem,
    StockItemStatus,
    StockMovement,
    StockReservation,
    StorageType,
    Warehouse,
    WarehouseStatus,
    WarehouseType,
)


class TestWarehouseModel:
    """Tests for Warehouse model."""

    def test_warehouse_creation_basic(self) -> None:
        """Test basic warehouse creation."""
        condo_id = uuid4()
        warehouse = Warehouse(
            condominio_id=condo_id,
            code="DEP-001",
            name="Depósito Central",
        )
        assert warehouse.code == "DEP-001"
        assert warehouse.name == "Depósito Central"
        assert warehouse.condominio_id == condo_id
        assert warehouse.warehouse_type == WarehouseType.PRINCIPAL
        assert warehouse.status == WarehouseStatus.ATIVO
        assert warehouse.storage_type == StorageType.NORMAL
        assert warehouse.active is True

    def test_warehouse_type_enum(self) -> None:
        """Test WarehouseType enum values."""
        assert WarehouseType.PRINCIPAL.value == "CENTRAL"
        assert WarehouseType.PRINCIPAL.value == "REGIONAL"
        assert WarehouseType.PRINCIPAL.value == "TRANSIT"
        assert WarehouseType.PRINCIPAL.value == "RESERVED"
        assert WarehouseType.PRINCIPAL.value == "QUARANTINE"
        assert WarehouseType.PRINCIPAL.value == "RETURN"
        assert WarehouseType.PRINCIPAL.value == "VIRTUAL"
        assert WarehouseType.PRINCIPAL.value == "CONSIGNMENT"

    def test_warehouse_status_enum(self) -> None:
        """Test WarehouseStatus enum values."""
        assert WarehouseStatus.ATIVO.value == "ACTIVE"
        assert WarehouseStatus.INATIVO.value == "INACTIVE"
        assert WarehouseStatus.ATIVO.value == "MAINTENANCE"
        assert WarehouseStatus.ATIVO.value == "BLOCKED"
        assert WarehouseStatus.ATIVO.value == "CLOSED"

    def test_storage_type_enum(self) -> None:
        """Test StorageType enum values."""
        assert StorageType.NORMAL.value == "GENERAL"
        assert StorageType.NORMAL.value == "REFRIGERATED"
        assert StorageType.NORMAL.value == "FROZEN"
        assert StorageType.NORMAL.value == "HAZARDOUS"
        assert StorageType.NORMAL.value == "HIGH_VALUE"
        assert StorageType.NORMAL.value == "BULK"

    def test_warehouse_with_capacity(self) -> None:
        """Test warehouse with capacity settings."""
        warehouse = Warehouse(
            condominio_id=uuid4(),
            code="DEP-002",
            name="Depósito Grande",
            total_area_m2=Decimal("1000.00"),
            usable_area_m2=Decimal("800.00"),
            max_weight_kg=Decimal("50000.00"),
            max_volume_m3=Decimal("5000.00"),
            current_occupancy_percent=Decimal("45.50"),
        )
        assert warehouse.total_area_m2 == Decimal("1000.00")
        assert warehouse.usable_area_m2 == Decimal("800.00")
        assert warehouse.current_occupancy_percent == Decimal("45.50")

    def test_warehouse_with_temperature_control(self) -> None:
        """Test warehouse with temperature control."""
        warehouse = Warehouse(
            condominio_id=uuid4(),
            code="DEP-FRIO",
            name="Câmara Fria",
            storage_type=StorageType.NORMAL,
            temperature_controlled=True,
            min_temperature=Decimal("-25.00"),
            max_temperature=Decimal("-18.00"),
            humidity_controlled=True,
            min_humidity=Decimal("60.00"),
            max_humidity=Decimal("80.00"),
        )
        assert warehouse.temperature_controlled is True
        assert warehouse.min_temperature == Decimal("-25.00")
        assert warehouse.humidity_controlled is True

    def test_warehouse_with_addressing(self) -> None:
        """Test warehouse with addressing system."""
        warehouse = Warehouse(
            condominio_id=uuid4(),
            code="DEP-END",
            name="Depósito Endereçado",
            has_addressing=True,
            addressing_levels=4,
            address_format="COR-RUA-PRAT-POS",
        )
        assert warehouse.has_addressing is True
        assert warehouse.addressing_levels == 4
        assert warehouse.address_format == "COR-RUA-PRAT-POS"


class TestStockItemModel:
    """Tests for StockItem model."""

    def test_stock_item_creation_basic(self) -> None:
        """Test basic stock item creation."""
        condo_id = uuid4()
        product_id = uuid4()
        warehouse_id = uuid4()
        stock_item = StockItem(
            condominio_id=condo_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            unit_of_measure="UN",
        )
        assert stock_item.product_id == product_id
        assert stock_item.warehouse_id == warehouse_id
        assert stock_item.status == StockItemStatus.DISPONIVEL
        assert stock_item.quantity_on_hand == Decimal("0")
        assert stock_item.costing_method == CostingMethod.CUSTO_MEDIO

    def test_stock_item_status_enum(self) -> None:
        """Test StockItemStatus enum values."""
        assert StockItemStatus.DISPONIVEL.value == "AVAILABLE"
        assert StockItemStatus.DISPONIVEL.value == "RESERVED"
        assert StockItemStatus.DISPONIVEL.value == "BLOCKED"
        assert StockItemStatus.DISPONIVEL.value == "QUARANTINE"
        assert StockItemStatus.DISPONIVEL.value == "EXPIRED"
        assert StockItemStatus.DISPONIVEL.value == "DAMAGED"
        assert StockItemStatus.DISPONIVEL.value == "IN_TRANSIT"

    def test_costing_method_enum(self) -> None:
        """Test CostingMethod enum values."""
        assert CostingMethod.FIFO.value == "FIFO"
        assert CostingMethod.LIFO.value == "LIFO"
        assert CostingMethod.CUSTO_MEDIO.value == "AVERAGE"
        assert CostingMethod.CUSTO_MEDIO.value == "SPECIFIC"
        assert CostingMethod.CUSTO_MEDIO.value == "STANDARD"

    def test_stock_item_with_quantities(self) -> None:
        """Test stock item with quantities."""
        stock_item = StockItem(
            condominio_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            unit_of_measure="UN",
            quantity_on_hand=Decimal("100.0000"),
            quantity_reserved=Decimal("20.0000"),
            quantity_committed=Decimal("10.0000"),
            quantity_available=Decimal("70.0000"),
        )
        assert stock_item.quantity_on_hand == Decimal("100.0000")
        assert stock_item.quantity_reserved == Decimal("20.0000")
        assert stock_item.quantity_available == Decimal("70.0000")

    def test_stock_item_with_costs(self) -> None:
        """Test stock item with cost tracking."""
        stock_item = StockItem(
            condominio_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            unit_of_measure="UN",
            quantity_on_hand=Decimal("50"),
            unit_cost=Decimal("25.50"),
            total_cost=Decimal("1275.00"),
            average_cost=Decimal("25.50"),
            last_purchase_cost=Decimal("26.00"),
        )
        assert stock_item.unit_cost == Decimal("25.50")
        assert stock_item.total_cost == Decimal("1275.00")
        assert stock_item.average_cost == Decimal("25.50")

    def test_stock_item_with_batch(self) -> None:
        """Test stock item with batch tracking."""
        stock_item = StockItem(
            condominio_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            unit_of_measure="UN",
            batch_number="LOTE-2024-001",
            manufacturing_date=date(2024, 1, 15),
            expiry_date=date(2025, 1, 15),
        )
        assert stock_item.batch_number == "LOTE-2024-001"
        assert stock_item.manufacturing_date == date(2024, 1, 15)
        assert stock_item.expiry_date == date(2025, 1, 15)

    def test_stock_item_with_abc_xyz_class(self) -> None:
        """Test stock item with ABC/XYZ classification."""
        stock_item = StockItem(
            condominio_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            unit_of_measure="UN",
            abc_class="A",
            xyz_class="X",
            turnover_rate=Decimal("12.5000"),
            days_of_stock=30,
        )
        assert stock_item.abc_class == "A"
        assert stock_item.xyz_class == "X"
        assert stock_item.turnover_rate == Decimal("12.5000")


class TestStockMovementModel:
    """Tests for StockMovement model."""

    def test_movement_creation_basic(self) -> None:
        """Test basic movement creation."""
        condo_id = uuid4()
        stock_item_id = uuid4()
        product_id = uuid4()
        warehouse_id = uuid4()
        movement = StockMovement(
            condominio_id=condo_id,
            movement_number="MOV-2024-00001",
            stock_item_id=stock_item_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementType.ENTRADA,
            movement_reason=MovementReason.COMPRA,
            quantity=Decimal("100"),
            unit_of_measure="UN",
            quantity_base=Decimal("100"),
            movement_date=datetime.now(),
        )
        assert movement.movement_number == "MOV-2024-00001"
        assert movement.movement_type == MovementType.ENTRADA
        assert movement.movement_reason == MovementReason.COMPRA
        assert movement.status == MovementStatus.RASCUNHO
        assert movement.quantity == Decimal("100")

    def test_movement_type_enum(self) -> None:
        """Test MovementType enum values."""
        assert MovementType.ENTRADA.value == "ENTRY"
        assert MovementType.ENTRADA.value == "EXIT"
        assert MovementType.ENTRADA.value == "TRANSFER_OUT"
        assert MovementType.ENTRADA.value == "TRANSFER_IN"
        assert MovementType.ENTRADA.value == "ADJUSTMENT_PLUS"
        assert MovementType.ENTRADA.value == "ADJUSTMENT_MINUS"
        assert MovementType.ENTRADA.value == "SCRAP"

    def test_movement_reason_enum(self) -> None:
        """Test MovementReason enum values."""
        assert MovementReason.COMPRA.value == "PURCHASE"
        assert MovementReason.COMPRA.value == "SALE"
        assert MovementReason.COMPRA.value == "TRANSFER"
        assert MovementReason.COMPRA.value == "INVENTORY_ADJUSTMENT"
        assert MovementReason.COMPRA.value == "DAMAGED"
        assert MovementReason.COMPRA.value == "EXPIRED"
        assert MovementReason.COMPRA.value == "LOSS"

    def test_movement_status_enum(self) -> None:
        """Test MovementStatus enum values."""
        assert MovementStatus.RASCUNHO.value == "DRAFT"
        assert MovementStatus.PENDENTE.value == "PENDING"
        assert MovementStatus.RASCUNHO.value == "CONFIRMED"
        assert MovementStatus.RASCUNHO.value == "COMPLETED"
        assert MovementStatus.CANCELADA.value == "CANCELLED"
        assert MovementStatus.RASCUNHO.value == "REVERSED"

    def test_movement_with_transfer(self) -> None:
        """Test movement for transfer."""
        dest_warehouse = uuid4()
        dest_stock_item = uuid4()
        movement = StockMovement(
            condominio_id=uuid4(),
            movement_number="MOV-2024-00002",
            stock_item_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            movement_type=MovementType.ENTRADA,
            movement_reason=MovementReason.COMPRA,
            destination_warehouse_id=dest_warehouse,
            destination_stock_item_id=dest_stock_item,
            quantity=Decimal("50"),
            unit_of_measure="UN",
            quantity_base=Decimal("50"),
            movement_date=datetime.now(),
        )
        assert movement.movement_type == MovementType.ENTRADA
        assert movement.destination_warehouse_id == dest_warehouse

    def test_movement_with_balance(self) -> None:
        """Test movement with balance tracking."""
        movement = StockMovement(
            condominio_id=uuid4(),
            movement_number="MOV-2024-00003",
            stock_item_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            movement_type=MovementType.ENTRADA,
            movement_reason=MovementReason.COMPRA,
            quantity=Decimal("100"),
            unit_of_measure="UN",
            quantity_base=Decimal("100"),
            movement_date=datetime.now(),
            balance_before=Decimal("50"),
            balance_after=Decimal("150"),
            unit_cost=Decimal("10.00"),
            total_cost=Decimal("1000.00"),
        )
        assert movement.balance_before == Decimal("50")
        assert movement.balance_after == Decimal("150")
        assert movement.total_cost == Decimal("1000.00")


class TestStockInventoryModel:
    """Tests for StockInventory model."""

    def test_inventory_creation_basic(self) -> None:
        """Test basic inventory creation."""
        condo_id = uuid4()
        warehouse_id = uuid4()
        inventory = StockInventory(
            condominio_id=condo_id,
            inventory_number="INV-2024-001",
            name="Inventário Anual 2024",
            warehouse_id=warehouse_id,
        )
        assert inventory.inventory_number == "INV-2024-001"
        assert inventory.name == "Inventário Anual 2024"
        assert inventory.inventory_type == InventoryType.GERAL
        assert inventory.status == InventoryStatus.PLANEJADO
        assert inventory.freeze_stock is False
        assert inventory.blind_count is False

    def test_inventory_type_enum(self) -> None:
        """Test InventoryType enum values."""
        assert InventoryType.GERAL.value == "FULL"
        assert InventoryType.GERAL.value == "PARTIAL"
        assert InventoryType.GERAL.value == "CYCLIC"
        assert InventoryType.GERAL.value == "BLIND"
        assert InventoryType.ABC.value == "ABC"
        assert InventoryType.GERAL.value == "PERPETUAL"

    def test_inventory_status_enum(self) -> None:
        """Test InventoryStatus enum values."""
        assert InventoryStatus.PLANEJADO.value == "DRAFT"
        assert InventoryStatus.PLANEJADO.value == "SCHEDULED"
        assert InventoryStatus.PLANEJADO.value == "IN_PROGRESS"
        assert InventoryStatus.PLANEJADO.value == "COUNTING"
        assert InventoryStatus.PLANEJADO.value == "REVIEW"
        assert InventoryStatus.PLANEJADO.value == "ADJUSTMENT"
        assert InventoryStatus.PLANEJADO.value == "COMPLETED"
        assert InventoryStatus.CANCELADO.value == "CANCELLED"
        assert InventoryStatus.PLANEJADO.value == "CLOSED"

    def test_inventory_with_settings(self) -> None:
        """Test inventory with settings."""
        inventory = StockInventory(
            condominio_id=uuid4(),
            inventory_number="INV-2024-002",
            name="Contagem Cega",
            warehouse_id=uuid4(),
            inventory_type=InventoryType.GERAL,
            freeze_stock=True,
            blind_count=True,
            require_double_count=True,
            tolerance_percent=Decimal("2.00"),
            tolerance_value=Decimal("100.00"),
        )
        assert inventory.inventory_type == InventoryType.GERAL
        assert inventory.freeze_stock is True
        assert inventory.blind_count is True
        assert inventory.require_double_count is True
        assert inventory.tolerance_percent == Decimal("2.00")

    def test_inventory_with_stats(self) -> None:
        """Test inventory with statistics."""
        inventory = StockInventory(
            condominio_id=uuid4(),
            inventory_number="INV-2024-003",
            name="Inventário Completo",
            warehouse_id=uuid4(),
            total_items=500,
            counted_items=450,
            divergent_items=25,
            adjusted_items=20,
            total_system_value=Decimal("250000.00"),
            total_counted_value=Decimal("248500.00"),
            total_divergence_value=Decimal("1500.00"),
            accuracy_percent=Decimal("95.00"),
        )
        assert inventory.total_items == 500
        assert inventory.counted_items == 450
        assert inventory.accuracy_percent == Decimal("95.00")


class TestStockInventoryItemModel:
    """Tests for StockInventoryItem model."""

    def test_inventory_item_creation_basic(self) -> None:
        """Test basic inventory item creation."""
        inventory_id = uuid4()
        stock_item_id = uuid4()
        product_id = uuid4()
        item = StockInventoryItem(
            inventory_id=inventory_id,
            stock_item_id=stock_item_id,
            product_id=product_id,
            system_quantity=Decimal("100.0000"),
            system_value=Decimal("1000.00"),
            unit_cost=Decimal("10.00"),
        )
        assert item.inventory_id == inventory_id
        assert item.status == InventoryItemStatus.PENDENTE
        assert item.system_quantity == Decimal("100.0000")

    def test_inventory_item_status_enum(self) -> None:
        """Test InventoryItemStatus enum values."""
        assert InventoryItemStatus.PENDENTE.value == "PENDING"
        assert InventoryItemStatus.PENDENTE.value == "COUNTED"
        assert InventoryItemStatus.PENDENTE.value == "RECOUNTED"
        assert InventoryItemStatus.PENDENTE.value == "DIVERGENT"
        assert InventoryItemStatus.PENDENTE.value == "ADJUSTED"
        assert InventoryItemStatus.APROVADO.value == "APPROVED"

    def test_inventory_item_with_count(self) -> None:
        """Test inventory item with count data."""
        item = StockInventoryItem(
            inventory_id=uuid4(),
            stock_item_id=uuid4(),
            product_id=uuid4(),
            system_quantity=Decimal("100.0000"),
            system_value=Decimal("1000.00"),
            unit_cost=Decimal("10.00"),
            counted_quantity=Decimal("98.0000"),
            counted_value=Decimal("980.00"),
            quantity_difference=Decimal("-2.0000"),
            value_difference=Decimal("-20.00"),
            difference_percent=Decimal("-2.0000"),
            is_within_tolerance=True,
            status=InventoryItemStatus.PENDENTE,
        )
        assert item.counted_quantity == Decimal("98.0000")
        assert item.quantity_difference == Decimal("-2.0000")
        assert item.is_within_tolerance is True


class TestStockReservationModel:
    """Tests for StockReservation model."""

    def test_reservation_creation_basic(self) -> None:
        """Test basic reservation creation."""
        condo_id = uuid4()
        stock_item_id = uuid4()
        product_id = uuid4()
        warehouse_id = uuid4()
        reservation = StockReservation(
            condominio_id=condo_id,
            reservation_number="RES-2024-00001",
            stock_item_id=stock_item_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity_reserved=Decimal("50.0000"),
            quantity_remaining=Decimal("50.0000"),
            unit_of_measure="UN",
            reservation_date=datetime.now(),
        )
        assert reservation.reservation_number == "RES-2024-00001"
        assert reservation.reservation_type == ReservationType.VENDA
        assert reservation.status == ReservationStatus.ATIVA
        assert reservation.priority == ReservationPriority.BAIXA
        assert reservation.quantity_reserved == Decimal("50.0000")

    def test_reservation_type_enum(self) -> None:
        """Test ReservationType enum values."""
        assert ReservationType.VENDA.value == "SALE"
        assert ReservationType.VENDA.value == "PRODUCTION"
        assert ReservationType.VENDA.value == "TRANSFER"
        assert ReservationType.VENDA.value == "PROJECT"
        assert ReservationType.VENDA.value == "SERVICE"
        assert ReservationType.VENDA.value == "CONSIGNMENT"
        assert ReservationType.VENDA.value == "SAMPLE"
        assert ReservationType.VENDA.value == "OTHER"

    def test_reservation_status_enum(self) -> None:
        """Test ReservationStatus enum values."""
        assert ReservationStatus.ATIVA.value == "PENDING"
        assert ReservationStatus.ATIVA.value == "CONFIRMED"
        assert ReservationStatus.ATIVA.value == "PARTIAL"
        assert ReservationStatus.ATIVA.value == "CONSUMED"
        assert ReservationStatus.ATIVA.value == "RELEASED"
        assert ReservationStatus.EXPIRADA.value == "EXPIRED"

    def test_reservation_priority_enum(self) -> None:
        """Test ReservationPriority enum values."""
        assert ReservationPriority.BAIXA.value == "LOW"
        assert ReservationPriority.BAIXA.value == "NORMAL"
        assert ReservationPriority.BAIXA.value == "HIGH"
        assert ReservationPriority.BAIXA.value == "URGENT"
        assert ReservationPriority.BAIXA.value == "CRITICAL"

    def test_reservation_with_expiry(self) -> None:
        """Test reservation with expiry date."""
        expiry = datetime.now() + timedelta(days=7)
        reservation = StockReservation(
            condominio_id=uuid4(),
            reservation_number="RES-2024-00002",
            stock_item_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            quantity_reserved=Decimal("25.0000"),
            quantity_remaining=Decimal("25.0000"),
            unit_of_measure="UN",
            reservation_date=datetime.now(),
            expiry_date=expiry,
            auto_release=True,
            auto_release_hours=168,
        )
        assert reservation.expiry_date == expiry
        assert reservation.auto_release is True
        assert reservation.auto_release_hours == 168

    def test_reservation_partial_release(self) -> None:
        """Test reservation with partial release."""
        reservation = StockReservation(
            condominio_id=uuid4(),
            reservation_number="RES-2024-00003",
            stock_item_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            quantity_reserved=Decimal("100.0000"),
            quantity_released=Decimal("40.0000"),
            quantity_remaining=Decimal("60.0000"),
            unit_of_measure="UN",
            reservation_date=datetime.now(),
            status=ReservationStatus.ATIVA,
            allow_partial_release=True,
        )
        assert reservation.quantity_released == Decimal("40.0000")
        assert reservation.quantity_remaining == Decimal("60.0000")
        assert reservation.status == ReservationStatus.ATIVA
