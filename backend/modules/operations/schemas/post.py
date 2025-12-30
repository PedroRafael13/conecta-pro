"""
Schemas Pydantic para Post (Posto de Trabalho).
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.operations.models.post import PostStatus, PostType, ShiftType


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

    # Horários
    default_start_time: Optional[time] = Field(None, description="Hora início padrão")
    default_end_time: Optional[time] = Field(None, description="Hora fim padrão")
    break_duration_minutes: int = Field(default=60, ge=0, description="Intervalo em minutos")

    # Capacidade e Custos
    headcount: int = Field(default=1, ge=1, description="Quantidade de funcionários")
    hourly_rate: float = Field(default=0.0, ge=0, description="Valor hora")
    monthly_cost: float = Field(default=0.0, ge=0, description="Custo mensal")

    # Configurações
    requires_armed: bool = Field(default=False, description="Requer armamento")
    requires_vehicle: bool = Field(default=False, description="Requer veículo")
    allows_overtime: bool = Field(default=True, description="Permite hora extra")

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
    requirements: Optional[Dict[str, Any]] = Field(None, description="Requisitos")
    equipment: Optional[Dict[str, Any]] = Field(None, description="Equipamentos")


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
    default_start_time: Optional[time] = None
    default_end_time: Optional[time] = None
    break_duration_minutes: Optional[int] = Field(None, ge=0)
    headcount: Optional[int] = Field(None, ge=1)
    hourly_rate: Optional[float] = Field(None, ge=0)
    monthly_cost: Optional[float] = Field(None, ge=0)
    requires_armed: Optional[bool] = None
    requires_vehicle: Optional[bool] = None
    allows_overtime: Optional[bool] = None
    requirements: Optional[Dict[str, Any]] = None
    equipment: Optional[Dict[str, Any]] = None
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
    default_start_time: Optional[time]
    default_end_time: Optional[time]
    break_duration_minutes: int
    requirements: Optional[Dict[str, Any]]
    equipment: Optional[Dict[str, Any]]
    headcount: int
    hourly_rate: float
    monthly_cost: float
    requires_armed: bool
    requires_vehicle: bool
    allows_overtime: bool
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
