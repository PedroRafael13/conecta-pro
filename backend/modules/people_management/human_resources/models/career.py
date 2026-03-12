"""
Model para Plano de Carreira.

Implementa a tabela de planos de carreira dos funcionarios,
com niveis hierarquicos, metas (milestones) e acompanhamento.

Tabela:
    - career_plans: Planos de carreira
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    DateTime,
    Enum,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base, TimestampMixin


class CareerLevel(StrEnum):
    """Niveis de carreira na empresa."""

    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    MANAGER = "manager"
    DIRECTOR = "director"


class CareerPlanStatus(StrEnum):
    """Status do plano de carreira."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class CareerPlan(Base, TimestampMixin):
    """
    Plano de carreira de funcionario.

    Registra o plano de desenvolvimento de carreira com posicao
    atual, posicao alvo, milestones e acompanhamento por mentor.

    Atributos:
        id: Identificador unico do plano
        employee_id: ID do funcionario
        current_position: Cargo atual
        target_position: Cargo alvo
        current_level: Nivel atual na hierarquia
        target_level: Nivel alvo na hierarquia
        estimated_timeline_months: Tempo estimado em meses
        status: Status do plano
        milestones: Lista de marcos/metas (JSON)
        mentor_id: ID do mentor (nullable)
        started_at: Data de inicio do plano
        completed_at: Data de conclusao
    """

    __tablename__ = "career_plans"
    __table_args__ = (
        Index("idx_career_plan_employee", "employee_id"),
        Index("idx_career_plan_status", "status"),
        Index("idx_career_plan_mentor", "mentor_id"),
        Index("idx_career_plan_levels", "current_level", "target_level"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Posicoes
    current_position: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    target_position: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    # Niveis
    current_level: Mapped[CareerLevel] = mapped_column(
        Enum(CareerLevel),
        nullable=False,
    )
    target_level: Mapped[CareerLevel] = mapped_column(
        Enum(CareerLevel),
        nullable=False,
    )

    # Timeline
    estimated_timeline_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=12,
        comment="Tempo estimado em meses para atingir o objetivo",
    )

    # Status
    status: Mapped[CareerPlanStatus] = mapped_column(
        Enum(CareerPlanStatus),
        nullable=False,
        default=CareerPlanStatus.ACTIVE,
    )

    # Milestones
    milestones: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Lista de marcos: [{title, description, target_date, completed, completed_at}]",
    )

    # Mentor
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Datas
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<CareerPlan(id={self.id}, "
            f"employee={self.employee_id}, "
            f"{self.current_position} -> {self.target_position})>"
        )

    @property
    def is_active(self) -> bool:
        """Verifica se o plano esta ativo."""
        return self.status == CareerPlanStatus.ACTIVE

    @property
    def completed_milestones_count(self) -> int:
        """Conta milestones concluidos."""
        if not self.milestones:
            return 0
        return sum(1 for m in self.milestones if m.get("completed", False))

    @property
    def total_milestones_count(self) -> int:
        """Conta total de milestones."""
        if not self.milestones:
            return 0
        return len(self.milestones)

    @property
    def progress_percentage(self) -> float:
        """Calcula percentual de progresso baseado nos milestones."""
        total = self.total_milestones_count
        if total == 0:
            return 0.0
        return round((self.completed_milestones_count / total) * 100, 1)
