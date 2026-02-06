"""
Schemas Pydantic para Scale (Escala de Trabalho).
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from modules.operacional.models.scale import ScaleStatus, ScaleType


class ScaleBase(BaseModel):
    """Schema base para Scale."""

    post_id: str = Field(..., description="ID do posto")
    scale_type: ScaleType = Field(default=ScaleType.SCALE_12X36, description="Tipo de escala")
    month: int = Field(..., ge=1, le=12, description="Mês (1-12)")
    year: int = Field(..., ge=2020, le=2100, description="Ano")
    notes: str | None = Field(None, description="Observações")
    config: dict[str, Any] | None = Field(None, description="Configurações da escala")

    @model_validator(mode="after")
    def validate_dates(self) -> "ScaleBase":
        """Valida período."""
        if self.year < 2020:
            raise ValueError("Ano deve ser >= 2020")
        return self


class ScaleCreate(ScaleBase):
    """
    Schema para criação de Scale (Escala de Trabalho).

    Uma escala organiza os turnos de trabalho dos funcionários em um posto
    durante um período específico (mês/ano).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "post_id": "550e8400-e29b-41d4-a716-446655440000",
                "scale_type": "SCALE_12X36",
                "month": 3,
                "year": 2026,
                "notes": "Escala com feriados no período",
                "config": {
                    "allow_overtime": True,
                    "max_consecutive_days": 6,
                    "rest_days_required": 1,
                },
            }
        }
    )


class ScaleUpdate(BaseModel):
    """
    Schema para atualização parcial de Scale.

    Todos os campos são opcionais. Apenas os campos fornecidos serão atualizados.
    """

    scale_type: ScaleType | None = Field(None, description="Tipo de escala")
    status: ScaleStatus | None = Field(None, description="Status da escala")
    notes: str | None = Field(None, description="Observações")
    config: dict[str, Any] | None = Field(None, description="Configurações da escala")
    is_active: bool | None = Field(None, description="Ativo/Inativo")


class ScaleResponse(BaseModel):
    """Schema de resposta para Scale."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    post_id: str
    scale_type: str
    status: str
    month: int
    year: int
    name: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    total_shifts: int = 0
    filled_shifts: int = 0
    total_hours: float = 0.0
    overtime_hours: float = 0.0
    estimated_cost: float = 0.0
    config: dict[str, Any] | None = None
    notes: str | None = None
    approved_by: str | None = None
    approved_at: datetime | None = None
    approval_notes: str | None = None
    published_by: str | None = None
    published_at: datetime | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None

    # Propriedades calculadas
    @computed_field
    @property
    def is_current_month(self) -> bool:
        """Verifica se é a escala do mês atual."""
        from datetime import date as date_type

        today = date_type.today()
        return self.month == today.month and self.year == today.year

    @computed_field
    @property
    def is_published(self) -> bool:
        """Verifica se a escala foi publicada."""
        return self.status == "published"

    @computed_field
    @property
    def can_edit(self) -> bool:
        """Verifica se a escala pode ser editada."""
        return self.status in ("draft", "pending_approval")

    @computed_field
    @property
    def fill_rate(self) -> float:
        """Calcula taxa de preenchimento da escala (%)."""
        if self.total_shifts == 0:
            return 0.0
        return (self.filled_shifts / self.total_shifts) * 100


class ScaleListResponse(BaseModel):
    """Schema para listagem paginada de Scales."""

    items: list[ScaleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScaleFilter(BaseModel):
    """Schema para filtros de busca de Scales."""

    post_id: str | None = None
    scale_type: ScaleType | None = None
    status: ScaleStatus | None = None
    month: int | None = Field(None, ge=1, le=12)
    year: int | None = Field(None, ge=2020, le=2100)
    is_current_month: bool | None = None
    created_by: str | None = Field(None, description="Filtrar por criador")


class ScaleGenerateRequest(BaseModel):
    """Schema para solicitação de geração automática de escala."""

    post_id: str = Field(..., description="ID do posto")
    month: int = Field(..., ge=1, le=12, description="Mês")
    year: int = Field(..., ge=2020, le=2100, description="Ano")
    scale_type: ScaleType = Field(..., description="Tipo de escala")
    employee_ids: list[str] = Field(..., min_length=1, description="IDs dos funcionários")
    config: dict[str, Any] | None = Field(
        None,
        description="Configurações adicionais",
        json_schema_extra={
            "example": {
                "consider_holidays": True,
                "balance_night_shifts": True,
                "max_consecutive_days": 6,
                "min_rest_hours": 11,
            }
        },
    )

    @field_validator("employee_ids")
    @classmethod
    def validate_employees(cls, v: list[str]) -> list[str]:
        """Valida lista de funcionários."""
        if len(v) == 0:
            raise ValueError("Deve informar pelo menos 1 funcionário")
        return list(set(v))  # Remove duplicados


class ScaleApproveRequest(BaseModel):
    """Schema para aprovação de escala."""

    notes: str | None = Field(None, description="Observações da aprovação")


class ScaleRejectRequest(BaseModel):
    """Schema para rejeição de escala."""

    reason: str = Field(..., min_length=10, max_length=500, description="Motivo da rejeição")
    notes: str | None = Field(None, description="Observações adicionais")


class ScalePublishRequest(BaseModel):
    """Schema para publicação de escala."""

    notify_employees: bool = Field(default=True, description="Notificar funcionários")
    notification_channels: list[str] = Field(
        default=["email", "push"],
        description="Canais de notificação",
    )


class ScaleStats(BaseModel):
    """Estatísticas de escalas."""

    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    total_hours: float
    total_overtime_hours: float
    total_estimated_cost: float
    avg_fill_rate: float
