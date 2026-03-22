"""
Schemas Pydantic para AdmissionProcess (Processo de Admissão).
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.people_management.hr.models.admission import AdmissionStatus


class AdmissionProcessCreate(BaseModel):
    """Schema para criação de processo de admissão."""

    candidate_id: str | None = None
    job_position_id: str | None = None
    expected_start_date: date | None = None
    salary_proposed: float | None = Field(None, ge=0)
    workplace_id: str | None = None
    checklist: dict | None = None
    notes: str | None = None


class AdmissionProcessUpdate(BaseModel):
    """Schema para atualização de processo de admissão."""

    status: AdmissionStatus | None = None
    expected_start_date: date | None = None
    actual_start_date: date | None = None
    salary_proposed: float | None = Field(None, ge=0)
    workplace_id: str | None = None
    checklist: dict | None = None
    documents_received: dict | None = None
    medical_exam_date: date | None = None
    medical_exam_result: str | None = None
    contract_signed_at: datetime | None = None
    employee_id: str | None = None
    notes: str | None = None


class AdmissionProcessResponse(BaseModel):
    """Schema de resposta para processo de admissão."""

    model_config = ConfigDict(from_attributes=True)

    id: str | UUID
    candidate_id: str | UUID | None = None
    employee_id: str | UUID | None = None
    job_position_id: str | UUID | None = None
    status: str
    expected_start_date: date | None = None
    actual_start_date: date | None = None
    salary_proposed: float | None = None
    workplace_id: str | UUID | None = None
    checklist: dict | None = None
    documents_received: dict | None = None
    medical_exam_date: date | None = None
    medical_exam_result: str | None = None
    contract_signed_at: datetime | None = None
    notes: str | None = None
    created_by_id: str | UUID | None = None
    created_at: datetime
    updated_at: datetime
