"""Sprint 04 - Create Predictive Analytics Tables.

Revision ID: sprint04_analytics
Revises: sprint03_notifications
Create Date: 2025-01-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers
revision = "sprint04_analytics"
down_revision = "sprint03_intelligent"
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Create predictive analytics tables."""

    if not table_exists("ml_models"):
        op.create_table(
            "ml_models",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("version", sa.String(50), nullable=False),
            sa.Column("model_type", sa.String(50), nullable=False),
            sa.Column("framework", sa.String(50), nullable=False),
            sa.Column("stage", sa.String(20), nullable=False, default="development"),
            sa.Column("description", sa.Text),
            sa.Column("model_path", sa.String(500)),
            sa.Column("model_hash", sa.String(64)),
            sa.Column("artifact_uri", sa.String(500)),
            sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("metrics", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("hyperparameters", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("feature_names", postgresql.ARRAY(sa.String(100))),
            sa.Column("target_column", sa.String(100)),
            sa.Column("author", sa.String(100)),
            sa.Column("is_active", sa.Boolean, default=True),
            sa.Column("promoted_at", sa.DateTime(timezone=True)),
            sa.Column("promoted_by", sa.String(100)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
            sa.UniqueConstraint("name", "version", name="uq_model_name_version"),
        )
        op.create_index("ix_ml_models_name", "ml_models", ["name"])
        op.create_index("ix_ml_models_stage", "ml_models", ["stage"])

    if not table_exists("ml_experiments"):
        op.create_table(
            "ml_experiments",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("model_name", sa.String(100), nullable=False),
            sa.Column("description", sa.Text),
            sa.Column("status", sa.String(20), nullable=False, default="running"),
            sa.Column("parameters", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("metrics", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("artifacts", postgresql.ARRAY(sa.String(500))),
            sa.Column("tags", postgresql.ARRAY(sa.String(50))),
            sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
            sa.Column("end_time", sa.DateTime(timezone=True)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not table_exists("churn_predictions"):
        op.create_table(
            "churn_predictions",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("churn_probability", sa.Float, nullable=False),
            sa.Column("risk_level", sa.String(20), nullable=False),
            sa.Column("confidence", sa.Float, nullable=False),
            sa.Column("contributing_factors", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("retention_actions", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("predicted_churn_date", sa.DateTime(timezone=True)),
            sa.Column("lifetime_value_at_risk", sa.Float, default=0),
            sa.Column("model_version", sa.String(50)),
            sa.Column("is_current", sa.Boolean, default=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_churn_predictions_user_id", "churn_predictions", ["user_id"])
        op.create_index("ix_churn_predictions_risk_level", "churn_predictions", ["risk_level"])

    if not table_exists("sales_forecasts"):
        op.create_table(
            "sales_forecasts",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("forecast_type", sa.String(50), nullable=False),
            sa.Column("granularity", sa.String(20), nullable=False),
            sa.Column("entity_type", sa.String(50)),
            sa.Column("entity_id", sa.String(100)),
            sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
            sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
            sa.Column("predictions", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("total_forecast", sa.Float),
            sa.Column("trend_info", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("seasonality_info", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("accuracy_metrics", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("insights", postgresql.ARRAY(sa.Text)),
            sa.Column("model_version", sa.String(50)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not table_exists("fraud_alerts"):
        op.create_table(
            "fraud_alerts",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("transaction_id", sa.String(100)),
            sa.Column("user_id", postgresql.UUID(as_uuid=True)),
            sa.Column("fraud_type", sa.String(50), nullable=False),
            sa.Column("risk_level", sa.String(20), nullable=False),
            sa.Column("risk_score", sa.Float, nullable=False),
            sa.Column("confidence", sa.Float, nullable=False),
            sa.Column("status", sa.String(20), nullable=False, default="open"),
            sa.Column("indicators", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("rule_violations", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("recommended_actions", postgresql.ARRAY(sa.Text)),
            sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("acknowledged_by", sa.String(100)),
            sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
            sa.Column("resolution_notes", sa.Text),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        )
        op.create_index("ix_fraud_alerts_user_id", "fraud_alerts", ["user_id"])
        op.create_index("ix_fraud_alerts_status", "fraud_alerts", ["status"])
        op.create_index("ix_fraud_alerts_risk_level", "fraud_alerts", ["risk_level"])

    if not table_exists("lead_scores"):
        op.create_table(
            "lead_scores",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("lead_id", sa.String(100), nullable=False),
            sa.Column("total_score", sa.Float, nullable=False),
            sa.Column("quality", sa.String(20), nullable=False),
            sa.Column("conversion_probability", sa.Float, nullable=False),
            sa.Column("conversion_level", sa.String(20)),
            sa.Column("stage", sa.String(50)),
            sa.Column("factors", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("insights", postgresql.JSONB, server_default=sa.text("'[]'::jsonb")),
            sa.Column("next_best_action", sa.Text),
            sa.Column("estimated_value", sa.Float, default=0),
            sa.Column("time_to_conversion", sa.Integer),
            sa.Column("model_version", sa.String(50)),
            sa.Column("is_current", sa.Boolean, default=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_lead_scores_lead_id", "lead_scores", ["lead_id"])
        op.create_index("ix_lead_scores_quality", "lead_scores", ["quality"])

    if not table_exists("model_performance_metrics"):
        op.create_table(
            "model_performance_metrics",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("model_name", sa.String(100), nullable=False),
            sa.Column("model_version", sa.String(50), nullable=False),
            sa.Column("metric_name", sa.String(50), nullable=False),
            sa.Column("metric_value", sa.Float, nullable=False),
            sa.Column("baseline_value", sa.Float),
            sa.Column("threshold_warning", sa.Float),
            sa.Column("threshold_critical", sa.Float),
            sa.Column("is_healthy", sa.Boolean, default=True),
            sa.Column("trend", sa.String(20)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_model_metrics_name_version", "model_performance_metrics", ["model_name", "model_version"])

    if not table_exists("drift_alerts"):
        op.create_table(
            "drift_alerts",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("model_name", sa.String(100), nullable=False),
            sa.Column("drift_type", sa.String(50), nullable=False),
            sa.Column("severity", sa.String(20), nullable=False),
            sa.Column("feature_name", sa.String(100)),
            sa.Column("drift_score", sa.Float, nullable=False),
            sa.Column("baseline_distribution", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("current_distribution", postgresql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("description", sa.Text),
            sa.Column("recommended_action", sa.Text),
            sa.Column("acknowledged", sa.Boolean, default=False),
            sa.Column("acknowledged_by", sa.String(100)),
            sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_drift_alerts_model", "drift_alerts", ["model_name"])
        op.create_index("ix_drift_alerts_acknowledged", "drift_alerts", ["acknowledged"])

    if not table_exists("feature_store_cache"):
        op.create_table(
            "feature_store_cache",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("entity_type", sa.String(50), nullable=False),
            sa.Column("entity_id", sa.Integer, nullable=False),
            sa.Column("feature_name", sa.String(100), nullable=False),
            sa.Column("feature_value", postgresql.JSONB),
            sa.Column("version", sa.String(20)),
            sa.Column("expires_at", sa.DateTime(timezone=True)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
            sa.UniqueConstraint("entity_type", "entity_id", "feature_name", name="uq_feature_cache"),
        )
        op.create_index("ix_feature_cache_entity", "feature_store_cache", ["entity_type", "entity_id"])

    if not table_exists("prediction_logs"):
        op.create_table(
            "prediction_logs",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("model_name", sa.String(100), nullable=False),
            sa.Column("model_version", sa.String(50)),
            sa.Column("request_id", sa.String(100)),
            sa.Column("entity_type", sa.String(50)),
            sa.Column("entity_id", sa.String(100)),
            sa.Column("input_features", postgresql.JSONB),
            sa.Column("prediction", postgresql.JSONB),
            sa.Column("latency_ms", sa.Float),
            sa.Column("success", sa.Boolean, default=True),
            sa.Column("error_message", sa.Text),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_prediction_logs_model", "prediction_logs", ["model_name"])
        op.create_index("ix_prediction_logs_created", "prediction_logs", ["created_at"])


def downgrade() -> None:
    """Drop predictive analytics tables."""
    op.drop_table("prediction_logs")
    op.drop_table("feature_store_cache")
    op.drop_table("drift_alerts")
    op.drop_table("model_performance_metrics")
    op.drop_table("lead_scores")
    op.drop_table("fraud_alerts")
    op.drop_table("sales_forecasts")
    op.drop_table("churn_predictions")
    op.drop_table("ml_experiments")
    op.drop_table("ml_models")
