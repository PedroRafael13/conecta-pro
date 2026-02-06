"""Sprint 36 - Create Notification Hub tables.

Revision ID: sprint36_notifications
Revises: sprint35_scheduler
Create Date: 2025-01-05

Notification Hub - Sistema centralizado de notificações multi-canal.

Tabelas:
- notification_channels: Configuração de canais (email, SMS, WhatsApp, etc)
- notification_templates: Templates multi-canal
- notification_preferences: Preferências de notificação por usuário
- notification_subscriptions: Inscrições em tópicos
- notification_queue: Fila unificada de notificações
- notification_logs: Histórico/audit log
- notification_metrics: Métricas agregadas
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint36_notifications"
down_revision: Union[str, None] = "sprint35_scheduler"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Notification Hub tables."""
    # =========================================================================
    # ENUM Types
    # =========================================================================

    # Channel Type
    channel_type = postgresql.ENUM(
        "email",
        "whatsapp",
        "sms",
        "push",
        "slack",
        "teams",
        "webhook",
        "in_app",
        "telegram",
        "voice",
        name="channeltype",
        create_type=False,
    )
    channel_type.create(op.get_bind(), checkfirst=True)

    # Channel Status
    channel_status = postgresql.ENUM(
        "active",
        "inactive",
        "maintenance",
        "degraded",
        "error",
        name="channelstatus",
        create_type=False,
    )
    channel_status.create(op.get_bind(), checkfirst=True)

    # Channel Provider
    channel_provider = postgresql.ENUM(
        "smtp",
        "sendgrid",
        "mailgun",
        "aws_ses",
        "postmark",
        "whatsapp_business",
        "twilio_whatsapp",
        "messagebird_whatsapp",
        "twilio_sms",
        "zenvia",
        "messagebird_sms",
        "nexmo",
        "aws_sns",
        "fcm",
        "apns",
        "onesignal",
        "pusher",
        "slack_api",
        "teams_api",
        "telegram_bot",
        "custom_webhook",
        "twilio_voice",
        "internal",
        name="channelprovider",
        create_type=False,
    )
    channel_provider.create(op.get_bind(), checkfirst=True)

    # Template Status
    template_status = postgresql.ENUM(
        "draft",
        "pending_approval",
        "approved",
        "rejected",
        "active",
        "inactive",
        "archived",
        name="templatestatus",
        create_type=False,
    )
    template_status.create(op.get_bind(), checkfirst=True)

    # Template Category
    template_category = postgresql.ENUM(
        "transactional",
        "marketing",
        "system",
        "alert",
        "reminder",
        "welcome",
        "confirmation",
        "notification",
        "report",
        "survey",
        name="templatecategory",
        create_type=False,
    )
    template_category.create(op.get_bind(), checkfirst=True)

    # Frequency Type
    frequency_type = postgresql.ENUM(
        "instant",
        "hourly",
        "daily",
        "weekly",
        "monthly",
        "never",
        name="frequencytype",
        create_type=False,
    )
    frequency_type.create(op.get_bind(), checkfirst=True)

    # Digest Type
    digest_type = postgresql.ENUM(
        "none",
        "daily_summary",
        "weekly_summary",
        "smart",
        name="digesttype",
        create_type=False,
    )
    digest_type.create(op.get_bind(), checkfirst=True)

    # Queue Status
    queue_status = postgresql.ENUM(
        "pending",
        "scheduled",
        "processing",
        "sent",
        "delivered",
        "failed",
        "retry",
        "cancelled",
        "expired",
        "bounced",
        "unsubscribed",
        name="queuestatus",
        create_type=False,
    )
    queue_status.create(op.get_bind(), checkfirst=True)

    # Queue Priority
    queue_priority = postgresql.ENUM(
        "1",
        "2",
        "5",
        "8",
        "10",
        name="queuepriority",
        create_type=False,
    )
    queue_priority.create(op.get_bind(), checkfirst=True)

    # Log Event Type
    log_event_type = postgresql.ENUM(
        "created",
        "queued",
        "scheduled",
        "processing",
        "sent",
        "delivered",
        "failed",
        "retrying",
        "cancelled",
        "expired",
        "opened",
        "clicked",
        "converted",
        "replied",
        "bounced",
        "complained",
        "unsubscribed",
        "blocked",
        "rate_limited",
        "provider_error",
        "validation_error",
        "preference_blocked",
        name="logeventtype",
        create_type=False,
    )
    log_event_type.create(op.get_bind(), checkfirst=True)

    # Log Level
    log_level = postgresql.ENUM(
        "debug",
        "info",
        "warning",
        "error",
        "critical",
        name="loglevel",
        create_type=False,
    )
    log_level.create(op.get_bind(), checkfirst=True)

    # =========================================================================
    # notification_channels
    # =========================================================================
    op.create_table(
        "notification_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificação
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("channel_type", channel_type, nullable=False, index=True),
        sa.Column("provider", channel_provider, nullable=False),
        sa.Column("status", channel_status, default="active", index=True),
        # Configuração
        sa.Column("provider_config", postgresql.JSONB, default={}),
        sa.Column("sender_config", postgresql.JSONB, default={}),
        # Rate Limiting
        sa.Column("rate_limit_per_second", sa.Integer, default=10),
        sa.Column("rate_limit_per_minute", sa.Integer, default=100),
        sa.Column("rate_limit_per_hour", sa.Integer, default=1000),
        sa.Column("rate_limit_per_day", sa.Integer, default=10000),
        sa.Column("current_rate_count", sa.Integer, default=0),
        sa.Column("rate_reset_at", sa.DateTime),
        # Retry
        sa.Column("max_retries", sa.Integer, default=3),
        sa.Column("retry_delay_seconds", sa.Integer, default=60),
        sa.Column("retry_backoff_multiplier", sa.Float, default=2.0),
        # Prioridade e Fallback
        sa.Column("priority", sa.Integer, default=5),
        sa.Column("fallback_channel_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("is_default", sa.Boolean, default=False),
        # Horários
        sa.Column("business_hours_only", sa.Boolean, default=False),
        sa.Column("business_hours_start", sa.String(5)),
        sa.Column("business_hours_end", sa.String(5)),
        sa.Column("business_days", postgresql.ARRAY(sa.Integer), default=[1, 2, 3, 4, 5]),
        sa.Column("timezone", sa.String(50), default="America/Sao_Paulo"),
        # Métricas
        sa.Column("total_sent", sa.Integer, default=0),
        sa.Column("total_delivered", sa.Integer, default=0),
        sa.Column("total_failed", sa.Integer, default=0),
        sa.Column("total_bounced", sa.Integer, default=0),
        sa.Column("delivery_rate", sa.Float),
        sa.Column("avg_delivery_time_seconds", sa.Float),
        sa.Column("last_sent_at", sa.DateTime),
        sa.Column("last_error_at", sa.DateTime),
        sa.Column("last_error_message", sa.Text),
        # Custos
        sa.Column("cost_per_message", sa.Float, default=0.0),
        sa.Column("monthly_budget", sa.Float),
        sa.Column("current_month_spend", sa.Float, default=0.0),
        # Categorias
        sa.Column("supported_categories", postgresql.ARRAY(sa.String), default=[]),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        sa.Column("tags", postgresql.ARRAY(sa.String), default=[]),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_notification_channels_tenant_slug", "notification_channels", ["tenant_id", "slug"], unique=True)

    # =========================================================================
    # notification_templates
    # =========================================================================
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificação
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False, index=True),
        sa.Column("description", sa.Text),
        sa.Column("category", template_category, default="notification", index=True),
        sa.Column("status", template_status, default="draft", index=True),
        # Canal
        sa.Column(
            "channel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_channels.id"),
            index=True,
        ),
        # Email
        sa.Column("email_subject", sa.String(500)),
        sa.Column("email_body_html", sa.Text),
        sa.Column("email_body_text", sa.Text),
        sa.Column("email_from_name", sa.String(100)),
        sa.Column("email_from_address", sa.String(200)),
        sa.Column("email_reply_to", sa.String(200)),
        sa.Column("email_cc", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("email_bcc", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("email_attachments", postgresql.JSONB, default=[]),
        # WhatsApp
        sa.Column("whatsapp_template_name", sa.String(200)),
        sa.Column("whatsapp_template_namespace", sa.String(200)),
        sa.Column("whatsapp_language", sa.String(10), default="pt_BR"),
        sa.Column("whatsapp_header", postgresql.JSONB),
        sa.Column("whatsapp_body", sa.Text),
        sa.Column("whatsapp_footer", sa.String(60)),
        sa.Column("whatsapp_buttons", postgresql.JSONB, default=[]),
        sa.Column("whatsapp_variables", postgresql.ARRAY(sa.String), default=[]),
        # SMS
        sa.Column("sms_body", sa.String(160)),
        sa.Column("sms_unicode", sa.Boolean, default=False),
        sa.Column("sms_flash", sa.Boolean, default=False),
        # Push
        sa.Column("push_title", sa.String(100)),
        sa.Column("push_body", sa.String(500)),
        sa.Column("push_image_url", sa.String(500)),
        sa.Column("push_icon_url", sa.String(500)),
        sa.Column("push_action_url", sa.String(500)),
        sa.Column("push_data", postgresql.JSONB, default={}),
        sa.Column("push_badge_count", sa.Integer),
        sa.Column("push_sound", sa.String(50)),
        sa.Column("push_android_config", postgresql.JSONB, default={}),
        sa.Column("push_ios_config", postgresql.JSONB, default={}),
        # Slack
        sa.Column("slack_text", sa.Text),
        sa.Column("slack_blocks", postgresql.JSONB, default=[]),
        sa.Column("slack_attachments", postgresql.JSONB, default=[]),
        # In-App
        sa.Column("in_app_title", sa.String(200)),
        sa.Column("in_app_body", sa.Text),
        sa.Column("in_app_icon", sa.String(50)),
        sa.Column("in_app_color", sa.String(20)),
        sa.Column("in_app_action_url", sa.String(500)),
        sa.Column("in_app_action_label", sa.String(50)),
        # Webhook
        sa.Column("webhook_url", sa.String(500)),
        sa.Column("webhook_method", sa.String(10), default="POST"),
        sa.Column("webhook_headers", postgresql.JSONB, default={}),
        sa.Column("webhook_body_template", sa.Text),
        # Variáveis
        sa.Column("variables", postgresql.JSONB, default=[]),
        sa.Column("sample_data", postgresql.JSONB, default={}),
        # Localização
        sa.Column("locale", sa.String(10), default="pt_BR"),
        sa.Column("translations", postgresql.JSONB, default={}),
        # A/B Testing
        sa.Column("is_variant", sa.Boolean, default=False),
        sa.Column("parent_template_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("variant_name", sa.String(50)),
        sa.Column("variant_weight", sa.Integer, default=50),
        # Aprovação
        sa.Column("requires_approval", sa.Boolean, default=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True)),
        sa.Column("approved_at", sa.DateTime),
        sa.Column("rejection_reason", sa.Text),
        # Métricas
        sa.Column("total_sent", sa.Integer, default=0),
        sa.Column("total_delivered", sa.Integer, default=0),
        sa.Column("total_opened", sa.Integer, default=0),
        sa.Column("total_clicked", sa.Integer, default=0),
        sa.Column("total_converted", sa.Integer, default=0),
        sa.Column("total_unsubscribed", sa.Integer, default=0),
        sa.Column("total_bounced", sa.Integer, default=0),
        sa.Column("total_complained", sa.Integer, default=0),
        sa.Column("open_rate", sa.Float),
        sa.Column("click_rate", sa.Float),
        sa.Column("conversion_rate", sa.Float),
        # Versionamento
        sa.Column("version", sa.Integer, default=1),
        sa.Column("previous_version_id", postgresql.UUID(as_uuid=True)),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        sa.Column("tags", postgresql.ARRAY(sa.String), default=[]),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_notification_templates_tenant_slug", "notification_templates", ["tenant_id", "slug"], unique=True)

    # =========================================================================
    # notification_preferences
    # =========================================================================
    op.create_table(
        "notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Usuário
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("user_email", sa.String(200)),
        sa.Column("user_phone", sa.String(20)),
        sa.Column("user_device_tokens", postgresql.JSONB, default=[]),
        # Preferências Globais
        sa.Column("notifications_enabled", sa.Boolean, default=True),
        sa.Column("quiet_hours_enabled", sa.Boolean, default=False),
        sa.Column("quiet_hours_start", sa.String(5)),
        sa.Column("quiet_hours_end", sa.String(5)),
        sa.Column("timezone", sa.String(50), default="America/Sao_Paulo"),
        sa.Column("locale", sa.String(10), default="pt_BR"),
        # Email
        sa.Column("email_enabled", sa.Boolean, default=True),
        sa.Column("email_address", sa.String(200)),
        sa.Column("email_frequency", frequency_type, default="instant"),
        sa.Column("email_digest", digest_type, default="none"),
        # WhatsApp
        sa.Column("whatsapp_enabled", sa.Boolean, default=True),
        sa.Column("whatsapp_number", sa.String(20)),
        sa.Column("whatsapp_frequency", frequency_type, default="instant"),
        # SMS
        sa.Column("sms_enabled", sa.Boolean, default=True),
        sa.Column("sms_number", sa.String(20)),
        sa.Column("sms_frequency", frequency_type, default="instant"),
        # Push
        sa.Column("push_enabled", sa.Boolean, default=True),
        sa.Column("push_frequency", frequency_type, default="instant"),
        sa.Column("push_sound_enabled", sa.Boolean, default=True),
        sa.Column("push_vibration_enabled", sa.Boolean, default=True),
        sa.Column("push_badge_enabled", sa.Boolean, default=True),
        # In-App
        sa.Column("in_app_enabled", sa.Boolean, default=True),
        sa.Column("in_app_sound_enabled", sa.Boolean, default=True),
        # Slack
        sa.Column("slack_enabled", sa.Boolean, default=False),
        sa.Column("slack_user_id", sa.String(50)),
        sa.Column("slack_channel_id", sa.String(50)),
        # Preferências por Categoria
        sa.Column("category_preferences", postgresql.JSONB, default={}),
        sa.Column("preferred_channels", postgresql.ARRAY(sa.String), default=["email", "push", "in_app"]),
        # Unsubscribes
        sa.Column("unsubscribed_categories", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("unsubscribed_channels", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("global_unsubscribe", sa.Boolean, default=False),
        sa.Column("unsubscribe_reason", sa.Text),
        sa.Column("unsubscribed_at", sa.DateTime),
        # Double Opt-in
        sa.Column("email_verified", sa.Boolean, default=False),
        sa.Column("email_verified_at", sa.DateTime),
        sa.Column("phone_verified", sa.Boolean, default=False),
        sa.Column("phone_verified_at", sa.DateTime),
        sa.Column("verification_token", sa.String(100)),
        sa.Column("verification_expires_at", sa.DateTime),
        # Consent
        sa.Column("marketing_consent", sa.Boolean, default=False),
        sa.Column("marketing_consent_at", sa.DateTime),
        sa.Column("marketing_consent_source", sa.String(100)),
        sa.Column("transactional_consent", sa.Boolean, default=True),
        sa.Column("data_processing_consent", sa.Boolean, default=True),
        sa.Column("data_processing_consent_at", sa.DateTime),
        # Métricas
        sa.Column("total_received", sa.Integer, default=0),
        sa.Column("total_opened", sa.Integer, default=0),
        sa.Column("total_clicked", sa.Integer, default=0),
        sa.Column("last_notification_at", sa.DateTime),
        sa.Column("last_opened_at", sa.DateTime),
        sa.Column("last_clicked_at", sa.DateTime),
        sa.Column("engagement_score", sa.Float),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index("ix_notification_preferences_tenant_user", "notification_preferences", ["tenant_id", "user_id"], unique=True)

    # =========================================================================
    # notification_subscriptions
    # =========================================================================
    op.create_table(
        "notification_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Usuário
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column(
            "preference_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_preferences.id"),
            index=True,
        ),
        # Tópico
        sa.Column("topic", sa.String(200), nullable=False, index=True),
        sa.Column("topic_type", sa.String(50)),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        # Configuração
        sa.Column("channels", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("frequency", frequency_type, default="instant"),
        sa.Column("priority_only", sa.Boolean, default=False),
        # Status
        sa.Column("subscribed", sa.Boolean, default=True),
        sa.Column("subscribed_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("unsubscribed_at", sa.DateTime),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index("ix_notification_subscriptions_user_topic", "notification_subscriptions", ["user_id", "topic"])

    # =========================================================================
    # notification_queue
    # =========================================================================
    op.create_table(
        "notification_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificação
        sa.Column("notification_id", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("correlation_id", sa.String(100), index=True),
        # Destinatário
        sa.Column("user_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("recipient_type", sa.String(20), default="user"),
        sa.Column("recipient_address", sa.String(200), nullable=False),
        sa.Column("recipient_name", sa.String(200)),
        # Canal e Template
        sa.Column(
            "channel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_channels.id"),
            index=True,
        ),
        sa.Column("channel_type", sa.String(20), nullable=False, index=True),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_templates.id"),
            index=True,
        ),
        # Conteúdo
        sa.Column("subject", sa.String(500)),
        sa.Column("body", sa.Text),
        sa.Column("body_html", sa.Text),
        sa.Column("content_data", postgresql.JSONB, default={}),
        sa.Column("template_variables", postgresql.JSONB, default={}),
        sa.Column("attachments", postgresql.JSONB, default=[]),
        # Status
        sa.Column("status", queue_status, default="pending", index=True),
        sa.Column("priority", queue_priority, default="5", index=True),
        # Agendamento
        sa.Column("scheduled_at", sa.DateTime, index=True),
        sa.Column("not_after", sa.DateTime),
        sa.Column("send_window_start", sa.String(5)),
        sa.Column("send_window_end", sa.String(5)),
        # Processamento
        sa.Column("enqueued_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("processing_started_at", sa.DateTime),
        sa.Column("sent_at", sa.DateTime),
        sa.Column("delivered_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("processing_time_ms", sa.Integer),
        # Retry
        sa.Column("attempt", sa.Integer, default=0),
        sa.Column("max_attempts", sa.Integer, default=3),
        sa.Column("next_retry_at", sa.DateTime),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("last_error", sa.Text),
        sa.Column("error_code", sa.String(50)),
        sa.Column("error_details", postgresql.JSONB),
        # Provider
        sa.Column("provider_message_id", sa.String(200)),
        sa.Column("provider_status", sa.String(50)),
        sa.Column("provider_response", postgresql.JSONB),
        # Tracking
        sa.Column("opened", sa.Boolean, default=False),
        sa.Column("opened_at", sa.DateTime),
        sa.Column("opened_count", sa.Integer, default=0),
        sa.Column("clicked", sa.Boolean, default=False),
        sa.Column("clicked_at", sa.DateTime),
        sa.Column("clicked_count", sa.Integer, default=0),
        sa.Column("clicked_links", postgresql.JSONB, default=[]),
        sa.Column("converted", sa.Boolean, default=False),
        sa.Column("converted_at", sa.DateTime),
        sa.Column("conversion_value", sa.Float),
        sa.Column("unsubscribed", sa.Boolean, default=False),
        sa.Column("unsubscribed_at", sa.DateTime),
        sa.Column("complained", sa.Boolean, default=False),
        sa.Column("complained_at", sa.DateTime),
        # Bounce
        sa.Column("bounced", sa.Boolean, default=False),
        sa.Column("bounced_at", sa.DateTime),
        sa.Column("bounce_type", sa.String(20)),
        sa.Column("bounce_reason", sa.Text),
        # Contexto
        sa.Column("trigger_type", sa.String(50)),
        sa.Column("trigger_id", postgresql.UUID(as_uuid=True)),
        sa.Column("source_entity_type", sa.String(100)),
        sa.Column("source_entity_id", postgresql.UUID(as_uuid=True)),
        # Categoria
        sa.Column("category", sa.String(50), index=True),
        sa.Column("tags", postgresql.JSONB, default=[]),
        # Custo
        sa.Column("cost", sa.Float, default=0.0),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("device_info", postgresql.JSONB),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_notification_queue_pending", "notification_queue", ["tenant_id", "status", "scheduled_at"])
    op.create_index("ix_notification_queue_user", "notification_queue", ["tenant_id", "user_id", "created_at"])

    # =========================================================================
    # notification_logs
    # =========================================================================
    op.create_table(
        "notification_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Referências
        sa.Column(
            "queue_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_queue.id"),
            index=True,
        ),
        sa.Column("notification_id", sa.String(50), index=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("correlation_id", sa.String(100), index=True),
        # Canal e Template
        sa.Column(
            "channel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_channels.id"),
            index=True,
        ),
        sa.Column("channel_type", sa.String(20), index=True),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notification_templates.id"),
            index=True,
        ),
        # Destinatário
        sa.Column("user_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("recipient_address", sa.String(200)),
        # Evento
        sa.Column("event_type", log_event_type, nullable=False, index=True),
        sa.Column("level", log_level, default="info", index=True),
        sa.Column("message", sa.Text),
        sa.Column("details", postgresql.JSONB, default={}),
        # Status
        sa.Column("previous_status", sa.String(30)),
        sa.Column("new_status", sa.String(30)),
        # Métricas
        sa.Column("processing_time_ms", sa.Integer),
        sa.Column("queue_wait_time_ms", sa.Integer),
        # Provider
        sa.Column("provider", sa.String(50)),
        sa.Column("provider_message_id", sa.String(200)),
        sa.Column("provider_status", sa.String(50)),
        sa.Column("provider_response", postgresql.JSONB),
        sa.Column("provider_error_code", sa.String(50)),
        sa.Column("provider_error_message", sa.Text),
        # Tracking
        sa.Column("user_agent", sa.String(500)),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("device_info", postgresql.JSONB),
        sa.Column("geo_location", postgresql.JSONB),
        sa.Column("clicked_url", sa.String(1000)),
        # Custo
        sa.Column("cost", sa.Float, default=0.0),
        # Retry
        sa.Column("attempt_number", sa.Integer),
        sa.Column("next_retry_at", sa.DateTime),
        # Contexto
        sa.Column("source_entity_type", sa.String(100)),
        sa.Column("source_entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("trigger_type", sa.String(50)),
        sa.Column("trigger_id", postgresql.UUID(as_uuid=True)),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        sa.Column("request_id", sa.String(100)),
        # Controle
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_notification_logs_notification", "notification_logs", ["notification_id", "created_at"])

    # =========================================================================
    # notification_metrics
    # =========================================================================
    op.create_table(
        "notification_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Período
        sa.Column("period_type", sa.String(20), nullable=False, index=True),
        sa.Column("period_start", sa.DateTime, nullable=False, index=True),
        sa.Column("period_end", sa.DateTime, nullable=False),
        # Dimensões
        sa.Column("channel_type", sa.String(20), index=True),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("category", sa.String(50), index=True),
        # Contadores envio
        sa.Column("total_queued", sa.Integer, default=0),
        sa.Column("total_sent", sa.Integer, default=0),
        sa.Column("total_delivered", sa.Integer, default=0),
        sa.Column("total_failed", sa.Integer, default=0),
        sa.Column("total_bounced", sa.Integer, default=0),
        sa.Column("total_cancelled", sa.Integer, default=0),
        sa.Column("total_expired", sa.Integer, default=0),
        # Contadores interação
        sa.Column("total_opened", sa.Integer, default=0),
        sa.Column("unique_opens", sa.Integer, default=0),
        sa.Column("total_clicked", sa.Integer, default=0),
        sa.Column("unique_clicks", sa.Integer, default=0),
        sa.Column("total_converted", sa.Integer, default=0),
        sa.Column("total_replied", sa.Integer, default=0),
        # Contadores problemas
        sa.Column("total_complaints", sa.Integer, default=0),
        sa.Column("total_unsubscribes", sa.Integer, default=0),
        # Taxas
        sa.Column("delivery_rate", sa.Float),
        sa.Column("open_rate", sa.Float),
        sa.Column("click_rate", sa.Float),
        sa.Column("conversion_rate", sa.Float),
        sa.Column("bounce_rate", sa.Float),
        sa.Column("complaint_rate", sa.Float),
        sa.Column("unsubscribe_rate", sa.Float),
        # Tempo
        sa.Column("avg_queue_time", sa.Float),
        sa.Column("avg_delivery_time", sa.Float),
        sa.Column("p50_delivery_time", sa.Float),
        sa.Column("p95_delivery_time", sa.Float),
        sa.Column("p99_delivery_time", sa.Float),
        # Custos
        sa.Column("total_cost", sa.Float, default=0.0),
        sa.Column("avg_cost_per_message", sa.Float),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index(
        "ix_notification_metrics_period",
        "notification_metrics",
        ["tenant_id", "period_type", "period_start", "channel_type"],
    )


def downgrade() -> None:
    """Drop Notification Hub tables."""
    # Drop tables
    op.drop_table("notification_metrics")
    op.drop_table("notification_logs")
    op.drop_table("notification_queue")
    op.drop_table("notification_subscriptions")
    op.drop_table("notification_preferences")
    op.drop_table("notification_templates")
    op.drop_table("notification_channels")

    # Drop ENUMs
    op.execute("DROP TYPE IF EXISTS loglevel")
    op.execute("DROP TYPE IF EXISTS logeventtype")
    op.execute("DROP TYPE IF EXISTS queuepriority")
    op.execute("DROP TYPE IF EXISTS queuestatus")
    op.execute("DROP TYPE IF EXISTS digesttype")
    op.execute("DROP TYPE IF EXISTS frequencytype")
    op.execute("DROP TYPE IF EXISTS templatecategory")
    op.execute("DROP TYPE IF EXISTS templatestatus")
    op.execute("DROP TYPE IF EXISTS channelprovider")
    op.execute("DROP TYPE IF EXISTS channelstatus")
    op.execute("DROP TYPE IF EXISTS channeltype")
