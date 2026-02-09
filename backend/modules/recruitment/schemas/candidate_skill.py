"""Schemas para CandidateSkill."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.candidate_skill import (
    SkillCategory,
    SkillLevel,
)


class CandidateSkillBase(BaseModel):
    """Schema base para CandidateSkill."""

    name: str = Field(..., min_length=2, max_length=100)
    category: SkillCategory = SkillCategory.TECNICA
    level: SkillLevel = SkillLevel.INTERMEDIARIO
    years_experience: int | None = Field(None, ge=0)
    months_experience: int | None = Field(None, ge=0, le=11)
    last_used_year: int | None = None
    notes: str | None = None
    is_primary: bool = False


class CandidateSkillCreate(CandidateSkillBase):
    """Schema para criação de habilidade."""

    candidate_id: str
    is_certified: bool = False
    certification_name: str | None = None
    certification_issuer: str | None = None
    certification_date: datetime | None = None
    certification_expiry: datetime | None = None
    certification_url: str | None = None


class CandidateSkillUpdate(BaseModel):
    """Schema para atualização de habilidade."""

    name: str | None = Field(None, min_length=2, max_length=100)
    category: SkillCategory | None = None
    level: SkillLevel | None = None
    years_experience: int | None = Field(None, ge=0)
    months_experience: int | None = Field(None, ge=0, le=11)
    last_used_year: int | None = None
    is_certified: bool | None = None
    certification_name: str | None = None
    certification_issuer: str | None = None
    certification_date: datetime | None = None
    certification_expiry: datetime | None = None
    certification_url: str | None = None
    notes: str | None = None
    is_primary: bool | None = None
    is_active: bool | None = None


class CandidateSkillResponse(CandidateSkillBase):
    """Schema de resposta para habilidade."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    is_certified: bool = False
    certification_name: str | None = None
    certification_issuer: str | None = None
    certification_date: datetime | None = None
    certification_expiry: datetime | None = None
    certification_url: str | None = None
    is_verified: bool = False
    verified_at: datetime | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    total_experience_months: int
    experience_display: str
    is_certification_valid: bool
    level_score: int


class CandidateSkillListResponse(BaseModel):
    """Schema de lista de habilidades."""

    items: list[CandidateSkillResponse]
    total: int


class CandidateSkillFilter(BaseModel):
    """Schema para filtro de habilidades."""

    candidate_id: str | None = None
    category: SkillCategory | None = None
    level: SkillLevel | None = None
    is_certified: bool | None = None
    is_verified: bool | None = None
    is_active: bool | None = None
    search: str | None = None


class CertificationAdd(BaseModel):
    """Schema para adicionar certificação."""

    certification_name: str = Field(..., min_length=3)
    certification_issuer: str = Field(..., min_length=2)
    certification_date: datetime | None = None
    certification_expiry: datetime | None = None
    certification_url: str | None = None
