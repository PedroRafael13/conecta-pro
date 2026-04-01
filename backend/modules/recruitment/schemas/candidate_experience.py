"""Schemas para CandidateExperience."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CandidateExperienceBase(BaseModel):
    """Schema base para CandidateExperience."""

    company: str = Field(..., min_length=2, max_length=200)
    position: str = Field(..., min_length=2, max_length=200)
    location: str | None = None
    description: str | None = None
    achievements: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    employment_type: str | None = None
    industry: str | None = None
    salary: float | None = None


class CandidateExperienceCreate(CandidateExperienceBase):
    """Schema para criacao de experiencia."""

    candidate_id: str


class CandidateExperienceUpdate(BaseModel):
    """Schema para atualizacao de experiencia."""

    company: str | None = None
    position: str | None = None
    location: str | None = None
    description: str | None = None
    achievements: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    employment_type: str | None = None
    industry: str | None = None
    salary: float | None = None


class CandidateExperienceResponse(CandidateExperienceBase):
    """Schema de resposta para experiencia."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CandidateExperienceListResponse(BaseModel):
    """Schema de lista de experiencias."""

    items: list[CandidateExperienceResponse]
    total: int
