"""
Schemas Pydantic v2 para Treinamento e Desenvolvimento.

Define schemas de criacao, atualizacao, resposta e listagem
para cursos, treinamentos, matriculas e certificados.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.people_management.human_resources.models.training import (
    CertificateStatus,
    EnrollmentStatus,
    TrainingCategoryCourse,
    TrainingStatus,
)

# =============================================================================
# Training Course Schemas
# =============================================================================


class TrainingCourseBase(BaseModel):
    """Schema base para curso de treinamento."""

    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    category: TrainingCategoryCourse = TrainingCategoryCourse.OTHER
    duration_hours: float = Field(1.0, gt=0, le=1000)
    max_participants: int | None = Field(None, gt=0, le=500)
    is_mandatory: bool = False
    is_active: bool = True
    required_for_workplace_types: list[str] | None = Field(default_factory=list)
    validity_months: int | None = Field(None, gt=0, le=120)
    syllabus: dict | None = None
    instructor_name: str | None = Field(None, max_length=200)
    instructor_qualification: str | None = None
    cost_per_participant: float | None = Field(None, ge=0)
    provider: str | None = Field(None, max_length=200)


class TrainingCourseCreate(TrainingCourseBase):
    """Schema para criacao de curso de treinamento."""

    pass


class TrainingCourseUpdate(BaseModel):
    """Schema para atualizacao de curso de treinamento."""

    name: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = None
    category: TrainingCategoryCourse | None = None
    duration_hours: float | None = Field(None, gt=0, le=1000)
    max_participants: int | None = Field(None, gt=0, le=500)
    is_mandatory: bool | None = None
    is_active: bool | None = None
    required_for_workplace_types: list[str] | None = None
    validity_months: int | None = Field(None, gt=0, le=120)
    syllabus: dict | None = None
    instructor_name: str | None = Field(None, max_length=200)
    instructor_qualification: str | None = None
    cost_per_participant: float | None = Field(None, ge=0)
    provider: str | None = Field(None, max_length=200)


class TrainingCourseResponse(TrainingCourseBase):
    """Schema de resposta para curso de treinamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    participants_count: int | None = None


class TrainingCourseListResponse(BaseModel):
    """Schema de listagem de cursos de treinamento."""

    items: list[TrainingCourseResponse]
    total: int
    page: int = 1
    page_size: int = 20


# =============================================================================
# Training Schemas
# =============================================================================


class TrainingBase(BaseModel):
    """Schema base para treinamento/turma."""

    course_id: UUID
    title: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    start_date: datetime
    end_date: datetime | None = None
    location: str | None = Field(None, max_length=300)
    instructor_name: str | None = Field(None, max_length=200)
    max_participants: int | None = Field(None, gt=0, le=500)
    workplace_id: UUID | None = None
    notes: str | None = None


class TrainingCreate(TrainingBase):
    """Schema para criacao de treinamento/turma."""

    pass


class TrainingUpdate(BaseModel):
    """Schema para atualizacao de treinamento/turma."""

    title: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    location: str | None = Field(None, max_length=300)
    status: TrainingStatus | None = None
    instructor_name: str | None = Field(None, max_length=200)
    max_participants: int | None = Field(None, gt=0, le=500)
    workplace_id: UUID | None = None
    notes: str | None = None


class TrainingResponse(TrainingBase):
    """Schema de resposta para treinamento/turma."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: TrainingStatus
    current_participants: int
    created_by_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class TrainingListResponse(BaseModel):
    """Schema de listagem de treinamentos."""

    items: list[TrainingResponse]
    total: int
    page: int = 1
    page_size: int = 20


# =============================================================================
# Training Enrollment Schemas
# =============================================================================


class TrainingEnrollmentCreate(BaseModel):
    """Schema para criacao de matricula."""

    training_id: UUID
    employee_id: UUID


class TrainingEnrollmentUpdate(BaseModel):
    """Schema para atualizacao de matricula."""

    status: EnrollmentStatus | None = None
    score: float | None = Field(None, ge=0, le=100)
    feedback: str | None = None


class TrainingEnrollmentResponse(BaseModel):
    """Schema de resposta para matricula."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    training_id: UUID
    employee_id: UUID
    status: EnrollmentStatus
    enrolled_at: datetime
    confirmed_at: datetime | None = None
    attended_at: datetime | None = None
    score: float | None = None
    feedback: str | None = None
    certificate_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class TrainingEnrollmentListResponse(BaseModel):
    """Schema de listagem de matriculas."""

    items: list[TrainingEnrollmentResponse]
    total: int
    page: int = 1
    page_size: int = 20


# =============================================================================
# Training Certificate Schemas
# =============================================================================


class TrainingCertificateResponse(BaseModel):
    """Schema de resposta para certificado de treinamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    enrollment_id: UUID
    employee_id: UUID
    course_id: UUID
    certificate_number: str
    issued_at: datetime
    expires_at: datetime | None = None
    status: CertificateStatus
    revoked_at: datetime | None = None
    revocation_reason: str | None = None
    document_path: str | None = None
    created_at: datetime
    employee_name: str | None = None
    course_name: str | None = None


class TrainingCertificateListResponse(BaseModel):
    """Schema de listagem de certificados."""

    items: list[TrainingCertificateResponse]
    total: int
    page: int = 1
    page_size: int = 20
