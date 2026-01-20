"""Cost Allocation model - Registro de Alocações de Custo."""

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
    from modules.financial.costing.models.cost_driver import CostDriver
    from modules.financial.costing.models.cost_object import CostObject
    from modules.financial.costing.models.cost_pool import CostPool


class AllocationType(str, enum.Enum):
    """Tipo de alocação."""

    POOL_TO_ACTIVITY = "POOL_TO_ACTIVITY"  # Pool -> Atividade (1º estágio ABC)
    ACTIVITY_TO_OBJECT = "ACTIVITY_TO_OBJECT"  # Atividade -> Objeto (2º estágio ABC)
    DIRECT = "DIRECT"  # Alocação direta
    OVERHEAD = "OVERHEAD"  # Rateio de overhead
    RECIPROCAL = "RECIPROCAL"  # Alocação recíproca (entre CCs)
    STEP_DOWN = "STEP_DOWN"  # Método step-down/escada
    ADJUSTMENT = "ADJUSTMENT"  # Ajuste
    REVERSAL = "REVERSAL"  # Estorno


class AllocationStatus(str, enum.Enum):
    """Status da alocação."""

    DRAFT = "DRAFT"  # Rascunho
    PENDING = "PENDING"  # Pendente aprovação
    APPROVED = "APPROVED"  # Aprovada
    EXECUTED = "EXECUTED"  # Executada
    REVERSED = "REVERSED"  # Estornada
    CANCELLED = "CANCELLED"  # Cancelada


class AllocationMethod(str, enum.Enum):
    """Método de cálculo da alocação."""

    DRIVER_BASED = "DRIVER_BASED"  # Baseado em direcionador
    PERCENTAGE = "PERCENTAGE"  # Percentual fixo
    PROPORTIONAL = "PROPORTIONAL"  # Proporcional a base
    FIXED_AMOUNT = "FIXED_AMOUNT"  # Valor fixo
    EQUAL_SHARE = "EQUAL_SHARE"  # Divisão igualitária
    WEIGHTED = "WEIGHTED"  # Ponderado
    FORMULA = "FORMULA"  # Fórmula customizada


