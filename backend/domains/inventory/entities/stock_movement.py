"""
domains/inventory/entities/stock_movement.py - STOCK MOVEMENT ENTITY
====================================================================
Enterprise stock movement tracking with full traceability
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, NewType
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import BatchStatus, StockMovementType, StockStatus, WarehouseType

# Strong typing for domain identifiers
MovementId = NewType("MovementId", UUID)
BatchId = NewType("BatchId", UUID)
WarehouseId = NewType("WarehouseId", UUID)


class BatchInfo(BaseModel):
    """Informacoes do lote - Value Object."""

    model_config = ConfigDict(frozen=True)

    batch_id: UUID = Field(default_factory=uuid4)
    batch_number: str = Field(..., pattern=r"^[A-Z0-9\-]{3,30}$")
    manufacturing_date: date | None = None
    expiration_date: date | None = None
    status: BatchStatus = Field(default=BatchStatus.ACTIVE)
    supplier_batch: str | None = None
    quantity: Decimal = Field(..., gt=Decimal("0"))
    unit_cost: Decimal = Field(..., ge=Decimal("0"))

    @property
    def is_expired(self) -> bool:
        """Verifica se lote esta vencido."""
        if not self.expiration_date:
            return False
        return self.expiration_date < date.today()

    @property
    def days_to_expire(self) -> int | None:
        """Dias para vencimento."""
        if not self.expiration_date:
            return None
        return (self.expiration_date - date.today()).days


class SerialNumber(BaseModel):
    """Numero de serie - Value Object."""

    model_config = ConfigDict(frozen=True)

    serial_id: UUID = Field(default_factory=uuid4)
    serial_number: str = Field(..., min_length=3, max_length=50)
    status: StockStatus = Field(default=StockStatus.AVAILABLE)
    warranty_end_date: date | None = None
    notes: str | None = None


class MovementLine(BaseModel):
    """Linha de movimento - Value Object."""

    model_config = ConfigDict(frozen=True)

    line_id: UUID = Field(default_factory=uuid4)
    product_id: UUID
    product_sku: str
    product_name: str
    quantity: Decimal = Field(..., gt=Decimal("0"))
    unit_of_measure: str
    unit_cost: Decimal = Field(..., ge=Decimal("0"))
    total_cost: Decimal = Field(..., ge=Decimal("0"))

    # Batch/Serial
    batch_info: BatchInfo | None = None
    serial_numbers: list[str] = Field(default_factory=list)

    # Location
    from_location: str | None = None
    to_location: str | None = None

    @model_validator(mode="after")
    def validate_line(self) -> "MovementLine":
        """Valida que total = quantidade * custo."""
        expected_total = (self.quantity * self.unit_cost).quantize(Decimal("0.01"))
        if self.total_cost != expected_total:
            # Auto-corrige
            object.__setattr__(self, "total_cost", expected_total)
        return self


class StockMovementEntity(BaseModel):
    """
    Entidade de movimentacao de estoque.

    Registra todas as entradas e saidas de estoque
    com rastreabilidade completa.
    """

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

    # Identity
    movement_id: UUID = Field(default_factory=uuid4)
    movement_number: str = Field(..., pattern=r"^MOV-\d{4}-\d{8}$")

    # Type
    movement_type: StockMovementType
    movement_date: datetime = Field(default_factory=datetime.utcnow)
    posting_date: datetime | None = None

    # Warehouse
    warehouse_id: UUID
    warehouse_code: str
    warehouse_type: WarehouseType
    destination_warehouse_id: UUID | None = None  # Para transferencias
    destination_warehouse_code: str | None = None

    # Document
    source_document_type: str | None = None  # NF, PO, SO, etc.
    source_document_id: UUID | None = None
    source_document_number: str | None = None
    fiscal_document_number: str | None = None
    fiscal_document_series: str | None = None

    # Header
    description: str = Field(..., min_length=5, max_length=500)
    notes: str | None = Field(None, max_length=2000)

    # Lines
    lines: list[MovementLine] = Field(..., min_length=1)

    # Totals
    total_quantity: Decimal = Field(default=Decimal("0"))
    total_cost: Decimal = Field(default=Decimal("0"))
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")

    # Status
    is_posted: bool = Field(default=False)
    is_cancelled: bool = Field(default=False)
    cancellation_reason: str | None = None
    cancelled_at: datetime | None = None
    cancelled_by: str | None = None

    # Financial Integration
    journal_entry_id: UUID | None = None  # Lancamento contabil
    cost_center_id: UUID | None = None

    # Multi-tenant
    tenant_id: UUID

    # Audit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    updated_by: str | None = None
    posted_by: str | None = None
    posted_at: datetime | None = None

    @model_validator(mode="after")
    def validate_movement(self) -> "StockMovementEntity":
        """Valida e calcula totais do movimento."""
        # Calcula totais
        self.total_quantity = sum(line.quantity for line in self.lines)
        self.total_cost = sum(line.total_cost for line in self.lines)

        # Valida transferencia
        if self.movement_type in [StockMovementType.TRANSFER_IN, StockMovementType.TRANSFER_OUT]:
            if not self.destination_warehouse_id:
                raise ValueError("Transferencia requer almoxarifado de destino")
            if self.warehouse_id == self.destination_warehouse_id:
                raise ValueError("Almoxarifado de origem e destino devem ser diferentes")

        # Valida documento fiscal
        if StockMovementType(self.movement_type).requires_document():
            if not self.fiscal_document_number:
                # Permite criar sem NF, mas gera warning
                pass

        return self

    # ==========================================================================
    # Business Methods
    # ==========================================================================

    @property
    def is_entry(self) -> bool:
        """Verifica se e movimento de entrada."""
        return StockMovementType(self.movement_type).is_entry()

    @property
    def is_exit(self) -> bool:
        """Verifica se e movimento de saida."""
        return StockMovementType(self.movement_type).is_exit()

    @property
    def affects_cost(self) -> bool:
        """Verifica se afeta custo medio."""
        return StockMovementType(self.movement_type).affects_cost()

    @property
    def can_be_posted(self) -> bool:
        """Verifica se pode ser contabilizado."""
        return not self.is_posted and not self.is_cancelled

    @property
    def can_be_cancelled(self) -> bool:
        """Verifica se pode ser cancelado."""
        return self.is_posted and not self.is_cancelled

    def post(self, user_id: str) -> bool:
        """Contabiliza o movimento."""
        if not self.can_be_posted:
            raise ValueError("Movimento nao pode ser contabilizado")

        self.is_posted = True
        self.posting_date = datetime.utcnow()
        self.posted_by = user_id
        self.posted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return True

    def cancel(self, user_id: str, reason: str) -> bool:
        """Cancela o movimento."""
        if not self.can_be_cancelled:
            raise ValueError("Movimento nao pode ser cancelado")

        if len(reason) < 10:
            raise ValueError("Motivo de cancelamento deve ter pelo menos 10 caracteres")

        self.is_cancelled = True
        self.cancellation_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = user_id
        self.updated_at = datetime.utcnow()
        self.updated_by = user_id

        return True

    def add_line(self, line: MovementLine) -> None:
        """Adiciona linha ao movimento."""
        if self.is_posted:
            raise ValueError("Movimento ja contabilizado nao pode ser alterado")

        self.lines.append(line)
        self._recalculate_totals()
        self.updated_at = datetime.utcnow()

    def remove_line(self, line_id: UUID) -> bool:
        """Remove linha do movimento."""
        if self.is_posted:
            raise ValueError("Movimento ja contabilizado nao pode ser alterado")

        original_count = len(self.lines)
        self.lines = [line for line in self.lines if line.line_id != line_id]

        if len(self.lines) == original_count:
            return False

        if len(self.lines) == 0:
            raise ValueError("Movimento deve ter pelo menos uma linha")

        self._recalculate_totals()
        self.updated_at = datetime.utcnow()
        return True

    def _recalculate_totals(self) -> None:
        """Recalcula totais do movimento."""
        self.total_quantity = sum(line.quantity for line in self.lines)
        self.total_cost = sum(line.total_cost for line in self.lines)

    def get_products_affected(self) -> list[UUID]:
        """Retorna IDs dos produtos afetados."""
        return list({line.product_id for line in self.lines})

    def get_line_by_product(self, product_id: UUID) -> MovementLine | None:
        """Busca linha por produto."""
        for line in self.lines:
            if line.product_id == product_id:
                return line
        return None

    @staticmethod
    def generate_movement_number(year: int, sequence: int) -> str:
        """Gera numero do movimento."""
        return f"MOV-{year}-{sequence:08d}"

    def to_summary(self) -> dict[str, Any]:
        """Retorna resumo do movimento."""
        return {
            "movement_id": str(self.movement_id),
            "movement_number": self.movement_number,
            "movement_type": self.movement_type,
            "movement_date": self.movement_date.isoformat(),
            "warehouse": self.warehouse_code,
            "total_quantity": str(self.total_quantity),
            "total_cost": str(self.total_cost),
            "lines_count": len(self.lines),
            "is_posted": self.is_posted,
            "is_cancelled": self.is_cancelled,
        }

    def create_reversal(self, user_id: str, reason: str) -> "StockMovementEntity":
        """Cria movimento de estorno."""
        if not self.is_posted:
            raise ValueError("Apenas movimentos contabilizados podem ser estornados")

        # Inverte tipo de movimento
        reversal_type_map = {
            StockMovementType.PURCHASE: StockMovementType.RETURN_SUPPLIER,
            StockMovementType.SALE: StockMovementType.RETURN_CUSTOMER,
            StockMovementType.TRANSFER_IN: StockMovementType.TRANSFER_OUT,
            StockMovementType.TRANSFER_OUT: StockMovementType.TRANSFER_IN,
            StockMovementType.ADJUSTMENT_IN: StockMovementType.ADJUSTMENT_OUT,
            StockMovementType.ADJUSTMENT_OUT: StockMovementType.ADJUSTMENT_IN,
        }

        reversal_type = reversal_type_map.get(
            StockMovementType(self.movement_type),
            StockMovementType.ADJUSTMENT_OUT if self.is_entry else StockMovementType.ADJUSTMENT_IN,
        )

        reversal = StockMovementEntity(
            movement_number=f"MOV-{datetime.now().year}-{uuid4().hex[:8].upper()}",
            movement_type=reversal_type,
            warehouse_id=self.warehouse_id,
            warehouse_code=self.warehouse_code,
            warehouse_type=self.warehouse_type,
            destination_warehouse_id=self.destination_warehouse_id,
            destination_warehouse_code=self.destination_warehouse_code,
            source_document_type="REVERSAL",
            source_document_id=self.movement_id,
            source_document_number=self.movement_number,
            description=f"Estorno de {self.movement_number}: {reason}",
            notes=reason,
            lines=self.lines,  # Mesmas linhas
            tenant_id=self.tenant_id,
            created_by=user_id,
        )

        return reversal
