"""Sprint 03 - Create intelligent notifications tables.

Revision ID: sprint03_intelligent
Revises: sprint02_mobile_api
Create Date: 2025-01-06

Tabelas para:
- Personalization engine
- A/B Testing
- Analytics
- LGPD Compliance
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision: str = "sprint03_intelligent"
down_revision: Union[str, None] = "sprint02_mobile_api"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Criar tabelas para notificações inteligentes."""

    if not table_exists("user_behavior_profiles"):
        op.create_table(
            "user_behavior_profiles",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True, index=True),
            sa.Column("engagement_level", sa.String(50), nullable=False, server_default="moderate"),
            sa.Column("patterns", postgresql.JSONB, server_default="[]"),
            sa.Column("preferred_hours", postgresql.ARRAY(sa.Integer()), server_default="{}"),
            sa.Column("preferred_days", postgresql.ARRAY(sa.Integer()), server_default="{}"),
            sa.Column("avg_response_time_minutes", sa.Float(), server_default="30.0"),
            sa.Column("notification_fatigue_score", sa.Float(), server_default="0.0"),
            sa.Column("churn_risk_score", sa.Float(), server_default="0.0"),
            sa.Column("segment", sa.String(50), server_default="standard"),
            sa.Column("last_activity", sa.DateTime(timezone=True)),
            sa.Column("metrics", postgresql.JSONB, server_default="{}"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        )
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_behavior_churn_risk
            ON user_behavior_profiles (churn_risk_score DESC)
            WHERE churn_risk_score > 0.5
        """)

    if not table_exists("ab_experiments"):
        op.create_table(
            "ab_experiments",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("status", sa.String(50), nullable=False, server_default="draft", index=True),
            sa.Column("primary_metric", sa.String(50), nullable=False),
            sa.Column("secondary_metrics", postgresql.ARRAY(sa.String(50))),
            sa.Column("target_sample_size", sa.Integer(), server_default="1000"),
            sa.Column("min_confidence_level", sa.Float(), server_default="0.95"),
            sa.Column("filters", postgresql.JSONB, server_default="{}"),
            sa.Column("start_date", sa.DateTime(timezone=True)),
            sa.Column("end_date", sa.DateTime(timezone=True)),
            sa.Column("tenant_id", sa.String(100), index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        )
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_experiments_active
            ON ab_experiments (start_date, end_date)
            WHERE status = 'running'
        """)

    if not table_exists("ab_experiment_variants"):
        op.create_table(
            "ab_experiment_variants",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ab_experiments.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("variant_id", sa.String(50), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("weight", sa.Float(), server_default="0.5"),
            sa.Column("is_control", sa.Boolean(), server_default="false"),
            sa.Column("config", postgresql.JSONB, server_default="{}"),
            sa.Column("impressions", sa.Integer(), server_default="0"),
            sa.Column("opens", sa.Integer(), server_default="0"),
            sa.Column("clicks", sa.Integer(), server_default="0"),
            sa.Column("conversions", sa.Integer(), server_default="0"),
            sa.Column("unsubscribes", sa.Integer(), server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.UniqueConstraint("experiment_id", "variant_id", name="uq_experiment_variant"),
        )

    if not table_exists("ab_experiment_events"):
        op.create_table(
            "ab_experiment_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ab_experiments.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("variant_id", sa.String(50), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column("event_type", sa.String(50), nullable=False, index=True),
            sa.Column("metadata", postgresql.JSONB, server_default="{}"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), index=True),
        )
        op.create_index("ix_ab_events_experiment_variant", "ab_experiment_events", ["experiment_id", "variant_id"])

    if not table_exists("notification_analytics"):
        op.create_table(
            "notification_analytics",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("date", sa.Date(), nullable=False, index=True),
            sa.Column("hour", sa.Integer()),
            sa.Column("channel", sa.String(50), nullable=False, index=True),
            sa.Column("notification_type", sa.String(100), index=True),
            sa.Column("campaign_id", sa.String(100), index=True),
            sa.Column("tenant_id", sa.String(100), index=True),
            sa.Column("total_sent", sa.Integer(), server_default="0"),
            sa.Column("total_delivered", sa.Integer(), server_default="0"),
            sa.Column("total_opened", sa.Integer(), server_default="0"),
            sa.Column("total_clicked", sa.Integer(), server_default="0"),
            sa.Column("total_converted", sa.Integer(), server_default="0"),
            sa.Column("total_unsubscribed", sa.Integer(), server_default="0"),
            sa.Column("total_bounced", sa.Integer(), server_default="0"),
            sa.Column("total_complained", sa.Integer(), server_default="0"),
            sa.Column("avg_delivery_time_ms", sa.Float()),
            sa.Column("cost", sa.Numeric(10, 4), server_default="0"),
            sa.Column("revenue", sa.Numeric(10, 2), server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.UniqueConstraint("date", "hour", "channel", "notification_type", "tenant_id", name="uq_analytics_granularity"),
        )

    if not table_exists("user_consents"):
        op.create_table(
            "user_consents",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column("consent_type", sa.String(50), nullable=False, index=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending", index=True),
            sa.Column("granted_at", sa.DateTime(timezone=True)),
            sa.Column("withdrawn_at", sa.DateTime(timezone=True)),
            sa.Column("expires_at", sa.DateTime(timezone=True)),
            sa.Column("ip_address", sa.String(45)),
            sa.Column("user_agent", sa.Text()),
            sa.Column("consent_text", sa.Text(), nullable=False),
            sa.Column("version", sa.String(50), nullable=False),
            sa.Column("metadata", postgresql.JSONB, server_default="{}"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.UniqueConstraint("user_id", "consent_type", name="uq_user_consent_type"),
        )
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_consents_active
            ON user_consents (user_id, consent_type)
            WHERE status = 'granted'
        """)

    if not table_exists("data_processing_requests"):
        op.create_table(
            "data_processing_requests",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column("request_type", sa.String(50), nullable=False, index=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending", index=True),
            sa.Column("requester_email", sa.String(255), nullable=False),
            sa.Column("verification_token", sa.String(64), nullable=False),
            sa.Column("verified", sa.Boolean(), server_default="false"),
            sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
            sa.Column("processed_at", sa.DateTime(timezone=True)),
            sa.Column("result_url", sa.Text()),
            sa.Column("notes", sa.Text()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        )

    if not table_exists("compliance_audit_logs"):
        op.create_table(
            "compliance_audit_logs",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), index=True),
            sa.Column("action", sa.String(100), nullable=False, index=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), index=True),
            sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
            sa.Column("resource_type", sa.String(100), nullable=False, index=True),
            sa.Column("resource_id", sa.String(255)),
            sa.Column("old_value", postgresql.JSONB),
            sa.Column("new_value", postgresql.JSONB),
            sa.Column("ip_address", sa.String(45)),
            sa.Column("reason", sa.Text()),
            sa.Column("tenant_id", sa.String(100), index=True),
        )
        op.create_index("ix_audit_logs_timestamp_action", "compliance_audit_logs", ["timestamp", "action"])

    if not table_exists("notification_personalization_cache"):
        op.create_table(
            "notification_personalization_cache",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column("cache_key", sa.String(255), nullable=False),
            sa.Column("personalized_data", postgresql.JSONB, nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False, index=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.UniqueConstraint("user_id", "cache_key", name="uq_user_cache_key"),
        )


def downgrade() -> None:
    """Remove tabelas de notificações inteligentes."""
    op.execute("DROP INDEX IF EXISTS ix_consents_active")
    op.execute("DROP INDEX IF EXISTS ix_experiments_active")
    op.execute("DROP INDEX IF EXISTS ix_behavior_churn_risk")
    op.drop_table("notification_personalization_cache")
    op.drop_table("compliance_audit_logs")
    op.drop_table("data_processing_requests")
    op.drop_table("user_consents")
    op.drop_table("notification_analytics")
    op.execute("DROP INDEX IF EXISTS ix_ab_events_experiment_variant")
    op.drop_table("ab_experiment_events")
    op.drop_table("ab_experiment_variants")
    op.drop_table("ab_experiments")
    op.drop_table("user_behavior_profiles")
