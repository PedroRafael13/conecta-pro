"""Model para itens em estoque."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.product import Product
    from modules.financial.models.warehouse import Warehouse


class StockItemStatus(StrEnum):
    """Status do item em estoque."""

    DISPONIVEL = "disponivel"
    RESERVADO = "reservado"
    BLOQUEADO = "bloqueado"
    QUARENTENA = "quarentena"
    AVARIADO = "avariado"
    VENCIDO = "vencido"
    EM_TRANSFERENCIA = "em_transferencia"


class CostingMethod(StrEnum):
    """Método de custeio."""

    CUSTO_MEDIO = "custo_medio"
    FIFO = "fifo"  # First In, First Out
    LIFO = "lifo"  # Last In, First Out
    CUSTO_ESPECIFICO = "custo_especifico"
    ULTIMO_CUSTO = "ultimo_custo"


class StockItem(Base):
    """Item em estoque (saldo por produto + armazém + lote)."""

    __tablename__ = "stock_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Produto
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    # Armazém
    warehouse_id = Column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id"),
        nullable=False,
        index=True,
    )

    # Status
    status = Column(String(20), nullable=False, default=StockItemStatus.DISPONIVEL.value)

    # Lote e validade
    batch_number = Column(String(50), nullable=True, index=True)  # Número do lote
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    serial_number = Column(String(100), nullable=True)  # Número de série (se aplicável)

    # Quantidades
    quantity_on_hand = Column(Numeric(15, 4), default=0)  # Quantidade em mãos
    quantity_reserved = Column(Numeric(15, 4), default=0)  # Quantidade reservada
    quantity_committed = Column(Numeric(15, 4), default=0)  # Quantidade comprometida (ordens)
    quantity_on_order = Column(Numeric(15, 4), default=0)  # Quantidade em pedido (compras)
    quantity_in_transit = Column(Numeric(15, 4), default=0)  # Quantidade em trânsito

    # Custos
    unit_cost = Column(Numeric(15, 4), default=0)  # Custo unitário atual
    average_cost = Column(Numeric(15, 4), default=0)  # Custo médio ponderado
    last_cost = Column(Numeric(15, 4), default=0)  # Último custo de compra
    total_cost = Column(Numeric(15, 2), default=0)  # Custo total (qty * unit_cost)
    costing_method = Column(String(20), default=CostingMethod.CUSTO_MEDIO.value)

    # Localização (endereçamento)
    location_code = Column(String(50), nullable=True)  # Código do endereço completo
    aisle = Column(String(10), nullable=True)  # Corredor
    rack = Column(String(10), nullable=True)  # Prateleira
    shelf = Column(String(10), nullable=True)  # Nível
    bin = Column(String(10), nullable=True)  # Posição/Bin

    # Parâmetros de estoque (sobrescreve produto)
    min_quantity = Column(Numeric(15, 4), nullable=True)  # Estoque mínimo
    max_quantity = Column(Numeric(15, 4), nullable=True)  # Estoque máximo
    reorder_point = Column(Numeric(15, 4), nullable=True)  # Ponto de pedido
    reorder_quantity = Column(Numeric(15, 4), nullable=True)  # Quantidade de reposição
    safety_stock = Column(Numeric(15, 4), nullable=True)  # Estoque de segurança

    # Última movimentação
    last_receipt_date = Column(DateTime, nullable=True)  # Última entrada
    last_issue_date = Column(DateTime, nullable=True)  # Última saída
    last_count_date = Column(DateTime, nullable=True)  # Última contagem
    last_movement_at = Column(DateTime, nullable=True)

    # Contador de movimentações
    receipt_count = Column(String(10), default="0")  # Total de entradas
    issue_count = Column(String(10), default="0")  # Total de saídas

    # ABC/XYZ Classification
    abc_class = Column(String(1), nullable=True)  # A, B ou C (valor)
    xyz_class = Column(String(1), nullable=True)  # X, Y ou Z (variabilidade)

    # Bloqueio
    is_blocked = Column(Boolean, default=False)
    blocked_reason = Column(Text, nullable=True)
    blocked_at = Column(DateTime, nullable=True)
    blocked_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Observações
    notes = Column(Text, nullable=True)

    # Metadados
    extra_data = Column(JSONB, default=dict)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    product: "Product" = relationship("Product")
    warehouse: "Warehouse" = relationship("Warehouse", back_populates="stock_items")

    __table_args__ = (
        Index("ix_stock_items_product", "product_id"),
        Index("ix_stock_items_warehouse", "warehouse_id"),
        Index("ix_stock_items_batch", "batch_number"),
        Index("ix_stock_items_expiry", "expiry_date"),
        Index("ix_stock_items_location", "location_code"),
        Index("ix_stock_items_status", "status"),
        Index("ix_stock_items_condominio", "condominio_id"),
        Index(
            "ix_stock_items_product_warehouse_batch",
            "product_id",
            "warehouse_id",
            "batch_number",
        ),
    )

    def __repr__(self) -> str:
        batch = f" [{self.batch_number}]" if self.batch_number else ""
        return f"<StockItem {self.product_id}{batch}>"

    @property
    def quantity_available(self) -> Decimal:
        """Quantidade disponível para uso."""
        on_hand = self.quantity_on_hand or Decimal("0")
        reserved = self.quantity_reserved or Decimal("0")
        committed = self.quantity_committed or Decimal("0")
        return on_hand - reserved - committed

    @property
    def is_available(self) -> bool:
        """Verifica se está disponível."""
        return self.status == StockItemStatus.DISPONIVEL.value and self.quantity_available > 0 and not self.is_blocked

    @property
    def is_low_stock(self) -> bool:
        """Verifica se está abaixo do mínimo."""
        if self.min_quantity:
            return (self.quantity_on_hand or Decimal("0")) < self.min_quantity
        return False

    @property
    def is_below_reorder_point(self) -> bool:
        """Verifica se está abaixo do ponto de pedido."""
        if self.reorder_point:
            return (self.quantity_on_hand or Decimal("0")) <= self.reorder_point
        return False

    @property
    def is_overstocked(self) -> bool:
        """Verifica se está acima do máximo."""
        if self.max_quantity:
            return (self.quantity_on_hand or Decimal("0")) > self.max_quantity
        return False

    @property
    def is_expired(self) -> bool:
        """Verifica se está vencido."""
        if self.expiry_date:
            return datetime.utcnow().date() > self.expiry_date
        return False

    @property
    def days_to_expiry(self) -> int | None:
        """Dias até vencer."""
        if self.expiry_date:
            delta = self.expiry_date - datetime.utcnow().date()
            return delta.days
        return None

    @property
    def is_expiring_soon(self) -> bool:
        """Verifica se vai vencer em 30 dias."""
        days = self.days_to_expiry
        return days is not None and 0 < days <= 30

    @property
    def full_location(self) -> str:
        """Localização completa."""
        parts = []
        if self.aisle:
            parts.append(f"C{self.aisle}")
        if self.rack:
            parts.append(f"P{self.rack}")
        if self.shelf:
            parts.append(f"N{self.shelf}")
        if self.bin:
            parts.append(f"B{self.bin}")
        return "-".join(parts) if parts else self.location_code or ""

    @property
    def classification(self) -> str:
        """Classificação ABC-XYZ combinada."""
        abc = self.abc_class or "-"
        xyz = self.xyz_class or "-"
        return f"{abc}{xyz}"

    def receive(self, quantity: Decimal, unit_cost: Decimal) -> None:
        """Registra entrada de estoque."""
        current_qty = self.quantity_on_hand or Decimal("0")
        current_cost = self.total_cost or Decimal("0")

        # Atualiza quantidade
        new_qty = current_qty + quantity
        self.quantity_on_hand = new_qty

        # Calcula custo médio ponderado
        if new_qty > 0:
            new_total = current_cost + (quantity * unit_cost)
            self.average_cost = new_total / new_qty
            self.total_cost = new_total
        else:
            self.average_cost = unit_cost
            self.total_cost = Decimal("0")

        # Atualiza último custo
        self.last_cost = unit_cost
        self.unit_cost = self.average_cost
        self.last_receipt_date = datetime.utcnow()
        self.last_movement_at = datetime.utcnow()

        # Incrementa contador
        self.receipt_count = str(int(self.receipt_count or "0") + 1)

    def issue(self, quantity: Decimal) -> None:
        """Registra saída de estoque."""
        current_qty = self.quantity_on_hand or Decimal("0")

        if quantity > current_qty:
            raise ValueError("Quantidade insuficiente em estoque")

        new_qty = current_qty - quantity
        self.quantity_on_hand = new_qty
        self.total_cost = new_qty * (self.unit_cost or Decimal("0"))
        self.last_issue_date = datetime.utcnow()
        self.last_movement_at = datetime.utcnow()

        # Incrementa contador
        self.issue_count = str(int(self.issue_count or "0") + 1)

    def reserve(self, quantity: Decimal) -> bool:
        """Reserva quantidade."""
        if quantity > self.quantity_available:
            return False
        self.quantity_reserved = (self.quantity_reserved or Decimal("0")) + quantity
        return True

    def release_reservation(self, quantity: Decimal) -> None:
        """Libera reserva."""
        current = self.quantity_reserved or Decimal("0")
        self.quantity_reserved = max(Decimal("0"), current - quantity)

    def commit(self, quantity: Decimal) -> bool:
        """Compromete quantidade (para ordens)."""
        if quantity > self.quantity_available:
            return False
        self.quantity_committed = (self.quantity_committed or Decimal("0")) + quantity
        return True

    def release_commitment(self, quantity: Decimal) -> None:
        """Libera comprometimento."""
        current = self.quantity_committed or Decimal("0")
        self.quantity_committed = max(Decimal("0"), current - quantity)

    def adjust(self, new_quantity: Decimal, reason: str) -> Decimal:
        """Ajusta quantidade e retorna diferença."""
        current = self.quantity_on_hand or Decimal("0")
        difference = new_quantity - current
        self.quantity_on_hand = new_quantity
        self.total_cost = new_quantity * (self.unit_cost or Decimal("0"))
        self.last_count_date = datetime.utcnow()
        self.last_movement_at = datetime.utcnow()
        self.notes = f"Ajuste: {reason}"
        return difference

    def block(self, reason: str, user_id: uuid.UUID) -> None:
        """Bloqueia o item."""
        self.status = StockItemStatus.BLOQUEADO.value
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = datetime.utcnow()
        self.blocked_by = user_id

    def unblock(self) -> None:
        """Desbloqueia o item."""
        self.status = StockItemStatus.DISPONIVEL.value
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_at = None
        self.blocked_by = None

    def quarantine(self, reason: str, user_id: uuid.UUID) -> None:
        """Coloca em quarentena."""
        self.status = StockItemStatus.QUARENTENA.value
        self.is_blocked = True
        self.blocked_reason = reason
        self.blocked_at = datetime.utcnow()
        self.blocked_by = user_id

    def mark_expired(self) -> None:
        """Marca como vencido."""
        self.status = StockItemStatus.VENCIDO.value

    def mark_damaged(self, reason: str) -> None:
        """Marca como avariado."""
        self.status = StockItemStatus.AVARIADO.value
        self.notes = f"Avaria: {reason}"

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "warehouse_id": str(self.warehouse_id),
            "status": self.status,
            "batch_number": self.batch_number,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "quantity_on_hand": float(self.quantity_on_hand) if self.quantity_on_hand else 0,
            "quantity_reserved": float(self.quantity_reserved) if self.quantity_reserved else 0,
            "quantity_available": float(self.quantity_available),
            "unit_cost": float(self.unit_cost) if self.unit_cost else 0,
            "average_cost": float(self.average_cost) if self.average_cost else 0,
            "total_cost": float(self.total_cost) if self.total_cost else 0,
            "location": self.full_location,
            "is_available": self.is_available,
            "is_low_stock": self.is_low_stock,
            "is_expired": self.is_expired,
            "days_to_expiry": self.days_to_expiry,
            "classification": self.classification,
        }
