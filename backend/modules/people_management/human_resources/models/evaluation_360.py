"""
Models para Avaliação 360° persistente.

Tabelas:
    - evaluation_360_cycles: Ciclos de avaliação 360°
    - evaluation_360_responses: Respostas individuais dos avaliadores
"""

import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base, TimestampMixin


class EvaluatorType(StrEnum):
    """Tipo de avaliador na avaliação 360°."""

    SELF = "self"
    MANAGER = "manager"
    PEER = "peer"
    SUBORDINATE = "subordinate"
    CLIENT = "client"


class EvaluationStatus(StrEnum):
    """Status do ciclo de avaliação."""

    DRAFT = "draft"
    COLLECTING = "collecting"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Evaluation360Cycle(Base, TimestampMixin):
    """Ciclo de avaliação 360° de um funcionário."""

    __tablename__ = "evaluation_360_cycles"
    __table_args__ = (
        Index("idx_eval360_employee", "employee_id"),
        Index("idx_eval360_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    employee_name: Mapped[str] = mapped_column(nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[EvaluationStatus] = mapped_column(
        Enum(EvaluationStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=EvaluationStatus.DRAFT,
    )
    weights: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Resultado completo calculado",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    responses: Mapped[list["Evaluation360Response"]] = relationship(
        back_populates="cycle",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Evaluation360Cycle(id={self.id}, employee={self.employee_name}, status={self.status})>"


class Evaluation360Response(Base, TimestampMixin):
    """Resposta individual de um avaliador no ciclo 360°."""

    __tablename__ = "evaluation_360_responses"
    __table_args__ = (
        Index("idx_eval360resp_cycle", "cycle_id"),
        Index("idx_eval360resp_evaluator", "evaluator_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evaluation_360_cycles.id", ondelete="CASCADE"),
        nullable=False,
    )
    evaluator_id: Mapped[str] = mapped_column(nullable=False)
    evaluator_type: Mapped[EvaluatorType] = mapped_column(
        Enum(EvaluatorType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    evaluator_name: Mapped[str] = mapped_column(nullable=False)
    scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    comments: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    cycle: Mapped[Evaluation360Cycle] = relationship(back_populates="responses")

    def __repr__(self) -> str:
        return f"<Evaluation360Response(evaluator={self.evaluator_name}, type={self.evaluator_type})>"
