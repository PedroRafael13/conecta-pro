"""Sprint 07 - Workflow Automation Engine

Revision ID: sprint07_workflow
Revises: sprint06_document
Create Date: 2026-01-07

Cria tabelas para o motor de automacao de workflows:
- workflows: Fluxos de automacao
- workflow_steps: Passos do workflow
- workflow_triggers: Gatilhos
- workflow_actions: Acoes executaveis
- workflow_conditions: Condicoes logicas
- workflow_executions: Historico de execucoes
- step_executions: Execucao de steps
- execution_logs: Logs de execucao
- scheduled_jobs: Jobs agendados
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "sprint07_workflow"
down_revision = "sprint06_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================
    # Tabela: workflows
    # ========================
    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(50), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("category", sa.String(50), default="custom"),
        sa.Column("tags", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("status", sa.String(20), default="draft"),
        sa.Column("priority", sa.String(20), default="normal"),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("run_once", sa.Boolean, default=False),
        sa.Column("max_executions", sa.Integer),
        sa.Column("timeout_seconds", sa.Integer, default=3600),
        sa.Column("retry_count", sa.Integer, default=3),
        sa.Column("retry_delay_seconds", sa.Integer, default=60),
        sa.Column("variables", postgresql.JSONB, default=[]),
        sa.Column("input_schema", postgresql.JSONB, default={}),
        sa.Column("output_schema", postgresql.JSONB, default={}),
        sa.Column("canvas_data", postgresql.JSONB, default={}),
        sa.Column("version", sa.Integer, default=1),
        sa.Column("parent_workflow_id", postgresql.UUID(as_uuid=True)),
        sa.Column("execution_count", sa.Integer, default=0),
        sa.Column("success_count", sa.Integer, default=0),
        sa.Column("failure_count", sa.Integer, default=0),
        sa.Column("avg_execution_time_ms", sa.Float, default=0),
        sa.Column("last_executed_at", sa.DateTime),
        sa.Column("last_success_at", sa.DateTime),
        sa.Column("last_failure_at", sa.DateTime),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("created_by", sa.String(50)),
        sa.Column("updated_by", sa.String(50)),
    )

    op.create_index("ix_workflows_tenant_status", "workflows", ["tenant_id", "status"])
    op.create_index("ix_workflows_category", "workflows", ["category"])

    # ========================
    # Tabela: workflow_steps
    # ========================
    op.create_table(
        "workflow_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("step_type", sa.String(30), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True)),
        sa.Column("condition_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subprocess_workflow_id", postgresql.UUID(as_uuid=True)),
        sa.Column("next_step_ids", postgresql.ARRAY(postgresql.UUID), default=[]),
        sa.Column("connections", postgresql.JSONB, default=[]),
        sa.Column("loop_collection", sa.String(200)),
        sa.Column("loop_variable", sa.String(50), default="item"),
        sa.Column("loop_index_variable", sa.String(50), default="index"),
        sa.Column("max_iterations", sa.Integer, default=1000),
        sa.Column("parallel_step_ids", postgresql.ARRAY(postgresql.UUID), default=[]),
        sa.Column("wait_for_all", sa.Boolean, default=True),
        sa.Column("delay_seconds", sa.Integer, default=0),
        sa.Column("delay_until", sa.DateTime),
        sa.Column("delay_expression", sa.String(200)),
        sa.Column("on_error", sa.String(20), default="fail"),
        sa.Column("error_handler_step_id", postgresql.UUID(as_uuid=True)),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("retry_delay_seconds", sa.Integer, default=30),
        sa.Column("timeout_seconds", sa.Integer, default=300),
        sa.Column("input_mapping", postgresql.JSONB, default={}),
        sa.Column("output_mapping", postgresql.JSONB, default={}),
        sa.Column("position_x", sa.Float, default=0),
        sa.Column("position_y", sa.Float, default=0),
        sa.Column("position_width", sa.Float, default=200),
        sa.Column("position_height", sa.Float, default=80),
        sa.Column("icon", sa.String(50)),
        sa.Column("color", sa.String(20)),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("order_num", sa.Integer, default=0),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_workflow_steps_workflow", "workflow_steps", ["workflow_id"])

    # ========================
    # Tabela: workflow_triggers
    # ========================
    op.create_table(
        "workflow_triggers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("trigger_type", sa.String(30), nullable=False),
        sa.Column("event", sa.String(50)),
        sa.Column("custom_event", sa.String(100)),
        sa.Column("schedule_config", postgresql.JSONB),
        sa.Column("webhook_config", postgresql.JSONB),
        sa.Column("data_change_config", postgresql.JSONB),
        sa.Column("filter_expression", sa.Text),
        sa.Column("filter_conditions", postgresql.JSONB, default={}),
        sa.Column("input_schema", postgresql.JSONB, default={}),
        sa.Column("input_mapping", postgresql.JSONB, default={}),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("last_triggered_at", sa.DateTime),
        sa.Column("trigger_count", sa.Integer, default=0),
        sa.Column("cooldown_seconds", sa.Integer, default=0),
        sa.Column("max_concurrent", sa.Integer, default=1),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_workflow_triggers_workflow", "workflow_triggers", ["workflow_id"])
    op.create_index("ix_workflow_triggers_type", "workflow_triggers", ["trigger_type"])
    op.create_index("ix_workflow_triggers_event", "workflow_triggers", ["event"])

    # ========================
    # Tabela: workflow_actions
    # ========================
    op.create_table(
        "workflow_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(50), index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("config", postgresql.JSONB, default={}),
        sa.Column("email_config", postgresql.JSONB),
        sa.Column("whatsapp_config", postgresql.JSONB),
        sa.Column("http_config", postgresql.JSONB),
        sa.Column("data_config", postgresql.JSONB),
        sa.Column("task_config", postgresql.JSONB),
        sa.Column("input_schema", postgresql.JSONB, default={}),
        sa.Column("output_schema", postgresql.JSONB, default={}),
        sa.Column("input_mapping", postgresql.JSONB, default={}),
        sa.Column("output_mapping", postgresql.JSONB, default={}),
        sa.Column("message_template", sa.Text),
        sa.Column("template_engine", sa.String(20), default="jinja2"),
        sa.Column("custom_script", sa.Text),
        sa.Column("script_language", sa.String(20), default="python"),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("is_builtin", sa.Boolean, default=False),
        sa.Column("execution_count", sa.Integer, default=0),
        sa.Column("success_count", sa.Integer, default=0),
        sa.Column("failure_count", sa.Integer, default=0),
        sa.Column("avg_execution_time_ms", sa.Float, default=0),
        sa.Column("icon", sa.String(50)),
        sa.Column("color", sa.String(20)),
        sa.Column("category", sa.String(50)),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_workflow_actions_type", "workflow_actions", ["action_type"])

    # ========================
    # Tabela: workflow_conditions
    # ========================
    op.create_table(
        "workflow_conditions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.String(50), index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("condition_type", sa.String(30), nullable=False),
        sa.Column("simple_condition", postgresql.JSONB),
        sa.Column("condition_group", postgresql.JSONB),
        sa.Column("expression", sa.Text),
        sa.Column("script", sa.Text),
        sa.Column("script_language", sa.String(20), default="python"),
        sa.Column("function_name", sa.String(100)),
        sa.Column("function_params", postgresql.JSONB, default={}),
        sa.Column("true_step_id", postgresql.UUID(as_uuid=True)),
        sa.Column("false_step_id", postgresql.UUID(as_uuid=True)),
        sa.Column("branches", postgresql.JSONB, default={}),
        sa.Column("is_enabled", sa.Boolean, default=True),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # ========================
    # Tabela: workflow_executions
    # ========================
    op.create_table(
        "workflow_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("workflow_name", sa.String(100)),
        sa.Column("workflow_version", sa.Integer),
        sa.Column("tenant_id", sa.String(50), nullable=False, index=True),
        sa.Column("trigger_id", postgresql.UUID(as_uuid=True)),
        sa.Column("trigger_type", sa.String(30)),
        sa.Column("triggered_by", sa.String(100)),
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("priority", sa.String(20), default="normal"),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("duration_ms", sa.Float, default=0),
        sa.Column("timeout_at", sa.DateTime),
        sa.Column("input_data", postgresql.JSONB, default={}),
        sa.Column("output_data", postgresql.JSONB, default={}),
        sa.Column("variables", postgresql.JSONB, default={}),
        sa.Column("context", postgresql.JSONB, default={}),
        sa.Column("current_step_id", postgresql.UUID(as_uuid=True)),
        sa.Column("completed_steps", postgresql.ARRAY(postgresql.UUID), default=[]),
        sa.Column("success", sa.Boolean, default=False),
        sa.Column("error", sa.Text),
        sa.Column("error_step_id", postgresql.UUID(as_uuid=True)),
        sa.Column("error_details", postgresql.JSONB, default={}),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("max_retries", sa.Integer, default=3),
        sa.Column("parent_execution_id", postgresql.UUID(as_uuid=True)),
        sa.Column("steps_total", sa.Integer, default=0),
        sa.Column("steps_completed", sa.Integer, default=0),
        sa.Column("steps_failed", sa.Integer, default=0),
        sa.Column("steps_skipped", sa.Integer, default=0),
        sa.Column("metadata", postgresql.JSONB, default={}),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_workflow_executions_workflow", "workflow_executions", ["workflow_id"])
    op.create_index("ix_workflow_executions_status", "workflow_executions", ["status"])
    op.create_index("ix_workflow_executions_created", "workflow_executions", ["created_at"])

    # ========================
    # Tabela: step_executions
    # ========================
    op.create_table(
        "step_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_name", sa.String(100)),
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("duration_ms", sa.Float, default=0),
        sa.Column("input_data", postgresql.JSONB, default={}),
        sa.Column("output_data", postgresql.JSONB, default={}),
        sa.Column("success", sa.Boolean, default=False),
        sa.Column("error", sa.Text),
        sa.Column("error_details", postgresql.JSONB, default={}),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("max_retries", sa.Integer, default=3),
        sa.Column("iteration", sa.Integer, default=0),
        sa.Column("loop_item", postgresql.JSONB),
    )

    op.create_index("ix_step_executions_execution", "step_executions", ["execution_id"])

    # ========================
    # Tabela: execution_logs
    # ========================
    op.create_table(
        "execution_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_id", postgresql.UUID(as_uuid=True)),
        sa.Column("action_id", postgresql.UUID(as_uuid=True)),
        sa.Column("level", sa.String(20), default="info"),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("data", postgresql.JSONB, default={}),
        sa.Column("error", sa.Text),
        sa.Column("stack_trace", sa.Text),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index("ix_execution_logs_execution", "execution_logs", ["execution_id"])
    op.create_index("ix_execution_logs_level", "execution_logs", ["level"])

    # ========================
    # Tabela: scheduled_jobs
    # ========================
    op.create_table(
        "scheduled_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trigger_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("workflow_triggers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_at", sa.DateTime, nullable=False, index=True),
        sa.Column("input_data", postgresql.JSONB, default={}),
        sa.Column("recurring", sa.Boolean, default=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True)),
        sa.Column("error", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("executed_at", sa.DateTime),
    )

    op.create_index("ix_scheduled_jobs_status", "scheduled_jobs", ["status"])
    op.create_index("ix_scheduled_jobs_trigger", "scheduled_jobs", ["trigger_id"])


def downgrade() -> None:
    op.drop_table("scheduled_jobs")
    op.drop_table("execution_logs")
    op.drop_table("step_executions")
    op.drop_table("workflow_executions")
    op.drop_table("workflow_conditions")
    op.drop_table("workflow_actions")
    op.drop_table("workflow_triggers")
    op.drop_table("workflow_steps")
    op.drop_table("workflows")
