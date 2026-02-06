"""Model para categorias de reembolso."""

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from core.models import Base


class ReimbursementCategory(Base):
    """Categoria de despesa para reembolso com regras e limites."""

    __tablename__ = "reimbursement_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação
    code = Column(String(20), nullable=False)  # TRANSP, ALIM, etc
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Limites
    default_limit_per_request = Column(Numeric(15, 2), nullable=True)  # Limite por solicitação
    default_limit_monthly = Column(Numeric(15, 2), nullable=True)  # Limite mensal por funcionário

    # Regras
    requires_receipt = Column(Boolean, default=True)  # Requer comprovante
    auto_approve_below = Column(Numeric(15, 2), nullable=True)  # Auto-aprovação abaixo deste valor

    # Contabilidade
    accounting_account = Column(String(30), nullable=True)  # Conta contábil
    cost_center = Column(String(50), nullable=True)  # Centro de custo padrão

    # Controle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_reimbursement_categories_code", "code"),
        Index("ix_reimbursement_categories_condominio", "condominio_id"),
        Index(
            "uq_reimbursement_categories_code_condominio",
            "code",
            "condominio_id",
            unique=True,
        ),
    )

    def __repr__(self) -> str:
        return f"<ReimbursementCategory {self.code} - {self.name}>"

    def check_limit(self, amount: Decimal, request_total: Decimal = Decimal("0.00")) -> tuple[bool, Optional[str]]:
        """
        Verifica se o valor está dentro do limite.

        Returns:
            Tuple (is_within_limit, error_message)
        """
        if self.default_limit_per_request:
            if amount + request_total > self.default_limit_per_request:
                return False, f"Valor excede limite por solicitação de R$ {self.default_limit_per_request}"

        return True, None

    def can_auto_approve(self, amount: Decimal) -> bool:
        """Verifica se pode ser auto-aprovado."""
        if not self.auto_approve_below:
            return False
        return amount <= self.auto_approve_below

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "default_limit_per_request": float(self.default_limit_per_request) if self.default_limit_per_request else None,
            "default_limit_monthly": float(self.default_limit_monthly) if self.default_limit_monthly else None,
            "requires_receipt": self.requires_receipt,
            "auto_approve_below": float(self.auto_approve_below) if self.auto_approve_below else None,
            "accounting_account": self.accounting_account,
            "cost_center": self.cost_center,
            "is_active": self.is_active,
        }
