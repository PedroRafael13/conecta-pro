"""Model para inventário/contagem de estoque."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.warehouse import Warehouse


class InventoryType(StrEnum):
    """Tipo de inventário."""

    GERAL = "geral"  # Todos os itens
    ROTATIVO = "rotativo"  # Por amostragem/ciclo
    PARCIAL = "parcial"  # Apenas alguns itens
    ABC = "abc"  # Baseado em classificação ABC
    CATEGORIA = "categoria"  # Por categoria
    LOCALIZACAO = "localizacao"  # Por local


class InventoryStatus(StrEnum):
    """Status do inventário."""

    PLANEJADO = "planejado"
    EM_ANDAMENTO = "em_andamento"
    CONTAGEM = "contagem"
    RECONFERENCIA = "reconferencia"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADO = "aprovado"
    AJUSTADO = "ajustado"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class InventoryItemStatus(StrEnum):
    """Status do item do inventário."""

    PENDENTE = "pendente"
    CONTADO = "contado"
    CONFERIDO = "conferido"
    DIVERGENTE = "divergente"
    APROVADO = "aprovado"
    AJUSTADO = "ajustado"


class StockInventory(Base):
    """Inventário/Contagem de estoque."""

    __tablename__ = "fin_stock_inventories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominiums.id"),
        nullable=False,
        index=True,
    )

    # Armazém
    warehouse_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_warehouses.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    number = Column(String(20), nullable=False, index=True)  # INV-YYYY-NNNN
    description = Column(String(200), nullable=True)
    inventory_type = Column(String(20), nullable=False, default=InventoryType.GERAL.value)
    status = Column(String(20), nullable=False, default=InventoryStatus.PLANEJADO.value)

    # Datas
    planned_date = Column(Date, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)

    # Filtros aplicados
    filter_categories = Column(JSONB, default=list)  # IDs de categorias
    filter_locations = Column(JSONB, default=list)  # Códigos de localização
    filter_abc_class = Column(JSONB, default=list)  # ["A", "B", "C"]
    filter_products = Column(JSONB, default=list)  # IDs de produtos específicos

    # Estatísticas
    total_items = Column(Integer, default=0)  # Total de itens a contar
    counted_items = Column(Integer, default=0)  # Itens contados
    verified_items = Column(Integer, default=0)  # Itens verificados
    divergent_items = Column(Integer, default=0)  # Itens com divergência
    adjusted_items = Column(Integer, default=0)  # Itens ajustados

    # Valores
    expected_value = Column(Numeric(15, 2), default=0)  # Valor esperado
    counted_value = Column(Numeric(15, 2), default=0)  # Valor contado
    difference_value = Column(Numeric(15, 2), default=0)  # Diferença em valor
    adjustment_value = Column(Numeric(15, 2), default=0)  # Valor ajustado

    # Quantidades
    expected_quantity = Column(Numeric(15, 4), default=0)
    counted_quantity = Column(Numeric(15, 4), default=0)
    difference_quantity = Column(Numeric(15, 4), default=0)

    # Acuracidade
    accuracy_rate = Column(Numeric(5, 2), nullable=True)  # Taxa de acuracidade (%)
    hit_rate = Column(Numeric(5, 2), nullable=True)  # Taxa de acerto (%)

    # Responsáveis
    supervisor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    team_members = Column(JSONB, default=list)  # IDs dos membros da equipe

    # Aprovação
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Configurações
    allow_recount = Column(Boolean, default=True)  # Permite recontagem
    require_double_count = Column(Boolean, default=False)  # Exige contagem dupla
    blind_count = Column(Boolean, default=False)  # Contagem cega (não mostra saldo)
    auto_adjust = Column(Boolean, default=False)  # Ajuste automático

    # Observações
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Anexos
    attachments = Column(JSONB, default=list)

    # Metadados
    extra_data = Column(JSONB, default=dict)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    warehouse: "Warehouse" = relationship("Warehouse")
    items: list["StockInventoryItem"] = relationship(
        "StockInventoryItem",
        back_populates="inventory",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_stock_inventories_number", "number"),
        Index("ix_stock_inventories_status", "status"),
        Index("ix_stock_inventories_warehouse", "warehouse_id"),
        Index("ix_stock_inventories_date", "planned_date"),
        Index("ix_stock_inventories_condominio", "condominio_id"),
    )

    def __repr__(self) -> str:
        return f"<StockInventory {self.number}>"

    @property
    def is_in_progress(self) -> bool:
        """Verifica se está em andamento."""
        return self.status in [
            InventoryStatus.EM_ANDAMENTO.value,
            InventoryStatus.CONTAGEM.value,
            InventoryStatus.RECONFERENCIA.value,
        ]

    @property
    def is_finalized(self) -> bool:
        """Verifica se está finalizado."""
        return self.status == InventoryStatus.FINALIZADO.value

    @property
    def is_cancelled(self) -> bool:
        """Verifica se está cancelado."""
        return self.status == InventoryStatus.CANCELADO.value

    @property
    def progress_percentage(self) -> Decimal:
        """Percentual de progresso."""
        if self.total_items and self.total_items > 0:
            return Decimal(self.counted_items / self.total_items * 100).quantize(Decimal("0.01"))
        return Decimal("0")

    @property
    def has_divergences(self) -> bool:
        """Verifica se há divergências."""
        return self.divergent_items > 0

    @property
    def can_start(self) -> bool:
        """Verifica se pode iniciar."""
        return self.status == InventoryStatus.PLANEJADO.value

    @property
    def can_finish(self) -> bool:
        """Verifica se pode finalizar."""
        return self.status == InventoryStatus.APROVADO.value or (
            not self.requires_approval and self.status == InventoryStatus.AJUSTADO.value
        )

    def start(self) -> None:
        """Inicia o inventário."""
        self.status = InventoryStatus.EM_ANDAMENTO.value
        self.start_date = datetime.utcnow()

    def start_counting(self) -> None:
        """Inicia fase de contagem."""
        self.status = InventoryStatus.CONTAGEM.value

    def start_recount(self) -> None:
        """Inicia reconferência."""
        self.status = InventoryStatus.RECONFERENCIA.value

    def submit_for_approval(self) -> None:
        """Submete para aprovação."""
        self.status = InventoryStatus.AGUARDANDO_APROVACAO.value

    def approve(self, approver_id: uuid.UUID, notes: str | None = None) -> None:
        """Aprova o inventário."""
        self.status = InventoryStatus.APROVADO.value
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes

    def mark_adjusted(self) -> None:
        """Marca como ajustado."""
        self.status = InventoryStatus.AJUSTADO.value

    def finalize(self) -> None:
        """Finaliza o inventário."""
        self.status = InventoryStatus.FINALIZADO.value
        self.end_date = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela o inventário."""
        self.status = InventoryStatus.CANCELADO.value

    def calculate_accuracy(self) -> None:
        """Calcula taxa de acuracidade."""
        if self.total_items and self.total_items > 0:
            correct = self.total_items - self.divergent_items
            self.accuracy_rate = Decimal(correct / self.total_items * 100).quantize(Decimal("0.01"))
            self.hit_rate = self.accuracy_rate

    def update_statistics(self) -> None:
        """Atualiza estatísticas do inventário."""
        if self.items:
            self.total_items = len(self.items)
            self.counted_items = len([i for i in self.items if i.is_counted])
            self.verified_items = len([i for i in self.items if i.is_verified])
            self.divergent_items = len([i for i in self.items if i.has_divergence])
            self.adjusted_items = len([i for i in self.items if i.is_adjusted])

            # Valores
            self.expected_value = sum(i.expected_value or Decimal("0") for i in self.items)
            self.counted_value = sum(i.counted_value or Decimal("0") for i in self.items)
            self.difference_value = self.counted_value - self.expected_value

            # Quantidades
            self.expected_quantity = sum(i.expected_quantity or Decimal("0") for i in self.items)
            self.counted_quantity = sum(i.counted_quantity or Decimal("0") for i in self.items)
            self.difference_quantity = self.counted_quantity - self.expected_quantity

            self.calculate_accuracy()

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "number": self.number,
            "description": self.description,
            "inventory_type": self.inventory_type,
            "status": self.status,
            "warehouse_id": str(self.warehouse_id),
            "planned_date": self.planned_date.isoformat() if self.planned_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "total_items": self.total_items,
            "counted_items": self.counted_items,
            "divergent_items": self.divergent_items,
            "progress_percentage": float(self.progress_percentage),
            "accuracy_rate": float(self.accuracy_rate) if self.accuracy_rate else None,
            "expected_value": float(self.expected_value) if self.expected_value else 0,
            "counted_value": float(self.counted_value) if self.counted_value else 0,
            "difference_value": float(self.difference_value) if self.difference_value else 0,
            "has_divergences": self.has_divergences,
            "is_in_progress": self.is_in_progress,
            "is_finalized": self.is_finalized,
        }


