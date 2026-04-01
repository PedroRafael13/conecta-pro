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
            warehouse_type=WarehouseType.PRINCIPAL,
            status=WarehouseStatus.ATIVO,
            storage_type=StorageType.NORMAL,
            ativo=True,
        )
        assert warehouse.code == "DEP-001"
        assert warehouse.name == "Depósito Central"
        assert warehouse.condominio_id == condo_id
        assert warehouse.warehouse_type == WarehouseType.PRINCIPAL
        assert warehouse.status == WarehouseStatus.ATIVO
        assert warehouse.storage_type == StorageType.NORMAL
        assert warehouse.ativo is True

    def test_warehouse_type_enum(self) -> None:
        """Test WarehouseType enum values."""
        assert WarehouseType.PRINCIPAL.value == "principal"
        assert WarehouseType.SECUNDARIO.value == "secundario"
        assert WarehouseType.TRANSITO.value == "transito"
        assert WarehouseType.DEVOLUCAO.value == "devolucao"
        assert WarehouseType.QUARENTENA.value == "quarentena"
        assert WarehouseType.AVARIADO.value == "avariado"
        assert WarehouseType.CONSIGNADO.value == "consignado"
        assert WarehouseType.TERCEIROS.value == "terceiros"

    def test_warehouse_status_enum(self) -> None:
        """Test WarehouseStatus enum values."""
        assert WarehouseStatus.ATIVO.value == "ativo"
        assert WarehouseStatus.INATIVO.value == "inativo"
        assert WarehouseStatus.BLOQUEADO.value == "bloqueado"
        assert WarehouseStatus.MANUTENCAO.value == "manutencao"
        assert WarehouseStatus.ENCERRADO.value == "encerrado"

    def test_storage_type_enum(self) -> None:
        """Test StorageType enum values."""
        assert StorageType.NORMAL.value == "normal"
        assert StorageType.REFRIGERADO.value == "refrigerado"
        assert StorageType.CONGELADO.value == "congelado"
        assert StorageType.CLIMATIZADO.value == "climatizado"
        assert StorageType.PERIGOSO.value == "perigoso"
        assert StorageType.ESPECIAL.value == "especial"

    def test_warehouse_with_capacity(self) -> None:
        """Test warehouse with capacity settings."""
        warehouse = Warehouse(
            condominio_id=uuid4(),
            code="DEP-002",
            name="Depósito Grande",
            total_area_m2=Decimal("1000.00"),
            storage_area_m2=Decimal("800.00"),
            max_weight_kg=Decimal("50000.00"),
        )
        assert warehouse.total_area_m2 == Decimal("1000.00")
        assert warehouse.storage_area_m2 == Decimal("800.00")
        assert warehouse.max_weight_kg == Decimal("50000.00")

    def test_warehouse_with_temperature_control(self) -> None:
        """Test warehouse with temperature control."""
        warehouse = Warehouse(
            condominio_id=uuid4(),
            code="DEP-FRIO",
            name="Câmara Fria",
            storage_type=StorageType.CONGELADO,
            min_temperature=Decimal("-25.00"),
            max_temperature=Decimal("-18.00"),
        )
        assert warehouse.min_temperature == Decimal("-25.00")
        assert warehouse.max_temperature == Decimal("-18.00")

    def test_warehouse_with_addressing(self) -> None:
        """Test warehouse with addressing system."""
        warehouse = Warehouse(
            condominio_id=uuid4(),
            code="DEP-END",
            name="Depósito Endereçado",
            has_addressing=True,
            addressing_format="COR-RUA-PRAT-POS",
        )
        assert warehouse.has_addressing is True
        assert warehouse.addressing_format == "COR-RUA-PRAT-POS"


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
            status=StockItemStatus.DISPONIVEL,
            quantity_on_hand=Decimal("0"),
            costing_method=CostingMethod.CUSTO_MEDIO,
        )
        assert stock_item.product_id == product_id
        assert stock_item.warehouse_id == warehouse_id
        assert stock_item.status == StockItemStatus.DISPONIVEL
        assert stock_item.quantity_on_hand == Decimal("0")
        assert stock_item.costing_method == CostingMethod.CUSTO_MEDIO

    def test_stock_item_status_enum(self) -> None:
        """Test StockItemStatus enum values."""
        assert StockItemStatus.DISPONIVEL.value == "disponivel"
        assert StockItemStatus.RESERVADO.value == "reservado"
        assert StockItemStatus.BLOQUEADO.value == "bloqueado"
        assert StockItemStatus.QUARENTENA.value == "quarentena"
        assert StockItemStatus.AVARIADO.value == "avariado"
        assert StockItemStatus.VENCIDO.value == "vencido"
        assert StockItemStatus.EM_TRANSFERENCIA.value == "em_transferencia"

    def test_costing_method_enum(self) -> None:
        """Test CostingMethod enum values."""
        assert CostingMethod.CUSTO_MEDIO.value == "custo_medio"
        assert CostingMethod.FIFO.value == "fifo"
        assert CostingMethod.LIFO.value == "lifo"
        assert CostingMethod.CUSTO_ESPECIFICO.value == "custo_especifico"
        assert CostingMethod.ULTIMO_CUSTO.value == "ultimo_custo"

    def test_stock_item_with_quantities(self) -> None:
        """Test stock item with quantities."""
        stock_item = StockItem(
            condominio_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            quantity_on_hand=Decimal("100.0000"),
            quantity_reserved=Decimal("20.0000"),
            quantity_committed=Decimal("10.0000"),
        )
        assert stock_item.quantity_on_hand == Decimal("100.0000")
        assert stock_item.quantity_reserved == Decimal("20.0000")
        assert stock_item.quantity_committed == Decimal("10.0000")

    def test_stock_item_with_costs(self) -> None:
        """Test stock item with cost tracking."""
        stock_item = StockItem(
            condominio_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            quantity_on_hand=Decimal("50"),
            unit_cost=Decimal("25.50"),
            total_cost=Decimal("1275.00"),
            average_cost=Decimal("25.50"),
            last_cost=Decimal("26.00"),
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
            abc_class="A",
            xyz_class="X",
        )
        assert stock_item.abc_class == "A"
        assert stock_item.xyz_class == "X"


