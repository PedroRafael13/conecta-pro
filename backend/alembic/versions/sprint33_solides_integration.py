"""Sprint 33: Sólides Integration - Tabelas específicas

Cria tabelas para integração Sólides:
- solides_integration_config: Configuração por condomínio
- solides_credential: Credenciais criptografadas
- solides_sync_state: Estado de sincronização por entidade
- solides_sync_log: Histórico de sincronizações
- solides_sync_conflict: Conflitos detectados
- solides_entity_mapping: Mapeamento IDs Sólides <-> Conecta
- solides_webhook_log: Log de webhooks recebidos

Revision ID: sprint33_solides_integration
Revises: sprint33_integration_framework
Create Date: 2026-01-18 10:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint33_solides_integration"
down_revision = "sprint33_integration_framework"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================
    # 1. SOLIDES_INTEGRATION_CONFIG
    # ========================================
    op.create_table(
        "solides_integration_config",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        # Configurações de API
        sa.Column("api_version", sa.String(10), nullable=False, server_default="v1"),
        sa.Column("base_url_v1", sa.String(500), nullable=True),
        sa.Column("base_url_v3", sa.String(500), nullable=True),
        # Configurações de sync
        sa.Column("sync_interval_minutes", sa.Integer, nullable=False, server_default="15"),
        sa.Column("sync_entities", postgresql.JSONB, nullable=True),
        sa.Column("conflict_strategy", sa.String(50), nullable=False, server_default="most_recent"),
        sa.Column("auto_create_departments", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("auto_create_positions", sa.Boolean, nullable=False, server_default="true"),
        # Rate limiting
        sa.Column("rate_limit_per_minute", sa.Integer, nullable=False, server_default="60"),
        # Webhook
        sa.Column("webhook_secret", sa.String(200), nullable=True),
        sa.Column("webhook_url", sa.String(500), nullable=True),
        # Status
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_connected", sa.Boolean, nullable=False, server_default="false"),
        # Health check
        sa.Column("last_health_check_at", sa.DateTime, nullable=True),
        sa.Column("last_health_check_status", sa.Boolean, nullable=True),
        sa.Column("last_health_check_message", sa.Text, nullable=True),
        # Sync status
        sa.Column("last_full_sync_at", sa.DateTime, nullable=True),
        sa.Column("last_incremental_sync_at", sa.DateTime, nullable=True),
        sa.Column("next_sync_at", sa.DateTime, nullable=True),
        # Configurações extras
        sa.Column("extra_config", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("ix_solides_config_condominio", "solides_integration_config", ["condominio_id"])
    op.create_index("ix_solides_config_enabled", "solides_integration_config", ["is_enabled"])
    op.create_index("ix_solides_config_next_sync", "solides_integration_config", ["next_sync_at"])

    # ========================================
    # 2. SOLIDES_CREDENTIAL
    # ========================================
    op.create_table(
        "solides_credential",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "config_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("solides_integration_config.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Credenciais criptografadas
        sa.Column("api_token_encrypted", sa.Text, nullable=False),
        sa.Column("encryption_iv", sa.String(64), nullable=False),
        sa.Column("encryption_key_id", sa.String(100), nullable=False),
        # Validade
        sa.Column("token_expires_at", sa.DateTime, nullable=True),
        sa.Column("is_valid", sa.Boolean, nullable=False, server_default="true"),
        # Último uso
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("last_error_at", sa.DateTime, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("rotated_at", sa.DateTime, nullable=True),
    )

    op.create_index("ix_solides_credential_config", "solides_credential", ["config_id"])
    op.create_index("ix_solides_credential_condominio", "solides_credential", ["condominio_id"])

    # ========================================
    # 3. SOLIDES_SYNC_STATE
    # ========================================
    op.create_table(
        "solides_sync_state",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        # Cursor/Paginação
        sa.Column("last_page", sa.Integer, nullable=True),
        sa.Column("last_cursor", sa.String(500), nullable=True),
        sa.Column("total_pages", sa.Integer, nullable=True),
        # Timestamps
        sa.Column("last_sync_at", sa.DateTime, nullable=True),
        sa.Column("last_modified_at", sa.DateTime, nullable=True),
        sa.Column("last_synced_id", sa.String(200), nullable=True),
        # Estatísticas
        sa.Column("total_items", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_synced", sa.Integer, nullable=False, server_default="0"),
        # Full sync
        sa.Column("last_full_sync_at", sa.DateTime, nullable=True),
        sa.Column("full_sync_required", sa.Boolean, nullable=False, server_default="false"),
        # Checkpoint
        sa.Column("checkpoint_data", postgresql.JSONB, nullable=True),
        # Erros
        sa.Column("consecutive_failures", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("last_error_at", sa.DateTime, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_unique_constraint(
        "uq_solides_sync_state_condominio_entity", "solides_sync_state", ["condominio_id", "entity_type"]
    )
    op.create_index("ix_solides_sync_state_condominio", "solides_sync_state", ["condominio_id"])
    op.create_index("ix_solides_sync_state_entity", "solides_sync_state", ["entity_type"])
    op.create_index("ix_solides_sync_state_last_sync", "solides_sync_state", ["last_sync_at"])

    # ========================================
    # 4. SOLIDES_SYNC_LOG
    # ========================================
    op.create_table(
        "solides_sync_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        # Tipo e direção
        sa.Column(
            "sync_type",
            sa.Enum("full", "incremental", "single", "webhook", name="solides_sync_type"),
            nullable=False,
            server_default="incremental",
        ),
        sa.Column(
            "direction",
            sa.Enum("solides_to_conecta", "conecta_to_solides", "bidirectional", name="solides_sync_direction"),
            nullable=False,
            server_default="solides_to_conecta",
        ),
        # Status
        sa.Column(
            "status",
            sa.Enum("running", "completed", "failed", "cancelled", "partial", name="solides_sync_status"),
            nullable=False,
            server_default="running",
        ),
        # Timing
        sa.Column("started_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        # Métricas
        sa.Column("items_processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_created", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_updated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_deleted", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_skipped", sa.Integer, nullable=False, server_default="0"),
        sa.Column("items_failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("conflicts_detected", sa.Integer, nullable=False, server_default="0"),
        # API metrics
        sa.Column("api_requests", sa.Integer, nullable=False, server_default="0"),
        sa.Column("api_errors", sa.Integer, nullable=False, server_default="0"),
        # Erro
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        # Quem disparou
        sa.Column("triggered_by", sa.String(100), nullable=True),
        sa.Column("triggered_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_solides_sync_log_condominio", "solides_sync_log", ["condominio_id"])
    op.create_index("ix_solides_sync_log_entity", "solides_sync_log", ["entity_type"])
    op.create_index("ix_solides_sync_log_status", "solides_sync_log", ["status"])
    op.create_index("ix_solides_sync_log_started", "solides_sync_log", ["started_at"])
    op.create_index("ix_solides_sync_log_condominio_status", "solides_sync_log", ["condominio_id", "status"])

    # ========================================
    # 5. SOLIDES_SYNC_CONFLICT
    # ========================================
    op.create_table(
        "solides_sync_conflict",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("solides_id", sa.String(200), nullable=False),
        sa.Column("conecta_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Dados conflitantes
        sa.Column("solides_data", postgresql.JSONB, nullable=False),
        sa.Column("conecta_data", postgresql.JSONB, nullable=True),
        sa.Column("diff_fields", postgresql.JSONB, nullable=True),
        # Status
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "resolved_solides",
                "resolved_conecta",
                "resolved_manual",
                "ignored",
                name="solides_conflict_status",
            ),
            nullable=False,
            server_default="pending",
        ),
        # Resolução
        sa.Column("resolution_data", postgresql.JSONB, nullable=True),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        # Timing
        sa.Column("detected_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("sync_log_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index("ix_solides_conflict_condominio", "solides_sync_conflict", ["condominio_id"])
    op.create_index("ix_solides_conflict_entity", "solides_sync_conflict", ["entity_type"])
    op.create_index("ix_solides_conflict_status", "solides_sync_conflict", ["status"])
    op.create_index("ix_solides_conflict_solides_id", "solides_sync_conflict", ["solides_id"])
    op.create_index(
        "ix_solides_conflict_pending",
        "solides_sync_conflict",
        ["condominio_id", "status"],
        postgresql_where=sa.text("status = 'pending'"),
    )

    # ========================================
    # 6. SOLIDES_ENTITY_MAPPING
    # ========================================
    op.create_table(
        "solides_entity_mapping",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        # IDs
        sa.Column("solides_id", sa.String(200), nullable=False),
        sa.Column("conecta_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Hash para detecção de mudanças
        sa.Column("solides_hash", sa.String(64), nullable=True),
        sa.Column("conecta_hash", sa.String(64), nullable=True),
        # Timestamps
        sa.Column("first_synced_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_synced_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("solides_updated_at", sa.DateTime, nullable=True),
        sa.Column("conecta_updated_at", sa.DateTime, nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("sync_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "last_sync_source", sa.Enum("solides", "conecta", "manual", name="solides_sync_source"), nullable=True
        ),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_unique_constraint(
        "uq_solides_mapping_solides", "solides_entity_mapping", ["condominio_id", "entity_type", "solides_id"]
    )
    op.create_unique_constraint(
        "uq_solides_mapping_conecta", "solides_entity_mapping", ["condominio_id", "entity_type", "conecta_id"]
    )
    op.create_index("ix_solides_mapping_condominio", "solides_entity_mapping", ["condominio_id"])
    op.create_index("ix_solides_mapping_entity", "solides_entity_mapping", ["entity_type"])
    op.create_index("ix_solides_mapping_solides_id", "solides_entity_mapping", ["solides_id"])
    op.create_index("ix_solides_mapping_conecta_id", "solides_entity_mapping", ["conecta_id"])

    # ========================================
    # 7. SOLIDES_WEBHOOK_LOG
    # ========================================
    op.create_table(
        "solides_webhook_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        # Payload
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("headers", postgresql.JSONB, nullable=True),
        # Request info
        sa.Column("request_id", sa.String(100), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="received"),
        sa.Column("error", sa.Text, nullable=True),
        # Timing
        sa.Column("received_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        # Retry
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("next_retry_at", sa.DateTime, nullable=True),
        # Auditoria
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_solides_webhook_condominio", "solides_webhook_log", ["condominio_id"])
    op.create_index("ix_solides_webhook_event", "solides_webhook_log", ["event_type"])
    op.create_index("ix_solides_webhook_status", "solides_webhook_log", ["status"])
    op.create_index("ix_solides_webhook_received", "solides_webhook_log", ["received_at"])
    op.create_index(
        "ix_solides_webhook_retry",
        "solides_webhook_log",
        ["status", "next_retry_at"],
        postgresql_where=sa.text("status = 'failed'"),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("solides_webhook_log")
    op.drop_table("solides_entity_mapping")
    op.drop_table("solides_sync_conflict")
    op.drop_table("solides_sync_log")
    op.drop_table("solides_sync_state")
    op.drop_table("solides_credential")
    op.drop_table("solides_integration_config")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS solides_sync_source")
    op.execute("DROP TYPE IF EXISTS solides_conflict_status")
    op.execute("DROP TYPE IF EXISTS solides_sync_status")
    op.execute("DROP TYPE IF EXISTS solides_sync_direction")
    op.execute("DROP TYPE IF EXISTS solides_sync_type")
