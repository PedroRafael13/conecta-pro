"""Schemas Pydantic para WorkSchedule."""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from modules.hr.time_tracking.models import (
    ScheduleType,
    ScheduleStatus,
    DayOfWeek,
)


class DailyScheduleEntry(BaseModel):
    """Horário de um dia específico."""

    entry: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    exit: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    break_start: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    break_end: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")


class AllowedLocation(BaseModel):
    """Localização permitida para registro."""

    name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    max_distance: int = Field(100, ge=10, le=5000)


class WorkScheduleBase(BaseModel):
    """Schema base para WorkSchedule."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    schedule_type: ScheduleType = ScheduleType.CLT_44H

    # Carga horária
    weekly_hours_minutes: int = Field(2640, ge=60, le=3600)  # 1h a 60h
    daily_hours_minutes: int = Field(528, ge=60, le=720)  # 1h a 12h
    max_daily_hours_minutes: int = Field(600, ge=60, le=720)

    # Horário padrão
    default_entry_time: Optional[time] = None
    default_exit_time: Optional[time] = None
    default_break_start: Optional[time] = None
    default_break_end: Optional[time] = None
    break_duration_minutes: int = Field(60, ge=0, le=180)


class WorkScheduleCreate(WorkScheduleBase):
    """Schema para criação de WorkSchedule."""

    # Funcionário (se não for template)
    employee_id: Optional[str] = Field(None, max_length=50)
    employee_name: Optional[str] = Field(None, max_length=200)
    is_template: bool = False

    # Departamento
    department_id: Optional[str] = Field(None, max_length=50)
    department_name: Optional[str] = Field(None, max_length=100)

    # Horários por dia
    daily_schedule: Optional[dict] = None
    work_days: Optional[List[str]] = None
    days_off: Optional[List[str]] = None

    # Tolerâncias
    entry_tolerance_minutes: int = Field(10, ge=0, le=60)
    exit_tolerance_minutes: int = Field(10, ge=0, le=60)
    break_tolerance_minutes: int = Field(5, ge=0, le=30)

    # Horas extras
    overtime_requires_approval: bool = True
    max_overtime_daily_minutes: int = Field(120, ge=0, le=240)
    max_overtime_weekly_minutes: int = Field(600, ge=0, le=1200)
    overtime_multiplier_50: Decimal = Field(Decimal("1.50"), ge=1, le=3)
    overtime_multiplier_100: Decimal = Field(Decimal("2.00"), ge=1, le=4)
    use_time_bank: bool = False

    # Noturno
    night_shift_start: time = time(22, 0)
    night_shift_end: time = time(5, 0)
    night_shift_multiplier: Decimal = Field(Decimal("1.20"), ge=1, le=2)

    # Banco de horas
    time_bank_expiry_months: int = Field(6, ge=1, le=12)
    time_bank_max_positive_hours: int = Field(40, ge=0, le=200)
    time_bank_max_negative_hours: int = Field(20, ge=0, le=100)

    # Geolocalização
    require_geolocation: bool = False
    allowed_locations: Optional[List[AllowedLocation]] = None
    max_distance_meters: int = Field(100, ge=10, le=5000)

    # Biometria
    require_biometric: bool = True
    min_biometric_score: int = Field(80, ge=0, le=100)
    require_face_match: bool = False
    require_liveness: bool = True

    # Feriados
    consider_holidays: bool = True
    holiday_calendar_id: Optional[str] = Field(None, max_length=50)

    # Validade
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    # Local
    condominium_id: Optional[str] = Field(None, max_length=50)
    condominium_name: Optional[str] = Field(None, max_length=200)

    notes: Optional[str] = None

    @field_validator("work_days")
    @classmethod
    def validate_work_days(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Valida dias de trabalho."""
        if v:
            valid_days = [d.value for d in DayOfWeek]
            for day in v:
                if day not in valid_days:
                    raise ValueError(f"Dia inválido: {day}")
        return v


class WorkScheduleUpdate(BaseModel):
    """Schema para atualização de WorkSchedule."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    status: Optional[ScheduleStatus] = None

    weekly_hours_minutes: Optional[int] = Field(None, ge=60, le=3600)
    daily_hours_minutes: Optional[int] = Field(None, ge=60, le=720)

    default_entry_time: Optional[time] = None
    default_exit_time: Optional[time] = None
    default_break_start: Optional[time] = None
    default_break_end: Optional[time] = None

    daily_schedule: Optional[dict] = None
    work_days: Optional[List[str]] = None

    entry_tolerance_minutes: Optional[int] = Field(None, ge=0, le=60)
    exit_tolerance_minutes: Optional[int] = Field(None, ge=0, le=60)

    overtime_requires_approval: Optional[bool] = None
    use_time_bank: Optional[bool] = None

    require_geolocation: Optional[bool] = None
    allowed_locations: Optional[List[AllowedLocation]] = None

    require_biometric: Optional[bool] = None
    min_biometric_score: Optional[int] = Field(None, ge=0, le=100)

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    notes: Optional[str] = None


class WorkScheduleResponse(WorkScheduleBase):
    """Schema de resposta para WorkSchedule."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    status: ScheduleStatus

    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    is_template: bool = False

    department_id: Optional[str] = None
    department_name: Optional[str] = None

    daily_schedule: Optional[dict] = None
    work_days: Optional[List[str]] = None
    days_off: Optional[List[str]] = None

    entry_tolerance_minutes: int = 10
    exit_tolerance_minutes: int = 10
    break_tolerance_minutes: int = 5

    overtime_requires_approval: bool = True
    max_overtime_daily_minutes: int = 120
    use_time_bank: bool = False

    night_shift_start: time
    night_shift_end: time

    time_bank_balance_minutes: int = 0

    require_geolocation: bool = False
    allowed_locations: Optional[List[dict]] = None

    require_biometric: bool = True
    min_biometric_score: int = 80

    consider_holidays: bool = True

    valid_from: Optional[date] = None
    valid_until: Optional[date] = None

    condominium_id: Optional[str] = None
    condominium_name: Optional[str] = None

    # Calculados
    weekly_hours: float
    daily_hours: float
    time_bank_hours: float
    is_valid: bool
    schedule_type_display: str

    created_at: datetime
    updated_at: datetime


class WorkScheduleListResponse(BaseModel):
    """Schema para listagem de WorkSchedule."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    schedule_type: ScheduleType
    schedule_type_display: str
    status: ScheduleStatus
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    is_template: bool = False
    weekly_hours: float
    is_valid: bool
    condominium_name: Optional[str] = None


class WorkScheduleFilter(BaseModel):
    """Schema para filtros de WorkSchedule."""

    employee_id: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    status: Optional[ScheduleStatus] = None
    department_id: Optional[str] = None
    condominium_id: Optional[str] = None
    is_template: Optional[bool] = None
    is_valid: Optional[bool] = None


class WorkScheduleStats(BaseModel):
    """Schema para estatísticas de WorkSchedule."""

    total_schedules: int = 0
    active_schedules: int = 0
    template_schedules: int = 0
    by_type: dict = Field(default_factory=dict)
    by_status: dict = Field(default_factory=dict)
    average_weekly_hours: float = 0


class WorkScheduleValidation(BaseModel):
    """Schema para validação de regras CLT."""

    is_valid: bool = True
    violations: List[str] = []
    warnings: List[str] = []
