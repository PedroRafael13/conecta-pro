"""
ReportExecution Model - Histórico de execuções.

Registra cada execução de geração de relatório com métricas e status.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ExecutionStatusEnum(StrEnum):
    """Status da execução."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COLLECTING_DATA = "collecting_data"
    PROCESSING = "processing"
    GENERATING_INSIGHTS = "generating_insights"
    RENDERING = "rendering"
    EXPORTING = "exporting"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionTriggerEnum(StrEnum):
    """Gatilho da execução."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"
    EVENT = "event"
    RETRY = "retry"


class ReportExecution(Base):
    """Model de execução de relatório."""

    __tablename__ = "ai_report_executions"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_number = Column(Integer, nullable=False)

    # Referências
    report_id = Column(UUID(as_uuid=True), ForeignKey("ai_reports.id"), nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_templates.id"), nullable=True)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_schedules.id"), nullable=True)
    schedule = relationship("AIReportSchedule", back_populates="executions")

    # Status
    status = Column(
        SQLEnum(ExecutionStatusEnum, name="execution_status_enum"), nullable=False, default=ExecutionStatusEnum.PENDING
    )
    progress = Column(Float, default=0.0)  # 0-100
    current_step = Column(String(100), nullable=True)

    # Gatilho
    trigger = Column(
        SQLEnum(ExecutionTriggerEnum, name="execution_trigger_enum"),
        nullable=False,
        default=ExecutionTriggerEnum.MANUAL,
    )
    triggered_by = Column(UUID(as_uuid=True), nullable=True)

    # Parâmetros da execução
    parameters = Column(JSONB, default=dict)
    filters = Column(JSONB, default=dict)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)

    # Formatos solicitados
    requested_formats = Column(JSONB, default=["pdf"])
    generated_formats = Column(JSONB, default=list)

    # Timestamps de execução
    queued_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    # Métricas de tempo (em ms)
    queue_time_ms = Column(Integer, default=0)
    data_collection_time_ms = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    insight_generation_time_ms = Column(Integer, default=0)
    rendering_time_ms = Column(Integer, default=0)
    export_time_ms = Column(Integer, default=0)
    delivery_time_ms = Column(Integer, default=0)
    total_time_ms = Column(Integer, default=0)

    # Métricas de dados
    records_processed = Column(Integer, default=0)
    data_sources_queried = Column(Integer, default=0)
    queries_executed = Column(Integer, default=0)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)

    # Métricas de IA
    insights_generated = Column(Integer, default=0)
    anomalies_detected = Column(Integer, default=0)
    recommendations_generated = Column(Integer, default=0)

    # Métricas de saída
    pages_generated = Column(Integer, default=0)
    charts_generated = Column(Integer, default=0)
    tables_generated = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)

    # Arquivos gerados
    output_files = Column(JSONB, default=list)
    storage_paths = Column(JSONB, default=dict)

    # Entrega
    delivery_status = Column(JSONB, default=dict)  # Por método de entrega
    delivered_to = Column(JSONB, default=list)
    delivery_errors = Column(JSONB, default=list)

    # Erros
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    error_details = Column(JSONB, default=dict)
    stack_trace = Column(Text, nullable=True)

    # Retry
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_after = Column(DateTime, nullable=True)
    parent_execution_id = Column(UUID(as_uuid=True), nullable=True)  # Se for retry

    # Logs
    execution_logs = Column(JSONB, default=list)
    debug_info = Column(JSONB, default=dict)

    # Recursos utilizados
    memory_used_mb = Column(Float, default=0.0)
    cpu_time_seconds = Column(Float, default=0.0)
    worker_id = Column(String(100), nullable=True)

    # Ownership
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ReportExecution(id={self.id}, status={self.status}, progress={self.progress}%)>"

    @property
    def is_running(self) -> bool:
        """Verifica se a execução está em andamento."""
        return self.status in [
            ExecutionStatusEnum.PENDING,
            ExecutionStatusEnum.QUEUED,
            ExecutionStatusEnum.RUNNING,
            ExecutionStatusEnum.COLLECTING_DATA,
            ExecutionStatusEnum.PROCESSING,
            ExecutionStatusEnum.GENERATING_INSIGHTS,
            ExecutionStatusEnum.RENDERING,
            ExecutionStatusEnum.EXPORTING,
            ExecutionStatusEnum.DELIVERING,
        ]

    @property
    def is_completed(self) -> bool:
        """Verifica se a execução foi completada com sucesso."""
        return self.status == ExecutionStatusEnum.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Verifica se a execução falhou."""
        return self.status in [
            ExecutionStatusEnum.FAILED,
            ExecutionStatusEnum.TIMEOUT,
        ]

    @property
    def can_retry(self) -> bool:
        """Verifica se pode fazer retry."""
        return self.is_failed and self.retry_count < self.max_retries

    @property
    def duration_seconds(self) -> float:
        """Duração total em segundos."""
        return self.total_time_ms / 1000 if self.total_time_ms else 0

    @property
    def cache_hit_rate(self) -> float:
        """Taxa de cache hit."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100

    def update_status(self, status: ExecutionStatusEnum, step: str = None) -> None:
        """Atualiza status e passo atual."""
        self.status = status
        if step:
            self.current_step = step
        self.updated_at = datetime.utcnow()

        # Atualiza timestamps específicos
        if status == ExecutionStatusEnum.QUEUED:
            self.queued_at = datetime.utcnow()
        elif status == ExecutionStatusEnum.RUNNING:
            self.started_at = datetime.utcnow()
        elif status == ExecutionStatusEnum.COMPLETED:
            self.completed_at = datetime.utcnow()
            self._calculate_total_time()
        elif status in [ExecutionStatusEnum.FAILED, ExecutionStatusEnum.TIMEOUT]:
            self.failed_at = datetime.utcnow()
            self._calculate_total_time()

    def update_progress(self, progress: float, step: str = None) -> None:
        """Atualiza progresso."""
        self.progress = min(100.0, max(0.0, progress))
        if step:
            self.current_step = step
        self.updated_at = datetime.utcnow()

    def add_log(self, level: str, message: str, data: dict = None) -> None:
        """Adiciona log de execução."""
        if not self.execution_logs:
            self.execution_logs = []
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
        }
        if data:
            log_entry["data"] = data
        self.execution_logs.append(log_entry)

    def set_error(self, message: str, code: str = None, details: dict = None, stack_trace: str = None) -> None:
        """Define erro da execução."""
        self.status = ExecutionStatusEnum.FAILED
        self.error_message = message
        self.error_code = code
        self.error_details = details or {}
        self.stack_trace = stack_trace
        self.failed_at = datetime.utcnow()
        self._calculate_total_time()

    def add_output_file(self, format_type: str, path: str, size_bytes: int, url: str = None) -> None:
        """Adiciona arquivo de saída."""
        if not self.output_files:
            self.output_files = []
        if not self.storage_paths:
            self.storage_paths = {}

        self.output_files.append(
            {
                "format": format_type,
                "path": path,
                "size_bytes": size_bytes,
                "url": url,
                "created_at": datetime.utcnow().isoformat(),
            }
        )
        self.storage_paths[format_type] = path

        if format_type not in self.generated_formats:
            self.generated_formats.append(format_type)

        self.file_size_bytes += size_bytes

    def record_delivery(self, method: str, recipient: str, success: bool, error: str = None) -> None:
        """Registra entrega."""
        if not self.delivery_status:
            self.delivery_status = {}
        if not self.delivered_to:
            self.delivered_to = []
        if not self.delivery_errors:
            self.delivery_errors = []

        self.delivery_status[f"{method}_{recipient}"] = {
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
        }

        if success:
            self.delivered_to.append(
                {
                    "method": method,
                    "recipient": recipient,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        else:
            self.delivery_errors.append(
                {
                    "method": method,
                    "recipient": recipient,
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def _calculate_total_time(self) -> None:
        """Calcula tempo total de execução."""
        self.total_time_ms = (
            self.queue_time_ms
            + self.data_collection_time_ms
            + self.processing_time_ms
            + self.insight_generation_time_ms
            + self.rendering_time_ms
            + self.export_time_ms
            + self.delivery_time_ms
        )

    def prepare_retry(self) -> "ReportExecution":
        """Prepara nova execução de retry."""
        return ReportExecution(
            execution_number=self.execution_number + 1,
            template_id=self.template_id,
            schedule_id=self.schedule_id,
            trigger=ExecutionTriggerEnum.RETRY,
            triggered_by=self.triggered_by,
            parameters=self.parameters,
            filters=self.filters,
            period_start=self.period_start,
            period_end=self.period_end,
            requested_formats=self.requested_formats,
            retry_count=self.retry_count + 1,
            max_retries=self.max_retries,
            parent_execution_id=self.id,
            organization_id=self.organization_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "execution_number": self.execution_number,
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "trigger": self.trigger.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "records_processed": self.records_processed,
            "insights_generated": self.insights_generated,
            "is_running": self.is_running,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed,
            "error_message": self.error_message,
            "output_files": self.output_files,
        }

    def to_summary_dict(self) -> dict[str, Any]:
        """Converte para dicionário resumido."""
        return {
            "id": str(self.id),
            "status": self.status.value,
            "progress": self.progress,
            "duration_seconds": self.duration_seconds,
            "is_completed": self.is_completed,
        }
