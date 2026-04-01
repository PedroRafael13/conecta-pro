"""Schemas para MobileCheckIn."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CheckInLocation(BaseModel):
    """Schema para localização do check-in."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: float | None = Field(None, ge=0)
    altitude: float | None = None
    provider: str | None = Field(None, max_length=20)


class CheckInBiometric(BaseModel):
    """Schema para dados biométricos."""

    verified: bool
    type: str = Field(..., pattern="^(fingerprint|face_id|iris)$")
    score: int | None = Field(None, ge=0, le=100)


class CheckInPhoto(BaseModel):
    """Schema para foto do check-in."""

    captured: bool
    path: str | None = None
    face_detected: bool | None = None
    match_score: float | None = Field(None, ge=0, le=100)


class CheckInValidation(BaseModel):
    """Schema para validação adicional."""

    wifi_ssid: str | None = None
    wifi_bssid: str | None = None
    beacon_uuid: str | None = None
    nfc_tag_id: str | None = None
    qr_code_data: str | None = None


class MobileCheckInCreate(BaseModel):
    """Schema para criar check-in mobile."""

    checkin_type: str = Field(default="entry")
    device_timestamp: datetime
    location: CheckInLocation | None = None
    biometric: CheckInBiometric | None = None
    photo: CheckInPhoto | None = None
    validation: CheckInValidation | None = None
    device_info: dict | None = Field(default_factory=dict)
    app_version: str | None = Field(None, max_length=20)

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
    local_validation: dict | None = None
    local_geofence_check: bool = Field(default=False)
    local_biometric_check: bool = Field(default=False)


class MobileCheckInBatch(BaseModel):
    """Schema para batch de check-ins offline."""

    checkins: list[MobileCheckInOffline] = Field(..., min_length=1, max_length=100)


class MobileCheckInReview(BaseModel):
    """Schema para revisar check-in."""

    approved: bool
    notes: str | None = Field(None, max_length=500)
    rejection_reason: str | None = Field(None, max_length=500)


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
    latitude: float | None
    longitude: float | None
    accuracy_meters: float | None
    location_accuracy: str
    geofence_id: UUID | None
    inside_geofence: bool
    distance_from_center: float | None
    status: str
    validation_methods: list[str] | None
    validation_score: int
    is_valid: bool
    biometric_verified: bool
    photo_captured: bool
    is_offline: bool
    synced_at: datetime | None
    has_anomaly: bool
    anomaly_type: str | None
    time_entry_id: UUID | None
    processed_at: datetime | None
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    review_notes: str | None
    created_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do Pydantic."""

        from_attributes = True


class MobileCheckInList(BaseModel):
    """Schema de lista de check-ins."""

    items: list[MobileCheckInResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MobileCheckInFilter(BaseModel):
    """Filtros para busca de check-ins."""

    device_id: UUID | None = None
    employee_id: UUID | None = None
    condominio_id: UUID | None = None
    geofence_id: UUID | None = None
    checkin_type: str | None = None
    status: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    inside_geofence: bool | None = None
    is_offline: bool | None = None
    has_anomaly: bool | None = None
    needs_review: bool | None = None


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
    methods_passed: list[str]
    methods_failed: list[str]
    warnings: list[str]
    errors: list[str]
    geofence_check: dict | None = None
    time_check: dict | None = None
    device_check: dict | None = None


class CheckInConfirmation(BaseModel):
    """Confirmação de check-in para o app."""

    success: bool
    checkin_id: UUID
    server_time: datetime
    message: str
    next_expected_type: str | None = None
    work_hours_today: float | None = None
    warnings: list[str] = Field(default_factory=list)
