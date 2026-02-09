"""Schemas para Candidate."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.recruitment.models.candidate import (
    CandidateSource,
    CandidateStatus,
    Gender,
    MaritalStatus,
)


class CandidateBase(BaseModel):
    """Schema base para Candidate."""

    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    cpf: str | None = Field(None, max_length=14)
    rg: str | None = Field(None, max_length=20)
    birth_date: date | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    zip_code: str | None = Field(None, max_length=10)
    neighborhood: str | None = None
    headline: str | None = Field(None, max_length=200)
    summary: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    salary_expectation: Decimal | None = Field(None, ge=0)
    salary_expectation_pj: Decimal | None = Field(None, ge=0)
    available_immediately: bool = True
    notice_period_days: int = Field(default=0, ge=0)
    available_date: date | None = None
    available_for_travel: bool = False
    available_for_relocation: bool = False
    preferred_work_model: str | None = None
    has_cnh: bool = False
    cnh_category: str | None = Field(None, max_length=5)
    has_vehicle: bool = False
    languages: list[dict] | None = Field(default_factory=list)
    source: CandidateSource = CandidateSource.SITE
    source_detail: str | None = None
    is_pcd: bool = False
    pcd_type: str | None = None
    pcd_cid: str | None = None
    needs_accommodation: bool = False
    accommodation_notes: str | None = None


class CandidateCreate(CandidateBase):
    """Schema para criação de candidato."""

    resume_file_path: str | None = None
    resume_text: str | None = None
    photo_url: str | None = None
    tags: list[str] | None = Field(default_factory=list)
    condominium_id: str | None = None
    created_by: str | None = None


class CandidateUpdate(BaseModel):
    """Schema para atualização de candidato."""

    name: str | None = Field(None, min_length=2, max_length=200)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    cpf: str | None = Field(None, max_length=14)
    rg: str | None = Field(None, max_length=20)
    birth_date: date | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    zip_code: str | None = Field(None, max_length=10)
    neighborhood: str | None = None
    headline: str | None = Field(None, max_length=200)
    summary: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    github_url: str | None = None
    resume_file_path: str | None = None
    resume_text: str | None = None
    photo_url: str | None = None
    salary_expectation: Decimal | None = Field(None, ge=0)
    salary_expectation_pj: Decimal | None = Field(None, ge=0)
    available_immediately: bool | None = None
    notice_period_days: int | None = Field(None, ge=0)
    available_date: date | None = None
    available_for_travel: bool | None = None
    available_for_relocation: bool | None = None
    preferred_work_model: str | None = None
    has_cnh: bool | None = None
    cnh_category: str | None = Field(None, max_length=5)
    has_vehicle: bool | None = None
    languages: list[dict] | None = None
    source: CandidateSource | None = None
    source_detail: str | None = None
    tags: list[str] | None = None
    internal_notes: str | None = None
    is_pcd: bool | None = None
    pcd_type: str | None = None
    pcd_cid: str | None = None
    needs_accommodation: bool | None = None
    accommodation_notes: str | None = None


class CandidateResponse(CandidateBase):
    """Schema de resposta para candidato."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: CandidateStatus
    resume_file_path: str | None = None
    resume_updated_at: datetime | None = None
    photo_url: str | None = None
    is_blocked: bool = False
    block_reason: str | None = None
    blocked_at: datetime | None = None
    profile_score: int = 0
    applications_count: int = 0
    interviews_count: int = 0
    hired_count: int = 0
    tags: list[str] | None = None
    last_activity_at: datetime | None = None
    last_application_at: datetime | None = None
    condominium_id: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    age: int | None = None
    is_available: bool
    full_address: str
    profile_completeness: int


class CandidateListResponse(BaseModel):
    """Schema de lista de candidatos."""

    items: list[CandidateResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CandidateFilter(BaseModel):
    """Schema para filtro de candidatos."""

    status: CandidateStatus | None = None
    source: CandidateSource | None = None
    city: str | None = None
    state: str | None = None
    available_immediately: bool | None = None
    has_cnh: bool | None = None
    is_pcd: bool | None = None
    is_blocked: bool | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    min_experience_years: int | None = None
    education_level: str | None = None
    skills: list[str] | None = None
    tags: list[str] | None = None
    condominium_id: str | None = None
    search: str | None = None


class CandidateStats(BaseModel):
    """Estatísticas de candidatos."""

    total_candidates: int = 0
    active_candidates: int = 0
    blocked_candidates: int = 0
    hired_candidates: int = 0
    by_status: dict = Field(default_factory=dict)
    by_source: dict = Field(default_factory=dict)
    by_city: dict = Field(default_factory=dict)
    avg_profile_score: float = 0
    avg_applications: float = 0
    new_this_month: int = 0
    new_this_week: int = 0


class CandidateBlock(BaseModel):
    """Schema para bloquear candidato."""

    reason: str = Field(..., min_length=5)


class CandidateImport(BaseModel):
    """Schema para importar candidato de currículo."""

    resume_text: str
    source: CandidateSource = CandidateSource.SITE
    source_detail: str | None = None


class LanguageInfo(BaseModel):
    """Schema para idioma."""

    language: str
    level: str
    is_native: bool = False
    certification: str | None = None
