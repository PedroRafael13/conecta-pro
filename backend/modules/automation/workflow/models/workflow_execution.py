"""Workflow Execution Model - Execucoes de Workflow.

Sprint 33 - Workflow Engine (Unificado).
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class ExecutionStatus(StrEnum):
    """Status da execucao."""

    PENDING = "PENDING"  # Pendente
    QUEUED = "QUEUED"  # Na fila
    RUNNING = "RUNNING"  # Executando
    PAUSED = "PAUSED"  # Pausada
    WAITING = "WAITING"  # Aguardando (evento/aprovacao)
    RETRYING = "RETRYING"  # Retentando
    COMPLETED = "COMPLETED"  # Completada com sucesso
    FAILED = "FAILED"  # Falhou
    CANCELLED = "CANCELLED"  # Cancelada
    TIMEOUT = "TIMEOUT"  # Timeout


class ExecutionPriority(StrEnum):
    """Prioridade de execucao."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WorkflowExecution(Base):
    """Execucao de um workflow."""

    __tablename__ = "workflow_executions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relacionamento com Workflow
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_name = Column(String(200), nullable=True)  # Cache do nome
    workflow_version = Column(Integer, default=1, nullable=False)

    # Relacionamento com Trigger (opcional)
    trigger_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_triggers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    trigger_type = Column(String(50), nullable=True)  # Cache do tipo

    # Status e Prioridade
    status = Column(
        Enum(ExecutionStatus, name="executionstatus", create_type=True),
        nullable=False,
        default=ExecutionStatus.PENDING,
        index=True,
    )
    priority = Column(
        Enum(ExecutionPriority, name="executionpriority", create_type=True),
        nullable=False,
        default=ExecutionPriority.NORMAL,
    )

    # Dados de entrada/saída
    # Ex input: {"lead_id": "...", "amount": 1000}
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)

    # Contexto da execucao (runtime)
    # Ex: {"lead_id": "...", "user_id": "...", "trigger_data": {...}}
    context = Column(JSONB, nullable=True)

    # Variaveis de execucao
    # Ex: {"total_enviados": 5, "ultimo_status": "ok"}
    variables = Column(JSONB, nullable=True)

    # Resultado final
    # Ex: {"success": true, "output": {...}, "steps_executed": 5}
    result = Column(JSONB, nullable=True)

    # Step atual
    current_step_id = Column(UUID(as_uuid=True), nullable=True)
    current_step_name = Column(String(100), nullable=True)
    current_step_index = Column(Integer, default=0, nullable=True)

    # Lista de steps completados
    completed_step_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Contadores de steps
    steps_total = Column(Integer, default=0, nullable=False)
    steps_completed = Column(Integer, default=0, nullable=False)
    steps_failed = Column(Integer, default=0, nullable=False)
    steps_skipped = Column(Integer, default=0, nullable=False)

    # Retries
    retries = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    # Tempo de execucao
    execution_time_ms = Column(Integer, nullable=True)

    # Sucesso
    success = Column(Boolean, default=False, nullable=False)

    # Erro (se falhou)
    error_message = Column(Text, nullable=True)
    error_step_id = Column(UUID(as_uuid=True), nullable=True)
    error_details = Column(JSONB, nullable=True)

    # Flags
    is_test = Column(Boolean, default=False, nullable=False)
    is_retry = Column(Boolean, default=False, nullable=False)
    is_scheduled = Column(Boolean, default=False, nullable=False)

    # Execucao pai (para sub-workflows ou retries)
    parent_execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    paused_at = Column(DateTime(timezone=True), nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)

    # Quem iniciou
    initiated_by = Column(UUID(as_uuid=True), nullable=True)
    triggered_by = Column(String(100), nullable=True)  # "user:<id>" ou "system" ou "schedule"

    # Metadados
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Relationships
    workflow = relationship("Workflow", lazy="joined")
    trigger = relationship("WorkflowTrigger", lazy="joined")
    logs = relationship(
        "WorkflowLog",
        back_populates="execution",
        lazy="selectin",
        order_by="WorkflowLog.created_at",
    )
    step_executions = relationship(
        "WorkflowStepExecution",
        back_populates="execution",
        lazy="selectin",
        order_by="WorkflowStepExecution.started_at",
    )
    child_executions = relationship(
        "WorkflowExecution",
        backref="parent_execution",
        remote_side="WorkflowExecution.id",
        lazy="select",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowExecution {self.id} ({self.status.value})>"

    @property
    def is_running(self) -> bool:
        """Verifica se esta executando."""
        return self.status == ExecutionStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Verifica se esta completada."""
        return self.status == ExecutionStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Verifica se falhou."""
        return self.status in (ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT)

    @property
    def is_finished(self) -> bool:
        """Verifica se esta finalizada."""
        return self.status in (
            ExecutionStatus.COMPLETED,
            ExecutionStatus.FAILED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.TIMEOUT,
        )

    @property
    def duration_seconds(self) -> float | None:
        """Retorna duracao em segundos."""
        if self.execution_time_ms:
            return self.execution_time_ms / 1000
        return None

    def start(self) -> None:
        """Inicia a execucao."""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, result: dict | None = None) -> None:
        """Marca como completada.

        Args:
            result: Resultado da execucao.
        """
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow()

        if result:
            self.result = result

        # Calcula tempo de execucao
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)

    def fail(self, error_message: str, step_id: str | None = None) -> None:
        """Marca como falha.

        Args:
            error_message: Mensagem de erro.
            step_id: ID do step que falhou.
        """
        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message

        if step_id:
            self.error_step_id = step_id

        self.steps_failed = (self.steps_failed or 0) + 1

        # Calcula tempo de execucao
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.execution_time_ms = int(delta.total_seconds() * 1000)

    def pause(self) -> None:
        """Pausa a execucao."""
        self.status = ExecutionStatus.PAUSED
        self.paused_at = datetime.utcnow()

    def resume(self) -> None:
        """Retoma a execucao."""
        if self.status == ExecutionStatus.PAUSED:
            self.status = ExecutionStatus.RUNNING
            self.paused_at = None

    def wait_for_event(self) -> None:
        """Marca como aguardando evento."""
        self.status = ExecutionStatus.WAITING

    def cancel(self) -> None:
        """Cancela a execucao."""
        self.status = ExecutionStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    def timeout(self) -> None:
        """Marca como timeout."""
        self.status = ExecutionStatus.TIMEOUT
        self.completed_at = datetime.utcnow()
        self.error_message = "Execution timed out"

    def advance_step(
        self,
        step_id: str,
        step_name: str,
    ) -> None:
        """Avanca para proximo step.

        Args:
            step_id: ID do step.
            step_name: Nome do step.
        """
        self.current_step_id = step_id
        self.current_step_name = step_name
        self.steps_executed = (self.steps_executed or 0) + 1

    def set_context(self, key: str, value: any) -> None:
        """Define valor no contexto.

        Args:
            key: Chave.
            value: Valor.
        """
        if self.context is None:
            self.context = {}
        self.context[key] = value

    def get_context(self, key: str, default: any = None) -> any:
        """Retorna valor do contexto.

        Args:
            key: Chave.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        if self.context:
            return self.context.get(key, default)
        return default

    def increment_retry(self) -> None:
        """Incrementa contador de retries."""
        self.retries = (self.retries or 0) + 1
        self.is_retry = True

    @property
    def progress_percent(self) -> float:
        """Percentual de progresso."""
        if not self.steps_total:
            return 0.0
        return (self.steps_completed / self.steps_total) * 100

    @property
    def can_retry(self) -> bool:
        """Verifica se pode fazer retry."""
        return self.retries < self.max_retries

    @property
    def is_timed_out(self) -> bool:
        """Verifica se expirou."""
        if not self.timeout_at:
            return False
        return datetime.utcnow() > self.timeout_at

    def set_variable(self, name: str, value: Any) -> None:
        """Define variavel de execucao.

        Args:
            name: Nome da variavel.
            value: Valor.
        """
        if self.variables is None:
            self.variables = {}
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Obtem variavel de execucao.

        Args:
            name: Nome da variavel.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        if self.variables:
            return self.variables.get(name, default)
        return default

    def mark_step_completed(self, step_id: str) -> None:
        """Marca step como completado.

        Args:
            step_id: ID do step.
        """
        if self.completed_step_ids is None:
            self.completed_step_ids = []
        if step_id not in [str(s) for s in self.completed_step_ids]:
            self.completed_step_ids.append(step_id)
        self.steps_completed = (self.steps_completed or 0) + 1

    def mark_step_failed(self) -> None:
        """Marca que um step falhou."""
        self.steps_failed = (self.steps_failed or 0) + 1

    def mark_step_skipped(self) -> None:
        """Marca que um step foi pulado."""
        self.steps_skipped = (self.steps_skipped or 0) + 1

    def update_stats(self) -> None:
        """Atualiza estatisticas baseado nos step_executions."""
        if not self.step_executions:
            return

        from .workflow_step_execution import StepExecutionStatus

        self.steps_completed = sum(1 for s in self.step_executions if s.status == StepExecutionStatus.COMPLETED)
        self.steps_failed = sum(1 for s in self.step_executions if s.status == StepExecutionStatus.FAILED)
        self.steps_skipped = sum(1 for s in self.step_executions if s.status == StepExecutionStatus.SKIPPED)

    def get_execution_summary(self) -> dict:
        """Retorna resumo da execucao.

        Returns:
            Dicionario com resumo.
        """
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "success": self.success,
            "progress_percent": self.progress_percent,
            "steps_total": self.steps_total,
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "steps_skipped": self.steps_skipped,
            "execution_time_ms": self.execution_time_ms,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error_message,
        }
