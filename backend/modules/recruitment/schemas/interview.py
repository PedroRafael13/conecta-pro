"""Schemas para Interview."""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.interview import (
    InterviewResult,
    InterviewStatus,
    InterviewType,
)


class InterviewBase(BaseModel):
    """Schema base para Interview."""

    interview_type: InterviewType = InterviewType.VIDEO
    scheduled_date: date
    scheduled_time: time
    duration_minutes: int = Field(default=60, ge=15, le=480)
    timezone: str = "America/Sao_Paulo"
    location: str | None = None
    meeting_link: str | None = None
    meeting_platform: str | None = None
    meeting_id: str | None = None
    meeting_password: str | None = None
    interviewer_ids: list[str] | None = Field(default_factory=list)
    interviewer_names: list[str] | None = Field(default_factory=list)
    lead_interviewer_id: str | None = None
    script: str | None = None
    questions: list[dict] | None = Field(default_factory=list)
    competencies_to_assess: list[str] | None = Field(default_factory=list)


class InterviewCreate(InterviewBase):
    """Schema para criação de entrevista."""

    application_id: str
    created_by: str | None = None


class InterviewUpdate(BaseModel):
    """Schema para atualização de entrevista."""

    interview_type: InterviewType | None = None
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    duration_minutes: int | None = Field(None, ge=15, le=480)
    location: str | None = None
    meeting_link: str | None = None
    meeting_platform: str | None = None
    meeting_id: str | None = None
    meeting_password: str | None = None
    interviewer_ids: list[str] | None = None
    interviewer_names: list[str] | None = None
    lead_interviewer_id: str | None = None
    script: str | None = None
    questions: list[dict] | None = None
    competencies_to_assess: list[str] | None = None
    internal_notes: str | None = None


class InterviewResponse(InterviewBase):
    """Schema de resposta para entrevista."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    status: InterviewStatus
    result: InterviewResult | None = None
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    actual_duration_minutes: int | None = None
    score: int | None = None
    evaluation: dict | None = None
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    competency_scores: dict | None = None
    feedback: str | None = None
    recommendation: str | None = None
    internal_notes: str | None = None
    candidate_feedback: str | None = None
    candidate_questions: list[str] | None = None
    candidate_confirmed: bool = False
    candidate_confirmed_at: datetime | None = None
    interviewer_confirmed: bool = False
    reminder_sent: bool = False
    reminder_sent_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    reschedule_count: int = 0
    is_recorded: bool = False
    recording_url: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    scheduled_datetime: datetime
    is_past: bool
    is_today: bool
    is_upcoming: bool
    is_pending_result: bool
    was_successful: bool


class InterviewListResponse(BaseModel):
    """Schema de lista de entrevistas."""

    items: list[InterviewResponse]
    total: int
    page: int
    page_size: int
    pages: int


class InterviewFilter(BaseModel):
    """Schema para filtro de entrevistas."""

    application_id: str | None = None
    interview_type: InterviewType | None = None
    status: InterviewStatus | None = None
    result: InterviewResult | None = None
    interviewer_id: str | None = None
    scheduled_after: date | None = None
    scheduled_before: date | None = None
    is_today: bool | None = None
    is_upcoming: bool | None = None


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
    score: int | None = Field(None, ge=0, le=100)
    feedback: str | None = None
    strengths: list[str] | None = Field(default_factory=list)
    weaknesses: list[str] | None = Field(default_factory=list)
    competency_scores: dict | None = None
    recommendation: str | None = None


class InterviewReschedule(BaseModel):
    """Schema para reagendar entrevista."""

    new_date: date
    new_time: time
    reason: str | None = None
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
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendation: str
    overall_impression: str | None = None
    culture_fit_score: int | None = Field(None, ge=0, le=100)
    technical_score: int | None = Field(None, ge=0, le=100)
    communication_score: int | None = Field(None, ge=0, le=100)


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
    interviews: list[InterviewResponse]
    available_slots: list[InterviewSlot]
