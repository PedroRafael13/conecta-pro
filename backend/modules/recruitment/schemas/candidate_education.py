"""Schemas para CandidateEducation."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.candidate_education import (
    EducationLevel,
    EducationStatus,
    StudyPeriod,
)


class CandidateEducationBase(BaseModel):
    """Schema base para CandidateEducation."""

    institution_name: str = Field(..., min_length=2, max_length=200)
    institution_type: str | None = None
    institution_location: str | None = None
    institution_country: str = "Brasil"
    course_name: str = Field(..., min_length=2, max_length=200)
    level: EducationLevel = EducationLevel.GRADUACAO
    area: str | None = None
    status: EducationStatus = EducationStatus.COMPLETO
    start_date: date | None = None
    end_date: date | None = None
    expected_end_date: date | None = None
    study_period: StudyPeriod | None = None
    gpa: float | None = Field(None, ge=0)
    gpa_max: float = Field(default=10.0, ge=1)
    activities: list[str] | None = Field(default_factory=list)
    honors: list[str] | None = Field(default_factory=list)


class CandidateEducationCreate(CandidateEducationBase):
    """Schema para criação de formação."""

    candidate_id: str
    class_rank: int | None = Field(None, ge=1)
    class_size: int | None = Field(None, ge=1)
    thesis_title: str | None = None
    thesis_advisor: str | None = None
    thesis_abstract: str | None = None
    scholarships: list[str] | None = Field(default_factory=list)
    has_exchange: bool = False
    exchange_institution: str | None = None
    exchange_country: str | None = None
    exchange_duration_months: int | None = Field(None, ge=1)
    diploma_number: str | None = None
    diploma_date: date | None = None


class CandidateEducationUpdate(BaseModel):
    """Schema para atualização de formação."""

    institution_name: str | None = Field(None, min_length=2, max_length=200)
    institution_type: str | None = None
    institution_location: str | None = None
    institution_country: str | None = None
    course_name: str | None = Field(None, min_length=2, max_length=200)
    level: EducationLevel | None = None
    area: str | None = None
    status: EducationStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    expected_end_date: date | None = None
    study_period: StudyPeriod | None = None
    gpa: float | None = Field(None, ge=0)
    gpa_max: float | None = Field(None, ge=1)
    class_rank: int | None = Field(None, ge=1)
    class_size: int | None = Field(None, ge=1)
    thesis_title: str | None = None
    thesis_advisor: str | None = None
    thesis_abstract: str | None = None
    activities: list[str] | None = None
    honors: list[str] | None = None
    scholarships: list[str] | None = None
    has_exchange: bool | None = None
    exchange_institution: str | None = None
    exchange_country: str | None = None
    exchange_duration_months: int | None = Field(None, ge=1)
    diploma_number: str | None = None
    diploma_date: date | None = None
    is_primary: bool | None = None
    order: int | None = None


class CandidateEducationResponse(CandidateEducationBase):
    """Schema de resposta para formação."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    class_rank: int | None = None
    class_size: int | None = None
    thesis_title: str | None = None
    thesis_advisor: str | None = None
    thesis_abstract: str | None = None
    scholarships: list[str] | None = None
    has_exchange: bool = False
    exchange_institution: str | None = None
    exchange_country: str | None = None
    exchange_duration_months: int | None = None
    diploma_number: str | None = None
    diploma_date: date | None = None
    diploma_verified: bool = False
    is_verified: bool = False
    verified_at: datetime | None = None
    is_active: bool = True
    is_primary: bool = False
    order: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    is_completed: bool
    is_in_progress: bool
    duration_months: int | None
    period_display: str
    gpa_normalized: float | None
    level_display: str
    level_weight: int


class CandidateEducationListResponse(BaseModel):
    """Schema de lista de formações."""

    items: list[CandidateEducationResponse]
    total: int
    highest_level: str | None = None


class CandidateEducationFilter(BaseModel):
    """Schema para filtro de formações."""

    candidate_id: str | None = None
    level: EducationLevel | None = None
    status: EducationStatus | None = None
    is_verified: bool | None = None
    institution_name: str | None = None
    course_name: str | None = None
    search: str | None = None


class ThesisInfo(BaseModel):
    """Schema para TCC/Tese."""

    title: str = Field(..., min_length=5)
    advisor: str | None = None
    abstract: str | None = None


class ExchangeInfo(BaseModel):
    """Schema para intercâmbio."""

    institution: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2)
    duration_months: int = Field(..., ge=1)
