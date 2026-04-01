"""Schemas para Interview.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
"""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.interview import (
    InterviewResult,
    InterviewStatus,
    InterviewType,
)


class InterviewCreate(BaseModel):
    """Schema para criacao de entrevista."""

    application_id: str
    interview_type: InterviewType = InterviewType.VIDEO
    format: str = "video"
    scheduled_date: date
    scheduled_time: time
    duration_minutes: int = Field(default=60, ge=15, le=480)
    location: str | None = None
    meeting_url: str | None = None
    interviewer_ids: list[str] | None = Field(default_factory=list)


class InterviewUpdate(BaseModel):
    """Schema para atualizacao de entrevista."""

    interview_type: InterviewType | None = None
    format: str | None = None
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    duration_minutes: int | None = Field(None, ge=15, le=480)
    location: str | None = None
    meeting_url: str | None = None
    interviewer_ids: list[str] | None = None


class InterviewResponse(BaseModel):
    """Schema de resposta para entrevista."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    application_id: str
    interview_type: str
    format: str
    status: str | None = None
    result: str | None = None
    scheduled_at: datetime
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    duration_minutes: int | None = None
    location: str | None = None
    meeting_url: str | None = None
    interviewer_ids: list[str] | None = None
    interviewer_notes: dict | None = None
    feedback: str | None = None
    rating: int | None = None
    score: int | None = None
    transcript: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    recording_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InterviewListResponse(BaseModel):
    """Schema de lista de entrevistas."""

    items: list[InterviewResponse]
    total: int
    skip: int = 0
    limit: int = 20


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
    """Estatisticas de entrevistas."""

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


class InterviewReschedule(BaseModel):
    """Schema para reagendar entrevista."""

    new_date: date
    new_time: time
    reason: str | None = None


class InterviewCancel(BaseModel):
    """Schema para cancelar entrevista."""

    reason: str = Field(..., min_length=5)


class InterviewEvaluation(BaseModel):
    """Schema para avaliacao de entrevista."""

    competency: str
    score: int = Field(..., ge=0, le=100)
    notes: str | None = None
    evaluator_id: str | None = None


class InterviewSlot(BaseModel):
    """Schema para slot de entrevista."""

    date: date
    time: time
    duration_minutes: int = 60
    available: bool = True


class InterviewCalendar(BaseModel):
    """Schema para calendario de entrevistas."""

    month: int
    year: int
    interviewer_id: str
    days: dict = Field(default_factory=dict)
    total_interviews: int = 0
