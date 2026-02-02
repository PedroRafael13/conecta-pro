"""
Schemas Pydantic para Shift (Turno de Trabalho).
"""

from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from modules.operacional.models.shift import ShiftStatus


class ShiftBase(BaseModel):
    """Schema base para Shift."""

    scale_id: str = Field(..., description="ID da escala")
    employee_id: str | None = Field(None, description="ID do funcionário")
    post_id: str = Field(..., description="ID do posto")
    shift_date: date = Field(..., description="Data do turno")
    planned_start_time: time = Field(..., description="Hora de início planejada")
    planned_end_time: time = Field(..., description="Hora de fim planejada")
    planned_break_minutes: int = Field(default=60, ge=0, description="Intervalo em minutos")
    is_off_day: bool = Field(default=False, description="É dia de folga")
    notes: str | None = Field(None, description="Observações")


class ShiftCreate(ShiftBase):
    """Schema para criação de Shift."""

    is_holiday: bool = Field(default=False, description="É feriado")
    is_night_shift: bool = Field(default=False, description="É turno noturno")
    is_overtime: bool = Field(default=False, description="É hora extra")
    planned_hours: float = Field(default=0.0, ge=0, description="Horas planejadas")

    @model_validator(mode="after")
    def validate_time_range(self):
        """Valida que horário de início é antes do fim."""
        if self.planned_start_time and self.planned_end_time:
            # Para turnos que cruzam meia-noite (ex: 22h às 6h), permitir
            # Mas validar se são horários diferentes
            if self.planned_start_time == self.planned_end_time:
                raise ValueError("Horário de início e fim não podem ser iguais")

            # Se não é turno noturno, validar ordem normal
            if not self.is_night_shift and self.planned_start_time >= self.planned_end_time:
                raise ValueError(
                    f"Horário de início ({self.planned_start_time}) deve ser anterior ao horário de fim ({self.planned_end_time}). "
                    "Para turnos noturnos que cruzam meia-noite, marque 'is_night_shift=true'"
                )

        return self


class ShiftUpdate(BaseModel):
    """Schema para atualização parcial de Shift."""

    employee_id: str | None = None
    planned_start_time: time | None = None
    planned_end_time: time | None = None
    planned_break_minutes: int | None = Field(None, ge=0)
    actual_start_time: datetime | None = None
    actual_end_time: datetime | None = None
    actual_break_minutes: int | None = Field(None, ge=0)
    status: ShiftStatus | None = None
    is_off_day: bool | None = None
    is_overtime: bool | None = None
    needs_substitution: bool | None = None
    actual_hours: float | None = Field(None, ge=0)
    overtime_hours: float | None = Field(None, ge=0)
    notes: str | None = None
    is_active: bool | None = None
    is_night_shift: bool | None = None

    @model_validator(mode="after")
    def validate_time_range(self):
        """Valida horários planejados e reais."""
        # Validar horários planejados
        if self.planned_start_time and self.planned_end_time:
            if self.planned_start_time == self.planned_end_time:
                raise ValueError("Horário de início e fim não podem ser iguais")

            if not self.is_night_shift and self.planned_start_time >= self.planned_end_time:
                raise ValueError(
                    "Horário planejado de início deve ser anterior ao fim. "
                    "Para turnos noturnos, marque 'is_night_shift=true'"
                )

        # Validar horários reais
        if self.actual_start_time and self.actual_end_time:
            if self.actual_start_time >= self.actual_end_time:
                raise ValueError(
                    f"Horário real de início ({self.actual_start_time}) deve ser anterior ao fim ({self.actual_end_time})"
                )

        return self


class ShiftResponse(BaseModel):
    """Schema de resposta para Shift."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    scale_id: str
    employee_id: str | None
    post_id: str
    shift_date: date
    planned_start_time: time
    planned_end_time: time
    planned_break_minutes: int
    actual_start_time: datetime | None
    actual_end_time: datetime | None
    actual_break_minutes: int | None
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
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    @computed_field
    @property
    def is_future(self) -> bool:
        """Turno futuro."""
        return self.shift_date > date.today()

    @computed_field
    @property
    def is_today(self) -> bool:
        """Turno de hoje."""
        return self.shift_date == date.today()

    @computed_field
    @property
    def is_filled(self) -> bool:
        """Turno com funcionário alocado."""
        return self.employee_id is not None

    @computed_field
    @property
    def was_worked(self) -> bool:
        """Turno trabalhado."""
        return self.status == "completed"


class ShiftListResponse(BaseModel):
    """Schema para listagem paginada de Shifts."""

    items: list[ShiftResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ShiftFilter(BaseModel):
    """Schema para filtros de busca de Shifts."""

    scale_id: str | None = None
    employee_id: str | None = None
    post_id: str | None = None
    status: ShiftStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_holiday: bool | None = None
    is_night_shift: bool | None = None
    is_off_day: bool | None = None
    is_filled: bool | None = None
    needs_substitution: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "ShiftFilter":
        """Valida range de datas."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date deve ser anterior a end_date")
        return self


class ShiftBulkCreate(BaseModel):
    """Schema para criação em lote de Shifts."""

    shifts: list[ShiftCreate] = Field(..., min_length=1, description="Lista de turnos")


class ShiftCheckIn(BaseModel):
    """Schema para registro de entrada."""

    actual_start_time: datetime = Field(..., description="Hora real de entrada")
    notes: str | None = Field(None, description="Observações")


class ShiftCheckOut(BaseModel):
    """Schema para registro de saída."""

    actual_end_time: datetime = Field(..., description="Hora real de saída")
    actual_break_minutes: int = Field(default=0, ge=0, description="Intervalo em minutos")
    notes: str | None = Field(None, description="Observações")


class ShiftBulkUpdateItem(BaseModel):
    """Item individual para atualização em lote de shifts."""

    shift_id: str = Field(..., description="ID do turno")
    data: ShiftUpdate = Field(..., description="Dados para atualização")


class ShiftBulkUpdate(BaseModel):
    """Schema para atualização em lote de shifts."""

    items: list[ShiftBulkUpdateItem] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Lista de turnos para atualizar (máximo 100)",
    )


class ShiftBulkOperationResult(BaseModel):
    """Resultado de operação em lote de shifts."""

    success_count: int = Field(..., description="Quantidade de sucessos")
    error_count: int = Field(..., description="Quantidade de erros")
    errors: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de erros (ID + mensagem)",
    )
