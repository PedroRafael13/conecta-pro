"""Model para itens de reembolso (despesas individuais)."""

import uuid
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
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.reimbursement.models.reimbursement_attachment import ReimbursementAttachment
    from modules.reimbursement.models.reimbursement_request import ReimbursementRequest


class ExpenseCategory(StrEnum):
    """Categoria de despesa."""

    TRANSPORTE = "transporte"  # Uber, taxi, combustível
    ALIMENTACAO = "alimentacao"  # Refeições, lanches
    HOSPEDAGEM = "hospedagem"  # Hotéis, pousadas
    MATERIAL = "material"  # Material de escritório, ferramentas
    COMUNICACAO = "comunicacao"  # Telefone, internet
    VIAGEM = "viagem"  # Passagens aéreas, rodoviárias
    ESTACIONAMENTO = "estacionamento"  # Estacionamento
    PEDAGIO = "pedagio"  # Pedágios
    SAUDE = "saude"  # Farmácia, exames
    CURSOS = "cursos"  # Treinamentos, cursos
    OUTROS = "outros"  # Outros


class DocumentType(StrEnum):
    """Tipo de documento fiscal."""

    NOTA_FISCAL = "nota_fiscal"
    CUPOM_FISCAL = "cupom_fiscal"
    RECIBO = "recibo"
    FATURA = "fatura"
    BOLETO = "boleto"
    COMPROVANTE = "comprovante"
    OUTROS = "outros"


# Labels para categorias
EXPENSE_CATEGORY_LABELS = {
    ExpenseCategory.TRANSPORTE: "Transporte",
    ExpenseCategory.ALIMENTACAO: "Alimentação",
    ExpenseCategory.HOSPEDAGEM: "Hospedagem",
    ExpenseCategory.MATERIAL: "Material",
    ExpenseCategory.COMUNICACAO: "Comunicação",
    ExpenseCategory.VIAGEM: "Viagem",
    ExpenseCategory.ESTACIONAMENTO: "Estacionamento",
    ExpenseCategory.PEDAGIO: "Pedágio",
    ExpenseCategory.SAUDE: "Saúde",
    ExpenseCategory.CURSOS: "Cursos/Treinamentos",
    ExpenseCategory.OUTROS: "Outros",
}


class ReimbursementItem(Base):
    """Item individual de uma solicitação de reembolso."""

    __tablename__ = "reimbursement_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Solicitação pai
    request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reimbursement_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Categoria vinculada (opcional)
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reimbursement_categories.id"),
        nullable=True,
    )

    # Tipo de despesa (legacy: "category" col no banco, mapeado aqui para compatibilidade)
    category = Column(String(50), nullable=False, default=ExpenseCategory.OUTROS.value)
    category_type = Column(String(30), nullable=False, default=ExpenseCategory.OUTROS.value)

    # Descrição
    description = Column(String(500), nullable=False)
    merchant = Column(String(200), nullable=True)  # Nome do estabelecimento

    # Data e valor
    expense_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2), nullable=True)  # Valor aprovado (pode ser diferente)

    # Documento fiscal
    document_type = Column(String(30), nullable=True, default=DocumentType.OUTROS.value)
    document_number = Column(String(50), nullable=True)  # Número da NF/Recibo

    # Aprovação do item
    is_approved = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    request: Optional["ReimbursementRequest"] = relationship(
        "ReimbursementRequest",
        back_populates="items",
    )
    attachments: list["ReimbursementAttachment"] = relationship(
        "ReimbursementAttachment",
        back_populates="item",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="ReimbursementAttachment.item_id",
    )

    __table_args__ = (
        Index("ix_reimbursement_items_request", "request_id"),
        Index("ix_reimbursement_items_category_type", "category_type"),
        Index("ix_reimbursement_items_expense_date", "expense_date"),
    )

    def __repr__(self) -> str:
        return f"<ReimbursementItem {self.id} - {self.category_type} - {self.amount}>"

    def approve(self, approved_amount: Decimal | None = None) -> None:
        """Aprova o item."""
        self.is_approved = True
        self.approved_amount = approved_amount or self.amount
        self.rejection_reason = None

    def reject(self, reason: str) -> None:
        """Rejeita o item."""
        self.is_approved = False
        self.approved_amount = Decimal("0.00")
        self.rejection_reason = reason

    @property
    def category_label(self) -> str:
        """Retorna o label da categoria."""
        try:
            return EXPENSE_CATEGORY_LABELS.get(
                ExpenseCategory(self.category_type),
                self.category_type,
            )
        except ValueError:
            return self.category_type

    @property
    def final_amount(self) -> Decimal:
        """Retorna o valor final (aprovado ou solicitado)."""
        if self.is_approved and self.approved_amount is not None:
            return self.approved_amount
        return self.amount

    @property
    def has_attachment(self) -> bool:
        """Verifica se tem comprovante anexado."""
        return len([a for a in self.attachments if a.is_active]) > 0

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "request_id": str(self.request_id),
            "category_type": self.category_type,
            "category_label": self.category_label,
            "description": self.description,
            "merchant": self.merchant,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "amount": float(self.amount),
            "approved_amount": float(self.approved_amount) if self.approved_amount else None,
            "document_type": self.document_type,
            "document_number": self.document_number,
            "is_approved": self.is_approved,
            "rejection_reason": self.rejection_reason,
            "has_attachment": self.has_attachment,
            "notes": self.notes,
            "is_active": self.is_active,
        }
