"""
tests/domains/inventory/test_product.py - PRODUCT ENTITY TESTS
=============================================================
Enterprise tests for product management
"""

import sys
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend")

from domains.inventory import (
    ProductDimensions,
    ProductEntity,
    ProductPricing,
    ProductStatus,
    ProductType,
    ReorderPointStatus,
    StockLevel,
    TaxClassification,
    UnitOfMeasure,
)


class TestProductPricing:
    """Testes para precificacao de produto."""

    def test_calculate_markup(self):
        """Testa calculo de markup."""
        pricing = ProductPricing(
            cost_price=Decimal("50.00"),
            average_cost=Decimal("50.00"),
            last_purchase_price=Decimal("48.00"),
            sale_price=Decimal("100.00"),
            minimum_price=Decimal("70.00"),
            currency="BRL",
        )

        assert pricing.markup_percent == Decimal("100.00")

    def test_calculate_margin(self):
        """Testa calculo de margem."""
        pricing = ProductPricing(
            cost_price=Decimal("50.00"),
            average_cost=Decimal("50.00"),
            last_purchase_price=Decimal("48.00"),
            sale_price=Decimal("100.00"),
            minimum_price=Decimal("70.00"),
            currency="BRL",
        )

        assert pricing.margin_percent == Decimal("50.00")


class TestStockLevel:
    """Testes para niveis de estoque."""

    def test_valid_stock_levels(self):
        """Testa niveis de estoque validos."""
        level = StockLevel(
            minimum_stock=Decimal("10"),
            maximum_stock=Decimal("100"),
            reorder_point=Decimal("20"),
            reorder_quantity=Decimal("50"),
            safety_stock=Decimal("5"),
            lead_time_days=7,
        )

        assert level.minimum_stock == Decimal("10")
        assert level.maximum_stock == Decimal("100")

    def test_reject_invalid_levels(self):
        """Testa rejeicao de niveis invalidos."""
        with pytest.raises(ValueError, match="minimo nao pode exceder"):
            StockLevel(
                minimum_stock=Decimal("100"),  # Maior que maximo
                maximum_stock=Decimal("50"),
                reorder_point=Decimal("20"),
                reorder_quantity=Decimal("50"),
                safety_stock=Decimal("5"),
                lead_time_days=7,
            )


