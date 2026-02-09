"""
application/use_cases/inventory/receive_stock.py - RECEIVE STOCK USE CASE
========================================================================
Clean Architecture use case for stock receipt with financial integration
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from application.dto.inventory import CreateStockMovementDTO, StockMovementResponseDTO
from application.interfaces.unit_of_work import IUnitOfWork
from domains.financial import JournalEntryEntity, JournalEntryStatus, JournalEntryType, JournalLine, TransactionSource
from domains.inventory import MovementLine, StockMovementEntity, StockMovementType, WarehouseType

logger = logging.getLogger(__name__)


@dataclass
class ReceiveStockResult:
    """Resultado do recebimento de estoque."""

    success: bool
    movement: StockMovementResponseDTO | None = None
    journal_entry_id: UUID | None = None
    error_code: str | None = None
    error_message: str | None = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class ReceiveStockUseCase:
    """
    Use Case para recebimento de estoque.

    Implementa entrada de estoque com:
    - Atualizacao de saldo e custo medio
    - Geracao de lancamento contabil
    - Integracao com contas a pagar (se aplicavel)
    """

    # Contas contabeis padrao (configuravel)
    ACCOUNT_STOCK = "1.1.3.01"  # Estoque
    ACCOUNT_SUPPLIER = "2.1.1.01"  # Fornecedores

    def __init__(self, unit_of_work: IUnitOfWork, generate_journal_entry: bool = True):
        self._uow = unit_of_work
        self._generate_journal_entry = generate_journal_entry

    async def execute(self, dto: CreateStockMovementDTO) -> ReceiveStockResult:
        """
        Executa recebimento de estoque.

        Args:
            dto: Dados da movimentacao

        Returns:
            ReceiveStockResult com movimento criado ou erro
        """
        warnings: list[str] = []

        try:
            async with self._uow:
                # 1. Valida tipo de movimento
                if dto.movement_type != StockMovementType.PURCHASE.value:
                    return ReceiveStockResult(
                        success=False,
                        error_code="INVALID_MOVEMENT_TYPE",
                        error_message="Use case especifico para recebimento de compra",
                    )

                # 2. Valida e processa linhas
                movement_lines: list[MovementLine] = []
                products_to_update = []

                for line_dto in dto.lines:
                    # Busca produto
                    product = await self._uow.products.get_by_id(line_dto.product_id)
                    if not product:
                        return ReceiveStockResult(
                            success=False,
                            error_code="PRODUCT_NOT_FOUND",
                            error_message=f"Produto {line_dto.product_id} nao encontrado",
                        )

                    if not product.is_active:
                        return ReceiveStockResult(
                            success=False,
                            error_code="PRODUCT_INACTIVE",
                            error_message=f"Produto {product.sku} esta inativo",
                        )

                    # Cria linha de movimento
                    total_cost = (line_dto.quantity * line_dto.unit_cost).quantize(Decimal("0.01"))

                    movement_line = MovementLine(
                        product_id=product.product_id,
                        product_sku=product.sku,
                        product_name=product.name,
                        quantity=line_dto.quantity,
                        unit_of_measure=product.unit_of_measure,
                        unit_cost=line_dto.unit_cost,
                        total_cost=total_cost,
                    )
                    movement_lines.append(movement_line)

                    # Prepara atualizacao do produto
                    products_to_update.append(
                        {"product": product, "quantity": line_dto.quantity, "unit_cost": line_dto.unit_cost}
                    )

                    # Verifica estoque maximo
                    new_stock = product.current_stock + line_dto.quantity
                    if product.stock_level.maximum_stock > 0 and new_stock > product.stock_level.maximum_stock:
                        warnings.append(
                            f"Produto {product.sku} excedera estoque maximo "
                            f"(atual: {product.current_stock}, recebendo: {line_dto.quantity}, "
                            f"maximo: {product.stock_level.maximum_stock})"
                        )

                # 3. Cria movimento de estoque
                movement_number = StockMovementEntity.generate_movement_number(
                    datetime.now().year, int(uuid4().hex[:8], 16)
                )

                movement = StockMovementEntity(
                    movement_number=movement_number,
                    movement_type=StockMovementType.PURCHASE,
                    warehouse_id=dto.warehouse_id,
                    warehouse_code="",  # Sera preenchido pelo repositorio
                    warehouse_type=WarehouseType.MAIN,
                    source_document_type=dto.source_document_type,
                    source_document_id=dto.source_document_id,
                    source_document_number=dto.source_document_number,
                    description=dto.description,
                    lines=movement_lines,
                    tenant_id=dto.tenant_id,
                    created_by=dto.created_by,
                )

                # 4. Persiste movimento
                created_movement = await self._uow.stock_movements.create(movement)

                # 5. Atualiza estoque dos produtos
                for item in products_to_update:
                    product = item["product"]
                    product.receive_stock(
                        quantity=item["quantity"], unit_cost=item["unit_cost"], user_id=dto.created_by
                    )
                    await self._uow.products.update(product)

                # 6. Gera lancamento contabil (se configurado)
                journal_entry_id = None
                if self._generate_journal_entry:
                    journal_entry = await self._create_journal_entry(
                        movement=created_movement, tenant_id=dto.tenant_id, user_id=dto.created_by
                    )
                    if journal_entry:
                        created_entry = await self._uow.journal_entries.create(journal_entry)
                        journal_entry_id = created_entry.entry_id
                        created_movement.journal_entry_id = journal_entry_id

                # 7. Contabiliza movimento
                created_movement.post(dto.created_by)
                await self._uow.stock_movements.update(created_movement)

                # 8. Commit
                await self._uow.commit()

                # 9. Monta resposta
                response = StockMovementResponseDTO(
                    movement_id=created_movement.movement_id,
                    movement_number=created_movement.movement_number,
                    movement_type=created_movement.movement_type,
                    movement_date=created_movement.movement_date,
                    warehouse_id=created_movement.warehouse_id,
                    warehouse_code=created_movement.warehouse_code,
                    description=created_movement.description,
                    total_quantity=created_movement.total_quantity,
                    total_cost=created_movement.total_cost,
                    is_posted=created_movement.is_posted,
                    is_cancelled=created_movement.is_cancelled,
                    lines_count=len(created_movement.lines),
                    created_at=created_movement.created_at,
                    created_by=created_movement.created_by,
                )

                logger.info(
                    f"Estoque recebido: {created_movement.movement_number}",
                    extra={
                        "movement_id": str(created_movement.movement_id),
                        "total_quantity": str(created_movement.total_quantity),
                        "total_cost": str(created_movement.total_cost),
                        "products_count": len(products_to_update),
                        "journal_entry_id": str(journal_entry_id) if journal_entry_id else None,
                        "tenant_id": str(dto.tenant_id),
                        "user_id": dto.created_by,
                    },
                )

                return ReceiveStockResult(
                    success=True,
                    movement=response,
                    journal_entry_id=journal_entry_id,
                    warnings=warnings if warnings else None,
                )

        except ValueError as e:
            logger.warning(f"Erro de validacao no recebimento: {e}")
            return ReceiveStockResult(success=False, error_code="VALIDATION_ERROR", error_message=str(e))

        except Exception as e:
            logger.error(f"Erro no recebimento de estoque: {e}", exc_info=True)
            return ReceiveStockResult(
                success=False, error_code="INTERNAL_ERROR", error_message="Erro interno no recebimento de estoque"
            )

    async def _create_journal_entry(
        self, movement: StockMovementEntity, tenant_id: UUID, user_id: str
    ) -> JournalEntryEntity | None:
        """
        Cria lancamento contabil para o recebimento.

        Debito: Estoque (ativo)
        Credito: Fornecedores (passivo)
        """
        try:
            today = date.today()
            entry_number = JournalEntryEntity.generate_entry_number(today.year, int(uuid4().hex[:8], 16))

            # Linha de debito - Estoque
            debit_line = JournalLine(
                account_id=uuid4(),  # Seria buscado do plano de contas
                account_code=self.ACCOUNT_STOCK,
                account_name="Estoque de Mercadorias",
                debit_amount=movement.total_cost,
                credit_amount=Decimal("0"),
                description=f"Entrada estoque - {movement.movement_number}",
            )

            # Linha de credito - Fornecedores
            credit_line = JournalLine(
                account_id=uuid4(),  # Seria buscado do plano de contas
                account_code=self.ACCOUNT_SUPPLIER,
                account_name="Fornecedores",
                debit_amount=Decimal("0"),
                credit_amount=movement.total_cost,
                description=f"Compra a prazo - {movement.source_document_number or movement.movement_number}",
            )

            journal_entry = JournalEntryEntity(
                entry_number=entry_number,
                entry_type=JournalEntryType.STANDARD,
                status=JournalEntryStatus.APPROVED,  # Auto-aprovado para integracao
                source=TransactionSource.INVENTORY,
                source_document_id=movement.movement_id,
                source_document_number=movement.movement_number,
                entry_date=today,
                period_month=today.month,
                period_year=today.year,
                description=f"Entrada de estoque - {movement.description}",
                lines=[debit_line, credit_line],
                tenant_id=tenant_id,
                created_by=user_id,
            )

            return journal_entry

        except Exception as e:
            logger.error(f"Erro ao criar lancamento contabil: {e}")
            return None
