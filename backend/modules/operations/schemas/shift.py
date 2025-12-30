"""
Schemas Pydantic para Shift (Turno de Trabalho).
"""

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from modules.operations.models.shift import ShiftStatus


class ShiftBase(BaseModel):
    """Schema base para Shift."""

    scale_id: str = Field(..., description="ID da escala")
    employee_id: Optional[str] = Field(None, description="ID do funcionário")
    post_id: Optional[str] = Field(None, description="ID do posto")
    shift_date: date = Field(..., description="Data do turno")
    start_time: time = Field(..., description="Hora de início")
    end_time: time = Field(..., description="Hora de fim")
    is_off_day: bool = Field(default=False, description="É dia de folga")
    notes: Optional[str] = Field(None, description="Observações")


class ShiftCreate(ShiftBase):
    """Schema para criação de Shift."""

    is_holiday: bool = Field(default=False, description="É feriado")
    is_sunday: bool = Field(default=False, description="É domingo")
    is_night_shift: bool = Field(default=False, description="É turno noturno")
    planned_hours: float = Field(default=0.0, ge=0, description="Horas planejadas")


class ShiftUpdate(BaseModel):
    """Schema para atualização parcial de Shift."""

    employee_id: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    actual_start_time: Optional[time] = None
    actual_end_time: Optional[time] = None
    actual_break_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[ShiftStatus] = None
    is_off_day: Optional[bool] = None
    actual_hours: Optional[float] = Field(None, ge=0)
    overtime_hours: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    absence_reason: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class ShiftResponse(BaseModel):
    """Schema de resposta para Shift."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    scale_id: str
    employee_id: Optional[str]
    post_id: Optional[str]
    shift_date: date
    start_time: time
    end_time: time
    actual_start_time: Optional[time]
    actual_end_time: Optional[time]
    actual_break_minutes: int
    status: str
    is_holiday: bool
    is_sunday: bool
    is_night_shift: bool
    is_off_day: bool
    planned_hours: float
    actual_hours: float
    overtime_hours: float
    night_hours: float
    base_cost: float
    overtime_cost: float
    night_bonus: float
    holiday_bonus: float
    total_cost: float
    notes: Optional[str]
    absence_reason: Optional[str]
    original_employee_id: Optional[str]
    substitution_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_future: bool
    is_today: bool
    is_filled: bool
    was_worked: bool
    needs_substitution: bool


class ShiftListResponse(BaseModel):
    """Schema para listagem paginada de Shifts."""

    items: List[ShiftResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ShiftFilter(BaseModel):
    """Schema para filtros de busca de Shifts."""

    scale_id: Optional[str] = None
    employee_id: Optional[str] = None
    post_id: Optional[str] = None
    status: Optional[ShiftStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_holiday: Optional[bool] = None
    is_night_shift: Optional[bool] = None
    is_off_day: Optional[bool] = None
    is_filled: Optional[bool] = None
    needs_substitution: Optional[bool] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "ShiftFilter":
        """Valida range de datas."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date deve ser anterior a end_date")
        return self


class ShiftBulkCreate(BaseModel):
    """Schema para criação em lote de Shifts."""

    shifts: List[ShiftCreate] = Field(..., min_length=1, description="Lista de turnos")


class ShiftCheckIn(BaseModel):
    """Schema para registro de entrada."""

    actual_start_time: time = Field(..., description="Hora real de entrada")
    notes: Optional[str] = Field(None, description="Observações")


class ShiftCheckOut(BaseModel):
    """Schema para registro de saída."""

    actual_end_time: time = Field(..., description="Hora real de saída")
    actual_break_minutes: int = Field(default=0, ge=0, description="Intervalo em minutos")
    notes: Optional[str] = Field(None, description="Observações")
