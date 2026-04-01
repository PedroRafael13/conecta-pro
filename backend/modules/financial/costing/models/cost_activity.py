"""Cost Activity model - Atividades ABC."""

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
    from modules.financial.costing.models.cost_driver import CostDriver
    from modules.financial.costing.models.cost_pool import CostPool


class ActivityType(StrEnum):
    """Tipo de atividade."""

    PRIMARY = "PRIMARY"  # Atividade primária (agrega valor)
    SUPPORT = "SUPPORT"  # Atividade de suporte
    ADMINISTRATIVE = "ADMINISTRATIVE"  # Administrativa
    QUALITY = "QUALITY"  # Qualidade/Inspeção
    LOGISTICS = "LOGISTICS"  # Logística
    MAINTENANCE = "MAINTENANCE"  # Manutenção
    SETUP = "SETUP"  # Preparação/Setup
    IDLE = "IDLE"  # Ociosidade
    REWORK = "REWORK"  # Retrabalho
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"  # Atendimento ao cliente


class ActivityLevel(StrEnum):
    """Nível hierárquico da atividade (ABC)."""

    UNIT = "UNIT"  # Por unidade produzida
    BATCH = "BATCH"  # Por lote
    PRODUCT = "PRODUCT"  # Por produto/serviço
    CUSTOMER = "CUSTOMER"  # Por cliente
    FACILITY = "FACILITY"  # Por instalação/estrutura