class TestStockMovementModel:
    """Tests for StockMovement model."""

    def test_movement_creation_basic(self) -> None:
        """Test basic movement creation."""
        condo_id = uuid4()
        product_id = uuid4()
        warehouse_id = uuid4()
        movement = StockMovement(
            condominio_id=condo_id,
            number="MOV-2024-00001",
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementType.ENTRADA,
            reason=MovementReason.COMPRA,
            quantity=Decimal("100"),
            status=MovementStatus.RASCUNHO,
            movement_date=datetime.now(),
        )
        assert movement.number == "MOV-2024-00001"
        assert movement.movement_type == MovementType.ENTRADA
        assert movement.reason == MovementReason.COMPRA
        assert movement.status == MovementStatus.RASCUNHO
        assert movement.quantity == Decimal("100")

    def test_movement_type_enum(self) -> None:
        """Test MovementType enum values."""
        assert MovementType.ENTRADA.value == "entrada"
        assert MovementType.SAIDA.value == "saida"
        assert MovementType.TRANSFERENCIA.value == "transferencia"
        assert MovementType.AJUSTE_POSITIVO.value == "ajuste_positivo"
        assert MovementType.AJUSTE_NEGATIVO.value == "ajuste_negativo"
        assert MovementType.PERDA.value == "perda"
        assert MovementType.BONIFICACAO.value == "bonificacao"

    def test_movement_reason_enum(self) -> None:
        """Test MovementReason enum values."""
        assert MovementReason.COMPRA.value == "compra"
        assert MovementReason.VENDA.value == "venda"
        assert MovementReason.TRANSFERENCIA_ENTRADA.value == "transferencia_entrada"
        assert MovementReason.AJUSTE_INVENTARIO.value == "ajuste_inventario"
        assert MovementReason.AVARIA.value == "avaria"
        assert MovementReason.VENCIMENTO.value == "vencimento"
        assert MovementReason.PERDA.value == "perda"

    def test_movement_status_enum(self) -> None:
        """Test MovementStatus enum values."""
        assert MovementStatus.RASCUNHO.value == "rascunho"
        assert MovementStatus.PENDENTE.value == "pendente"
        assert MovementStatus.CONFIRMADA.value == "confirmada"
        assert MovementStatus.APROVADA.value == "aprovada"
        assert MovementStatus.CANCELADA.value == "cancelada"
        assert MovementStatus.ESTORNADA.value == "estornada"

    def test_movement_with_transfer(self) -> None:
        """Test movement for transfer."""
        dest_warehouse = uuid4()
        movement = StockMovement(
            condominio_id=uuid4(),
            number="MOV-2024-00002",
            product_id=uuid4(),
            warehouse_id=uuid4(),
            movement_type=MovementType.TRANSFERENCIA,
            reason=MovementReason.TRANSFERENCIA_SAIDA,
            destination_warehouse_id=dest_warehouse,
            quantity=Decimal("50"),
            movement_date=datetime.now(),
        )
        assert movement.movement_type == MovementType.TRANSFERENCIA
        assert movement.destination_warehouse_id == dest_warehouse

    def test_movement_with_balance(self) -> None:
        """Test movement with balance tracking."""
        movement = StockMovement(
            condominio_id=uuid4(),
            number="MOV-2024-00003",
            product_id=uuid4(),
            warehouse_id=uuid4(),
            movement_type=MovementType.ENTRADA,
            reason=MovementReason.COMPRA,
            quantity=Decimal("100"),
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
            number="INV-2024-001",
            description="Inventário Anual 2024",
            warehouse_id=warehouse_id,
            inventory_type=InventoryType.GERAL,
            status=InventoryStatus.PLANEJADO,
            blind_count=False,
        )
        assert inventory.number == "INV-2024-001"
        assert inventory.description == "Inventário Anual 2024"
        assert inventory.inventory_type == InventoryType.GERAL
        assert inventory.status == InventoryStatus.PLANEJADO
        assert inventory.blind_count is False

    def test_inventory_type_enum(self) -> None:
        """Test InventoryType enum values."""
        assert InventoryType.GERAL.value == "geral"
        assert InventoryType.PARCIAL.value == "parcial"
        assert InventoryType.ROTATIVO.value == "rotativo"
        assert InventoryType.ABC.value == "abc"
        assert InventoryType.CATEGORIA.value == "categoria"
        assert InventoryType.LOCALIZACAO.value == "localizacao"

    def test_inventory_status_enum(self) -> None:
        """Test InventoryStatus enum values."""
        assert InventoryStatus.PLANEJADO.value == "planejado"
        assert InventoryStatus.EM_ANDAMENTO.value == "em_andamento"
        assert InventoryStatus.CONTAGEM.value == "contagem"
        assert InventoryStatus.RECONFERENCIA.value == "reconferencia"
        assert InventoryStatus.AGUARDANDO_APROVACAO.value == "aguardando_aprovacao"
        assert InventoryStatus.APROVADO.value == "aprovado"
        assert InventoryStatus.AJUSTADO.value == "ajustado"
        assert InventoryStatus.FINALIZADO.value == "finalizado"
        assert InventoryStatus.CANCELADO.value == "cancelado"

    def test_inventory_with_settings(self) -> None:
        """Test inventory with settings."""
        inventory = StockInventory(
            condominio_id=uuid4(),
            number="INV-2024-002",
            description="Contagem Cega",
            warehouse_id=uuid4(),
            inventory_type=InventoryType.PARCIAL,
            blind_count=True,
            allow_recount=True,
            require_double_count=True,
        )
        assert inventory.inventory_type == InventoryType.PARCIAL
        assert inventory.blind_count is True
        assert inventory.allow_recount is True
        assert inventory.require_double_count is True

    def test_inventory_with_stats(self) -> None:
        """Test inventory with statistics."""
        inventory = StockInventory(
            condominio_id=uuid4(),
            number="INV-2024-003",
            description="Inventário Completo",
            warehouse_id=uuid4(),
            total_items=500,
            counted_items=450,
            divergent_items=25,
            adjusted_items=20,
            expected_value=Decimal("250000.00"),
            counted_value=Decimal("248500.00"),
            difference_value=Decimal("1500.00"),
            accuracy_rate=Decimal("95.00"),
        )
        assert inventory.total_items == 500
        assert inventory.counted_items == 450
        assert inventory.accuracy_rate == Decimal("95.00")


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
            expected_quantity=Decimal("100.0000"),
            expected_value=Decimal("1000.00"),
            unit_cost=Decimal("10.00"),
            status=InventoryItemStatus.PENDENTE,
        )
        assert item.inventory_id == inventory_id
        assert item.status == InventoryItemStatus.PENDENTE
        assert item.expected_quantity == Decimal("100.0000")

    def test_inventory_item_status_enum(self) -> None:
        """Test InventoryItemStatus enum values."""
        assert InventoryItemStatus.PENDENTE.value == "pendente"
        assert InventoryItemStatus.CONTADO.value == "contado"
        assert InventoryItemStatus.CONFERIDO.value == "conferido"
        assert InventoryItemStatus.DIVERGENTE.value == "divergente"
        assert InventoryItemStatus.AJUSTADO.value == "ajustado"
        assert InventoryItemStatus.APROVADO.value == "aprovado"

    def test_inventory_item_with_count(self) -> None:
        """Test inventory item with count data."""
        item = StockInventoryItem(
            inventory_id=uuid4(),
            stock_item_id=uuid4(),
            product_id=uuid4(),
            expected_quantity=Decimal("100.0000"),
            expected_value=Decimal("1000.00"),
            unit_cost=Decimal("10.00"),
            counted_quantity=Decimal("98.0000"),
            counted_value=Decimal("980.00"),
            difference_quantity=Decimal("-2.0000"),
            difference_value=Decimal("-20.00"),
            status=InventoryItemStatus.CONTADO,
        )
        assert item.counted_quantity == Decimal("98.0000")
        assert item.difference_quantity == Decimal("-2.0000")


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
            number="RES-2024-00001",
            stock_item_id=stock_item_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity_requested=Decimal("50.0000"),
            quantity_reserved=Decimal("50.0000"),
            reservation_date=datetime.now(),
            reservation_type=ReservationType.VENDA,
            status=ReservationStatus.ATIVA,
            priority=ReservationPriority.MEDIA,
        )
        assert reservation.number == "RES-2024-00001"
        assert reservation.reservation_type == ReservationType.VENDA
        assert reservation.status == ReservationStatus.ATIVA
        assert reservation.priority == ReservationPriority.MEDIA
        assert reservation.quantity_requested == Decimal("50.0000")

    def test_reservation_type_enum(self) -> None:
        """Test ReservationType enum values."""
        assert ReservationType.VENDA.value == "venda"
        assert ReservationType.PRODUCAO.value == "producao"
        assert ReservationType.TRANSFERENCIA.value == "transferencia"
        assert ReservationType.ORDEM_SERVICO.value == "ordem_servico"
        assert ReservationType.REQUISICAO.value == "requisicao"
        assert ReservationType.EVENTO.value == "evento"
        assert ReservationType.MANUTENCAO.value == "manutencao"
        assert ReservationType.OUTRO.value == "outro"

    def test_reservation_status_enum(self) -> None:
        """Test ReservationStatus enum values."""
        assert ReservationStatus.ATIVA.value == "ativa"
        assert ReservationStatus.ATENDIDA.value == "atendida"
        assert ReservationStatus.PARCIALMENTE_ATENDIDA.value == "parcialmente_atendida"
        assert ReservationStatus.LIBERADA.value == "liberada"
        assert ReservationStatus.CANCELADA.value == "cancelada"
        assert ReservationStatus.EXPIRADA.value == "expirada"

    def test_reservation_priority_enum(self) -> None:
        """Test ReservationPriority enum values."""
        assert ReservationPriority.BAIXA.value == "baixa"
        assert ReservationPriority.MEDIA.value == "media"
        assert ReservationPriority.ALTA.value == "alta"
        assert ReservationPriority.URGENTE.value == "urgente"
        assert ReservationPriority.CRITICA.value == "critica"

    def test_reservation_with_expiry(self) -> None:
        """Test reservation with expiry date."""
        expiry = datetime.now() + timedelta(days=7)
        reservation = StockReservation(
            condominio_id=uuid4(),
            number="RES-2024-00002",
            stock_item_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            quantity_requested=Decimal("25.0000"),
            quantity_reserved=Decimal("25.0000"),
            reservation_date=datetime.now(),
            expiry_date=expiry,
            auto_release=True,
        )
        assert reservation.expiry_date == expiry
        assert reservation.auto_release is True

    def test_reservation_partial_release(self) -> None:
        """Test reservation with partial release."""
        reservation = StockReservation(
            condominio_id=uuid4(),
            number="RES-2024-00003",
            stock_item_id=uuid4(),
            product_id=uuid4(),
            warehouse_id=uuid4(),
            quantity_requested=Decimal("100.0000"),
            quantity_reserved=Decimal("100.0000"),
            quantity_released=Decimal("40.0000"),
            quantity_pending=Decimal("60.0000"),
            reservation_date=datetime.now(),
            status=ReservationStatus.PARCIALMENTE_ATENDIDA,
            allow_partial=True,
        )
        assert reservation.quantity_released == Decimal("40.0000")
        assert reservation.quantity_pending == Decimal("60.0000")
        assert reservation.status == ReservationStatus.PARCIALMENTE_ATENDIDA