class TestProductEntity:
    """Testes para entidade de produto."""

    @pytest.fixture
    def sample_product(self) -> ProductEntity:
        """Fixture para produto de exemplo."""
        return ProductEntity(
            sku="PROD-000001",
            barcode="7891234567890",
            name="Produto Teste",
            description="Descricao do produto teste",
            product_type=ProductType.FINISHED_GOODS,
            status=ProductStatus.ACTIVE,
            category_id=uuid4(),
            category_name="Categoria Teste",
            unit_of_measure=UnitOfMeasure.UNIT,
            dimensions=ProductDimensions(
                weight_kg=Decimal("1.5"), length_cm=Decimal("30"), width_cm=Decimal("20"), height_cm=Decimal("10")
            ),
            pricing=ProductPricing(
                cost_price=Decimal("50.00"),
                average_cost=Decimal("50.00"),
                last_purchase_price=Decimal("48.00"),
                sale_price=Decimal("89.90"),
                minimum_price=Decimal("70.00"),
                currency="BRL",
            ),
            stock_level=StockLevel(
                minimum_stock=Decimal("10"),
                maximum_stock=Decimal("1000"),
                reorder_point=Decimal("50"),
                reorder_quantity=Decimal("100"),
                safety_stock=Decimal("20"),
                lead_time_days=7,
            ),
            tax_classification=TaxClassification(
                ncm="12345678",
                cfop_sale="5102",
                cfop_purchase="1102",
                origin="0",
                icms_cst="00",
                pis_cst="01",
                cofins_cst="01",
            ),
            current_stock=Decimal("100"),
            reserved_stock=Decimal("10"),
            tenant_id=uuid4(),
            created_by="test-user",
        )

    def test_create_product(self, sample_product: ProductEntity):
        """Testa criacao de produto."""
        assert sample_product.sku == "PROD-000001"
        assert sample_product.is_active is True
        assert sample_product.is_stockable is True

    def test_available_stock_calculation(self, sample_product: ProductEntity):
        """Testa calculo de estoque disponivel."""
        assert sample_product.available_stock == Decimal("90")  # 100 - 10

    def test_stock_value_calculation(self, sample_product: ProductEntity):
        """Testa calculo de valor do estoque."""
        expected = Decimal("100") * Decimal("50.00")
        assert sample_product.stock_value == expected

    def test_stock_status_normal(self, sample_product: ProductEntity):
        """Testa status de estoque normal."""
        assert sample_product.stock_status == ReorderPointStatus.NORMAL

    def test_stock_status_warning(self, sample_product: ProductEntity):
        """Testa status de estoque em alerta."""
        sample_product.current_stock = Decimal("45")  # Abaixo do ponto de reposicao
        sample_product.available_stock = Decimal("45") - sample_product.reserved_stock

        assert sample_product.stock_status == ReorderPointStatus.WARNING

    def test_stock_status_critical(self, sample_product: ProductEntity):
        """Testa status de estoque critico."""
        sample_product.current_stock = Decimal("5")  # Abaixo do minimo
        sample_product.reserved_stock = Decimal("0")
        sample_product.available_stock = Decimal("5")

        assert sample_product.stock_status == ReorderPointStatus.CRITICAL

    def test_stock_status_stockout(self, sample_product: ProductEntity):
        """Testa status de ruptura."""
        sample_product.current_stock = Decimal("0")
        sample_product.reserved_stock = Decimal("0")
        sample_product.available_stock = Decimal("0")

        assert sample_product.stock_status == ReorderPointStatus.STOCKOUT


class TestStockOperations:
    """Testes para operacoes de estoque."""

    @pytest.fixture
    def product_with_stock(self) -> ProductEntity:
        """Fixture para produto com estoque."""
        return ProductEntity(
            sku="STK-000001",
            name="Produto com Estoque",
            product_type=ProductType.FINISHED_GOODS,
            category_id=uuid4(),
            category_name="Teste",
            unit_of_measure=UnitOfMeasure.UNIT,
            dimensions=ProductDimensions(
                weight_kg=Decimal("0"), length_cm=Decimal("0"), width_cm=Decimal("0"), height_cm=Decimal("0")
            ),
            pricing=ProductPricing(
                cost_price=Decimal("100.00"),
                average_cost=Decimal("100.00"),
                last_purchase_price=Decimal("0"),
                sale_price=Decimal("150.00"),
                minimum_price=Decimal("0"),
                currency="BRL",
            ),
            stock_level=StockLevel(
                minimum_stock=Decimal("0"),
                maximum_stock=Decimal("0"),
                reorder_point=Decimal("0"),
                reorder_quantity=Decimal("0"),
                safety_stock=Decimal("0"),
                lead_time_days=0,
            ),
            tax_classification=TaxClassification(
                ncm="12345678",
                cfop_sale="5102",
                cfop_purchase="1102",
                origin="0",
                icms_cst="00",
                pis_cst="01",
                cofins_cst="01",
            ),
            current_stock=Decimal("100"),
            reserved_stock=Decimal("0"),
            tenant_id=uuid4(),
            created_by="test-user",
        )

    def test_receive_stock(self, product_with_stock: ProductEntity):
        """Testa recebimento de estoque."""
        new_stock = product_with_stock.receive_stock(
            quantity=Decimal("50"), unit_cost=Decimal("90.00"), user_id="test-user"
        )

        assert new_stock == Decimal("150")
        # Custo medio: (100 * 100 + 50 * 90) / 150 = 96.67
        assert product_with_stock.pricing.average_cost == Decimal("96.67")

    def test_ship_stock(self, product_with_stock: ProductEntity):
        """Testa expedicao de estoque."""
        new_stock = product_with_stock.ship_stock(quantity=Decimal("30"), user_id="test-user")

        assert new_stock == Decimal("70")

    def test_ship_stock_insufficient(self, product_with_stock: ProductEntity):
        """Testa expedicao com estoque insuficiente."""
        with pytest.raises(ValueError, match="insuficiente"):
            product_with_stock.ship_stock(quantity=Decimal("150"), user_id="test-user")

    def test_reserve_stock(self, product_with_stock: ProductEntity):
        """Testa reserva de estoque."""
        result = product_with_stock.reserve_stock(quantity=Decimal("20"), user_id="test-user")

        assert result is True
        assert product_with_stock.reserved_stock == Decimal("20")
        assert product_with_stock.available_stock == Decimal("80")

    def test_release_reservation(self, product_with_stock: ProductEntity):
        """Testa liberacao de reserva."""
        product_with_stock.reserve_stock(Decimal("20"), "test-user")
        result = product_with_stock.release_reservation(quantity=Decimal("10"), user_id="test-user")

        assert result is True
        assert product_with_stock.reserved_stock == Decimal("10")
        assert product_with_stock.available_stock == Decimal("90")

    def test_adjust_stock(self, product_with_stock: ProductEntity):
        """Testa ajuste de estoque (inventario)."""
        difference = product_with_stock.adjust_stock(
            new_quantity=Decimal("95"), user_id="test-user", reason="Ajuste de inventario"
        )

        assert difference == Decimal("-5")
        assert product_with_stock.current_stock == Decimal("95")


