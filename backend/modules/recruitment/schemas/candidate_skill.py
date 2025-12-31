"""Schemas para CandidateSkill."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from modules.recruitment.models.candidate_skill import (
    SkillCategory,
    SkillLevel,
)


class CandidateSkillBase(BaseModel):
    """Schema base para CandidateSkill."""

    name: str = Field(..., min_length=2, max_length=100)
    category: SkillCategory = SkillCategory.TECNICA
    level: SkillLevel = SkillLevel.INTERMEDIARIO
    years_experience: Optional[int] = Field(None, ge=0)
    months_experience: Optional[int] = Field(None, ge=0, le=11)
    last_used_year: Optional[int] = None
    notes: Optional[str] = None
    is_primary: bool = False


class CandidateSkillCreate(CandidateSkillBase):
    """Schema para criação de habilidade."""

    candidate_id: str
    is_certified: bool = False
    certification_name: Optional[str] = None
    certification_issuer: Optional[str] = None
    certification_date: Optional[datetime] = None
    certification_expiry: Optional[datetime] = None
    certification_url: Optional[str] = None


class CandidateSkillUpdate(BaseModel):
    """Schema para atualização de habilidade."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[SkillCategory] = None
    level: Optional[SkillLevel] = None
    years_experience: Optional[int] = Field(None, ge=0)
    months_experience: Optional[int] = Field(None, ge=0, le=11)
    last_used_year: Optional[int] = None
    is_certified: Optional[bool] = None
    certification_name: Optional[str] = None
    certification_issuer: Optional[str] = None
    certification_date: Optional[datetime] = None
    certification_expiry: Optional[datetime] = None
    certification_url: Optional[str] = None
    notes: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class CandidateSkillResponse(CandidateSkillBase):
    """Schema de resposta para habilidade."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_id: str
    is_certified: bool = False
    certification_name: Optional[str] = None
    certification_issuer: Optional[str] = None
    certification_date: Optional[datetime] = None
    certification_expiry: Optional[datetime] = None
    certification_url: Optional[str] = None
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    total_experience_months: int
    experience_display: str
    is_certification_valid: bool
    level_score: int


class CandidateSkillListResponse(BaseModel):
    """Schema de lista de habilidades."""

    items: List[CandidateSkillResponse]
    total: int


class CandidateSkillFilter(BaseModel):
    """Schema para filtro de habilidades."""

    candidate_id: Optional[str] = None
    category: Optional[SkillCategory] = None
    level: Optional[SkillLevel] = None
    is_certified: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


class CertificationAdd(BaseModel):
    """Schema para adicionar certificação."""

    certification_name: str = Field(..., min_length=3)
    certification_issuer: str = Field(..., min_length=2)
    certification_date: Optional[datetime] = None
    certification_expiry: Optional[datetime] = None
    certification_url: Optional[str] = None
