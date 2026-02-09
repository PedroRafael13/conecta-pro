"""Sprint 17 - Criar tabelas de integração REP.

Revision ID: sprint17_rep_integration
Revises: sprint16_create_time_tracking_tables
Create Date: 2025-12-31

Tabelas:
- rep_devices: Dispositivos REP (Control iD, Intelbras, etc.)
- rep_events: Eventos brutos recebidos dos REPs
- rep_syncs: Histórico de sincronizações
- afd_records: Registros AFD (Portaria 671 MTE)
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint17_rep_integration"
down_revision = "sprint16_time_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas de integração REP."""

    # ==================== REP_DEVICES ====================
    op.create_table(
        "rep_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Fabricante e modelo
        sa.Column("manufacturer", sa.String(50), nullable=False, default="control_id"),
        sa.Column("model", sa.String(50), nullable=False, default="generic"),
        sa.Column("firmware_version", sa.String(50), nullable=True),
        sa.Column("mte_registration", sa.String(20), nullable=True),
        # Identificação
        sa.Column("serial_number", sa.String(50), nullable=False, unique=True),
        sa.Column("device_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Localização
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("geofence_radius", sa.Integer, default=100),
        # Conexão
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("port", sa.Integer, default=80),
        sa.Column("mac_address", sa.String(17), nullable=True),
        sa.Column("communication_protocol", sa.String(20), default="http_rest"),
        # Autenticação
        sa.Column("auth_method", sa.String(20), default="token"),
        sa.Column("auth_username", sa.String(100), nullable=True),
        sa.Column("auth_password_encrypted", sa.Text, nullable=True),
        sa.Column("api_key_encrypted", sa.Text, nullable=True),
        sa.Column("certificate_path", sa.String(500), nullable=True),
        # Endpoints e configurações
        sa.Column("endpoints_config", postgresql.JSONB, nullable=True, default=dict),
        # Status
        sa.Column("status", sa.String(20), default="offline"),
        sa.Column("last_online", sa.DateTime, nullable=True),
        sa.Column("last_sync", sa.DateTime, nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("last_error_at", sa.DateTime, nullable=True),
        sa.Column("consecutive_errors", sa.Integer, default=0),
        # Sync
        sa.Column("sync_enabled", sa.Boolean, default=True),
        sa.Column("sync_interval_seconds", sa.Integer, default=300),
        sa.Column("sync_mode", sa.String(20), default="pull"),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        sa.Column("webhook_secret", sa.String(100), nullable=True),
        # Capacidades
        sa.Column("supports_biometric", sa.Boolean, default=True),
        sa.Column("supports_facial", sa.Boolean, default=False),
        sa.Column("supports_rfid", sa.Boolean, default=True),
        sa.Column("supports_password", sa.Boolean, default=True),
        sa.Column("supports_qrcode", sa.Boolean, default=False),
        sa.Column("max_users", sa.Integer, default=10000),
        sa.Column("max_fingerprints", sa.Integer, default=20000),
        sa.Column("max_faces", sa.Integer, default=3000),
        sa.Column("max_events_storage", sa.Integer, default=100000),
        # Contadores
        sa.Column("registered_users", sa.Integer, default=0),
        sa.Column("registered_fingerprints", sa.Integer, default=0),
        sa.Column("registered_faces", sa.Integer, default=0),
        sa.Column("events_count", sa.Integer, default=0),
        sa.Column("events_pending_sync", sa.Integer, default=0),
        # Configurações adicionais
        sa.Column("timezone", sa.String(50), default="America/Sao_Paulo"),
        sa.Column("ntp_server", sa.String(100), nullable=True),
        sa.Column("auto_adjust_time", sa.Boolean, default=True),
        sa.Column("time_drift_tolerance_seconds", sa.Integer, default=30),
        sa.Column("vendor_config", postgresql.JSONB, nullable=True, default=dict),
        # Auditoria
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Índices rep_devices
    op.create_index("ix_rep_devices_condominio", "rep_devices", ["condominio_id"])
    op.create_index("ix_rep_devices_status", "rep_devices", ["status"])
    op.create_index("ix_rep_devices_condominio_status", "rep_devices", ["condominio_id", "status"])
    op.create_index("ix_rep_devices_manufacturer", "rep_devices", ["manufacturer"])
    op.create_index("ix_rep_devices_serial", "rep_devices", ["serial_number"])
    op.create_index("ix_rep_devices_active", "rep_devices", ["is_active"])

    # ==================== REP_EVENTS ====================
    op.create_table(
        "rep_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rep_devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # NSR
        sa.Column("nsr", sa.Integer, nullable=False),
        # Dados do evento
        sa.Column("event_datetime", sa.DateTime, nullable=False),
        sa.Column("event_date", sa.Date, nullable=False),
        sa.Column("event_time", sa.Time, nullable=False),
        sa.Column("event_type", sa.String(20), nullable=False, default="entry"),
        # Identificação do funcionário
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("pis_number", sa.String(11), nullable=True),
        sa.Column("employee_code", sa.String(50), nullable=True),
        sa.Column("employee_name", sa.String(200), nullable=True),
        # Método de identificação
        sa.Column("identification_method", sa.String(20), nullable=False, default="biometric"),
        sa.Column("identification_score", sa.Integer, nullable=True),
        # Dados biométricos
        sa.Column("biometric_hash", sa.String(64), nullable=True),
        sa.Column("finger_index", sa.Integer, nullable=True),
        # Cartão RFID
        sa.Column("card_number", sa.String(50), nullable=True),
        sa.Column("card_facility_code", sa.String(20), nullable=True),
        # Foto
        sa.Column("photo_captured", sa.Boolean, default=False),
        sa.Column("photo_path", sa.String(500), nullable=True),
        # Geolocalização
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("location_accuracy", sa.Float, nullable=True),
        # Status e processamento
        sa.Column("status", sa.String(20), default="received"),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("time_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Erros
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_code", sa.String(20), nullable=True),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("max_retries", sa.Integer, default=3),
        # Dados brutos
        sa.Column("raw_data", postgresql.JSONB, nullable=True),
        sa.Column("afd_line", sa.String(100), nullable=True),
        # Validações
        sa.Column("is_valid", sa.Boolean, default=True),
        sa.Column("validation_errors", postgresql.JSONB, nullable=True, default=list),
        # Sync
        sa.Column("sync_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("received_at", sa.DateTime, server_default=sa.func.now()),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Índices rep_events
    op.create_index("ix_rep_events_device", "rep_events", ["device_id"])
    op.create_index("ix_rep_events_condominio", "rep_events", ["condominio_id"])
    op.create_index("ix_rep_events_device_nsr", "rep_events", ["device_id", "nsr"], unique=True)
    op.create_index("ix_rep_events_device_datetime", "rep_events", ["device_id", "event_datetime"])
    op.create_index("ix_rep_events_employee_date", "rep_events", ["employee_id", "event_date"])
    op.create_index("ix_rep_events_pis_date", "rep_events", ["pis_number", "event_date"])
    op.create_index("ix_rep_events_status", "rep_events", ["status"])
    op.create_index("ix_rep_events_event_date", "rep_events", ["event_date"])

    # ==================== REP_SYNCS ====================
    op.create_table(
        "rep_syncs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rep_devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Tipo e status
        sa.Column("sync_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("trigger", sa.String(20), default="scheduled"),
        # Timestamps
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        # Progresso
        sa.Column("total_items", sa.Integer, default=0),
        sa.Column("processed_items", sa.Integer, default=0),
        sa.Column("success_items", sa.Integer, default=0),
        sa.Column("error_items", sa.Integer, default=0),
        sa.Column("skipped_items", sa.Integer, default=0),
        # NSR
        sa.Column("last_nsr_before", sa.Integer, nullable=True),
        sa.Column("last_nsr_after", sa.Integer, nullable=True),
        sa.Column("events_from_datetime", sa.DateTime, nullable=True),
        sa.Column("events_to_datetime", sa.DateTime, nullable=True),
        # Erros
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        # Retries
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("max_retries", sa.Integer, default=3),
        sa.Column("next_retry_at", sa.DateTime, nullable=True),
        # Logs
        sa.Column("request_log", postgresql.JSONB, nullable=True),
        sa.Column("response_log", postgresql.JSONB, nullable=True),
        sa.Column("items_log", postgresql.JSONB, nullable=True),
        # Métricas
        sa.Column("bytes_transferred", sa.Integer, default=0),
        sa.Column("api_calls_made", sa.Integer, default=0),
        # Quem disparou
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Índices rep_syncs
    op.create_index("ix_rep_syncs_device", "rep_syncs", ["device_id"])
    op.create_index("ix_rep_syncs_condominio", "rep_syncs", ["condominio_id"])
    op.create_index("ix_rep_syncs_device_type", "rep_syncs", ["device_id", "sync_type"])
    op.create_index("ix_rep_syncs_device_created", "rep_syncs", ["device_id", "created_at"])
    op.create_index("ix_rep_syncs_status", "rep_syncs", ["status"])

    # ==================== AFD_RECORDS ====================
    op.create_table(
        "afd_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rep_devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # NSR e tipo
        sa.Column("nsr", sa.Integer, nullable=False),
        sa.Column("record_type", sa.String(1), nullable=False, default="3"),
        sa.Column("afd_line", sa.String(200), nullable=False),
        # Dados tipo 3 (marcação)
        sa.Column("record_date", sa.Date, nullable=True),
        sa.Column("record_time", sa.Time, nullable=True),
        sa.Column("pis_number", sa.String(12), nullable=True),
        # Dados tipo 2 (empregador)
        sa.Column("cnpj", sa.String(14), nullable=True),
        sa.Column("cei", sa.String(12), nullable=True),
        sa.Column("company_name", sa.String(150), nullable=True),
        # Dados tipo 1 (cabeçalho)
        sa.Column("rep_serial", sa.String(17), nullable=True),
        sa.Column("rep_manufacturer", sa.String(20), nullable=True),
        sa.Column("rep_model", sa.String(20), nullable=True),
        sa.Column("generation_date", sa.DateTime, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        # Dados tipo 4 (ajuste)
        sa.Column("original_date", sa.Date, nullable=True),
        sa.Column("original_time", sa.Time, nullable=True),
        sa.Column("adjusted_date", sa.Date, nullable=True),
        sa.Column("adjusted_time", sa.Time, nullable=True),
        # Referência ao evento
        sa.Column(
            "event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rep_events.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Integridade
        sa.Column("line_hash", sa.String(64), nullable=False),
        # Exportação
        sa.Column("is_exported", sa.Boolean, default=False),
        sa.Column("exported_at", sa.DateTime, nullable=True),
        sa.Column("export_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Validação
        sa.Column("is_valid", sa.Boolean, default=True),
        sa.Column("validation_error", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Índices afd_records
    op.create_index("ix_afd_records_device", "afd_records", ["device_id"])
    op.create_index("ix_afd_records_condominio", "afd_records", ["condominio_id"])
    op.create_index("ix_afd_records_device_nsr", "afd_records", ["device_id", "nsr"], unique=True)
    op.create_index("ix_afd_records_device_date", "afd_records", ["device_id", "record_date"])
    op.create_index("ix_afd_records_pis_date", "afd_records", ["pis_number", "record_date"])
    op.create_index("ix_afd_records_type", "afd_records", ["record_type"])
    op.create_index("ix_afd_records_exported", "afd_records", ["is_exported"])


def downgrade() -> None:
    """Remove tabelas de integração REP."""

    op.drop_table("afd_records")
    op.drop_table("rep_syncs")
    op.drop_table("rep_events")
    op.drop_table("rep_devices")
