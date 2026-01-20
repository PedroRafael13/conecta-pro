"""
Schemas Pydantic para Post (Posto de Trabalho).
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.operacional.models.post import PostStatus, PostType, ShiftType


class PostBase(BaseModel):
    """Schema base para Post."""

    name: str = Field(..., min_length=2, max_length=255, description="Nome do posto")
    description: Optional[str] = Field(None, description="Descrição")
    post_type: PostType = Field(default=PostType.VIGILANTE, description="Tipo de posto")
    shift_type: ShiftType = Field(default=ShiftType.DIURNO, description="Tipo de turno")

    # Localização
    address: Optional[str] = Field(None, max_length=500, description="Endereço")
    city: Optional[str] = Field(None, max_length=100, description="Cidade")
    state: Optional[str] = Field(None, max_length=2, description="UF")
    zip_code: Optional[str] = Field(None, max_length=10, description="CEP")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")

    # Horários (nomes conforme schema do banco)
    shift_start_time: Optional[time] = Field(None, description="Hora início do turno")
    shift_end_time: Optional[time] = Field(None, description="Hora fim do turno")
    break_duration_minutes: int = Field(default=60, ge=0, description="Intervalo em minutos")
    night_shift_bonus_percent: float = Field(default=20.0, ge=0, description="Adicional noturno %")
    hazard_pay_percent: float = Field(default=0.0, ge=0, description="Periculosidade %")

    # Capacidade e Custos
    required_headcount: int = Field(default=1, ge=1, description="Quantidade necessária de funcionários")
    requires_experience_months: int = Field(default=0, ge=0, description="Experiência mínima em meses")
    hourly_rate: float = Field(default=0.0, ge=0, description="Valor hora")
    monthly_cost: float = Field(default=0.0, ge=0, description="Custo mensal")

    # Configurações
    requires_armed: bool = Field(default=False, description="Requer armamento")
    requires_vehicle: bool = Field(default=False, description="Requer veículo")

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        """Valida UF."""
        if v is not None:
            return v.upper()
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida CEP."""
        if v is not None:
            digits = "".join(c for c in v if c.isdigit())
            if len(digits) != 8:
                raise ValueError("CEP deve ter 8 dígitos")
        return v


class PostCreate(PostBase):
    """Schema para criação de Post."""

    contract_id: Optional[str] = Field(None, description="ID do contrato")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    required_certifications: Optional[Dict[str, Any]] = Field(None, description="Certificações necessárias")
    supervisor_name: Optional[str] = Field(None, max_length=200, description="Nome do supervisor")
    supervisor_phone: Optional[str] = Field(None, max_length=20, description="Telefone do supervisor")
    emergency_contact: Optional[str] = Field(None, max_length=200, description="Contato de emergência")
    emergency_phone: Optional[str] = Field(None, max_length=20, description="Telefone de emergência")
    notes: Optional[str] = Field(None, description="Observações")


class PostUpdate(BaseModel):
    """Schema para atualização parcial de Post."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    post_type: Optional[PostType] = None
    status: Optional[PostStatus] = None
    shift_type: Optional[ShiftType] = None
    contract_id: Optional[str] = None
    client_id: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    zip_code: Optional[str] = Field(None, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    shift_start_time: Optional[time] = None
    shift_end_time: Optional[time] = None
    break_duration_minutes: Optional[int] = Field(None, ge=0)
    night_shift_bonus_percent: Optional[float] = Field(None, ge=0)
    hazard_pay_percent: Optional[float] = Field(None, ge=0)
    required_headcount: Optional[int] = Field(None, ge=1)
    requires_experience_months: Optional[int] = Field(None, ge=0)
    hourly_rate: Optional[float] = Field(None, ge=0)
    monthly_cost: Optional[float] = Field(None, ge=0)
    requires_armed: Optional[bool] = None
    requires_vehicle: Optional[bool] = None
    required_certifications: Optional[Dict[str, Any]] = None
    supervisor_name: Optional[str] = Field(None, max_length=200)
    supervisor_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact: Optional[str] = Field(None, max_length=200)
    emergency_phone: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PostResponse(BaseModel):
    """Schema de resposta para Post."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str]
    post_type: str
    status: str
    shift_type: str
    contract_id: Optional[str]
    client_id: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    shift_start_time: Optional[time]
    shift_end_time: Optional[time]
    break_duration_minutes: int
    night_shift_bonus_percent: float
    hazard_pay_percent: float
    required_certifications: Optional[Dict[str, Any]]
    required_headcount: int
    current_headcount: int
    requires_experience_months: int
    hourly_rate: float
    monthly_cost: float
    requires_armed: bool
    requires_vehicle: bool
    supervisor_name: Optional[str]
    supervisor_phone: Optional[str]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_filled: bool
    vacancy_count: int
    daily_hours: float


class PostListResponse(BaseModel):
    """Schema para listagem paginada de Posts."""

    items: List[PostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PostFilter(BaseModel):
    """Schema para filtros de busca de Posts."""

    post_type: Optional[PostType] = None
    status: Optional[PostStatus] = None
    shift_type: Optional[ShiftType] = None
    contract_id: Optional[str] = None
    client_id: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    requires_armed: Optional[bool] = None
    requires_vehicle: Optional[bool] = None
    has_vacancy: Optional[bool] = None
    search: Optional[str] = Field(None, description="Busca por nome ou código")


class PostStats(BaseModel):
    """Estatísticas de postos."""

    total: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_shift: Dict[str, int]
    filled: int
    with_vacancy: int
    total_headcount: int
    total_allocated: int
    total_monthly_cost: float