class TestProductLifecycle:
    """Testes para ciclo de vida do produto."""

    @pytest.fixture
    def active_product(self) -> ProductEntity:
        """Fixture para produto ativo."""
        return ProductEntity(
            sku="LFC-000001",
            name="Produto Ciclo de Vida",
            product_type=ProductType.FINISHED_GOODS,
            category_id=uuid4(),
            category_name="Teste",
            unit_of_measure=UnitOfMeasure.UNIT,
            dimensions=ProductDimensions(
                weight_kg=Decimal("0"), length_cm=Decimal("0"), width_cm=Decimal("0"), height_cm=Decimal("0")
            ),
            pricing=ProductPricing(
                cost_price=Decimal("100.00"),
                average_cost=Decimal("100.00"),
                last_purchase_price=Decimal("0"),
                sale_price=Decimal("150.00"),
                minimum_price=Decimal("0"),
                currency="BRL",
            ),
            stock_level=StockLevel(
                minimum_stock=Decimal("0"),
                maximum_stock=Decimal("0"),
                reorder_point=Decimal("0"),
                reorder_quantity=Decimal("0"),
                safety_stock=Decimal("0"),
                lead_time_days=0,
            ),
            tax_classification=TaxClassification(
                ncm="12345678",
                cfop_sale="5102",
                cfop_purchase="1102",
                origin="0",
                icms_cst="00",
                pis_cst="01",
                cofins_cst="01",
            ),
            current_stock=Decimal("0"),
            tenant_id=uuid4(),
            created_by="test-user",
        )

    def test_deactivate_product_without_stock(self, active_product: ProductEntity):
        """Testa desativacao de produto sem estoque."""
        active_product.deactivate("test-user")

        assert active_product.status == ProductStatus.INACTIVE
        assert active_product.is_active is False

    def test_deactivate_product_with_stock_fails(self, active_product: ProductEntity):
        """Testa que produto com estoque nao pode ser desativado."""
        active_product.current_stock = Decimal("10")

        with pytest.raises(ValueError, match="com estoque"):
            active_product.deactivate("test-user")

    def test_discontinue_product(self, active_product: ProductEntity):
        """Testa descontinuacao de produto."""
        active_product.discontinue("test-user")

        assert active_product.status == ProductStatus.DISCONTINUED

    def test_reactivate_product(self, active_product: ProductEntity):
        """Testa reativacao de produto."""
        active_product.deactivate("test-user")
        active_product.activate("test-user")

        assert active_product.status == ProductStatus.ACTIVE
        assert active_product.is_active is True
