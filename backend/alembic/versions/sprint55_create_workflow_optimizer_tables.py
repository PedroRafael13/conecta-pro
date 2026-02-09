"""Sprint 55: Create workflow optimizer tables.

Revision ID: sprint55_workflow_optimizer
Revises: sprint54_email_assistant
Create Date: 2025-01-06
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID

from alembic import op

revision = "sprint55_workflow_optimizer"
down_revision = "sprint54_email_assistant"
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
    create_enum_safe("workflow_status_enum", ["draft", "active", "paused", "archived", "disabled"])

    create_enum_safe(
        "workflow_type_enum",
        [
            "approval",
            "notification",
            "data_processing",
            "integration",
            "maintenance",
            "report",
            "alert",
            "scheduling",
            "communication",
            "financial",
            "custom",
        ],
    )

    create_enum_safe(
        "execution_status_enum",
        ["pending", "running", "completed", "failed", "cancelled", "timeout", "waiting", "paused"],
    )

    create_enum_safe("optimization_type_enum", ["performance", "cost", "reliability", "efficiency", "automation"])

    # Tabela ai_workflows
    op.create_table(
        "ai_workflows",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.String(20), server_default="'1.0.0'"),
        # Tipo
        sa.Column(
            "workflow_type",
            ENUM(
                "approval",
                "notification",
                "data_processing",
                "integration",
                "maintenance",
                "report",
                "alert",
                "scheduling",
                "communication",
                "financial",
                "custom",
                name="workflow_type_enum",
                create_type=False,
            ),
            server_default="custom",
        ),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", ARRAY(sa.String), server_default="{}"),
        # Status
        sa.Column(
            "status",
            ENUM("draft", "active", "paused", "archived", "disabled", name="workflow_status_enum", create_type=False),
            server_default="draft",
        ),
        # Configuracao
        sa.Column("trigger_config", JSONB, server_default="{}"),
        sa.Column("steps", JSONB, server_default="[]"),
        sa.Column("variables", JSONB, server_default="{}"),
        sa.Column("settings", JSONB, server_default="{}"),
        # IA
        sa.Column("is_ai_optimized", sa.Boolean, server_default="false"),
        sa.Column("ai_suggestions", JSONB, server_default="[]"),
        sa.Column("optimization_score", sa.Float, server_default="0.0"),
        sa.Column("last_optimization", sa.DateTime, nullable=True),
        # Estatisticas
        sa.Column("execution_count", sa.Integer, server_default="0"),
        sa.Column("success_count", sa.Integer, server_default="0"),
        sa.Column("failure_count", sa.Integer, server_default="0"),
        sa.Column("avg_execution_time", sa.Float, server_default="0.0"),
        sa.Column("total_execution_time", sa.Float, server_default="0.0"),
        sa.Column("success_rate", sa.Float, server_default="0.0"),
        sa.Column("efficiency_score", sa.Float, server_default="0.0"),
        # Limites
        sa.Column("max_concurrent", sa.Integer, server_default="1"),
        sa.Column("timeout_seconds", sa.Integer, server_default="300"),
        sa.Column("retry_count", sa.Integer, server_default="3"),
        sa.Column("retry_delay", sa.Integer, server_default="60"),
        # Relacionamentos
        sa.Column("condominio_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("owner_id", UUID(as_uuid=True), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_run_at", sa.DateTime, nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
    )

    # Indices
    op.create_index("ix_ai_workflows_code", "ai_workflows", ["code"])
    op.create_index("ix_ai_workflows_status", "ai_workflows", ["status"])
    op.create_index("ix_ai_workflows_type", "ai_workflows", ["workflow_type"])
    op.create_index("ix_ai_workflows_condominio_id", "ai_workflows", ["condominio_id"])

    # Tabela ai_workflow_executions
    op.create_table(
        "ai_workflow_executions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Status
        sa.Column(
            "status",
            ENUM(
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
                "timeout",
                "waiting",
                "paused",
                name="execution_status_enum",
                create_type=False,
            ),
            server_default="pending",
        ),
        # Progresso
        sa.Column("current_step", sa.Integer, server_default="0"),
        sa.Column("total_steps", sa.Integer, server_default="0"),
        sa.Column("progress_percent", sa.Float, server_default="0.0"),
        # Input/Output
        sa.Column("input_data", JSONB, server_default="{}"),
        sa.Column("output_data", JSONB, server_default="{}"),
        sa.Column("context", JSONB, server_default="{}"),
        # Logs
        sa.Column("logs", JSONB, server_default="[]"),
        sa.Column("step_results", JSONB, server_default="{}"),
        # Erro
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_step", sa.String(100), nullable=True),
        sa.Column("error_details", JSONB, server_default="{}"),
        # Tempo
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("execution_time_ms", sa.Integer, server_default="0"),
        # Trigger
        sa.Column("trigger_type", sa.String(50), nullable=True),
        sa.Column("trigger_data", JSONB, server_default="{}"),
        sa.Column("triggered_by", UUID(as_uuid=True), nullable=True),
        # Retry
        sa.Column("retry_attempt", sa.Integer, server_default="0"),
        sa.Column("parent_execution_id", UUID(as_uuid=True), nullable=True),
        # Relacionamentos
        sa.Column(
            "workflow_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index(
        "ix_ai_workflow_executions_workflow_id",
        "ai_workflow_executions",
        ["workflow_id"],
    )
    op.create_index(
        "ix_ai_workflow_executions_status",
        "ai_workflow_executions",
        ["status"],
    )
    op.create_index(
        "ix_ai_workflow_executions_created_at",
        "ai_workflow_executions",
        ["created_at"],
    )

    # ENUM para tipo de template (evita conflito)
    create_enum_safe(
        "workflow_type_enum_template",
        [
            "approval",
            "notification",
            "data_processing",
            "integration",
            "maintenance",
            "report",
            "alert",
            "scheduling",
            "communication",
            "financial",
            "custom",
        ],
    )

    # Tabela ai_workflow_templates
    op.create_table(
        "ai_workflow_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Identificacao
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.String(20), server_default="'1.0.0'"),
        # Tipo
        sa.Column(
            "workflow_type",
            ENUM(
                "approval",
                "notification",
                "data_processing",
                "integration",
                "maintenance",
                "report",
                "alert",
                "scheduling",
                "communication",
                "financial",
                "custom",
                name="workflow_type_enum_template",
                create_type=False,
            ),
            server_default="custom",
        ),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("tags", ARRAY(sa.String), server_default="{}"),
        # Definicao
        sa.Column("trigger_template", JSONB, server_default="{}"),
        sa.Column("steps_template", JSONB, server_default="[]"),
        sa.Column("variables_template", JSONB, server_default="{}"),
        sa.Column("settings_template", JSONB, server_default="{}"),
        # Parametros
        sa.Column("required_params", JSONB, server_default="[]"),
        sa.Column("optional_params", JSONB, server_default="[]"),
        # IA
        sa.Column("ai_recommended", sa.Boolean, server_default="false"),
        sa.Column("use_cases", ARRAY(sa.String), server_default="{}"),
        sa.Column("complexity", sa.String(20), server_default="'medium'"),
        # Estatisticas
        sa.Column("usage_count", sa.Integer, server_default="0"),
        sa.Column("avg_rating", sa.Float, server_default="0.0"),
        sa.Column("total_ratings", sa.Integer, server_default="0"),
        # Config
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_premium", sa.Boolean, server_default="false"),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true", nullable=False),
    )

    op.create_index("ix_ai_workflow_templates_code", "ai_workflow_templates", ["code"])
    op.create_index("ix_ai_workflow_templates_type", "ai_workflow_templates", ["workflow_type"])

    # Tabela ai_workflow_optimizations
    op.create_table(
        "ai_workflow_optimizations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Tipo
        sa.Column(
            "optimization_type",
            ENUM(
                "performance",
                "cost",
                "reliability",
                "efficiency",
                "automation",
                name="optimization_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        # Sugestao
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("suggestion", sa.Text, nullable=False),
        # Impacto
        sa.Column("estimated_improvement", sa.Float, server_default="0.0"),
        sa.Column("confidence", sa.Float, server_default="0.0"),
        sa.Column("priority", sa.Integer, server_default="0"),
        # Detalhes
        sa.Column("current_state", JSONB, server_default="{}"),
        sa.Column("proposed_state", JSONB, server_default="{}"),
        sa.Column("changes", JSONB, server_default="[]"),
        # Analise
        sa.Column("analysis_data", JSONB, server_default="{}"),
        sa.Column("metrics_before", JSONB, server_default="{}"),
        sa.Column("metrics_after", JSONB, server_default="{}"),
        # Status
        sa.Column("status", sa.String(50), server_default="'pending'"),
        sa.Column("applied_at", sa.DateTime, nullable=True),
        sa.Column("applied_by", UUID(as_uuid=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Resultado
        sa.Column("actual_improvement", sa.Float, nullable=True),
        # Relacionamentos
        sa.Column(
            "workflow_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=True),
    )

    op.create_index(
        "ix_ai_workflow_optimizations_workflow_id",
        "ai_workflow_optimizations",
        ["workflow_id"],
    )
    op.create_index(
        "ix_ai_workflow_optimizations_status",
        "ai_workflow_optimizations",
        ["status"],
    )

    # Tabela ai_workflow_metrics
    op.create_table(
        "ai_workflow_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        # Periodo
        sa.Column("period_type", sa.String(20), nullable=False),
        sa.Column("period_start", sa.DateTime, nullable=False),
        sa.Column("period_end", sa.DateTime, nullable=False),
        # Contadores
        sa.Column("executions_total", sa.Integer, server_default="0"),
        sa.Column("executions_success", sa.Integer, server_default="0"),
        sa.Column("executions_failed", sa.Integer, server_default="0"),
        sa.Column("executions_cancelled", sa.Integer, server_default="0"),
        # Tempo
        sa.Column("total_execution_time_ms", sa.Integer, server_default="0"),
        sa.Column("avg_execution_time_ms", sa.Float, server_default="0.0"),
        sa.Column("min_execution_time_ms", sa.Integer, server_default="0"),
        sa.Column("max_execution_time_ms", sa.Integer, server_default="0"),
        sa.Column("p95_execution_time_ms", sa.Integer, server_default="0"),
        # Performance
        sa.Column("success_rate", sa.Float, server_default="0.0"),
        sa.Column("failure_rate", sa.Float, server_default="0.0"),
        sa.Column("throughput", sa.Float, server_default="0.0"),
        # Erros
        sa.Column("errors_by_type", JSONB, server_default="{}"),
        sa.Column("errors_by_step", JSONB, server_default="{}"),
        # Custos
        sa.Column("estimated_cost", sa.Float, server_default="0.0"),
        sa.Column("estimated_savings", sa.Float, server_default="0.0"),
        # Relacionamentos
        sa.Column(
            "workflow_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Auditoria
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index(
        "ix_ai_workflow_metrics_workflow_id",
        "ai_workflow_metrics",
        ["workflow_id"],
    )
    op.create_index(
        "ix_ai_workflow_metrics_period",
        "ai_workflow_metrics",
        ["period_type", "period_start"],
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table("ai_workflow_metrics")
    op.drop_table("ai_workflow_optimizations")
    op.drop_table("ai_workflow_templates")
    op.drop_table("ai_workflow_executions")
    op.drop_table("ai_workflows")

    # Drop ENUMs
    op.execute("DROP TYPE IF EXISTS workflow_type_enum_template")
    op.execute("DROP TYPE IF EXISTS optimization_type_enum")
    op.execute("DROP TYPE IF EXISTS execution_status_enum")
    op.execute("DROP TYPE IF EXISTS workflow_type_enum")
    op.execute("DROP TYPE IF EXISTS workflow_status_enum")
