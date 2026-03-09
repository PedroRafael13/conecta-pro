"""Model para movimentações de estoque."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.product import Product
    from modules.financial.models.warehouse import Warehouse


class MovementType(StrEnum):
    """Tipo de movimentação."""

    ENTRADA = "entrada"
    SAIDA = "saida"
    TRANSFERENCIA = "transferencia"
    AJUSTE_POSITIVO = "ajuste_positivo"
    AJUSTE_NEGATIVO = "ajuste_negativo"
    DEVOLUCAO_CLIENTE = "devolucao_cliente"
    DEVOLUCAO_FORNECEDOR = "devolucao_fornecedor"
    PRODUCAO = "producao"
    CONSUMO = "consumo"
    PERDA = "perda"
    BONIFICACAO = "bonificacao"


class MovementReason(StrEnum):
    """Motivo da movimentação."""

    # Entradas
    COMPRA = "compra"
    PRODUCAO = "producao"
    DEVOLUCAO = "devolucao"
    BONIFICACAO = "bonificacao"
    AJUSTE_INVENTARIO = "ajuste_inventario"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    CONSIGNACAO = "consignacao"
    AMOSTRA = "amostra"

    # Saídas
    VENDA = "venda"
    CONSUMO_INTERNO = "consumo_interno"
    PERDA = "perda"
    ROUBO = "roubo"
    AVARIA = "avaria"
    VENCIMENTO = "vencimento"
    REQUISICAO = "requisicao"
    TRANSFERENCIA_SAIDA = "transferencia_saida"
    DEVOLUCAO_FORNECEDOR = "devolucao_fornecedor"
    BAIXA = "baixa"

    # Outros
    OUTRO = "outro"


class MovementStatus(StrEnum):
    """Status da movimentação."""

    RASCUNHO = "rascunho"
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    ESTORNADA = "estornada"


class StockMovement(Base):
    """Movimentação de estoque."""

    __tablename__ = "fin_stock_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    number = Column(String(20), nullable=False, index=True)  # MOV-YYYY-NNNN
    movement_type = Column(String(30), nullable=False)
    reason = Column(String(30), nullable=False, default=MovementReason.OUTRO.value)
    status = Column(String(20), nullable=False, default=MovementStatus.RASCUNHO.value)

    # Produto
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    # Armazéns
    warehouse_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_warehouses.id"),
        nullable=False,
        index=True,
    )
    # Para transferências
    destination_warehouse_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_warehouses.id"),
        nullable=True,
        index=True,
    )

    # Datas
    movement_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    confirmed_at = Column(DateTime, nullable=True)

    # Lote
    batch_number = Column(String(50), nullable=True)
    expiry_date = Column(Date, nullable=True)
    serial_number = Column(String(100), nullable=True)

    # Quantidades
    quantity = Column(Numeric(15, 4), nullable=False)
    unit_of_measure = Column(String(10), nullable=False, default="un")

    # Custos
    unit_cost = Column(Numeric(15, 4), default=0)
    total_cost = Column(Numeric(15, 2), default=0)

    # Saldo (antes e depois)
    balance_before = Column(Numeric(15, 4), nullable=True)
    balance_after = Column(Numeric(15, 4), nullable=True)

    # Localização (origem)
    source_location = Column(String(50), nullable=True)
    source_aisle = Column(String(10), nullable=True)
    source_rack = Column(String(10), nullable=True)
    source_shelf = Column(String(10), nullable=True)
    source_bin = Column(String(10), nullable=True)

    # Localização (destino)
    dest_location = Column(String(50), nullable=True)
    dest_aisle = Column(String(10), nullable=True)
    dest_rack = Column(String(10), nullable=True)
    dest_shelf = Column(String(10), nullable=True)
    dest_bin = Column(String(10), nullable=True)

    # Referências (documento de origem)
    reference_type = Column(String(50), nullable=True)  # purchase_order, goods_receipt, etc
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    reference_number = Column(String(50), nullable=True)

    # Nota fiscal
    invoice_number = Column(String(50), nullable=True)
    invoice_series = Column(String(10), nullable=True)
    invoice_key = Column(String(50), nullable=True)

    # Fornecedor/Cliente
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)

    # Requisição interna
    requisition_id = Column(UUID(as_uuid=True), nullable=True)
    requisition_number = Column(String(50), nullable=True)

    # Aprovação
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Estorno
    is_reversal = Column(Boolean, default=False)
    reversal_of = Column(UUID(as_uuid=True), nullable=True)  # Movimento original
    reversed_by = Column(UUID(as_uuid=True), nullable=True)  # Movimento de estorno

    # Observações
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Anexos
    attachments = Column(JSONB, default=list)

    # Metadados
    extra_data = Column(JSONB, default=dict)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    product: "Product" = relationship("Product")
    warehouse: "Warehouse" = relationship(
        "Warehouse",
        foreign_keys=[warehouse_id],
    )
    destination_warehouse: Optional["Warehouse"] = relationship(
        "Warehouse",
        foreign_keys=[destination_warehouse_id],
    )

    __table_args__ = (
        Index("ix_stock_movements_number", "number"),
        Index("ix_stock_movements_type", "movement_type"),
        Index("ix_stock_movements_status", "status"),
        Index("ix_stock_movements_product", "product_id"),
        Index("ix_stock_movements_warehouse", "warehouse_id"),
        Index("ix_stock_movements_date", "movement_date"),
        Index("ix_stock_movements_condominio_date", "condominio_id", "movement_date"),
        Index("ix_stock_movements_reference", "reference_type", "reference_id"),
        Index("ix_stock_movements_batch", "batch_number"),
    )

    def __repr__(self) -> str:
        return f"<StockMovement {self.number}>"

    @property
    def is_entry(self) -> bool:
        """Verifica se é entrada."""
        return self.movement_type in [
            MovementType.ENTRADA.value,
            MovementType.AJUSTE_POSITIVO.value,
            MovementType.DEVOLUCAO_CLIENTE.value,
            MovementType.PRODUCAO.value,
            MovementType.BONIFICACAO.value,
        ]

    @property
    def is_exit(self) -> bool:
        """Verifica se é saída."""
        return self.movement_type in [
            MovementType.SAIDA.value,
            MovementType.AJUSTE_NEGATIVO.value,
            MovementType.DEVOLUCAO_FORNECEDOR.value,
            MovementType.CONSUMO.value,
            MovementType.PERDA.value,
        ]

    @property
    def is_transfer(self) -> bool:
        """Verifica se é transferência."""
        return self.movement_type == MovementType.TRANSFERENCIA.value

    @property
    def is_adjustment(self) -> bool:
        """Verifica se é ajuste."""
        return self.movement_type in [
            MovementType.AJUSTE_POSITIVO.value,
            MovementType.AJUSTE_NEGATIVO.value,
        ]

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == MovementStatus.PENDENTE.value

    @property
    def is_confirmed(self) -> bool:
        """Verifica se está confirmada."""
        return self.status == MovementStatus.CONFIRMADA.value

    @property
    def is_cancelled(self) -> bool:
        """Verifica se está cancelada."""
        return self.status == MovementStatus.CANCELADA.value

    @property
    def can_confirm(self) -> bool:
        """Verifica se pode ser confirmada."""
        if self.requires_approval and not self.approved_by:
            return False
        return self.status in [MovementStatus.RASCUNHO.value, MovementStatus.PENDENTE.value]

    @property
    def can_cancel(self) -> bool:
        """Verifica se pode ser cancelada."""
        return self.status in [
            MovementStatus.RASCUNHO.value,
            MovementStatus.PENDENTE.value,
            MovementStatus.APROVADA.value,
        ]

    @property
    def can_reverse(self) -> bool:
        """Verifica se pode ser estornada."""
        return self.status == MovementStatus.CONFIRMADA.value and not self.is_reversal

    @property
    def source_full_location(self) -> str:
        """Localização de origem completa."""
        parts = []
        if self.source_aisle:
            parts.append(f"C{self.source_aisle}")
        if self.source_rack:
            parts.append(f"P{self.source_rack}")
        if self.source_shelf:
            parts.append(f"N{self.source_shelf}")
        if self.source_bin:
            parts.append(f"B{self.source_bin}")
        return "-".join(parts) if parts else self.source_location or ""

    @property
    def dest_full_location(self) -> str:
        """Localização de destino completa."""
        parts = []
        if self.dest_aisle:
            parts.append(f"C{self.dest_aisle}")
        if self.dest_rack:
            parts.append(f"P{self.dest_rack}")
        if self.dest_shelf:
            parts.append(f"N{self.dest_shelf}")
        if self.dest_bin:
            parts.append(f"B{self.dest_bin}")
        return "-".join(parts) if parts else self.dest_location or ""

    @property
    def signed_quantity(self) -> Decimal:
        """Quantidade com sinal (+ entrada, - saída)."""
        qty = self.quantity or Decimal("0")
        if self.is_exit:
            return -qty
        return qty

    def approve(self, approver_id: uuid.UUID, notes: str | None = None) -> None:
        """Aprova a movimentação."""
        self.status = MovementStatus.APROVADA.value
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes

    def confirm(self, user_id: uuid.UUID, balance_before: Decimal, balance_after: Decimal) -> None:
        """Confirma a movimentação."""
        self.status = MovementStatus.CONFIRMADA.value
        self.confirmed_by = user_id
        self.confirmed_at = datetime.utcnow()
        self.balance_before = balance_before
        self.balance_after = balance_after
        self.total_cost = (self.quantity or Decimal("0")) * (self.unit_cost or Decimal("0"))

    def cancel(self) -> None:
        """Cancela a movimentação."""
        self.status = MovementStatus.CANCELADA.value

    def set_pending(self) -> None:
        """Define como pendente de aprovação."""
        self.status = MovementStatus.PENDENTE.value

    def calculate_total_cost(self) -> None:
        """Calcula custo total."""
        self.total_cost = (self.quantity or Decimal("0")) * (self.unit_cost or Decimal("0"))

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "number": self.number,
            "movement_type": self.movement_type,
            "reason": self.reason,
            "status": self.status,
            "product_id": str(self.product_id),
            "warehouse_id": str(self.warehouse_id),
            "destination_warehouse_id": (str(self.destination_warehouse_id) if self.destination_warehouse_id else None),
            "movement_date": (self.movement_date.isoformat() if self.movement_date else None),
            "batch_number": self.batch_number,
            "quantity": float(self.quantity) if self.quantity else 0,
            "unit_of_measure": self.unit_of_measure,
            "unit_cost": float(self.unit_cost) if self.unit_cost else 0,
            "total_cost": float(self.total_cost) if self.total_cost else 0,
            "balance_before": float(self.balance_before) if self.balance_before else None,
            "balance_after": float(self.balance_after) if self.balance_after else None,
            "source_location": self.source_full_location,
            "dest_location": self.dest_full_location,
            "reference_type": self.reference_type,
            "reference_number": self.reference_number,
            "is_entry": self.is_entry,
            "is_exit": self.is_exit,
            "is_confirmed": self.is_confirmed,
            "description": self.description,
        }
