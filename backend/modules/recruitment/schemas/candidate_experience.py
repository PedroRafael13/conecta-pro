"""Schemas para CandidateExperience."""

from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from modules.recruitment.models.candidate_experience import (
    EmploymentType,
    ExperienceLevel,
)


class CandidateExperienceBase(BaseModel):
    """Schema base para CandidateExperience."""

    company_name: str = Field(..., min_length=2, max_length=200)
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_location: Optional[str] = None
    company_linkedin: Optional[str] = None
    job_title: str = Field(..., min_length=2, max_length=200)
    department: Optional[str] = None
    level: Optional[ExperienceLevel] = None
    employment_type: EmploymentType = EmploymentType.CLT
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = Field(default_factory=list)
    achievements: Optional[List[str]] = Field(default_factory=list)
    technologies: Optional[List[str]] = Field(default_factory=list)
    team_size: Optional[int] = Field(None, ge=0)
    direct_reports: Optional[int] = Field(None, ge=0)
    budget_managed: Optional[str] = None
    leaving_reason: Optional[str] = None


class CandidateExperienceCreate(CandidateExperienceBase):
    """Schema para criação de experiência."""

    candidate_id: str
    reference_name: Optional[str] = None
    reference_title: Optional[str] = None
    reference_phone: Optional[str] = None
    reference_email: Optional[EmailStr] = None
    can_contact_reference: bool = True


class CandidateExperienceUpdate(BaseModel):
    """Schema para atualização de experiência."""

    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    company_industry: Optional[str] = None
    company_size: Optional[str] = None
    company_location: Optional[str] = None
    company_linkedin: Optional[str] = None
    job_title: Optional[str] = Field(None, min_length=2, max_length=200)
    department: Optional[str] = None
    level: Optional[ExperienceLevel] = None
    employment_type: Optional[EmploymentType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    team_size: Optional[int] = Field(None, ge=0)
    direct_reports: Optional[int] = Field(None, ge=0)
    budget_managed: Optional[str] = None
    leaving_reason: Optional[str] = None
    reference_name: Optional[str] = None
    reference_title: Optional[str] = None
    reference_phone: Optional[str] = None
    reference_email: Optional[EmailStr] = None
    can_contact_reference: Optional[bool] = None
    order: Optional[int] = None


class CandidateExperienceResponse(CandidateExperienceBase):
    """Schema de resposta para experiência."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    reference_name: Optional[str] = None
    reference_title: Optional[str] = None
    reference_phone: Optional[str] = None
    reference_email: Optional[str] = None
    can_contact_reference: bool = True
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    is_active: bool = True
    order: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    duration_months: int
    duration_years: float
    duration_display: str
    period_display: str
    has_reference: bool


class CandidateExperienceListResponse(BaseModel):
    """Schema de lista de experiências."""

    items: List[CandidateExperienceResponse]
    total: int
    total_experience_months: int


class CandidateExperienceFilter(BaseModel):
    """Schema para filtro de experiências."""

    candidate_id: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    level: Optional[ExperienceLevel] = None
    is_current: Optional[bool] = None
    is_verified: Optional[bool] = None
    company_name: Optional[str] = None
    search: Optional[str] = None


class ReferenceInfo(BaseModel):
    """Schema para referência."""

    name: str = Field(..., min_length=2)
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    can_contact: bool = True
