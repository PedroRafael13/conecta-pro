"""Sprint 05 - Create Marketplace Tables.

Revision ID: sprint05_marketplace
Revises: sprint04_analytics
Create Date: 2025-01-07

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers
revision = "sprint05_marketplace"
down_revision = "sprint04_analytics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create marketplace tables."""

    # 1. Installed Integrations
    op.create_table(
        "marketplace_integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="active"),
        sa.Column(
            "config",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("config_encrypted", sa.Text),  # Configurações sensíveis
        sa.Column("version", sa.String(50)),
        sa.Column("auth_method", sa.String(50)),
        sa.Column("last_sync_at", sa.DateTime(timezone=True)),
        sa.Column("sync_status", sa.String(20)),
        sa.Column("sync_error", sa.Text),
        sa.Column("installed_by", sa.String(100)),
        sa.Column(
            "installed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "connector_slug",
            name="uq_integration_tenant_connector",
        ),
    )

    op.create_index(
        "ix_integrations_tenant",
        "marketplace_integrations",
        ["tenant_id"],
    )

    op.create_index(
        "ix_integrations_connector",
        "marketplace_integrations",
        ["connector_slug"],
    )

    op.create_index(
        "ix_integrations_status",
        "marketplace_integrations",
        ["status"],
    )

    # 2. OAuth Credentials
    op.create_table(
        "marketplace_oauth_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("access_token_encrypted", sa.Text),
        sa.Column("refresh_token_encrypted", sa.Text),
        sa.Column("token_type", sa.String(50), default="Bearer"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("scopes", postgresql.ARRAY(sa.String(100))),
        sa.Column(
            "oauth_config",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.UniqueConstraint(
            "tenant_id",
            "connector_slug",
            name="uq_oauth_tenant_connector",
        ),
    )

    # 3. API Keys
    op.create_table(
        "marketplace_api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("key_id", sa.String(50), nullable=False),
        sa.Column("api_key_hash", sa.String(128), nullable=False),
        sa.Column("api_secret_hash", sa.String(128)),
        sa.Column("permissions", postgresql.ARRAY(sa.String(100))),
        sa.Column("rate_limit", sa.Integer),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("usage_count", sa.Integer, default=0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )

    op.create_index(
        "ix_api_keys_tenant",
        "marketplace_api_keys",
        ["tenant_id"],
    )

    op.create_index(
        "ix_api_keys_key_id",
        "marketplace_api_keys",
        ["key_id"],
        unique=True,
    )

    # 4. Webhook Subscriptions
    op.create_table(
        "marketplace_webhook_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("secret_hash", sa.String(128)),
        sa.Column("events", postgresql.ARRAY(sa.String(100))),
        sa.Column(
            "headers",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("status", sa.String(20), nullable=False, default="active"),
        sa.Column("max_retries", sa.Integer, default=5),
        sa.Column("retry_delay_seconds", sa.Integer, default=60),
        sa.Column("timeout_seconds", sa.Integer, default=30),
        sa.Column("consecutive_failures", sa.Integer, default=0),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True)),
        sa.Column("last_success_at", sa.DateTime(timezone=True)),
        sa.Column("last_failure_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_index(
        "ix_webhook_subs_tenant",
        "marketplace_webhook_subscriptions",
        ["tenant_id"],
    )

    op.create_index(
        "ix_webhook_subs_connector",
        "marketplace_webhook_subscriptions",
        ["connector_slug"],
    )

    op.create_index(
        "ix_webhook_subs_status",
        "marketplace_webhook_subscriptions",
        ["status"],
    )

    # 5. Webhook Deliveries
    op.create_table(
        "marketplace_webhook_deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("marketplace_webhook_subscriptions.id"),
            nullable=False,
        ),
        sa.Column("event_id", postgresql.UUID(as_uuid=True)),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("request_body", sa.Text),
        sa.Column(
            "request_headers",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("response_status_code", sa.Integer),
        sa.Column("response_body", sa.Text),
        sa.Column(
            "response_headers",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("attempt_count", sa.Integer, default=0),
        sa.Column("next_retry_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text),
        sa.Column("latency_ms", sa.Float),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True)),
    )

    op.create_index(
        "ix_webhook_deliveries_subscription",
        "marketplace_webhook_deliveries",
        ["subscription_id"],
    )

    op.create_index(
        "ix_webhook_deliveries_status",
        "marketplace_webhook_deliveries",
        ["status"],
    )

    op.create_index(
        "ix_webhook_deliveries_created",
        "marketplace_webhook_deliveries",
        ["created_at"],
    )

    # 6. Sync History
    op.create_table(
        "marketplace_sync_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("direction", sa.String(20), nullable=False),  # inbound, outbound
        sa.Column("mode", sa.String(20), nullable=False),  # full, incremental
        sa.Column("entity_type", sa.String(100)),
        sa.Column("status", sa.String(20), nullable=False, default="running"),
        sa.Column("records_fetched", sa.Integer, default=0),
        sa.Column("records_created", sa.Integer, default=0),
        sa.Column("records_updated", sa.Integer, default=0),
        sa.Column("records_deleted", sa.Integer, default=0),
        sa.Column("records_skipped", sa.Integer, default=0),
        sa.Column("records_failed", sa.Integer, default=0),
        sa.Column(
            "errors",
            postgresql.JSONB,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("warnings", postgresql.ARRAY(sa.Text)),
        sa.Column("cursor", sa.String(500)),
        sa.Column("duration_seconds", sa.Float),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_index(
        "ix_sync_history_tenant",
        "marketplace_sync_history",
        ["tenant_id"],
    )

    op.create_index(
        "ix_sync_history_connector",
        "marketplace_sync_history",
        ["connector_slug"],
    )

    op.create_index(
        "ix_sync_history_started",
        "marketplace_sync_history",
        ["started_at"],
    )

    # 7. Transform Pipelines
    op.create_table(
        "marketplace_transform_pipelines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("source_schema", postgresql.JSONB),
        sa.Column("target_schema", postgresql.JSONB),
        sa.Column(
            "mappings",
            postgresql.JSONB,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "pre_transforms",
            postgresql.JSONB,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "post_transforms",
            postgresql.JSONB,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_index(
        "ix_transform_pipelines_tenant",
        "marketplace_transform_pipelines",
        ["tenant_id"],
    )

    # 8. Integration Health Checks
    op.create_table(
        "marketplace_health_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("latency_ms", sa.Float),
        sa.Column("message", sa.Text),
        sa.Column(
            "details",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "checked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_health_checks_tenant_connector",
        "marketplace_health_checks",
        ["tenant_id", "connector_slug"],
    )

    op.create_index(
        "ix_health_checks_checked",
        "marketplace_health_checks",
        ["checked_at"],
    )

    # 9. Integration Alerts
    op.create_table(
        "marketplace_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text),
        sa.Column("metric_name", sa.String(100)),
        sa.Column("metric_value", sa.Float),
        sa.Column("threshold", sa.Float),
        sa.Column("acknowledged", sa.Boolean, default=False),
        sa.Column("acknowledged_by", sa.String(100)),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("resolved", sa.Boolean, default=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_alerts_tenant",
        "marketplace_alerts",
        ["tenant_id"],
    )

    op.create_index(
        "ix_alerts_connector",
        "marketplace_alerts",
        ["connector_slug"],
    )

    op.create_index(
        "ix_alerts_severity",
        "marketplace_alerts",
        ["severity"],
    )

    op.create_index(
        "ix_alerts_resolved",
        "marketplace_alerts",
        ["resolved"],
    )

    # 10. Integration Metrics (Time series)
    op.create_table(
        "marketplace_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_type", sa.String(20), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column(
            "labels",
            postgresql.JSONB,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_metrics_tenant_connector",
        "marketplace_metrics",
        ["tenant_id", "connector_slug"],
    )

    op.create_index(
        "ix_metrics_name",
        "marketplace_metrics",
        ["metric_name"],
    )

    op.create_index(
        "ix_metrics_timestamp",
        "marketplace_metrics",
        ["timestamp"],
    )

    # 11. Request Logs
    op.create_table(
        "marketplace_request_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False),
        sa.Column("connector_slug", sa.String(100), nullable=False),
        sa.Column("request_id", sa.String(100)),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("status_code", sa.Integer),
        sa.Column("success", sa.Boolean),
        sa.Column("latency_ms", sa.Float),
        sa.Column("retries", sa.Integer, default=0),
        sa.Column("rate_limited", sa.Boolean, default=False),
        sa.Column("circuit_broken", sa.Boolean, default=False),
        sa.Column("error_message", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_request_logs_tenant_connector",
        "marketplace_request_logs",
        ["tenant_id", "connector_slug"],
    )

    op.create_index(
        "ix_request_logs_created",
        "marketplace_request_logs",
        ["created_at"],
    )


def downgrade() -> None:
    """Drop marketplace tables."""

    op.drop_table("marketplace_request_logs")
    op.drop_table("marketplace_metrics")
    op.drop_table("marketplace_alerts")
    op.drop_table("marketplace_health_checks")
    op.drop_table("marketplace_transform_pipelines")
    op.drop_table("marketplace_sync_history")
    op.drop_table("marketplace_webhook_deliveries")
    op.drop_table("marketplace_webhook_subscriptions")
    op.drop_table("marketplace_api_keys")
    op.drop_table("marketplace_oauth_credentials")
    op.drop_table("marketplace_integrations")
