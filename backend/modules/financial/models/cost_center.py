"""Cost Center model - Centro de Custo."""

import enum
from datetime import datetime
from decimal import Decimal
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


class CostCenterType(str, enum.Enum):
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


class CostCenterStatus(str, enum.Enum):
    """Status do centro de custo."""

    ACTIVE = "ACTIVE"  # Ativo
    INACTIVE = "INACTIVE"  # Inativo
    BLOCKED = "BLOCKED"  # Bloqueado
    CLOSED = "CLOSED"  # Encerrado


class AllocationMethod(str, enum.Enum):
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
    short_name = Column(String(30), nullable=True)
    description = Column(Text, nullable=True)

    # Tipo e Status
    cost_center_type = Column(
        Enum(CostCenterType, name="costcentertype", create_type=True),
        nullable=False,
        default=CostCenterType.ADMINISTRATIVE,
    )
    status = Column(
        Enum(CostCenterStatus, name="costcenterstatus", create_type=True),
        nullable=False,
        default=CostCenterStatus.ACTIVE,
    )

    # Nível e Ordem
    level = Column(Integer, nullable=False, default=1)
    order_index = Column(Integer, nullable=True)
    path = Column(String(200), nullable=True)

    # Responsável
    manager_id = Column(UUID(as_uuid=True), nullable=True)
    manager_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    # Orçamento
    budget_annual = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    budget_monthly = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    budget_used = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    budget_available = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Rateio
    allocation_method = Column(
        Enum(AllocationMethod, name="allocationmethod", create_type=True),
        nullable=False,
        default=AllocationMethod.DIRECT,
    )
    allocation_percentage = Column(Numeric(5, 2), default=Decimal("100"), nullable=False)
    allocation_base = Column(String(50), nullable=True)

    # Métricas para rateio
    headcount = Column(Integer, default=0, nullable=False)
    area_m2 = Column(Numeric(12, 2), default=Decimal("0"), nullable=False)

    # Totais acumulados
    total_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_balance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Período atual
    period_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    period_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Controle de período
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Última movimentação
    last_movement_date = Column(DateTime(timezone=True), nullable=True)

    # Integração
    external_code = Column(String(50), nullable=True)
    legacy_code = Column(String(50), nullable=True)
    integration_data = Column(JSONB, nullable=True)

    # Flags
    is_default = Column(Boolean, default=False, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    approval_limit = Column(Numeric(18, 2), nullable=True)
    allows_over_budget = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
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
