"""Schemas para Application."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from modules.recruitment.models.application import (
    ApplicationStatus,
    RejectionReason,
)


class ApplicationBase(BaseModel):
    """Schema base para Application."""

    cover_letter: Optional[str] = None
    screening_answers: Optional[List[dict]] = Field(default_factory=list)
    referral_employee_id: Optional[str] = None
    referral_notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    """Schema para criação de candidatura."""

    job_position_id: str
    candidate_id: str
    created_by: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Schema para atualização de candidatura."""

    status: Optional[ApplicationStatus] = None
    current_stage: Optional[int] = None
    current_stage_name: Optional[str] = None
    matching_score: Optional[int] = Field(None, ge=0, le=100)
    interview_score: Optional[int] = Field(None, ge=0, le=100)
    test_score: Optional[int] = Field(None, ge=0, le=100)
    is_favorite: Optional[bool] = None
    is_shortlisted: Optional[bool] = None
    recruiter_notes: Optional[str] = None
    hiring_manager_notes: Optional[str] = None
    feedback: Optional[str] = None
    assigned_recruiter_id: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    """Schema de resposta para candidatura."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    job_position_id: str
    candidate_id: str
    status: ApplicationStatus
    current_stage: int
    current_stage_name: Optional[str] = None
    matching_score: int = 0
    interview_score: Optional[int] = None
    test_score: Optional[int] = None
    final_score: Optional[int] = None
    ranking_position: Optional[int] = None
    is_favorite: bool = False
    is_shortlisted: bool = False
    status_history: Optional[List[dict]] = None
    recruiter_notes: Optional[str] = None
    hiring_manager_notes: Optional[str] = None
    feedback: Optional[str] = None
    rejection_reason: Optional[RejectionReason] = None
    rejection_details: Optional[str] = None
    rejected_at: Optional[datetime] = None
    proposal_sent_at: Optional[datetime] = None
    proposal_amount: Optional[int] = None
    proposal_accepted: Optional[bool] = None
    hired_at: Optional[datetime] = None
    start_date: Optional[datetime] = None
    applied_at: datetime
    last_update_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    assigned_recruiter_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    is_active: bool
    is_in_process: bool
    is_hired: bool
    is_rejected: bool
    days_in_process: int


class ApplicationListResponse(BaseModel):
    """Schema de lista de candidaturas."""

    items: List[ApplicationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ApplicationFilter(BaseModel):
    """Schema para filtro de candidaturas."""

    job_position_id: Optional[str] = None
    candidate_id: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    is_favorite: Optional[bool] = None
    is_shortlisted: Optional[bool] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    assigned_recruiter_id: Optional[str] = None
    applied_after: Optional[datetime] = None
    applied_before: Optional[datetime] = None


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
    notes: Optional[str] = None


class ApplicationReject(BaseModel):
    """Schema para rejeitar candidatura."""

    reason: RejectionReason
    details: Optional[str] = None
    send_notification: bool = True


class ApplicationProposal(BaseModel):
    """Schema para proposta."""

    amount: int = Field(..., gt=0)
    benefits: Optional[List[str]] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationHire(BaseModel):
    """Schema para contratação."""

    start_date: datetime
    final_salary: int = Field(..., gt=0)
    position_id: Optional[str] = None
    notes: Optional[str] = None


class ApplicationBulkAction(BaseModel):
    """Schema para ação em lote."""

    application_ids: List[str]
    action: str
    notes: Optional[str] = None
