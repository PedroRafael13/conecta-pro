"""Schemas para GeofenceZone."""

from datetime import datetime, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    """Schema para coordenada."""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class GeofenceZoneBase(BaseModel):
    """Schema base para zona de geofencing."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    zone_type: str = Field(default="circle")
    category: str = Field(default="headquarters")

    @field_validator("zone_type")
    @classmethod
    def validate_zone_type(cls, v: str) -> str:
        allowed = ["circle", "polygon", "rectangle"]
        if v.lower() not in allowed:
            raise ValueError(f"Zone type must be one of: {allowed}")
        return v.lower()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["headquarters", "branch", "client_site", "external", "home_office", "temporary"]
        if v.lower() not in allowed:
            raise ValueError(f"Category must be one of: {allowed}")
        return v.lower()


class GeofenceZoneCreate(GeofenceZoneBase):
    """Schema para criar zona."""
    post_id: Optional[UUID] = None

    # Geometria
    center_latitude: float = Field(..., ge=-90, le=90)
    center_longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(default=100, ge=10, le=10000)
    polygon_coordinates: Optional[List[Coordinate]] = None

    # Endereço
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)

    # Configurações
    min_accuracy_meters: int = Field(default=50, ge=5, le=200)
    require_wifi: bool = Field(default=False)
    allowed_wifi_ssids: Optional[List[str]] = None
    require_beacon: bool = Field(default=False)
    allowed_beacons: Optional[List[str]] = None

    # Horários
    allow_all_hours: bool = Field(default=True)
    allowed_start_time: Optional[time] = None
    allowed_end_time: Optional[time] = None
    allowed_days: Optional[List[int]] = Field(default=[1, 2, 3, 4, 5])

    # Tolerância
    entry_tolerance_minutes: int = Field(default=15, ge=0, le=60)
    exit_tolerance_minutes: int = Field(default=15, ge=0, le=60)
    grace_period_meters: int = Field(default=20, ge=0, le=100)

    # Funcionários
    allow_all_employees: bool = Field(default=True)
    allowed_employees: Optional[List[UUID]] = None
    allowed_departments: Optional[List[UUID]] = None

    # Status
    is_primary: bool = Field(default=False)
    priority: int = Field(default=0, ge=0, le=100)


class GeofenceZoneUpdate(BaseModel):
    """Schema para atualizar zona."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None

    # Geometria
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius_meters: Optional[int] = Field(None, ge=10, le=10000)
    polygon_coordinates: Optional[List[Coordinate]] = None

    # Endereço
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)

    # Configurações
    min_accuracy_meters: Optional[int] = Field(None, ge=5, le=200)
    require_wifi: Optional[bool] = None
    allowed_wifi_ssids: Optional[List[str]] = None
    require_beacon: Optional[bool] = None
    allowed_beacons: Optional[List[str]] = None

    # Horários
    allow_all_hours: Optional[bool] = None
    allowed_start_time: Optional[time] = None
    allowed_end_time: Optional[time] = None
    allowed_days: Optional[List[int]] = None

    # Tolerância
    entry_tolerance_minutes: Optional[int] = Field(None, ge=0, le=60)
    exit_tolerance_minutes: Optional[int] = Field(None, ge=0, le=60)
    grace_period_meters: Optional[int] = Field(None, ge=0, le=100)

    # Funcionários
    allow_all_employees: Optional[bool] = None
    allowed_employees: Optional[List[UUID]] = None
    allowed_departments: Optional[List[UUID]] = None

    # Status
    status: Optional[str] = None
    is_primary: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class GeofenceZoneResponse(BaseModel):
    """Schema de resposta para zona."""
    id: UUID
    condominio_id: UUID
    post_id: Optional[UUID]
    name: str
    description: Optional[str]
    zone_type: str
    category: str
    center_latitude: float
    center_longitude: float
    radius_meters: int
    polygon_coordinates: Optional[List[dict]]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    min_accuracy_meters: int
    require_wifi: bool
    allowed_wifi_ssids: Optional[List[str]]
    require_beacon: bool
    allowed_beacons: Optional[List[str]]
    allow_all_hours: bool
    allowed_start_time: Optional[time]
    allowed_end_time: Optional[time]
    allowed_days: Optional[List[int]]
    entry_tolerance_minutes: int
    exit_tolerance_minutes: int
    grace_period_meters: int
    allow_all_employees: bool
    status: str
    is_primary: bool
    priority: int
    total_checkins: int
    last_checkin_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GeofenceZoneList(BaseModel):
    """Schema de lista de zonas."""
    items: List[GeofenceZoneResponse]
    total: int
    page: int
    page_size: int
    pages: int


class GeofenceZoneFilter(BaseModel):
    """Filtros para busca de zonas."""
    condominio_id: Optional[UUID] = None
    post_id: Optional[UUID] = None
    category: Optional[str] = None
    status: Optional[str] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    near_latitude: Optional[float] = Field(None, ge=-90, le=90)
    near_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_distance_km: Optional[float] = Field(None, ge=0.1, le=100)


class GeofenceCheckRequest(BaseModel):
    """Request para verificar geofence."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: Optional[float] = Field(None, ge=0)
    employee_id: Optional[UUID] = None


class GeofenceCheckResponse(BaseModel):
    """Resposta da verificação de geofence."""
    is_inside: bool
    zone: Optional[GeofenceZoneResponse] = None
    distance_meters: Optional[float] = None
    zones_in_range: List[dict] = Field(default_factory=list)
    validation_passed: bool
    validation_errors: List[str] = Field(default_factory=list)


class GeofenceZoneStats(BaseModel):
    """Estatísticas de zonas."""
    total_zones: int
    active_zones: int
    by_category: dict
    by_status: dict
    total_checkins: int
    most_used_zones: List[dict]
    avg_radius_meters: float
