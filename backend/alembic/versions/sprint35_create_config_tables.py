"""Sprint 35: Create config tables

Revision ID: sprint35_config
Revises: sprint34_reports
Create Date: 2026-01-01

Módulo de Configurações e Multi-tenant:
- Tenant: Gestão de inquilinos/clientes do sistema
- TenantSettings: Configurações específicas por tenant
- SystemConfig: Configurações globais do sistema
- FeatureFlag: Feature flags com A/B testing e rollout gradual
- NotificationTemplate: Templates de notificação multicanal
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint35_config"
down_revision: str | None = "sprint34_reports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Criar tabelas do módulo config."""
    # Enum types
    op.execute("""
        CREATE TYPE tenant_status AS ENUM (
            'active', 'inactive', 'suspended', 'blocked', 'trial', 'cancelled'
        )
    """)
    op.execute("""
        CREATE TYPE tenant_plan AS ENUM (
            'free', 'basic', 'professional', 'enterprise', 'custom'
        )
    """)
    op.execute("""
        CREATE TYPE tenant_type AS ENUM (
            'company', 'individual', 'government', 'nonprofit', 'educational'
        )
    """)
    op.execute("""
        CREATE TYPE setting_category AS ENUM (
            'general', 'security', 'notifications', 'integrations',
            'appearance', 'billing', 'features', 'limits', 'custom'
        )
    """)
    op.execute("""
        CREATE TYPE setting_type AS ENUM (
            'string', 'integer', 'float', 'boolean', 'json',
            'list', 'password', 'email', 'url', 'date',
            'datetime', 'color', 'file', 'image'
        )
    """)
    op.execute("""
        CREATE TYPE config_scope AS ENUM (
            'global', 'default', 'system', 'security'
        )
    """)
    op.execute("""
        CREATE TYPE config_priority AS ENUM (
            'low', 'normal', 'high', 'critical'
        )
    """)
    op.execute("""
        CREATE TYPE flag_status AS ENUM (
            'active', 'inactive', 'scheduled', 'expired', 'testing'
        )
    """)
    op.execute("""
        CREATE TYPE flag_type AS ENUM (
            'release', 'experiment', 'operational', 'permission', 'kill_switch'
        )
    """)
    op.execute("""
        CREATE TYPE rollout_strategy AS ENUM (
            'all', 'none', 'percentage', 'gradual',
            'tenant_list', 'user_list', 'attribute_based'
        )
    """)
    op.execute("""
        CREATE TYPE notification_channel AS ENUM (
            'email', 'sms', 'push', 'whatsapp', 'slack',
            'webhook', 'in_app', 'telegram'
        )
    """)
    op.execute("""
        CREATE TYPE notification_type AS ENUM (
            'transactional', 'marketing', 'system', 'alert',
            'reminder', 'welcome', 'password_reset', 'verification'
        )
    """)
    op.execute("""
        CREATE TYPE template_status AS ENUM (
            'draft', 'active', 'inactive', 'archived', 'testing'
        )
    """)

    # Table: tenants
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(50), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("nome_fantasia", sa.String(200), nullable=True),
        sa.Column("documento", sa.String(20), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active",
                "inactive",
                "suspended",
                "blocked",
                "trial",
                "cancelled",
                name="tenant_status",
                create_type=False,
            ),
            nullable=False,
            server_default="trial",
        ),
        sa.Column(
            "plano",
            postgresql.ENUM(
                "free", "basic", "professional", "enterprise", "custom", name="tenant_plan", create_type=False
            ),
            nullable=False,
            server_default="free",
        ),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "company", "individual", "government", "nonprofit", "educational", name="tenant_type", create_type=False
            ),
            nullable=False,
            server_default="company",
        ),
        sa.Column("endereco_logradouro", sa.String(255), nullable=True),
        sa.Column("endereco_numero", sa.String(20), nullable=True),
        sa.Column("endereco_complemento", sa.String(100), nullable=True),
        sa.Column("endereco_bairro", sa.String(100), nullable=True),
        sa.Column("endereco_cidade", sa.String(100), nullable=True),
        sa.Column("endereco_estado", sa.String(2), nullable=True),
        sa.Column("endereco_cep", sa.String(10), nullable=True),
        sa.Column("endereco_pais", sa.String(50), nullable=True, server_default="Brasil"),
        sa.Column("data_inicio", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_fim_trial", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_cancelamento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("limite_usuarios", sa.Integer, nullable=False, server_default="5"),
        sa.Column("limite_storage_gb", sa.Integer, nullable=False, server_default="5"),
        sa.Column("limite_api_calls_mes", sa.Integer, nullable=False, server_default="10000"),
        sa.Column("uso_storage_bytes", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("uso_usuarios_ativos", sa.Integer, nullable=False, server_default="0"),
        sa.Column("uso_api_calls_mes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("features_habilitadas", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("modulos_habilitados", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("configuracoes", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notas", sa.Text, nullable=True),
        sa.Column("responsavel_nome", sa.String(200), nullable=True),
        sa.Column("responsavel_email", sa.String(255), nullable=True),
        sa.Column("responsavel_telefone", sa.String(20), nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
    )

    # Table: tenant_settings
    op.create_table(
        "tenant_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("chave", sa.String(100), nullable=False),
        sa.Column("valor", sa.Text, nullable=True),
        sa.Column("valor_padrao", sa.Text, nullable=True),
        sa.Column(
            "categoria",
            postgresql.ENUM(
                "general",
                "security",
                "notifications",
                "integrations",
                "appearance",
                "billing",
                "features",
                "limits",
                "custom",
                name="setting_category",
                create_type=False,
            ),
            nullable=False,
            server_default="general",
        ),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "string",
                "integer",
                "float",
                "boolean",
                "json",
                "list",
                "password",
                "email",
                "url",
                "date",
                "datetime",
                "color",
                "file",
                "image",
                name="setting_type",
                create_type=False,
            ),
            nullable=False,
            server_default="string",
        ),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("validacao", postgresql.JSONB, nullable=True),
        sa.Column("opcoes", postgresql.JSONB, nullable=True),
        sa.Column("is_sensivel", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_editavel", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_visivel", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("grupo", sa.String(100), nullable=True),
        sa.Column("icone", sa.String(50), nullable=True),
        sa.Column("historico", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.UniqueConstraint("tenant_id", "chave", name="uq_tenant_setting_key"),
    )

    # Table: system_configs
    op.create_table(
        "system_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chave", sa.String(100), nullable=False, unique=True),
        sa.Column("valor", sa.Text, nullable=True),
        sa.Column("valor_padrao", sa.Text, nullable=True),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "string",
                "integer",
                "float",
                "boolean",
                "json",
                "list",
                "password",
                "email",
                "url",
                "date",
                "datetime",
                "color",
                "file",
                "image",
                name="setting_type",
                create_type=False,
            ),
            nullable=False,
            server_default="string",
        ),
        sa.Column(
            "escopo",
            postgresql.ENUM("global", "default", "system", "security", name="config_scope", create_type=False),
            nullable=False,
            server_default="global",
        ),
        sa.Column(
            "prioridade",
            postgresql.ENUM("low", "normal", "high", "critical", name="config_priority", create_type=False),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("validacao", postgresql.JSONB, nullable=True),
        sa.Column("is_sensivel", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_editavel", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_visivel", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("requer_restart", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("permite_override", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("cache_ttl_seconds", sa.Integer, nullable=True),
        sa.Column("grupo", sa.String(100), nullable=True),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("historico", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
    )

    # Table: feature_flags
    op.create_table(
        "feature_flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(100), nullable=False, unique=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active", "inactive", "scheduled", "expired", "testing", name="flag_status", create_type=False
            ),
            nullable=False,
            server_default="inactive",
        ),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "release", "experiment", "operational", "permission", "kill_switch", name="flag_type", create_type=False
            ),
            nullable=False,
            server_default="release",
        ),
        sa.Column(
            "estrategia",
            postgresql.ENUM(
                "all",
                "none",
                "percentage",
                "gradual",
                "tenant_list",
                "user_list",
                "attribute_based",
                name="rollout_strategy",
                create_type=False,
            ),
            nullable=False,
            server_default="none",
        ),
        sa.Column("percentual", sa.Integer, nullable=False, server_default="0"),
        sa.Column("percentual_alvo", sa.Integer, nullable=True),
        sa.Column("incremento_diario", sa.Integer, nullable=True),
        sa.Column("tenants_habilitados", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("tenants_desabilitados", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("usuarios_habilitados", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("usuarios_desabilitados", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("regras_atributos", postgresql.JSONB, nullable=True),
        sa.Column("is_ab_test", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("variantes", postgresql.JSONB, nullable=True),
        sa.Column("variante_padrao", sa.String(50), nullable=True),
        sa.Column("data_inicio", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_fim", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("dependencias", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("metricas", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notas", sa.Text, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
    )

    # Table: notification_templates
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column(
            "canal",
            postgresql.ENUM(
                "email",
                "sms",
                "push",
                "whatsapp",
                "slack",
                "webhook",
                "in_app",
                "telegram",
                name="notification_channel",
                create_type=False,
            ),
            nullable=False,
            server_default="email",
        ),
        sa.Column(
            "tipo",
            postgresql.ENUM(
                "transactional",
                "marketing",
                "system",
                "alert",
                "reminder",
                "welcome",
                "password_reset",
                "verification",
                name="notification_type",
                create_type=False,
            ),
            nullable=False,
            server_default="transactional",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft", "active", "inactive", "archived", "testing", name="template_status", create_type=False
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("assunto", sa.String(500), nullable=True),
        sa.Column("corpo", sa.Text, nullable=False),
        sa.Column("corpo_html", sa.Text, nullable=True),
        sa.Column("corpo_texto", sa.Text, nullable=True),
        sa.Column("variaveis", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("variaveis_obrigatorias", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("configuracoes_canal", postgresql.JSONB, nullable=True),
        sa.Column("idioma", sa.String(10), nullable=False, server_default="'pt-BR'"),
        sa.Column(
            "prioridade",
            postgresql.ENUM("low", "normal", "high", "critical", name="config_priority", create_type=False),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("horario_silencioso_inicio", sa.Time, nullable=True),
        sa.Column("horario_silencioso_fim", sa.Time, nullable=True),
        sa.Column("respeitar_horario_silencioso", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("versao", sa.Integer, nullable=False, server_default="1"),
        sa.Column("template_pai_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metricas", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("updated_by", sa.String(100), nullable=True),
        sa.UniqueConstraint("tenant_id", "codigo", "canal", name="uq_template_tenant_code_channel"),
    )

    # Self-referential FK for template_pai_id
    op.create_foreign_key(
        "fk_template_pai",
        "notification_templates",
        "notification_templates",
        ["template_pai_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Indexes
    op.create_index("ix_tenants_status", "tenants", ["status"])
    op.create_index("ix_tenants_plano", "tenants", ["plano"])
    op.create_index("ix_tenants_documento", "tenants", ["documento"])
    op.create_index("ix_tenants_email", "tenants", ["email"])
    op.create_index("ix_tenants_ativo", "tenants", ["ativo"])

    op.create_index("ix_tenant_settings_tenant_id", "tenant_settings", ["tenant_id"])
    op.create_index("ix_tenant_settings_chave", "tenant_settings", ["chave"])
    op.create_index("ix_tenant_settings_categoria", "tenant_settings", ["categoria"])

    op.create_index("ix_system_configs_chave", "system_configs", ["chave"])
    op.create_index("ix_system_configs_escopo", "system_configs", ["escopo"])
    op.create_index("ix_system_configs_grupo", "system_configs", ["grupo"])

    op.create_index("ix_feature_flags_codigo", "feature_flags", ["codigo"])
    op.create_index("ix_feature_flags_status", "feature_flags", ["status"])
    op.create_index("ix_feature_flags_tipo", "feature_flags", ["tipo"])

    op.create_index("ix_notification_templates_tenant_id", "notification_templates", ["tenant_id"])
    op.create_index("ix_notification_templates_codigo", "notification_templates", ["codigo"])
    op.create_index("ix_notification_templates_canal", "notification_templates", ["canal"])
    op.create_index("ix_notification_templates_tipo", "notification_templates", ["tipo"])
    op.create_index("ix_notification_templates_status", "notification_templates", ["status"])


def downgrade() -> None:
    """Remover tabelas do módulo config."""
    # Drop foreign keys
    op.drop_constraint("fk_template_pai", "notification_templates", type_="foreignkey")

    # Drop indexes
    op.drop_index("ix_notification_templates_status", "notification_templates")
    op.drop_index("ix_notification_templates_tipo", "notification_templates")
    op.drop_index("ix_notification_templates_canal", "notification_templates")
    op.drop_index("ix_notification_templates_codigo", "notification_templates")
    op.drop_index("ix_notification_templates_tenant_id", "notification_templates")

    op.drop_index("ix_feature_flags_tipo", "feature_flags")
    op.drop_index("ix_feature_flags_status", "feature_flags")
    op.drop_index("ix_feature_flags_codigo", "feature_flags")

    op.drop_index("ix_system_configs_grupo", "system_configs")
    op.drop_index("ix_system_configs_escopo", "system_configs")
    op.drop_index("ix_system_configs_chave", "system_configs")

    op.drop_index("ix_tenant_settings_categoria", "tenant_settings")
    op.drop_index("ix_tenant_settings_chave", "tenant_settings")
    op.drop_index("ix_tenant_settings_tenant_id", "tenant_settings")

    op.drop_index("ix_tenants_ativo", "tenants")
    op.drop_index("ix_tenants_email", "tenants")
    op.drop_index("ix_tenants_documento", "tenants")
    op.drop_index("ix_tenants_plano", "tenants")
    op.drop_index("ix_tenants_status", "tenants")

    # Drop tables
    op.drop_table("notification_templates")
    op.drop_table("feature_flags")
    op.drop_table("system_configs")
    op.drop_table("tenant_settings")
    op.drop_table("tenants")

    # Drop enum types
    op.execute("DROP TYPE template_status")
    op.execute("DROP TYPE notification_type")
    op.execute("DROP TYPE notification_channel")
    op.execute("DROP TYPE rollout_strategy")
    op.execute("DROP TYPE flag_type")
    op.execute("DROP TYPE flag_status")
    op.execute("DROP TYPE config_priority")
    op.execute("DROP TYPE config_scope")
    op.execute("DROP TYPE setting_type")
    op.execute("DROP TYPE setting_category")
    op.execute("DROP TYPE tenant_type")
    op.execute("DROP TYPE tenant_plan")
    op.execute("DROP TYPE tenant_status")
