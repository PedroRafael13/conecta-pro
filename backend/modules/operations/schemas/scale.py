"""
Schemas Pydantic para Scale (Escala de Trabalho).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from modules.operations.models.scale import ScaleStatus, ScaleType


class ScaleBase(BaseModel):
    """Schema base para Scale."""

    post_id: str = Field(..., description="ID do posto")
    scale_type: ScaleType = Field(default=ScaleType.SCALE_12X36, description="Tipo de escala")
    month: int = Field(..., ge=1, le=12, description="Mês (1-12)")
    year: int = Field(..., ge=2020, le=2100, description="Ano")
    notes: Optional[str] = Field(None, description="Observações")
    config: Optional[Dict[str, Any]] = Field(None, description="Configurações da escala")

    @model_validator(mode="after")
    def validate_dates(self) -> "ScaleBase":
        """Valida período."""
        if self.year < 2020:
            raise ValueError("Ano deve ser >= 2020")
        return self


class ScaleCreate(ScaleBase):
    """Schema para criação de Scale - herda todos os campos de ScaleBase."""


class ScaleUpdate(BaseModel):
    """Schema para atualização parcial de Scale."""

    scale_type: Optional[ScaleType] = None
    status: Optional[ScaleStatus] = None
    notes: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ScaleResponse(BaseModel):
    """Schema de resposta para Scale."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    post_id: str
    scale_type: str
    status: str
    month: int
    year: int
    start_date: date
    end_date: date
    total_shifts: int
    total_hours: float
    overtime_hours: float
    estimated_cost: float
    config: Optional[Dict[str, Any]]
    notes: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    published_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_current_month: bool
    is_published: bool
    can_edit: bool
    filled_shifts_count: int
    fill_rate: float


class ScaleListResponse(BaseModel):
    """Schema para listagem paginada de Scales."""

    items: List[ScaleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScaleFilter(BaseModel):
    """Schema para filtros de busca de Scales."""

    post_id: Optional[str] = None
    scale_type: Optional[ScaleType] = None
    status: Optional[ScaleStatus] = None
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2020, le=2100)
    is_current_month: Optional[bool] = None


class ScaleGenerateRequest(BaseModel):
    """Schema para solicitação de geração automática de escala."""

    post_id: str = Field(..., description="ID do posto")
    month: int = Field(..., ge=1, le=12, description="Mês")
    year: int = Field(..., ge=2020, le=2100, description="Ano")
    scale_type: ScaleType = Field(..., description="Tipo de escala")
    employee_ids: List[str] = Field(..., min_length=1, description="IDs dos funcionários")
    config: Optional[Dict[str, Any]] = Field(
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
    def validate_employees(cls, v: List[str]) -> List[str]:
        """Valida lista de funcionários."""
        if len(v) == 0:
            raise ValueError("Deve informar pelo menos 1 funcionário")
        return list(set(v))  # Remove duplicados


class ScaleApproveRequest(BaseModel):
    """Schema para aprovação de escala."""

    notes: Optional[str] = Field(None, description="Observações da aprovação")


class ScalePublishRequest(BaseModel):
    """Schema para publicação de escala."""

    notify_employees: bool = Field(default=True, description="Notificar funcionários")
    notification_channels: List[str] = Field(
        default=["email", "push"],
        description="Canais de notificação",
    )


class ScaleStats(BaseModel):
    """Estatísticas de escalas."""

    total: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    total_hours: float
    total_overtime_hours: float
    total_estimated_cost: float
    avg_fill_rate: float
