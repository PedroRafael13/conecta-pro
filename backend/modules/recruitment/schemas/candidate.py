"""Schemas para Candidate.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.recruitment.models.candidate import (
    CandidateSource,
    CandidateStatus,
)


class CandidateCreate(BaseModel):
    """Schema para criacao de candidato."""

    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    cpf: str | None = Field(None, max_length=14)
    rg: str | None = Field(None, max_length=20)
    birth_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    zip_code: str | None = Field(None, max_length=10)
    country: str | None = None
    headline: str | None = Field(None, max_length=200)
    summary: str | None = None
    current_company: str | None = None
    current_position: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    resume_url: str | None = None
    resume_text: str | None = None
    photo_url: str | None = None
    salary_expectation: Decimal | None = Field(None, ge=0)
    availability: str | None = None
    source: str | None = "site"
    tags: list[str] | None = Field(default_factory=list)


class CandidateUpdate(BaseModel):
    """Schema para atualizacao de candidato."""

    name: str | None = Field(None, min_length=2, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    cpf: str | None = Field(None, max_length=14)
    rg: str | None = Field(None, max_length=20)
    birth_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    zip_code: str | None = Field(None, max_length=10)
    country: str | None = None
    headline: str | None = Field(None, max_length=200)
    summary: str | None = None
    current_company: str | None = None
    current_position: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    resume_url: str | None = None
    resume_text: str | None = None
    photo_url: str | None = None
    salary_expectation: Decimal | None = None
    availability: str | None = None
    source: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class CandidateResponse(BaseModel):
    """Schema de resposta para candidato."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str | None = None
    name: str
    email: str
    phone: str | None = None
    whatsapp: str | None = None
    cpf: str | None = None
    rg: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    headline: str | None = None
    summary: str | None = None
    current_company: str | None = None
    current_position: str | None = None
    linkedin_url: str | None = None
    linkedin_id: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    resume_url: str | None = None
    resume_text: str | None = None
    resume_parsed: dict | None = None
    photo_url: str | None = None
    salary_expectation: Decimal | None = None
    availability: str | None = None
    status: str | None = None
    source: str | None = None
    ai_score: Decimal | None = None
    ai_analysis: dict | None = None
    tags: list[str] | None = None
    is_active: bool | None = True
    is_deleted: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CandidateListResponse(BaseModel):
    """Schema de lista de candidatos."""

    model_config = {"extra": "allow"}

    items: list[CandidateResponse]
    total: int
    skip: int = 0
    limit: int = 20


class CandidateFilter(BaseModel):
    """Schema para filtro de candidatos."""

    status: CandidateStatus | None = None
    source: CandidateSource | None = None
    city: str | None = None
    state: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    search: str | None = None


class CandidateStats(BaseModel):
    """Estatisticas de candidatos."""

    total_candidates: int = 0
    active_candidates: int = 0
    blocked_candidates: int = 0
    hired_candidates: int = 0
    by_status: dict = Field(default_factory=dict)
    by_source: dict = Field(default_factory=dict)
    by_city: dict = Field(default_factory=dict)
    avg_profile_score: float = 0
    new_this_month: int = 0
    new_this_week: int = 0


class CandidateBlock(BaseModel):
    """Schema para bloquear candidato."""

    reason: str = Field(..., min_length=5)


class CandidateImport(BaseModel):
    """Schema para importar candidato de curriculo."""

    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str | None = None
    resume_text: str
    resume_url: str | None = None
    source: str | None = "site"
