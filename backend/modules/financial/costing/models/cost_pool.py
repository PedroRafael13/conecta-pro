"""Cost Pool model - Pools de Custos Indiretos."""

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
    from modules.financial.costing.models.cost_activity import CostActivity


class PoolType(str, enum.Enum):
    """Tipo do pool de custo."""

    OVERHEAD = "OVERHEAD"  # Custos indiretos gerais
    LABOR = "LABOR"  # Mão de obra indireta
    EQUIPMENT = "EQUIPMENT"  # Equipamentos/Máquinas
    FACILITIES = "FACILITIES"  # Instalações
    UTILITIES = "UTILITIES"  # Utilidades (energia, água)
    ADMINISTRATIVE = "ADMINISTRATIVE"  # Administrativo
    TECHNOLOGY = "TECHNOLOGY"  # TI/Tecnologia
    QUALITY = "QUALITY"  # Qualidade
    LOGISTICS = "LOGISTICS"  # Logística
    MAINTENANCE = "MAINTENANCE"  # Manutenção
    SHARED_SERVICES = "SHARED_SERVICES"  # Serviços compartilhados
    CUSTOM = "CUSTOM"  # Personalizado


class PoolStatus(str, enum.Enum):
    """Status do pool."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CLOSED = "CLOSED"


class AllocationBasis(str, enum.Enum):
    """Base de alocação do pool."""

    DIRECT_LABOR_HOURS = "DIRECT_LABOR_HOURS"  # Horas de MOD
    DIRECT_LABOR_COST = "DIRECT_LABOR_COST"  # Custo de MOD
    MACHINE_HOURS = "MACHINE_HOURS"  # Horas máquina
    UNITS_PRODUCED = "UNITS_PRODUCED"  # Unidades produzidas
    REVENUE = "REVENUE"  # Receita
    DIRECT_MATERIALS = "DIRECT_MATERIALS"  # Materiais diretos
    FLOOR_SPACE = "FLOOR_SPACE"  # Área ocupada
    HEADCOUNT = "HEADCOUNT"  # Número de funcionários
    ACTIVITY_BASED = "ACTIVITY_BASED"  # Baseado em atividades (ABC)
    CUSTOM = "CUSTOM"  # Personalizado


class CostPool(Base):
    """Pool de Custo - agrupa custos indiretos para alocação."""

    __tablename__ = "fin_cost_pools"
    __table_args__ = (
        UniqueConstraint("condominio_id", "code", name="uq_cost_pool_code"),
    )

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
        ForeignKey("fin_cost_pools.id"),
        nullable=True,
        index=True,
    )

    # Centro de Custo associado
    cost_center_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_centers.id"),
        nullable=True,
        index=True,
    )

    # Identificação
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Classificação
    pool_type = Column(
        Enum(PoolType, name="pooltype", create_type=True),
        nullable=False,
        default=PoolType.OVERHEAD,
    )
    status = Column(
        Enum(PoolStatus, name="poolstatus", create_type=True),
        nullable=False,
        default=PoolStatus.ACTIVE,
    )
    allocation_basis = Column(
        Enum(AllocationBasis, name="allocationbasis", create_type=True),
        nullable=False,
        default=AllocationBasis.ACTIVITY_BASED,
    )

    # Hierarquia
    level = Column(Integer, default=1, nullable=False)
    path = Column(String(200), nullable=True)
    order_index = Column(Integer, nullable=True)

    # Custos
    total_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    allocated_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    unallocated_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Orçamento
    budget_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    budget_variance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Base de alocação
    allocation_base_quantity = Column(
        Numeric(18, 4), default=Decimal("0"), nullable=False
    )
    allocation_rate = Column(Numeric(18, 6), default=Decimal("0"), nullable=False)
    rate_currency = Column(String(3), default="BRL", nullable=False)

    # Fórmula personalizada (para CUSTOM)
    custom_allocation_formula = Column(Text, nullable=True)
    allocation_weights = Column(JSONB, nullable=True)
    # Ex: {"activity_1": 0.4, "activity_2": 0.6}

    # Componentes do pool
    cost_components = Column(JSONB, nullable=True)
    # Ex: [{"account": "5001", "name": "Energia", "amount": 5000}]

    # Estatísticas
    activities_count = Column(Integer, default=0, nullable=False)
    allocations_count = Column(Integer, default=0, nullable=False)
    last_allocation_date = Column(DateTime(timezone=True), nullable=True)

    # Período
    reference_period = Column(String(7), nullable=True)  # "2024-01"
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Responsável
    manager_id = Column(UUID(as_uuid=True), nullable=True)
    manager_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    # Flags
    is_homogeneous = Column(Boolean, default=True, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    auto_allocate = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    parent: Optional["CostPool"] = relationship(
        "CostPool",
        remote_side="CostPool.id",
        back_populates="children",
    )
    children: list["CostPool"] = relationship(
        "CostPool",
        back_populates="parent",
        lazy="dynamic",
    )
    activities: list["CostActivity"] = relationship(
        "CostActivity",
        back_populates="cost_pool",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostPool {self.code} - {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se o pool está ativo."""
        return self.status == PoolStatus.ACTIVE and self.active

    @property
    def allocation_percent(self) -> Decimal:
        """Calcula percentual alocado."""
        if self.total_cost == 0:
            return Decimal("0")
        return (self.allocated_cost / self.total_cost) * 100

    @property
    def is_fully_allocated(self) -> bool:
        """Verifica se todo custo foi alocado."""
        return abs(self.unallocated_cost) < Decimal("0.01")

    @property
    def budget_variance_percent(self) -> Decimal:
        """Calcula variação percentual do orçamento."""
        if self.budget_amount == 0:
            return Decimal("0")
        return (self.budget_variance / self.budget_amount) * 100

    def calculate_rate(self) -> Decimal:
        """Calcula taxa de alocação."""
        if self.allocation_base_quantity == 0:
            return Decimal("0")
        return self.total_cost / self.allocation_base_quantity

    def add_cost(self, amount: Decimal, component_name: str = None) -> None:
        """Adiciona custo ao pool."""
        self.total_cost += amount
        self.unallocated_cost += amount
        if component_name and self.cost_components is not None:
            self.cost_components.append(
                {
                    "name": component_name,
                    "amount": str(amount),
                    "added_at": datetime.utcnow().isoformat(),
                }
            )

    def allocate(self, amount: Decimal) -> None:
        """Registra alocação."""
        self.allocated_cost += amount
        self.unallocated_cost -= amount
        self.allocations_count += 1
        self.last_allocation_date = datetime.utcnow()

    def recalculate(self) -> None:
        """Recalcula valores do pool."""
        self.unallocated_cost = self.total_cost - self.allocated_cost
        self.budget_variance = self.total_cost - self.budget_amount
        self.allocation_rate = self.calculate_rate()
