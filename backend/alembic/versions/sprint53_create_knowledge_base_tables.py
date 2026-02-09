"""Sprint 53: Create Knowledge Base tables.

Revision ID: sprint53_kb
Revises: sprint52_voice
Create Date: 2025-01-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint53_kb"
down_revision: str | None = "sprint52_voice"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create ENUMs
    knowledge_base_status_enum = postgresql.ENUM(
        "draft", "active", "inactive", "archived", "maintenance", name="knowledge_base_status_enum", create_type=False
    )
    knowledge_base_status_enum.create(op.get_bind(), checkfirst=True)

    knowledge_base_type_enum = postgresql.ENUM(
        "general",
        "technical",
        "support",
        "faq",
        "procedures",
        "policies",
        "training",
        "product",
        "internal",
        "external",
        name="knowledge_base_type_enum",
        create_type=False,
    )
    knowledge_base_type_enum.create(op.get_bind(), checkfirst=True)

    knowledge_base_visibility_enum = postgresql.ENUM(
        "public", "private", "restricted", "internal", name="knowledge_base_visibility_enum", create_type=False
    )
    knowledge_base_visibility_enum.create(op.get_bind(), checkfirst=True)

    article_status_enum = postgresql.ENUM(
        "draft",
        "pending_review",
        "published",
        "archived",
        "outdated",
        "needs_update",
        name="article_status_enum",
        create_type=False,
    )
    article_status_enum.create(op.get_bind(), checkfirst=True)

    article_type_enum = postgresql.ENUM(
        "how_to",
        "tutorial",
        "guide",
        "reference",
        "troubleshooting",
        "announcement",
        "policy",
        "procedure",
        "best_practice",
        "glossary",
        name="article_type_enum",
        create_type=False,
    )
    article_type_enum.create(op.get_bind(), checkfirst=True)

    article_priority_enum = postgresql.ENUM(
        "low", "normal", "high", "featured", name="article_priority_enum", create_type=False
    )
    article_priority_enum.create(op.get_bind(), checkfirst=True)

    faq_status_enum = postgresql.ENUM(
        "draft", "published", "archived", "needs_update", name="faq_status_enum", create_type=False
    )
    faq_status_enum.create(op.get_bind(), checkfirst=True)

    faq_source_enum = postgresql.ENUM(
        "manual",
        "imported",
        "ai_generated",
        "from_ticket",
        "from_chat",
        "from_call",
        "community",
        name="faq_source_enum",
        create_type=False,
    )
    faq_source_enum.create(op.get_bind(), checkfirst=True)

    qa_session_status_enum = postgresql.ENUM(
        "active", "completed", "abandoned", "escalated", name="qa_session_status_enum", create_type=False
    )
    qa_session_status_enum.create(op.get_bind(), checkfirst=True)

    qa_source_enum = postgresql.ENUM(
        "web_widget",
        "mobile_app",
        "api",
        "chat",
        "voice",
        "email",
        "whatsapp",
        "internal",
        name="qa_source_enum",
        create_type=False,
    )
    qa_source_enum.create(op.get_bind(), checkfirst=True)

    qa_interaction_type_enum = postgresql.ENUM(
        "question",
        "clarification",
        "follow_up",
        "feedback",
        "escalation",
        name="qa_interaction_type_enum",
        create_type=False,
    )
    qa_interaction_type_enum.create(op.get_bind(), checkfirst=True)

    qa_response_type_enum = postgresql.ENUM(
        "direct_answer",
        "article_match",
        "faq_match",
        "generated",
        "no_answer",
        "escalated",
        "clarification_needed",
        name="qa_response_type_enum",
        create_type=False,
    )
    qa_response_type_enum.create(op.get_bind(), checkfirst=True)

    # Create ai_knowledge_bases table
    op.create_table(
        "ai_knowledge_bases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("kb_type", knowledge_base_type_enum, nullable=False, server_default="general"),
        sa.Column("status", knowledge_base_status_enum, nullable=False, server_default="draft"),
        sa.Column("visibility", knowledge_base_visibility_enum, nullable=False, server_default="internal"),
        sa.Column("default_language", sa.String(10), server_default="pt-BR"),
        sa.Column("supported_languages", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("enable_ai_answers", sa.Boolean, server_default="true"),
        sa.Column("enable_semantic_search", sa.Boolean, server_default="true"),
        sa.Column("enable_auto_suggestions", sa.Boolean, server_default="true"),
        sa.Column("enable_feedback", sa.Boolean, server_default="true"),
        sa.Column("index_status", sa.String(50), server_default="pending"),
        sa.Column("last_indexed_at", sa.DateTime, nullable=True),
        sa.Column("total_indexed_articles", sa.Integer, server_default="0"),
        sa.Column("total_indexed_faqs", sa.Integer, server_default="0"),
        sa.Column("embedding_model", sa.String(100), server_default="all-MiniLM-L6-v2"),
        sa.Column("vector_dimension", sa.Integer, server_default="384"),
        sa.Column("total_articles", sa.Integer, server_default="0"),
        sa.Column("total_faqs", sa.Integer, server_default="0"),
        sa.Column("total_categories", sa.Integer, server_default="0"),
        sa.Column("total_searches", sa.Integer, server_default="0"),
        sa.Column("total_views", sa.Integer, server_default="0"),
        sa.Column("average_rating", sa.Integer, server_default="0"),
        sa.Column("allowed_roles", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("allowed_users", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column("allowed_condominios", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column("settings", postgresql.JSONB, server_default="{}"),
        sa.Column("custom_prompts", postgresql.JSONB, server_default="{}"),
        sa.Column("synonyms", postgresql.JSONB, server_default="{}"),
        sa.Column("stopwords", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )
    op.create_index("ix_ai_knowledge_bases_slug", "ai_knowledge_bases", ["slug"])
    op.create_index("ix_ai_knowledge_bases_status", "ai_knowledge_bases", ["status"])
    op.create_index("ix_ai_knowledge_bases_condominio", "ai_knowledge_bases", ["condominio_id"])

    # Create ai_kb_categories table
    op.create_table(
        "ai_kb_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_categories.id"), nullable=True),
        sa.Column("level", sa.Integer, server_default="0"),
        sa.Column("path", sa.String(500), nullable=True),
        sa.Column("order", sa.Integer, server_default="0"),
        sa.Column("article_count", sa.Integer, server_default="0"),
        sa.Column("faq_count", sa.Integer, server_default="0"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column(
            "knowledge_base_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_knowledge_bases.id"), nullable=False
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )
    op.create_index("ix_ai_kb_categories_kb", "ai_kb_categories", ["knowledge_base_id"])
    op.create_index("ix_ai_kb_categories_parent", "ai_kb_categories", ["parent_id"])

    # Create ai_kb_articles table
    op.create_table(
        "ai_kb_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(500), nullable=False),
        sa.Column("subtitle", sa.String(500), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_html", sa.Text, nullable=True),
        sa.Column("content_plain", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("excerpt", sa.String(500), nullable=True),
        sa.Column("article_type", article_type_enum, nullable=False, server_default="guide"),
        sa.Column("status", article_status_enum, nullable=False, server_default="draft"),
        sa.Column("priority", article_priority_enum, nullable=False, server_default="normal"),
        sa.Column("tags", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("keywords", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("related_topics", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("language", sa.String(10), server_default="pt-BR"),
        sa.Column("meta_title", sa.String(200), nullable=True),
        sa.Column("meta_description", sa.String(500), nullable=True),
        sa.Column("search_vector", postgresql.TSVECTOR, nullable=True),
        sa.Column("embedding", postgresql.ARRAY(sa.Float), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=True),
        sa.Column("embedding_updated_at", sa.DateTime, nullable=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("is_latest", sa.Boolean, server_default="true"),
        sa.Column(
            "parent_article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_articles.id"), nullable=True
        ),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("search_count", sa.Integer, server_default="0"),
        sa.Column("helpful_count", sa.Integer, server_default="0"),
        sa.Column("not_helpful_count", sa.Integer, server_default="0"),
        sa.Column("share_count", sa.Integer, server_default="0"),
        sa.Column("rating_sum", sa.Integer, server_default="0"),
        sa.Column("rating_count", sa.Integer, server_default="0"),
        sa.Column("average_rating", sa.Float, server_default="0"),
        sa.Column("average_time_on_page", sa.Integer, server_default="0"),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("review_at", sa.DateTime, nullable=True),
        sa.Column("last_viewed_at", sa.DateTime, nullable=True),
        sa.Column(
            "knowledge_base_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_knowledge_bases.id"), nullable=False
        ),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_categories.id"), nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_articles", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column("related_faqs", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column("attachments", postgresql.JSONB, server_default="[]"),
        sa.Column("media", postgresql.JSONB, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("custom_fields", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )
    op.create_index("ix_ai_kb_articles_kb", "ai_kb_articles", ["knowledge_base_id"])
    op.create_index("ix_ai_kb_articles_category", "ai_kb_articles", ["category_id"])
    op.create_index("ix_ai_kb_articles_status", "ai_kb_articles", ["status"])
    op.create_index("ix_ai_kb_articles_slug", "ai_kb_articles", ["knowledge_base_id", "slug"])

    # Create ai_kb_article_versions table
    op.create_table(
        "ai_kb_article_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("version_label", sa.String(100), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("change_summary", sa.Text, nullable=True),
        sa.Column("changed_fields", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_articles.id"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_kb_article_versions_article", "ai_kb_article_versions", ["article_id"])

    # Create ai_kb_article_feedback table
    op.create_table(
        "ai_kb_article_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("is_helpful", sa.Boolean, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("search_query", sa.String(500), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_articles.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_kb_article_feedback_article", "ai_kb_article_feedback", ["article_id"])

    # Create ai_kb_faqs table
    op.create_table(
        "ai_kb_faqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("question_normalized", sa.Text, nullable=True),
        sa.Column("question_variations", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("answer_html", sa.Text, nullable=True),
        sa.Column("answer_short", sa.String(500), nullable=True),
        sa.Column("status", faq_status_enum, nullable=False, server_default="draft"),
        sa.Column("source", faq_source_enum, nullable=False, server_default="manual"),
        sa.Column("tags", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("keywords", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("language", sa.String(10), server_default="pt-BR"),
        sa.Column("order", sa.Integer, server_default="0"),
        sa.Column("priority", sa.Integer, server_default="0"),
        sa.Column("search_vector", postgresql.TSVECTOR, nullable=True),
        sa.Column("question_embedding", postgresql.ARRAY(sa.Float), nullable=True),
        sa.Column("answer_embedding", postgresql.ARRAY(sa.Float), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=True),
        sa.Column("embedding_updated_at", sa.DateTime, nullable=True),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("search_count", sa.Integer, server_default="0"),
        sa.Column("helpful_count", sa.Integer, server_default="0"),
        sa.Column("not_helpful_count", sa.Integer, server_default="0"),
        sa.Column("click_count", sa.Integer, server_default="0"),
        sa.Column("helpfulness_score", sa.Float, server_default="0"),
        sa.Column("ai_used_count", sa.Integer, server_default="0"),
        sa.Column("ai_confidence_avg", sa.Float, server_default="0"),
        sa.Column("last_ai_used_at", sa.DateTime, nullable=True),
        sa.Column("applicable_scenarios", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("preconditions", sa.Text, nullable=True),
        sa.Column("related_questions", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column(
            "knowledge_base_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_knowledge_bases.id"), nullable=False
        ),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_categories.id"), nullable=True),
        sa.Column(
            "related_article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_articles.id"), nullable=True
        ),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_ticket_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_chat_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_call_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )
    op.create_index("ix_ai_kb_faqs_kb", "ai_kb_faqs", ["knowledge_base_id"])
    op.create_index("ix_ai_kb_faqs_category", "ai_kb_faqs", ["category_id"])
    op.create_index("ix_ai_kb_faqs_status", "ai_kb_faqs", ["status"])

    # Create ai_kb_faq_feedback table
    op.create_table(
        "ai_kb_faq_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("is_helpful", sa.Boolean, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("improvement_suggestion", sa.Text, nullable=True),
        sa.Column("search_query", sa.String(500), nullable=True),
        sa.Column("matched_confidence", sa.Float, nullable=True),
        sa.Column("was_ai_response", sa.Boolean, server_default="false"),
        sa.Column("faq_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_faqs.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_kb_faq_feedback_faq", "ai_kb_faq_feedback", ["faq_id"])

    # Create ai_qa_sessions table
    op.create_table(
        "ai_qa_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_key", sa.String(100), unique=True, nullable=False),
        sa.Column("status", qa_session_status_enum, nullable=False, server_default="active"),
        sa.Column("source", qa_source_enum, nullable=False, server_default="web_widget"),
        sa.Column("context", postgresql.JSONB, server_default="{}"),
        sa.Column("user_context", postgresql.JSONB, server_default="{}"),
        sa.Column("page_context", postgresql.JSONB, server_default="{}"),
        sa.Column("interaction_count", sa.Integer, server_default="0"),
        sa.Column("question_count", sa.Integer, server_default="0"),
        sa.Column("answered_count", sa.Integer, server_default="0"),
        sa.Column("unanswered_count", sa.Integer, server_default="0"),
        sa.Column("average_confidence", sa.Float, server_default="0"),
        sa.Column("average_response_time_ms", sa.Integer, server_default="0"),
        sa.Column("overall_rating", sa.Integer, nullable=True),
        sa.Column("overall_helpful", sa.Boolean, nullable=True),
        sa.Column("feedback_comment", sa.Text, nullable=True),
        sa.Column("resolved", sa.Boolean, server_default="false"),
        sa.Column("resolution_type", sa.String(50), nullable=True),
        sa.Column("escalated", sa.Boolean, server_default="false"),
        sa.Column("escalated_to", sa.String(100), nullable=True),
        sa.Column("escalation_reason", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime, nullable=True),
        sa.Column("last_interaction_at", sa.DateTime, nullable=True),
        sa.Column("total_duration_seconds", sa.Integer, server_default="0"),
        sa.Column(
            "knowledge_base_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_knowledge_bases.id"), nullable=True
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_id", sa.String(100), nullable=True),
        sa.Column("client_ip", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )
    op.create_index("ix_ai_qa_sessions_key", "ai_qa_sessions", ["session_key"])
    op.create_index("ix_ai_qa_sessions_user", "ai_qa_sessions", ["user_id"])
    op.create_index("ix_ai_qa_sessions_kb", "ai_qa_sessions", ["knowledge_base_id"])

    # Create ai_qa_interactions table
    op.create_table(
        "ai_qa_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("interaction_type", qa_interaction_type_enum, nullable=False, server_default="question"),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("question_normalized", sa.Text, nullable=True),
        sa.Column("question_intent", sa.String(100), nullable=True),
        sa.Column("question_entities", postgresql.JSONB, server_default="[]"),
        sa.Column("question_embedding", postgresql.ARRAY(sa.Float), nullable=True),
        sa.Column("response_type", qa_response_type_enum, nullable=True),
        sa.Column("response", sa.Text, nullable=True),
        sa.Column("response_formatted", sa.Text, nullable=True),
        sa.Column("response_sources", postgresql.JSONB, server_default="[]"),
        sa.Column("confidence_score", sa.Float, server_default="0"),
        sa.Column("relevance_score", sa.Float, server_default="0"),
        sa.Column("quality_score", sa.Float, server_default="0"),
        sa.Column("response_time_ms", sa.Integer, server_default="0"),
        sa.Column("matched_articles", postgresql.JSONB, server_default="[]"),
        sa.Column("matched_faqs", postgresql.JSONB, server_default="[]"),
        sa.Column("search_results", postgresql.JSONB, server_default="[]"),
        sa.Column("is_helpful", sa.Boolean, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("feedback_text", sa.Text, nullable=True),
        sa.Column("feedback_at", sa.DateTime, nullable=True),
        sa.Column("action_taken", sa.String(100), nullable=True),
        sa.Column("clicked_article_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("clicked_faq_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("context_used", postgresql.JSONB, server_default="{}"),
        sa.Column("previous_context", postgresql.JSONB, server_default="{}"),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_qa_sessions.id"), nullable=False),
        sa.Column(
            "parent_interaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_qa_interactions.id"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_ai_qa_interactions_session", "ai_qa_interactions", ["session_id"])
    op.create_index("ix_ai_qa_interactions_parent", "ai_qa_interactions", ["parent_interaction_id"])

    # Create ai_qa_suggestions table
    op.create_table(
        "ai_qa_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("suggestion_text", sa.String(500), nullable=False),
        sa.Column("suggestion_type", sa.String(50), server_default="related"),
        sa.Column("context_page", sa.String(200), nullable=True),
        sa.Column("context_category", sa.String(100), nullable=True),
        sa.Column("context_keywords", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("shown_count", sa.Integer, server_default="0"),
        sa.Column("click_count", sa.Integer, server_default="0"),
        sa.Column("click_rate", sa.Float, server_default="0"),
        sa.Column("valid_from", sa.DateTime, nullable=True),
        sa.Column("valid_until", sa.DateTime, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column(
            "knowledge_base_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_knowledge_bases.id"), nullable=False
        ),
        sa.Column("target_faq_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_faqs.id"), nullable=True),
        sa.Column(
            "target_article_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_kb_articles.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )
    op.create_index("ix_ai_qa_suggestions_kb", "ai_qa_suggestions", ["knowledge_base_id"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("ai_qa_suggestions")
    op.drop_table("ai_qa_interactions")
    op.drop_table("ai_qa_sessions")
    op.drop_table("ai_kb_faq_feedback")
    op.drop_table("ai_kb_faqs")
    op.drop_table("ai_kb_article_feedback")
    op.drop_table("ai_kb_article_versions")
    op.drop_table("ai_kb_articles")
    op.drop_table("ai_kb_categories")
    op.drop_table("ai_knowledge_bases")

    # Drop ENUMs
    op.execute("DROP TYPE IF EXISTS qa_response_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS qa_interaction_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS qa_source_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS qa_session_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS faq_source_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS faq_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS article_priority_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS article_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS article_status_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS knowledge_base_visibility_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS knowledge_base_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS knowledge_base_status_enum CASCADE")
