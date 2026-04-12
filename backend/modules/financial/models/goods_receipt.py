"""Model para recebimento de mercadorias."""

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
    from modules.financial.models.purchase_order import PurchaseOrder


class ReceiptStatus(StrEnum):
    """Status do recebimento."""

    PENDENTE = "pendente"
    EM_CONFERENCIA = "em_conferencia"
    CONFERIDO = "conferido"
    APROVADO = "aprovado"
    COM_DIVERGENCIA = "com_divergencia"
    PARCIAL = "parcial"
    RECUSADO = "recusado"
    DEVOLVIDO = "devolvido"
    FINALIZADO = "finalizado"


class ReceiptType(StrEnum):
    """Tipo de recebimento."""

    NORMAL = "normal"
    DEVOLUCAO = "devolucao"
    TRANSFERENCIA = "transferencia"
    BONIFICACAO = "bonificacao"
    AMOSTRA = "amostra"
    CONSIGNACAO = "consignacao"


class InspectionResult(StrEnum):
    """Resultado da inspeção."""

    APROVADO = "aprovado"
    APROVADO_COM_RESSALVA = "aprovado_com_ressalva"
    REPROVADO = "reprovado"
    PENDENTE = "pendente"


class GoodsReceipt(Base):
    """Recebimento de mercadorias."""

    __tablename__ = "goods_receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominiums.id"),
        nullable=False,
        index=True,
    )

    # Ordem de compra
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_orders.id"),
        nullable=False,
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
    number = Column(String(20), nullable=False, index=True)  # REC-YYYY-NNNN
    receipt_type = Column(String(20), nullable=False, default=ReceiptType.NORMAL.value)
    status = Column(String(20), nullable=False, default=ReceiptStatus.PENDENTE.value)

    # Datas
    receipt_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    expected_date = Column(Date, nullable=True)  # Data esperada
    inspection_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)

    # Nota fiscal
    invoice_number = Column(String(50), nullable=True)
    invoice_series = Column(String(10), nullable=True)
    invoice_date = Column(Date, nullable=True)
    invoice_key = Column(String(50), nullable=True)  # Chave da NF-e
    invoice_total = Column(Numeric(15, 2), nullable=True)

    # Valores
    total_expected = Column(Numeric(15, 2), default=0)  # Total esperado
    total_received = Column(Numeric(15, 2), default=0)  # Total recebido
    total_accepted = Column(Numeric(15, 2), default=0)  # Total aceito
    total_rejected = Column(Numeric(15, 2), default=0)  # Total rejeitado
    total_difference = Column(Numeric(15, 2), default=0)  # Diferença

    # Transporte
    carrier = Column(String(200), nullable=True)  # Transportadora
    carrier_cnpj = Column(String(18), nullable=True)
    vehicle_plate = Column(String(10), nullable=True)
    driver_name = Column(String(100), nullable=True)
    driver_document = Column(String(20), nullable=True)
    seal_number = Column(String(50), nullable=True)  # Número do lacre
    volumes = Column(Integer, nullable=True)  # Quantidade de volumes
    gross_weight = Column(Numeric(10, 2), nullable=True)  # Peso bruto
    net_weight = Column(Numeric(10, 2), nullable=True)  # Peso líquido

    # Inspeção
    inspection_result = Column(String(30), nullable=True)
    inspection_notes = Column(Text, nullable=True)
    inspected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Divergências
    has_divergence = Column(Boolean, default=False)
    divergence_type = Column(String(50), nullable=True)  # quantidade, qualidade, preco, etc
    divergence_description = Column(Text, nullable=True)
    divergence_action = Column(String(50), nullable=True)  # aceitar, devolver, negociar

    # Aprovação
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Recusa
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Local de armazenamento
    storage_location = Column(String(100), nullable=True)
    storage_notes = Column(Text, nullable=True)

    # Observações
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Fotos/Anexos
    attachments = Column(JSONB, default=list)
    # [{type: "foto_entrega", url: "...", timestamp: "..."}]

    # Assinatura do recebedor
    receiver_name = Column(String(100), nullable=True)
    receiver_document = Column(String(20), nullable=True)
    receiver_signature = Column(Text, nullable=True)  # Base64 ou URL
    received_at = Column(DateTime, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    order: "PurchaseOrder" = relationship("PurchaseOrder", back_populates="receipts")
    items: list["GoodsReceiptItem"] = relationship(
        "GoodsReceiptItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_goods_receipts_number", "number"),
        Index("ix_goods_receipts_status", "status"),
        Index("ix_goods_receipts_order", "order_id"),
        Index("ix_goods_receipts_supplier", "supplier_id"),
        Index("ix_goods_receipts_condominio_status", "condominio_id", "status"),
        Index("ix_goods_receipts_date", "receipt_date"),
        Index("ix_goods_receipts_invoice", "invoice_number"),
    )

    def __repr__(self) -> str:
        return f"<GoodsReceipt {self.number}>"

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == ReceiptStatus.PENDENTE.value

    @property
    def is_inspecting(self) -> bool:
        """Verifica se está em conferência."""
        return self.status == ReceiptStatus.EM_CONFERENCIA.value

    @property
    def is_approved(self) -> bool:
        """Verifica se foi aprovado."""
        return self.status in [
            ReceiptStatus.APROVADO.value,
            ReceiptStatus.FINALIZADO.value,
        ]

    @property
    def is_finalized(self) -> bool:
        """Verifica se está finalizado."""
        return self.status == ReceiptStatus.FINALIZADO.value

    @property
    def items_count(self) -> int:
        """Retorna quantidade de itens."""
        return len(self.items) if self.items else 0

    @property
    def acceptance_rate(self) -> Decimal | None:
        """Taxa de aceitação (%)."""
        if self.total_received and self.total_received > 0:
            return (self.total_accepted / self.total_received) * 100
        return None

    @property
    def has_invoice(self) -> bool:
        """Verifica se tem nota fiscal."""
        return bool(self.invoice_number)

    def start_inspection(self, inspector_id: uuid.UUID) -> None:
        """Inicia conferência."""
        self.status = ReceiptStatus.EM_CONFERENCIA.value
        self.inspected_by = inspector_id
        self.inspection_date = datetime.utcnow()

    def complete_inspection(self, result: str, notes: str | None = None) -> None:
        """Conclui conferência."""
        self.status = ReceiptStatus.CONFERIDO.value
        self.inspection_result = result
        self.inspection_notes = notes

    def approve(self, approver_id: uuid.UUID, notes: str | None = None) -> None:
        """Aprova o recebimento."""
        self.status = ReceiptStatus.APROVADO.value
        self.approved_by = approver_id
        self.approval_date = datetime.utcnow()
        self.approval_notes = notes

    def reject(self, rejector_id: uuid.UUID, reason: str) -> None:
        """Recusa o recebimento."""
        self.status = ReceiptStatus.RECUSADO.value
        self.rejection_reason = reason
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejector_id

    def mark_with_divergence(
        self,
        divergence_type: str,
        description: str,
        action: str | None = None,
    ) -> None:
        """Marca com divergência."""
        self.status = ReceiptStatus.COM_DIVERGENCIA.value
        self.has_divergence = True
        self.divergence_type = divergence_type
        self.divergence_description = description
        self.divergence_action = action

    def mark_partial(self) -> None:
        """Marca como recebimento parcial."""
        self.status = ReceiptStatus.PARCIAL.value

    def finalize(self) -> None:
        """Finaliza o recebimento."""
        self.status = ReceiptStatus.FINALIZADO.value

    def mark_returned(self) -> None:
        """Marca como devolvido."""
        self.status = ReceiptStatus.DEVOLVIDO.value

    def sign_receipt(
        self,
        receiver_name: str,
        receiver_document: str,
        signature: str | None = None,
    ) -> None:
        """Registra assinatura do recebimento."""
        self.receiver_name = receiver_name
        self.receiver_document = receiver_document
        self.receiver_signature = signature
        self.received_at = datetime.utcnow()

    def calculate_totals(self) -> None:
        """Calcula totais do recebimento."""
        expected = Decimal("0")
        received = Decimal("0")
        accepted = Decimal("0")
        rejected = Decimal("0")

        if self.items:
            for item in self.items:
                if item.expected_total:
                    expected += item.expected_total
                if item.received_total:
                    received += item.received_total
                if item.accepted_total:
                    accepted += item.accepted_total
                if item.rejected_total:
                    rejected += item.rejected_total

        self.total_expected = expected
        self.total_received = received
        self.total_accepted = accepted
        self.total_rejected = rejected
        self.total_difference = received - expected

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "number": self.number,
            "receipt_type": self.receipt_type,
            "status": self.status,
            "order_id": str(self.order_id),
            "supplier_id": str(self.supplier_id),
            "receipt_date": self.receipt_date.isoformat() if self.receipt_date else None,
            "invoice_number": self.invoice_number,
            "invoice_total": float(self.invoice_total) if self.invoice_total else None,
            "total_expected": float(self.total_expected) if self.total_expected else 0,
            "total_received": float(self.total_received) if self.total_received else 0,
            "total_accepted": float(self.total_accepted) if self.total_accepted else 0,
            "has_divergence": self.has_divergence,
            "inspection_result": self.inspection_result,
            "items_count": self.items_count,
            "is_approved": self.is_approved,
        }


