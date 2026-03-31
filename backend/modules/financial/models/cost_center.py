"""Cost Center model - Centro de Custo."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.journal_entry import JournalEntryLine


class CostCenterType(StrEnum):
    """Tipo do centro de custo."""

    PRODUCTIVE = "PRODUCTIVE"  # Produtivo (gera receita)
    ADMINISTRATIVE = "ADMINISTRATIVE"  # Administrativo
    COMMERCIAL = "COMMERCIAL"  # Comercial
    OPERATIONAL = "OPERATIONAL"  # Operacional
    SUPPORT = "SUPPORT"  # Suporte/Apoio
    PROJECT = "PROJECT"  # Projeto específico
    DEPARTMENT = "DEPARTMENT"  # Departamento
    BRANCH = "BRANCH"  # Filial
    OTHER = "OTHER"  # Outros


class CostCenterStatus(StrEnum):
    """Status do centro de custo."""

    ACTIVE = "ACTIVE"  # Ativo
    INACTIVE = "INACTIVE"  # Inativo
    BLOCKED = "BLOCKED"  # Bloqueado
    CLOSED = "CLOSED"  # Encerrado


class AllocationMethod(StrEnum):
    """Método de rateio."""

    DIRECT = "DIRECT"  # Direto (100%)
    PERCENTAGE = "PERCENTAGE"  # Por percentual
    HEADCOUNT = "HEADCOUNT"  # Por número de funcionários
    AREA = "AREA"  # Por área (m²)
    REVENUE = "REVENUE"  # Por receita
    PRODUCTION = "PRODUCTION"  # Por produção
    CUSTOM = "CUSTOM"  # Personalizado


class CostCenter(Base):
    """Centro de Custo - para rateio de despesas e receitas."""

    __tablename__ = "fin_cost_centers"
    __table_args__ = (UniqueConstraint("condominio_id", "code", name="uq_cost_center_code"),)

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Hierarquia
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_centers.id"),
        nullable=True,
        index=True,
    )

    # Identificação
    code = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    # short_name removido: coluna não existe na tabela fin_cost_centers
    description = Column(Text, nullable=True)

    # Tipo e Status
    # cost_center_type removido: coluna chama-se center_type no banco
    center_type = Column(
        Enum(CostCenterType, name="costcentertype", create_type=True),
        nullable=False,
        default=CostCenterType.ADMINISTRATIVE,
    )
    status = Column(
        Enum(CostCenterStatus, name="costcenterstatus", create_type=True),
        nullable=False,
        default=CostCenterStatus.ACTIVE,
    )

    # Nível e Caminho
    level = Column(Integer, nullable=False, default=1)
    full_path = Column(String(500), nullable=True)
    # order_index removido: não existe na tabela
    # path removido: chama-se full_path no banco

    # Responsável
    manager_id = Column(UUID(as_uuid=True), nullable=True)
    # manager_name removido: não existe na tabela
    department = Column(String(100), nullable=True)

    # Orçamento (mapeados para nomes reais do banco)
    budget_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    actual_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    budget_year = Column(Integer, nullable=True)
    budget_alert_percent = Column(Numeric(5, 2), nullable=True)
    # budget_annual, budget_monthly, budget_used, budget_available removidos: não existem

    # Rateio
    allocation_method = Column(
        Enum(AllocationMethod, name="allocationmethod", create_type=True),
        nullable=False,
        default=AllocationMethod.DIRECT,
    )
    allocation_percentage = Column(Numeric(5, 2), default=Decimal("100"), nullable=False)
    allocation_basis = Column(String(50), nullable=True)
    allocation_value = Column(Numeric(18, 2), nullable=True)
    # allocation_base removido: chama-se allocation_basis no banco
    # headcount, area_m2 removidos: não existem na tabela

    # Totais removidos (não existem na tabela): total_debit, total_credit,
    # current_balance, period_debit, period_credit

    # Controle de período
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Última movimentação removido: last_movement_date não existe

    # Integração
    external_code = Column(String(50), nullable=True)
    # legacy_code removido: não existe na tabela
    integration_data = Column(JSONB, nullable=True)

    # Flags
    is_productive = Column(Boolean, default=True, nullable=False)
    is_allocatable = Column(Boolean, default=True, nullable=False)
    accepts_entries = Column(Boolean, default=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    # is_default, requires_approval, approval_limit, allows_over_budget removidos: não existem

    # Observações
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    parent: Optional["CostCenter"] = relationship(
        "CostCenter",
        remote_side="CostCenter.id",
        back_populates="children",
    )
    children: list["CostCenter"] = relationship(
        "CostCenter",
        back_populates="parent",
        lazy="dynamic",
    )
    journal_lines: list["JournalEntryLine"] = relationship(
        "JournalEntryLine",
        back_populates="cost_center",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostCenter {self.code} - {self.name}>"

    @property
    def is_over_budget(self) -> bool:
        """Verifica se está acima do orçamento."""
        if self.budget_monthly == 0:
            return False
        return self.period_debit > self.budget_monthly

    @property
    def budget_usage_percent(self) -> Decimal:
        """Calcula percentual de uso do orçamento."""
        if self.budget_monthly == 0:
            return Decimal("0")
        return (self.period_debit / self.budget_monthly) * 100

    @property
    def is_active(self) -> bool:
        """Verifica se o centro de custo está ativo."""
        return self.status == CostCenterStatus.ACTIVE and self.active
