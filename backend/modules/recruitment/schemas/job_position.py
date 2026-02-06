"""Schemas para JobPosition."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from modules.recruitment.models.job_position import (
    PositionType,
    PositionLevel,
    PositionStatus,
    WorkModel,
    Department,
)


class JobPositionBase(BaseModel):
    """Schema base para JobPosition."""

    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    position_type: PositionType = PositionType.CLT
    position_level: PositionLevel = PositionLevel.PLENO
    department: Department = Department.OPERACIONAL
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    required_skills: Optional[List[str]] = Field(default_factory=list)
    desired_skills: Optional[List[str]] = Field(default_factory=list)
    min_experience_years: int = Field(default=0, ge=0)
    education_level: Optional[str] = None
    salary_min: Optional[Decimal] = Field(None, ge=0)
    salary_max: Optional[Decimal] = Field(None, ge=0)
    salary_display: bool = False
    benefits: Optional[List[str]] = Field(default_factory=list)
    work_model: WorkModel = WorkModel.PRESENCIAL
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    address: Optional[str] = None
    vacancies: int = Field(default=1, ge=1)
    is_urgent: bool = False
    is_confidential: bool = False
    deadline_date: Optional[date] = None
    expected_start_date: Optional[date] = None
    selection_stages: Optional[List[dict]] = Field(default_factory=list)


class JobPositionCreate(JobPositionBase):
    """Schema para criação de vaga."""

    condominium_id: Optional[str] = None
    recruiter_id: Optional[str] = None
    hiring_manager_id: Optional[str] = None
    created_by: Optional[str] = None


class JobPositionUpdate(BaseModel):
    """Schema para atualização de vaga."""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    position_type: Optional[PositionType] = None
    position_level: Optional[PositionLevel] = None
    department: Optional[Department] = None
    status: Optional[PositionStatus] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    required_skills: Optional[List[str]] = None
    desired_skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = Field(None, ge=0)
    education_level: Optional[str] = None
    salary_min: Optional[Decimal] = Field(None, ge=0)
    salary_max: Optional[Decimal] = Field(None, ge=0)
    salary_display: Optional[bool] = None
    benefits: Optional[List[str]] = None
    work_model: Optional[WorkModel] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    address: Optional[str] = None
    vacancies: Optional[int] = Field(None, ge=1)
    is_urgent: Optional[bool] = None
    is_confidential: Optional[bool] = None
    deadline_date: Optional[date] = None
    expected_start_date: Optional[date] = None
    selection_stages: Optional[List[dict]] = None
    recruiter_id: Optional[str] = None
    hiring_manager_id: Optional[str] = None


class JobPositionResponse(JobPositionBase):
    """Schema de resposta para vaga."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    status: PositionStatus
    opening_date: Optional[date] = None
    closed_at: Optional[datetime] = None
    filled_vacancies: int = 0
    applications_count: int = 0
    views_count: int = 0
    recruiter_id: Optional[str] = None
    hiring_manager_id: Optional[str] = None
    condominium_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed
    is_open: bool
    is_expired: bool
    remaining_vacancies: int
    is_fully_filled: bool
    salary_range: str


class JobPositionListResponse(BaseModel):
    """Schema de lista de vagas."""

    items: List[JobPositionResponse]
    total: int
    page: int
    page_size: int
    pages: int


class JobPositionFilter(BaseModel):
    """Schema para filtro de vagas."""

    status: Optional[PositionStatus] = None
    position_type: Optional[PositionType] = None
    position_level: Optional[PositionLevel] = None
    department: Optional[Department] = None
    work_model: Optional[WorkModel] = None
    city: Optional[str] = None
    state: Optional[str] = None
    is_urgent: Optional[bool] = None
    is_confidential: Optional[bool] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    recruiter_id: Optional[str] = None
    condominium_id: Optional[str] = None
    search: Optional[str] = None


class JobPositionStats(BaseModel):
    """Estatísticas de vagas."""

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
    avg_time_to_fill_days: float = 0
    avg_applications_per_position: float = 0


class JobPositionPublish(BaseModel):
    """Schema para publicar vaga."""

    channels: Optional[List[str]] = Field(default_factory=list)
    post_to_linkedin: bool = False
    post_to_indeed: bool = False
    post_to_catho: bool = False
    post_to_website: bool = True


class SelectionStage(BaseModel):
    """Schema para etapa do processo seletivo."""

    name: str
    description: Optional[str] = None
    order: int = 1
    stage_type: str = "interview"
    is_mandatory: bool = True
    is_eliminatory: bool = True
    weight: float = 1.0
    duration_days: int = 7
    responsible_id: Optional[str] = None
