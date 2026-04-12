"""Model para requisições de compra."""

import uuid
from datetime import datetime, timedelta
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
    from modules.financial.models.purchase_quotation import PurchaseQuotation


class RequisitionStatus(StrEnum):
    """Status da requisição de compra."""

    RASCUNHO = "rascunho"
    PENDENTE_APROVACAO = "pendente_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    EM_COTACAO = "em_cotacao"
    COTACAO_CONCLUIDA = "cotacao_concluida"
    EM_COMPRA = "em_compra"
    PARCIALMENTE_ATENDIDA = "parcialmente_atendida"
    ATENDIDA = "atendida"
    CANCELADA = "cancelada"


class RequisitionPriority(StrEnum):
    """Prioridade da requisição."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"
    CRITICA = "critica"


class RequisitionType(StrEnum):
    """Tipo de requisição."""

    MATERIAL = "material"
    SERVICO = "servico"
    EQUIPAMENTO = "equipamento"
    MANUTENCAO = "manutencao"
    EMERGENCIAL = "emergencial"
    REPOSICAO = "reposicao"
    PROJETO = "projeto"


class PurchaseRequisition(Base):
    """Requisição de compra (solicitação interna)."""

    __tablename__ = "purchase_requisitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    number = Column(String(20), nullable=False, index=True)  # REQ-YYYY-NNNN
    revision = Column(Integer, default=1)  # Versão/revisão
    requisition_type = Column(String(20), nullable=False, default=RequisitionType.MATERIAL.value)
    status = Column(String(30), nullable=False, default=RequisitionStatus.RASCUNHO.value)
    priority = Column(String(20), nullable=False, default=RequisitionPriority.MEDIA.value)

    # Descrição
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    justification = Column(Text, nullable=True)  # Justificativa da compra

    # Solicitante
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    department = Column(String(100), nullable=True)  # Departamento solicitante
    cost_center = Column(String(50), nullable=True)  # Centro de custo

    # Datas
    request_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    needed_by_date = Column(Date, nullable=True)  # Data necessária
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Valores estimados
    estimated_total = Column(Numeric(15, 2), default=0)
    approved_budget = Column(Numeric(15, 2), nullable=True)  # Orçamento aprovado
    actual_total = Column(Numeric(15, 2), default=0)  # Total real após compra

    # Cotação
    min_quotations = Column(Integer, default=3)  # Mínimo de cotações necessárias
    quotation_deadline = Column(Date, nullable=True)  # Prazo para cotações

    # Entrega
    delivery_address = Column(Text, nullable=True)
    delivery_contact = Column(String(100), nullable=True)
    delivery_phone = Column(String(20), nullable=True)
    delivery_instructions = Column(Text, nullable=True)

    # Fornecedor sugerido
    suggested_supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    supplier_justification = Column(Text, nullable=True)  # Justificativa do fornecedor único

    # Anexos e observações
    attachments = Column(JSONB, default=list)  # [{type, url, name}]
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Rejeição
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Cancelamento
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Histórico de aprovações
    approval_history = Column(JSONB, default=list)
    # [{level, approver_id, action, comment, timestamp}]

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    items: list["PurchaseRequisitionItem"] = relationship(
        "PurchaseRequisitionItem",
        back_populates="requisition",
        cascade="all, delete-orphan",
    )
    quotations: list["PurchaseQuotation"] = relationship("PurchaseQuotation", back_populates="requisition")

    __table_args__ = (
        Index("ix_purchase_requisitions_number", "number"),
        Index("ix_purchase_requisitions_status", "status"),
        Index("ix_purchase_requisitions_requester", "requester_id"),
        Index("ix_purchase_requisitions_condominio_status", "condominio_id", "status"),
        Index("ix_purchase_requisitions_date", "request_date"),
    )

    def __repr__(self) -> str:
        return f"<PurchaseRequisition {self.number}>"

    @property
    def is_draft(self) -> bool:
        """Verifica se está em rascunho."""
        return self.status == RequisitionStatus.RASCUNHO.value

    @property
    def is_pending_approval(self) -> bool:
        """Verifica se aguarda aprovação."""
        return self.status == RequisitionStatus.PENDENTE_APROVACAO.value

    @property
    def is_approved(self) -> bool:
        """Verifica se está aprovada."""
        return self.status in [
            RequisitionStatus.APROVADA.value,
            RequisitionStatus.EM_COTACAO.value,
            RequisitionStatus.COTACAO_CONCLUIDA.value,
            RequisitionStatus.EM_COMPRA.value,
            RequisitionStatus.PARCIALMENTE_ATENDIDA.value,
            RequisitionStatus.ATENDIDA.value,
        ]

    @property
    def is_cancelled(self) -> bool:
        """Verifica se está cancelada."""
        return self.status == RequisitionStatus.CANCELADA.value

    @property
    def is_urgent(self) -> bool:
        """Verifica se é urgente."""
        return self.priority in [
            RequisitionPriority.URGENTE.value,
            RequisitionPriority.CRITICA.value,
        ]

    @property
    def items_count(self) -> int:
        """Retorna quantidade de itens."""
        return len(self.items) if self.items else 0

    @property
    def quotations_count(self) -> int:
        """Retorna quantidade de cotações."""
        return len(self.quotations) if self.quotations else 0

    @property
    def is_overdue(self) -> bool:
        """Verifica se passou da data necessária."""
        if self.needed_by_date and not self.is_cancelled:
            return datetime.utcnow().date() > self.needed_by_date
        return False

    @property
    def days_until_needed(self) -> int | None:
        """Dias até a data necessária."""
        if self.needed_by_date:
            delta = self.needed_by_date - datetime.utcnow().date()
            return delta.days
        return None

    def submit_for_approval(self) -> None:
        """Submete para aprovação."""
        if self.status != RequisitionStatus.RASCUNHO.value:
            raise ValueError("Apenas requisições em rascunho podem ser submetidas")
        if not self.items:
            raise ValueError("Requisição deve ter pelo menos um item")
        self.status = RequisitionStatus.PENDENTE_APROVACAO.value

    def approve(self, approver_id: uuid.UUID, comment: str | None = None) -> None:
        """Aprova a requisição."""
        if self.status != RequisitionStatus.PENDENTE_APROVACAO.value:
            raise ValueError("Apenas requisições pendentes podem ser aprovadas")
        self.status = RequisitionStatus.APROVADA.value
        self.approved_at = datetime.utcnow()
        self.approved_by = approver_id
        self._add_approval_history("aprovado", approver_id, comment)

    def reject(self, rejector_id: uuid.UUID, reason: str, comment: str | None = None) -> None:
        """Rejeita a requisição."""
        if self.status != RequisitionStatus.PENDENTE_APROVACAO.value:
            raise ValueError("Apenas requisições pendentes podem ser rejeitadas")
        self.status = RequisitionStatus.REJEITADA.value
        self.rejection_reason = reason
        self.rejected_at = datetime.utcnow()
        self.rejected_by = rejector_id
        self._add_approval_history("rejeitado", rejector_id, comment or reason)

    def cancel(self, user_id: uuid.UUID, reason: str) -> None:
        """Cancela a requisição."""
        if self.status in [
            RequisitionStatus.ATENDIDA.value,
            RequisitionStatus.CANCELADA.value,
        ]:
            raise ValueError("Requisição não pode ser cancelada")
        self.status = RequisitionStatus.CANCELADA.value
        self.cancellation_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = user_id

    def start_quotation(self) -> None:
        """Inicia processo de cotação."""
        if self.status != RequisitionStatus.APROVADA.value:
            raise ValueError("Apenas requisições aprovadas podem iniciar cotação")
        self.status = RequisitionStatus.EM_COTACAO.value
        if not self.quotation_deadline:
            self.quotation_deadline = datetime.utcnow().date() + timedelta(days=7)

    def complete_quotation(self) -> None:
        """Marca cotação como concluída."""
        if self.status != RequisitionStatus.EM_COTACAO.value:
            raise ValueError("Requisição não está em cotação")
        self.status = RequisitionStatus.COTACAO_CONCLUIDA.value

    def start_purchase(self) -> None:
        """Inicia processo de compra."""
        if self.status != RequisitionStatus.COTACAO_CONCLUIDA.value:
            raise ValueError("Cotação não foi concluída")
        self.status = RequisitionStatus.EM_COMPRA.value

    def mark_partially_fulfilled(self) -> None:
        """Marca como parcialmente atendida."""
        self.status = RequisitionStatus.PARCIALMENTE_ATENDIDA.value

    def mark_fulfilled(self) -> None:
        """Marca como totalmente atendida."""
        self.status = RequisitionStatus.ATENDIDA.value

    def calculate_total(self) -> Decimal:
        """Calcula total estimado dos itens."""
        total = Decimal("0")
        if self.items:
            for item in self.items:
                if item.estimated_total:
                    total += item.estimated_total
        self.estimated_total = total
        return total

    def _add_approval_history(self, action: str, user_id: uuid.UUID, comment: str | None = None) -> None:
        """Adiciona entrada ao histórico de aprovações."""
        if not self.approval_history:
            self.approval_history = []
        self.approval_history.append(
            {
                "action": action,
                "user_id": str(user_id),
                "comment": comment,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "number": self.number,
            "title": self.title,
            "requisition_type": self.requisition_type,
            "status": self.status,
            "priority": self.priority,
            "request_date": self.request_date.isoformat() if self.request_date else None,
            "needed_by_date": (self.needed_by_date.isoformat() if self.needed_by_date else None),
            "estimated_total": float(self.estimated_total) if self.estimated_total else 0,
            "items_count": self.items_count,
            "quotations_count": self.quotations_count,
            "is_urgent": self.is_urgent,
            "is_overdue": self.is_overdue,
        }


class PurchaseRequisitionItem(Base):
    """Item da requisição de compra."""

    __tablename__ = "purchase_requisition_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requisition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Produto
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True)

    # Identificação do item
    item_number = Column(Integer, nullable=False)  # Número sequencial
    description = Column(String(500), nullable=False)
    specifications = Column(Text, nullable=True)  # Especificações técnicas
    unit_of_measure = Column(String(10), nullable=False, default="un")

    # Quantidade
    quantity_requested = Column(Numeric(10, 2), nullable=False)
    quantity_approved = Column(Numeric(10, 2), nullable=True)
    quantity_ordered = Column(Numeric(10, 2), default=0)  # Quantidade em pedidos
    quantity_received = Column(Numeric(10, 2), default=0)  # Quantidade recebida

    # Preços
    estimated_unit_price = Column(Numeric(15, 2), nullable=True)
    estimated_total = Column(Numeric(15, 2), nullable=True)
    approved_unit_price = Column(Numeric(15, 2), nullable=True)  # Preço aprovado
    actual_unit_price = Column(Numeric(15, 2), nullable=True)  # Preço real

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    requisition: "PurchaseRequisition" = relationship("PurchaseRequisition", back_populates="items")

    __table_args__ = (
        Index("ix_purchase_requisition_items_requisition", "requisition_id"),
        Index("ix_purchase_requisition_items_product", "product_id"),
    )

    def __repr__(self) -> str:
        return f"<PurchaseRequisitionItem {self.item_number}: {self.description[:30]}>"

    @property
    def is_fully_ordered(self) -> bool:
        """Verifica se quantidade total foi pedida."""
        qty = self.quantity_approved or self.quantity_requested
        return self.quantity_ordered >= qty

    @property
    def is_fully_received(self) -> bool:
        """Verifica se quantidade total foi recebida."""
        qty = self.quantity_approved or self.quantity_requested
        return self.quantity_received >= qty

    @property
    def pending_quantity(self) -> Decimal:
        """Quantidade pendente de pedido."""
        qty = self.quantity_approved or self.quantity_requested
        return max(Decimal("0"), qty - self.quantity_ordered)

    @property
    def pending_receipt(self) -> Decimal:
        """Quantidade pendente de recebimento."""
        return max(Decimal("0"), self.quantity_ordered - self.quantity_received)

    def calculate_total(self) -> None:
        """Calcula total estimado."""
        if self.quantity_requested and self.estimated_unit_price:
            self.estimated_total = self.quantity_requested * self.estimated_unit_price

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "item_number": self.item_number,
            "description": self.description,
            "unit_of_measure": self.unit_of_measure,
            "quantity_requested": float(self.quantity_requested),
            "quantity_ordered": float(self.quantity_ordered) if self.quantity_ordered else 0,
            "quantity_received": float(self.quantity_received) if self.quantity_received else 0,
            "estimated_unit_price": (float(self.estimated_unit_price) if self.estimated_unit_price else None),
            "estimated_total": float(self.estimated_total) if self.estimated_total else None,
            "product_id": str(self.product_id) if self.product_id else None,
        }
