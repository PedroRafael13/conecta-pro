"""Sprint 37 - Create Push Notifications tables.

Revision ID: sprint37_push_notifications
Revises: sprint36_notification_hub
Create Date: 2025-01-05

Sprint 37 - Push Notifications Mobile:
- push_devices: Dispositivos registrados para push
- push_device_sessions: Sessões de dispositivo
- push_campaigns: Campanhas de push marketing
- push_segments: Segmentos de audiência
- push_notifications: Notificações enviadas
- push_notification_actions: Ações de notificação
- push_metrics: Métricas agregadas
- push_ab_test_results: Resultados de testes A/B
- push_delivery_reports: Relatórios de entrega
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint37_push_notifications"
down_revision = "sprint36_notifications"
branch_labels = None
depends_on = None


def create_enum_safe(name: str, values: list):
    """Cria enum de forma segura (ignora se já existir)."""
    values_str = ", ".join([f"'{v}'" for v in values])
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values_str});
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def upgrade() -> None:
    """Create Push Notifications tables."""

    # ========================================================================
    # Enums
    # ========================================================================

    create_enum_safe("device_platform", ["ios", "android", "web", "huawei", "windows", "macos"])
    create_enum_safe("device_status", ["active", "inactive", "unregistered", "blocked", "failed"])
    create_enum_safe(
        "campaign_status", ["draft", "scheduled", "sending", "sent", "paused", "cancelled", "failed", "completed"]
    )
    create_enum_safe("campaign_type", ["one_time", "scheduled", "recurring", "triggered", "ab_test", "transactional"])
    create_enum_safe("target_type", ["all", "segment", "users", "devices", "topic", "tags", "geo"])
    create_enum_safe(
        "notification_status",
        [
            "pending",
            "queued",
            "sending",
            "sent",
            "delivered",
            "opened",
            "clicked",
            "dismissed",
            "failed",
            "expired",
            "undeliverable",
        ],
    )
    create_enum_safe("notification_priority", ["low", "normal", "high", "urgent"])
    create_enum_safe("metric_period", ["hourly", "daily", "weekly", "monthly"])

    # ========================================================================
    # push_devices - Dispositivos registrados
    # ========================================================================

    op.create_table(
        "push_devices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("device_id", sa.String(200), nullable=False),
        sa.Column("device_token", sa.Text, nullable=False),
        sa.Column(
            "platform",
            ENUM("ios", "android", "web", "huawei", "windows", "macos", name="device_platform", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            ENUM("active", "inactive", "unregistered", "blocked", "failed", name="device_status", create_type=False),
            nullable=False,
            server_default="active",
        ),
        sa.Column("app_id", sa.String(200), nullable=False),
        sa.Column("app_version", sa.String(50)),
        sa.Column("app_build", sa.String(50)),
        sa.Column("device_model", sa.String(100)),
        sa.Column("device_brand", sa.String(50)),
        sa.Column("os_version", sa.String(50)),
        sa.Column("language", sa.String(10)),
        sa.Column("timezone", sa.String(50)),
        sa.Column("push_enabled", sa.Boolean, server_default="true"),
        sa.Column("badge_enabled", sa.Boolean, server_default="true"),
        sa.Column("sound_enabled", sa.Boolean, server_default="true"),
        sa.Column("topics", ARRAY(sa.String), server_default="{}"),
        sa.Column("tags", JSONB, server_default="{}"),
        sa.Column("last_active_at", sa.DateTime),
        sa.Column("token_updated_at", sa.DateTime),
        sa.Column("last_notification_at", sa.DateTime),
        sa.Column("last_opened_at", sa.DateTime),
        sa.Column("total_notifications", sa.Integer, server_default="0"),
        sa.Column("total_opened", sa.Integer, server_default="0"),
        sa.Column("total_clicked", sa.Integer, server_default="0"),
        sa.Column("last_error_at", sa.DateTime),
        sa.Column("last_error_code", sa.String(100)),
        sa.Column("last_error_message", sa.Text),
        sa.Column("token_invalidated_at", sa.DateTime),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_unique_constraint(
        "uq_push_devices_tenant_user_device", "push_devices", ["tenant_id", "user_id", "device_id"]
    )
    op.create_index("ix_push_devices_token", "push_devices", ["device_token"])
    op.create_index("ix_push_devices_platform", "push_devices", ["platform"])
    op.create_index("ix_push_devices_app_id", "push_devices", ["app_id"])

    # ========================================================================
    # push_device_sessions - Sessões de dispositivo
    # ========================================================================

    op.create_table(
        "push_device_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "device_id",
            UUID(as_uuid=True),
            sa.ForeignKey("push_devices.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("session_id", sa.String(100), nullable=False),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.Text),
        sa.Column("started_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime),
        sa.Column("duration_seconds", sa.Integer),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # ========================================================================
    # push_segments - Segmentos de audiência
    # ========================================================================

    op.create_table(
        "push_segments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("rules", JSONB, nullable=False, server_default="[]"),
        sa.Column("rules_logic", sa.String(10), server_default="AND"),
        sa.Column("is_dynamic", sa.Boolean, server_default="true"),
        sa.Column("cached_count", sa.Integer),
        sa.Column("cached_at", sa.DateTime),
        sa.Column("cached_device_ids", ARRAY(UUID(as_uuid=True))),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================================================
    # push_campaigns - Campanhas de push
    # ========================================================================

    op.create_table(
        "push_campaigns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column(
            "status",
            ENUM(
                "draft",
                "scheduled",
                "sending",
                "sent",
                "paused",
                "cancelled",
                "failed",
                "completed",
                name="campaign_status",
                create_type=False,
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "campaign_type",
            ENUM(
                "one_time",
                "scheduled",
                "recurring",
                "triggered",
                "ab_test",
                "transactional",
                name="campaign_type",
                create_type=False,
            ),
            nullable=False,
            server_default="one_time",
        ),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("image_url", sa.String(500)),
        sa.Column("icon_url", sa.String(500)),
        sa.Column("action_url", sa.String(500)),
        sa.Column("data", JSONB, server_default="{}"),
        sa.Column("android_config", JSONB, server_default="{}"),
        sa.Column("ios_config", JSONB, server_default="{}"),
        sa.Column("web_config", JSONB, server_default="{}"),
        sa.Column(
            "target_type",
            ENUM("all", "segment", "users", "devices", "topic", "tags", "geo", name="target_type", create_type=False),
            nullable=False,
            server_default="all",
        ),
        sa.Column("segment_id", UUID(as_uuid=True)),
        sa.Column("target_users", ARRAY(UUID(as_uuid=True))),
        sa.Column("target_devices", ARRAY(UUID(as_uuid=True))),
        sa.Column("target_topics", ARRAY(sa.String)),
        sa.Column("target_tags", JSONB),
        sa.Column("geo_targeting", JSONB),
        sa.Column("scheduled_at", sa.DateTime),
        sa.Column("send_immediately", sa.Boolean, server_default="false"),
        sa.Column("timezone", sa.String(50), server_default="UTC"),
        sa.Column("local_time_delivery", sa.Boolean, server_default="false"),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("cancelled_at", sa.DateTime),
        sa.Column("ab_test_config", JSONB),
        sa.Column("ab_test_variants", JSONB),
        sa.Column("ab_test_winner_id", sa.String(50)),
        sa.Column("total_target", sa.Integer, server_default="0"),
        sa.Column("total_sent", sa.Integer, server_default="0"),
        sa.Column("total_delivered", sa.Integer, server_default="0"),
        sa.Column("total_opened", sa.Integer, server_default="0"),
        sa.Column("total_clicked", sa.Integer, server_default="0"),
        sa.Column("total_dismissed", sa.Integer, server_default="0"),
        sa.Column("total_failed", sa.Integer, server_default="0"),
        sa.Column("total_converted", sa.Integer, server_default="0"),
        sa.Column("delivery_rate", sa.Float),
        sa.Column("open_rate", sa.Float),
        sa.Column("click_rate", sa.Float),
        sa.Column("conversion_rate", sa.Float),
        sa.Column("category", sa.String(50)),
        sa.Column("tags", ARRAY(sa.String), server_default="{}"),
        sa.Column("external_id", sa.String(100)),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_index("ix_push_campaigns_status", "push_campaigns", ["status"])
    op.create_index("ix_push_campaigns_scheduled_at", "push_campaigns", ["scheduled_at"])

    # ========================================================================
    # push_notifications - Notificações individuais
    # ========================================================================

    op.create_table(
        "push_notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column(
            "device_id",
            UUID(as_uuid=True),
            sa.ForeignKey("push_devices.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column(
            "campaign_id", UUID(as_uuid=True), sa.ForeignKey("push_campaigns.id", ondelete="SET NULL"), index=True
        ),
        sa.Column("message_id", sa.String(200), unique=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("image_url", sa.String(500)),
        sa.Column("action_url", sa.String(500)),
        sa.Column("data", JSONB, server_default="{}"),
        sa.Column(
            "status",
            ENUM(
                "pending",
                "queued",
                "sending",
                "sent",
                "delivered",
                "opened",
                "clicked",
                "dismissed",
                "failed",
                "expired",
                "undeliverable",
                name="notification_status",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "priority",
            ENUM("low", "normal", "high", "urgent", name="notification_priority", create_type=False),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("ttl_seconds", sa.Integer),
        sa.Column("collapse_key", sa.String(100)),
        sa.Column("queued_at", sa.DateTime),
        sa.Column("sent_at", sa.DateTime),
        sa.Column("delivered_at", sa.DateTime),
        sa.Column("opened_at", sa.DateTime),
        sa.Column("clicked_at", sa.DateTime),
        sa.Column("dismissed_at", sa.DateTime),
        sa.Column("failed_at", sa.DateTime),
        sa.Column("error_code", sa.String(100)),
        sa.Column("error_message", sa.Text),
        sa.Column("provider_message_id", sa.String(200)),
        sa.Column("provider_response", JSONB),
        sa.Column("retry_count", sa.Integer, server_default="0"),
        sa.Column("max_retries", sa.Integer, server_default="3"),
        sa.Column("next_retry_at", sa.DateTime),
        sa.Column("source_type", sa.String(50)),
        sa.Column("source_id", UUID(as_uuid=True)),
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_index("ix_push_notifications_status", "push_notifications", ["status"])
    op.create_index("ix_push_notifications_created", "push_notifications", ["created_at"])

    # ========================================================================
    # push_notification_actions - Ações/cliques em notificações
    # ========================================================================

    op.create_table(
        "push_notification_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notification_id",
            UUID(as_uuid=True),
            sa.ForeignKey("push_notifications.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("action_id", sa.String(50), nullable=False),
        sa.Column("action_type", sa.String(50)),
        sa.Column("action_url", sa.String(500)),
        sa.Column("action_data", JSONB),
        sa.Column("clicked_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # ========================================================================
    # push_metrics - Métricas agregadas
    # ========================================================================

    op.create_table(
        "push_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column(
            "period",
            ENUM("hourly", "daily", "weekly", "monthly", name="metric_period", create_type=False),
            nullable=False,
        ),
        sa.Column("period_start", sa.DateTime, nullable=False),
        sa.Column("period_end", sa.DateTime, nullable=False),
        sa.Column("platform", sa.String(20)),
        sa.Column("app_id", sa.String(200)),
        sa.Column("campaign_id", UUID(as_uuid=True)),
        sa.Column("total_sent", sa.Integer, server_default="0"),
        sa.Column("total_delivered", sa.Integer, server_default="0"),
        sa.Column("total_opened", sa.Integer, server_default="0"),
        sa.Column("total_clicked", sa.Integer, server_default="0"),
        sa.Column("total_dismissed", sa.Integer, server_default="0"),
        sa.Column("total_failed", sa.Integer, server_default="0"),
        sa.Column("total_converted", sa.Integer, server_default="0"),
        sa.Column("active_devices", sa.Integer, server_default="0"),
        sa.Column("new_devices", sa.Integer, server_default="0"),
        sa.Column("unregistered_devices", sa.Integer, server_default="0"),
        sa.Column("avg_time_to_deliver_ms", sa.Integer),
        sa.Column("avg_time_to_open_ms", sa.Integer),
        sa.Column("avg_time_to_click_ms", sa.Integer),
        sa.Column("delivery_rate", sa.Float),
        sa.Column("open_rate", sa.Float),
        sa.Column("click_rate", sa.Float),
        sa.Column("conversion_rate", sa.Float),
        sa.Column("errors_by_code", JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    op.create_unique_constraint(
        "uq_push_metrics_period",
        "push_metrics",
        ["tenant_id", "period", "period_start", "platform", "app_id", "campaign_id"],
    )

    # ========================================================================
    # push_ab_test_results - Resultados de A/B Tests
    # ========================================================================

    op.create_table(
        "push_ab_test_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_id",
            UUID(as_uuid=True),
            sa.ForeignKey("push_campaigns.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("variant_id", sa.String(50), nullable=False),
        sa.Column("variant_name", sa.String(100)),
        sa.Column("total_sent", sa.Integer, server_default="0"),
        sa.Column("total_delivered", sa.Integer, server_default="0"),
        sa.Column("total_opened", sa.Integer, server_default="0"),
        sa.Column("total_clicked", sa.Integer, server_default="0"),
        sa.Column("total_converted", sa.Integer, server_default="0"),
        sa.Column("is_winner", sa.Boolean, server_default="false"),
        sa.Column("confidence_level", sa.Float),
        sa.Column("statistical_significance", sa.Boolean, server_default="false"),
        sa.Column("p_value", sa.Float),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================================================
    # push_delivery_reports - Relatórios de entrega detalhados
    # ========================================================================

    op.create_table(
        "push_delivery_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "campaign_id",
            UUID(as_uuid=True),
            sa.ForeignKey("push_campaigns.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("report_date", sa.Date, nullable=False),
        sa.Column("by_platform", JSONB, server_default="{}"),
        sa.Column("by_status", JSONB, server_default="{}"),
        sa.Column("by_country", JSONB, server_default="{}"),
        sa.Column("by_hour", JSONB, server_default="{}"),
        sa.Column("avg_delivery_time_ms", sa.Integer),
        sa.Column("percentile_95_delivery_time_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop Push Notifications tables."""

    # Drop tables in reverse order
    op.drop_table("push_delivery_reports")
    op.drop_table("push_ab_test_results")
    op.drop_table("push_metrics")
    op.drop_table("push_notification_actions")
    op.drop_table("push_notifications")
    op.drop_table("push_campaigns")
    op.drop_table("push_segments")
    op.drop_table("push_device_sessions")
    op.drop_table("push_devices")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS metric_period")
    op.execute("DROP TYPE IF EXISTS notification_priority")
    op.execute("DROP TYPE IF EXISTS notification_status")
    op.execute("DROP TYPE IF EXISTS target_type")
    op.execute("DROP TYPE IF EXISTS campaign_type")
    op.execute("DROP TYPE IF EXISTS campaign_status")
    op.execute("DROP TYPE IF EXISTS device_status")
    op.execute("DROP TYPE IF EXISTS device_platform")
