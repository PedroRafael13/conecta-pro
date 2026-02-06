"""Schemas para MobileCheckIn."""

from datetime import datetime, date, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CheckInLocation(BaseModel):
    """Schema para localização do check-in."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: Optional[float] = Field(None, ge=0)
    altitude: Optional[float] = None
    provider: Optional[str] = Field(None, max_length=20)


class CheckInBiometric(BaseModel):
    """Schema para dados biométricos."""
    verified: bool
    type: str = Field(..., pattern="^(fingerprint|face_id|iris)$")
    score: Optional[int] = Field(None, ge=0, le=100)


class CheckInPhoto(BaseModel):
    """Schema para foto do check-in."""
    captured: bool
    path: Optional[str] = None
    face_detected: Optional[bool] = None
    match_score: Optional[float] = Field(None, ge=0, le=100)


class CheckInValidation(BaseModel):
    """Schema para validação adicional."""
    wifi_ssid: Optional[str] = None
    wifi_bssid: Optional[str] = None
    beacon_uuid: Optional[str] = None
    nfc_tag_id: Optional[str] = None
    qr_code_data: Optional[str] = None


class MobileCheckInCreate(BaseModel):
    """Schema para criar check-in mobile."""
    checkin_type: str = Field(default="entry")
    device_timestamp: datetime
    location: Optional[CheckInLocation] = None
    biometric: Optional[CheckInBiometric] = None
    photo: Optional[CheckInPhoto] = None
    validation: Optional[CheckInValidation] = None
    device_info: Optional[dict] = Field(default_factory=dict)
    app_version: Optional[str] = Field(None, max_length=20)

    @field_validator("checkin_type")
    @classmethod
    def validate_checkin_type(cls, v: str) -> str:
        """Valida tipo de checkin."""
        allowed = ["entry", "exit", "break_start", "break_end", "extra_entry", "extra_exit"]
        if v.lower() not in allowed:
            raise ValueError(f"CheckIn type must be one of: {allowed}")
        return v.lower()


class MobileCheckInOffline(MobileCheckInCreate):
    """Schema para check-in offline."""
    offline_id: str = Field(..., min_length=10, max_length=100)
    local_validation: Optional[dict] = None
    local_geofence_check: bool = Field(default=False)
    local_biometric_check: bool = Field(default=False)


class MobileCheckInBatch(BaseModel):
    """Schema para batch de check-ins offline."""
    checkins: List[MobileCheckInOffline] = Field(..., min_length=1, max_length=100)


class MobileCheckInReview(BaseModel):
    """Schema para revisar check-in."""
    approved: bool
    notes: Optional[str] = Field(None, max_length=500)
    rejection_reason: Optional[str] = Field(None, max_length=500)


class MobileCheckInResponse(BaseModel):
    """Schema de resposta para check-in."""
    id: UUID
    device_id: UUID
    employee_id: UUID
    condominio_id: UUID
    checkin_type: str
    checkin_datetime: datetime
    checkin_date: date
    checkin_time: time
    device_timestamp: datetime
    server_timestamp: datetime
    time_drift_seconds: int
    latitude: Optional[float]
    longitude: Optional[float]
    accuracy_meters: Optional[float]
    location_accuracy: str
    geofence_id: Optional[UUID]
    inside_geofence: bool
    distance_from_center: Optional[float]
    status: str
    validation_methods: Optional[List[str]]
    validation_score: int
    is_valid: bool
    biometric_verified: bool
    photo_captured: bool
    is_offline: bool
    synced_at: Optional[datetime]
    has_anomaly: bool
    anomaly_type: Optional[str]
    time_entry_id: Optional[UUID]
    processed_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    created_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do Pydantic."""

        from_attributes = True


class MobileCheckInList(BaseModel):
    """Schema de lista de check-ins."""
    items: List[MobileCheckInResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MobileCheckInFilter(BaseModel):
    """Filtros para busca de check-ins."""
    device_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    geofence_id: Optional[UUID] = None
    checkin_type: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    inside_geofence: Optional[bool] = None
    is_offline: Optional[bool] = None
    has_anomaly: Optional[bool] = None
    needs_review: Optional[bool] = None


class MobileCheckInStats(BaseModel):
    """Estatísticas de check-ins."""
    total_checkins: int
    today_checkins: int
    pending_review: int
    offline_checkins: int
    anomalies_detected: int
    by_type: dict
    by_status: dict
    avg_validation_score: float
    geofence_compliance: float
    biometric_usage: float


class CheckInValidationResult(BaseModel):
    """Resultado da validação de check-in."""
    is_valid: bool
    score: int
    methods_passed: List[str]
    methods_failed: List[str]
    warnings: List[str]
    errors: List[str]
    geofence_check: Optional[dict] = None
    time_check: Optional[dict] = None
    device_check: Optional[dict] = None


class CheckInConfirmation(BaseModel):
    """Confirmação de check-in para o app."""
    success: bool
    checkin_id: UUID
    server_time: datetime
    message: str
    next_expected_type: Optional[str] = None
    work_hours_today: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)
