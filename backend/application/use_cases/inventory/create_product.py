"""
application/use_cases/inventory/create_product.py - CREATE PRODUCT USE CASE
==========================================================================
Clean Architecture use case for product creation
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

from application.dto.inventory import CreateProductDTO, ProductResponseDTO
from application.interfaces.unit_of_work import IUnitOfWork
from domains.inventory import (
    ProductDimensions,
    ProductEntity,
    ProductPricing,
    ProductStatus,
    ProductType,
    StockLevel,
    TaxClassification,
    UnitOfMeasure,
)

logger = logging.getLogger(__name__)


@dataclass
class CreateProductResult:
    """Resultado da criacao de produto."""

    success: bool
    product: ProductResponseDTO | None = None
    error_code: str | None = None
    error_message: str | None = None


class CreateProductUseCase:
    """
    Use Case para criacao de produto.

    Implementa regras de negocio e orquestra
    operacoes de dominio e persistencia.
    """

    def __init__(self, unit_of_work: IUnitOfWork):
        self._uow = unit_of_work

    async def execute(self, dto: CreateProductDTO) -> CreateProductResult:
        """
        Executa criacao de produto.

        Args:
            dto: Dados para criacao do produto

        Returns:
            CreateProductResult com produto criado ou erro
        """
        try:
            async with self._uow:
                # 1. Valida SKU unico
                existing = await self._uow.products.get_by_sku(dto.sku, dto.tenant_id)
                if existing:
                    return CreateProductResult(
                        success=False, error_code="SKU_EXISTS", error_message=f"SKU {dto.sku} ja existe"
                    )

                # 2. Valida codigo de barras unico (se informado)
                if dto.barcode:
                    existing_barcode = await self._uow.products.get_by_barcode(dto.barcode, dto.tenant_id)
                    if existing_barcode:
                        return CreateProductResult(
                            success=False,
                            error_code="BARCODE_EXISTS",
                            error_message=f"Codigo de barras {dto.barcode} ja existe",
                        )

                # 3. Cria entidade de dominio
                product = ProductEntity(
                    sku=dto.sku,
                    barcode=dto.barcode,
                    name=dto.name,
                    description=dto.description,
                    product_type=ProductType(dto.product_type),
                    status=ProductStatus.ACTIVE,
                    category_id=dto.category_id,
                    category_name="",  # Sera preenchido pelo repositorio
                    unit_of_measure=UnitOfMeasure(dto.unit_of_measure),
                    dimensions=ProductDimensions(
                        weight_kg=Decimal("0"), length_cm=Decimal("0"), width_cm=Decimal("0"), height_cm=Decimal("0")
                    ),
                    pricing=ProductPricing(
                        cost_price=dto.cost_price,
                        average_cost=dto.cost_price,
                        last_purchase_price=Decimal("0"),
                        sale_price=dto.sale_price,
                        minimum_price=Decimal("0"),
                        currency="BRL",
                    ),
                    stock_level=StockLevel(
                        minimum_stock=dto.minimum_stock,
                        maximum_stock=dto.maximum_stock,
                        reorder_point=dto.reorder_point,
                        reorder_quantity=Decimal("0"),
                        safety_stock=Decimal("0"),
                        lead_time_days=0,
                    ),
                    tax_classification=TaxClassification(
                        ncm=dto.ncm,
                        cfop_sale="5102",
                        cfop_purchase="1102",
                        origin="0",
                        icms_cst="00",
                        pis_cst="01",
                        cofins_cst="01",
                    ),
                    tenant_id=dto.tenant_id,
                    created_by=dto.created_by,
                )

                # 4. Persiste
                created = await self._uow.products.create(product)
                await self._uow.commit()

                # 5. Monta resposta
                response = ProductResponseDTO(
                    product_id=created.product_id,
                    sku=created.sku,
                    name=created.name,
                    description=created.description,
                    product_type=created.product_type,
                    status=created.status,
                    category_id=created.category_id,
                    category_name=created.category_name,
                    unit_of_measure=created.unit_of_measure,
                    cost_price=created.pricing.cost_price,
                    average_cost=created.pricing.average_cost,
                    sale_price=created.pricing.sale_price,
                    current_stock=created.current_stock,
                    available_stock=created.available_stock,
                    reserved_stock=created.reserved_stock,
                    stock_status=created.stock_status.value,
                    stock_value=created.stock_value,
                    created_at=created.created_at,
                    updated_at=created.updated_at,
                )

                logger.info(
                    f"Produto criado: {created.sku} - {created.name}",
                    extra={
                        "product_id": str(created.product_id),
                        "tenant_id": str(dto.tenant_id),
                        "user_id": dto.created_by,
                    },
                )

                return CreateProductResult(success=True, product=response)

        except ValueError as e:
            logger.warning(f"Erro de validacao ao criar produto: {e}")
            return CreateProductResult(success=False, error_code="VALIDATION_ERROR", error_message=str(e))

        except Exception as e:
            logger.error(f"Erro ao criar produto: {e}", exc_info=True)
            return CreateProductResult(
                success=False, error_code="INTERNAL_ERROR", error_message="Erro interno ao criar produto"
            )
