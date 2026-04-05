"""
Schemas Pydantic v2 para Plano de Carreira.

Define schemas de criacao, atualizacao, resposta e listagem
para planos de carreira e milestones.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.people_management.human_resources.models.career import (
    CareerLevel,
    CareerPlanStatus,
)


class MilestoneCreate(BaseModel):
    """Schema para criacao de milestone no plano de carreira."""

    title: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    target_date: date | None = None


class MilestoneUpdate(BaseModel):
    """Schema para atualizacao de milestone."""

    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = None
    target_date: date | None = None
    completed: bool | None = None


class MilestoneResponse(BaseModel):
    """Schema de resposta para milestone."""

    title: str
    description: str | None = None
    target_date: date | None = None
    completed: bool = False
    completed_at: datetime | None = None


class CareerPlanBase(BaseModel):
    """Schema base para plano de carreira."""

    employee_id: UUID
    current_position: str = Field(..., min_length=2, max_length=200)
    target_position: str = Field(..., min_length=2, max_length=200)
    current_level: CareerLevel
    target_level: CareerLevel
    estimated_timeline_months: int = Field(12, gt=0, le=120)
    mentor_id: UUID | None = None


class CareerPlanCreate(CareerPlanBase):
    """Schema para criacao de plano de carreira."""

    milestones: list[MilestoneCreate] | None = Field(default_factory=list)


class CareerPlanUpdate(BaseModel):
    """Schema para atualizacao de plano de carreira."""

    current_position: str | None = Field(None, min_length=2, max_length=200)
    target_position: str | None = Field(None, min_length=2, max_length=200)
    current_level: CareerLevel | None = None
    target_level: CareerLevel | None = None
    estimated_timeline_months: int | None = Field(None, gt=0, le=120)
    status: CareerPlanStatus | None = None
    mentor_id: UUID | None = None
    milestones: list[MilestoneCreate] | None = None


class CareerPlanResponse(BaseModel):
    """Schema de resposta para plano de carreira."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    employee_name: str | None = None
    current_position: str
    target_position: str
    current_level: CareerLevel
    target_level: CareerLevel
    estimated_timeline_months: int
    status: CareerPlanStatus
    milestones: list[MilestoneResponse] | None = None
    mentor_id: UUID | None = None
    started_at: datetime
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @property
    def progress_percentage(self) -> float:
        """Calcula percentual de progresso."""
        if not self.milestones:
            return 0.0
        total = len(self.milestones)
        completed = sum(1 for m in self.milestones if m.completed)
        return round((completed / total) * 100, 1) if total > 0 else 0.0


class CareerPlanListResponse(BaseModel):
    """Schema de listagem de planos de carreira."""

    items: list[CareerPlanResponse]
    total: int
    page: int = 1
    page_size: int = 20
