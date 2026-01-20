"""
Schemas Pydantic para Shift (Turno de Trabalho).
"""

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from modules.operacional.models.shift import ShiftStatus


class ShiftBase(BaseModel):
    """Schema base para Shift."""

    scale_id: str = Field(..., description="ID da escala")
    employee_id: Optional[str] = Field(None, description="ID do funcionário")
    post_id: str = Field(..., description="ID do posto")
    shift_date: date = Field(..., description="Data do turno")
    planned_start_time: time = Field(..., description="Hora de início planejada")
    planned_end_time: time = Field(..., description="Hora de fim planejada")
    planned_break_minutes: int = Field(default=60, ge=0, description="Intervalo em minutos")
    is_off_day: bool = Field(default=False, description="É dia de folga")
    notes: Optional[str] = Field(None, description="Observações")


class ShiftCreate(ShiftBase):
    """Schema para criação de Shift."""

    is_holiday: bool = Field(default=False, description="É feriado")
    is_night_shift: bool = Field(default=False, description="É turno noturno")
    is_overtime: bool = Field(default=False, description="É hora extra")
    planned_hours: float = Field(default=0.0, ge=0, description="Horas planejadas")


class ShiftUpdate(BaseModel):
    """Schema para atualização parcial de Shift."""

    employee_id: Optional[str] = None
    planned_start_time: Optional[time] = None
    planned_end_time: Optional[time] = None
    planned_break_minutes: Optional[int] = Field(None, ge=0)
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_break_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[ShiftStatus] = None
    is_off_day: Optional[bool] = None
    is_overtime: Optional[bool] = None
    needs_substitution: Optional[bool] = None
    actual_hours: Optional[float] = Field(None, ge=0)
    overtime_hours: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ShiftResponse(BaseModel):
    """Schema de resposta para Shift."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    scale_id: str
    employee_id: Optional[str]
    post_id: str
    shift_date: date
    planned_start_time: time
    planned_end_time: time
    planned_break_minutes: int
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    actual_break_minutes: Optional[int]
    status: str
    is_holiday: bool
    is_night_shift: bool
    is_overtime: bool
    is_off_day: bool
    needs_substitution: bool
    planned_hours: float
    actual_hours: float
    overtime_hours: float
    night_hours: float
    base_pay: float
    overtime_pay: float
    night_bonus: float
    holiday_bonus: float
    total_pay: float
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_future: bool
    is_today: bool
    is_filled: bool
    was_worked: bool


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

    actual_start_time: datetime = Field(..., description="Hora real de entrada")
    notes: Optional[str] = Field(None, description="Observações")


class ShiftCheckOut(BaseModel):
    """Schema para registro de saída."""

    actual_end_time: datetime = Field(..., description="Hora real de saída")
    actual_break_minutes: int = Field(default=0, ge=0, description="Intervalo em minutos")
    notes: Optional[str] = Field(None, description="Observações")
