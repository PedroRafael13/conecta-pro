"""Sprint 54: Create email assistant tables.

Revision ID: sprint54_email_assistant
Revises: sprint53_knowledge_base
Create Date: 2025-01-06
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID

from alembic import op

revision = "sprint54_email_assistant"
down_revision = "sprint53_kb"
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
    # Criar ENUMs
    create_enum_safe(
        "email_status_enum", ["received", "processing", "classified", "responded", "archived", "spam", "deleted"]
    )

    create_enum_safe(
        "email_category_enum",
        [
            "support",
            "sales",
            "billing",
            "complaint",
            "information",
            "scheduling",
            "feedback",
            "newsletter",
            "spam",
            "phishing",
            "internal",
            "other",
        ],
    )

    create_enum_safe("email_priority_enum", ["critical", "high", "medium", "low", "none"])

    create_enum_safe("email_sentiment_enum", ["very_negative", "negative", "neutral", "positive", "very_positive"])

    # Tabela ai_emails
    op.create_table(
        "ai_emails",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("message_id", sa.String(500), unique=True, nullable=False),
        sa.Column("thread_id", sa.String(500), nullable=True),
        sa.Column("in_reply_to", sa.String(500), nullable=True),
        # Remetente/Destinatario
        sa.Column("from_address", sa.String(500), nullable=False),
        sa.Column("from_name", sa.String(200), nullable=True),
        sa.Column("to_addresses", ARRAY(sa.String), server_default="{}"),
        sa.Column("cc_addresses", ARRAY(sa.String), server_default="{}"),
        sa.Column("bcc_addresses", ARRAY(sa.String), server_default="{}"),
        sa.Column("reply_to", sa.String(500), nullable=True),
        # Conteudo
        sa.Column("subject", sa.String(1000), nullable=True),
        sa.Column("body_text", sa.Text, nullable=True),
        sa.Column("body_html", sa.Text, nullable=True),
        sa.Column("body_preview", sa.String(500), nullable=True),
        # Anexos
        sa.Column("has_attachments", sa.Boolean, server_default="false"),
        sa.Column("attachment_count", sa.Integer, server_default="0"),
        sa.Column("attachments", JSONB, server_default="[]"),
        # Classificacao
        sa.Column(
            "status",
            ENUM(
                "received",
                "processing",
                "classified",
                "responded",
                "archived",
                "spam",
                "deleted",
                name="email_status_enum",
                create_type=False,
            ),
            server_default="received",
            nullable=False,
        ),
        sa.Column(
            "category",
            ENUM(
                "support",
                "sales",
                "billing",
                "complaint",
                "information",
                "scheduling",
                "feedback",
                "newsletter",
                "spam",
                "phishing",
                "internal",
                "other",
                name="email_category_enum",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("category_confidence", sa.Float, server_default="0.0"),
        sa.Column("subcategory", sa.String(100), nullable=True),
        # Prioridade
        sa.Column(
            "priority",
            ENUM("critical", "high", "medium", "low", "none", name="email_priority_enum", create_type=False),
            server_default="medium",
        ),
        sa.Column("priority_score", sa.Float, server_default="0.5"),
        sa.Column("priority_factors", JSONB, server_default="{}"),
        # Sentimento
        sa.Column(
            "sentiment",
            ENUM(
                "very_negative",
                "negative",
                "neutral",
                "positive",
                "very_positive",
                name="email_sentiment_enum",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("sentiment_score", sa.Float, server_default="0.0"),
        sa.Column("emotions", JSONB, server_default="{}"),
        # Analise
        sa.Column("language", sa.String(10), server_default="'pt-BR'"),
        sa.Column("keywords", ARRAY(sa.String), server_default="{}"),
        sa.Column("entities", JSONB, server_default="[]"),
        sa.Column("topics", ARRAY(sa.String), server_default="{}"),
        sa.Column("intent", sa.String(100), nullable=True),
        sa.Column("intent_confidence", sa.Float, server_default="0.0"),
        # Acoes
        sa.Column("action_items", JSONB, server_default="[]"),
        sa.Column("questions", JSONB, server_default="[]"),
        sa.Column("requests", JSONB, server_default="[]"),
        # Seguranca
        sa.Column("is_spam", sa.Boolean, server_default="false"),
        sa.Column("spam_score", sa.Float, server_default="0.0"),
        sa.Column("is_phishing", sa.Boolean, server_default="false"),
        sa.Column("phishing_indicators", JSONB, server_default="[]"),
        sa.Column("security_score", sa.Float, server_default="1.0"),
        # Resposta
        sa.Column("auto_reply_sent", sa.Boolean, server_default="false"),
        sa.Column("auto_reply_id", UUID(as_uuid=True), nullable=True),
        sa.Column("suggested_reply", sa.Text, nullable=True),
        sa.Column("reply_confidence", sa.Float, server_default="0.0"),
        # Roteamento
        sa.Column("assigned_to", UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_team", sa.String(100), nullable=True),
        sa.Column("routing_reason", sa.String(500), nullable=True),
        # Datas
        sa.Column("received_at", sa.DateTime, nullable=False),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("responded_at", sa.DateTime, nullable=True),
        sa.Column("read_at", sa.DateTime, nullable=True),
        # Metricas
        sa.Column("processing_time_ms", sa.Integer, server_default="0"),
        sa.Column("response_time_minutes", sa.Integer, nullable=True),
        # Relacionamentos
        sa.Column("account_id", UUID(as_uuid=True), nullable=True),
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        sa.Column("contact_id", UUID(as_uuid=True), nullable=True),
        sa.Column("ticket_id", UUID(as_uuid=True), nullable=True),
        # Metadados
        sa.Column("headers", JSONB, server_default="{}"),
        sa.Column("metadata", JSONB, server_default="{}"),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
    )

    # Indices para ai_emails
    op.create_index("ix_ai_emails_message_id", "ai_emails", ["message_id"])
    op.create_index("ix_ai_emails_thread_id", "ai_emails", ["thread_id"])
    op.create_index("ix_ai_emails_from_address", "ai_emails", ["from_address"])
    op.create_index("ix_ai_emails_status", "ai_emails", ["status"])
    op.create_index("ix_ai_emails_category", "ai_emails", ["category"])
    op.create_index("ix_ai_emails_priority", "ai_emails", ["priority"])
    op.create_index("ix_ai_emails_is_spam", "ai_emails", ["is_spam"])
    op.create_index("ix_ai_emails_received_at", "ai_emails", ["received_at"])
    op.create_index("ix_ai_emails_condominio_id", "ai_emails", ["condominio_id"])
    op.create_index("ix_ai_emails_assigned_to", "ai_emails", ["assigned_to"])

    # Tabela ai_email_responses
    op.create_table(
        "ai_email_responses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Conteudo
        sa.Column("subject", sa.String(1000), nullable=True),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("body_html", sa.Text, nullable=True),
        # Tipo
        sa.Column("response_type", sa.String(50), server_default="'manual'"),
        sa.Column("template_id", UUID(as_uuid=True), nullable=True),
        sa.Column("template_name", sa.String(200), nullable=True),
        # Status
        sa.Column("is_draft", sa.Boolean, server_default="true"),
        sa.Column("is_sent", sa.Boolean, server_default="false"),
        sa.Column("sent_at", sa.DateTime, nullable=True),
        # IA
        sa.Column("ai_generated", sa.Boolean, server_default="false"),
        sa.Column("generation_confidence", sa.Float, server_default="0.0"),
        sa.Column("modifications", JSONB, server_default="[]"),
        # Relacionamentos
        sa.Column(
            "email_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_emails.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_ai_email_responses_email_id", "ai_email_responses", ["email_id"])

    # ENUM para categoria de template (diferente para evitar conflito)
    create_enum_safe(
        "email_category_enum_template",
        [
            "support",
            "sales",
            "billing",
            "complaint",
            "information",
            "scheduling",
            "feedback",
            "newsletter",
            "spam",
            "phishing",
            "internal",
            "other",
        ],
    )

    # Tabela ai_email_templates
    op.create_table(
        "ai_email_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Conteudo
        sa.Column("subject_template", sa.String(1000), nullable=True),
        sa.Column("body_template", sa.Text, nullable=False),
        sa.Column("body_html_template", sa.Text, nullable=True),
        # Classificacao
        sa.Column(
            "category",
            ENUM(
                "support",
                "sales",
                "billing",
                "complaint",
                "information",
                "scheduling",
                "feedback",
                "newsletter",
                "spam",
                "phishing",
                "internal",
                "other",
                name="email_category_enum_template",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("language", sa.String(10), server_default="'pt-BR'"),
        sa.Column("tags", ARRAY(sa.String), server_default="{}"),
        # Condicoes
        sa.Column("trigger_keywords", ARRAY(sa.String), server_default="{}"),
        sa.Column("trigger_intents", ARRAY(sa.String), server_default="{}"),
        sa.Column("min_confidence", sa.Float, server_default="0.7"),
        # Variaveis
        sa.Column("variables", JSONB, server_default="[]"),
        # Estatisticas
        sa.Column("usage_count", sa.Integer, server_default="0"),
        sa.Column("success_rate", sa.Float, server_default="0.0"),
        sa.Column("avg_response_time", sa.Float, server_default="0.0"),
        # Config
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("requires_approval", sa.Boolean, server_default="false"),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
    )

    op.create_index("ix_ai_email_templates_code", "ai_email_templates", ["code"])
    op.create_index("ix_ai_email_templates_category", "ai_email_templates", ["category"])
    op.create_index("ix_ai_email_templates_is_active", "ai_email_templates", ["is_active"])

    # Tabela ai_email_rules
    op.create_table(
        "ai_email_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("priority", sa.Integer, server_default="0"),
        # Condicoes e acoes
        sa.Column("conditions", JSONB, nullable=False),
        sa.Column("condition_logic", sa.String(10), server_default="'AND'"),
        sa.Column("actions", JSONB, nullable=False),
        # Config
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("stop_processing", sa.Boolean, server_default="false"),
        # Estatisticas
        sa.Column("match_count", sa.Integer, server_default="0"),
        sa.Column("last_match_at", sa.DateTime, nullable=True),
        # Relacionamentos
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
    )

    op.create_index("ix_ai_email_rules_priority", "ai_email_rules", ["priority"])
    op.create_index("ix_ai_email_rules_is_active", "ai_email_rules", ["is_active"])
    op.create_index("ix_ai_email_rules_condominio_id", "ai_email_rules", ["condominio_id"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("ai_email_rules")
    op.drop_table("ai_email_templates")
    op.drop_table("ai_email_responses")
    op.drop_table("ai_emails")

    # Drop ENUMs
    op.execute("DROP TYPE IF EXISTS email_category_enum_template")
    op.execute("DROP TYPE IF EXISTS email_sentiment_enum")
    op.execute("DROP TYPE IF EXISTS email_priority_enum")
    op.execute("DROP TYPE IF EXISTS email_category_enum")
    op.execute("DROP TYPE IF EXISTS email_status_enum")
