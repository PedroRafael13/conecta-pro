"""Schemas para Interview."""

from datetime import datetime, date, time
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from modules.recruitment.models.interview import (
    InterviewType,
    InterviewStatus,
    InterviewResult,
)


class InterviewBase(BaseModel):
    """Schema base para Interview."""

    interview_type: InterviewType = InterviewType.VIDEO
    scheduled_date: date
    scheduled_time: time
    duration_minutes: int = Field(default=60, ge=15, le=480)
    timezone: str = "America/Sao_Paulo"
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    interviewer_ids: Optional[List[str]] = Field(default_factory=list)
    interviewer_names: Optional[List[str]] = Field(default_factory=list)
    lead_interviewer_id: Optional[str] = None
    script: Optional[str] = None
    questions: Optional[List[dict]] = Field(default_factory=list)
    competencies_to_assess: Optional[List[str]] = Field(default_factory=list)


class InterviewCreate(InterviewBase):
    """Schema para criação de entrevista."""

    application_id: str
    created_by: Optional[str] = None


class InterviewUpdate(BaseModel):
    """Schema para atualização de entrevista."""

    interview_type: Optional[InterviewType] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_password: Optional[str] = None
    interviewer_ids: Optional[List[str]] = None
    interviewer_names: Optional[List[str]] = None
    lead_interviewer_id: Optional[str] = None
    script: Optional[str] = None
    questions: Optional[List[dict]] = None
    competencies_to_assess: Optional[List[str]] = None
    internal_notes: Optional[str] = None


class InterviewResponse(InterviewBase):
    """Schema de resposta para entrevista."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    status: InterviewStatus
    result: Optional[InterviewResult] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    score: Optional[int] = None
    evaluation: Optional[dict] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    competency_scores: Optional[dict] = None
    feedback: Optional[str] = None
    recommendation: Optional[str] = None
    internal_notes: Optional[str] = None
    candidate_feedback: Optional[str] = None
    candidate_questions: Optional[List[str]] = None
    candidate_confirmed: bool = False
    candidate_confirmed_at: Optional[datetime] = None
    interviewer_confirmed: bool = False
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    reschedule_count: int = 0
    is_recorded: bool = False
    recording_url: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    scheduled_datetime: datetime
    is_past: bool
    is_today: bool
    is_upcoming: bool
    is_pending_result: bool
    was_successful: bool


class InterviewListResponse(BaseModel):
    """Schema de lista de entrevistas."""

    items: List[InterviewResponse]
    total: int
    page: int
    page_size: int
    pages: int


class InterviewFilter(BaseModel):
    """Schema para filtro de entrevistas."""

    application_id: Optional[str] = None
    interview_type: Optional[InterviewType] = None
    status: Optional[InterviewStatus] = None
    result: Optional[InterviewResult] = None
    interviewer_id: Optional[str] = None
    scheduled_after: Optional[date] = None
    scheduled_before: Optional[date] = None
    is_today: Optional[bool] = None
    is_upcoming: Optional[bool] = None


class InterviewStats(BaseModel):
    """Estatísticas de entrevistas."""

    total_interviews: int = 0
    scheduled: int = 0
    completed: int = 0
    cancelled: int = 0
    no_show: int = 0
    by_type: dict = Field(default_factory=dict)
    by_result: dict = Field(default_factory=dict)
    avg_score: float = 0
    avg_duration_minutes: float = 0
    approval_rate: float = 0


class InterviewComplete(BaseModel):
    """Schema para completar entrevista."""

    result: InterviewResult
    score: Optional[int] = Field(None, ge=0, le=100)
    feedback: Optional[str] = None
    strengths: Optional[List[str]] = Field(default_factory=list)
    weaknesses: Optional[List[str]] = Field(default_factory=list)
    competency_scores: Optional[dict] = None
    recommendation: Optional[str] = None


class InterviewReschedule(BaseModel):
    """Schema para reagendar entrevista."""

    new_date: date
    new_time: time
    reason: Optional[str] = None
    notify_candidate: bool = True
    notify_interviewers: bool = True


class InterviewCancel(BaseModel):
    """Schema para cancelar entrevista."""

    reason: str = Field(..., min_length=5)
    notify_candidate: bool = True
    notify_interviewers: bool = True


class InterviewEvaluation(BaseModel):
    """Schema para avaliação de entrevista."""

    competency_scores: dict = Field(...)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendation: str
    overall_impression: Optional[str] = None
    culture_fit_score: Optional[int] = Field(None, ge=0, le=100)
    technical_score: Optional[int] = Field(None, ge=0, le=100)
    communication_score: Optional[int] = Field(None, ge=0, le=100)


class InterviewSlot(BaseModel):
    """Schema para slot de entrevista."""

    date: date
    start_time: time
    end_time: time
    interviewer_id: str
    is_available: bool = True


class InterviewCalendar(BaseModel):
    """Schema para calendário de entrevistas."""

    date: date
    interviews: List[InterviewResponse]
    available_slots: List[InterviewSlot]
