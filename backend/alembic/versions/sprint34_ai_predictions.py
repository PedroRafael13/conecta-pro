"""Sprint 34 - AI Predictions Tables.

Revision ID: sprint34_ai_predictions
Revises:
Create Date: 2026-01-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision = "sprint34_ai_predictions"
down_revision = None
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
    """Create AI tables."""
    # Enums
    create_enum_safe("predictiontype", ['CHURN', 'REVENUE_FORECAST', 'EXPENSE_FORECAST', 'DEMAND_FORECAST', 'LEAD_SCORING', 'CREDIT_RISK', 'ANOMALY', 'CLASSIFICATION', 'REGRESSION', 'RECOMMENDATION', 'SENTIMENT', 'CLUSTER'])

    create_enum_safe("predictionstatus", ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'EXPIRED', 'INVALIDATED'])

    create_enum_safe("modeltype", ['CLASSIFICATION', 'REGRESSION', 'CLUSTERING', 'ANOMALY_DETECTION', 'TIME_SERIES', 'RECOMMENDATION', 'NLP', 'RANKING'])

    create_enum_safe("modelstatus", ['DRAFT', 'TRAINING', 'VALIDATING', 'READY', 'DEPLOYED', 'DEPRECATED', 'FAILED', 'ARCHIVED'])

    create_enum_safe("featurestatus", ['DRAFT', 'ACTIVE', 'DEPRECATED', 'ARCHIVED'])

    create_enum_safe("featuredatatype", ['NUMERIC', 'INTEGER', 'CATEGORICAL', 'BOOLEAN', 'TEXT', 'DATE', 'DATETIME', 'ARRAY', 'EMBEDDING'])

    create_enum_safe("trainingstatus", ['QUEUED', 'PREPARING', 'TRAINING', 'VALIDATING', 'COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT'])

    create_enum_safe("anomalytype", ['OUTLIER', 'SPIKE', 'DROP', 'TREND_CHANGE', 'SEASONAL_DEVIATION', 'MISSING_DATA', 'DUPLICATE', 'PATTERN_BREAK', 'FRAUD', 'ERROR', 'OTHER'])

    create_enum_safe("anomalyseverity", ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])

    create_enum_safe("anomalystatus", ['DETECTED', 'INVESTIGATING', 'CONFIRMED', 'FALSE_POSITIVE', 'RESOLVED', 'IGNORED'])

    create_enum_safe("recommendationtype", ['PRODUCT', 'SERVICE', 'ACTION', 'CONTENT', 'UPSELL', 'CROSS_SELL', 'RETENTION', 'OPTIMIZATION', 'ALERT', 'INSIGHT', 'NEXT_BEST_ACTION'])

    create_enum_safe("recommendationstatus", ['PENDING', 'SHOWN', 'CLICKED', 'ACCEPTED', 'REJECTED', 'EXPIRED', 'CONVERTED'])

    # ML Models table
    op.create_table(
        "ai_ml_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("slug", sa.String(100), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.String(50), nullable=False, default="1.0.0"),
        sa.Column("model_type", postgresql.ENUM("CLASSIFICATION", "REGRESSION", "CLUSTERING", "ANOMALY_DETECTION", "TIME_SERIES", "RECOMMENDATION", "NLP", "RANKING", name="modeltype", create_type=False), nullable=False, index=True),
        sa.Column("status", postgresql.ENUM("DRAFT", "TRAINING", "VALIDATING", "READY", "DEPLOYED", "DEPRECATED", "FAILED", "ARCHIVED", name="modelstatus", create_type=False), nullable=False, default="DRAFT", index=True),
        sa.Column("algorithm", sa.String(100), nullable=False),
        sa.Column("framework", sa.String(50), nullable=True),
        sa.Column("library_version", sa.String(50), nullable=True),
        sa.Column("hyperparameters", postgresql.JSONB, nullable=True),
        sa.Column("feature_store_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("input_features", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("target_variable", sa.String(100), nullable=True),
        sa.Column("feature_preprocessing", postgresql.JSONB, nullable=True),
        sa.Column("model_path", sa.String(500), nullable=True),
        sa.Column("model_size_bytes", sa.Integer, nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column("training_metrics", postgresql.JSONB, nullable=True),
        sa.Column("validation_metrics", postgresql.JSONB, nullable=True),
        sa.Column("production_metrics", postgresql.JSONB, nullable=True),
        sa.Column("training_dataset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("training_samples", sa.Integer, nullable=True),
        sa.Column("validation_samples", sa.Integer, nullable=True),
        sa.Column("test_samples", sa.Integer, nullable=True),
        sa.Column("prediction_threshold", sa.Float, default=0.5, nullable=True),
        sa.Column("confidence_threshold", sa.Float, default=0.7, nullable=True),
        sa.Column("total_predictions", sa.Integer, default=0, nullable=False),
        sa.Column("successful_predictions", sa.Integer, default=0, nullable=False),
        sa.Column("failed_predictions", sa.Integer, default=0, nullable=False),
        sa.Column("avg_prediction_time_ms", sa.Integer, nullable=True),
        sa.Column("last_drift_check", sa.DateTime(timezone=True), nullable=True),
        sa.Column("drift_score", sa.Float, nullable=True),
        sa.Column("drift_detected", sa.Boolean, default=False, nullable=False),
        sa.Column("retrain_scheduled", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_default", sa.Boolean, default=False, nullable=False),
        sa.Column("auto_retrain", sa.Boolean, default=False, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Predictions table
    op.create_table(
        "ai_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_ml_models.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("prediction_type", postgresql.ENUM("CHURN", "REVENUE_FORECAST", "EXPENSE_FORECAST", "DEMAND_FORECAST", "LEAD_SCORING", "CREDIT_RISK", "ANOMALY", "CLASSIFICATION", "REGRESSION", "RECOMMENDATION", "SENTIMENT", "CLUSTER", name="predictiontype", create_type=False), nullable=False, index=True),
        sa.Column("status", postgresql.ENUM("PENDING", "PROCESSING", "COMPLETED", "FAILED", "EXPIRED", "INVALIDATED", name="predictionstatus", create_type=False), nullable=False, default="PENDING", index=True),
        sa.Column("entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("prediction_value", sa.Float, nullable=True),
        sa.Column("prediction_label", sa.String(100), nullable=True),
        sa.Column("prediction_probabilities", postgresql.JSONB, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("features_used", postgresql.JSONB, nullable=True),
        sa.Column("feature_importance", postgresql.JSONB, nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("shap_values", postgresql.JSONB, nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("algorithm", sa.String(100), nullable=True),
        sa.Column("threshold_used", sa.Float, nullable=True),
        sa.Column("scenarios", postgresql.JSONB, nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_value", sa.Float, nullable=True),
        sa.Column("actual_label", sa.String(100), nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("feedback_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("feedback_notes", sa.Text, nullable=True),
        sa.Column("absolute_error", sa.Float, nullable=True),
        sa.Column("percentage_error", sa.Float, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=True),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_batch", sa.Boolean, default=False, nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Feature Stores table
    op.create_table(
        "ai_feature_stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("slug", sa.String(100), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.String(50), nullable=False, default="1.0.0"),
        sa.Column("status", postgresql.ENUM("DRAFT", "ACTIVE", "DEPRECATED", "ARCHIVED", name="featurestatus", create_type=False), nullable=False, default="DRAFT", index=True),
        sa.Column("entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("data_source", sa.String(200), nullable=True),
        sa.Column("source_query", sa.Text, nullable=True),
        sa.Column("source_config", postgresql.JSONB, nullable=True),
        sa.Column("refresh_frequency", sa.String(50), nullable=True),
        sa.Column("last_refresh_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_refresh_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refresh_status", sa.String(50), nullable=True),
        sa.Column("total_features", sa.Integer, default=0, nullable=False),
        sa.Column("total_entities", sa.Integer, default=0, nullable=False),
        sa.Column("storage_size_bytes", sa.Integer, nullable=True),
        sa.Column("data_quality_score", sa.Float, nullable=True),
        sa.Column("completeness_score", sa.Float, nullable=True),
        sa.Column("freshness_score", sa.Float, nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_online", sa.Boolean, default=False, nullable=False),
        sa.Column("is_cached", sa.Boolean, default=True, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Features table
    op.create_table(
        "ai_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("feature_store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_feature_stores.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("slug", sa.String(100), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("data_type", postgresql.ENUM("NUMERIC", "INTEGER", "CATEGORICAL", "BOOLEAN", "TEXT", "DATE", "DATETIME", "ARRAY", "EMBEDDING", name="featuredatatype", create_type=False), nullable=False),
        sa.Column("status", postgresql.ENUM("DRAFT", "ACTIVE", "DEPRECATED", "ARCHIVED", name="featurestatus", create_type=False), nullable=False, default="ACTIVE"),
        sa.Column("source_column", sa.String(200), nullable=True),
        sa.Column("transformation", sa.Text, nullable=True),
        sa.Column("transformation_config", postgresql.JSONB, nullable=True),
        sa.Column("statistics", postgresql.JSONB, nullable=True),
        sa.Column("validation_rules", postgresql.JSONB, nullable=True),
        sa.Column("importance_score", sa.Float, nullable=True),
        sa.Column("correlation_target", sa.Float, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("sensitivity", sa.String(50), nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_computed", sa.Boolean, default=False, nullable=False),
        sa.Column("is_derived", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Training Jobs table
    op.create_table(
        "ai_training_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_ml_models.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", postgresql.ENUM("QUEUED", "PREPARING", "TRAINING", "VALIDATING", "COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", name="trainingstatus", create_type=False), nullable=False, default="QUEUED", index=True),
        sa.Column("config", postgresql.JSONB, nullable=True),
        sa.Column("hyperparameters", postgresql.JSONB, nullable=True),
        sa.Column("feature_store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("training_data_path", sa.String(500), nullable=True),
        sa.Column("training_samples", sa.Integer, nullable=True),
        sa.Column("validation_split", sa.Float, default=0.2, nullable=True),
        sa.Column("test_split", sa.Float, default=0.1, nullable=True),
        sa.Column("cv_folds", sa.Integer, nullable=True),
        sa.Column("cv_results", postgresql.JSONB, nullable=True),
        sa.Column("current_epoch", sa.Integer, nullable=True),
        sa.Column("total_epochs", sa.Integer, nullable=True),
        sa.Column("progress_percent", sa.Float, default=0, nullable=False),
        sa.Column("training_loss", sa.Float, nullable=True),
        sa.Column("validation_loss", sa.Float, nullable=True),
        sa.Column("training_history", postgresql.JSONB, nullable=True),
        sa.Column("final_metrics", postgresql.JSONB, nullable=True),
        sa.Column("output_model_path", sa.String(500), nullable=True),
        sa.Column("output_model_size", sa.Integer, nullable=True),
        sa.Column("artifacts_path", sa.String(500), nullable=True),
        sa.Column("compute_type", sa.String(50), nullable=True),
        sa.Column("worker_count", sa.Integer, default=1, nullable=True),
        sa.Column("memory_limit_gb", sa.Float, nullable=True),
        sa.Column("gpu_memory_limit_gb", sa.Float, nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("timeout_seconds", sa.Integer, default=3600, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_traceback", sa.Text, nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_scheduled", sa.Boolean, default=False, nullable=False),
        sa.Column("is_auto_retrain", sa.Boolean, default=False, nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cron_expression", sa.String(100), nullable=True),
        sa.Column("retry_count", sa.Integer, default=0, nullable=False),
        sa.Column("max_retries", sa.Integer, default=3, nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cancelled_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Prediction Logs table
    op.create_table(
        "ai_prediction_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_predictions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("request_id", sa.String(100), nullable=True, index=True),
        sa.Column("request_source", sa.String(100), nullable=True),
        sa.Column("request_ip", sa.String(45), nullable=True),
        sa.Column("request_user_agent", sa.String(500), nullable=True),
        sa.Column("input_features", postgresql.JSONB, nullable=True),
        sa.Column("input_raw", postgresql.JSONB, nullable=True),
        sa.Column("preprocessing_steps", postgresql.JSONB, nullable=True),
        sa.Column("output_raw", postgresql.JSONB, nullable=True),
        sa.Column("output_processed", postgresql.JSONB, nullable=True),
        sa.Column("probabilities", postgresql.JSONB, nullable=True),
        sa.Column("preprocessing_time_ms", sa.Integer, nullable=True),
        sa.Column("inference_time_ms", sa.Integer, nullable=True),
        sa.Column("postprocessing_time_ms", sa.Integer, nullable=True),
        sa.Column("total_time_ms", sa.Integer, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("uncertainty_score", sa.Float, nullable=True),
        sa.Column("feature_importance", postgresql.JSONB, nullable=True),
        sa.Column("shap_values", postgresql.JSONB, nullable=True),
        sa.Column("lime_explanation", postgresql.JSONB, nullable=True),
        sa.Column("cache_hit", sa.String(20), nullable=True),
        sa.Column("cache_key", sa.String(200), nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Anomaly Logs table
    op.create_table(
        "ai_anomaly_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("anomaly_type", postgresql.ENUM("OUTLIER", "SPIKE", "DROP", "TREND_CHANGE", "SEASONAL_DEVIATION", "MISSING_DATA", "DUPLICATE", "PATTERN_BREAK", "FRAUD", "ERROR", "OTHER", name="anomalytype", create_type=False), nullable=False, index=True),
        sa.Column("severity", postgresql.ENUM("LOW", "MEDIUM", "HIGH", "CRITICAL", name="anomalyseverity", create_type=False), nullable=False, default="MEDIUM", index=True),
        sa.Column("status", postgresql.ENUM("DETECTED", "INVESTIGATING", "CONFIRMED", "FALSE_POSITIVE", "RESOLVED", "IGNORED", name="anomalystatus", create_type=False), nullable=False, default="DETECTED", index=True),
        sa.Column("entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("entity_field", sa.String(100), nullable=True),
        sa.Column("detector_name", sa.String(100), nullable=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("observed_value", sa.Float, nullable=True),
        sa.Column("expected_value", sa.Float, nullable=True),
        sa.Column("expected_range_min", sa.Float, nullable=True),
        sa.Column("expected_range_max", sa.Float, nullable=True),
        sa.Column("anomaly_score", sa.Float, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("deviation_score", sa.Float, nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("data_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("context_data", postgresql.JSONB, nullable=True),
        sa.Column("contributing_factors", postgresql.JSONB, nullable=True),
        sa.Column("impact_score", sa.Float, nullable=True),
        sa.Column("affected_entities_count", sa.Integer, nullable=True),
        sa.Column("estimated_impact_value", sa.Float, nullable=True),
        sa.Column("recommended_actions", postgresql.JSONB, nullable=True),
        sa.Column("actions_taken", postgresql.JSONB, nullable=True),
        sa.Column("resolution", sa.Text, nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("alert_sent", sa.Boolean, default=False, nullable=False),
        sa.Column("alert_channels", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("alert_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_recurring", sa.Boolean, default=False, nullable=False),
        sa.Column("recurrence_count", sa.Integer, default=0, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Recommendations table
    op.create_table(
        "ai_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("recommendation_type", postgresql.ENUM("PRODUCT", "SERVICE", "ACTION", "CONTENT", "UPSELL", "CROSS_SELL", "RETENTION", "OPTIMIZATION", "ALERT", "INSIGHT", "NEXT_BEST_ACTION", name="recommendationtype", create_type=False), nullable=False, index=True),
        sa.Column("status", postgresql.ENUM("PENDING", "SHOWN", "CLICKED", "ACCEPTED", "REJECTED", "EXPIRED", "CONVERTED", name="recommendationstatus", create_type=False), nullable=False, default="PENDING", index=True),
        sa.Column("target_entity_type", sa.String(100), nullable=False, index=True),
        sa.Column("target_entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("recommended_entity_type", sa.String(100), nullable=True),
        sa.Column("recommended_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recommended_entity_name", sa.String(300), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("action_text", sa.String(100), nullable=True),
        sa.Column("action_url", sa.String(500), nullable=True),
        sa.Column("relevance_score", sa.Float, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=True),
        sa.Column("priority_score", sa.Float, nullable=True),
        sa.Column("expected_value", sa.Float, nullable=True),
        sa.Column("rank_position", sa.Integer, nullable=True),
        sa.Column("total_recommendations", sa.Integer, nullable=True),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("algorithm", sa.String(100), nullable=True),
        sa.Column("context", postgresql.JSONB, nullable=True),
        sa.Column("user_features", postgresql.JSONB, nullable=True),
        sa.Column("item_features", postgresql.JSONB, nullable=True),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("similar_users_count", sa.Integer, nullable=True),
        sa.Column("feature_importance", postgresql.JSONB, nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("shown_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("clicked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("action_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("feedback", sa.String(50), nullable=True),
        sa.Column("feedback_text", sa.Text, nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted", sa.Boolean, default=False, nullable=False),
        sa.Column("conversion_value", sa.Float, nullable=True),
        sa.Column("conversion_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("conversion_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("variant", sa.String(50), nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_personalized", sa.Boolean, default=True, nullable=False),
        sa.Column("is_realtime", sa.Boolean, default=False, nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Indexes
    op.create_index("ix_ai_predictions_entity", "ai_predictions", ["entity_type", "entity_id"])
    op.create_index("ix_ai_predictions_created", "ai_predictions", ["created_at"])
    op.create_index("ix_ai_anomaly_logs_detected", "ai_anomaly_logs", ["detected_at"])
    op.create_index("ix_ai_recommendations_target", "ai_recommendations", ["target_entity_type", "target_entity_id"])


def downgrade() -> None:
    """Drop AI tables."""
    op.drop_table("ai_recommendations")
    op.drop_table("ai_anomaly_logs")
    op.drop_table("ai_prediction_logs")
    op.drop_table("ai_training_jobs")
    op.drop_table("ai_features")
    op.drop_table("ai_feature_stores")
    op.drop_table("ai_predictions")
    op.drop_table("ai_ml_models")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS recommendationstatus")
    op.execute("DROP TYPE IF EXISTS recommendationtype")
    op.execute("DROP TYPE IF EXISTS anomalystatus")
    op.execute("DROP TYPE IF EXISTS anomalyseverity")
    op.execute("DROP TYPE IF EXISTS anomalytype")
    op.execute("DROP TYPE IF EXISTS trainingstatus")
    op.execute("DROP TYPE IF EXISTS featuredatatype")
    op.execute("DROP TYPE IF EXISTS featurestatus")
    op.execute("DROP TYPE IF EXISTS modelstatus")
    op.execute("DROP TYPE IF EXISTS modeltype")
    op.execute("DROP TYPE IF EXISTS predictionstatus")
    op.execute("DROP TYPE IF EXISTS predictiontype")
