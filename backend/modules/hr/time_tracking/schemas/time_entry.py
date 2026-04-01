"""Schemas Pydantic para TimeEntry."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.hr.time_tracking.models import (
    AnomalyType,
    EntryStatus,
    EntryType,
    RegistrationMethod,
)


class TimeEntryBase(BaseModel):
    """Schema base para TimeEntry."""

    employee_id: str = Field(..., min_length=1, max_length=50)
    employee_name: str = Field(..., min_length=1, max_length=200)
    entry_type: EntryType = EntryType.ENTRADA
    registration_method: RegistrationMethod = RegistrationMethod.BIOMETRIA_DIGITAL
    entry_date: date
    entry_time: time
    entry_datetime: datetime

    employee_registration: str | None = Field(None, max_length=50)
    department_id: str | None = Field(None, max_length=50)
    department_name: str | None = Field(None, max_length=100)
    position_name: str | None = Field(None, max_length=100)
    work_schedule_id: str | None = Field(None, max_length=50)


class TimeEntryCreate(TimeEntryBase):
    """Schema para criação de TimeEntry."""

    # Geolocalização
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    accuracy_meters: float | None = Field(None, ge=0)
    address: str | None = Field(None, max_length=500)

    # Dispositivo
    device_id: str | None = Field(None, max_length=100)
    device_name: str | None = Field(None, max_length=200)
    device_type: str | None = Field(None, max_length=50)
    device_ip: str | None = Field(None, max_length=50)
    user_agent: str | None = Field(None, max_length=500)
    app_version: str | None = Field(None, max_length=20)

    # Biometria
    biometric_score: float | None = Field(None, ge=0, le=100)
    biometric_template_id: str | None = Field(None, max_length=100)
    face_match_score: float | None = Field(None, ge=0, le=100)
    photo_url: str | None = Field(None, max_length=500)

    # REP
    rep_id: str | None = Field(None, max_length=50)
    rep_serial: str | None = Field(None, max_length=50)
    nsr: int | None = Field(None, ge=0)
    pis_pasep: str | None = Field(None, max_length=15)

    # Local
    condominium_id: str | None = Field(None, max_length=50)
    condominium_name: str | None = Field(None, max_length=200)
    work_location_id: str | None = Field(None, max_length=50)
    work_location_name: str | None = Field(None, max_length=200)

    notes: str | None = None


class TimeEntryUpdate(BaseModel):
    """Schema para atualização de TimeEntry."""

    entry_time: time | None = None
    entry_datetime: datetime | None = None
    status: EntryStatus | None = None
    notes: str | None = None
    adjustment_reason: str | None = None


class TimeEntryManualAdjust(BaseModel):
    """Schema para ajuste manual."""

    new_time: time
    reason: str = Field(..., min_length=10, max_length=500)


class TimeEntryApproval(BaseModel):
    """Schema para aprovação."""

    approved: bool = True
    notes: str | None = Field(None, max_length=500)


class TimeEntryResponse(TimeEntryBase):
    """Schema de resposta para TimeEntry."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    status: EntryStatus
    expected_time: time | None = None
    tolerance_minutes: int = 10
    difference_minutes: int = 0
    is_late: bool = False
    is_early: bool = False
    is_overtime: bool = False

    # Geolocalização
    latitude: float | None = None
    longitude: float | None = None
    is_within_allowed_area: bool = True
    distance_from_work_meters: float | None = None

    # Biometria
    biometric_score: float | None = None
    is_valid_biometric: bool = True

    # Anomalia
    anomaly_type: AnomalyType = AnomalyType.SEM_ANOMALIA
    anomaly_description: str | None = None
    anomaly_resolved: bool = False
    has_anomaly: bool = False

    # Justificativa
    has_justification: bool = False
    justification_id: str | None = None

    # Ajuste
    is_manual_entry: bool = False
    original_time: time | None = None
    adjusted_by_name: str | None = None
    adjusted_at: datetime | None = None

    # Aprovação
    requires_approval: bool = False
    is_pending_approval: bool = False
    approved_by_name: str | None = None
    approved_at: datetime | None = None

    # Noturno
    is_night_shift: bool = False
    night_hours_minutes: int = 0

    # Local
    condominium_name: str | None = None
    work_location_name: str | None = None

    # Formatado
    time_formatted: str
    datetime_formatted: str
    entry_type_display: str

    # Controle
    created_at: datetime
    updated_at: datetime


class TimeEntryListResponse(BaseModel):
    """Schema para listagem de TimeEntry."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    employee_id: str
    employee_name: str
    entry_type: EntryType
    entry_type_display: str
    entry_date: date
    entry_time: time
    status: EntryStatus
    is_late: bool = False
    is_early: bool = False
    has_anomaly: bool = False
    anomaly_type: AnomalyType = AnomalyType.SEM_ANOMALIA
    requires_approval: bool = False
    condominium_name: str | None = None


class TimeEntryFilter(BaseModel):
    """Schema para filtros de TimeEntry."""

    employee_id: str | None = None
    entry_type: EntryType | None = None
    status: EntryStatus | None = None
    registration_method: RegistrationMethod | None = None
    anomaly_type: AnomalyType | None = None
    condominium_id: str | None = None
    department_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    has_anomaly: bool | None = None
    requires_approval: bool | None = None
    is_manual_entry: bool | None = None


class TimeEntryStats(BaseModel):
    """Schema para estatísticas de TimeEntry."""

    total_entries: int = 0
    entries_by_type: dict = Field(default_factory=dict)
    entries_by_status: dict = Field(default_factory=dict)
    anomaly_count: int = 0
    anomaly_by_type: dict = Field(default_factory=dict)
    pending_approval_count: int = 0
    manual_entries_count: int = 0
    average_arrival_time: str | None = None
    late_count: int = 0
    early_count: int = 0


class TimeEntryDaySummary(BaseModel):
    """Resumo do dia."""

    employee_id: str | None = None
    date: date
    entries: list[TimeEntryListResponse] = []
    total_entries: int = 0
    has_entry: bool = False
    has_exit: bool = False
    has_break: bool = False
    worked_minutes: int = 0
    expected_minutes: int = 0
    overtime_minutes: int = 0
    late_minutes: int = 0
    anomalies: list[str] = []
