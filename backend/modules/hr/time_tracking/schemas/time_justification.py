"""Schemas Pydantic para TimeJustification."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.hr.time_tracking.models import (
    JustificationCategory,
    JustificationStatus,
    JustificationType,
)


class AttachmentInfo(BaseModel):
    """Informação de anexo."""

    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., min_length=1, max_length=100)
    size: int = Field(..., ge=0)


class MedicalInfo(BaseModel):
    """Informações médicas."""

    cid_code: str | None = Field(None, max_length=10)
    cid_description: str | None = Field(None, max_length=200)
    certificate_number: str | None = Field(None, max_length=50)
    doctor_name: str | None = Field(None, max_length=200)
    doctor_crm: str | None = Field(None, max_length=20)
    clinic_name: str | None = Field(None, max_length=200)


class TimeJustificationBase(BaseModel):
    """Schema base para TimeJustification."""

    employee_id: str = Field(..., min_length=1, max_length=50)
    employee_name: str = Field(..., min_length=1, max_length=200)
    justification_type: JustificationType
    title: str = Field(..., min_length=5, max_length=200)
    start_date: date
    end_date: date


class TimeJustificationCreate(TimeJustificationBase):
    """Schema para criação de TimeJustification."""

    employee_registration: str | None = Field(None, max_length=50)
    department_id: str | None = Field(None, max_length=50)
    department_name: str | None = Field(None, max_length=100)

    start_time: time | None = None
    end_time: time | None = None
    is_full_day: bool = True

    description: str | None = Field(None, max_length=1000)
    detailed_reason: str | None = Field(None, max_length=2000)

    # Médico
    medical_info: MedicalInfo | None = None

    # Registros vinculados
    time_entry_ids: list[str] | None = None

    # Jornada
    work_schedule_id: str | None = Field(None, max_length=50)

    # Local
    condominium_id: str | None = Field(None, max_length=50)
    condominium_name: str | None = Field(None, max_length=200)

    notes: str | None = None


class TimeJustificationUpdate(BaseModel):
    """Schema para atualização de TimeJustification."""

    justification_type: JustificationType | None = None
    title: str | None = Field(None, min_length=5, max_length=200)
    start_date: date | None = None
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    is_full_day: bool | None = None
    description: str | None = Field(None, max_length=1000)
    detailed_reason: str | None = Field(None, max_length=2000)
    medical_info: MedicalInfo | None = None
    notes: str | None = None


class TimeJustificationAnalysis(BaseModel):
    """Schema para análise."""

    notes: str | None = Field(None, max_length=500)


class TimeJustificationApproval(BaseModel):
    """Schema para aprovação."""

    approved: bool = True
    notes: str | None = Field(None, max_length=500)


class TimeJustificationPartialApproval(BaseModel):
    """Schema para aprovação parcial."""

    approved_days: int | None = Field(None, ge=0)
    approved_minutes: int | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=500)


class TimeJustificationRejection(BaseModel):
    """Schema para rejeição."""

    reason: str = Field(..., min_length=10, max_length=500)


class TimeJustificationVerification(BaseModel):
    """Schema para verificação RH."""

    notes: str | None = Field(None, max_length=500)


class TimeJustificationResponse(TimeJustificationBase):
    """Schema de resposta para TimeJustification."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    category: JustificationCategory
    status: JustificationStatus

    employee_registration: str | None = None
    department_id: str | None = None
    department_name: str | None = None

    start_time: time | None = None
    end_time: time | None = None
    is_full_day: bool = True
    days_count: int = 1
    hours_count: int = 0
    minutes_justified: int = 0

    description: str | None = None
    detailed_reason: str | None = None

    has_attachments: bool = False
    attachments: list[dict] | None = None

    cid_code: str | None = None
    cid_description: str | None = None
    medical_certificate_number: str | None = None
    doctor_name: str | None = None
    doctor_crm: str | None = None
    clinic_name: str | None = None

    time_entry_ids: list[str] | None = None

    analyzed_by_name: str | None = None
    analyzed_at: datetime | None = None

    requires_approval: bool = True
    approved_by_name: str | None = None
    approved_at: datetime | None = None
    approval_notes: str | None = None

    approval_level: int = 1
    max_approval_level: int = 1
    approval_history: list[dict] | None = None

    rejected_by_name: str | None = None
    rejected_at: datetime | None = None
    rejection_reason: str | None = None

    partial_approved_days: int | None = None
    partial_approved_minutes: int | None = None

    grants_paid_leave: bool = False
    affects_dsr: bool = True

    deadline_for_submission: datetime | None = None
    is_late_submission: bool = False
    late_submission_days: int = 0

    is_verified: bool = False
    verified_by_name: str | None = None
    verified_at: datetime | None = None

    condominium_name: str | None = None

    # Calculados
    is_pending: bool
    is_approved: bool
    requires_medical_docs: bool
    is_legal_leave: bool
    period_display: str
    type_display: str
    status_display: str

    created_at: datetime
    updated_at: datetime
    submitted_at: datetime | None = None


class TimeJustificationListResponse(BaseModel):
    """Schema para listagem de TimeJustification."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    employee_id: str
    employee_name: str
    justification_type: JustificationType
    type_display: str
    category: JustificationCategory
    status: JustificationStatus
    status_display: str
    start_date: date
    end_date: date
    days_count: int
    is_pending: bool
    has_attachments: bool
    condominium_name: str | None = None


class TimeJustificationFilter(BaseModel):
    """Schema para filtros de TimeJustification."""

    employee_id: str | None = None
    justification_type: JustificationType | None = None
    category: JustificationCategory | None = None
    status: JustificationStatus | None = None
    condominium_id: str | None = None
    department_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    is_pending: bool | None = None
    is_verified: bool | None = None
    has_attachments: bool | None = None
    is_late_submission: bool | None = None


class TimeJustificationStats(BaseModel):
    """Schema para estatísticas de TimeJustification."""

    total_justifications: int = 0
    pending_count: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    total_days_justified: int = 0
    total_hours_justified: int = 0
    by_type: dict = Field(default_factory=dict)
    by_category: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    late_submissions_count: int = 0
    pending_verification_count: int = 0
