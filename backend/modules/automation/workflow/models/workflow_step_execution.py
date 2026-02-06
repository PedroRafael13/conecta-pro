"""Workflow Step Execution Model - Execucao de Steps.

Sprint 33 - Workflow Engine (Unificado).
"""

import enum
from datetime import datetime
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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class StepExecutionStatus(str, enum.Enum):
    """Status da execucao do step."""

    PENDING = "PENDING"  # Pendente
    RUNNING = "RUNNING"  # Executando
    COMPLETED = "COMPLETED"  # Completado
    FAILED = "FAILED"  # Falhou
    SKIPPED = "SKIPPED"  # Pulado
    WAITING = "WAITING"  # Aguardando
    CANCELLED = "CANCELLED"  # Cancelado
    RETRYING = "RETRYING"  # Retentando
    TIMEOUT = "TIMEOUT"  # Timeout


class WorkflowStepExecution(Base):
    """Execucao de um step do workflow."""

    __tablename__ = "step_executions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Relacionamento com Execution
    execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relacionamento com Step
    step_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_steps.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    step_name = Column(String(100), nullable=True)  # Cache do nome

    # Ordem de execucao
    execution_order = Column(Integer, default=0, nullable=False)

    # Status
    status = Column(
        Enum(StepExecutionStatus, name="stepexecutionstatus", create_type=True),
        nullable=False,
        default=StepExecutionStatus.PENDING,
    )

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, default=0, nullable=False)

    # Input/Output
    # Ex input: {"email": "user@example.com", "subject": "Hello"}
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)

    # Resultado
    success = Column(Boolean, default=False, nullable=False)
    error = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)

    # Retries
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    # Loop (se step esta em um loop)
    iteration = Column(Integer, default=0, nullable=False)
    loop_item = Column(JSONB, nullable=True)  # Item atual do loop

    # Action executada (se aplicavel)
    action_id = Column(UUID(as_uuid=True), nullable=True)
    action_type = Column(String(50), nullable=True)

    # Condicao avaliada (se aplicavel)
    condition_result = Column(Boolean, nullable=True)
    condition_details = Column(JSONB, nullable=True)

    # Metadados
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Relationships
    execution = relationship(
        "WorkflowExecution",
        back_populates="step_executions",
    )
    step = relationship("WorkflowStep", lazy="joined")
    logs = relationship(
        "WorkflowLog",
        primaryjoin="WorkflowStepExecution.id == foreign(WorkflowLog.step_execution_id)",
        lazy="selectin",
        order_by="WorkflowLog.created_at",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowStepExecution {self.step_name} ({self.status.value})>"

    @property
    def is_running(self) -> bool:
        """Verifica se esta executando."""
        return self.status == StepExecutionStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Verifica se completou."""
        return self.status == StepExecutionStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Verifica se falhou."""
        return self.status in (StepExecutionStatus.FAILED, StepExecutionStatus.TIMEOUT)

    @property
    def is_finished(self) -> bool:
        """Verifica se terminou."""
        return self.status in (
            StepExecutionStatus.COMPLETED,
            StepExecutionStatus.FAILED,
            StepExecutionStatus.SKIPPED,
            StepExecutionStatus.CANCELLED,
            StepExecutionStatus.TIMEOUT,
        )

    @property
    def can_retry(self) -> bool:
        """Verifica se pode fazer retry."""
        return self.retry_count < self.max_retries

    def start(self) -> None:
        """Inicia execucao do step."""
        self.status = StepExecutionStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, output: dict | None = None) -> None:
        """Completa execucao com sucesso.

        Args:
            output: Dados de saida.
        """
        self.status = StepExecutionStatus.COMPLETED
        self.success = True
        self.completed_at = datetime.utcnow()
        if output:
            self.output_data = output
        self._calculate_duration()

    def fail(self, error: str, details: dict | None = None) -> None:
        """Marca execucao como falha.

        Args:
            error: Mensagem de erro.
            details: Detalhes do erro.
        """
        self.status = StepExecutionStatus.FAILED
        self.success = False
        self.error = error
        if details:
            self.error_details = details
        self.completed_at = datetime.utcnow()
        self._calculate_duration()

    def skip(self, reason: str = "") -> None:
        """Pula o step.

        Args:
            reason: Motivo.
        """
        self.status = StepExecutionStatus.SKIPPED
        self.completed_at = datetime.utcnow()
        if reason:
            self.metadata = self.metadata or {}
            self.metadata["skip_reason"] = reason

    def retry(self) -> bool:
        """Tenta retry se possivel.

        Returns:
            True se pode retentar.
        """
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = StepExecutionStatus.RETRYING
            self.error = None
            self.error_details = None
            return True
        return False

    def timeout(self) -> None:
        """Marca como timeout."""
        self.status = StepExecutionStatus.TIMEOUT
        self.success = False
        self.error = "Step execution timed out"
        self.completed_at = datetime.utcnow()
        self._calculate_duration()

    def cancel(self) -> None:
        """Cancela execucao."""
        self.status = StepExecutionStatus.CANCELLED
        self.completed_at = datetime.utcnow()

    def wait(self) -> None:
        """Marca como aguardando."""
        self.status = StepExecutionStatus.WAITING

    def set_input(self, key: str, value: Any) -> None:
        """Define valor de input.

        Args:
            key: Chave.
            value: Valor.
        """
        if self.input_data is None:
            self.input_data = {}
        self.input_data[key] = value

    def get_input(self, key: str, default: Any = None) -> Any:
        """Obtem valor de input.

        Args:
            key: Chave.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        if self.input_data:
            return self.input_data.get(key, default)
        return default

    def set_output(self, key: str, value: Any) -> None:
        """Define valor de output.

        Args:
            key: Chave.
            value: Valor.
        """
        if self.output_data is None:
            self.output_data = {}
        self.output_data[key] = value

    def get_output(self, key: str, default: Any = None) -> Any:
        """Obtem valor de output.

        Args:
            key: Chave.
            default: Valor padrao.

        Returns:
            Valor ou default.
        """
        if self.output_data:
            return self.output_data.get(key, default)
        return default

    def _calculate_duration(self) -> None:
        """Calcula duracao."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)

    def to_dict(self) -> dict:
        """Converte para dicionario.

        Returns:
            Dados do step execution.
        """
        return {
            "id": str(self.id),
            "execution_id": str(self.execution_id),
            "step_id": str(self.step_id) if self.step_id else None,
            "step_name": self.step_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "success": self.success,
            "error": self.error,
            "retry_count": self.retry_count,
            "iteration": self.iteration,
        }
