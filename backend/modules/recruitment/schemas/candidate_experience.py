"""Schemas para CandidateExperience."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.recruitment.models.candidate_experience import (
    EmploymentType,
    ExperienceLevel,
)


class CandidateExperienceBase(BaseModel):
    """Schema base para CandidateExperience."""

    company_name: str = Field(..., min_length=2, max_length=200)
    company_industry: str | None = None
    company_size: str | None = None
    company_location: str | None = None
    company_linkedin: str | None = None
    job_title: str = Field(..., min_length=2, max_length=200)
    department: str | None = None
    level: ExperienceLevel | None = None
    employment_type: EmploymentType = EmploymentType.CLT
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    description: str | None = None
    responsibilities: list[str] | None = Field(default_factory=list)
    achievements: list[str] | None = Field(default_factory=list)
    technologies: list[str] | None = Field(default_factory=list)
    team_size: int | None = Field(None, ge=0)
    direct_reports: int | None = Field(None, ge=0)
    budget_managed: str | None = None
    leaving_reason: str | None = None


class CandidateExperienceCreate(CandidateExperienceBase):
    """Schema para criação de experiência."""

    candidate_id: str
    reference_name: str | None = None
    reference_title: str | None = None
    reference_phone: str | None = None
    reference_email: EmailStr | None = None
    can_contact_reference: bool = True


class CandidateExperienceUpdate(BaseModel):
    """Schema para atualização de experiência."""

    company_name: str | None = Field(None, min_length=2, max_length=200)
    company_industry: str | None = None
    company_size: str | None = None
    company_location: str | None = None
    company_linkedin: str | None = None
    job_title: str | None = Field(None, min_length=2, max_length=200)
    department: str | None = None
    level: ExperienceLevel | None = None
    employment_type: EmploymentType | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    description: str | None = None
    responsibilities: list[str] | None = None
    achievements: list[str] | None = None
    technologies: list[str] | None = None
    team_size: int | None = Field(None, ge=0)
    direct_reports: int | None = Field(None, ge=0)
    budget_managed: str | None = None
    leaving_reason: str | None = None
    reference_name: str | None = None
    reference_title: str | None = None
    reference_phone: str | None = None
    reference_email: EmailStr | None = None
    can_contact_reference: bool | None = None
    order: int | None = None


class CandidateExperienceResponse(CandidateExperienceBase):
    """Schema de resposta para experiência."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    reference_name: str | None = None
    reference_title: str | None = None
    reference_phone: str | None = None
    reference_email: str | None = None
    can_contact_reference: bool = True
    is_verified: bool = False
    verified_at: datetime | None = None
    verification_notes: str | None = None
    is_active: bool = True
    order: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    duration_months: int
    duration_years: float
    duration_display: str
    period_display: str
    has_reference: bool


class CandidateExperienceListResponse(BaseModel):
    """Schema de lista de experiências."""

    items: list[CandidateExperienceResponse]
    total: int
    total_experience_months: int


class CandidateExperienceFilter(BaseModel):
    """Schema para filtro de experiências."""

    candidate_id: str | None = None
    employment_type: EmploymentType | None = None
    level: ExperienceLevel | None = None
    is_current: bool | None = None
    is_verified: bool | None = None
    company_name: str | None = None
    search: str | None = None


class ReferenceInfo(BaseModel):
    """Schema para referência."""

    name: str = Field(..., min_length=2)
    title: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    can_contact: bool = True
