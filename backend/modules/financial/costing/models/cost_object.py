"""Cost Object model - Objetos de Custo (produtos, serviços, clientes, projetos)."""

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
    from modules.financial.costing.models.cost_allocation import CostAllocation


class CostObjectType(str, enum.Enum):
    """Tipo do objeto de custo."""

    PRODUCT = "PRODUCT"  # Produto
    SERVICE = "SERVICE"  # Serviço
    CONTRACT = "CONTRACT"  # Contrato
    PROJECT = "PROJECT"  # Projeto
    CUSTOMER = "CUSTOMER"  # Cliente
    CUSTOMER_SEGMENT = "CUSTOMER_SEGMENT"  # Segmento de clientes
    CHANNEL = "CHANNEL"  # Canal de distribuição
    REGION = "REGION"  # Região geográfica
    DEPARTMENT = "DEPARTMENT"  # Departamento
    BUSINESS_UNIT = "BUSINESS_UNIT"  # Unidade de negócio
    ORDER = "ORDER"  # Pedido/Ordem
    BATCH = "BATCH"  # Lote
    CAMPAIGN = "CAMPAIGN"  # Campanha


class CostObjectStatus(str, enum.Enum):
    """Status do objeto de custo."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"
    PENDING = "PENDING"


class ProfitabilityLevel(str, enum.Enum):
    """Nível de rentabilidade."""

    HIGHLY_PROFITABLE = "HIGHLY_PROFITABLE"  # >20% margem
    PROFITABLE = "PROFITABLE"  # 10-20% margem
    MARGINAL = "MARGINAL"  # 0-10% margem
    BREAK_EVEN = "BREAK_EVEN"  # ~0% margem
    UNPROFITABLE = "UNPROFITABLE"  # <0% margem


class CostObject(Base):
    """Objeto de Custo - destino final dos custos alocados."""

    __tablename__ = "fin_cost_objects"
    __table_args__ = (
        UniqueConstraint("condominio_id", "code", name="uq_cost_object_code"),
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
        ForeignKey("fin_cost_objects.id"),
        nullable=True,
        index=True,
    )

    # Referência externa (produto, serviço, cliente, projeto)
    reference_type = Column(String(50), nullable=True)  # "product", "customer", etc.
    reference_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Identificação
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    short_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    # Classificação
    object_type = Column(
        Enum(CostObjectType, name="costobjecttype", create_type=True),
        nullable=False,
        default=CostObjectType.SERVICE,
    )
    status = Column(
        Enum(CostObjectStatus, name="costobjectstatus", create_type=True),
        nullable=False,
        default=CostObjectStatus.ACTIVE,
    )

    # Categoria
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)

    # Hierarquia
    level = Column(Integer, default=1, nullable=False)
    path = Column(String(300), nullable=True)
    order_index = Column(Integer, nullable=True)

    # Receita
    revenue = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    revenue_budget = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Custos Diretos
    direct_material_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    direct_labor_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    other_direct_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_direct_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Custos Indiretos (alocados via ABC)
    allocated_overhead = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    allocated_activity_cost = Column(
        Numeric(18, 2), default=Decimal("0"), nullable=False
    )
    total_indirect_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Custo Total
    total_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    cost_budget = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    cost_variance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Margens
    gross_margin = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    gross_margin_percent = Column(Numeric(8, 4), default=Decimal("0"), nullable=False)
    contribution_margin = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    contribution_margin_percent = Column(
        Numeric(8, 4), default=Decimal("0"), nullable=False
    )
    net_margin = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    net_margin_percent = Column(Numeric(8, 4), default=Decimal("0"), nullable=False)

    # Rentabilidade
    profitability_level = Column(
        Enum(ProfitabilityLevel, name="profitabilitylevel", create_type=True),
        nullable=True,
    )
    profitability_score = Column(Numeric(5, 2), nullable=True)  # 0-100

    # Custo unitário
    unit_cost = Column(Numeric(18, 6), default=Decimal("0"), nullable=False)
    unit_price = Column(Numeric(18, 6), default=Decimal("0"), nullable=False)
    quantity = Column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    unit_of_measure = Column(String(20), nullable=True)

    # Detalhamento de custos
    cost_breakdown = Column(JSONB, nullable=True)
    # Ex: [{"category": "material", "amount": 1000, "percent": 40}]

    # Atividades consumidas
    activities_consumed = Column(JSONB, nullable=True)
    # Ex: [{"activity_id": "uuid", "quantity": 10, "cost": 500}]

    # Drivers consumidos
    drivers_consumed = Column(JSONB, nullable=True)
    # Ex: [{"driver_id": "uuid", "quantity": 5, "unit_cost": 10}]

    # Estatísticas
    allocations_count = Column(Integer, default=0, nullable=False)
    last_cost_update = Column(DateTime(timezone=True), nullable=True)

    # Período
    reference_period = Column(String(7), nullable=True)  # "2024-01"
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Responsável
    owner_id = Column(UUID(as_uuid=True), nullable=True)
    owner_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    # Flags
    is_strategic = Column(Boolean, default=False, nullable=False)
    requires_analysis = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)

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
    parent: Optional["CostObject"] = relationship(
        "CostObject",
        remote_side="CostObject.id",
        back_populates="children",
    )
    children: list["CostObject"] = relationship(
        "CostObject",
        back_populates="parent",
        lazy="dynamic",
    )
    allocations: list["CostAllocation"] = relationship(
        "CostAllocation",
        back_populates="cost_object",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostObject {self.code} - {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se o objeto está ativo."""
        return self.status == CostObjectStatus.ACTIVE and self.active

    @property
    def is_profitable(self) -> bool:
        """Verifica se é rentável."""
        return self.net_margin > 0

    @property
    def cost_variance_percent(self) -> Decimal:
        """Calcula variação percentual do custo."""
        if self.cost_budget == 0:
            return Decimal("0")
        return (self.cost_variance / self.cost_budget) * 100

    def calculate_margins(self) -> None:
        """Calcula todas as margens."""
        # Custo total
        self.total_direct_cost = (
            self.direct_material_cost + self.direct_labor_cost + self.other_direct_cost
        )
        self.total_indirect_cost = (
            self.allocated_overhead + self.allocated_activity_cost
        )
        self.total_cost = self.total_direct_cost + self.total_indirect_cost

        # Margem bruta (receita - custo direto)
        self.gross_margin = self.revenue - self.total_direct_cost
        if self.revenue > 0:
            self.gross_margin_percent = (self.gross_margin / self.revenue) * 100
        else:
            self.gross_margin_percent = Decimal("0")

        # Margem de contribuição
        self.contribution_margin = self.gross_margin
        if self.revenue > 0:
            self.contribution_margin_percent = (
                self.contribution_margin / self.revenue
            ) * 100
        else:
            self.contribution_margin_percent = Decimal("0")

        # Margem líquida (receita - custo total)
        self.net_margin = self.revenue - self.total_cost
        if self.revenue > 0:
            self.net_margin_percent = (self.net_margin / self.revenue) * 100
        else:
            self.net_margin_percent = Decimal("0")

        # Variação de custo
        self.cost_variance = self.total_cost - self.cost_budget

        # Custo unitário
        if self.quantity > 0:
            self.unit_cost = self.total_cost / self.quantity

        # Classificar rentabilidade
        self._classify_profitability()

    def _classify_profitability(self) -> None:
        """Classifica nível de rentabilidade."""
        margin = self.net_margin_percent

        if margin >= 20:
            self.profitability_level = ProfitabilityLevel.HIGHLY_PROFITABLE
            self.profitability_score = Decimal("90")
        elif margin >= 10:
            self.profitability_level = ProfitabilityLevel.PROFITABLE
            self.profitability_score = Decimal("70")
        elif margin >= 0:
            self.profitability_level = ProfitabilityLevel.MARGINAL
            self.profitability_score = Decimal("50")
        elif margin >= -5:
            self.profitability_level = ProfitabilityLevel.BREAK_EVEN
            self.profitability_score = Decimal("30")
        else:
            self.profitability_level = ProfitabilityLevel.UNPROFITABLE
            self.profitability_score = Decimal("10")

    def add_direct_cost(
        self, material: Decimal = None, labor: Decimal = None, other: Decimal = None
    ) -> None:
        """Adiciona custos diretos."""
        if material:
            self.direct_material_cost += material
        if labor:
            self.direct_labor_cost += labor
        if other:
            self.other_direct_cost += other
        self.calculate_margins()

    def add_allocated_cost(
        self, overhead: Decimal = None, activity: Decimal = None
    ) -> None:
        """Adiciona custos alocados (indiretos)."""
        if overhead:
            self.allocated_overhead += overhead
        if activity:
            self.allocated_activity_cost += activity
        self.calculate_margins()
        self.allocations_count += 1
        self.last_cost_update = datetime.utcnow()
