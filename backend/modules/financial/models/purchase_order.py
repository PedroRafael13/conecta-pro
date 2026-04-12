"""Model para ordens de compra."""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

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
    from modules.financial.models.goods_receipt import GoodsReceipt
    from modules.financial.models.purchase_quotation import PurchaseQuotation


class OrderStatus(StrEnum):
    """Status da ordem de compra."""

    RASCUNHO = "rascunho"
    PENDENTE_APROVACAO = "pendente_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    ENVIADA = "enviada"  # Enviada ao fornecedor
    CONFIRMADA = "confirmada"  # Confirmada pelo fornecedor
    EM_PRODUCAO = "em_producao"
    EM_TRANSITO = "em_transito"
    PARCIALMENTE_RECEBIDA = "parcialmente_recebida"
    RECEBIDA = "recebida"
    FATURADA = "faturada"
    PAGA = "paga"
    CANCELADA = "cancelada"
    DEVOLVIDA = "devolvida"


class OrderPriority(StrEnum):
    """Prioridade da ordem."""

    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class PurchaseOrder(Base):
    """Ordem de compra (pedido ao fornecedor)."""

    __tablename__ = "purchase_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Origem
    quotation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_quotations.id"),
        nullable=True,
        index=True,
    )
    requisition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisitions.id"),
        nullable=True,
        index=True,
    )

    # Fornecedor
    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    number = Column(String(20), nullable=False, index=True)  # PO-YYYY-NNNN
    revision = Column(Integer, default=1)
    status = Column(String(30), nullable=False, default=OrderStatus.RASCUNHO.value)
    priority = Column(String(20), nullable=False, default=OrderPriority.NORMAL.value)

    # Datas
    order_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    approval_date = Column(DateTime, nullable=True)
    sent_date = Column(DateTime, nullable=True)
    confirmed_date = Column(DateTime, nullable=True)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # Condições comerciais
    payment_condition = Column(String(20), nullable=True)
    payment_installments = Column(Integer, nullable=True)
    delivery_type = Column(String(20), nullable=True)  # CIF, FOB, Retirada

    # Valores
    subtotal = Column(Numeric(15, 2), default=0)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    freight_amount = Column(Numeric(15, 2), default=0)
    insurance_amount = Column(Numeric(15, 2), default=0)
    other_costs = Column(Numeric(15, 2), default=0)
    total = Column(Numeric(15, 2), default=0)

    # Impostos
    ipi_amount = Column(Numeric(15, 2), default=0)
    icms_amount = Column(Numeric(15, 2), default=0)
    icms_st_amount = Column(Numeric(15, 2), default=0)
    pis_amount = Column(Numeric(15, 2), default=0)
    cofins_amount = Column(Numeric(15, 2), default=0)

    # Valores realizados
    received_total = Column(Numeric(15, 2), default=0)  # Total recebido
    invoiced_total = Column(Numeric(15, 2), default=0)  # Total faturado
    paid_total = Column(Numeric(15, 2), default=0)  # Total pago

    # Entrega
    delivery_address = Column(Text, nullable=True)
    delivery_contact = Column(String(100), nullable=True)
    delivery_phone = Column(String(20), nullable=True)
    delivery_instructions = Column(Text, nullable=True)

    # Faturamento
    billing_address = Column(Text, nullable=True)
    billing_contact = Column(String(100), nullable=True)

    # Aprovação
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Rejeição
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Cancelamento
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Observações
    notes = Column(Text, nullable=True)
    supplier_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Anexos
    attachments = Column(JSONB, default=list)

    # Histórico de status
    status_history = Column(JSONB, default=list)
    # [{status, timestamp, user_id, notes}]

    # Vinculo com Contas a Pagar
    payable_account_id = Column(UUID(as_uuid=True), ForeignKey("payable_accounts.id"), nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    quotation: Optional["PurchaseQuotation"] = relationship("PurchaseQuotation", back_populates="orders")
    items: list["PurchaseOrderItem"] = relationship(
        "PurchaseOrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    receipts: list["GoodsReceipt"] = relationship("GoodsReceipt", back_populates="order")

    __table_args__ = (
        Index("ix_purchase_orders_number", "number"),
        Index("ix_purchase_orders_status", "status"),
        Index("ix_purchase_orders_supplier", "supplier_id"),
        Index("ix_purchase_orders_condominio_status", "condominio_id", "status"),
        Index("ix_purchase_orders_date", "order_date"),
    )

    def __repr__(self) -> str:
        return f"<PurchaseOrder {self.number}>"

    @property
    def is_draft(self) -> bool:
        """Verifica se está em rascunho."""
        return self.status == OrderStatus.RASCUNHO.value

    @property
    def is_pending_approval(self) -> bool:
        """Verifica se aguarda aprovação."""
        return self.status == OrderStatus.PENDENTE_APROVACAO.value

    @property
    def is_approved(self) -> bool:
        """Verifica se está aprovada."""
        return self.status not in [
            OrderStatus.RASCUNHO.value,
            OrderStatus.PENDENTE_APROVACAO.value,
            OrderStatus.REJEITADA.value,
            OrderStatus.CANCELADA.value,
        ]

    @property
    def is_sent(self) -> bool:
        """Verifica se foi enviada."""
        return self.status not in [
            OrderStatus.RASCUNHO.value,
            OrderStatus.PENDENTE_APROVACAO.value,
            OrderStatus.APROVADA.value,
            OrderStatus.REJEITADA.value,
            OrderStatus.CANCELADA.value,
        ]

    @property
    def is_closed(self) -> bool:
        """Verifica se está finalizada."""
        return self.status in [
            OrderStatus.RECEBIDA.value,
            OrderStatus.FATURADA.value,
            OrderStatus.PAGA.value,
            OrderStatus.CANCELADA.value,
            OrderStatus.DEVOLVIDA.value,
        ]

    @property
    def is_cancelled(self) -> bool:
        """Verifica se está cancelada."""
        return self.status == OrderStatus.CANCELADA.value

    @property
    def items_count(self) -> int:
        """Retorna quantidade de itens."""
        return len(self.items) if self.items else 0

    @property
    def receipts_count(self) -> int:
        """Retorna quantidade de recebimentos."""
        return len(self.receipts) if self.receipts else 0

    @property
    def pending_amount(self) -> Decimal:
        """Valor pendente de recebimento."""
        return self.total - (self.received_total or Decimal("0"))

    @property
    def pending_payment(self) -> Decimal:
        """Valor pendente de pagamento."""
        return (self.invoiced_total or Decimal("0")) - (self.paid_total or Decimal("0"))

    @property
    def is_fully_received(self) -> bool:
        """Verifica se foi totalmente recebida."""
        return self.received_total >= self.total

    @property
    def is_fully_paid(self) -> bool:
        """Verifica se foi totalmente paga."""
        return self.paid_total >= self.invoiced_total if self.invoiced_total else False

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if self.expected_delivery_date and not self.is_closed:
            return datetime.utcnow().date() > self.expected_delivery_date
        return False

    def submit_for_approval(self) -> None:
        """Submete para aprovação."""
        if self.status != OrderStatus.RASCUNHO.value:
            raise ValueError("Apenas ordens em rascunho podem ser submetidas")
        if not self.items:
            raise ValueError("Ordem deve ter pelo menos um item")
        self._change_status(OrderStatus.PENDENTE_APROVACAO.value)

    def approve(self, approver_id: uuid.UUID, notes: str | None = None) -> None:
        """Aprova a ordem."""
        if self.status != OrderStatus.PENDENTE_APROVACAO.value:
            raise ValueError("Apenas ordens pendentes podem ser aprovadas")
        self._change_status(OrderStatus.APROVADA.value)
        self.approval_date = datetime.utcnow()
        self.approved_by = approver_id
        self.approval_notes = notes

    def reject(self, rejector_id: uuid.UUID, reason: str) -> None:
        """Rejeita a ordem."""
        if self.status != OrderStatus.PENDENTE_APROVACAO.value:
            raise ValueError("Apenas ordens pendentes podem ser rejeitadas")
        self._change_status(OrderStatus.REJEITADA.value)
        self.rejection_reason = reason
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejector_id

    def send_to_supplier(self) -> None:
        """Envia ao fornecedor."""
        if self.status != OrderStatus.APROVADA.value:
            raise ValueError("Apenas ordens aprovadas podem ser enviadas")
        self._change_status(OrderStatus.ENVIADA.value)
        self.sent_date = datetime.utcnow()

    def confirm_by_supplier(self) -> None:
        """Confirmação pelo fornecedor."""
        if self.status != OrderStatus.ENVIADA.value:
            raise ValueError("Apenas ordens enviadas podem ser confirmadas")
        self._change_status(OrderStatus.CONFIRMADA.value)
        self.confirmed_date = datetime.utcnow()

    def mark_in_production(self) -> None:
        """Marca como em produção."""
        self._change_status(OrderStatus.EM_PRODUCAO.value)

    def mark_in_transit(self) -> None:
        """Marca como em trânsito."""
        self._change_status(OrderStatus.EM_TRANSITO.value)

    def mark_partially_received(self, amount: Decimal) -> None:
        """Marca como parcialmente recebida."""
        self.received_total = (self.received_total or Decimal("0")) + amount
        self._change_status(OrderStatus.PARCIALMENTE_RECEBIDA.value)

    def mark_received(self) -> None:
        """Marca como totalmente recebida."""
        self.received_total = self.total
        self.actual_delivery_date = datetime.utcnow().date()
        self._change_status(OrderStatus.RECEBIDA.value)

    def mark_invoiced(self, invoice_total: Decimal) -> None:
        """Marca como faturada."""
        self.invoiced_total = invoice_total
        self._change_status(OrderStatus.FATURADA.value)

    def mark_paid(self, paid_amount: Decimal) -> None:
        """Registra pagamento."""
        self.paid_total = (self.paid_total or Decimal("0")) + paid_amount
        if self.is_fully_paid:
            self._change_status(OrderStatus.PAGA.value)

    def cancel(self, user_id: uuid.UUID, reason: str) -> None:
        """Cancela a ordem."""
        if self.is_closed:
            raise ValueError("Ordem já finalizada não pode ser cancelada")
        self._change_status(OrderStatus.CANCELADA.value)
        self.cancellation_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = user_id

    def calculate_total(self) -> Decimal:
        """Calcula total da ordem."""
        subtotal = Decimal("0")
        if self.items:
            for item in self.items:
                if item.total:
                    subtotal += item.total

        self.subtotal = subtotal
        self.total = (
            subtotal
            - (self.discount_amount or Decimal("0"))
            + (self.freight_amount or Decimal("0"))
            + (self.insurance_amount or Decimal("0"))
            + (self.other_costs or Decimal("0"))
        )
        return self.total

    def _change_status(self, new_status: str, notes: str | None = None) -> None:
        """Muda status e registra no histórico."""
        old_status = self.status
        self.status = new_status
        if not self.status_history:
            self.status_history = []
        self.status_history.append(
            {
                "from": old_status,
                "to": new_status,
                "timestamp": datetime.utcnow().isoformat(),
                "notes": notes,
            }
        )

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "number": self.number,
            "status": self.status,
            "priority": self.priority,
            "supplier_id": str(self.supplier_id),
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "expected_delivery_date": (
                self.expected_delivery_date.isoformat() if self.expected_delivery_date else None
            ),
            "subtotal": float(self.subtotal) if self.subtotal else 0,
            "total": float(self.total) if self.total else 0,
            "received_total": float(self.received_total) if self.received_total else 0,
            "payment_condition": self.payment_condition,
            "items_count": self.items_count,
            "is_approved": self.is_approved,
            "is_overdue": self.is_overdue,
        }


class PurchaseOrderItem(Base):
    """Item da ordem de compra."""

    __tablename__ = "purchase_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Item de origem
    quotation_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_quotation_items.id"),
        nullable=True,
    )
    requisition_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisition_items.id"),
        nullable=True,
    )

    # Produto
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)

    # Identificação
    item_number = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    supplier_code = Column(String(50), nullable=True)
    unit_of_measure = Column(String(10), nullable=False, default="un")

    # Quantidade
    quantity_ordered = Column(Numeric(10, 2), nullable=False)
    quantity_received = Column(Numeric(10, 2), default=0)
    quantity_invoiced = Column(Numeric(10, 2), default=0)
    quantity_returned = Column(Numeric(10, 2), default=0)

    # Preços
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    total = Column(Numeric(15, 2), nullable=False)

    # Impostos
    ipi_percentage = Column(Numeric(5, 2), default=0)
    ipi_amount = Column(Numeric(15, 2), default=0)
    icms_percentage = Column(Numeric(5, 2), default=0)
    icms_amount = Column(Numeric(15, 2), default=0)

    # Entrega
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    order: "PurchaseOrder" = relationship("PurchaseOrder", back_populates="items")

    __table_args__ = (
        Index("ix_purchase_order_items_order", "order_id"),
        Index("ix_purchase_order_items_product", "product_id"),
    )

    def __repr__(self) -> str:
        return f"<PurchaseOrderItem {self.item_number}: {self.description[:30]}>"

    @property
    def is_fully_received(self) -> bool:
        """Verifica se foi totalmente recebido."""
        return self.quantity_received >= self.quantity_ordered

    @property
    def pending_quantity(self) -> Decimal:
        """Quantidade pendente de recebimento."""
        return max(Decimal("0"), self.quantity_ordered - self.quantity_received)

    @property
    def returned_quantity(self) -> Decimal:
        """Quantidade devolvida."""
        return self.quantity_returned or Decimal("0")

    def receive(self, quantity: Decimal) -> None:
        """Registra recebimento."""
        self.quantity_received = (self.quantity_received or Decimal("0")) + quantity
        if self.quantity_received >= self.quantity_ordered:
            self.actual_delivery_date = datetime.utcnow().date()

    def return_items(self, quantity: Decimal) -> None:
        """Registra devolução."""
        self.quantity_returned = (self.quantity_returned or Decimal("0")) + quantity
        self.quantity_received = max(Decimal("0"), (self.quantity_received or Decimal("0")) - quantity)

    def calculate_total(self) -> None:
        """Calcula total do item."""
        if self.quantity_ordered and self.unit_price:
            subtotal = self.quantity_ordered * self.unit_price
            if self.discount_percentage:
                self.discount_amount = subtotal * (self.discount_percentage / 100)
            self.total = subtotal - (self.discount_amount or Decimal("0"))

            # Impostos
            if self.ipi_percentage:
                self.ipi_amount = self.total * (self.ipi_percentage / 100)
            if self.icms_percentage:
                self.icms_amount = self.total * (self.icms_percentage / 100)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "item_number": self.item_number,
            "description": self.description,
            "supplier_code": self.supplier_code,
            "unit_of_measure": self.unit_of_measure,
            "quantity_ordered": float(self.quantity_ordered),
            "quantity_received": float(self.quantity_received) if self.quantity_received else 0,
            "unit_price": float(self.unit_price),
            "total": float(self.total),
            "pending_quantity": float(self.pending_quantity),
            "is_fully_received": self.is_fully_received,
        }
