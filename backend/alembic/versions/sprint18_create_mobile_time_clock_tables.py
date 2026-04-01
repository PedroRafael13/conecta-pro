"""Sprint 18: Create Mobile Time Clock tables.

Revision ID: sprint18_mobile_time_clock
Revises: sprint17_rep_integration
Create Date: 2025-12-31

Tabelas:
- mobile_devices: Dispositivos móveis registrados para ponto
- mobile_checkins: Check-ins realizados via app mobile
- geofence_zones: Zonas de geofencing para validação de localização
- offline_queue: Fila de sincronização de check-ins offline
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint18_mobile_time_clock"
down_revision: str | None = "sprint17_rep_integration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabelas do módulo Mobile Time Clock."""

    # ==================== MOBILE_DEVICES ====================
    op.create_table(
        "mobile_devices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("employee_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=False, index=True),
        # Identificação do dispositivo
        sa.Column("device_name", sa.String(100), nullable=False),
        sa.Column("device_uuid", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("platform", sa.String(20), nullable=False),  # android, ios, web
        sa.Column("os_version", sa.String(50), nullable=True),
        sa.Column("app_version", sa.String(20), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(100), nullable=True),
        # Push notifications
        sa.Column("push_token", sa.String(500), nullable=True),
        sa.Column("push_provider", sa.String(20), nullable=True),  # fcm, apns
        # Biometria
        sa.Column("biometric_capability", sa.String(50), nullable=True),
        sa.Column("biometric_enabled", sa.Boolean, default=False),
        sa.Column("biometric_enrolled_at", sa.DateTime, nullable=True),
        # Status e controle
        sa.Column("status", sa.String(20), default="pending"),  # pending, active, blocked, revoked, lost
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_trusted", sa.Boolean, default=False),
        sa.Column("trust_score", sa.Integer, default=0),
        # Aprovação
        sa.Column("approved_by", UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        # Bloqueio
        sa.Column("blocked_by", UUID(as_uuid=True), nullable=True),
        sa.Column("blocked_at", sa.DateTime, nullable=True),
        sa.Column("blocked_reason", sa.String(500), nullable=True),
        # Segurança
        sa.Column("failed_attempts", sa.Integer, default=0),
        sa.Column("last_failed_at", sa.DateTime, nullable=True),
        # Localização
        sa.Column("last_known_lat", sa.Float, nullable=True),
        sa.Column("last_known_lng", sa.Float, nullable=True),
        sa.Column("last_location_at", sa.DateTime, nullable=True),
        # Configurações
        sa.Column("allow_offline_checkin", sa.Boolean, default=False),
        sa.Column("max_offline_hours", sa.Integer, default=24),
        sa.Column("require_photo", sa.Boolean, default=False),
        sa.Column("require_geofence", sa.Boolean, default=True),
        # Estatísticas
        sa.Column("checkin_count", sa.Integer, default=0),
        sa.Column("first_seen_at", sa.DateTime, nullable=True),
        sa.Column("last_seen_at", sa.DateTime, nullable=True),
        # Metadados
        sa.Column("device_info", JSONB, default={}),
        # Timestamps
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )

    op.create_index("ix_mobile_devices_employee_active", "mobile_devices", ["employee_id", "is_active"])
    op.create_index("ix_mobile_devices_condominio_status", "mobile_devices", ["condominio_id", "status"])

    # ==================== GEOFENCE_ZONES ====================
    op.create_table(
        "geofence_zones",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("post_id", UUID(as_uuid=True), nullable=True, index=True),
        # Identificação
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("zone_type", sa.String(20), nullable=False, default="circle"),  # circle, polygon, rectangle
        sa.Column("category", sa.String(50), nullable=False, default="work"),  # work, parking, entrance, exit
        sa.Column("status", sa.String(20), nullable=False, default="active"),  # active, inactive, maintenance
        # Coordenadas centrais
        sa.Column("center_latitude", sa.Float, nullable=False),
        sa.Column("center_longitude", sa.Float, nullable=False),
        sa.Column("radius_meters", sa.Float, nullable=False, default=100),
        # Polígono (para zone_type = polygon)
        sa.Column("polygon_coordinates", JSONB, nullable=True),
        # Endereço
        sa.Column("address", sa.String(300), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        # Validação de localização
        sa.Column("min_accuracy_meters", sa.Float, default=50),
        sa.Column("require_wifi", sa.Boolean, default=False),
        sa.Column("allowed_wifi_ssids", JSONB, nullable=True),
        sa.Column("require_beacon", sa.Boolean, default=False),
        sa.Column("allowed_beacons", JSONB, nullable=True),
        # Restrições de horário
        sa.Column("allow_all_hours", sa.Boolean, default=True),
        sa.Column("allowed_start_time", sa.Time, nullable=True),
        sa.Column("allowed_end_time", sa.Time, nullable=True),
        sa.Column("allowed_days", JSONB, nullable=True),  # [0,1,2,3,4,5,6]
        # Tolerâncias
        sa.Column("entry_tolerance_minutes", sa.Integer, default=15),
        sa.Column("exit_tolerance_minutes", sa.Integer, default=15),
        sa.Column("grace_period_meters", sa.Float, default=10),
        # Funcionários permitidos
        sa.Column("allow_all_employees", sa.Boolean, default=True),
        sa.Column("allowed_employees", JSONB, nullable=True),
        sa.Column("allowed_departments", JSONB, nullable=True),
        # Prioridade
        sa.Column("is_primary", sa.Boolean, default=False),
        sa.Column("priority", sa.Integer, default=0),
        sa.Column("is_active", sa.Boolean, default=True),
        # Estatísticas
        sa.Column("total_checkins", sa.Integer, default=0),
        sa.Column("last_checkin_at", sa.DateTime, nullable=True),
        # Auditoria
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )

    op.create_index("ix_geofence_zones_location", "geofence_zones", ["center_latitude", "center_longitude"])
    op.create_index("ix_geofence_zones_condominio_active", "geofence_zones", ["condominio_id", "is_active", "status"])

    # ==================== MOBILE_CHECKINS ====================
    op.create_table(
        "mobile_checkins",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("device_id", UUID(as_uuid=True), sa.ForeignKey("mobile_devices.id"), nullable=False, index=True),
        sa.Column("employee_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("geofence_id", UUID(as_uuid=True), sa.ForeignKey("geofence_zones.id"), nullable=True),
        # Tipo e timing
        sa.Column("checkin_type", sa.String(20), nullable=False),  # entry, exit, break_start, break_end
        sa.Column("checkin_datetime", sa.DateTime, nullable=False),
        sa.Column("checkin_date", sa.Date, nullable=False, index=True),
        sa.Column("checkin_time", sa.Time, nullable=False),
        # Timestamps de sincronização
        sa.Column("device_timestamp", sa.DateTime, nullable=False),
        sa.Column("server_timestamp", sa.DateTime, nullable=False),
        sa.Column("time_drift_seconds", sa.Integer, default=0),
        # Localização
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("accuracy_meters", sa.Float, nullable=True),
        sa.Column("altitude", sa.Float, nullable=True),
        sa.Column("location_provider", sa.String(20), nullable=True),
        sa.Column("location_accuracy", sa.String(20), nullable=True),  # high, medium, low, very_low
        # Geofence
        sa.Column("inside_geofence", sa.Boolean, nullable=True),
        sa.Column("distance_from_center", sa.Float, nullable=True),
        # Biometria
        sa.Column("biometric_verified", sa.Boolean, default=False),
        sa.Column("biometric_type", sa.String(30), nullable=True),
        sa.Column("biometric_score", sa.Float, nullable=True),
        # Foto/Selfie
        sa.Column("photo_captured", sa.Boolean, default=False),
        sa.Column("photo_path", sa.String(500), nullable=True),
        sa.Column("face_match_score", sa.Float, nullable=True),
        # Validação adicional
        sa.Column("wifi_ssid", sa.String(100), nullable=True),
        sa.Column("wifi_bssid", sa.String(50), nullable=True),
        sa.Column("beacon_uuid", sa.String(100), nullable=True),
        sa.Column("nfc_tag_id", sa.String(100), nullable=True),
        sa.Column("qr_code_data", sa.String(500), nullable=True),
        # Status e validação
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("validation_methods", JSONB, nullable=True),
        sa.Column("validation_score", sa.Integer, default=0),
        sa.Column("is_valid", sa.Boolean, default=False),
        # Anomalias
        sa.Column("has_anomaly", sa.Boolean, default=False),
        sa.Column("anomaly_type", sa.String(50), nullable=True),
        sa.Column("anomaly_details", JSONB, nullable=True),
        # Revisão
        sa.Column("reviewed_by", UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("review_notes", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        # Offline
        sa.Column("is_offline", sa.Boolean, default=False),
        sa.Column("offline_id", sa.String(100), nullable=True),
        sa.Column("synced_at", sa.DateTime, nullable=True),
        # Processamento
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("time_entry_id", UUID(as_uuid=True), nullable=True),
        # Metadados
        sa.Column("app_version", sa.String(20), nullable=True),
        sa.Column("device_info", JSONB, default={}),
        # Timestamps
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=True, onupdate=sa.func.now()),
    )

    op.create_index("ix_mobile_checkins_employee_date", "mobile_checkins", ["employee_id", "checkin_date"])
    op.create_index("ix_mobile_checkins_status", "mobile_checkins", ["status", "has_anomaly"])
    op.create_index("ix_mobile_checkins_condominio_date", "mobile_checkins", ["condominio_id", "checkin_date"])
    op.create_index(
        "ix_mobile_checkins_offline",
        "mobile_checkins",
        ["offline_id"],
        unique=True,
        postgresql_where=sa.text("offline_id IS NOT NULL"),
    )

    # ==================== OFFLINE_QUEUE ====================
    op.create_table(
        "offline_queue",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("device_id", UUID(as_uuid=True), sa.ForeignKey("mobile_devices.id"), nullable=False, index=True),
        sa.Column("employee_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=False, index=True),
        # Identificação offline
        sa.Column("offline_id", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("checkin_data", JSONB, nullable=False),
        sa.Column("checkin_type", sa.String(20), nullable=False),
        sa.Column("device_timestamp", sa.DateTime, nullable=False),
        # Localização
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("accuracy_meters", sa.Float, nullable=True),
        # Validação local
        sa.Column("local_validation", JSONB, nullable=True),
        sa.Column("local_geofence_check", sa.Boolean, default=False),
        sa.Column("local_biometric_check", sa.Boolean, default=False),
        # Status da fila
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("priority", sa.String(20), nullable=False, default="normal"),
        # Resultado
        sa.Column("checkin_id", UUID(as_uuid=True), nullable=True),
        sa.Column("synced_at", sa.DateTime, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        # Retry
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("max_retries", sa.Integer, default=5),
        sa.Column("next_retry_at", sa.DateTime, nullable=True),
        # Expiração
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("is_expired", sa.Boolean, default=False),
        # Metadados
        sa.Column("app_version", sa.String(20), nullable=True),
        sa.Column("device_info", JSONB, default={}),
        sa.Column("network_type", sa.String(20), nullable=True),
        # Timestamps
        sa.Column("queued_at", sa.DateTime, nullable=False),
        sa.Column("received_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_offline_queue_status_retry", "offline_queue", ["status", "next_retry_at"])
    op.create_index("ix_offline_queue_device_pending", "offline_queue", ["device_id", "status"])
    op.create_index("ix_offline_queue_expiration", "offline_queue", ["expires_at", "is_expired"])


def downgrade() -> None:
    """Remove tabelas do módulo Mobile Time Clock."""
    op.drop_table("offline_queue")
    op.drop_table("mobile_checkins")
    op.drop_table("geofence_zones")
    op.drop_table("mobile_devices")
