"""Schemas para Application."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.application import (
    ApplicationStatus,
    RejectionReason,
)


class ApplicationBase(BaseModel):
    """Schema base para Application."""

    cover_letter: str | None = None
    screening_answers: list[dict] | None = Field(default_factory=list)
    referral_employee_id: str | None = None
    referral_notes: str | None = None


class ApplicationCreate(ApplicationBase):
    """Schema para criação de candidatura."""

    job_position_id: str
    candidate_id: str
    created_by: str | None = None


class ApplicationUpdate(BaseModel):
    """Schema para atualização de candidatura."""

    status: ApplicationStatus | None = None
    current_stage: int | None = None
    current_stage_name: str | None = None
    matching_score: int | None = Field(None, ge=0, le=100)
    interview_score: int | None = Field(None, ge=0, le=100)
    test_score: int | None = Field(None, ge=0, le=100)
    is_favorite: bool | None = None
    is_shortlisted: bool | None = None
    recruiter_notes: str | None = None
    hiring_manager_notes: str | None = None
    feedback: str | None = None
    assigned_recruiter_id: str | None = None


class ApplicationResponse(ApplicationBase):
    """Schema de resposta para candidatura."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    job_position_id: str
    candidate_id: str
    status: ApplicationStatus
    current_stage: int
    current_stage_name: str | None = None
    matching_score: int = 0
    interview_score: int | None = None
    test_score: int | None = None
    final_score: int | None = None
    ranking_position: int | None = None
    is_favorite: bool = False
    is_shortlisted: bool = False
    status_history: list[dict] | None = None
    recruiter_notes: str | None = None
    hiring_manager_notes: str | None = None
    feedback: str | None = None
    rejection_reason: RejectionReason | None = None
    rejection_details: str | None = None
    rejected_at: datetime | None = None
    proposal_sent_at: datetime | None = None
    proposal_amount: int | None = None
    proposal_accepted: bool | None = None
    hired_at: datetime | None = None
    start_date: datetime | None = None
    applied_at: datetime
    last_update_at: datetime | None = None
    viewed_at: datetime | None = None
    assigned_recruiter_id: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    is_active: bool
    is_in_process: bool
    is_hired: bool
    is_rejected: bool
    days_in_process: int


class ApplicationListResponse(BaseModel):
    """Schema de lista de candidaturas."""

    items: list[ApplicationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ApplicationFilter(BaseModel):
    """Schema para filtro de candidaturas."""

    job_position_id: str | None = None
    candidate_id: str | None = None
    status: ApplicationStatus | None = None
    is_favorite: bool | None = None
    is_shortlisted: bool | None = None
    min_score: int | None = None
    max_score: int | None = None
    assigned_recruiter_id: str | None = None
    applied_after: datetime | None = None
    applied_before: datetime | None = None


class ApplicationStats(BaseModel):
    """Estatísticas de candidaturas."""

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
    """Schema para avançar candidatura."""

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
    """Schema para contratação."""

    start_date: datetime
    final_salary: int = Field(..., gt=0)
    position_id: str | None = None
    notes: str | None = None


class ApplicationBulkAction(BaseModel):
    """Schema para ação em lote."""

    application_ids: list[str]
    action: str
    notes: str | None = None
