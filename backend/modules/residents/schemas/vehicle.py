"""Schemas para ResidentVehicle."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.residents.models.vehicle import VehicleType, VehicleStatus, FuelType


# ========== Base Schemas ==========


class VehicleBase(BaseModel):
    """Schema base para Vehicle."""

    vehicle_type: VehicleType = VehicleType.CARRO
    plate: str = Field(..., min_length=6, max_length=10)
    plate_city: Optional[str] = Field(None, max_length=100)
    plate_state: Optional[str] = Field(None, max_length=2)

    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    year_model: Optional[int] = Field(None, ge=1900, le=2100)
    color: Optional[str] = Field(None, max_length=50)
    fuel_type: Optional[FuelType] = None


class VehicleCreate(VehicleBase):
    """Schema para criação de Vehicle."""

    resident_id: UUID
    renavam: Optional[str] = Field(None, max_length=20)
    chassi: Optional[str] = Field(None, max_length=50)
    parking_spot: Optional[str] = Field(None, max_length=20)
    parking_spot_type: Optional[str] = Field(None, max_length=50)
    tag_rfid: Optional[str] = Field(None, max_length=50)
    control_code: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class VehicleUpdate(BaseModel):
    """Schema para atualização de Vehicle."""

    vehicle_type: Optional[VehicleType] = None
    status: Optional[VehicleStatus] = None
    plate: Optional[str] = Field(None, min_length=6, max_length=10)
    plate_city: Optional[str] = Field(None, max_length=100)
    plate_state: Optional[str] = Field(None, max_length=2)

    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    year_model: Optional[int] = Field(None, ge=1900, le=2100)
    color: Optional[str] = Field(None, max_length=50)
    fuel_type: Optional[FuelType] = None

    renavam: Optional[str] = Field(None, max_length=20)
    chassi: Optional[str] = Field(None, max_length=50)
    parking_spot: Optional[str] = Field(None, max_length=20)
    parking_spot_type: Optional[str] = Field(None, max_length=50)
    tag_rfid: Optional[str] = Field(None, max_length=50)
    control_code: Optional[str] = Field(None, max_length=50)
    photo_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class VehicleResponse(BaseModel):
    """Schema de resposta para Vehicle."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resident_id: UUID
    vehicle_type: VehicleType
    status: VehicleStatus

    plate: str
    plate_city: Optional[str] = None
    plate_state: Optional[str] = None

    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    year_model: Optional[int] = None
    color: Optional[str] = None
    fuel_type: Optional[FuelType] = None

    renavam: Optional[str] = None
    chassi: Optional[str] = None

    parking_spot: Optional[str] = None
    parking_spot_type: Optional[str] = None
    has_reserved_spot: bool

    tag_rfid: Optional[str] = None
    control_code: Optional[str] = None
    is_authorized: bool

    photo_url: Optional[str] = None

    registration_date: date
    deactivation_date: Optional[date] = None

    is_blocked: bool
    block_reason: Optional[str] = None

    is_active: bool
    is_valid_for_access: bool
    full_description: str
    formatted_plate: str

    notes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# ========== Action Schemas ==========


class VehicleBlock(BaseModel):
    """Schema para bloqueio de veículo."""

    reason: str = Field(..., min_length=5, max_length=500)


class VehicleAssignParking(BaseModel):
    """Schema para atribuir vaga."""

    spot: str = Field(..., max_length=20)
    spot_type: Optional[str] = Field(None, max_length=50)


# ========== Filter Schemas ==========


class VehicleFilter(BaseModel):
    """Schema para filtros de busca."""

    resident_id: Optional[UUID] = None
    vehicle_type: Optional[VehicleType] = None
    status: Optional[VehicleStatus] = None
    plate: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    is_blocked: Optional[bool] = None
    is_authorized: Optional[bool] = None
    has_parking_spot: Optional[bool] = None
    condominium_id: Optional[str] = None


# ========== List Response ==========


class VehicleListResponse(BaseModel):
    """Schema de resposta para lista de Vehicles."""

    items: list[VehicleResponse]
    total: int
    page: int
    page_size: int
    pages: int = 0


# ========== Stats ==========


class VehicleStats(BaseModel):
    """Estatísticas de veículos."""

    total: int = 0
    active: int = 0
    blocked: int = 0
    by_type: dict = {}
    by_brand: dict = {}
    by_color: dict = {}
    with_parking_spot: int = 0
    with_tag_rfid: int = 0
