"""Schemas para Candidate."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from modules.recruitment.models.candidate import (
    CandidateStatus,
    CandidateSource,
    Gender,
    MaritalStatus,
)


class CandidateBase(BaseModel):
    """Schema base para Candidate."""

    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    neighborhood: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    salary_expectation: Optional[Decimal] = Field(None, ge=0)
    salary_expectation_pj: Optional[Decimal] = Field(None, ge=0)
    available_immediately: bool = True
    notice_period_days: int = Field(default=0, ge=0)
    available_date: Optional[date] = None
    available_for_travel: bool = False
    available_for_relocation: bool = False
    preferred_work_model: Optional[str] = None
    has_cnh: bool = False
    cnh_category: Optional[str] = Field(None, max_length=5)
    has_vehicle: bool = False
    languages: Optional[List[dict]] = Field(default_factory=list)
    source: CandidateSource = CandidateSource.SITE
    source_detail: Optional[str] = None
    is_pcd: bool = False
    pcd_type: Optional[str] = None
    pcd_cid: Optional[str] = None
    needs_accommodation: bool = False
    accommodation_notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema para criação de candidato."""

    resume_file_path: Optional[str] = None
    resume_text: Optional[str] = None
    photo_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    condominium_id: Optional[str] = None
    created_by: Optional[str] = None


class CandidateUpdate(BaseModel):
    """Schema para atualização de candidato."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    cpf: Optional[str] = Field(None, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    neighborhood: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_file_path: Optional[str] = None
    resume_text: Optional[str] = None
    photo_url: Optional[str] = None
    salary_expectation: Optional[Decimal] = Field(None, ge=0)
    salary_expectation_pj: Optional[Decimal] = Field(None, ge=0)
    available_immediately: Optional[bool] = None
    notice_period_days: Optional[int] = Field(None, ge=0)
    available_date: Optional[date] = None
    available_for_travel: Optional[bool] = None
    available_for_relocation: Optional[bool] = None
    preferred_work_model: Optional[str] = None
    has_cnh: Optional[bool] = None
    cnh_category: Optional[str] = Field(None, max_length=5)
    has_vehicle: Optional[bool] = None
    languages: Optional[List[dict]] = None
    source: Optional[CandidateSource] = None
    source_detail: Optional[str] = None
    tags: Optional[List[str]] = None
    internal_notes: Optional[str] = None
    is_pcd: Optional[bool] = None
    pcd_type: Optional[str] = None
    pcd_cid: Optional[str] = None
    needs_accommodation: Optional[bool] = None
    accommodation_notes: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema de resposta para candidato."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: CandidateStatus
    resume_file_path: Optional[str] = None
    resume_updated_at: Optional[datetime] = None
    photo_url: Optional[str] = None
    is_blocked: bool = False
    block_reason: Optional[str] = None
    blocked_at: Optional[datetime] = None
    profile_score: int = 0
    applications_count: int = 0
    interviews_count: int = 0
    hired_count: int = 0
    tags: Optional[List[str]] = None
    last_activity_at: Optional[datetime] = None
    last_application_at: Optional[datetime] = None
    condominium_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    age: Optional[int] = None
    is_available: bool
    full_address: str
    profile_completeness: int


class CandidateListResponse(BaseModel):
    """Schema de lista de candidatos."""

    items: List[CandidateResponse]
    total: int
    page: int
    page_size: int
    pages: int


class CandidateFilter(BaseModel):
    """Schema para filtro de candidatos."""

    status: Optional[CandidateStatus] = None
    source: Optional[CandidateSource] = None
    city: Optional[str] = None
    state: Optional[str] = None
    available_immediately: Optional[bool] = None
    has_cnh: Optional[bool] = None
    is_pcd: Optional[bool] = None
    is_blocked: Optional[bool] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    min_experience_years: Optional[int] = None
    education_level: Optional[str] = None
    skills: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    condominium_id: Optional[str] = None
    search: Optional[str] = None


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
    source_detail: Optional[str] = None


class LanguageInfo(BaseModel):
    """Schema para idioma."""

    language: str
    level: str
    is_native: bool = False
    certification: Optional[str] = None
