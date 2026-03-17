"""Schemas para JobPosition.

Reescrito para refletir o schema real do banco de dados (15/03/2026).
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from modules.recruitment.models.job_position import (
    Department,
    PositionLevel,
    PositionStatus,
    PositionType,
    WorkModel,
)


class JobPositionCreate(BaseModel):
    """Schema para criacao de vaga."""

    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    position_type: str = "clt"
    position_level: str | None = None
    department: str | None = None
    requirements: str | None = None
    responsibilities: str | None = None
    benefits: str | None = None
    required_skills: list[str] | None = Field(default_factory=list)
    desired_skills: list[str] | None = Field(default_factory=list)
    min_experience_years: int | None = Field(None, ge=0)
    education_level: str | None = None
    languages: dict | None = None
    salary_min: Decimal | None = Field(None, ge=0)
    salary_max: Decimal | None = Field(None, ge=0)
    show_salary: bool = False
    additional_benefits: dict | None = None
    work_model: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    country: str | None = None
    address: str | None = None
    vacancies: int = Field(default=1, ge=1)
    deadline: date | None = None
    selection_steps: dict | None = None
    condominio_id: str | None = None
    responsible_id: str | None = None


class JobPositionUpdate(BaseModel):
    """Schema para atualizacao de vaga."""

    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    position_type: str | None = None
    position_level: str | None = None
    department: str | None = None
    status: str | None = None
    requirements: str | None = None
    responsibilities: str | None = None
    benefits: str | None = None
    required_skills: list[str] | None = None
    desired_skills: list[str] | None = None
    min_experience_years: int | None = Field(None, ge=0)
    education_level: str | None = None
    salary_min: Decimal | None = Field(None, ge=0)
    salary_max: Decimal | None = Field(None, ge=0)
    show_salary: bool | None = None
    work_model: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    address: str | None = None
    vacancies: int | None = Field(None, ge=1)
    deadline: date | None = None
    responsible_id: str | None = None


class JobPositionResponse(BaseModel):
    """Schema de resposta para vaga."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str | None = None
    condominio_id: str | None = None
    code: str | None = None
    title: str
    description: str | None = None
    position_type: str
    position_level: str | None = None
    department: str | None = None
    status: str
    requirements: str | None = None
    responsibilities: str | None = None
    benefits: str | None = None
    required_skills: list[str] | None = None
    desired_skills: list[str] | None = None
    min_experience_years: int | None = None
    education_level: str | None = None
    languages: dict | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    show_salary: bool | None = None
    additional_benefits: dict | None = None
    work_model: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    address: str | None = None
    vacancies: int | None = None
    filled_count: int | None = 0
    published_at: datetime | None = None
    deadline: date | None = None
    closed_at: datetime | None = None
    selection_steps: dict | None = None
    responsible_id: str | None = None
    linkedin_job_id: str | None = None
    indeed_job_id: str | None = None
    external_url: str | None = None
    is_active: bool | None = True
    is_deleted: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by_id: str | None = None

    # Computed properties
    is_open: bool | None = None
    is_expired: bool | None = None
    remaining_vacancies: int | None = None
    salary_range: str | None = None


class JobPositionListResponse(BaseModel):
    """Schema de lista de vagas."""

    model_config = {"extra": "allow"}

    items: list[JobPositionResponse]
    total: int
    skip: int = 0
    limit: int = 20


class JobPositionFilter(BaseModel):
    """Schema para filtro de vagas."""

    status: PositionStatus | None = None
    position_type: PositionType | None = None
    position_level: PositionLevel | None = None
    department: Department | None = None
    work_model: WorkModel | None = None
    city: str | None = None
    state: str | None = None
    is_urgent: bool | None = None
    is_confidential: bool | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    recruiter_id: str | None = None
    condominium_id: str | None = None
    search: str | None = None


class JobPositionStats(BaseModel):
    """Estatisticas de vagas."""

    total_positions: int = 0
    open_positions: int = 0
    closed_positions: int = 0
    filled_positions: int = 0
    total_vacancies: int = 0
    filled_vacancies: int = 0
    total_applications: int = 0
    by_status: dict = Field(default_factory=dict)
    by_department: dict = Field(default_factory=dict)
    by_level: dict = Field(default_factory=dict)
    by_type: dict = Field(default_factory=dict)


class JobPositionPublish(BaseModel):
    """Schema para publicar vaga."""

    published_at: date | None = None
    deadline_date: date | None = None
    publish_externally: bool | None = None
    external_platforms: list[str] | None = None
