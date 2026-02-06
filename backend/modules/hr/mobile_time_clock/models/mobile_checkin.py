"""Modelo MobileCheckIn - Registros de ponto via app mobile.

Armazena registros de entrada/saída feitos pelo aplicativo.
"""

import uuid
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Time,
    Integer,
    Float,
    String,
    Text,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .mobile_device import MobileDevice
    from .geofence_zone import GeofenceZone


class CheckInType(str, Enum):
    """Tipo de registro."""
    ENTRY = "entry"                    # Entrada
    EXIT = "exit"                      # Saída
    BREAK_START = "break_start"        # Início intervalo
    BREAK_END = "break_end"            # Fim intervalo
    EXTRA_ENTRY = "extra_entry"        # Entrada extra
    EXTRA_EXIT = "extra_exit"          # Saída extra


class CheckInStatus(str, Enum):
    """Status do registro."""
    PENDING = "pending"                # Aguardando processamento
    VALIDATED = "validated"            # Validado automaticamente
    APPROVED = "approved"              # Aprovado por supervisor
    REJECTED = "rejected"              # Rejeitado
    FLAGGED = "flagged"                # Marcado para revisão
    PROCESSED = "processed"            # Processado no ponto


class ValidationMethod(str, Enum):
    """Método de validação usado."""
    GEOFENCE = "geofence"              # Dentro da zona permitida
    BIOMETRIC = "biometric"            # Biometria do dispositivo
    PHOTO = "photo"                    # Foto selfie
    SUPERVISOR = "supervisor"          # Aprovação manual
    QR_CODE = "qr_code"               # Leitura de QR code
    NFC = "nfc"                       # Tag NFC
    WIFI = "wifi"                     # Rede WiFi específica
    BEACON = "beacon"                 # Beacon Bluetooth


class LocationAccuracy(str, Enum):
    """Precisão da localização."""
    HIGH = "high"          # < 10m
    MEDIUM = "medium"      # 10-50m
    LOW = "low"           # 50-100m
    VERY_LOW = "very_low" # > 100m
    UNKNOWN = "unknown"


class MobileCheckIn(Base):
    """Modelo de registro de ponto mobile."""

    __tablename__ = "mobile_checkins"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mobile_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Dados do registro
    checkin_type: Mapped[str] = mapped_column(
        String(20),
        default=CheckInType.ENTRY.value,
    )
    checkin_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    checkin_time: Mapped[time] = mapped_column(Time, nullable=False)

    # Timestamp do dispositivo vs servidor
    device_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    server_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    time_drift_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Geolocalização
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    altitude: Mapped[Optional[float]] = mapped_column(Float)
    accuracy_meters: Mapped[Optional[float]] = mapped_column(Float)
    location_accuracy: Mapped[str] = mapped_column(
        String(20),
        default=LocationAccuracy.UNKNOWN.value,
    )
    location_provider: Mapped[Optional[str]] = mapped_column(String(20))  # gps, network, fused

    # Geofence
    geofence_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("geofence_zones.id", ondelete="SET NULL"),
    )
    inside_geofence: Mapped[bool] = mapped_column(Boolean, default=False)
    distance_from_center: Mapped[Optional[float]] = mapped_column(Float)  # metros

    # Validação
    status: Mapped[str] = mapped_column(
        String(20),
        default=CheckInStatus.PENDING.value,
        index=True,
    )
    validation_methods: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    validation_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)

    # Biometria
    biometric_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    biometric_type: Mapped[Optional[str]] = mapped_column(String(20))
    biometric_score: Mapped[Optional[int]] = mapped_column(Integer)

    # Foto selfie
    photo_captured: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_path: Mapped[Optional[str]] = mapped_column(String(500))
    photo_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    face_match_score: Mapped[Optional[float]] = mapped_column(Float)

    # QR Code / NFC
    qr_code_data: Mapped[Optional[str]] = mapped_column(String(500))
    nfc_tag_id: Mapped[Optional[str]] = mapped_column(String(100))

    # WiFi / Beacon
    wifi_ssid: Mapped[Optional[str]] = mapped_column(String(100))
    wifi_bssid: Mapped[Optional[str]] = mapped_column(String(20))
    beacon_uuid: Mapped[Optional[str]] = mapped_column(String(50))

    # Offline
    is_offline: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    offline_queue_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    # Anomalias
    has_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_type: Mapped[Optional[str]] = mapped_column(String(50))
    anomaly_details: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Processamento
    time_entry_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Aprovação/Rejeição
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    review_notes: Mapped[Optional[str]] = mapped_column(Text)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Metadados do dispositivo
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    app_version: Mapped[Optional[str]] = mapped_column(String(20))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    # Relacionamentos
    device: Mapped["MobileDevice"] = relationship(
        "MobileDevice",
        back_populates="checkins",
    )
    geofence: Mapped[Optional["GeofenceZone"]] = relationship(
        "GeofenceZone",
        back_populates="checkins",
    )

    # Índices
    __table_args__ = (
        Index("ix_mobile_checkins_employee_date", "employee_id", "checkin_date"),
        Index("ix_mobile_checkins_device_date", "device_id", "checkin_date"),
        Index("ix_mobile_checkins_condominio_date", "condominio_id", "checkin_date"),
        Index("ix_mobile_checkins_status_date", "status", "checkin_date"),
        Index("ix_mobile_checkins_geofence", "geofence_id"),
    )

    @property
    def is_validated(self) -> bool:
        """Verifica se foi validado."""
        return self.status in [
            CheckInStatus.VALIDATED.value,
            CheckInStatus.APPROVED.value,
            CheckInStatus.PROCESSED.value,
        ]

    @property
    def needs_review(self) -> bool:
        """Verifica se precisa de revisão."""
        return self.status == CheckInStatus.FLAGGED.value or self.has_anomaly

    @property
    def location_tuple(self) -> Optional[tuple]:
        """Retorna tupla (lat, lng)."""
        if self.latitude and self.longitude:
            return (self.latitude, self.longitude)
        return None

    def calculate_accuracy_level(self) -> str:
        """Calcula nível de precisão."""
        if not self.accuracy_meters:
            return LocationAccuracy.UNKNOWN.value
        if self.accuracy_meters < 10:
            return LocationAccuracy.HIGH.value
        if self.accuracy_meters < 50:
            return LocationAccuracy.MEDIUM.value
        if self.accuracy_meters < 100:
            return LocationAccuracy.LOW.value
        return LocationAccuracy.VERY_LOW.value

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "employee_id": str(self.employee_id),
            "checkin_type": self.checkin_type,
            "checkin_datetime": self.checkin_datetime.isoformat(),
            "status": self.status,
            "is_valid": self.is_valid,
            "validation_score": self.validation_score,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "inside_geofence": self.inside_geofence,
            "biometric_verified": self.biometric_verified,
            "photo_captured": self.photo_captured,
            "is_offline": self.is_offline,
            "has_anomaly": self.has_anomaly,
        }
