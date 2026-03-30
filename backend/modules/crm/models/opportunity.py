"""
Modelo Opportunity para gestão do funil de vendas.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:  # pragma: no cover
    from core.models import User
    from modules.crm.models.lead import Lead


class OpportunityStage(StrEnum):
    """Estágios do funil de vendas."""

    QUALIFICATION = "qualification"  # Qualificação inicial
    NEEDS_ANALYSIS = "needs_analysis"  # Análise de necessidades
    PROPOSAL = "proposal"  # Proposta enviada
    NEGOTIATION = "negotiation"  # Em negociação
    CLOSED_WON = "closed_won"  # Fechado - Ganho
    CLOSED_LOST = "closed_lost"  # Fechado - Perdido


class OpportunityPriority(StrEnum):
    """Prioridade da oportunidade."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LossReason(StrEnum):
    """Motivo de perda da oportunidade."""

    PRICE = "price"  # Preço
    COMPETITOR = "competitor"  # Perdeu para concorrente
    NO_BUDGET = "no_budget"  # Sem orçamento
    NO_DECISION = "no_decision"  # Não houve decisão
    TIMING = "timing"  # Timing inadequado
    PRODUCT_FIT = "product_fit"  # Produto não adequado
    NO_RESPONSE = "no_response"  # Cliente não respondeu
    OTHER = "other"  # Outro motivo


class Opportunity(Base):
    """
    Modelo de Opportunity para gestão do funil de vendas.

    Representa uma oportunidade de negócio originada de um Lead qualificado.

    Attributes:
        id: Identificador único
        title: Título/nome da oportunidade
        lead_id: Lead de origem (opcional após conversão)
        stage: Estágio no funil
        priority: Prioridade
        value: Valor da oportunidade
        probability: Probabilidade de fechamento (%)
        expected_close_date: Data prevista de fechamento
        actual_close_date: Data real de fechamento
        owner_id: Responsável pela oportunidade
        loss_reason: Motivo de perda (se perdida)
        competitor: Nome do concorrente (se perdido para)
        notes: Observações
    """

    __tablename__ = "opportunities"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Dados básicos
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Origem
    lead_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Dados do cliente (copiados do Lead ou preenchidos manualmente)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Estágio e prioridade
    stage: Mapped[str] = mapped_column(
        String(50),
        default=OpportunityStage.QUALIFICATION.value,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        default=OpportunityPriority.MEDIUM.value,
        nullable=False,
    )

    # Valores
    value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    probability: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Datas
    expected_close_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    actual_close_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)

    # Responsável
    owner_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Dados de fechamento
    loss_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    competitor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    win_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    loss_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Observações gerais
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campos de controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relacionamentos
    lead: Mapped[Optional["Lead"]] = relationship(
        "Lead",
        foreign_keys=[lead_id],
        lazy="selectin",
    )
    owner: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[owner_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Opportunity {self.title} ({self.stage})>"

    @property
    def weighted_value(self) -> float:
        """Calcula valor ponderado (valor * probabilidade)."""
        return self.value * (self.probability / 100)

    @property
    def is_open(self) -> bool:
        """Verifica se a oportunidade está aberta."""
        return self.stage not in (
            OpportunityStage.CLOSED_WON.value,
            OpportunityStage.CLOSED_LOST.value,
        )

    @property
    def is_won(self) -> bool:
        """Verifica se a oportunidade foi ganha."""
        return self.stage == OpportunityStage.CLOSED_WON.value

    @property
    def is_lost(self) -> bool:
        """Verifica se a oportunidade foi perdida."""
        return self.stage == OpportunityStage.CLOSED_LOST.value

    @property
    def days_in_pipeline(self) -> int:
        """Calcula dias no pipeline."""
        if self.actual_close_date:
            return (self.actual_close_date - self.created_at.date()).days
        return (datetime.now().date() - self.created_at.date()).days

    @property
    def is_overdue(self) -> bool:
        """Verifica se passou da data prevista de fechamento."""
        if not self.expected_close_date or not self.is_open:
            return False
        return datetime.now().date() > self.expected_close_date
