"""Schemas para CandidateEducation."""

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from modules.recruitment.models.candidate_education import (
    EducationLevel,
    EducationStatus,
    StudyPeriod,
)


class CandidateEducationBase(BaseModel):
    """Schema base para CandidateEducation."""

    institution_name: str = Field(..., min_length=2, max_length=200)
    institution_type: Optional[str] = None
    institution_location: Optional[str] = None
    institution_country: str = "Brasil"
    course_name: str = Field(..., min_length=2, max_length=200)
    level: EducationLevel = EducationLevel.GRADUACAO
    area: Optional[str] = None
    status: EducationStatus = EducationStatus.COMPLETO
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    study_period: Optional[StudyPeriod] = None
    gpa: Optional[float] = Field(None, ge=0)
    gpa_max: float = Field(default=10.0, ge=1)
    activities: Optional[List[str]] = Field(default_factory=list)
    honors: Optional[List[str]] = Field(default_factory=list)


class CandidateEducationCreate(CandidateEducationBase):
    """Schema para criação de formação."""

    candidate_id: str
    class_rank: Optional[int] = Field(None, ge=1)
    class_size: Optional[int] = Field(None, ge=1)
    thesis_title: Optional[str] = None
    thesis_advisor: Optional[str] = None
    thesis_abstract: Optional[str] = None
    scholarships: Optional[List[str]] = Field(default_factory=list)
    has_exchange: bool = False
    exchange_institution: Optional[str] = None
    exchange_country: Optional[str] = None
    exchange_duration_months: Optional[int] = Field(None, ge=1)
    diploma_number: Optional[str] = None
    diploma_date: Optional[date] = None


class CandidateEducationUpdate(BaseModel):
    """Schema para atualização de formação."""

    institution_name: Optional[str] = Field(None, min_length=2, max_length=200)
    institution_type: Optional[str] = None
    institution_location: Optional[str] = None
    institution_country: Optional[str] = None
    course_name: Optional[str] = Field(None, min_length=2, max_length=200)
    level: Optional[EducationLevel] = None
    area: Optional[str] = None
    status: Optional[EducationStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    study_period: Optional[StudyPeriod] = None
    gpa: Optional[float] = Field(None, ge=0)
    gpa_max: Optional[float] = Field(None, ge=1)
    class_rank: Optional[int] = Field(None, ge=1)
    class_size: Optional[int] = Field(None, ge=1)
    thesis_title: Optional[str] = None
    thesis_advisor: Optional[str] = None
    thesis_abstract: Optional[str] = None
    activities: Optional[List[str]] = None
    honors: Optional[List[str]] = None
    scholarships: Optional[List[str]] = None
    has_exchange: Optional[bool] = None
    exchange_institution: Optional[str] = None
    exchange_country: Optional[str] = None
    exchange_duration_months: Optional[int] = Field(None, ge=1)
    diploma_number: Optional[str] = None
    diploma_date: Optional[date] = None
    is_primary: Optional[bool] = None
    order: Optional[int] = None


class CandidateEducationResponse(CandidateEducationBase):
    """Schema de resposta para formação."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    class_rank: Optional[int] = None
    class_size: Optional[int] = None
    thesis_title: Optional[str] = None
    thesis_advisor: Optional[str] = None
    thesis_abstract: Optional[str] = None
    scholarships: Optional[List[str]] = None
    has_exchange: bool = False
    exchange_institution: Optional[str] = None
    exchange_country: Optional[str] = None
    exchange_duration_months: Optional[int] = None
    diploma_number: Optional[str] = None
    diploma_date: Optional[date] = None
    diploma_verified: bool = False
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    is_active: bool = True
    is_primary: bool = False
    order: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    is_completed: bool
    is_in_progress: bool
    duration_months: Optional[int]
    period_display: str
    gpa_normalized: Optional[float]
    level_display: str
    level_weight: int


class CandidateEducationListResponse(BaseModel):
    """Schema de lista de formações."""

    items: List[CandidateEducationResponse]
    total: int
    highest_level: Optional[str] = None


class CandidateEducationFilter(BaseModel):
    """Schema para filtro de formações."""

    candidate_id: Optional[str] = None
    level: Optional[EducationLevel] = None
    status: Optional[EducationStatus] = None
    is_verified: Optional[bool] = None
    institution_name: Optional[str] = None
    course_name: Optional[str] = None
    search: Optional[str] = None


class ThesisInfo(BaseModel):
    """Schema para TCC/Tese."""

    title: str = Field(..., min_length=5)
    advisor: Optional[str] = None
    abstract: Optional[str] = None


class ExchangeInfo(BaseModel):
    """Schema para intercâmbio."""

    institution: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2)
    duration_months: int = Field(..., ge=1)