class GoodsReceiptItem(Base):
    """Item do recebimento de mercadorias."""

    __tablename__ = "goods_receipt_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("goods_receipts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Item da ordem de compra
    order_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_order_items.id"),
        nullable=True,
        index=True,
    )

    # Produto
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)

    # Identificação
    item_number = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    unit_of_measure = Column(String(10), nullable=False, default="un")

    # Quantidades
    quantity_expected = Column(Numeric(10, 2), nullable=False)  # Esperado
    quantity_received = Column(Numeric(10, 2), default=0)  # Recebido
    quantity_accepted = Column(Numeric(10, 2), default=0)  # Aceito
    quantity_rejected = Column(Numeric(10, 2), default=0)  # Rejeitado
    quantity_difference = Column(Numeric(10, 2), default=0)  # Diferença

    # Preços
    unit_price = Column(Numeric(15, 2), nullable=True)
    expected_total = Column(Numeric(15, 2), nullable=True)
    received_total = Column(Numeric(15, 2), nullable=True)
    accepted_total = Column(Numeric(15, 2), nullable=True)
    rejected_total = Column(Numeric(15, 2), nullable=True)

    # Inspeção do item
    inspection_result = Column(String(30), nullable=True)
    inspection_notes = Column(Text, nullable=True)

    # Lote e validade
    batch_number = Column(String(50), nullable=True)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    serial_numbers = Column(JSONB, default=list)  # Lista de números de série

    # Local de armazenamento
    storage_location = Column(String(100), nullable=True)
    storage_position = Column(String(50), nullable=True)  # Posição específica

    # Rejeição
    rejection_reason = Column(Text, nullable=True)

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    receipt: "GoodsReceipt" = relationship("GoodsReceipt", back_populates="items")

    __table_args__ = (
        Index("ix_goods_receipt_items_receipt", "receipt_id"),
        Index("ix_goods_receipt_items_product", "product_id"),
        Index("ix_goods_receipt_items_order_item", "order_item_id"),
    )

    def __repr__(self) -> str:
        return f"<GoodsReceiptItem {self.item_number}: {self.description[:30]}>"

    @property
    def is_fully_received(self) -> bool:
        """Verifica se foi totalmente recebido."""
        return self.quantity_received >= self.quantity_expected

    @property
    def is_fully_accepted(self) -> bool:
        """Verifica se foi totalmente aceito."""
        return self.quantity_accepted >= self.quantity_expected

    @property
    def has_rejection(self) -> bool:
        """Verifica se tem rejeição."""
        return self.quantity_rejected > 0 if self.quantity_rejected else False

    @property
    def acceptance_rate(self) -> Decimal | None:
        """Taxa de aceitação do item (%)."""
        if self.quantity_received and self.quantity_received > 0:
            return (self.quantity_accepted / self.quantity_received) * 100
        return None

    @property
    def is_expired(self) -> bool:
        """Verifica se está vencido."""
        if self.expiry_date:
            return datetime.utcnow().date() > self.expiry_date
        return False

    def receive(
        self,
        quantity: Decimal,
        accepted: Decimal | None = None,
        rejected: Decimal | None = None,
    ) -> None:
        """Registra recebimento do item."""
        self.quantity_received = quantity
        self.quantity_accepted = accepted or quantity
        self.quantity_rejected = rejected or Decimal("0")
        self.quantity_difference = quantity - self.quantity_expected
        self._calculate_totals()

    def accept_all(self) -> None:
        """Aceita toda quantidade recebida."""
        self.quantity_accepted = self.quantity_received
        self.quantity_rejected = Decimal("0")
        self.inspection_result = InspectionResult.APROVADO.value
        self._calculate_totals()

    def reject_all(self, reason: str) -> None:
        """Rejeita toda quantidade recebida."""
        self.quantity_accepted = Decimal("0")
        self.quantity_rejected = self.quantity_received
        self.rejection_reason = reason
        self.inspection_result = InspectionResult.REPROVADO.value
        self._calculate_totals()

    def partial_accept(self, accepted: Decimal, rejected: Decimal, rejection_reason: str | None = None) -> None:
        """Aceita parcialmente."""
        self.quantity_accepted = accepted
        self.quantity_rejected = rejected
        self.rejection_reason = rejection_reason
        self.inspection_result = InspectionResult.APROVADO_COM_RESSALVA.value
        self._calculate_totals()

    def _calculate_totals(self) -> None:
        """Calcula totais do item."""
        if self.unit_price:
            self.expected_total = self.quantity_expected * self.unit_price
            self.received_total = (self.quantity_received or Decimal("0")) * self.unit_price
            self.accepted_total = (self.quantity_accepted or Decimal("0")) * self.unit_price
            self.rejected_total = (self.quantity_rejected or Decimal("0")) * self.unit_price

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "item_number": self.item_number,
            "description": self.description,
            "unit_of_measure": self.unit_of_measure,
            "quantity_expected": float(self.quantity_expected),
            "quantity_received": float(self.quantity_received) if self.quantity_received else 0,
            "quantity_accepted": float(self.quantity_accepted) if self.quantity_accepted else 0,
            "quantity_rejected": float(self.quantity_rejected) if self.quantity_rejected else 0,
            "unit_price": float(self.unit_price) if self.unit_price else None,
            "inspection_result": self.inspection_result,
            "batch_number": self.batch_number,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "is_fully_accepted": self.is_fully_accepted,
        }
