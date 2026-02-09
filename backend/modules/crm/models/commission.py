"""
Model para Comissões de Vendedores.
Gerencia regras de comissão, cálculos e pagamentos.
"""

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    pass


class CommissionType(StrEnum):
    """Tipo de comissão."""

    FIXED = "fixed"  # Valor fixo por venda
    PERCENTAGE = "percentage"  # Percentual sobre valor
    MARGIN = "margin"  # Percentual sobre margem
    PROGRESSIVE = "progressive"  # Escala progressiva
    BONUS = "bonus"  # Bônus por meta


class CommissionTrigger(StrEnum):
    """Gatilho para pagamento da comissão."""

    ON_SIGNATURE = "on_signature"  # Na assinatura do contrato
    ON_FIRST_PAYMENT = "on_first_payment"  # No primeiro pagamento
    ON_EACH_PAYMENT = "on_each_payment"  # A cada pagamento
    ON_FULL_PAYMENT = "on_full_payment"  # Após pagamento total
    MONTHLY = "monthly"  # Mensal (recorrente)


class CommissionStatus(StrEnum):
    """Status da comissão."""

    PENDING = "pending"  # Pendente (aguardando gatilho)
    APPROVED = "approved"  # Aprovada para pagamento
    PAID = "paid"  # Paga
    CANCELLED = "cancelled"  # Cancelada
    REVERSED = "reversed"  # Estornada


class PaymentMethod(StrEnum):
    """Método de pagamento da comissão."""

    PAYROLL = "payroll"  # Folha de pagamento
    BANK_TRANSFER = "bank_transfer"  # Transferência bancária
    PIX = "pix"  # PIX
    CHECK = "check"  # Cheque


