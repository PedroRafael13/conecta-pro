"""
Schemas Pydantic para Substitution (Substituição de Funcionário).
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.operacional.models.substitution import SubstitutionReason, SubstitutionStatus


class SubstitutionBase(BaseModel):
    """Schema base para Substitution."""

    shift_id: str = Field(..., description="ID do turno")
    post_id: str = Field(..., description="ID do posto")
    original_employee_id: str = Field(..., description="ID do funcionário original")
    reason: SubstitutionReason = Field(..., description="Motivo da substituição")
    substitution_date: date = Field(..., description="Data da substituição")
    reason_details: str | None = Field(None, max_length=500, description="Detalhes")
    notes: str | None = Field(None, description="Observações")


class SubstitutionCreate(SubstitutionBase):
    """Schema para criação de Substitution."""

    substitute_employee_id: str | None = Field(None, description="ID do substituto")


class SubstitutionUpdate(BaseModel):
    """Schema para atualização parcial de Substitution."""

    substitute_employee_id: str | None = None
    status: SubstitutionStatus | None = None
    reason: SubstitutionReason | None = None
    reason_details: str | None = Field(None, max_length=500)
    notes: str | None = None
    rejection_reason: str | None = Field(None, max_length=255)
    is_active: bool | None = None


class SubstitutionResponse(BaseModel):
    """Schema de resposta para Substitution."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    shift_id: str
    post_id: str
    original_employee_id: str
    substitute_employee_id: str | None
    reason: str
    status: str
    substitution_date: date
    requested_at: datetime
    confirmed_at: datetime | None
    completed_at: datetime | None
    additional_cost: float
    overtime_hours: float
    is_overtime: bool
    notes: str | None
    reason_details: str | None
    rejection_reason: str | None
    notification_sent: bool
    notification_sent_at: datetime | None
    requested_by: str | None
    approved_by: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_pending: bool
    is_confirmed: bool
    has_substitute: bool
    response_time_hours: float | None


class SubstitutionListResponse(BaseModel):
    """Schema para listagem paginada de Substitutions."""

    items: list[SubstitutionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SubstitutionFilter(BaseModel):
    """Schema para filtros de busca de Substitutions."""

    shift_id: str | None = None
    post_id: str | None = None
    original_employee_id: str | None = None
    substitute_employee_id: str | None = None
    status: SubstitutionStatus | None = None
    reason: SubstitutionReason | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_pending: bool | None = None
    has_substitute: bool | None = None


class SubstitutionConfirm(BaseModel):
    """Schema para confirmação de substituição."""

    substitute_employee_id: str = Field(..., description="ID do substituto")
    notes: str | None = Field(None, description="Observações")


class SubstitutionReject(BaseModel):
    """Schema para rejeição de substituição."""

    rejection_reason: str = Field(..., max_length=255, description="Motivo da rejeição")


class SubstituteSuggestion(BaseModel):
    """Schema para sugestão de substituto pela IA."""

    employee_id: str
    employee_name: str
    score: float = Field(..., ge=0, le=100, description="Score de adequação (0-100)")
    reasons: list[str] = Field(..., description="Motivos da sugestão")
    is_overtime: bool = Field(..., description="Será hora extra")
    estimated_cost: float = Field(..., ge=0, description="Custo estimado")
    distance_km: float | None = Field(None, ge=0, description="Distância em km")
    availability: str = Field(..., description="Disponibilidade")


class SubstitutionSuggestRequest(BaseModel):
    """Schema para solicitação de sugestões de substitutos."""

    shift_id: str = Field(..., description="ID do turno")
    max_suggestions: int = Field(default=5, ge=1, le=10, description="Máximo de sugestões")
    prefer_same_post: bool = Field(default=True, description="Preferir mesmo posto")
    consider_distance: bool = Field(default=True, description="Considerar distância")
    max_distance_km: float | None = Field(None, ge=0, description="Distância máxima")
