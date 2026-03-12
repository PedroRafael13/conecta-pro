"""
Model para Avaliacao de Desempenho.

Implementa a tabela de avaliacoes de desempenho dos funcionarios,
com suporte a diferentes tipos de avaliacao (mensal, trimestral,
anual, probatorio) e fluxo de aprovacao.

Tabela:
    - performance_reviews: Avaliacoes de desempenho
"""

import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base, TimestampMixin


class ReviewType(StrEnum):
    """Tipos de avaliacao de desempenho."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    PROBATION = "probation"


class ReviewStatus(StrEnum):
    """Status do fluxo de avaliacao."""

    DRAFT = "draft"
    SELF_EVALUATION = "self_evaluation"
    MANAGER_REVIEW = "manager_review"
    CALIBRATION = "calibration"
    COMPLETED = "completed"


class PerformanceReview(Base, TimestampMixin):
    """
    Avaliacao de desempenho de funcionario.

    Registra avaliacoes periodicas com scores por dimensao,
    comentarios de funcionario e gestor, e processo de calibracao.

    Atributos:
        id: Identificador unico da avaliacao
        employee_id: ID do funcionario avaliado
        reviewer_id: ID do avaliador (gestor)
        review_period_start: Inicio do periodo avaliado
        review_period_end: Fim do periodo avaliado
        type: Tipo de avaliacao (mensal, trimestral, anual, probatorio)
        status: Status do fluxo (rascunho, auto-avaliacao, etc)
        overall_score: Score geral de 0 a 100
        scores_breakdown: Scores por dimensao (JSON)
        strengths: Pontos fortes identificados
        improvements: Areas de melhoria
        goals_next_period: Metas para o proximo periodo (JSON)
        employee_comments: Comentarios do funcionario
        reviewer_comments: Comentarios do avaliador
        calibrated_score: Score apos calibracao (nullable)
        completed_at: Data de conclusao da avaliacao
    """

    __tablename__ = "performance_reviews"
    __table_args__ = (
        Index("idx_perf_review_employee", "employee_id"),
        Index("idx_perf_review_reviewer", "reviewer_id"),
        Index("idx_perf_review_status", "status"),
        Index("idx_perf_review_type", "type"),
        Index("idx_perf_review_period", "review_period_start", "review_period_end"),
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
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Periodo
    review_period_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    review_period_end: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Tipo e status
    type: Mapped[ReviewType] = mapped_column(
        Enum(ReviewType),
        nullable=False,
        default=ReviewType.QUARTERLY,
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus),
        nullable=False,
        default=ReviewStatus.DRAFT,
    )

    # Scores
    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Score geral de 0 a 100",
    )
    scores_breakdown: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Scores por dimensao: punctuality, quality, initiative, teamwork, leadership",
    )

    # Qualitativo
    strengths: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Pontos fortes identificados",
    )
    improvements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Areas de melhoria",
    )
    goals_next_period: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Metas para o proximo periodo",
    )

    # Comentarios
    employee_comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    reviewer_comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Calibracao
    calibrated_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Score apos calibracao gerencial",
    )

    # Conclusao
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<PerformanceReview(id={self.id}, "
            f"employee={self.employee_id}, "
            f"type={self.type.value}, status={self.status.value})>"
        )

    @property
    def final_score(self) -> float | None:
        """Retorna o score final (calibrado se disponivel, senao o geral)."""
        return self.calibrated_score if self.calibrated_score is not None else self.overall_score

    @property
    def is_completed(self) -> bool:
        """Verifica se a avaliacao foi concluida."""
        return self.status == ReviewStatus.COMPLETED

    @staticmethod
    def classify_score(score: float) -> str:
        """Classifica o score em faixa de desempenho."""
        if score >= 90:
            return "excepcional"
        if score >= 75:
            return "acima_esperado"
        if score >= 60:
            return "esperado"
        if score >= 40:
            return "abaixo_esperado"
        return "insatisfatorio"
