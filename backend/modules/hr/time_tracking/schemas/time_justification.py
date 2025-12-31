"""Schemas Pydantic para TimeJustification."""

from datetime import datetime, date, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.hr.time_tracking.models import (
    JustificationType,
    JustificationStatus,
    JustificationCategory,
)


class AttachmentInfo(BaseModel):
    """Informação de anexo."""

    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=500)
    type: str = Field(..., min_length=1, max_length=100)
    size: int = Field(..., ge=0)


class MedicalInfo(BaseModel):
    """Informações médicas."""

    cid_code: Optional[str] = Field(None, max_length=10)
    cid_description: Optional[str] = Field(None, max_length=200)
    certificate_number: Optional[str] = Field(None, max_length=50)
    doctor_name: Optional[str] = Field(None, max_length=200)
    doctor_crm: Optional[str] = Field(None, max_length=20)
    clinic_name: Optional[str] = Field(None, max_length=200)


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

    employee_registration: Optional[str] = Field(None, max_length=50)
    department_id: Optional[str] = Field(None, max_length=50)
    department_name: Optional[str] = Field(None, max_length=100)

    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_full_day: bool = True

    description: Optional[str] = Field(None, max_length=1000)
    detailed_reason: Optional[str] = Field(None, max_length=2000)

    # Médico
    medical_info: Optional[MedicalInfo] = None

    # Registros vinculados
    time_entry_ids: Optional[List[str]] = None

    # Jornada
    work_schedule_id: Optional[str] = Field(None, max_length=50)

    # Local
    condominium_id: Optional[str] = Field(None, max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)

    notes: Optional[str] = None


class TimeJustificationUpdate(BaseModel):
    """Schema para atualização de TimeJustification."""

    justification_type: Optional[JustificationType] = None
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_full_day: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=1000)
    detailed_reason: Optional[str] = Field(None, max_length=2000)
    medical_info: Optional[MedicalInfo] = None
    notes: Optional[str] = None


class TimeJustificationAnalysis(BaseModel):
    """Schema para análise."""

    notes: Optional[str] = Field(None, max_length=500)


class TimeJustificationApproval(BaseModel):
    """Schema para aprovação."""

    approved: bool = True
    notes: Optional[str] = Field(None, max_length=500)


class TimeJustificationPartialApproval(BaseModel):
    """Schema para aprovação parcial."""

    approved_days: Optional[int] = Field(None, ge=0)
    approved_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class TimeJustificationRejection(BaseModel):
    """Schema para rejeição."""

    reason: str = Field(..., min_length=10, max_length=500)


class TimeJustificationVerification(BaseModel):
    """Schema para verificação RH."""

    notes: Optional[str] = Field(None, max_length=500)


class TimeJustificationResponse(TimeJustificationBase):
    """Schema de resposta para TimeJustification."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    category: JustificationCategory
    status: JustificationStatus

    employee_registration: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None

    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_full_day: bool = True
    days_count: int = 1
    hours_count: int = 0
    minutes_justified: int = 0

    description: Optional[str] = None
    detailed_reason: Optional[str] = None

    has_attachments: bool = False
    attachments: Optional[List[dict]] = None

    cid_code: Optional[str] = None
    cid_description: Optional[str] = None
    medical_certificate_number: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_crm: Optional[str] = None
    clinic_name: Optional[str] = None

    time_entry_ids: Optional[List[str]] = None

    analyzed_by_name: Optional[str] = None
    analyzed_at: Optional[datetime] = None

    requires_approval: bool = True
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None

    approval_level: int = 1
    max_approval_level: int = 1
    approval_history: Optional[List[dict]] = None

    rejected_by_name: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    partial_approved_days: Optional[int] = None
    partial_approved_minutes: Optional[int] = None

    grants_paid_leave: bool = False
    affects_dsr: bool = True

    deadline_for_submission: Optional[datetime] = None
    is_late_submission: bool = False
    late_submission_days: int = 0

    is_verified: bool = False
    verified_by_name: Optional[str] = None
    verified_at: Optional[datetime] = None

    condominium_name: Optional[str] = None

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
    submitted_at: Optional[datetime] = None


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
    condominium_name: Optional[str] = None


class TimeJustificationFilter(BaseModel):
    """Schema para filtros de TimeJustification."""

    employee_id: Optional[str] = None
    justification_type: Optional[JustificationType] = None
    category: Optional[JustificationCategory] = None
    status: Optional[JustificationStatus] = None
    condominium_id: Optional[str] = None
    department_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_pending: Optional[bool] = None
    is_verified: Optional[bool] = None
    has_attachments: Optional[bool] = None
    is_late_submission: Optional[bool] = None


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