class CostAllocation(Base):
    """Alocação de Custo - registro de cada alocação realizada."""

    __tablename__ = "fin_cost_allocations"
    __table_args__ = (
        UniqueConstraint(
            "condominio_id",
            "allocation_number",
            name="uq_cost_allocation_number",
        ),
    )

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Número sequencial
    allocation_number = Column(String(30), nullable=False, index=True)

    # Lote de alocação
    batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    batch_sequence = Column(Integer, nullable=True)

    # Origem do Custo
    source_pool_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_pools.id"),
        nullable=True,
        index=True,
    )
    source_activity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_activities.id"),
        nullable=True,
        index=True,
    )
    source_cost_center_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_centers.id"),
        nullable=True,
        index=True,
    )

    # Destino do Custo
    activity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_activities.id"),
        nullable=True,
        index=True,
    )
    cost_object_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_objects.id"),
        nullable=True,
        index=True,
    )
    target_cost_center_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_centers.id"),
        nullable=True,
        index=True,
    )

    # Direcionador usado
    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_cost_drivers.id"),
        nullable=True,
        index=True,
    )

    # Classificação
    allocation_type = Column(
        Enum(AllocationType, name="allocationtype", create_type=True),
        nullable=False,
        default=AllocationType.ACTIVITY_TO_OBJECT,
    )
    status = Column(
        Enum(AllocationStatus, name="allocationstatus", create_type=True),
        nullable=False,
        default=AllocationStatus.DRAFT,
    )
    allocation_method = Column(
        Enum(AllocationMethod, name="allocationmethod_alloc", create_type=True),
        nullable=False,
        default=AllocationMethod.DRIVER_BASED,
    )

    # Descrição
    description = Column(String(200), nullable=True)
    reference = Column(String(100), nullable=True)

    # Valores
    allocated_amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="BRL", nullable=False)

    # Base de cálculo
    driver_quantity = Column(Numeric(18, 6), nullable=True)
    driver_rate = Column(Numeric(18, 6), nullable=True)
    allocation_percentage = Column(Numeric(8, 4), nullable=True)
    allocation_weight = Column(Numeric(8, 4), nullable=True)

    # Fórmula (se FORMULA)
    formula_used = Column(Text, nullable=True)
    formula_variables = Column(JSONB, nullable=True)

    # Período
    reference_period = Column(String(7), nullable=False, index=True)  # "2024-01"
    allocation_date = Column(DateTime(timezone=True), nullable=False)
    effective_date = Column(DateTime(timezone=True), nullable=True)

    # Detalhamento
    cost_components = Column(JSONB, nullable=True)
    # Ex: [{"type": "labor", "amount": 500}, {"type": "overhead", "amount": 300}]

    # Validação
    is_validated = Column(Boolean, default=False, nullable=False)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    validated_by = Column(UUID(as_uuid=True), nullable=True)
    validation_notes = Column(Text, nullable=True)

    # Aprovação
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Execução
    executed_at = Column(DateTime(timezone=True), nullable=True)
    executed_by = Column(UUID(as_uuid=True), nullable=True)

    # Estorno
    is_reversed = Column(Boolean, default=False, nullable=False)
    reversed_at = Column(DateTime(timezone=True), nullable=True)
    reversed_by = Column(UUID(as_uuid=True), nullable=True)
    reversal_reason = Column(Text, nullable=True)
    reversal_allocation_id = Column(UUID(as_uuid=True), nullable=True)

    # Contabilização
    journal_entry_id = Column(UUID(as_uuid=True), nullable=True)
    debit_account_id = Column(UUID(as_uuid=True), nullable=True)
    credit_account_id = Column(UUID(as_uuid=True), nullable=True)
    is_posted = Column(Boolean, default=False, nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)

    # Fonte de dados
    source_document = Column(String(100), nullable=True)
    source_system = Column(String(50), nullable=True)
    external_reference = Column(String(100), nullable=True)

    # Flags
    is_automatic = Column(Boolean, default=False, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
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
    source_pool: Optional["CostPool"] = relationship(
        "CostPool",
        foreign_keys=[source_pool_id],
    )
    activity: Optional["CostActivity"] = relationship(
        "CostActivity",
        foreign_keys=[activity_id],
    )
    cost_object: Optional["CostObject"] = relationship(
        "CostObject",
        back_populates="allocations",
        foreign_keys=[cost_object_id],
    )
    driver: Optional["CostDriver"] = relationship(
        "CostDriver",
        foreign_keys=[driver_id],
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<CostAllocation {self.allocation_number} - {self.allocated_amount}>"

    @property
    def is_draft(self) -> bool:
        """Verifica se está em rascunho."""
        return self.status == AllocationStatus.DRAFT

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == AllocationStatus.PENDING

    @property
    def is_executed(self) -> bool:
        """Verifica se foi executada."""
        return self.status == AllocationStatus.EXECUTED

    @property
    def can_reverse(self) -> bool:
        """Verifica se pode ser estornada."""
        return self.is_executed and not self.is_reversed

    @property
    def calculated_amount(self) -> Decimal:
        """Calcula valor baseado em driver."""
        if self.driver_quantity and self.driver_rate:
            return self.driver_quantity * self.driver_rate
        return self.allocated_amount

    def submit_for_approval(self) -> None:
        """Submete para aprovação."""
        if self.status == AllocationStatus.DRAFT:
            self.status = AllocationStatus.PENDING

    def approve(self, approved_by: str, notes: str = None) -> None:
        """Aprova a alocação."""
        if self.status == AllocationStatus.PENDING:
            self.status = AllocationStatus.APPROVED
            self.approved_at = datetime.utcnow()
            self.approved_by = approved_by
            self.approval_notes = notes

    def execute(self, executed_by: str) -> None:
        """Executa a alocação."""
        if self.status in (AllocationStatus.APPROVED, AllocationStatus.DRAFT):
            self.status = AllocationStatus.EXECUTED
            self.executed_at = datetime.utcnow()
            self.executed_by = executed_by

    def reverse(self, reversed_by: str, reason: str) -> "CostAllocation":
        """Estorna a alocação."""
        if not self.can_reverse:
            raise ValueError("Alocação não pode ser estornada")

        self.is_reversed = True
        self.reversed_at = datetime.utcnow()
        self.reversed_by = reversed_by
        self.reversal_reason = reason
        self.status = AllocationStatus.REVERSED

        # Cria alocação de estorno
        reversal = CostAllocation(
            condominio_id=self.condominio_id,
            allocation_number=f"{self.allocation_number}-REV",
            batch_id=self.batch_id,
            source_pool_id=self.source_pool_id,
            source_activity_id=self.source_activity_id,
            activity_id=self.activity_id,
            cost_object_id=self.cost_object_id,
            driver_id=self.driver_id,
            allocation_type=AllocationType.REVERSAL,
            status=AllocationStatus.EXECUTED,
            allocation_method=self.allocation_method,
            description=f"Estorno: {self.description}",
            allocated_amount=-self.allocated_amount,
            reference_period=self.reference_period,
            allocation_date=datetime.utcnow(),
            reversal_allocation_id=self.id,
            created_by=reversed_by,
        )

        return reversal

    def cancel(self) -> None:
        """Cancela a alocação."""
        if self.status in (AllocationStatus.DRAFT, AllocationStatus.PENDING):
            self.status = AllocationStatus.CANCELLED

    def validate(self, validated_by: str, notes: str = None) -> bool:
        """Valida a alocação."""
        # Verifica se tem destino
        if not self.activity_id and not self.cost_object_id:
            return False

        # Verifica se tem valor
        if self.allocated_amount == 0:
            return False

        self.is_validated = True
        self.validated_at = datetime.utcnow()
        self.validated_by = validated_by
        self.validation_notes = notes

        return True
