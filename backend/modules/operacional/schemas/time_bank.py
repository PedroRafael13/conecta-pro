"""
Schemas Pydantic para TimeBank (Banco de Horas).
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from modules.operacional.models.time_bank import TimeBankEntryType, TimeBankStatus


class TimeBankBase(BaseModel):
    """Schema base para TimeBank."""

    employee_id: str = Field(..., description="ID do funcionário")
    entry_type: TimeBankEntryType = Field(..., description="Tipo de entrada")
    hours: float = Field(..., description="Quantidade de horas")
    reference_date: date = Field(..., description="Data de referência")
    description: str | None = Field(None, description="Descrição")
    reason: str | None = Field(None, max_length=255, description="Motivo")

    @model_validator(mode="after")
    def validate_hours(self) -> "TimeBankBase":
        """Valida horas."""
        if self.hours == 0:
            raise ValueError("Horas não pode ser zero")
        return self


class TimeBankCreate(TimeBankBase):
    """Schema para criação de TimeBank."""

    shift_id: str | None = Field(None, description="ID do turno relacionado")
    post_id: str | None = Field(None, description="ID do posto")
    expiration_date: date | None = Field(None, description="Data de expiração")


class TimeBankUpdate(BaseModel):
    """Schema para atualização parcial de TimeBank."""

    status: TimeBankStatus | None = None
    hours: float | None = None
    description: str | None = None
    reason: str | None = Field(None, max_length=255)
    expiration_date: date | None = None
    rejection_reason: str | None = Field(None, max_length=255)
    is_active: bool | None = None


class TimeBankResponse(BaseModel):
    """Schema de resposta para TimeBank."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    entry_type: str
    status: str
    hours: float
    balance_before: float
    balance_after: float
    reference_date: date
    expiration_date: date | None
    shift_id: str | None
    post_id: str | None
    description: str | None
    reason: str | None
    approved_by: str | None
    approved_at: datetime | None
    rejection_reason: str | None
    compensated_at: datetime | None
    compensation_shift_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_credit: bool
    is_debit: bool
    is_expired: bool
    is_pending: bool
    signed_hours: float
    days_until_expiration: int | None


class TimeBankListResponse(BaseModel):
    """Schema para listagem paginada de TimeBank."""

    items: list[TimeBankResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TimeBankFilter(BaseModel):
    """Schema para filtros de busca de TimeBank."""

    employee_id: str | None = None
    entry_type: TimeBankEntryType | None = None
    status: TimeBankStatus | None = None
    shift_id: str | None = None
    post_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_expired: bool | None = None
    is_pending: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "TimeBankFilter":
        """Valida range de datas."""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date deve ser anterior a end_date")
        return self


class TimeBankApprove(BaseModel):
    """Schema para aprovação de entrada no banco."""

    notes: str | None = Field(None, description="Observações")


class TimeBankReject(BaseModel):
    """Schema para rejeição de entrada no banco."""

    rejection_reason: str = Field(..., max_length=255, description="Motivo da rejeição")


class TimeBankCompensate(BaseModel):
    """Schema para compensação de horas."""

    hours: float = Field(..., gt=0, description="Horas a compensar")
    compensation_date: date = Field(..., description="Data da compensação")
    shift_id: str | None = Field(None, description="ID do turno de compensação")
    notes: str | None = Field(None, description="Observações")


class TimeBankSummary(BaseModel):
    """Resumo do banco de horas de um funcionário."""

    employee_id: str
    total_credit: float = Field(..., description="Total de horas creditadas")
    total_debit: float = Field(..., description="Total de horas debitadas")
    total_compensated: float = Field(..., description="Total de horas compensadas")
    total_expired: float = Field(..., description="Total de horas expiradas")
    current_balance: float = Field(..., description="Saldo atual")
    pending_approval: float = Field(..., description="Horas pendentes de aprovação")
    expiring_soon: float = Field(..., description="Horas expirando em 30 dias")
    entries_count: int = Field(..., description="Quantidade de entradas")


class TimeBankStats(BaseModel):
    """Estatísticas gerais do banco de horas."""

    total_employees: int
    total_credit_hours: float
    total_debit_hours: float
    total_compensated_hours: float
    total_expired_hours: float
    total_pending_hours: float
    avg_balance: float
    by_status: dict[str, int]
    by_entry_type: dict[str, float]