class ActivityStatus(StrEnum):
    """Status da atividade."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class ValueAddedType(StrEnum):
    """Classificação de valor agregado."""

    VALUE_ADDED = "VALUE_ADDED"  # Agrega valor ao cliente
    NON_VALUE_ADDED = "NON_VALUE_ADDED"  # Não agrega valor (candidata a eliminação)
    BUSINESS_VALUE = "BUSINESS_VALUE"  # Necessária ao negócio (não ao cliente)


class CostActivity(Base):
    """Atividade de Custo - base do custeio ABC (Activity-Based Costing)."""

    __tablename__ = "fin_cost_activities"
    __table_args__ = (UniqueConstraint("condominio_id", "code", name="uq_cost_activity_code"),)

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
        ForeignKey("fin_cost_activities.id"),
        nullable=True,
        index=True,
    )

    # Pool de Custo associado
    cost_pool_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_pools.id"),
        nullable=True,
        index=True,
    )

    # Direcionador primário
    primary_driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_drivers.id"),
        nullable=True,
        index=True,
    )

    # Centro de Custo
    cost_center_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_centers.id"),
        nullable=True,
        index=True,
    )

    # Identificação
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    short_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    # Classificação
    activity_type = Column(
        Enum(ActivityType, name="activitytype", create_type=True),
        nullable=False,
        default=ActivityType.PRIMARY,
    )
    activity_level = Column(
        Enum(ActivityLevel, name="activitylevel", create_type=True),
        nullable=False,
        default=ActivityLevel.UNIT,
    )
    status = Column(
        Enum(ActivityStatus, name="activitystatus", create_type=True),
        nullable=False,
        default=ActivityStatus.ACTIVE,
    )
    value_added_type = Column(
        Enum(ValueAddedType, name="valueaddedtype", create_type=True),
        nullable=False,
        default=ValueAddedType.VALUE_ADDED,
    )

    # Hierarquia
    level = Column(Integer, default=1, nullable=False)
    path = Column(String(300), nullable=True)
    order_index = Column(Integer, nullable=True)

    # Custos
    total_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    fixed_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    variable_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    allocated_cost = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Taxa da atividade
    activity_rate = Column(Numeric(18, 6), default=Decimal("0"), nullable=False)
    rate_currency = Column(String(3), default="BRL", nullable=False)

    # Capacidade
    practical_capacity = Column(Numeric(18, 4), nullable=True)
    used_capacity = Column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    capacity_unit = Column(String(20), nullable=True)

    # Tempo
    standard_time = Column(Numeric(10, 4), nullable=True)  # Tempo padrão em horas
    actual_time = Column(Numeric(10, 4), nullable=True)  # Tempo real em horas
    time_variance = Column(Numeric(10, 4), nullable=True)  # Variação

    # Frequência
    execution_frequency = Column(String(20), default="CONTINUOUS", nullable=False)
    executions_count = Column(Integer, default=0, nullable=False)
    last_execution_at = Column(DateTime(timezone=True), nullable=True)

    # Recursos consumidos
    resources_consumed = Column(JSONB, nullable=True)
    # Ex: [{"resource": "energia", "quantity": 100, "unit": "kWh"}]

    # Outputs
    outputs_produced = Column(JSONB, nullable=True)
    # Ex: [{"output": "relatório", "quantity": 50, "unit": "un"}]

    # Direcionadores secundários
    secondary_drivers = Column(JSONB, nullable=True)
    # Ex: [{"driver_id": "uuid", "weight": 0.3}]

    # Benchmarks
    benchmark_cost = Column(Numeric(18, 2), nullable=True)
    benchmark_time = Column(Numeric(10, 4), nullable=True)
    benchmark_source = Column(String(100), nullable=True)

    # Processo
    process_name = Column(String(100), nullable=True)
    subprocess_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    responsible_id = Column(UUID(as_uuid=True), nullable=True)
    responsible_name = Column(String(100), nullable=True)

    # Período
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    reference_period = Column(String(7), nullable=True)  # "2024-01"

    # Flags
    is_core = Column(Boolean, default=False, nullable=False)  # Atividade essencial
    is_outsourceable = Column(Boolean, default=False, nullable=False)  # Terceirizável
    is_automatable = Column(Boolean, default=False, nullable=False)  # Automatizável
    requires_approval = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)
    extra_metadata = Column(JSONB, nullable=True)

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
    parent: Optional["CostActivity"] = relationship(
        "CostActivity",
        remote_side="CostActivity.id",
        back_populates="children",
    )
    children: list["CostActivity"] = relationship(
        "CostActivity",
        back_populates="parent",
        lazy="dynamic",
    )
    cost_pool: Optional["CostPool"] = relationship(
        "CostPool",
        back_populates="activities",
    )
    primary_driver: Optional["CostDriver"] = relationship(
        "CostDriver",
        back_populates="activities",
        foreign_keys=[primary_driver_id],
    )
    # allocations: Relacionamento desabilitado temporariamente devido a FK ambígua
    # allocations: list["CostAllocation"] = relationship(
    #     "CostAllocation",
    #     back_populates="activity",
    #     foreign_keys="[CostAllocation.activity_id]",
    #     lazy="dynamic",
    # )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostActivity {self.code} - {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se a atividade está ativa."""
        return self.status == ActivityStatus.ACTIVE and self.active

    @property
    def is_value_adding(self) -> bool:
        """Verifica se agrega valor."""
        return self.value_added_type == ValueAddedType.VALUE_ADDED

    @property
    def capacity_usage_percent(self) -> Decimal:
        """Calcula percentual de uso da capacidade."""
        if not self.practical_capacity or self.practical_capacity == 0:
            return Decimal("0")
        return (self.used_capacity / self.practical_capacity) * 100

    @property
    def idle_capacity(self) -> Decimal:
        """Calcula capacidade ociosa."""
        if not self.practical_capacity:
            return Decimal("0")
        return max(Decimal("0"), self.practical_capacity - self.used_capacity)

    @property
    def time_efficiency(self) -> Decimal:
        """Calcula eficiência de tempo."""
        if not self.actual_time or self.actual_time == 0:
            return Decimal("100")
        if not self.standard_time:
            return Decimal("100")
        return (self.standard_time / self.actual_time) * 100

    @property
    def cost_variance(self) -> Decimal:
        """Calcula variação de custo vs benchmark."""
        if not self.benchmark_cost:
            return Decimal("0")
        return self.total_cost - self.benchmark_cost

    def calculate_rate(self) -> Decimal:
        """Calcula taxa da atividade."""
        if not self.used_capacity or self.used_capacity == 0:
            return Decimal("0")
        return self.total_cost / self.used_capacity

    def allocate_cost(self, quantity: Decimal) -> Decimal:
        """Calcula custo alocado baseado na quantidade."""
        return quantity * self.activity_rate

    def update_capacity(self, used: Decimal) -> None:
        """Atualiza capacidade utilizada."""
        self.used_capacity += used
        self.executions_count += 1
        self.last_execution_at = datetime.utcnow()
