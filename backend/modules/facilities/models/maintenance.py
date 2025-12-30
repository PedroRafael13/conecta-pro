"""
Modelo Maintenance (Manutenção) para Facilities.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .area import Area


class MaintenanceType(str, Enum):
    """Tipo de manutenção."""

    PREVENTIVA = "preventiva"  # Manutenção preventiva programada
    CORRETIVA = "corretiva"  # Manutenção corretiva (reparo)
    PREDITIVA = "preditiva"  # Manutenção baseada em análise
    EMERGENCIAL = "emergencial"  # Manutenção de emergência
    MELHORIA = "melhoria"  # Melhoria/upgrade


class MaintenanceStatus(str, Enum):
    """Status da manutenção."""

    PENDING = "pending"  # Pendente/Aguardando
    SCHEDULED = "scheduled"  # Agendada
    IN_PROGRESS = "in_progress"  # Em andamento
    ON_HOLD = "on_hold"  # Pausada
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    VERIFIED = "verified"  # Verificada/Aprovada


class MaintenancePriority(str, Enum):
    """Prioridade da manutenção."""

    LOW = "low"  # Baixa
    MEDIUM = "medium"  # Média
    HIGH = "high"  # Alta
    CRITICAL = "critical"  # Crítica


class Maintenance(Base):
    """
    Modelo de Manutenção.

    Representa uma manutenção programada ou corretiva em uma área.

    Attributes:
        id: Identificador único
        code: Código da manutenção (MNT-001)
        title: Título da manutenção
        description: Descrição detalhada
        maintenance_type: Tipo (preventiva, corretiva, etc)
        status: Status atual
        priority: Prioridade
        area_id: Área associada
        client_id: Cliente associado
        equipment_id: Equipamento específico
        scheduled_date: Data agendada
        started_at: Data/hora de início
        completed_at: Data/hora de conclusão
        deadline: Prazo limite
        assigned_to: Responsável técnico
        team_ids: IDs da equipe
        estimated_hours: Horas estimadas
        actual_hours: Horas reais
        estimated_cost: Custo estimado
        actual_cost: Custo real
        materials_used: Materiais utilizados
        work_performed: Trabalho realizado
        root_cause: Causa raiz (para corretivas)
        preventive_actions: Ações preventivas
        requires_approval: Requer aprovação
        approved_by: Aprovado por
        approved_at: Data aprovação
    """

    __tablename__ = "maintenances"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo, Status e Prioridade
    maintenance_type: Mapped[str] = mapped_column(
        String(50),
        default=MaintenanceType.CORRETIVA.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=MaintenanceStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        default=MaintenancePriority.MEDIUM.value,
        nullable=False,
        index=True,
    )

    # Relacionamentos
    area_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("areas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    equipment_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    service_request_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("service_requests.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Datas e Prazos
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Responsáveis
    assigned_to: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    team_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    requested_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Horas
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Custos
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    labor_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    material_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Detalhes do trabalho
    materials_used: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    work_performed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preventive_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Recorrência (para preventivas)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recurrence_interval: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    next_occurrence: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Aprovação
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Anexos e fotos
    attachments: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    before_photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    after_photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Avaliação
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Relacionamentos
    area: Mapped[Optional["Area"]] = relationship(
        "Area",
        back_populates="maintenances",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Maintenance {self.code} - {self.title}>"

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if not self.deadline:
            return False
        if self.status in (
            MaintenanceStatus.COMPLETED.value,
            MaintenanceStatus.CANCELLED.value,
            MaintenanceStatus.VERIFIED.value,
        ):
            return False
        return date.today() > self.deadline

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status in (
            MaintenanceStatus.PENDING.value,
            MaintenanceStatus.SCHEDULED.value,
        )

    @property
    def is_in_progress(self) -> bool:
        """Verifica se está em andamento."""
        return self.status == MaintenanceStatus.IN_PROGRESS.value

    @property
    def is_completed(self) -> bool:
        """Verifica se está concluída."""
        return self.status in (
            MaintenanceStatus.COMPLETED.value,
            MaintenanceStatus.VERIFIED.value,
        )

    @property
    def cost_variance(self) -> float:
        """Calcula variação de custo (real - estimado)."""
        return self.actual_cost - self.estimated_cost

    @property
    def hours_variance(self) -> float:
        """Calcula variação de horas (real - estimado)."""
        return self.actual_hours - self.estimated_hours

    @property
    def duration_days(self) -> Optional[int]:
        """Calcula duração em dias."""
        if not self.started_at:
            return None
        end = self.completed_at or datetime.now()
        return (end - self.started_at).days

    def calculate_total_cost(self) -> float:
        """Calcula custo total."""
        return self.labor_cost + self.material_cost