class StockInventoryItem(Base):
    """Item do inventário."""

    __tablename__ = "fin_stock_inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_stock_inventories.id", ondelete="CASCADE"),
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

    # Stock Item
    stock_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_stock_items.id"),
        nullable=True,
        index=True,
    )

    # Status
    status = Column(String(20), nullable=False, default=InventoryItemStatus.PENDENTE.value)

    # Lote
    batch_number = Column(String(50), nullable=True)
    expiry_date = Column(Date, nullable=True)

    # Localização
    location_code = Column(String(50), nullable=True)
    aisle = Column(String(10), nullable=True)
    rack = Column(String(10), nullable=True)
    shelf = Column(String(10), nullable=True)
    bin_loc = Column(String(10), nullable=True)

    # Quantidades
    expected_quantity = Column(Numeric(15, 4), default=0)  # Quantidade no sistema
    counted_quantity = Column(Numeric(15, 4), nullable=True)  # Quantidade contada
    recount_quantity = Column(Numeric(15, 4), nullable=True)  # Segunda contagem
    difference_quantity = Column(Numeric(15, 4), nullable=True)  # Diferença
    adjusted_quantity = Column(Numeric(15, 4), nullable=True)  # Quantidade após ajuste

    # Custos
    unit_cost = Column(Numeric(15, 4), default=0)
    expected_value = Column(Numeric(15, 2), default=0)
    counted_value = Column(Numeric(15, 2), nullable=True)
    difference_value = Column(Numeric(15, 2), nullable=True)

    # Contagem
    counted_at = Column(DateTime, nullable=True)
    counted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Segunda contagem
    recounted_at = Column(DateTime, nullable=True)
    recounted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Verificação
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Ajuste
    adjustment_reason = Column(Text, nullable=True)
    adjustment_movement_id = Column(UUID(as_uuid=True), nullable=True)
    adjusted_at = Column(DateTime, nullable=True)
    adjusted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    inventory: "StockInventory" = relationship("StockInventory", back_populates="items")

    __table_args__ = (
        Index("ix_stock_inventory_items_inventory", "inventory_id"),
        Index("ix_stock_inventory_items_product", "product_id"),
        Index("ix_stock_inventory_items_status", "status"),
        Index("ix_stock_inventory_items_location", "location_code"),
    )

    def __repr__(self) -> str:
        return f"<StockInventoryItem {self.product_id}>"

    @property
    def is_counted(self) -> bool:
        """Verifica se foi contado."""
        return self.counted_quantity is not None

    @property
    def is_recounted(self) -> bool:
        """Verifica se foi recontado."""
        return self.recount_quantity is not None

    @property
    def is_verified(self) -> bool:
        """Verifica se foi verificado."""
        return self.verified_at is not None

    @property
    def is_adjusted(self) -> bool:
        """Verifica se foi ajustado."""
        return self.adjusted_quantity is not None

    @property
    def has_divergence(self) -> bool:
        """Verifica se há divergência."""
        if self.counted_quantity is not None:
            return self.counted_quantity != self.expected_quantity
        return False

    @property
    def divergence_percentage(self) -> Decimal | None:
        """Percentual de divergência."""
        if self.expected_quantity and self.expected_quantity > 0 and self.difference_quantity:
            return abs(self.difference_quantity / self.expected_quantity * 100)
        return None

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
        if self.bin_loc:
            parts.append(f"B{self.bin_loc}")
        return "-".join(parts) if parts else self.location_code or ""

    def count(self, quantity: Decimal, user_id: uuid.UUID) -> None:
        """Registra contagem."""
        self.counted_quantity = quantity
        self.counted_at = datetime.utcnow()
        self.counted_by = user_id
        self.status = InventoryItemStatus.CONTADO.value
        self._calculate_difference()

    def recount(self, quantity: Decimal, user_id: uuid.UUID) -> None:
        """Registra recontagem."""
        self.recount_quantity = quantity
        self.recounted_at = datetime.utcnow()
        self.recounted_by = user_id
        # Usa recontagem como quantidade final
        self.counted_quantity = quantity
        self._calculate_difference()

    def verify(self, user_id: uuid.UUID) -> None:
        """Verifica o item."""
        self.verified_at = datetime.utcnow()
        self.verified_by = user_id
        self.status = InventoryItemStatus.CONFERIDO.value

    def adjust(
        self,
        quantity: Decimal,
        reason: str,
        movement_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """Registra ajuste."""
        self.adjusted_quantity = quantity
        self.adjustment_reason = reason
        self.adjustment_movement_id = movement_id
        self.adjusted_at = datetime.utcnow()
        self.adjusted_by = user_id
        self.status = InventoryItemStatus.AJUSTADO.value

    def _calculate_difference(self) -> None:
        """Calcula diferença."""
        if self.counted_quantity is not None:
            self.difference_quantity = self.counted_quantity - (self.expected_quantity or Decimal("0"))
            self.counted_value = self.counted_quantity * (self.unit_cost or Decimal("0"))
            self.difference_value = self.counted_value - (self.expected_value or Decimal("0"))

            if self.difference_quantity != 0:
                self.status = InventoryItemStatus.DIVERGENTE.value
            else:
                self.status = InventoryItemStatus.APROVADO.value

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "status": self.status,
            "batch_number": self.batch_number,
            "location": self.full_location,
            "expected_quantity": float(self.expected_quantity) if self.expected_quantity else 0,
            "counted_quantity": (float(self.counted_quantity) if self.counted_quantity is not None else None),
            "difference_quantity": (float(self.difference_quantity) if self.difference_quantity is not None else None),
            "unit_cost": float(self.unit_cost) if self.unit_cost else 0,
            "expected_value": float(self.expected_value) if self.expected_value else 0,
            "counted_value": (float(self.counted_value) if self.counted_value is not None else None),
            "has_divergence": self.has_divergence,
            "divergence_percentage": (float(self.divergence_percentage) if self.divergence_percentage else None),
            "is_counted": self.is_counted,
            "is_verified": self.is_verified,
            "is_adjusted": self.is_adjusted,
        }
