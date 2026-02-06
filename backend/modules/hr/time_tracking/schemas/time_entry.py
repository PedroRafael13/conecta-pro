"""Schemas Pydantic para TimeEntry."""

from datetime import datetime, date, time
from decimal import Decimal  # pylint: disable=unused-import
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.hr.time_tracking.models import (
    EntryType,
    RegistrationMethod,
    EntryStatus,
    AnomalyType,
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

    employee_registration: Optional[str] = Field(None, max_length=50)
    department_id: Optional[str] = Field(None, max_length=50)
    department_name: Optional[str] = Field(None, max_length=100)
    position_name: Optional[str] = Field(None, max_length=100)
    work_schedule_id: Optional[str] = Field(None, max_length=50)


class TimeEntryCreate(TimeEntryBase):
    """Schema para criação de TimeEntry."""

    # Geolocalização
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    accuracy_meters: Optional[float] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=500)

    # Dispositivo
    device_id: Optional[str] = Field(None, max_length=100)
    device_name: Optional[str] = Field(None, max_length=200)
    device_type: Optional[str] = Field(None, max_length=50)
    device_ip: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = Field(None, max_length=500)
    app_version: Optional[str] = Field(None, max_length=20)

    # Biometria
    biometric_score: Optional[float] = Field(None, ge=0, le=100)
    biometric_template_id: Optional[str] = Field(None, max_length=100)
    face_match_score: Optional[float] = Field(None, ge=0, le=100)
    photo_url: Optional[str] = Field(None, max_length=500)

    # REP
    rep_id: Optional[str] = Field(None, max_length=50)
    rep_serial: Optional[str] = Field(None, max_length=50)
    nsr: Optional[int] = Field(None, ge=0)
    pis_pasep: Optional[str] = Field(None, max_length=15)

    # Local
    condominium_id: Optional[str] = Field(None, max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)
    work_location_id: Optional[str] = Field(None, max_length=50)
    work_location_name: Optional[str] = Field(None, max_length=200)

    notes: Optional[str] = None


class TimeEntryUpdate(BaseModel):
    """Schema para atualização de TimeEntry."""

    entry_time: Optional[time] = None
    entry_datetime: Optional[datetime] = None
    status: Optional[EntryStatus] = None
    notes: Optional[str] = None
    adjustment_reason: Optional[str] = None


class TimeEntryManualAdjust(BaseModel):
    """Schema para ajuste manual."""

    new_time: time
    reason: str = Field(..., min_length=10, max_length=500)


class TimeEntryApproval(BaseModel):
    """Schema para aprovação."""

    approved: bool = True
    notes: Optional[str] = Field(None, max_length=500)


class TimeEntryResponse(TimeEntryBase):
    """Schema de resposta para TimeEntry."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    status: EntryStatus
    expected_time: Optional[time] = None
    tolerance_minutes: int = 10
    difference_minutes: int = 0
    is_late: bool = False
    is_early: bool = False
    is_overtime: bool = False

    # Geolocalização
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_within_allowed_area: bool = True
    distance_from_work_meters: Optional[float] = None

    # Biometria
    biometric_score: Optional[float] = None
    is_valid_biometric: bool = True

    # Anomalia
    anomaly_type: AnomalyType = AnomalyType.SEM_ANOMALIA
    anomaly_description: Optional[str] = None
    anomaly_resolved: bool = False
    has_anomaly: bool = False

    # Justificativa
    has_justification: bool = False
    justification_id: Optional[str] = None

    # Ajuste
    is_manual_entry: bool = False
    original_time: Optional[time] = None
    adjusted_by_name: Optional[str] = None
    adjusted_at: Optional[datetime] = None

    # Aprovação
    requires_approval: bool = False
    is_pending_approval: bool = False
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None

    # Noturno
    is_night_shift: bool = False
    night_hours_minutes: int = 0

    # Local
    condominium_name: Optional[str] = None
    work_location_name: Optional[str] = None

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
    condominium_name: Optional[str] = None


class TimeEntryFilter(BaseModel):
    """Schema para filtros de TimeEntry."""

    employee_id: Optional[str] = None
    entry_type: Optional[EntryType] = None
    status: Optional[EntryStatus] = None
    registration_method: Optional[RegistrationMethod] = None
    anomaly_type: Optional[AnomalyType] = None
    condominium_id: Optional[str] = None
    department_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    has_anomaly: Optional[bool] = None
    requires_approval: Optional[bool] = None
    is_manual_entry: Optional[bool] = None


class TimeEntryStats(BaseModel):
    """Schema para estatísticas de TimeEntry."""

    total_entries: int = 0
    entries_by_type: dict = Field(default_factory=dict)
    entries_by_status: dict = Field(default_factory=dict)
    anomaly_count: int = 0
    anomaly_by_type: dict = Field(default_factory=dict)
    pending_approval_count: int = 0
    manual_entries_count: int = 0
    average_arrival_time: Optional[str] = None
    late_count: int = 0
    early_count: int = 0


class TimeEntryDaySummary(BaseModel):
    """Resumo do dia."""

    date: date
    entries: List[TimeEntryListResponse] = []
    total_entries: int = 0
    has_entry: bool = False
    has_exit: bool = False
    has_break: bool = False
    worked_minutes: int = 0
    expected_minutes: int = 0
    overtime_minutes: int = 0
    late_minutes: int = 0
    anomalies: List[str] = []
