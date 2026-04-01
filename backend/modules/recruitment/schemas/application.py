"""Schemas para Application.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.application import (
    ApplicationStatus,
    RejectionReason,
)


class ApplicationCreate(BaseModel):
    """Schema para criacao de candidatura."""

    job_position_id: str
    candidate_id: str
    cover_letter: str | None = None
    salary_expectation: Decimal | None = None
    availability_date: date | None = None


class ApplicationUpdate(BaseModel):
    """Schema para atualizacao de candidatura."""

    status: str | None = None
    current_step: str | None = None
    recruiter_notes: str | None = None
    rating: int | None = Field(None, ge=0, le=100)
    assigned_to_id: str | None = None


class ApplicationResponse(BaseModel):
    """Schema de resposta para candidatura."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    job_position_id: str
    candidate_id: str
    status: str | None = None
    current_step: str | None = None
    step_order: int | None = None
    recruiter_notes: str | None = None
    rating: int | None = None
    ai_match_score: Decimal | None = None
    ai_match_details: dict | None = None
    step_history: list | dict | None = None
    cover_letter: str | None = None
    salary_expectation: Decimal | None = None
    availability_date: date | None = None
    applied_at: datetime | None = None
    screened_at: datetime | None = None
    interviewed_at: datetime | None = None
    offered_at: datetime | None = None
    hired_at: datetime | None = None
    rejected_at: datetime | None = None
    withdrawn_at: datetime | None = None
    rejection_reason: str | None = None
    withdrawal_reason: str | None = None
    assigned_to_id: str | None = None
    is_active: bool | None = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApplicationListResponse(BaseModel):
    """Schema de lista de candidaturas."""

    items: list[ApplicationResponse]
    total: int
    skip: int = 0
    limit: int = 20


class ApplicationFilter(BaseModel):
    """Schema para filtro de candidaturas."""

    job_position_id: str | None = None
    candidate_id: str | None = None
    status: ApplicationStatus | None = None
    min_score: int | None = None
    max_score: int | None = None
    assigned_to_id: str | None = None
    applied_after: datetime | None = None
    applied_before: datetime | None = None


class ApplicationStats(BaseModel):
    """Estatisticas de candidaturas."""

    total_applications: int = 0
    active_applications: int = 0
    hired: int = 0
    rejected: int = 0
    in_process: int = 0
    by_status: dict = Field(default_factory=dict)
    by_stage: dict = Field(default_factory=dict)
    avg_time_to_hire_days: float = 0
    avg_score: float = 0
    conversion_rate: float = 0


class ApplicationAdvance(BaseModel):
    """Schema para avancar candidatura."""

    new_status: ApplicationStatus
    notes: str | None = None


class ApplicationReject(BaseModel):
    """Schema para rejeitar candidatura."""

    reason: RejectionReason
    details: str | None = None
    send_notification: bool = True


class ApplicationProposal(BaseModel):
    """Schema para proposta."""

    amount: int = Field(..., gt=0)
    benefits: list[str] | None = Field(default_factory=list)
    start_date: datetime | None = None
    notes: str | None = None


class ApplicationHire(BaseModel):
    """Schema para contratacao."""

    start_date: datetime | None = None
    final_salary: int | None = None
    notes: str | None = None


class ApplicationBulkAction(BaseModel):
    """Schema para acao em lote."""

    application_ids: list[str]
    action: str
    notes: str | None = None
