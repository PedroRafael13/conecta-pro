"""
Schemas Pydantic para Scale (Escala de Trabalho).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from modules.operacional.models.scale import ScaleStatus, ScaleType


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
    post_id: str
    scale_type: str
    status: str
    month: int
    year: int
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_shifts: int = 0
    filled_shifts: int = 0
    total_hours: float = 0.0
    overtime_hours: float = 0.0
    estimated_cost: float = 0.0
    config: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    published_by: Optional[str] = None
    published_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

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
