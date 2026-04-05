"""
Schemas Pydantic v2 para Avaliacao de Desempenho.

Define schemas de criacao, atualizacao, resposta e listagem
para avaliacoes de desempenho.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.people_management.human_resources.models.performance import (
    ReviewStatus,
    ReviewType,
)


class ScoresBreakdown(BaseModel):
    """Schema para scores por dimensao de desempenho."""

    punctuality: float = Field(0.0, ge=0, le=100, description="Pontualidade")
    quality: float = Field(0.0, ge=0, le=100, description="Qualidade do trabalho")
    initiative: float = Field(0.0, ge=0, le=100, description="Iniciativa e proatividade")
    teamwork: float = Field(0.0, ge=0, le=100, description="Trabalho em equipe")
    leadership: float = Field(0.0, ge=0, le=100, description="Lideranca")


class GoalItem(BaseModel):
    """Schema para meta do proximo periodo."""

    title: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    target_date: date | None = None
    metric: str | None = None


class PerformanceReviewBase(BaseModel):
    """Schema base para avaliacao de desempenho."""

    employee_id: UUID
    reviewer_id: UUID
    review_period_start: date
    review_period_end: date
    type: ReviewType = ReviewType.QUARTERLY


class PerformanceReviewCreate(PerformanceReviewBase):
    """Schema para criacao de avaliacao de desempenho."""

    scores_breakdown: ScoresBreakdown | None = None
    strengths: str | None = None
    improvements: str | None = None
    goals_next_period: list[GoalItem] | None = Field(default_factory=list)
    reviewer_comments: str | None = None


class PerformanceReviewUpdate(BaseModel):
    """Schema para atualizacao de avaliacao de desempenho."""

    status: ReviewStatus | None = None
    overall_score: float | None = Field(None, ge=0, le=100)
    scores_breakdown: ScoresBreakdown | None = None
    strengths: str | None = None
    improvements: str | None = None
    goals_next_period: list[GoalItem] | None = None
    employee_comments: str | None = None
    reviewer_comments: str | None = None
    calibrated_score: float | None = Field(None, ge=0, le=100)


class PerformanceReviewResponse(BaseModel):
    """Schema de resposta para avaliacao de desempenho."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    reviewer_id: UUID
    employee_name: str | None = None
    reviewer_name: str | None = None
    review_period_start: date
    review_period_end: date
    type: ReviewType
    status: ReviewStatus
    overall_score: float | None = None
    scores_breakdown: dict | None = None
    strengths: str | None = None
    improvements: str | None = None
    goals_next_period: list | None = None
    employee_comments: str | None = None
    reviewer_comments: str | None = None
    calibrated_score: float | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @property
    def final_score(self) -> float | None:
        """Retorna score final (calibrado ou geral)."""
        return self.calibrated_score if self.calibrated_score is not None else self.overall_score

    @property
    def score_classification(self) -> str | None:
        """Classifica o score final."""
        score = self.final_score
        if score is None:
            return None
        if score >= 90:
            return "excepcional"
        if score >= 75:
            return "acima_esperado"
        if score >= 60:
            return "esperado"
        if score >= 40:
            return "abaixo_esperado"
        return "insatisfatorio"


class PerformanceReviewListResponse(BaseModel):
    """Schema de listagem de avaliacoes de desempenho."""

    items: list[PerformanceReviewResponse]
    total: int
    page: int = 1
    page_size: int = 20
