"""Sprint 32: Create integrations tables

Revision ID: sprint32_integrations
Revises: sprint31_services
Create Date: 2026-01-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint32_integrations"
down_revision: str | None = "sprint31_services"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create integrations tables."""

    # Tabela api_endpoints
    op.create_table(
        "api_endpoints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.String(20), nullable=False, default="v1"),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column(
            "method",
            sa.Enum("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", name="httpmethod"),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "authentication",
                "clients",
                "services",
                "financial",
                "documents",
                "reports",
                "analytics",
                "webhooks",
                "sync",
                "admin",
                name="endpointcategory",
            ),
            nullable=False,
            default="services",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "deprecated", "beta", "maintenance", "disabled", name="endpointstatus"),
            nullable=False,
            default="active",
        ),
        sa.Column("deprecated_at", sa.DateTime, nullable=True),
        sa.Column("sunset_date", sa.DateTime, nullable=True),
        sa.Column("replacement_endpoint_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requires_auth", sa.Boolean, nullable=False, default=True),
        sa.Column("auth_methods", postgresql.JSONB, nullable=True),
        sa.Column("required_scopes", postgresql.JSONB, nullable=True),
        sa.Column("required_permissions", postgresql.JSONB, nullable=True),
        sa.Column("rate_limit_enabled", sa.Boolean, nullable=False, default=True),
        sa.Column(
            "rate_limit_type",
            sa.Enum("per_second", "per_minute", "per_hour", "per_day", name="ratelimittype"),
            nullable=True,
            default="per_minute",
        ),
        sa.Column("rate_limit_value", sa.Integer, nullable=True, default=60),
        sa.Column("rate_limit_by_key", sa.Boolean, nullable=False, default=True),
        sa.Column("request_schema", postgresql.JSONB, nullable=True),
        sa.Column("response_schema", postgresql.JSONB, nullable=True),
        sa.Column("request_example", postgresql.JSONB, nullable=True),
        sa.Column("response_example", postgresql.JSONB, nullable=True),
        sa.Column("error_responses", postgresql.JSONB, nullable=True),
        sa.Column("request_validation_enabled", sa.Boolean, nullable=False, default=True),
        sa.Column("response_validation_enabled", sa.Boolean, nullable=False, default=False),
        sa.Column("max_request_size_bytes", sa.Integer, nullable=True, default=1048576),
        sa.Column("cache_enabled", sa.Boolean, nullable=False, default=False),
        sa.Column("cache_ttl_seconds", sa.Integer, nullable=True),
        sa.Column("cache_key_pattern", sa.String(200), nullable=True),
        sa.Column("documentation_url", sa.String(500), nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("total_calls", sa.Integer, nullable=False, default=0),
        sa.Column("successful_calls", sa.Integer, nullable=False, default=0),
        sa.Column("failed_calls", sa.Integer, nullable=False, default=0),
        sa.Column("avg_response_time_ms", sa.Integer, nullable=True),
        sa.Column("last_called_at", sa.DateTime, nullable=True),
        sa.Column("timeout_seconds", sa.Integer, nullable=True, default=30),
        sa.Column("retry_enabled", sa.Boolean, nullable=False, default=False),
        sa.Column("retry_count", sa.Integer, nullable=True, default=3),
        sa.Column("circuit_breaker_enabled", sa.Boolean, nullable=False, default=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("ix_api_endpoints_path_method", "api_endpoints", ["path", "method"])
    op.create_index("ix_api_endpoints_category", "api_endpoints", ["category"])
    op.create_index("ix_api_endpoints_status", "api_endpoints", ["status"])
    op.create_index("ix_api_endpoints_version", "api_endpoints", ["version"])
    op.create_index("ix_api_endpoints_ativo", "api_endpoints", ["ativo"])

    # Tabela api_keys
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("key_prefix", sa.String(10), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("key_hint", sa.String(10), nullable=True),
        sa.Column(
            "key_type",
            sa.Enum("production", "sandbox", "development", "testing", name="apikeytype"),
            nullable=False,
            default="production",
        ),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", "expired", "revoked", name="apikeystatus"),
            nullable=False,
            default="active",
        ),
        sa.Column("scopes", postgresql.JSONB, nullable=True),
        sa.Column("allowed_endpoints", postgresql.JSONB, nullable=True),
        sa.Column("blocked_endpoints", postgresql.JSONB, nullable=True),
        sa.Column("rate_limit_per_minute", sa.Integer, nullable=True, default=60),
        sa.Column("rate_limit_per_hour", sa.Integer, nullable=True, default=1000),
        sa.Column("rate_limit_per_day", sa.Integer, nullable=True, default=10000),
        sa.Column("current_minute_calls", sa.Integer, nullable=False, default=0),
        sa.Column("current_hour_calls", sa.Integer, nullable=False, default=0),
        sa.Column("current_day_calls", sa.Integer, nullable=False, default=0),
        sa.Column("last_rate_reset", sa.DateTime, nullable=True),
        sa.Column("ip_whitelist", postgresql.JSONB, nullable=True),
        sa.Column("ip_blacklist", postgresql.JSONB, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("never_expires", sa.Boolean, nullable=False, default=False),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("last_used_ip", sa.String(45), nullable=True),
        sa.Column("last_used_user_agent", sa.String(500), nullable=True),
        sa.Column("total_requests", sa.Integer, nullable=False, default=0),
        sa.Column("successful_requests", sa.Integer, nullable=False, default=0),
        sa.Column("failed_requests", sa.Integer, nullable=False, default=0),
        sa.Column("revoked_at", sa.DateTime, nullable=True),
        sa.Column("revoked_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revocation_reason", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])
    op.create_index("ix_api_keys_client_id", "api_keys", ["client_id"])
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_status", "api_keys", ["status"])
    op.create_index("ix_api_keys_key_type", "api_keys", ["key_type"])
    op.create_index("ix_api_keys_expires_at", "api_keys", ["expires_at"])
    op.create_index("ix_api_keys_ativo", "api_keys", ["ativo"])

    # Tabela webhook_configs
    op.create_table(
        "webhook_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("api_key_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("api_keys.id"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("method", sa.String(10), nullable=False, default="POST"),
        sa.Column("events", postgresql.JSONB, nullable=False),
        sa.Column("event_filters", postgresql.JSONB, nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "disabled", "failing", name="webhookstatus"),
            nullable=False,
            default="active",
        ),
        sa.Column("content_type", sa.String(100), nullable=False, default="application/json"),
        sa.Column(
            "payload_format", sa.Enum("json", "xml", "form", name="webhookformat"), nullable=False, default="json"
        ),
        sa.Column("payload_template", sa.Text, nullable=True),
        sa.Column(
            "auth_type",
            sa.Enum("none", "basic", "bearer", "api_key", "hmac", "oauth2", name="webhookauthtype"),
            nullable=False,
            default="hmac",
        ),
        sa.Column("auth_credentials", postgresql.JSONB, nullable=True),
        sa.Column("secret_key", sa.String(64), nullable=True),
        sa.Column("verify_ssl", sa.Boolean, nullable=False, default=True),
        sa.Column("allowed_ips", postgresql.JSONB, nullable=True),
        sa.Column("custom_headers", postgresql.JSONB, nullable=True),
        sa.Column("retry_enabled", sa.Boolean, nullable=False, default=True),
        sa.Column("max_retries", sa.Integer, nullable=False, default=3),
        sa.Column("retry_delay_seconds", sa.Integer, nullable=False, default=60),
        sa.Column("retry_backoff_multiplier", sa.Integer, nullable=False, default=2),
        sa.Column("timeout_seconds", sa.Integer, nullable=False, default=30),
        sa.Column("connect_timeout_seconds", sa.Integer, nullable=False, default=10),
        sa.Column("batch_enabled", sa.Boolean, nullable=False, default=False),
        sa.Column("batch_size", sa.Integer, nullable=True, default=10),
        sa.Column("batch_interval_seconds", sa.Integer, nullable=True, default=60),
        sa.Column("total_deliveries", sa.Integer, nullable=False, default=0),
        sa.Column("successful_deliveries", sa.Integer, nullable=False, default=0),
        sa.Column("failed_deliveries", sa.Integer, nullable=False, default=0),
        sa.Column("consecutive_failures", sa.Integer, nullable=False, default=0),
        sa.Column("avg_response_time_ms", sa.Integer, nullable=True),
        sa.Column("last_delivery_at", sa.DateTime, nullable=True),
        sa.Column("last_success_at", sa.DateTime, nullable=True),
        sa.Column("last_failure_at", sa.DateTime, nullable=True),
        sa.Column("last_failure_reason", sa.Text, nullable=True),
        sa.Column("disabled_until", sa.DateTime, nullable=True),
        sa.Column("auto_disable_on_failures", sa.Integer, nullable=True, default=10),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("ix_webhook_configs_client_id", "webhook_configs", ["client_id"])
    op.create_index("ix_webhook_configs_api_key_id", "webhook_configs", ["api_key_id"])
    op.create_index("ix_webhook_configs_status", "webhook_configs", ["status"])
    op.create_index("ix_webhook_configs_ativo", "webhook_configs", ["ativo"])

    # Tabela integration_logs
    op.create_table(
        "integration_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "endpoint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("api_endpoints.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "api_key_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("api_keys.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "webhook_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("webhook_configs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sync_queue_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "log_type",
            sa.Enum(
                "api_call",
                "webhook_delivery",
                "sync_operation",
                "authentication",
                "rate_limit",
                "error",
                "system",
                name="logtype",
            ),
            nullable=False,
            default="api_call",
        ),
        sa.Column(
            "level",
            sa.Enum("debug", "info", "warning", "error", "critical", name="loglevel"),
            nullable=False,
            default="info",
        ),
        sa.Column(
            "status",
            sa.Enum(
                "success",
                "failure",
                "pending",
                "timeout",
                "rate_limited",
                "unauthorized",
                "validation_error",
                name="logstatus",
            ),
            nullable=False,
            default="success",
        ),
        sa.Column("correlation_id", sa.String(50), nullable=True),
        sa.Column("trace_id", sa.String(50), nullable=True),
        sa.Column("request_id", sa.String(50), nullable=True),
        sa.Column("method", sa.String(10), nullable=True),
        sa.Column("path", sa.String(500), nullable=True),
        sa.Column("query_params", postgresql.JSONB, nullable=True),
        sa.Column("request_headers", postgresql.JSONB, nullable=True),
        sa.Column("request_body", sa.Text, nullable=True),
        sa.Column("request_size_bytes", sa.Integer, nullable=True),
        sa.Column("response_status_code", sa.Integer, nullable=True),
        sa.Column("response_headers", postgresql.JSONB, nullable=True),
        sa.Column("response_body", sa.Text, nullable=True),
        sa.Column("response_size_bytes", sa.Integer, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("time_to_first_byte_ms", sa.Integer, nullable=True),
        sa.Column("dns_lookup_ms", sa.Integer, nullable=True),
        sa.Column("tcp_connection_ms", sa.Integer, nullable=True),
        sa.Column("ssl_handshake_ms", sa.Integer, nullable=True),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("client_user_agent", sa.String(500), nullable=True),
        sa.Column("client_country", sa.String(2), nullable=True),
        sa.Column("client_region", sa.String(100), nullable=True),
        sa.Column("server_host", sa.String(200), nullable=True),
        sa.Column("server_region", sa.String(50), nullable=True),
        sa.Column("server_version", sa.String(50), nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        sa.Column("stack_trace", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, default=0),
        sa.Column("is_retry", sa.Boolean, nullable=False, default=False),
        sa.Column("original_log_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rate_limit_remaining", sa.Integer, nullable=True),
        sa.Column("rate_limit_reset_at", sa.DateTime, nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_index("ix_integration_logs_endpoint_id", "integration_logs", ["endpoint_id"])
    op.create_index("ix_integration_logs_api_key_id", "integration_logs", ["api_key_id"])
    op.create_index("ix_integration_logs_webhook_id", "integration_logs", ["webhook_id"])
    op.create_index("ix_integration_logs_log_type", "integration_logs", ["log_type"])
    op.create_index("ix_integration_logs_level", "integration_logs", ["level"])
    op.create_index("ix_integration_logs_status", "integration_logs", ["status"])
    op.create_index("ix_integration_logs_correlation_id", "integration_logs", ["correlation_id"])
    op.create_index("ix_integration_logs_trace_id", "integration_logs", ["trace_id"])
    op.create_index("ix_integration_logs_timestamp", "integration_logs", ["timestamp"])
    op.create_index("ix_integration_logs_client_id", "integration_logs", ["client_id"])
    op.create_index("ix_integration_logs_user_id", "integration_logs", ["user_id"])
    op.create_index("ix_integration_logs_timestamp_status", "integration_logs", ["timestamp", "status"])

    # Tabela sync_queue
    op.create_table(
        "sync_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("correlation_id", sa.String(50), nullable=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "external_system",
            sa.Enum(
                "sap",
                "totvs",
                "omie",
                "bling",
                "tiny",
                "netsuite",
                "salesforce",
                "hubspot",
                "pipedrive",
                "custom",
                name="externalsystem",
            ),
            nullable=False,
            default="custom",
        ),
        sa.Column("external_system_config_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "direction",
            sa.Enum("inbound", "outbound", "bidirectional", name="syncdirection"),
            nullable=False,
            default="outbound",
        ),
        sa.Column(
            "entity_type",
            sa.Enum(
                "client",
                "service",
                "service_order",
                "invoice",
                "payment",
                "document",
                "product",
                "inventory",
                "user",
                "lead",
                "proposal",
                "contract",
                name="syncentitytype",
            ),
            nullable=False,
        ),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_id", sa.String(200), nullable=True),
        sa.Column(
            "operation",
            sa.Enum("create", "update", "delete", "upsert", "full_sync", "delta_sync", name="syncoperationtype"),
            nullable=False,
            default="upsert",
        ),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column("payload_hash", sa.String(64), nullable=True),
        sa.Column("previous_payload", postgresql.JSONB, nullable=True),
        sa.Column("transformed_payload", postgresql.JSONB, nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "completed",
                "failed",
                "retrying",
                "cancelled",
                "skipped",
                "partial",
                name="syncstatus",
            ),
            nullable=False,
            default="pending",
        ),
        sa.Column(
            "priority",
            sa.Enum("critical", "high", "normal", "low", "batch", name="syncpriority"),
            nullable=False,
            default="normal",
        ),
        sa.Column("scheduled_at", sa.DateTime, nullable=True),
        sa.Column("not_before", sa.DateTime, nullable=True),
        sa.Column("not_after", sa.DateTime, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("processed_by", sa.String(100), nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, default=0),
        sa.Column("max_retries", sa.Integer, nullable=False, default=3),
        sa.Column("next_retry_at", sa.DateTime, nullable=True),
        sa.Column("retry_delay_seconds", sa.Integer, nullable=False, default=60),
        sa.Column("retry_backoff_multiplier", sa.Integer, nullable=False, default=2),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        sa.Column("last_error_at", sa.DateTime, nullable=True),
        sa.Column("external_response", postgresql.JSONB, nullable=True),
        sa.Column("external_status_code", sa.Integer, nullable=True),
        sa.Column("depends_on", postgresql.JSONB, nullable=True),
        sa.Column("blocks", postgresql.JSONB, nullable=True),
        sa.Column("callback_url", sa.String(500), nullable=True),
        sa.Column("callback_on_success", sa.Boolean, nullable=False, default=False),
        sa.Column("callback_on_failure", sa.Boolean, nullable=False, default=False),
        sa.Column("validation_errors", postgresql.JSONB, nullable=True),
        sa.Column("requires_review", sa.Boolean, nullable=False, default=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("ix_sync_queue_status", "sync_queue", ["status"])
    op.create_index("ix_sync_queue_priority", "sync_queue", ["priority"])
    op.create_index("ix_sync_queue_entity_type", "sync_queue", ["entity_type"])
    op.create_index("ix_sync_queue_entity_id", "sync_queue", ["entity_id"])
    op.create_index("ix_sync_queue_external_system", "sync_queue", ["external_system"])
    op.create_index("ix_sync_queue_external_id", "sync_queue", ["external_id"])
    op.create_index("ix_sync_queue_direction", "sync_queue", ["direction"])
    op.create_index("ix_sync_queue_batch_id", "sync_queue", ["batch_id"])
    op.create_index("ix_sync_queue_correlation_id", "sync_queue", ["correlation_id"])
    op.create_index("ix_sync_queue_scheduled_at", "sync_queue", ["scheduled_at"])
    op.create_index("ix_sync_queue_next_retry_at", "sync_queue", ["next_retry_at"])
    op.create_index("ix_sync_queue_status_priority_scheduled", "sync_queue", ["status", "priority", "scheduled_at"])
    op.create_index("ix_sync_queue_ativo", "sync_queue", ["ativo"])


def downgrade() -> None:
    """Drop integrations tables."""
    op.drop_table("sync_queue")
    op.drop_table("integration_logs")
    op.drop_table("webhook_configs")
    op.drop_table("api_keys")
    op.drop_table("api_endpoints")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS syncpriority")
    op.execute("DROP TYPE IF EXISTS syncstatus")
    op.execute("DROP TYPE IF EXISTS syncoperationtype")
    op.execute("DROP TYPE IF EXISTS syncentitytype")
    op.execute("DROP TYPE IF EXISTS syncdirection")
    op.execute("DROP TYPE IF EXISTS externalsystem")
    op.execute("DROP TYPE IF EXISTS logstatus")
    op.execute("DROP TYPE IF EXISTS loglevel")
    op.execute("DROP TYPE IF EXISTS logtype")
    op.execute("DROP TYPE IF EXISTS webhookauthtype")
    op.execute("DROP TYPE IF EXISTS webhookformat")
    op.execute("DROP TYPE IF EXISTS webhookstatus")
    op.execute("DROP TYPE IF EXISTS apikeystatus")
    op.execute("DROP TYPE IF EXISTS apikeytype")
    op.execute("DROP TYPE IF EXISTS ratelimittype")
    op.execute("DROP TYPE IF EXISTS endpointstatus")
    op.execute("DROP TYPE IF EXISTS endpointcategory")
    op.execute("DROP TYPE IF EXISTS httpmethod")