class CommissionRule(Base):
    """Model para regras de comissão."""

    __tablename__ = "commission_rules"

    id = Column(UUID(as_uuid=False), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e cálculo
    commission_type = Column(String(20), default=CommissionType.PERCENTAGE.value, nullable=False)
    base_value = Column(Float, default=0.0, nullable=False)  # Valor ou percentual base
    min_value = Column(Float, nullable=True)  # Comissão mínima
    max_value = Column(Float, nullable=True)  # Comissão máxima

    # Escala progressiva (se commission_type = progressive)
    # Formato: [{"min": 0, "max": 10000, "rate": 5}, {"min": 10001, "max": 50000, "rate": 7}]
    progressive_scale = Column(Text, nullable=True)  # JSON string

    # Gatilho de pagamento
    trigger = Column(String(20), default=CommissionTrigger.ON_FIRST_PAYMENT.value, nullable=False)
    trigger_delay_days = Column(Integer, default=0, nullable=False)  # Dias após gatilho

    # Filtros de aplicação
    applies_to_all = Column(Boolean, default=True, nullable=False)
    product_categories = Column(Text, nullable=True)  # JSON: categorias de produto
    service_types = Column(Text, nullable=True)  # JSON: tipos de serviço
    min_sale_value = Column(Float, nullable=True)  # Valor mínimo da venda
    max_sale_value = Column(Float, nullable=True)  # Valor máximo da venda

    # Período de vigência
    valid_from = Column(Date, default=date.today, nullable=False)
    valid_until = Column(Date, nullable=True)

    # Prioridade (para regras conflitantes)
    priority = Column(Integer, default=0, nullable=False)

    # Controle
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    commissions = relationship("Commission", back_populates="rule")
    seller_rules = relationship("SellerCommissionRule", back_populates="rule")

    @property
    def is_valid(self) -> bool:
        """Verifica se a regra está vigente."""
        today = date.today()
        if self.valid_from and self.valid_from > today:
            return False
        if self.valid_until and self.valid_until < today:
            return False
        return self.is_active

    def calculate_commission(self, sale_value: float, margin: float = 0.0) -> float:
        """
        Calcula valor da comissão.

        Args:
            sale_value: Valor total da venda
            margin: Margem de lucro (se commission_type = margin)

        Returns:
            Valor da comissão calculada
        """
        commission = 0.0

        if self.commission_type == CommissionType.FIXED.value:
            commission = self.base_value

        elif self.commission_type == CommissionType.PERCENTAGE.value:
            commission = sale_value * (self.base_value / 100)

        elif self.commission_type == CommissionType.MARGIN.value:
            commission = margin * (self.base_value / 100)

        elif self.commission_type == CommissionType.PROGRESSIVE.value:
            commission = self._calculate_progressive(sale_value)

        # Aplicar limites
        if self.min_value and commission < self.min_value:
            commission = self.min_value
        if self.max_value and commission > self.max_value:
            commission = self.max_value

        return round(commission, 2)

    def _calculate_progressive(self, sale_value: float) -> float:
        """Calcula comissão com escala progressiva."""
        import json  # pylint: disable=import-outside-toplevel

        if not self.progressive_scale:
            return sale_value * (self.base_value / 100)

        try:
            scale = json.loads(self.progressive_scale)
            for tier in scale:
                tier_min = tier.get("min", 0)
                tier_max = tier.get("max", float("inf"))
                rate = tier.get("rate", 0)

                if tier_min <= sale_value <= tier_max:
                    return sale_value * (rate / 100)

            # Se não encontrou tier, usa base_value
            return sale_value * (self.base_value / 100)

        except (json.JSONDecodeError, KeyError):
            return sale_value * (self.base_value / 100)


class SellerCommissionRule(Base):  # pylint: disable=too-few-public-methods
    """Associação entre vendedor e regra de comissão (regras específicas por vendedor)."""

    __tablename__ = "seller_commission_rules"

    id = Column(UUID(as_uuid=False), primary_key=True)
    seller_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_id = Column(
        UUID(as_uuid=False),
        ForeignKey("commission_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Override do percentual base (opcional)
    custom_base_value = Column(Float, nullable=True)

    # Período de validade específico
    valid_from = Column(Date, default=date.today, nullable=False)
    valid_until = Column(Date, nullable=True)

    # Controle
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    rule = relationship("CommissionRule", back_populates="seller_rules")


class Commission(Base):
    """Model para comissão calculada."""

    __tablename__ = "commissions"

    id = Column(UUID(as_uuid=False), primary_key=True)
    reference_number = Column(String(50), unique=True, nullable=False, index=True)

    # Relacionamentos
    seller_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    proposal_id = Column(
        UUID(as_uuid=False),
        ForeignKey("proposals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rule_id = Column(
        UUID(as_uuid=False),
        ForeignKey("commission_rules.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Valores da venda
    sale_value = Column(Float, nullable=False)  # Valor total da venda
    sale_margin = Column(Float, default=0.0, nullable=False)  # Margem (se aplicável)

    # Cálculo da comissão
    commission_type = Column(String(20), nullable=False)
    commission_rate = Column(Float, nullable=False)  # Taxa aplicada (% ou valor)
    base_commission = Column(Float, nullable=False)  # Comissão calculada
    adjustments = Column(Float, default=0.0, nullable=False)  # Ajustes (+/-)
    final_commission = Column(Float, nullable=False)  # Comissão final

    # Status e datas
    status = Column(String(20), default=CommissionStatus.PENDING.value, nullable=False, index=True)
    trigger = Column(String(20), nullable=False)
    trigger_date = Column(Date, nullable=True)  # Data do gatilho
    due_date = Column(Date, nullable=True)  # Data prevista para pagamento
    paid_date = Column(Date, nullable=True)  # Data efetiva do pagamento

    # Período de referência (para comissões recorrentes)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)

    # Descrição
    description = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    # Controle
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_by_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at = Column(DateTime, nullable=True)

    # Relationships
    rule = relationship("CommissionRule", back_populates="commissions")
    payments = relationship("CommissionPayment", back_populates="commission", cascade="all, delete-orphan")

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == CommissionStatus.PENDING.value

    @property
    def is_approved(self) -> bool:
        """Verifica se foi aprovada."""
        return self.status == CommissionStatus.APPROVED.value

    @property
    def is_paid(self) -> bool:
        """Verifica se foi paga."""
        return self.status == CommissionStatus.PAID.value

    @property
    def paid_amount(self) -> float:
        """Valor total pago."""
        if not self.payments:
            return 0.0
        return sum(p.amount for p in self.payments if p.is_confirmed)

    @property
    def pending_amount(self) -> float:
        """Valor pendente de pagamento."""
        return self.final_commission - self.paid_amount

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if not self.due_date:
            return False
        if self.is_paid:
            return False
        return self.due_date < date.today()

    @property
    def days_until_due(self) -> int | None:
        """Dias até vencimento."""
        if not self.due_date:
            return None
        delta = self.due_date - date.today()
        return delta.days


class CommissionPayment(Base):  # pylint: disable=too-few-public-methods
    """Model para pagamento de comissão."""

    __tablename__ = "commission_payments"

    id = Column(UUID(as_uuid=False), primary_key=True)
    commission_id = Column(
        UUID(as_uuid=False),
        ForeignKey("commissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Pagamento
    amount = Column(Float, nullable=False)
    payment_method = Column(String(20), default=PaymentMethod.PAYROLL.value, nullable=False)
    payment_date = Column(Date, nullable=False)

    # Referência
    payment_reference = Column(String(100), nullable=True)  # Nº do lote/folha
    bank_account = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)

    # Confirmação
    is_confirmed = Column(Boolean, default=False, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Observações
    notes = Column(Text, nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationship
    commission = relationship("Commission", back_populates="payments")


class CommissionSummary(Base):
    """Model para resumo mensal de comissões por vendedor."""

    __tablename__ = "commission_summaries"

    id = Column(UUID(as_uuid=False), primary_key=True)
    seller_id = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Período
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # Totais
    total_sales = Column(Float, default=0.0, nullable=False)
    total_sales_count = Column(Integer, default=0, nullable=False)
    total_commissions = Column(Float, default=0.0, nullable=False)
    total_paid = Column(Float, default=0.0, nullable=False)
    total_pending = Column(Float, default=0.0, nullable=False)

    # Metas
    sales_target = Column(Float, nullable=True)
    target_percentage = Column(Float, nullable=True)  # % atingido da meta
    bonus_earned = Column(Float, default=0.0, nullable=False)

    # Controle
    is_closed = Column(Boolean, default=False, nullable=False)  # Mês fechado
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def is_target_achieved(self) -> bool:
        """Verifica se atingiu a meta."""
        if not self.sales_target:
            return False
        return self.total_sales >= self.sales_target

    @property
    def remaining_to_target(self) -> float:
        """Valor restante para atingir meta."""
        if not self.sales_target:
            return 0.0
        remaining = self.sales_target - self.total_sales
        return max(0.0, remaining)
