"""Schemas para GeofenceZone."""

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    """Schema para coordenada."""

    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class GeofenceZoneBase(BaseModel):
    """Schema base para zona de geofencing."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    zone_type: str = Field(default="circle")
    category: str = Field(default="headquarters")

    @field_validator("zone_type")
    @classmethod
    def validate_zone_type(cls, v: str) -> str:
        """Valida tipo de zona."""
        allowed = ["circle", "polygon", "rectangle"]
        if v.lower() not in allowed:
            raise ValueError(f"Zone type must be one of: {allowed}")
        return v.lower()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Valida categoria."""
        allowed = ["headquarters", "branch", "client_site", "external", "home_office", "temporary"]
        if v.lower() not in allowed:
            raise ValueError(f"Category must be one of: {allowed}")
        return v.lower()


class GeofenceZoneCreate(GeofenceZoneBase):
    """Schema para criar zona."""

    post_id: UUID | None = None

    # Geometria
    center_latitude: float = Field(..., ge=-90, le=90)
    center_longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(default=100, ge=10, le=10000)
    polygon_coordinates: list[Coordinate] | None = None

    # Endereço
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=50)
    postal_code: str | None = Field(None, max_length=20)

    # Configurações
    min_accuracy_meters: int = Field(default=50, ge=5, le=200)
    require_wifi: bool = Field(default=False)
    allowed_wifi_ssids: list[str] | None = None
    require_beacon: bool = Field(default=False)
    allowed_beacons: list[str] | None = None

    # Horários
    allow_all_hours: bool = Field(default=True)
    allowed_start_time: time | None = None
    allowed_end_time: time | None = None
    allowed_days: list[int] | None = Field(default=[1, 2, 3, 4, 5])

    # Tolerância
    entry_tolerance_minutes: int = Field(default=15, ge=0, le=60)
    exit_tolerance_minutes: int = Field(default=15, ge=0, le=60)
    grace_period_meters: int = Field(default=20, ge=0, le=100)

    # Funcionários
    allow_all_employees: bool = Field(default=True)
    allowed_employees: list[UUID] | None = None
    allowed_departments: list[UUID] | None = None

    # Status
    is_primary: bool = Field(default=False)
    priority: int = Field(default=0, ge=0, le=100)


class GeofenceZoneUpdate(BaseModel):
    """Schema para atualizar zona."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    category: str | None = None

    # Geometria
    center_latitude: float | None = Field(None, ge=-90, le=90)
    center_longitude: float | None = Field(None, ge=-180, le=180)
    radius_meters: int | None = Field(None, ge=10, le=10000)
    polygon_coordinates: list[Coordinate] | None = None

    # Endereço
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=50)
    postal_code: str | None = Field(None, max_length=20)

    # Configurações
    min_accuracy_meters: int | None = Field(None, ge=5, le=200)
    require_wifi: bool | None = None
    allowed_wifi_ssids: list[str] | None = None
    require_beacon: bool | None = None
    allowed_beacons: list[str] | None = None

    # Horários
    allow_all_hours: bool | None = None
    allowed_start_time: time | None = None
    allowed_end_time: time | None = None
    allowed_days: list[int] | None = None

    # Tolerância
    entry_tolerance_minutes: int | None = Field(None, ge=0, le=60)
    exit_tolerance_minutes: int | None = Field(None, ge=0, le=60)
    grace_period_meters: int | None = Field(None, ge=0, le=100)

    # Funcionários
    allow_all_employees: bool | None = None
    allowed_employees: list[UUID] | None = None
    allowed_departments: list[UUID] | None = None

    # Status
    status: str | None = None
    is_primary: bool | None = None
    priority: int | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class GeofenceZoneResponse(BaseModel):
    """Schema de resposta para zona."""

    id: UUID
    condominio_id: UUID
    post_id: UUID | None
    name: str
    description: str | None
    zone_type: str
    category: str
    center_latitude: float
    center_longitude: float
    radius_meters: int
    polygon_coordinates: list[dict] | None
    address: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    min_accuracy_meters: int
    require_wifi: bool
    allowed_wifi_ssids: list[str] | None
    require_beacon: bool
    allowed_beacons: list[str] | None
    allow_all_hours: bool
    allowed_start_time: time | None
    allowed_end_time: time | None
    allowed_days: list[int] | None
    entry_tolerance_minutes: int
    exit_tolerance_minutes: int
    grace_period_meters: int
    allow_all_employees: bool
    status: str
    is_primary: bool
    priority: int
    total_checkins: int
    last_checkin_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do Pydantic."""

        from_attributes = True


class GeofenceZoneList(BaseModel):
    """Schema de lista de zonas."""

    items: list[GeofenceZoneResponse]
    total: int
    page: int
    page_size: int
    pages: int


class GeofenceZoneFilter(BaseModel):
    """Filtros para busca de zonas."""

    condominio_id: UUID | None = None
    post_id: UUID | None = None
    category: str | None = None
    status: str | None = None
    is_primary: bool | None = None
    is_active: bool | None = None
    near_latitude: float | None = Field(None, ge=-90, le=90)
    near_longitude: float | None = Field(None, ge=-180, le=180)
    max_distance_km: float | None = Field(None, ge=0.1, le=100)


class GeofenceCheckRequest(BaseModel):
    """Request para verificar geofence."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: float | None = Field(None, ge=0)
    employee_id: UUID | None = None


class GeofenceCheckResponse(BaseModel):
    """Resposta da verificação de geofence."""

    is_inside: bool
    zone: GeofenceZoneResponse | None = None
    distance_meters: float | None = None
    zones_in_range: list[dict] = Field(default_factory=list)
    validation_passed: bool
    validation_errors: list[str] = Field(default_factory=list)


class GeofenceZoneStats(BaseModel):
    """Estatísticas de zonas."""

    total_zones: int
    active_zones: int
    by_category: dict
    by_status: dict
    total_checkins: int
    most_used_zones: list[dict]
    avg_radius_meters: float
