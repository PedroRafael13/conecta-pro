"""Sprint 33: Integration Framework - Sólides, Bling, Domínio, GOV

Cria tabelas para o framework de integrações:
- integration_accounts: Credenciais e config por tenant
- sync_runs: Histórico de execuções
- sync_states: Estado incremental por entidade
- id_maps: Mapeamento IDs externos <-> internos

Revision ID: sprint33_integration_framework
Revises: sprint32_create_integrations_tables
Create Date: 2026-01-15 17:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint33_integration_framework"
down_revision = "b0b10e87f1c1"  # add_campo_diaristas_improvements (última revisão aplicada)
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================
    # 1. INTEGRATION_ACCOUNTS
    # ========================================
    op.create_table(
        "integration_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "connector_type",
            sa.Enum("bling", "solides", "dominio", "omie", "nibo", "totvs", "sap", "custom", name="connector_type"),
            nullable=False,
            default="custom",
        ),
        sa.Column(
            "auth_type",
            sa.Enum(
                "api_key",
                "oauth2",
                "oauth2_client_credentials",
                "basic",
                "mtls",
                "certificate",
                "custom",
                name="auth_type",
            ),
            nullable=False,
            default="api_key",
        ),
        # Credenciais criptografadas
        sa.Column("credentials_encrypted", sa.Text, nullable=True),
        sa.Column("credentials_iv", sa.String(64), nullable=True),
        sa.Column("credentials_key_id", sa.String(100), nullable=True),
        # OAuth2
        sa.Column("oauth2_client_id", sa.String(500), nullable=True),
        sa.Column("oauth2_client_secret_encrypted", sa.Text, nullable=True),
        sa.Column("oauth2_token_url", sa.String(500), nullable=True),
        sa.Column("oauth2_authorization_url", sa.String(500), nullable=True),
        sa.Column("oauth2_scopes", postgresql.JSONB, nullable=True),
        sa.Column("oauth2_access_token_encrypted", sa.Text, nullable=True),
        sa.Column("oauth2_refresh_token_encrypted", sa.Text, nullable=True),
        sa.Column("oauth2_token_expires_at", sa.DateTime, nullable=True),
        # Certificado
        sa.Column("certificate_path", sa.String(500), nullable=True),
        sa.Column("certificate_password_encrypted", sa.Text, nullable=True),
        sa.Column("certificate_expires_at", sa.DateTime, nullable=True),
        # Config
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("api_version", sa.String(50), nullable=True),
        sa.Column("environment", sa.String(50), nullable=False, default="production"),
        sa.Column("extra_config", postgresql.JSONB, nullable=True),
        # Rate Limiting
        sa.Column("rate_limit_per_second", sa.Integer, nullable=True),
        sa.Column("rate_limit_per_minute", sa.Integer, nullable=True),
        sa.Column("rate_limit_per_hour", sa.Integer, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "suspended", "error", "pending_auth", "expired", name="account_status"),
            nullable=False,
            default="pending_auth",
        ),
        sa.Column("status_message", sa.Text, nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("last_error_at", sa.DateTime, nullable=True),
        # Health Check
        sa.Column("last_health_check_at", sa.DateTime, nullable=True),
        sa.Column("last_health_check_status", sa.Boolean, nullable=True),
        sa.Column("last_health_check_latency_ms", sa.Integer, nullable=True),
        sa.Column("health_check_failures", sa.Integer, nullable=False, default=0),
        # Sync Config
        sa.Column("sync_enabled", sa.Boolean, nullable=False, default=True),
        sa.Column("sync_interval_minutes", sa.Integer, nullable=False, default=60),
        sa.Column("sync_entities", postgresql.JSONB, nullable=True),
        sa.Column("sync_mode", sa.String(50), nullable=False, default="incremental"),
        sa.Column("last_sync_at", sa.DateTime, nullable=True),
        sa.Column("next_sync_at", sa.DateTime, nullable=True),
        # Feature Flags
        sa.Column("write_enabled", sa.Boolean, nullable=False, default=False),
        sa.Column("webhooks_enabled", sa.Boolean, nullable=False, default=False),
        # Webhook
        sa.Column("webhook_secret", sa.String(200), nullable=True),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        # Meta
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Índices integration_accounts
    op.create_index("ix_integration_accounts_tenant_id", "integration_accounts", ["tenant_id"])
    op.create_index("ix_integration_accounts_connector_type", "integration_accounts", ["connector_type"])
    op.create_index("ix_integration_accounts_status", "integration_accounts", ["status"])
    op.create_index("ix_integration_accounts_environment", "integration_accounts", ["environment"])
    op.create_index("ix_integration_accounts_tenant_connector", "integration_accounts", ["tenant_id", "connector_type"])
    op.create_index("ix_integration_accounts_next_sync_at", "integration_accounts", ["next_sync_at"])
    op.create_index("ix_integration_accounts_ativo", "integration_accounts", ["ativo"])

    # ========================================
    # 2. SYNC_RUNS
    # ========================================
    op.create_table(
        "sync_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("integration_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("correlation_id", sa.String(100), nullable=True),
        sa.Column("parent_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Tipo e Modo
        sa.Column("connector_type", sa.String(50), nullable=False),
        sa.Column(
            "mode",
            sa.Enum("full", "incremental", "delta", "manual", "webhook_triggered", "recovery", name="sync_run_mode"),
            nullable=False,
            default="incremental",
        ),
        sa.Column(
            "trigger",
            sa.Enum("scheduled", "manual", "webhook", "api", "retry", "recovery", name="sync_run_trigger"),
            nullable=False,
            default="scheduled",
        ),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Entidades
        sa.Column("entities", postgresql.JSONB, nullable=True),
        sa.Column("entity_filters", postgresql.JSONB, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.Enum(
                "pending", "running", "completed", "failed", "cancelled", "partial", "timeout", name="sync_run_status"
            ),
            nullable=False,
            default="pending",
        ),
        sa.Column("status_message", sa.Text, nullable=True),
        # Timing
        sa.Column("scheduled_at", sa.DateTime, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("timeout_seconds", sa.Integer, nullable=False, default=3600),
        # Worker
        sa.Column("worker_id", sa.String(100), nullable=True),
        sa.Column("worker_host", sa.String(200), nullable=True),
        # Métricas de Processamento
        sa.Column("items_total", sa.Integer, nullable=False, default=0),
        sa.Column("items_processed", sa.Integer, nullable=False, default=0),
        sa.Column("items_created", sa.Integer, nullable=False, default=0),
        sa.Column("items_updated", sa.Integer, nullable=False, default=0),
        sa.Column("items_deleted", sa.Integer, nullable=False, default=0),
        sa.Column("items_skipped", sa.Integer, nullable=False, default=0),
        sa.Column("items_failed", sa.Integer, nullable=False, default=0),
        # Métricas de API
        sa.Column("api_requests_total", sa.Integer, nullable=False, default=0),
        sa.Column("api_requests_success", sa.Integer, nullable=False, default=0),
        sa.Column("api_requests_failed", sa.Integer, nullable=False, default=0),
        sa.Column("api_rate_limit_hits", sa.Integer, nullable=False, default=0),
        sa.Column("api_total_latency_ms", sa.Integer, nullable=False, default=0),
        # Paginação
        sa.Column("pages_processed", sa.Integer, nullable=False, default=0),
        sa.Column("last_cursor", sa.String(500), nullable=True),
        sa.Column("last_processed_id", sa.String(200), nullable=True),
        sa.Column("last_processed_at", sa.DateTime, nullable=True),
        # Erros
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        sa.Column("errors_log", postgresql.JSONB, nullable=True),
        # Retry
        sa.Column("retry_count", sa.Integer, nullable=False, default=0),
        sa.Column("max_retries", sa.Integer, nullable=False, default=3),
        sa.Column("retry_delay_seconds", sa.Integer, nullable=False, default=60),
        # Checkpoint
        sa.Column("checkpoint_data", postgresql.JSONB, nullable=True),
        sa.Column("can_resume", sa.Boolean, nullable=False, default=True),
        # Resultado
        sa.Column("result_summary", postgresql.JSONB, nullable=True),
        sa.Column("warnings", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices sync_runs
    op.create_index("ix_sync_runs_tenant_id", "sync_runs", ["tenant_id"])
    op.create_index("ix_sync_runs_account_id", "sync_runs", ["account_id"])
    op.create_index("ix_sync_runs_status", "sync_runs", ["status"])
    op.create_index("ix_sync_runs_connector_type", "sync_runs", ["connector_type"])
    op.create_index("ix_sync_runs_correlation_id", "sync_runs", ["correlation_id"])
    op.create_index("ix_sync_runs_started_at", "sync_runs", ["started_at"])
    op.create_index("ix_sync_runs_completed_at", "sync_runs", ["completed_at"])
    op.create_index("ix_sync_runs_tenant_status", "sync_runs", ["tenant_id", "status"])
    op.create_index("ix_sync_runs_account_status", "sync_runs", ["account_id", "status"])
    op.create_index("ix_sync_runs_ativo", "sync_runs", ["ativo"])

    # ========================================
    # 3. SYNC_STATES
    # ========================================
    op.create_table(
        "sync_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("integration_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("connector_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        # Cursor/Pagination
        sa.Column("last_cursor", sa.String(500), nullable=True),
        sa.Column("last_page", sa.Integer, nullable=True),
        sa.Column("last_offset", sa.Integer, nullable=True),
        # Timestamp-based
        sa.Column("last_sync_timestamp", sa.DateTime, nullable=True),
        sa.Column("last_created_at", sa.DateTime, nullable=True),
        sa.Column("last_modified_at", sa.DateTime, nullable=True),
        # ID-based
        sa.Column("last_synced_id", sa.String(200), nullable=True),
        sa.Column("last_synced_external_id", sa.String(200), nullable=True),
        # ETag/Version
        sa.Column("etag", sa.String(200), nullable=True),
        sa.Column("version", sa.String(100), nullable=True),
        # Estatísticas
        sa.Column("total_items_synced", sa.Integer, nullable=False, default=0),
        sa.Column("total_syncs", sa.Integer, nullable=False, default=0),
        sa.Column("last_sync_items", sa.Integer, nullable=False, default=0),
        # Full sync
        sa.Column("last_full_sync_at", sa.DateTime, nullable=True),
        sa.Column("full_sync_required", sa.Boolean, nullable=False, default=False),
        sa.Column("full_sync_reason", sa.String(500), nullable=True),
        # Checkpoint
        sa.Column("checkpoint_data", postgresql.JSONB, nullable=True),
        # Timing
        sa.Column("first_sync_at", sa.DateTime, nullable=True),
        sa.Column("last_sync_at", sa.DateTime, nullable=True),
        sa.Column("last_sync_duration_ms", sa.Integer, nullable=True),
        # Erros
        sa.Column("consecutive_failures", sa.Integer, nullable=False, default=0),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("last_error_at", sa.DateTime, nullable=True),
        # Hash
        sa.Column("schema_hash", sa.String(64), nullable=True),
        # Meta
        sa.Column("extra_state", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Constraint única
    op.create_unique_constraint(
        "uq_sync_state_tenant_account_entity", "sync_states", ["tenant_id", "account_id", "entity_type"]
    )

    # Índices sync_states
    op.create_index("ix_sync_states_tenant_id", "sync_states", ["tenant_id"])
    op.create_index("ix_sync_states_account_id", "sync_states", ["account_id"])
    op.create_index("ix_sync_states_entity_type", "sync_states", ["entity_type"])
    op.create_index("ix_sync_states_connector_type", "sync_states", ["connector_type"])
    op.create_index("ix_sync_states_last_sync_at", "sync_states", ["last_sync_at"])
    op.create_index("ix_sync_states_tenant_account", "sync_states", ["tenant_id", "account_id"])
    op.create_index("ix_sync_states_ativo", "sync_states", ["ativo"])

    # ========================================
    # 4. ID_MAPS
    # ========================================
    op.create_table(
        "id_maps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("integration_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("connector_type", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        # IDs
        sa.Column("external_id", sa.String(500), nullable=False),
        sa.Column("internal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_code", sa.String(200), nullable=True),
        sa.Column("external_reference", sa.String(200), nullable=True),
        # Hash
        sa.Column("data_hash", sa.String(64), nullable=True),
        sa.Column("last_data_hash", sa.String(64), nullable=True),
        # Timestamps
        sa.Column("first_synced_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_synced_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_modified_external_at", sa.DateTime, nullable=True),
        sa.Column("last_modified_internal_at", sa.DateTime, nullable=True),
        # Direção
        sa.Column("last_sync_direction", sa.String(20), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("is_synced", sa.Boolean, nullable=False, default=True),
        sa.Column("needs_update", sa.Boolean, nullable=False, default=False),
        sa.Column("has_conflict", sa.Boolean, nullable=False, default=False),
        # Conflito
        sa.Column("conflict_data", postgresql.JSONB, nullable=True),
        sa.Column("conflict_resolved_at", sa.DateTime, nullable=True),
        sa.Column("conflict_resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Meta
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Constraints únicas
    op.create_unique_constraint(
        "uq_id_map_external", "id_maps", ["tenant_id", "account_id", "entity_type", "external_id"]
    )
    op.create_unique_constraint(
        "uq_id_map_internal", "id_maps", ["tenant_id", "account_id", "entity_type", "internal_id"]
    )

    # Índices id_maps
    op.create_index("ix_id_maps_tenant_id", "id_maps", ["tenant_id"])
    op.create_index("ix_id_maps_account_id", "id_maps", ["account_id"])
    op.create_index("ix_id_maps_entity_type", "id_maps", ["entity_type"])
    op.create_index("ix_id_maps_external_id", "id_maps", ["external_id"])
    op.create_index("ix_id_maps_internal_id", "id_maps", ["internal_id"])
    op.create_index("ix_id_maps_connector_type", "id_maps", ["connector_type"])
    op.create_index("ix_id_maps_external_code", "id_maps", ["external_code"])
    op.create_index("ix_id_maps_tenant_entity", "id_maps", ["tenant_id", "entity_type"])
    op.create_index("ix_id_maps_account_entity", "id_maps", ["account_id", "entity_type"])
    op.create_index("ix_id_maps_needs_update", "id_maps", ["needs_update"])
    op.create_index("ix_id_maps_has_conflict", "id_maps", ["has_conflict"])
    op.create_index("ix_id_maps_ativo", "id_maps", ["ativo"])


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table("id_maps")
    op.drop_table("sync_states")
    op.drop_table("sync_runs")
    op.drop_table("integration_accounts")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS sync_run_status")
    op.execute("DROP TYPE IF EXISTS sync_run_mode")
    op.execute("DROP TYPE IF EXISTS sync_run_trigger")
    op.execute("DROP TYPE IF EXISTS account_status")
    op.execute("DROP TYPE IF EXISTS auth_type")
    op.execute("DROP TYPE IF EXISTS connector_type")
