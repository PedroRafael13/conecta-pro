"""
Schemas Pydantic para ScaleTemplate.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field


class TemplateShiftPattern(BaseModel):
    """Padrão de turno dentro do template."""

    employee_id: str = Field(..., description="ID do funcionário (pode ser placeholder)")
    post_id: str = Field(..., description="ID do posto")
    days_of_week: list[int] = Field(
        ...,
        description="Dias da semana (0=segunda, 6=domingo)",
        min_length=1,
    )
    start_time: str = Field(..., description="Hora de início (HH:MM)")
    end_time: str = Field(..., description="Hora de fim (HH:MM)")
    shift_type: str = Field(..., description="Tipo de turno (12x36, 6x1, etc)")
    is_night_shift: bool = Field(default=False, description="Se é turno noturno")
    break_minutes: int = Field(default=60, description="Minutos de intervalo")


class TemplateMetadata(BaseModel):
    """Metadados do template."""

    total_employees: int = Field(default=0, description="Total de funcionários")
    coverage_percentage: float = Field(default=100.0, description="Percentual de cobertura")
    total_shifts_per_month: int = Field(default=0, description="Total de turnos por mês")
    avg_hours_per_employee: float = Field(default=0.0, description="Média de horas por funcionário")


class TemplateData(BaseModel):
    """Estrutura completa dos dados do template."""

    scale_type: str = Field(..., description="Tipo de escala")
    posts: list[str] = Field(..., description="IDs dos postos", min_length=1)
    shifts_pattern: list[TemplateShiftPattern] = Field(
        ...,
        description="Padrões de turnos",
        min_length=1,
    )
    config: dict[str, Any] | None = Field(None, description="Configurações da escala")
    metadata: TemplateMetadata = Field(
        default_factory=TemplateMetadata,
        description="Metadados do template",
    )


class ScaleTemplateBase(BaseModel):
    """Schema base para ScaleTemplate."""

    name: str = Field(..., min_length=3, max_length=100, description="Nome do template")
    description: str | None = Field(None, description="Descrição do template")


class ScaleTemplateCreate(ScaleTemplateBase):
    """Schema para criação de template."""

    template_data: TemplateData = Field(..., description="Dados do template")


class ScaleTemplateCreateFromScale(BaseModel):
    """Schema para criar template a partir de escala existente."""

    scale_id: str = Field(..., description="ID da escala base")
    name: str = Field(..., min_length=3, max_length=100, description="Nome do template")
    description: str | None = Field(None, description="Descrição do template")
    include_employee_mapping: bool = Field(
        default=False,
        description="Se deve incluir mapeamento específico de funcionários",
    )


class ScaleTemplateUpdate(BaseModel):
    """Schema para atualização de template."""

    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    template_data: TemplateData | None = None
    is_active: bool | None = None


class ScaleTemplateResponse(BaseModel):
    """Schema de resposta para ScaleTemplate."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    description: str | None = None
    template_data: dict[str, Any]
    times_used: int = 0
    last_used: datetime | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @computed_field
    @property
    def is_popular(self) -> bool:
        """Verifica se o template é popular (usado 5+ vezes)."""
        return self.times_used >= 5

    @computed_field
    @property
    def total_employees(self) -> int:
        """Retorna total de funcionários no template."""
        metadata = self.template_data.get("metadata", {})
        return metadata.get("total_employees", 0)

    @computed_field
    @property
    def coverage_percentage(self) -> float:
        """Retorna percentual de cobertura do template."""
        metadata = self.template_data.get("metadata", {})
        return metadata.get("coverage_percentage", 0.0)


class ScaleTemplateListResponse(BaseModel):
    """Schema para listagem paginada de templates."""

    items: list[ScaleTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScaleTemplateApplyRequest(BaseModel):
    """Schema para aplicação de template."""

    month: int = Field(..., ge=1, le=12, description="Mês da nova escala")
    year: int = Field(..., ge=2020, le=2100, description="Ano da nova escala")
    post_id: str | None = Field(None, description="Posto (se diferente do template)")
    employee_mapping: dict[str, str] | None = Field(
        None,
        description="Mapeamento de funcionários antigos -> novos",
        json_schema_extra={
            "example": {
                "old_employee_id_1": "new_employee_id_1",
                "old_employee_id_2": "new_employee_id_2",
            }
        },
    )
    config_overrides: dict[str, Any] | None = Field(
        None,
        description="Sobrescrever configurações do template",
    )


class ScaleTemplateStats(BaseModel):
    """Estatísticas de templates."""

    total: int
    active: int
    inactive: int
    most_used: list[ScaleTemplateResponse] = Field(default_factory=list)
    recently_created: list[ScaleTemplateResponse] = Field(default_factory=list)
    avg_usage: float = 0.0
