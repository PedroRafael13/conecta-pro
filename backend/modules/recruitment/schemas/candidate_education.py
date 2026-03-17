"""Schemas para CandidateEducation."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CandidateEducationBase(BaseModel):
    """Schema base para CandidateEducation."""

    institution: str = Field(..., min_length=2, max_length=200)
    degree: str | None = None
    field_of_study: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False
    status: str | None = None
    grade: str | None = None


class CandidateEducationCreate(CandidateEducationBase):
    """Schema para criar CandidateEducation."""

    candidate_id: str


class CandidateEducationUpdate(BaseModel):
    """Schema para atualizar CandidateEducation."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    status: str | None = None
    grade: str | None = None


class CandidateEducationResponse(CandidateEducationBase):
    """Schema de resposta para CandidateEducation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
