"""Sprint 46: Create Sentiment Analysis Tables

Revision ID: sprint46_sentiment
Revises: sprint45_fraud
Create Date: 2025-01-05

Tabelas para analise de sentimento com NLP:
- sentiment_analyses: Analises de sentimento
- sentiment_rules: Regras de classificacao e alerta
- sentiment_trends: Tendencias de sentimento
- feedback_insights: Insights e recomendacoes
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "sprint46_sentiment"
down_revision = "sprint45_fraud_detection"
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
    # ============================================================
    # Criar Enums (safe)
    # ============================================================
    create_enum_safe("sentiment_type", ["very_positive", "positive", "neutral", "negative", "very_negative", "mixed"])

    create_enum_safe(
        "emotion_type",
        [
            "joy",
            "satisfaction",
            "gratitude",
            "trust",
            "anticipation",
            "surprise",
            "neutral",
            "concern",
            "frustration",
            "disappointment",
            "anger",
            "fear",
            "sadness",
            "disgust",
            "urgency",
        ],
    )

    create_enum_safe(
        "source_type",
        [
            "ticket",
            "email",
            "chat",
            "review",
            "survey",
            "social_media",
            "call_transcript",
            "feedback_form",
            "complaint",
            "suggestion",
            "comment",
            "nps_response",
            "whatsapp",
            "other",
        ],
    )

    create_enum_safe("analysis_status", ["pending", "processing", "completed", "failed", "requires_review"])

    create_enum_safe("trend_period", ["hourly", "daily", "weekly", "monthly", "quarterly", "yearly"])

    create_enum_safe("trend_direction", ["improving", "stable", "declining", "volatile"])

    create_enum_safe(
        "trend_category",
        ["overall", "by_source", "by_customer", "by_segment", "by_product", "by_service", "by_topic", "by_aspect"],
    )

    create_enum_safe(
        "insight_type",
        [
            "sentiment_drop",
            "sentiment_spike",
            "sentiment_anomaly",
            "emerging_topic",
            "trending_topic",
            "recurring_issue",
            "churn_risk",
            "customer_champion",
            "customer_recovery",
            "service_issue",
            "product_issue",
            "process_bottleneck",
            "upsell_opportunity",
            "improvement_suggestion",
            "feature_request",
            "benchmark_deviation",
            "competitor_mention",
            "urgent_attention",
            "compliance_risk",
            "success_story",
            "team_recognition",
        ],
    )

    create_enum_safe("insight_priority", ["critical", "high", "medium", "low", "info"])

    create_enum_safe("insight_status", ["new", "acknowledged", "in_progress", "implemented", "dismissed", "expired"])

    create_enum_safe(
        "rule_category",
        [
            "sentiment",
            "emotion",
            "keyword",
            "aspect",
            "urgency",
            "churn",
            "escalation",
            "notification",
            "classification",
            "custom",
        ],
    )

    create_enum_safe(
        "rule_action",
        [
            "alert",
            "escalate",
            "notify_email",
            "notify_sms",
            "notify_slack",
            "create_ticket",
            "assign_agent",
            "tag",
            "priority_boost",
            "auto_respond",
            "trigger_workflow",
            "log",
        ],
    )

    # ============================================================
    # Tabela: sentiment_analyses
    # ============================================================
    op.create_table(
        "sentiment_analyses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Texto analisado
        sa.Column("original_text", sa.Text, nullable=False),
        sa.Column("normalized_text", sa.Text),
        sa.Column("language", sa.String(10), server_default="pt"),
        sa.Column("word_count", sa.Integer),
        sa.Column("char_count", sa.Integer),
        # Fonte
        sa.Column(
            "source_type",
            ENUM(
                "ticket",
                "email",
                "chat",
                "review",
                "survey",
                "social_media",
                "call_transcript",
                "feedback_form",
                "complaint",
                "suggestion",
                "comment",
                "nps_response",
                "whatsapp",
                "other",
                name="source_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("source_id", UUID(as_uuid=True)),
        sa.Column("source_reference", sa.String(255)),
        # Entidade relacionada
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("entity_name", sa.String(255)),
        # Cliente
        sa.Column("customer_id", UUID(as_uuid=True)),
        sa.Column("customer_name", sa.String(255)),
        sa.Column("customer_segment", sa.String(100)),
        # Resultado do sentimento
        sa.Column(
            "sentiment_type",
            ENUM(
                "very_positive",
                "positive",
                "neutral",
                "negative",
                "very_negative",
                "mixed",
                name="sentiment_type",
                create_type=False,
            ),
            server_default="neutral",
        ),
        sa.Column("sentiment_score", sa.Float, server_default="0"),
        sa.Column("confidence_score", sa.Float, server_default="0"),
        # Polaridade detalhada
        sa.Column("positive_score", sa.Float, server_default="0"),
        sa.Column("negative_score", sa.Float, server_default="0"),
        sa.Column("neutral_score", sa.Float, server_default="0"),
        # Emocoes detectadas
        sa.Column(
            "primary_emotion",
            ENUM(
                "joy",
                "satisfaction",
                "gratitude",
                "trust",
                "anticipation",
                "surprise",
                "neutral",
                "concern",
                "frustration",
                "disappointment",
                "anger",
                "fear",
                "sadness",
                "disgust",
                "urgency",
                name="emotion_type",
                create_type=False,
            ),
        ),
        sa.Column(
            "secondary_emotion",
            ENUM(
                "joy",
                "satisfaction",
                "gratitude",
                "trust",
                "anticipation",
                "surprise",
                "neutral",
                "concern",
                "frustration",
                "disappointment",
                "anger",
                "fear",
                "sadness",
                "disgust",
                "urgency",
                name="emotion_type",
                create_type=False,
            ),
        ),
        sa.Column("emotion_scores", JSONB, server_default="{}"),
        # Aspectos e keywords
        sa.Column("aspects", JSONB, server_default="[]"),
        sa.Column("topics", JSONB, server_default="[]"),
        sa.Column("keywords", JSONB, server_default="[]"),
        # Entidades extraidas
        sa.Column("entities_mentioned", JSONB, server_default="[]"),
        sa.Column("products_mentioned", JSONB, server_default="[]"),
        sa.Column("services_mentioned", JSONB, server_default="[]"),
        # Indicadores especiais
        sa.Column("has_urgency", sa.Boolean, server_default="false"),
        sa.Column("urgency_level", sa.Integer, server_default="0"),
        sa.Column("has_complaint", sa.Boolean, server_default="false"),
        sa.Column("has_praise", sa.Boolean, server_default="false"),
        sa.Column("has_question", sa.Boolean, server_default="false"),
        sa.Column("has_suggestion", sa.Boolean, server_default="false"),
        sa.Column("has_intent_to_leave", sa.Boolean, server_default="false"),
        sa.Column("requires_action", sa.Boolean, server_default="false"),
        # Frases importantes
        sa.Column("key_phrases", JSONB, server_default="[]"),
        sa.Column("negative_phrases", JSONB, server_default="[]"),
        sa.Column("positive_phrases", JSONB, server_default="[]"),
        # NPS
        sa.Column("nps_score", sa.Integer),
        sa.Column("nps_category", sa.String(20)),
        # Comparacao historico
        sa.Column("sentiment_change", sa.Float, server_default="0"),
        sa.Column("is_sentiment_improving", sa.Boolean),
        # Status e processamento
        sa.Column(
            "status",
            ENUM(
                "pending",
                "processing",
                "completed",
                "failed",
                "requires_review",
                name="analysis_status",
                create_type=False,
            ),
            server_default="pending",
        ),
        sa.Column("processing_time_ms", sa.Integer),
        sa.Column("model_version", sa.String(50)),
        sa.Column("error_message", sa.Text),
        # Revisao humana
        sa.Column("is_reviewed", sa.Boolean, server_default="false"),
        sa.Column("reviewed_by", UUID(as_uuid=True)),
        sa.Column("reviewed_at", sa.DateTime),
        sa.Column("review_notes", sa.Text),
        sa.Column(
            "corrected_sentiment",
            ENUM(
                "very_positive",
                "positive",
                "neutral",
                "negative",
                "very_negative",
                "mixed",
                name="sentiment_type",
                create_type=False,
            ),
        ),
        # Regras acionadas
        sa.Column("triggered_rules", JSONB, server_default="[]"),
        sa.Column("alert_generated", sa.Boolean, server_default="false"),
        sa.Column("alert_id", UUID(as_uuid=True)),
        # Metadados
        sa.Column("metadata", JSONB, server_default="{}"),
        sa.Column("tags", JSONB, server_default="[]"),
        # Timestamps
        sa.Column("analyzed_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # Indices para sentiment_analyses
    op.create_index("ix_sentiment_analyses_customer_id", "sentiment_analyses", ["customer_id"])
    op.create_index("ix_sentiment_analyses_source_type", "sentiment_analyses", ["source_type"])
    op.create_index("ix_sentiment_analyses_sentiment_type", "sentiment_analyses", ["sentiment_type"])
    op.create_index("ix_sentiment_analyses_status", "sentiment_analyses", ["status"])
    op.create_index("ix_sentiment_analyses_created_at", "sentiment_analyses", ["created_at"])
    op.create_index("ix_sentiment_analyses_entity", "sentiment_analyses", ["entity_type", "entity_id"])
    op.create_index("ix_sentiment_analyses_has_urgency", "sentiment_analyses", ["has_urgency"])
    op.create_index("ix_sentiment_analyses_requires_action", "sentiment_analyses", ["requires_action"])

    # ============================================================
    # Tabela: sentiment_rules
    # ============================================================
    op.create_table(
        "sentiment_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        # Categoria
        sa.Column(
            "category",
            ENUM(
                "sentiment",
                "emotion",
                "keyword",
                "aspect",
                "urgency",
                "churn",
                "escalation",
                "notification",
                "classification",
                "custom",
                name="rule_category",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("subcategory", sa.String(100)),
        # Prioridade
        sa.Column("priority", sa.Integer, server_default="50"),
        sa.Column("weight", sa.Float, server_default="1.0"),
        # Condicoes
        sa.Column("conditions", JSONB, server_default="[]"),
        sa.Column("sentiment_threshold", sa.Float),
        sa.Column("sentiment_types", JSONB, server_default="[]"),
        sa.Column("emotion_types", JSONB, server_default="[]"),
        sa.Column("emotion_threshold", sa.Float),
        # Keywords
        sa.Column("keywords_include", JSONB, server_default="[]"),
        sa.Column("keywords_exclude", JSONB, server_default="[]"),
        sa.Column("keywords_match_all", sa.Boolean, server_default="false"),
        # Aspectos
        sa.Column("aspects_include", JSONB, server_default="[]"),
        sa.Column("aspects_sentiment", sa.String(20)),
        # Fontes
        sa.Column("source_types", JSONB, server_default="[]"),
        sa.Column("exclude_sources", JSONB, server_default="[]"),
        # Clientes
        sa.Column("customer_segments", JSONB, server_default="[]"),
        sa.Column("customer_tiers", JSONB, server_default="[]"),
        # Acoes
        sa.Column(
            "primary_action",
            ENUM(
                "alert",
                "escalate",
                "notify_email",
                "notify_sms",
                "notify_slack",
                "create_ticket",
                "assign_agent",
                "tag",
                "priority_boost",
                "auto_respond",
                "trigger_workflow",
                "log",
                name="rule_action",
                create_type=False,
            ),
            server_default="alert",
        ),
        sa.Column("secondary_actions", JSONB, server_default="[]"),
        sa.Column("action_config", JSONB, server_default="{}"),
        # Notificacoes
        sa.Column("notify_channels", JSONB, server_default="[]"),
        sa.Column("notify_recipients", JSONB, server_default="[]"),
        sa.Column("notify_template", sa.String(100)),
        # Cooldown
        sa.Column("cooldown_minutes", sa.Integer, server_default="60"),
        sa.Column("cooldown_per_customer", sa.Boolean, server_default="true"),
        sa.Column("max_triggers_per_day", sa.Integer),
        # Horarios
        sa.Column("active_hours_start", sa.Integer),
        sa.Column("active_hours_end", sa.Integer),
        sa.Column("active_days", JSONB, server_default="[]"),
        # Estatisticas
        sa.Column("total_triggers", sa.Integer, server_default="0"),
        sa.Column("total_actions", sa.Integer, server_default="0"),
        sa.Column("true_positives", sa.Integer, server_default="0"),
        sa.Column("false_positives", sa.Integer, server_default="0"),
        sa.Column("last_triggered_at", sa.DateTime),
        # Status
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_system", sa.Boolean, server_default="false"),
        sa.Column("is_test_mode", sa.Boolean, server_default="false"),
        # Audit
        sa.Column("created_by", UUID(as_uuid=True)),
        sa.Column("updated_by", UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # Indices para sentiment_rules
    op.create_index("ix_sentiment_rules_code", "sentiment_rules", ["code"])
    op.create_index("ix_sentiment_rules_category", "sentiment_rules", ["category"])
    op.create_index("ix_sentiment_rules_is_active", "sentiment_rules", ["is_active"])
    op.create_index("ix_sentiment_rules_priority", "sentiment_rules", ["priority"])

    # ============================================================
    # Tabela: sentiment_trends
    # ============================================================
    op.create_table(
        "sentiment_trends",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Periodo
        sa.Column(
            "period_type",
            ENUM("hourly", "daily", "weekly", "monthly", "quarterly", "yearly", name="trend_period", create_type=False),
            nullable=False,
        ),
        sa.Column("period_start", sa.DateTime, nullable=False),
        sa.Column("period_end", sa.DateTime, nullable=False),
        sa.Column("period_label", sa.String(50)),
        # Categoria
        sa.Column(
            "category",
            ENUM(
                "overall",
                "by_source",
                "by_customer",
                "by_segment",
                "by_product",
                "by_service",
                "by_topic",
                "by_aspect",
                name="trend_category",
                create_type=False,
            ),
            server_default="overall",
        ),
        sa.Column("category_value", sa.String(255)),
        # Entidade
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("entity_name", sa.String(255)),
        # Metricas de sentimento
        sa.Column("avg_sentiment_score", sa.Float, server_default="0"),
        sa.Column("min_sentiment_score", sa.Float),
        sa.Column("max_sentiment_score", sa.Float),
        sa.Column("std_sentiment_score", sa.Float),
        # Distribuicao
        sa.Column("very_positive_count", sa.Integer, server_default="0"),
        sa.Column("positive_count", sa.Integer, server_default="0"),
        sa.Column("neutral_count", sa.Integer, server_default="0"),
        sa.Column("negative_count", sa.Integer, server_default="0"),
        sa.Column("very_negative_count", sa.Integer, server_default="0"),
        sa.Column("mixed_count", sa.Integer, server_default="0"),
        # Percentuais
        sa.Column("very_positive_pct", sa.Float, server_default="0"),
        sa.Column("positive_pct", sa.Float, server_default="0"),
        sa.Column("neutral_pct", sa.Float, server_default="0"),
        sa.Column("negative_pct", sa.Float, server_default="0"),
        sa.Column("very_negative_pct", sa.Float, server_default="0"),
        # Total
        sa.Column("total_analyses", sa.Integer, server_default="0"),
        sa.Column("total_with_action", sa.Integer, server_default="0"),
        # Emocoes agregadas
        sa.Column("emotion_distribution", JSONB, server_default="{}"),
        sa.Column("primary_emotion", sa.String(50)),
        # Aspectos agregados
        sa.Column("aspect_sentiments", JSONB, server_default="{}"),
        sa.Column("top_positive_aspects", JSONB, server_default="[]"),
        sa.Column("top_negative_aspects", JSONB, server_default="[]"),
        # Keywords
        sa.Column("top_keywords", JSONB, server_default="[]"),
        sa.Column("trending_keywords", JSONB, server_default="[]"),
        # Topicos
        sa.Column("top_topics", JSONB, server_default="[]"),
        # NPS
        sa.Column("nps_score", sa.Float),
        sa.Column("promoters_count", sa.Integer, server_default="0"),
        sa.Column("passives_count", sa.Integer, server_default="0"),
        sa.Column("detractors_count", sa.Integer, server_default="0"),
        # Indicadores especiais
        sa.Column("complaints_count", sa.Integer, server_default="0"),
        sa.Column("complaints_rate", sa.Float, server_default="0"),
        sa.Column("urgency_count", sa.Integer, server_default="0"),
        sa.Column("churn_risk_count", sa.Integer, server_default="0"),
        # Comparacao periodo anterior
        sa.Column("prev_avg_score", sa.Float),
        sa.Column("score_change", sa.Float, server_default="0"),
        sa.Column("score_change_pct", sa.Float, server_default="0"),
        sa.Column("volume_change", sa.Integer, server_default="0"),
        sa.Column("volume_change_pct", sa.Float, server_default="0"),
        # Tendencia
        sa.Column(
            "trend_direction",
            ENUM("improving", "stable", "declining", "volatile", name="trend_direction", create_type=False),
            server_default="stable",
        ),
        sa.Column("trend_strength", sa.Float, server_default="0"),
        sa.Column("trend_confidence", sa.Float, server_default="0"),
        # Previsao
        sa.Column("predicted_next_score", sa.Float),
        sa.Column("prediction_confidence", sa.Float),
        # Alertas gerados
        sa.Column("alerts_generated", sa.Integer, server_default="0"),
        sa.Column("alert_ids", JSONB, server_default="[]"),
        # Insights
        sa.Column("insights", JSONB, server_default="[]"),
        # Timestamps
        sa.Column("calculated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # Indices para sentiment_trends
    op.create_index("ix_sentiment_trends_period", "sentiment_trends", ["period_type", "period_label"])
    op.create_index("ix_sentiment_trends_category", "sentiment_trends", ["category", "category_value"])
    op.create_index("ix_sentiment_trends_entity", "sentiment_trends", ["entity_type", "entity_id"])
    op.create_index("ix_sentiment_trends_period_start", "sentiment_trends", ["period_start"])

    # ============================================================
    # Tabela: feedback_insights
    # ============================================================
    op.create_table(
        "feedback_insights",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("insight_number", sa.String(20), unique=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text),
        # Tipo e prioridade
        sa.Column(
            "insight_type",
            ENUM(
                "sentiment_drop",
                "sentiment_spike",
                "sentiment_anomaly",
                "emerging_topic",
                "trending_topic",
                "recurring_issue",
                "churn_risk",
                "customer_champion",
                "customer_recovery",
                "service_issue",
                "product_issue",
                "process_bottleneck",
                "upsell_opportunity",
                "improvement_suggestion",
                "feature_request",
                "benchmark_deviation",
                "competitor_mention",
                "urgent_attention",
                "compliance_risk",
                "success_story",
                "team_recognition",
                name="insight_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            ENUM("critical", "high", "medium", "low", "info", name="insight_priority", create_type=False),
            server_default="medium",
        ),
        sa.Column(
            "status",
            ENUM(
                "new",
                "acknowledged",
                "in_progress",
                "implemented",
                "dismissed",
                "expired",
                name="insight_status",
                create_type=False,
            ),
            server_default="new",
        ),
        # Categoria
        sa.Column("category", sa.String(100)),
        sa.Column("subcategory", sa.String(100)),
        sa.Column("tags", JSONB, server_default="[]"),
        # Escopo
        sa.Column("scope", sa.String(50)),
        sa.Column("scope_value", sa.String(255)),
        # Entidade relacionada
        sa.Column("entity_type", sa.String(50)),
        sa.Column("entity_id", UUID(as_uuid=True)),
        sa.Column("entity_name", sa.String(255)),
        # Metricas do insight
        sa.Column("impact_score", sa.Float, server_default="0"),
        sa.Column("confidence_score", sa.Float, server_default="0"),
        sa.Column("urgency_score", sa.Float, server_default="0"),
        sa.Column("actionability_score", sa.Float, server_default="0"),
        # Dados de suporte
        sa.Column("supporting_data", JSONB, server_default="{}"),
        sa.Column("analysis_ids", JSONB, server_default="[]"),
        sa.Column("analysis_count", sa.Integer, server_default="0"),
        # Periodo de referencia
        sa.Column("period_start", sa.DateTime),
        sa.Column("period_end", sa.DateTime),
        sa.Column("detection_window_days", sa.Integer),
        # Metricas agregadas
        sa.Column("avg_sentiment", sa.Float),
        sa.Column("sentiment_change", sa.Float),
        sa.Column("volume", sa.Integer),
        sa.Column("affected_customers", sa.Integer),
        # Topicos/Keywords
        sa.Column("related_keywords", JSONB, server_default="[]"),
        sa.Column("related_topics", JSONB, server_default="[]"),
        sa.Column("related_aspects", JSONB, server_default="[]"),
        # Recomendacoes
        sa.Column("recommendations", JSONB, server_default="[]"),
        sa.Column("actions_taken", JSONB, server_default="[]"),
        sa.Column("action_results", sa.Text),
        # Benchmark
        sa.Column("benchmark_value", sa.Float),
        sa.Column("deviation_from_benchmark", sa.Float),
        # Previsao
        sa.Column("predicted_impact", sa.Text),
        sa.Column("predicted_revenue_impact", sa.Float),
        sa.Column("predicted_churn_impact", sa.Float),
        # Validade
        sa.Column("valid_until", sa.DateTime),
        sa.Column("is_recurring", sa.Boolean, server_default="false"),
        sa.Column("recurrence_pattern", sa.String(100)),
        # Notificacoes
        sa.Column("notifications_sent", sa.Integer, server_default="0"),
        sa.Column("last_notified_at", sa.DateTime),
        sa.Column("notify_recipients", JSONB, server_default="[]"),
        # Atribuicao
        sa.Column("assigned_to", UUID(as_uuid=True)),
        sa.Column("assigned_at", sa.DateTime),
        sa.Column("assigned_team", sa.String(100)),
        # Resolucao
        sa.Column("resolved_by", UUID(as_uuid=True)),
        sa.Column("resolved_at", sa.DateTime),
        sa.Column("resolution_notes", sa.Text),
        sa.Column("resolution_outcome", sa.String(50)),
        # Feedback
        sa.Column("was_useful", sa.Boolean),
        sa.Column("usefulness_rating", sa.Integer),
        sa.Column("feedback_notes", sa.Text),
        # Geracao
        sa.Column("generated_by", sa.String(50)),
        sa.Column("model_version", sa.String(50)),
        sa.Column("generation_context", JSONB, server_default="{}"),
        # Audit
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # Indices para feedback_insights
    op.create_index("ix_feedback_insights_number", "feedback_insights", ["insight_number"])
    op.create_index("ix_feedback_insights_type", "feedback_insights", ["insight_type"])
    op.create_index("ix_feedback_insights_priority", "feedback_insights", ["priority"])
    op.create_index("ix_feedback_insights_status", "feedback_insights", ["status"])
    op.create_index("ix_feedback_insights_entity", "feedback_insights", ["entity_type", "entity_id"])
    op.create_index("ix_feedback_insights_assigned_to", "feedback_insights", ["assigned_to"])
    op.create_index("ix_feedback_insights_created_at", "feedback_insights", ["created_at"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("feedback_insights")
    op.drop_table("sentiment_trends")
    op.drop_table("sentiment_rules")
    op.drop_table("sentiment_analyses")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS insight_status")
    op.execute("DROP TYPE IF EXISTS insight_priority")
    op.execute("DROP TYPE IF EXISTS insight_type")
    op.execute("DROP TYPE IF EXISTS rule_action")
    op.execute("DROP TYPE IF EXISTS rule_category")
    op.execute("DROP TYPE IF EXISTS trend_category")
    op.execute("DROP TYPE IF EXISTS trend_direction")
    op.execute("DROP TYPE IF EXISTS trend_period")
    op.execute("DROP TYPE IF EXISTS analysis_status")
    op.execute("DROP TYPE IF EXISTS source_type")
    op.execute("DROP TYPE IF EXISTS emotion_type")
    op.execute("DROP TYPE IF EXISTS sentiment_type")
