"""Sprint 01: Create conversation AI tables.

Revision ID: sprint01_conv_ai
Revises: ews001_create_monitoring_tables
Create Date: 2025-01-06

Tabelas para o modulo de IA Conversacional:
- chat_sessions: Sessoes de conversa
- chat_messages: Mensagens das conversas
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision: str = "sprint01_conv_ai"
down_revision: str | None = "ews001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabelas do modulo de IA Conversacional."""

    # ===========================================================================
    # TABELA: chat_sessions
    # ===========================================================================
    op.create_table(
        "chat_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(200), nullable=False, default="Nova Conversa"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("module_context", sa.String(50), nullable=True),
        sa.Column(
            "context_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("message_count", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "last_message_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, default=False),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        # Foreign Keys
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_chat_sessions_user_id",
            ondelete="CASCADE",
        ),
    )

    # Indices para chat_sessions
    op.create_index(
        "ix_chat_sessions_user_id",
        "chat_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_chat_sessions_user_active",
        "chat_sessions",
        ["user_id", "is_active"],
        postgresql_where=sa.text("is_active = true"),
    )
    op.create_index(
        "ix_chat_sessions_last_message",
        "chat_sessions",
        ["last_message_at"],
    )
    op.create_index(
        "ix_chat_sessions_module",
        "chat_sessions",
        ["module_context"],
        postgresql_where=sa.text("module_context IS NOT NULL"),
    )

    # ===========================================================================
    # ENUM TYPES
    # ===========================================================================
    message_type_enum = postgresql.ENUM(
        "user",
        "assistant",
        "system",
        name="message_type",
        create_type=False,
    )
    message_type_enum.create(op.get_bind(), checkfirst=True)

    message_status_enum = postgresql.ENUM(
        "pending",
        "processing",
        "completed",
        "failed",
        "cancelled",
        name="message_status",
        create_type=False,
    )
    message_status_enum.create(op.get_bind(), checkfirst=True)

    intent_category_enum = postgresql.ENUM(
        "help_navigation",
        "data_query",
        "action_request",
        "analysis_request",
        "system_info",
        "troubleshooting",
        "feedback",
        "greeting",
        "farewell",
        "general_conversation",
        name="intent_category",
        create_type=False,
    )
    intent_category_enum.create(op.get_bind(), checkfirst=True)

    # ===========================================================================
    # TABELA: chat_messages
    # ===========================================================================
    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "message_type",
            message_type_enum,
            nullable=False,
            default="user",
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_html", sa.Text(), nullable=True),
        sa.Column(
            "intent",
            intent_category_enum,
            nullable=True,
        ),
        sa.Column("intent_confidence", sa.Float(), nullable=True),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column(
            "entities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "suggestions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "related_links",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(50), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column(
            "context_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("user_rating", sa.Integer(), nullable=True),
        sa.Column("was_helpful", sa.Boolean(), nullable=True),
        sa.Column("user_feedback", sa.Text(), nullable=True),
        sa.Column(
            "status",
            message_status_enum,
            nullable=False,
            default="completed",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        # Foreign Keys
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["chat_sessions.id"],
            name="fk_chat_messages_session_id",
            ondelete="CASCADE",
        ),
    )

    # Indices para chat_messages
    op.create_index(
        "ix_chat_messages_session_id",
        "chat_messages",
        ["session_id"],
    )
    op.create_index(
        "ix_chat_messages_session_created",
        "chat_messages",
        ["session_id", "created_at"],
    )
    op.create_index(
        "ix_chat_messages_intent",
        "chat_messages",
        ["intent"],
        postgresql_where=sa.text("intent IS NOT NULL"),
    )
    op.create_index(
        "ix_chat_messages_message_type",
        "chat_messages",
        ["message_type"],
    )
    op.create_index(
        "ix_chat_messages_rating",
        "chat_messages",
        ["user_rating"],
        postgresql_where=sa.text("user_rating IS NOT NULL"),
    )

    # ===========================================================================
    # TABELA: chat_analytics (para metricas agregadas)
    # ===========================================================================
    op.create_table(
        "chat_analytics",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("module", sa.String(50), nullable=True),
        sa.Column("total_sessions", sa.Integer(), nullable=False, default=0),
        sa.Column("total_messages", sa.Integer(), nullable=False, default=0),
        sa.Column("user_messages", sa.Integer(), nullable=False, default=0),
        sa.Column("assistant_messages", sa.Integer(), nullable=False, default=0),
        sa.Column("avg_response_time_ms", sa.Float(), nullable=True),
        sa.Column("total_tokens_used", sa.Integer(), nullable=False, default=0),
        sa.Column("helpful_count", sa.Integer(), nullable=False, default=0),
        sa.Column("unhelpful_count", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "intent_distribution",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "sentiment_distribution",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        # Constraint de unicidade
        sa.UniqueConstraint(
            "date",
            "user_id",
            "module",
            name="uq_chat_analytics_date_user_module",
        ),
    )

    # Indices para analytics
    op.create_index(
        "ix_chat_analytics_date",
        "chat_analytics",
        ["date"],
    )
    op.create_index(
        "ix_chat_analytics_user",
        "chat_analytics",
        ["user_id"],
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )

    # ===========================================================================
    # TABELA: chat_templates (templates de resposta)
    # ===========================================================================
    op.create_table(
        "chat_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("module", sa.String(50), nullable=True),
        sa.Column("intent", intent_category_enum, nullable=True),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column(
            "variables",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
        sa.Column(
            "suggestions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "actions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("priority", sa.Integer(), nullable=False, default=0),
        sa.Column("usage_count", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Indices para templates
    op.create_index(
        "ix_chat_templates_category",
        "chat_templates",
        ["category"],
    )
    op.create_index(
        "ix_chat_templates_module",
        "chat_templates",
        ["module"],
        postgresql_where=sa.text("module IS NOT NULL"),
    )
    op.create_index(
        "ix_chat_templates_intent",
        "chat_templates",
        ["intent"],
        postgresql_where=sa.text("intent IS NOT NULL"),
    )


def downgrade() -> None:
    """Remove tabelas do modulo de IA Conversacional."""

    # Drop tables
    op.drop_table("chat_templates")
    op.drop_table("chat_analytics")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS intent_category CASCADE")
    op.execute("DROP TYPE IF EXISTS message_status CASCADE")
    op.execute("DROP TYPE IF EXISTS message_type CASCADE")
