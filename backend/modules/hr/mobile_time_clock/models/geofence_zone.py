"""Modelo GeofenceZone - Zonas de geofencing para registro de ponto.

Define áreas geográficas permitidas para registro de ponto.
"""

import uuid
import math
from datetime import datetime, time
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Time,
    Integer,
    Float,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .mobile_checkin import MobileCheckIn


class ZoneType(str, Enum):
    """Tipo de zona."""
    CIRCLE = "circle"          # Círculo com centro e raio
    POLYGON = "polygon"        # Polígono com vértices
    RECTANGLE = "rectangle"    # Retângulo


class ZoneCategory(str, Enum):
    """Categoria da zona."""
    HEADQUARTERS = "headquarters"    # Sede principal
    BRANCH = "branch"                # Filial
    CLIENT_SITE = "client_site"      # Local do cliente
    EXTERNAL = "external"            # Trabalho externo
    HOME_OFFICE = "home_office"      # Home office
    TEMPORARY = "temporary"          # Zona temporária


class ZoneStatus(str, Enum):
    """Status da zona."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class GeofenceZone(Base):
    """Modelo de zona de geofencing."""

    __tablename__ = "geofence_zones"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
    )  # Opcional: vinculado a um posto

    # Informações básicas
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    zone_type: Mapped[str] = mapped_column(
        String(20),
        default=ZoneType.CIRCLE.value,
    )
    category: Mapped[str] = mapped_column(
        String(20),
        default=ZoneCategory.HEADQUARTERS.value,
    )

    # Geometria - Círculo
    center_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    center_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_meters: Mapped[int] = mapped_column(Integer, default=100)

    # Geometria - Polígono (lista de coordenadas)
    polygon_coordinates: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=list,
    )  # [{lat: x, lng: y}, ...]

    # Endereço (para referência)
    address: Mapped[Optional[str]] = mapped_column(String(500))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))

    # Configurações de validação
    min_accuracy_meters: Mapped[int] = mapped_column(Integer, default=50)
    require_wifi: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_wifi_ssids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    require_beacon: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_beacons: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Horários permitidos
    allow_all_hours: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_start_time: Mapped[Optional[time]] = mapped_column(Time)
    allowed_end_time: Mapped[Optional[time]] = mapped_column(Time)
    allowed_days: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=lambda: [1, 2, 3, 4, 5],
    )  # 1=seg, 7=dom

    # Tolerância
    entry_tolerance_minutes: Mapped[int] = mapped_column(Integer, default=15)
    exit_tolerance_minutes: Mapped[int] = mapped_column(Integer, default=15)
    grace_period_meters: Mapped[int] = mapped_column(Integer, default=20)

    # Funcionários permitidos
    allow_all_employees: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_employees: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    allowed_departments: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=ZoneStatus.ACTIVE.value,
        index=True,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    # Estatísticas
    total_checkins: Mapped[int] = mapped_column(Integer, default=0)
    last_checkin_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadados
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Auditoria
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamentos
    checkins: Mapped[list["MobileCheckIn"]] = relationship(
        "MobileCheckIn",
        back_populates="geofence",
        lazy="dynamic",
    )

    # Índices
    __table_args__ = (
        Index("ix_geofence_zones_condominio_status", "condominio_id", "status"),
        Index("ix_geofence_zones_category", "category"),
        Index("ix_geofence_zones_coordinates", "center_latitude", "center_longitude"),
    )

    @property
    def is_available(self) -> bool:
        """Verifica se zona está disponível."""
        return self.status == ZoneStatus.ACTIVE.value and self.is_active

    @property
    def effective_radius(self) -> int:
        """Raio efetivo incluindo tolerância."""
        return self.radius_meters + self.grace_period_meters

    def contains_point(self, lat: float, lng: float) -> bool:
        """Verifica se ponto está dentro da zona."""
        if self.zone_type == ZoneType.CIRCLE.value:
            return self._point_in_circle(lat, lng)
        elif self.zone_type == ZoneType.POLYGON.value:
            return self._point_in_polygon(lat, lng)
        return False

    def _point_in_circle(self, lat: float, lng: float) -> bool:
        """Verifica se ponto está no círculo."""
        distance = self.calculate_distance(lat, lng)
        return distance <= self.effective_radius

    def _point_in_polygon(self, lat: float, lng: float) -> bool:
        """Verifica se ponto está no polígono (ray casting)."""
        if not self.polygon_coordinates:
            return False

        n = len(self.polygon_coordinates)
        inside = False

        j = n - 1
        for i in range(n):
            xi = self.polygon_coordinates[i].get("lat", 0)
            yi = self.polygon_coordinates[i].get("lng", 0)
            xj = self.polygon_coordinates[j].get("lat", 0)
            yj = self.polygon_coordinates[j].get("lng", 0)

            if ((yi > lng) != (yj > lng)) and (lat < (xj - xi) * (lng - yi) / (yj - yi) + xi):
                inside = not inside

            j = i

        return inside

    def calculate_distance(self, lat: float, lng: float) -> float:
        """Calcula distância em metros usando Haversine."""
        earth_radius = 6371000  # Raio da Terra em metros

        lat1 = math.radians(self.center_latitude)
        lat2 = math.radians(lat)
        delta_lat = math.radians(lat - self.center_latitude)
        delta_lng = math.radians(lng - self.center_longitude)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius * c

    def is_time_allowed(self, check_time: time) -> bool:
        """Verifica se horário é permitido."""
        if self.allow_all_hours:
            return True

        if not self.allowed_start_time or not self.allowed_end_time:
            return True

        return self.allowed_start_time <= check_time <= self.allowed_end_time

    def is_day_allowed(self, weekday: int) -> bool:
        """Verifica se dia da semana é permitido (1=seg, 7=dom)."""
        if not self.allowed_days:
            return True
        return weekday in self.allowed_days

    def is_employee_allowed(self, employee_id: str, department_id: str = None) -> bool:
        """Verifica se funcionário é permitido."""
        if self.allow_all_employees:
            return True

        if self.allowed_employees and employee_id in self.allowed_employees:
            return True

        if self.allowed_departments and department_id and department_id in self.allowed_departments:
            return True

        return False

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "name": self.name,
            "zone_type": self.zone_type,
            "category": self.category,
            "center_latitude": self.center_latitude,
            "center_longitude": self.center_longitude,
            "radius_meters": self.radius_meters,
            "status": self.status,
            "is_primary": self.is_primary,
            "total_checkins": self.total_checkins,
        }
