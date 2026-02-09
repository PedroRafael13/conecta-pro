"""Sprint 33 - Workflow Engine Unified

Revision ID: sprint33_workflow
Revises: sprint33_audit
Create Date: 2026-01-07

Adiciona campos extras aos modelos de workflow unificados:
- Campos de controle e estatisticas
- Suporte a execucao detalhada de steps
- Campos de metadados e configuracao expandidos
"""

import contextlib

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "sprint33_workflow"
down_revision = "sprint33_audit"
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    """Verifica se uma coluna existe em uma tabela."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def add_column_safe(table_name: str, column: sa.Column):
    """Adiciona coluna apenas se tabela existe e coluna não existe."""
    if table_exists(table_name) and not column_exists(table_name, column.name):
        op.add_column(table_name, column)


def upgrade() -> None:
    # ==================== workflows ====================
    add_column_safe("workflows", sa.Column("slug", sa.String(100), nullable=True))
    add_column_safe("workflows", sa.Column("context_variables", postgresql.ARRAY(sa.String), nullable=True))
    add_column_safe("workflows", sa.Column("versions_history", postgresql.JSONB, nullable=True))
    add_column_safe("workflows", sa.Column("is_system", sa.Boolean, server_default="false"))
    add_column_safe("workflows", sa.Column("is_template", sa.Boolean, server_default="false"))
    add_column_safe("workflows", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    add_column_safe("workflows", sa.Column("active", sa.Boolean, server_default="true"))

    # ==================== workflow_steps ====================
    add_column_safe("workflow_steps", sa.Column("config", postgresql.JSONB, server_default="{}"))
    add_column_safe("workflow_steps", sa.Column("position", postgresql.JSONB, nullable=True))
    add_column_safe("workflow_steps", sa.Column("entry_condition", postgresql.JSONB, nullable=True))
    add_column_safe("workflow_steps", sa.Column("active", sa.Boolean, server_default="true"))
    add_column_safe("workflow_steps", sa.Column("is_start", sa.Boolean, server_default="false"))
    add_column_safe("workflow_steps", sa.Column("is_end", sa.Boolean, server_default="false"))
    add_column_safe("workflow_steps", sa.Column("continue_on_error", sa.Boolean, server_default="false"))

    # ==================== workflow_triggers ====================
    add_column_safe("workflow_triggers", sa.Column("status", sa.String(20), server_default="ACTIVE"))
    add_column_safe("workflow_triggers", sa.Column("config", postgresql.JSONB, server_default="{}"))
    add_column_safe("workflow_triggers", sa.Column("filters", postgresql.JSONB, nullable=True))
    add_column_safe("workflow_triggers", sa.Column("max_executions", sa.Integer, nullable=True))
    add_column_safe("workflow_triggers", sa.Column("current_executions", sa.Integer, server_default="0"))
    add_column_safe("workflow_triggers", sa.Column("priority", sa.Integer, server_default="0"))
    add_column_safe("workflow_triggers", sa.Column("active", sa.Boolean, server_default="true"))
    add_column_safe("workflow_triggers", sa.Column("once_per_entity", sa.Boolean, server_default="false"))
    add_column_safe("workflow_triggers", sa.Column("next_scheduled_at", sa.DateTime(timezone=True), nullable=True))
    add_column_safe("workflow_triggers", sa.Column("last_error", sa.Text, nullable=True))
    add_column_safe("workflow_triggers", sa.Column("error_count", sa.Integer, server_default="0"))

    # ==================== workflow_actions ====================
    add_column_safe("workflow_actions", sa.Column("type_config", postgresql.JSONB, nullable=True))

    # ==================== workflow_executions ====================
    add_column_safe("workflow_executions", sa.Column("current_step_name", sa.String(100), nullable=True))
    add_column_safe("workflow_executions", sa.Column("current_step_index", sa.Integer, server_default="0"))
    add_column_safe(
        "workflow_executions", sa.Column("completed_step_ids", postgresql.ARRAY(postgresql.UUID), nullable=True)
    )
    add_column_safe("workflow_executions", sa.Column("is_test", sa.Boolean, server_default="false"))
    add_column_safe("workflow_executions", sa.Column("is_retry", sa.Boolean, server_default="false"))
    add_column_safe("workflow_executions", sa.Column("is_scheduled", sa.Boolean, server_default="false"))
    add_column_safe("workflow_executions", sa.Column("paused_at", sa.DateTime(timezone=True), nullable=True))
    add_column_safe("workflow_executions", sa.Column("initiated_by", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_safe("workflow_executions", sa.Column("execution_time_ms", sa.Integer, nullable=True))
    add_column_safe("workflow_executions", sa.Column("result", postgresql.JSONB, nullable=True))

    # ==================== step_executions ====================
    add_column_safe("step_executions", sa.Column("execution_order", sa.Integer, server_default="0"))
    add_column_safe("step_executions", sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_safe("step_executions", sa.Column("action_type", sa.String(50), nullable=True))
    add_column_safe("step_executions", sa.Column("condition_result", sa.Boolean, nullable=True))
    add_column_safe("step_executions", sa.Column("condition_details", postgresql.JSONB, nullable=True))
    add_column_safe("step_executions", sa.Column("metadata", postgresql.JSONB, nullable=True))

    # ==================== execution_logs ====================
    add_column_safe("execution_logs", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_safe("execution_logs", sa.Column("step_name", sa.String(100), nullable=True))
    add_column_safe("execution_logs", sa.Column("step_execution_id", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_safe("execution_logs", sa.Column("log_type", sa.String(50), nullable=True))
    add_column_safe("execution_logs", sa.Column("error_type", sa.String(100), nullable=True))
    add_column_safe("execution_logs", sa.Column("error_traceback", sa.Text, nullable=True))
    add_column_safe("execution_logs", sa.Column("duration_ms", sa.Integer, nullable=True))
    add_column_safe("execution_logs", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))

    # Criar indices adicionais (apenas se tabelas existem)
    if table_exists("execution_logs"):
        with contextlib.suppress(Exception):
            op.create_index("ix_execution_logs_step_execution", "execution_logs", ["step_execution_id"])
        with contextlib.suppress(Exception):
            op.create_index("ix_execution_logs_tenant", "execution_logs", ["tenant_id"])
    if table_exists("step_executions"):
        with contextlib.suppress(Exception):
            op.create_index("ix_step_executions_step", "step_executions", ["step_id"])


def downgrade() -> None:
    # Remove indices
    op.drop_index("ix_step_executions_step", table_name="step_executions", if_exists=True)
    op.drop_index("ix_execution_logs_tenant", table_name="execution_logs", if_exists=True)
    op.drop_index("ix_execution_logs_step_execution", table_name="execution_logs", if_exists=True)

    # Nota: Nao remove colunas no downgrade para evitar perda de dados
    # As colunas adicionadas sao opcionais e nao quebram a compatibilidade
    pass
