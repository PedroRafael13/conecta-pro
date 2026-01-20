"""
Schemas Pydantic para Area (Área Física).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.facilities.models.area import AreaStatus, AreaType


class AreaBase(BaseModel):
    """Schema base para Area."""

    name: str = Field(..., min_length=1, max_length=255, description="Nome da área")
    description: Optional[str] = Field(None, max_length=2000, description="Descrição")
    area_type: AreaType = Field(default=AreaType.COMUM, description="Tipo de área")
    parent_id: Optional[str] = Field(None, description="ID da área pai")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    condominium_id: Optional[str] = Field(None, description="ID do condomínio")
    floor: Optional[str] = Field(None, max_length=20, description="Andar/Pavimento")
    building: Optional[str] = Field(None, max_length=100, description="Bloco/Prédio")
    area_m2: Optional[float] = Field(None, ge=0, description="Área em m²")
    capacity: Optional[int] = Field(None, ge=0, description="Capacidade de pessoas")
    location_details: Optional[str] = Field(None, description="Detalhes de localização")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    equipment: Optional[Dict[str, Any]] = Field(None, description="Equipamentos")
    access_restrictions: Optional[Dict[str, Any]] = Field(None, description="Restrições")
    responsible_id: Optional[str] = Field(None, description="ID do responsável")
    requires_reservation: bool = Field(default=False, description="Requer reserva")
    is_rentable: bool = Field(default=False, description="Pode ser alugada")
    rental_price: Optional[float] = Field(None, ge=0, description="Preço de aluguel")


class AreaCreate(AreaBase):
    """Schema para criação de Area."""

    code: Optional[str] = Field(None, max_length=20, description="Código (auto-gerado se vazio)")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida e normaliza o código da área."""
        if v:
            return v.upper().strip()
        return v


class AreaUpdate(BaseModel):
    """Schema para atualização parcial de Area."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    area_type: Optional[AreaType] = None
    status: Optional[AreaStatus] = None
    parent_id: Optional[str] = None
    client_id: Optional[str] = None
    condominium_id: Optional[str] = None
    floor: Optional[str] = Field(None, max_length=20)
    building: Optional[str] = Field(None, max_length=100)
    area_m2: Optional[float] = Field(None, ge=0)
    capacity: Optional[int] = Field(None, ge=0)
    location_details: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    equipment: Optional[Dict[str, Any]] = None
    access_restrictions: Optional[Dict[str, Any]] = None
    responsible_id: Optional[str] = None
    requires_reservation: Optional[bool] = None
    is_rentable: Optional[bool] = None
    rental_price: Optional[float] = Field(None, ge=0)
    next_inspection_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class AreaResponse(BaseModel):
    """Schema de resposta para Area."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    description: Optional[str]
    area_type: str
    status: str
    parent_id: Optional[str]
    client_id: Optional[str]
    condominium_id: Optional[str]
    floor: Optional[str]
    building: Optional[str]
    area_m2: Optional[float]
    capacity: Optional[int]
    location_details: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    equipment: Optional[Dict[str, Any]]
    access_restrictions: Optional[Dict[str, Any]]
    responsible_id: Optional[str]
    last_inspection_date: Optional[datetime]
    next_inspection_date: Optional[datetime]
    requires_reservation: bool
    is_rentable: bool
    rental_price: Optional[float]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_available: bool
    needs_inspection: bool
    has_pending_maintenance: bool
    child_count: int


class AreaListResponse(BaseModel):
    """Schema para listagem paginada de Areas."""

    items: List[AreaResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AreaFilter(BaseModel):
    """Schema para filtros de busca de Areas."""

    search: Optional[str] = Field(None, description="Busca por nome ou código")
    area_type: Optional[AreaType] = None
    status: Optional[AreaStatus] = None
    parent_id: Optional[str] = None
    client_id: Optional[str] = None
    condominium_id: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    requires_reservation: Optional[bool] = None
    is_rentable: Optional[bool] = None
    needs_inspection: Optional[bool] = None
    has_pending_maintenance: Optional[bool] = None


class AreaStats(BaseModel):
    """Estatísticas de áreas."""

    total: int = Field(..., description="Total de áreas")
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    by_status: Dict[str, int] = Field(..., description="Por status")
    total_area_m2: float = Field(..., description="Área total em m²")
    total_capacity: int = Field(..., description="Capacidade total")
    needing_inspection: int = Field(..., description="Precisando de inspeção")
    with_pending_maintenance: int = Field(..., description="Com manutenção pendente")
    rentable_count: int = Field(..., description="Áreas alugáveis")
