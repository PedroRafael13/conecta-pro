"""Cost Driver model - Direcionadores de Custo ABC."""

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
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


class DriverType(str, enum.Enum):
    """Tipo do direcionador de custo."""

    TRANSACTION = "TRANSACTION"  # Baseado em transações (qtd pedidos, entregas)
    DURATION = "DURATION"  # Baseado em tempo (horas, minutos)
    INTENSITY = "INTENSITY"  # Baseado em intensidade/esforço
    VOLUME = "VOLUME"  # Baseado em volume (m³, kg, unidades)
    HEADCOUNT = "HEADCOUNT"  # Baseado em número de funcionários
    AREA = "AREA"  # Baseado em área (m²)
    REVENUE = "REVENUE"  # Baseado em receita
    CONSUMPTION = "CONSUMPTION"  # Baseado em consumo (energia, materiais)
    EQUIPMENT = "EQUIPMENT"  # Baseado em uso de equipamento (horas máquina)
    CUSTOM = "CUSTOM"  # Personalizado


class DriverCategory(str, enum.Enum):
    """Categoria do direcionador."""

    RESOURCE = "RESOURCE"  # Direcionador de recurso (1º estágio ABC)
    ACTIVITY = "ACTIVITY"  # Direcionador de atividade (2º estágio ABC)
    COST_OBJECT = "COST_OBJECT"  # Direcionador para objeto de custo


class DriverStatus(str, enum.Enum):
    """Status do direcionador."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"


class DriverMeasureUnit(str, enum.Enum):
    """Unidade de medida do direcionador."""

    QUANTITY = "QUANTITY"  # Quantidade (unidades)
    HOURS = "HOURS"  # Horas
    MINUTES = "MINUTES"  # Minutos
    DAYS = "DAYS"  # Dias
    SQUARE_METERS = "SQUARE_METERS"  # m²
    CUBIC_METERS = "CUBIC_METERS"  # m³
    KILOGRAMS = "KILOGRAMS"  # kg
    LITERS = "LITERS"  # Litros
    KILOMETERS = "KILOMETERS"  # km
    CURRENCY = "CURRENCY"  # Valor monetário
    PERCENTAGE = "PERCENTAGE"  # Percentual
    HEADCOUNT = "HEADCOUNT"  # Número de pessoas


class CostDriver(Base):
    """Direcionador de Custo - base do custeio ABC."""

    __tablename__ = "fin_cost_drivers"
    __table_args__ = (
        UniqueConstraint("condominio_id", "code", name="uq_cost_driver_code"),
    )

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificação
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Classificação
    driver_type = Column(
        Enum(DriverType, name="drivertype", create_type=True),
        nullable=False,
        default=DriverType.TRANSACTION,
    )
    driver_category = Column(
        Enum(DriverCategory, name="drivercategory", create_type=True),
        nullable=False,
        default=DriverCategory.ACTIVITY,
    )
    status = Column(
        Enum(DriverStatus, name="driverstatus", create_type=True),
        nullable=False,
        default=DriverStatus.ACTIVE,
    )

    # Unidade de Medida
    measure_unit = Column(
        Enum(DriverMeasureUnit, name="drivermeasureunit", create_type=True),
        nullable=False,
        default=DriverMeasureUnit.QUANTITY,
    )
    measure_symbol = Column(String(10), nullable=True)  # Ex: "h", "m²", "kg"

    # Taxa/Custo unitário
    unit_cost = Column(Numeric(18, 6), default=Decimal("0"), nullable=False)
    unit_cost_currency = Column(String(3), default="BRL", nullable=False)

    # Capacidade
    practical_capacity = Column(Numeric(18, 4), nullable=True)  # Capacidade prática
    theoretical_capacity = Column(Numeric(18, 4), nullable=True)  # Capacidade teórica
    used_capacity = Column(Numeric(18, 4), default=Decimal("0"), nullable=False)

    # Fórmula personalizada (para CUSTOM)
    custom_formula = Column(Text, nullable=True)  # Ex: "hours * complexity_factor"
    formula_variables = Column(JSONB, nullable=True)  # {"complexity_factor": 1.5}

    # Frequência de atualização
    update_frequency = Column(String(20), default="MONTHLY", nullable=False)
    last_rate_update = Column(DateTime(timezone=True), nullable=True)
    next_rate_update = Column(DateTime(timezone=True), nullable=True)

    # Histórico de taxas
    rate_history = Column(JSONB, nullable=True)  # [{"date": "2024-01", "rate": 10.5}]

    # Fonte de dados
    data_source = Column(String(100), nullable=True)  # Ex: "sistema_ponto", "erp"
    source_table = Column(String(100), nullable=True)
    source_field = Column(String(100), nullable=True)
    is_automated = Column(Boolean, default=False, nullable=False)

    # Validação
    min_value = Column(Numeric(18, 4), nullable=True)
    max_value = Column(Numeric(18, 4), nullable=True)
    requires_validation = Column(Boolean, default=False, nullable=False)

    # Estatísticas
    total_allocations = Column(Integer, default=0, nullable=False)
    total_allocated_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    average_rate = Column(Numeric(18, 6), default=Decimal("0"), nullable=False)

    # Flags
    is_primary = Column(Boolean, default=False, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)  # ["fixo", "operacional"]

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
    activities: list["CostActivity"] = relationship(
        "CostActivity",
        back_populates="primary_driver",
        foreign_keys="CostActivity.primary_driver_id",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostDriver {self.code} - {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se o direcionador está ativo."""
        return self.status == DriverStatus.ACTIVE and self.active

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
    def idle_capacity_cost(self) -> Decimal:
        """Calcula custo da capacidade ociosa."""
        return self.idle_capacity * self.unit_cost

    def calculate_allocation(self, quantity: Decimal) -> Decimal:
        """Calcula valor de alocação baseado na quantidade."""
        return quantity * self.unit_cost

    def update_statistics(
        self, allocation_count: int, allocated_amount: Decimal
    ) -> None:
        """Atualiza estatísticas do direcionador."""
        self.total_allocations += allocation_count
        self.total_allocated_amount += allocated_amount
        if self.total_allocations > 0:
            self.average_rate = self.total_allocated_amount / self.total_allocations

    def add_rate_history(self, rate: Decimal, period: str) -> None:
        """Adiciona taxa ao histórico."""
        if self.rate_history is None:
            self.rate_history = []
        self.rate_history.append(
            {
                "period": period,
                "rate": str(rate),
                "recorded_at": datetime.utcnow().isoformat(),
            }
        )
