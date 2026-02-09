"""Sprint 02 - Create mobile API tables.

Revision ID: sprint02_mobile_api
Revises: sprint01_conversation_ai
Create Date: 2026-01-06

Tables:
- device_tokens: Tokens de dispositivos para push notifications
- push_notifications: Histórico de notificações push
- sync_queue: Fila de sincronização offline
- mobile_sessions: Sessões mobile com tokens de sync
"""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint02_mobile_api"
down_revision = "sprint01_conv_ai"
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Create mobile API tables."""

    # ==========================================================================
    # DEVICE TOKENS - Tokens FCM/APNs para notificações push
    # ==========================================================================
    if not table_exists("device_tokens"):
        op.create_table(
            "device_tokens",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token", sa.String(500), nullable=False),
            sa.Column("platform", sa.String(20), nullable=False),
            sa.Column("device_id", sa.String(100), nullable=False),
            sa.Column("device_name", sa.String(100), nullable=True),
            sa.Column("device_model", sa.String(100), nullable=True),
            sa.Column("os_version", sa.String(50), nullable=True),
            sa.Column("app_version", sa.String(50), nullable=True),
            sa.Column("push_enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("locale", sa.String(10), nullable=True),
            sa.Column("timezone", sa.String(50), nullable=True),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])
        op.create_index("ix_device_tokens_token", "device_tokens", ["token"])
        op.create_index("ix_device_tokens_platform", "device_tokens", ["platform"])
        op.create_index("ix_device_tokens_device_id", "device_tokens", ["device_id"])
        op.create_index(
            "ix_device_tokens_active", "device_tokens", ["is_active"], postgresql_where=sa.text("is_active = true")
        )
        op.create_unique_constraint("uq_device_tokens_token_platform", "device_tokens", ["token", "platform"])

    # ==========================================================================
    # PUSH NOTIFICATIONS - Histórico de notificações enviadas
    # ==========================================================================
    if not table_exists("push_notifications"):
        op.create_table(
            "push_notifications",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column(
                "device_token_id",
                UUID(as_uuid=True),
                sa.ForeignKey("device_tokens.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("notification_type", sa.String(20), nullable=False, server_default="info"),
            sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
            sa.Column("data_payload", JSONB, nullable=True),
            sa.Column("image_url", sa.String(500), nullable=True),
            sa.Column("action_url", sa.String(500), nullable=True),
            sa.Column("category", sa.String(50), nullable=True),
            sa.Column("thread_id", sa.String(100), nullable=True),
            sa.Column("collapse_key", sa.String(100), nullable=True),
            sa.Column("ttl_seconds", sa.Integer(), server_default="86400", nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("external_id", sa.String(100), nullable=True),
            sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
            sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_push_notifications_user_id", "push_notifications", ["user_id"])
        op.create_index("ix_push_notifications_status", "push_notifications", ["status"])
        op.create_index("ix_push_notifications_type", "push_notifications", ["notification_type"])
        op.create_index("ix_push_notifications_created_at", "push_notifications", ["created_at"])

    # ==========================================================================
    # SYNC QUEUE - Fila de operações para sincronização offline
    # ==========================================================================
    if not table_exists("sync_queue"):
        op.create_table(
            "sync_queue",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("device_id", sa.String(100), nullable=False),
            sa.Column("operation_type", sa.String(20), nullable=False),
            sa.Column("table_name", sa.String(100), nullable=False),
            sa.Column("record_id", sa.String(100), nullable=False),
            sa.Column("data", JSONB, nullable=True),
            sa.Column("changed_fields", JSONB, nullable=True),
            sa.Column("client_timestamp", sa.DateTime(timezone=True), nullable=False),
            sa.Column("server_timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
            sa.Column("conflict_resolution", sa.String(30), nullable=True),
            sa.Column("conflict_data", JSONB, nullable=True),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_sync_queue_user_id", "sync_queue", ["user_id"])
        op.create_index("ix_sync_queue_device_id", "sync_queue", ["device_id"])
        op.create_index("ix_sync_queue_status", "sync_queue", ["status"])
        op.create_index("ix_sync_queue_table_record", "sync_queue", ["table_name", "record_id"])

    # ==========================================================================
    # MOBILE SESSIONS - Sessões mobile com controle de sync
    # ==========================================================================
    if not table_exists("mobile_sessions"):
        op.create_table(
            "mobile_sessions",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("device_id", sa.String(100), nullable=False),
            sa.Column("sync_token", sa.String(64), nullable=False),
            sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("cached_modules", JSONB, server_default="[]", nullable=False),
            sa.Column("cache_version", sa.Integer(), server_default="1", nullable=False),
            sa.Column("offline_data_size", sa.BigInteger(), server_default="0", nullable=False),
            sa.Column("pending_operations", sa.Integer(), server_default="0", nullable=False),
            sa.Column("connection_quality", sa.String(20), nullable=True),
            sa.Column("battery_level", sa.String(20), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_mobile_sessions_user_id", "mobile_sessions", ["user_id"])
        op.create_index("ix_mobile_sessions_device_id", "mobile_sessions", ["device_id"])
        op.create_index("ix_mobile_sessions_sync_token", "mobile_sessions", ["sync_token"])
        op.create_unique_constraint("uq_mobile_sessions_user_device", "mobile_sessions", ["user_id", "device_id"])

    # ==========================================================================
    # NOTIFICATION PREFERENCES - Preferências de notificação do usuário
    # ==========================================================================
    if not table_exists("notification_preferences"):
        op.create_table(
            "notification_preferences",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column(
                "user_id",
                UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                unique=True,
            ),
            sa.Column("push_enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("email_enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("sms_enabled", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("quiet_hours_enabled", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("quiet_hours_start", sa.String(5), server_default="22:00", nullable=True),
            sa.Column("quiet_hours_end", sa.String(5), server_default="07:00", nullable=True),
            sa.Column(
                "categories",
                JSONB,
                server_default='{"system": true, "alert": true, "info": true, "marketing": false}',
                nullable=False,
            ),
            sa.Column("sound_enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("vibration_enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("badge_enabled", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"])


def downgrade() -> None:
    """Drop mobile API tables."""
    op.drop_table("notification_preferences")
    op.drop_table("mobile_sessions")
    op.drop_table("sync_queue")
    op.drop_table("push_notifications")
    op.drop_table("device_tokens")
