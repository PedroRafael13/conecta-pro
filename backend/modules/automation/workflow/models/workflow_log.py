"""Workflow Log Model - Logs de Execucao.

Sprint 33 - Workflow Engine (Unificado).
"""

import enum
from datetime import datetime

from sqlalchemy import (
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


class LogLevel(str, enum.Enum):
    """Nivel do log."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(str, enum.Enum):
    """Tipo de log."""

    # Execucao
    EXECUTION_STARTED = "EXECUTION_STARTED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_PAUSED = "EXECUTION_PAUSED"
    EXECUTION_RESUMED = "EXECUTION_RESUMED"
    EXECUTION_CANCELLED = "EXECUTION_CANCELLED"
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"

    # Steps
    STEP_STARTED = "STEP_STARTED"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"
    STEP_SKIPPED = "STEP_SKIPPED"
    STEP_RETRIED = "STEP_RETRIED"

    # Condicoes
    CONDITION_EVALUATED = "CONDITION_EVALUATED"
    CONDITION_TRUE = "CONDITION_TRUE"
    CONDITION_FALSE = "CONDITION_FALSE"

    # Acoes
    ACTION_EMAIL_SENT = "ACTION_EMAIL_SENT"
    ACTION_WHATSAPP_SENT = "ACTION_WHATSAPP_SENT"
    ACTION_SMS_SENT = "ACTION_SMS_SENT"
    ACTION_WEBHOOK_CALLED = "ACTION_WEBHOOK_CALLED"
    ACTION_TASK_CREATED = "ACTION_TASK_CREATED"
    ACTION_RECORD_UPDATED = "ACTION_RECORD_UPDATED"
    ACTION_RECORD_CREATED = "ACTION_RECORD_CREATED"

    # Espera
    WAIT_STARTED = "WAIT_STARTED"
    WAIT_COMPLETED = "WAIT_COMPLETED"
    WAIT_APPROVAL_REQUESTED = "WAIT_APPROVAL_REQUESTED"
    WAIT_APPROVAL_RECEIVED = "WAIT_APPROVAL_RECEIVED"
    WAIT_APPROVAL_REJECTED = "WAIT_APPROVAL_REJECTED"

    # Erros
    ERROR_OCCURRED = "ERROR_OCCURRED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"

    # Debug
    DEBUG_INFO = "DEBUG_INFO"
    VARIABLE_SET = "VARIABLE_SET"


class WorkflowLog(Base):
    """Log de execucao de workflow."""

    __tablename__ = "execution_logs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relacionamento com Execution
    execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relacionamento com Step (opcional)
    step_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    step_name = Column(String(100), nullable=True)

    # Relacionamento com StepExecution (opcional)
    step_execution_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Action relacionada (opcional)
    action_id = Column(UUID(as_uuid=True), nullable=True)

    # Log info
    level = Column(
        Enum(LogLevel, name="loglevel", create_type=True),
        nullable=False,
        default=LogLevel.INFO,
    )
    log_type = Column(
        Enum(LogType, name="logtype", create_type=True),
        nullable=False,
    )

    # Mensagem
    message = Column(Text, nullable=False)

    # Dados adicionais
    # Ex: {"input": {...}, "output": {...}, "duration_ms": 150}
    data = Column(JSONB, nullable=True)

    # Error details
    error_type = Column(String(100), nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Timing
    duration_ms = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    execution = relationship("WorkflowExecution", back_populates="logs")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowLog {self.log_type.value} ({self.level.value})>"

    @property
    def is_error(self) -> bool:
        """Verifica se e erro."""
        return self.level in (LogLevel.ERROR, LogLevel.CRITICAL)

    @property
    def is_step_log(self) -> bool:
        """Verifica se e log de step."""
        return self.step_id is not None

    @classmethod
    def create_info(
        cls,
        tenant_id: str,
        execution_id: str,
        log_type: LogType,
        message: str,
        step_id: str | None = None,
        step_name: str | None = None,
        data: dict | None = None,
        duration_ms: int | None = None,
    ) -> "WorkflowLog":
        """Cria log de info.

        Args:
            tenant_id: ID do tenant.
            execution_id: ID da execucao.
            log_type: Tipo do log.
            message: Mensagem.
            step_id: ID do step.
            step_name: Nome do step.
            data: Dados adicionais.
            duration_ms: Duracao em ms.

        Returns:
            Novo log.
        """
        return cls(
            tenant_id=tenant_id,
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            level=LogLevel.INFO,
            log_type=log_type,
            message=message,
            data=data,
            duration_ms=duration_ms,
        )

    @classmethod
    def create_error(
        cls,
        tenant_id: str,
        execution_id: str,
        log_type: LogType,
        message: str,
        error_type: str | None = None,
        error_traceback: str | None = None,
        step_id: str | None = None,
        step_name: str | None = None,
        data: dict | None = None,
    ) -> "WorkflowLog":
        """Cria log de erro.

        Args:
            tenant_id: ID do tenant.
            execution_id: ID da execucao.
            log_type: Tipo do log.
            message: Mensagem.
            error_type: Tipo do erro.
            error_traceback: Traceback.
            step_id: ID do step.
            step_name: Nome do step.
            data: Dados adicionais.

        Returns:
            Novo log.
        """
        return cls(
            tenant_id=tenant_id,
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            level=LogLevel.ERROR,
            log_type=log_type,
            message=message,
            error_type=error_type,
            error_traceback=error_traceback,
            data=data,
        )

    @classmethod
    def create_debug(
        cls,
        tenant_id: str,
        execution_id: str,
        message: str,
        data: dict | None = None,
        step_id: str | None = None,
        step_name: str | None = None,
    ) -> "WorkflowLog":
        """Cria log de debug.

        Args:
            tenant_id: ID do tenant.
            execution_id: ID da execucao.
            message: Mensagem.
            data: Dados adicionais.
            step_id: ID do step.
            step_name: Nome do step.

        Returns:
            Novo log.
        """
        return cls(
            tenant_id=tenant_id,
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            level=LogLevel.DEBUG,
            log_type=LogType.DEBUG_INFO,
            message=message,
            data=data,
        )

    @classmethod
    def step_started(
        cls,
        tenant_id: str,
        execution_id: str,
        step_id: str,
        step_name: str,
        input_data: dict | None = None,
    ) -> "WorkflowLog":
        """Cria log de step iniciado.

        Args:
            tenant_id: ID do tenant.
            execution_id: ID da execucao.
            step_id: ID do step.
            step_name: Nome do step.
            input_data: Dados de entrada.

        Returns:
            Novo log.
        """
        return cls.create_info(
            tenant_id=tenant_id,
            execution_id=execution_id,
            log_type=LogType.STEP_STARTED,
            message=f"Step '{step_name}' started",
            step_id=step_id,
            step_name=step_name,
            data={"input": input_data} if input_data else None,
        )

    @classmethod
    def step_completed(
        cls,
        tenant_id: str,
        execution_id: str,
        step_id: str,
        step_name: str,
        output_data: dict | None = None,
        duration_ms: int | None = None,
    ) -> "WorkflowLog":
        """Cria log de step completado.

        Args:
            tenant_id: ID do tenant.
            execution_id: ID da execucao.
            step_id: ID do step.
            step_name: Nome do step.
            output_data: Dados de saida.
            duration_ms: Duracao em ms.

        Returns:
            Novo log.
        """
        return cls.create_info(
            tenant_id=tenant_id,
            execution_id=execution_id,
            log_type=LogType.STEP_COMPLETED,
            message=f"Step '{step_name}' completed",
            step_id=step_id,
            step_name=step_name,
            data={"output": output_data} if output_data else None,
            duration_ms=duration_ms,
        )

    @classmethod
    def step_failed(
        cls,
        tenant_id: str,
        execution_id: str,
        step_id: str,
        step_name: str,
        error_message: str,
        error_type: str | None = None,
        error_traceback: str | None = None,
    ) -> "WorkflowLog":
        """Cria log de step falho.

        Args:
            tenant_id: ID do tenant.
            execution_id: ID da execucao.
            step_id: ID do step.
            step_name: Nome do step.
            error_message: Mensagem de erro.
            error_type: Tipo do erro.
            error_traceback: Traceback.

        Returns:
            Novo log.
        """
        return cls.create_error(
            tenant_id=tenant_id,
            execution_id=execution_id,
            log_type=LogType.STEP_FAILED,
            message=f"Step '{step_name}' failed: {error_message}",
            error_type=error_type,
            error_traceback=error_traceback,
            step_id=step_id,
            step_name=step_name,
        )
