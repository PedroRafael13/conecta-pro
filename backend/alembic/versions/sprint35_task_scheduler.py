"""Sprint 35 - Task Scheduler.

Revision ID: sprint35_scheduler
Revises: sprint34_ai_predictions
Create Date: 2026-01-05

Módulo de agendamento de tarefas com:
- Tarefas agendadas (cron, interval, once, event, dependency)
- Fila de tarefas com prioridades
- Workers distribuídos
- Locks para evitar duplicação
- Histórico de execuções
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint35_scheduler"
down_revision: Union[str, None] = "sprint34_ai_predictions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create scheduler tables."""
    # Criar ENUMs
    task_status_enum = postgresql.ENUM(
        "draft", "active", "paused", "disabled", "completed", "failed", "expired",
        name="task_status",
        create_type=False,
    )
    task_status_enum.create(op.get_bind(), checkfirst=True)

    task_type_enum = postgresql.ENUM(
        "cron", "interval", "once", "event", "dependency", "manual",
        name="task_type",
        create_type=False,
    )
    task_type_enum.create(op.get_bind(), checkfirst=True)

    task_category_enum = postgresql.ENUM(
        "system", "backup", "cleanup", "sync", "report", "notification",
        "ai", "integration", "maintenance", "workflow", "custom",
        name="task_category",
        create_type=False,
    )
    task_category_enum.create(op.get_bind(), checkfirst=True)

    execution_status_enum = postgresql.ENUM(
        "pending", "queued", "running", "success", "failed",
        "timeout", "cancelled", "skipped", "retry",
        name="execution_status",
        create_type=False,
    )
    execution_status_enum.create(op.get_bind(), checkfirst=True)

    queue_status_enum = postgresql.ENUM(
        "pending", "claimed", "processing", "completed",
        "failed", "dead", "cancelled", "deferred",
        name="queue_status",
        create_type=False,
    )
    queue_status_enum.create(op.get_bind(), checkfirst=True)

    queue_priority_enum = postgresql.ENUM(
        "critical", "high", "normal", "low", "background",
        name="queue_priority",
        create_type=False,
    )
    queue_priority_enum.create(op.get_bind(), checkfirst=True)

    worker_status_enum = postgresql.ENUM(
        "starting", "idle", "busy", "paused", "draining",
        "stopping", "stopped", "offline", "error",
        name="worker_status",
        create_type=False,
    )
    worker_status_enum.create(op.get_bind(), checkfirst=True)

    lock_status_enum = postgresql.ENUM(
        "acquired", "released", "expired", "stolen",
        name="lock_status",
        create_type=False,
    )
    lock_status_enum.create(op.get_bind(), checkfirst=True)

    # Tabela: scheduler_tasks
    op.create_table(
        "scheduler_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificação
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, index=True),
        sa.Column("description", sa.Text),
        # Classificação
        sa.Column("task_type", task_type_enum, nullable=False, server_default="cron"),
        sa.Column("category", task_category_enum, nullable=False, server_default="custom"),
        sa.Column("status", task_status_enum, nullable=False, server_default="draft"),
        # Agendamento
        sa.Column("cron_expression", sa.String(100)),
        sa.Column("timezone", sa.String(50), server_default="America/Sao_Paulo"),
        sa.Column("interval_seconds", sa.Integer),
        sa.Column("interval_type", sa.String(20)),
        sa.Column("scheduled_at", sa.DateTime),
        sa.Column("depends_on_task_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_tasks.id")),
        sa.Column("dependency_condition", sa.String(20)),
        sa.Column("valid_from", sa.DateTime),
        sa.Column("valid_until", sa.DateTime),
        # Handler
        sa.Column("handler", sa.String(200), nullable=False),
        sa.Column("handler_module", sa.String(200)),
        sa.Column("handler_args", postgresql.JSONB, server_default="{}"),
        sa.Column("handler_kwargs", postgresql.JSONB, server_default="{}"),
        # Config
        sa.Column("timeout_seconds", sa.Integer, server_default="3600"),
        sa.Column("max_retries", sa.Integer, server_default="3"),
        sa.Column("retry_delay_seconds", sa.Integer, server_default="60"),
        sa.Column("retry_backoff_multiplier", sa.Float, server_default="2.0"),
        sa.Column("max_concurrent", sa.Integer, server_default="1"),
        sa.Column("allow_overlap", sa.Boolean, server_default="false"),
        sa.Column("priority", sa.Integer, server_default="5"),
        sa.Column("queue_name", sa.String(100), server_default="'default'"),
        sa.Column("memory_limit_mb", sa.Integer),
        sa.Column("cpu_limit", sa.Float),
        # Notificações
        sa.Column("notify_on_success", sa.Boolean, server_default="false"),
        sa.Column("notify_on_failure", sa.Boolean, server_default="true"),
        sa.Column("notify_on_retry", sa.Boolean, server_default="false"),
        sa.Column("notify_emails", postgresql.ARRAY(sa.String)),
        sa.Column("notify_webhook", sa.String(500)),
        # Métricas
        sa.Column("total_executions", sa.Integer, server_default="0"),
        sa.Column("successful_executions", sa.Integer, server_default="0"),
        sa.Column("failed_executions", sa.Integer, server_default="0"),
        sa.Column("avg_duration_seconds", sa.Float),
        sa.Column("last_duration_seconds", sa.Float),
        sa.Column("last_run_at", sa.DateTime),
        sa.Column("last_success_at", sa.DateTime),
        sa.Column("last_failure_at", sa.DateTime),
        sa.Column("next_run_at", sa.DateTime),
        # Metadados
        sa.Column("tags", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
        # Auditoria
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("active", sa.Boolean, server_default="true"),
    )

    # Tabela: scheduler_workers
    op.create_table(
        "scheduler_workers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("worker_id", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("hostname", sa.String(200), nullable=False),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("pid", sa.Integer),
        sa.Column("process_name", sa.String(100)),
        sa.Column("status", worker_status_enum, nullable=False, server_default="starting"),
        sa.Column("queues", postgresql.ARRAY(sa.String), server_default="{'default'}"),
        sa.Column("concurrency", sa.Integer, server_default="4"),
        sa.Column("prefetch_count", sa.Integer, server_default="1"),
        sa.Column("categories", postgresql.ARRAY(sa.String)),
        sa.Column("tags", postgresql.ARRAY(sa.String)),
        sa.Column("max_memory_mb", sa.Integer),
        sa.Column("max_tasks_per_hour", sa.Integer),
        # Recursos
        sa.Column("cpu_count", sa.Integer),
        sa.Column("cpu_percent", sa.Float),
        sa.Column("memory_total_mb", sa.Float),
        sa.Column("memory_used_mb", sa.Float),
        sa.Column("memory_percent", sa.Float),
        sa.Column("disk_total_gb", sa.Float),
        sa.Column("disk_used_gb", sa.Float),
        sa.Column("disk_percent", sa.Float),
        sa.Column("load_average", postgresql.ARRAY(sa.Float)),
        # Métricas
        sa.Column("total_tasks_processed", sa.Integer, server_default="0"),
        sa.Column("tasks_succeeded", sa.Integer, server_default="0"),
        sa.Column("tasks_failed", sa.Integer, server_default="0"),
        sa.Column("tasks_in_progress", sa.Integer, server_default="0"),
        sa.Column("avg_task_duration_seconds", sa.Float),
        sa.Column("tasks_this_hour", sa.Integer, server_default="0"),
        sa.Column("tasks_today", sa.Integer, server_default="0"),
        sa.Column("hour_reset_at", sa.DateTime),
        sa.Column("day_reset_at", sa.DateTime),
        # Heartbeat
        sa.Column("heartbeat_interval_seconds", sa.Integer, server_default="30"),
        sa.Column("last_heartbeat_at", sa.DateTime),
        sa.Column("heartbeat_missed_count", sa.Integer, server_default="0"),
        sa.Column("max_missed_heartbeats", sa.Integer, server_default="3"),
        # Versão
        sa.Column("version", sa.String(50)),
        sa.Column("python_version", sa.String(20)),
        sa.Column("platform", sa.String(100)),
        # Timing
        sa.Column("started_at", sa.DateTime),
        sa.Column("last_task_at", sa.DateTime),
        sa.Column("last_idle_at", sa.DateTime),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
        sa.Column("labels", postgresql.JSONB, server_default="{}"),
        sa.Column("registered_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("active", sa.Boolean, server_default="true"),
    )

    # Tabela: scheduler_executions
    op.create_table(
        "scheduler_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_tasks.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("execution_number", sa.Integer, nullable=False),
        sa.Column("run_id", sa.String(50), unique=True, index=True),
        sa.Column("status", execution_status_enum, nullable=False, server_default="pending"),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_workers.id")),
        sa.Column("worker_hostname", sa.String(200)),
        sa.Column("worker_pid", sa.Integer),
        # Timing
        sa.Column("scheduled_at", sa.DateTime),
        sa.Column("queued_at", sa.DateTime),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("duration_seconds", sa.Float),
        # Retries
        sa.Column("attempt_number", sa.Integer, server_default="1"),
        sa.Column("max_attempts", sa.Integer, server_default="3"),
        sa.Column("retry_at", sa.DateTime),
        sa.Column("retry_count", sa.Integer, server_default="0"),
        # I/O
        sa.Column("input_args", postgresql.JSONB),
        sa.Column("input_kwargs", postgresql.JSONB),
        sa.Column("output_result", postgresql.JSONB),
        sa.Column("output_artifacts", postgresql.JSONB),
        # Erro
        sa.Column("error_type", sa.String(200)),
        sa.Column("error_message", sa.Text),
        sa.Column("error_traceback", sa.Text),
        sa.Column("error_code", sa.String(50)),
        # Recursos
        sa.Column("memory_used_mb", sa.Float),
        sa.Column("cpu_used_percent", sa.Float),
        sa.Column("disk_read_mb", sa.Float),
        sa.Column("disk_write_mb", sa.Float),
        # Logs
        sa.Column("log_output", sa.Text),
        sa.Column("log_level", sa.String(20)),
        sa.Column("log_lines_count", sa.Integer),
        # Progresso
        sa.Column("progress_percent", sa.Float, server_default="0"),
        sa.Column("progress_message", sa.String(500)),
        sa.Column("progress_data", postgresql.JSONB),
        # Trigger
        sa.Column("trigger_type", sa.String(50)),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True)),
        sa.Column("trigger_event", sa.String(200)),
        # Metadados
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("checkpoint_data", postgresql.JSONB),
        sa.Column("checkpoint_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Tabela: scheduler_execution_logs
    op.create_table(
        "scheduler_execution_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_executions.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now(), index=True),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("logger_name", sa.String(200)),
        sa.Column("context", postgresql.JSONB),
        sa.Column("extra_data", postgresql.JSONB),
        sa.Column("exc_info", sa.Text),
    )

    # Tabela: scheduler_queue
    op.create_table(
        "scheduler_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("queue_name", sa.String(100), nullable=False, index=True,
                  server_default="'default'"),
        sa.Column("message_id", sa.String(100), unique=True, index=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_tasks.id")),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_executions.id")),
        sa.Column("status", queue_status_enum, nullable=False, index=True,
                  server_default="pending"),
        sa.Column("priority", queue_priority_enum, nullable=False,
                  server_default="normal"),
        sa.Column("priority_value", sa.Integer, server_default="5", index=True),
        sa.Column("handler", sa.String(200), nullable=False),
        sa.Column("handler_module", sa.String(200)),
        sa.Column("payload", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("headers", postgresql.JSONB, server_default="{}"),
        # Agendamento
        sa.Column("scheduled_at", sa.DateTime, index=True),
        sa.Column("not_before", sa.DateTime),
        sa.Column("not_after", sa.DateTime),
        # Retry
        sa.Column("attempt", sa.Integer, server_default="0"),
        sa.Column("max_attempts", sa.Integer, server_default="3"),
        sa.Column("retry_at", sa.DateTime),
        sa.Column("retry_delay_seconds", sa.Integer, server_default="60"),
        sa.Column("retry_backoff", sa.Float, server_default="2.0"),
        # Timeout
        sa.Column("timeout_seconds", sa.Integer, server_default="3600"),
        sa.Column("visibility_timeout_seconds", sa.Integer, server_default="300"),
        # Claim
        sa.Column("claimed_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_workers.id")),
        sa.Column("claimed_at", sa.DateTime),
        sa.Column("claim_expires_at", sa.DateTime),
        # Timing
        sa.Column("enqueued_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("processing_time_ms", sa.Integer),
        # Resultado
        sa.Column("result", postgresql.JSONB),
        sa.Column("error_message", sa.Text),
        sa.Column("error_code", sa.String(50)),
        # Agrupamento
        sa.Column("group_id", sa.String(100), index=True),
        sa.Column("correlation_id", sa.String(100), index=True),
        sa.Column("deduplication_id", sa.String(200), index=True),
        sa.Column("deduplication_scope", sa.String(50), server_default="'queue'"),
        # Metadados
        sa.Column("source", sa.String(100)),
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Tabela: scheduler_locks
    op.create_table(
        "scheduler_locks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("lock_key", sa.String(500), nullable=False, index=True),
        sa.Column("lock_name", sa.String(200)),
        sa.Column("status", lock_status_enum, nullable=False, server_default="acquired"),
        sa.Column("owner_id", sa.String(200), nullable=False),
        sa.Column("owner_hostname", sa.String(200)),
        sa.Column("owner_pid", sa.Integer),
        sa.Column("task_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_tasks.id")),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_executions.id")),
        sa.Column("acquired_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("ttl_seconds", sa.Integer, server_default="3600"),
        sa.Column("released_at", sa.DateTime),
        sa.Column("renew_count", sa.Integer, server_default="0"),
        sa.Column("last_renewed_at", sa.DateTime),
        sa.Column("max_renewals", sa.Integer, server_default="10"),
        sa.Column("auto_renew", sa.Boolean, server_default="false"),
        sa.Column("waiters_count", sa.Integer, server_default="0"),
        sa.Column("max_waiters", sa.Integer, server_default="100"),
        sa.Column("reason", sa.String(500)),
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Tabela: scheduler_lock_waiters
    op.create_table(
        "scheduler_lock_waiters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lock_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("scheduler_locks.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("waiter_id", sa.String(200), nullable=False),
        sa.Column("waiter_hostname", sa.String(200)),
        sa.Column("waiter_pid", sa.Integer),
        sa.Column("priority", sa.Integer, server_default="5"),
        sa.Column("position", sa.Integer),
        sa.Column("waiting_since", sa.DateTime, server_default=sa.func.now()),
        sa.Column("timeout_at", sa.DateTime),
        sa.Column("notified_at", sa.DateTime),
        sa.Column("acquired", sa.Boolean, server_default="false"),
        sa.Column("cancelled", sa.Boolean, server_default="false"),
        sa.Column("timed_out", sa.Boolean, server_default="false"),
        sa.Column("extra_data", postgresql.JSONB, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Índices compostos
    op.create_index(
        "ix_scheduler_tasks_tenant_status",
        "scheduler_tasks",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_scheduler_tasks_next_run",
        "scheduler_tasks",
        ["status", "next_run_at"],
    )
    op.create_index(
        "ix_scheduler_executions_task_status",
        "scheduler_executions",
        ["task_id", "status"],
    )
    op.create_index(
        "ix_scheduler_queue_available",
        "scheduler_queue",
        ["queue_name", "status", "priority_value", "enqueued_at"],
    )
    op.create_index(
        "ix_scheduler_locks_active",
        "scheduler_locks",
        ["tenant_id", "lock_key", "status"],
    )


def downgrade() -> None:
    """Drop scheduler tables."""
    op.drop_table("scheduler_lock_waiters")
    op.drop_table("scheduler_locks")
    op.drop_table("scheduler_queue")
    op.drop_table("scheduler_execution_logs")
    op.drop_table("scheduler_executions")
    op.drop_table("scheduler_workers")
    op.drop_table("scheduler_tasks")

    # Drop ENUMs
    op.execute("DROP TYPE IF EXISTS lock_status")
    op.execute("DROP TYPE IF EXISTS worker_status")
    op.execute("DROP TYPE IF EXISTS queue_priority")
    op.execute("DROP TYPE IF EXISTS queue_status")
    op.execute("DROP TYPE IF EXISTS execution_status")
    op.execute("DROP TYPE IF EXISTS task_category")
    op.execute("DROP TYPE IF EXISTS task_type")
    op.execute("DROP TYPE IF EXISTS task_status")
