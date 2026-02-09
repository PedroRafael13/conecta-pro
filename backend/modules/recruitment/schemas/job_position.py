"""Schemas para JobPosition."""

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


class JobPositionBase(BaseModel):
    """Schema base para JobPosition."""

    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    position_type: PositionType = PositionType.CLT
    position_level: PositionLevel = PositionLevel.PLENO
    department: Department = Department.OPERACIONAL
    requirements: str | None = None
    responsibilities: str | None = None
    required_skills: list[str] | None = Field(default_factory=list)
    desired_skills: list[str] | None = Field(default_factory=list)
    min_experience_years: int = Field(default=0, ge=0)
    education_level: str | None = None
    salary_min: Decimal | None = Field(None, ge=0)
    salary_max: Decimal | None = Field(None, ge=0)
    salary_display: bool = False
    benefits: list[str] | None = Field(default_factory=list)
    work_model: WorkModel = WorkModel.PRESENCIAL
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    address: str | None = None
    vacancies: int = Field(default=1, ge=1)
    is_urgent: bool = False
    is_confidential: bool = False
    deadline_date: date | None = None
    expected_start_date: date | None = None
    selection_stages: list[dict] | None = Field(default_factory=list)


class JobPositionCreate(JobPositionBase):
    """Schema para criação de vaga."""

    condominium_id: str | None = None
    recruiter_id: str | None = None
    hiring_manager_id: str | None = None
    created_by: str | None = None


class JobPositionUpdate(BaseModel):
    """Schema para atualização de vaga."""

    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    position_type: PositionType | None = None
    position_level: PositionLevel | None = None
    department: Department | None = None
    status: PositionStatus | None = None
    requirements: str | None = None
    responsibilities: str | None = None
    required_skills: list[str] | None = None
    desired_skills: list[str] | None = None
    min_experience_years: int | None = Field(None, ge=0)
    education_level: str | None = None
    salary_min: Decimal | None = Field(None, ge=0)
    salary_max: Decimal | None = Field(None, ge=0)
    salary_display: bool | None = None
    benefits: list[str] | None = None
    work_model: WorkModel | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    address: str | None = None
    vacancies: int | None = Field(None, ge=1)
    is_urgent: bool | None = None
    is_confidential: bool | None = None
    deadline_date: date | None = None
    expected_start_date: date | None = None
    selection_stages: list[dict] | None = None
    recruiter_id: str | None = None
    hiring_manager_id: str | None = None


class JobPositionResponse(JobPositionBase):
    """Schema de resposta para vaga."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    status: PositionStatus
    opening_date: date | None = None
    closed_at: datetime | None = None
    filled_vacancies: int = 0
    applications_count: int = 0
    views_count: int = 0
    recruiter_id: str | None = None
    hiring_manager_id: str | None = None
    condominium_id: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Computed
    is_open: bool
    is_expired: bool
    remaining_vacancies: int
    is_fully_filled: bool
    salary_range: str


class JobPositionListResponse(BaseModel):
    """Schema de lista de vagas."""

    items: list[JobPositionResponse]
    total: int
    page: int
    page_size: int
    pages: int


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

    channels: list[str] | None = Field(default_factory=list)
    post_to_linkedin: bool = False
    post_to_indeed: bool = False
    post_to_catho: bool = False
    post_to_website: bool = True


class SelectionStage(BaseModel):
    """Schema para etapa do processo seletivo."""

    name: str
    description: str | None = None
    order: int = 1
    stage_type: str = "interview"
    is_mandatory: bool = True
    is_eliminatory: bool = True
    weight: float = 1.0
    duration_days: int = 7
    responsible_id: str | None = None
