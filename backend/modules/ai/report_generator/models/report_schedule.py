"""
ReportSchedule Model - Agendamento de relatórios.

Permite agendar geração automática de relatórios em diferentes periodicidades.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ScheduleFrequencyEnum(str, Enum):
    """Frequência de agendamento."""

    ONCE = "once"  # Uma vez
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"  # Cron expression


class ScheduleStatusEnum(str, Enum):
    """Status do agendamento."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"  # Para agendamentos únicos
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DeliveryMethodEnum(str, Enum):
    """Método de entrega."""

    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    STORAGE = "storage"  # Apenas salva
    FTP = "ftp"
    S3 = "s3"


class AIReportSchedule(Base):
    """Model de agendamento de relatório AI."""

    __tablename__ = "ai_report_schedules"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Template
    template_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_templates.id"), nullable=False)
    template = relationship("AIReportTemplate", back_populates="schedules")

    # Status
    status = Column(
        SQLEnum(ScheduleStatusEnum, name="schedule_status_enum"),
        nullable=False,
        default=ScheduleStatusEnum.ACTIVE
    )

    # Frequência
    frequency = Column(
        SQLEnum(ScheduleFrequencyEnum, name="schedule_frequency_enum"),
        nullable=False,
        default=ScheduleFrequencyEnum.DAILY
    )
    cron_expression = Column(String(100), nullable=True)  # Para CUSTOM

    # Horário de execução
    run_time = Column(Time, nullable=True)  # Hora do dia para executar
    timezone = Column(String(50), default="America/Sao_Paulo")

    # Dias específicos
    days_of_week = Column(JSONB, default=list)  # [0-6] para WEEKLY
    days_of_month = Column(JSONB, default=list)  # [1-31] para MONTHLY
    months = Column(JSONB, default=list)  # [1-12] para YEARLY

    # Período do relatório
    period_type = Column(String(50), nullable=True)  # previous_day, previous_week, etc.
    period_offset = Column(Integer, default=0)  # Dias de offset
    custom_period_start = Column(String(100), nullable=True)  # Expression
    custom_period_end = Column(String(100), nullable=True)

    # Parâmetros
    parameters = Column(JSONB, default=dict)
    filters = Column(JSONB, default=dict)
    dynamic_parameters = Column(JSONB, default=dict)  # Calculados em runtime

    # Formato de saída
    output_formats = Column(JSONB, default=["pdf"])
    primary_format = Column(String(20), default="pdf")

    # Entrega
    delivery_methods = Column(JSONB, default=["email"])

    # Configuração de email
    email_recipients = Column(JSONB, default=list)
    email_cc = Column(JSONB, default=list)
    email_bcc = Column(JSONB, default=list)
    email_subject = Column(String(500), nullable=True)
    email_body = Column(Text, nullable=True)
    attach_report = Column(Boolean, default=True)
    include_summary_in_body = Column(Boolean, default=True)

    # Configuração de webhook
    webhook_url = Column(String(500), nullable=True)
    webhook_headers = Column(JSONB, default=dict)
    webhook_method = Column(String(10), default="POST")

    # Configuração de storage
    storage_path = Column(String(500), nullable=True)
    filename_template = Column(String(255), default="{report_name}_{date}")
    overwrite_existing = Column(Boolean, default=False)

    # Slack/Teams
    slack_channel = Column(String(100), nullable=True)
    slack_webhook = Column(String(500), nullable=True)
    teams_webhook = Column(String(500), nullable=True)

    # Controle de execução
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)

    # Estatísticas
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)

    # Limites
    max_runs = Column(Integer, nullable=True)  # Máximo de execuções (para ONCE ou limitado)
    max_consecutive_failures = Column(Integer, default=3)  # Pausa após X falhas
    retry_on_failure = Column(Boolean, default=True)
    retry_attempts = Column(Integer, default=3)
    retry_delay_minutes = Column(Integer, default=15)

    # Validade
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Notificações
    notify_on_success = Column(Boolean, default=False)
    notify_on_failure = Column(Boolean, default=True)
    notification_recipients = Column(JSONB, default=list)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)
    tags = Column(JSONB, default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    executions = relationship("ReportExecution", back_populates="schedule")

    def __repr__(self) -> str:
        return f"<AIReportSchedule(id={self.id}, name={self.name}, frequency={self.frequency})>"

    @property
    def is_due(self) -> bool:
        """Verifica se está na hora de executar."""
        if self.status != ScheduleStatusEnum.ACTIVE:
            return False
        if self.next_run_at is None:
            return False
        return datetime.utcnow() >= self.next_run_at

    @property
    def is_expired(self) -> bool:
        """Verifica se o agendamento expirou."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        if self.end_date and datetime.utcnow() > self.end_date:
            return True
        if self.max_runs and self.total_runs >= self.max_runs:
            return True
        return False

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso das execuções."""
        if self.total_runs == 0:
            return 0.0
        return (self.successful_runs / self.total_runs) * 100

    @property
    def should_pause(self) -> bool:
        """Verifica se deve pausar por falhas consecutivas."""
        return self.consecutive_failures >= self.max_consecutive_failures

    def calculate_next_run(self) -> Optional[datetime]:
        """Calcula próxima execução baseada na frequência."""
        now = datetime.utcnow()

        if self.is_expired:
            return None

        if self.frequency == ScheduleFrequencyEnum.ONCE:
            if self.total_runs > 0:
                return None
            return self.start_date or now

        if self.frequency == ScheduleFrequencyEnum.HOURLY:
            next_run = now + timedelta(hours=1)
            return next_run.replace(minute=0, second=0, microsecond=0)

        if self.frequency == ScheduleFrequencyEnum.DAILY:
            next_run = now + timedelta(days=1)
            if self.run_time:
                next_run = next_run.replace(
                    hour=self.run_time.hour,
                    minute=self.run_time.minute,
                    second=0,
                    microsecond=0
                )
            return next_run

        if self.frequency == ScheduleFrequencyEnum.WEEKLY:
            next_run = now + timedelta(weeks=1)
            if self.run_time:
                next_run = next_run.replace(
                    hour=self.run_time.hour,
                    minute=self.run_time.minute,
                    second=0,
                    microsecond=0
                )
            return next_run

        if self.frequency == ScheduleFrequencyEnum.MONTHLY:
            # Próximo mês, mesmo dia
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1)
            else:
                next_run = now.replace(month=now.month + 1)
            if self.run_time:
                next_run = next_run.replace(
                    hour=self.run_time.hour,
                    minute=self.run_time.minute,
                    second=0,
                    microsecond=0
                )
            return next_run

        if self.frequency == ScheduleFrequencyEnum.QUARTERLY:
            # Próximo trimestre
            current_quarter = (now.month - 1) // 3
            next_quarter_month = ((current_quarter + 1) % 4) * 3 + 1
            if next_quarter_month <= now.month:
                next_run = now.replace(year=now.year + 1, month=next_quarter_month, day=1)
            else:
                next_run = now.replace(month=next_quarter_month, day=1)
            return next_run

        if self.frequency == ScheduleFrequencyEnum.YEARLY:
            next_run = now.replace(year=now.year + 1)
            if self.run_time:
                next_run = next_run.replace(
                    hour=self.run_time.hour,
                    minute=self.run_time.minute,
                    second=0,
                    microsecond=0
                )
            return next_run

        return None

    def get_report_period(self) -> tuple[datetime, datetime]:
        """Calcula período do relatório baseado na configuração."""
        now = datetime.utcnow()

        if self.period_type == "previous_day":
            end = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start = end - timedelta(days=1)
        elif self.period_type == "previous_week":
            end = now - timedelta(days=now.weekday())
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)
            start = end - timedelta(weeks=1)
        elif self.period_type == "previous_month":
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start = (end - timedelta(days=1)).replace(day=1)
        elif self.period_type == "previous_quarter":
            current_quarter = (now.month - 1) // 3
            end_month = current_quarter * 3 + 1
            end = now.replace(month=end_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            start_month = end_month - 3 if end_month > 3 else end_month + 9
            start_year = now.year if end_month > 3 else now.year - 1
            start = datetime(start_year, start_month, 1)
        elif self.period_type == "year_to_date":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif self.period_type == "last_30_days":
            end = now
            start = now - timedelta(days=30)
        elif self.period_type == "last_90_days":
            end = now
            start = now - timedelta(days=90)
        else:
            # Default: último dia
            end = now
            start = now - timedelta(days=1)

        # Aplica offset
        if self.period_offset:
            start = start - timedelta(days=self.period_offset)
            end = end - timedelta(days=self.period_offset)

        return start, end

    def record_success(self) -> None:
        """Registra execução bem-sucedida."""
        self.total_runs += 1
        self.successful_runs += 1
        self.consecutive_failures = 0
        self.last_run_at = datetime.utcnow()
        self.last_success_at = datetime.utcnow()
        self.next_run_at = self.calculate_next_run()

        if self.is_expired:
            self.status = ScheduleStatusEnum.COMPLETED

    def record_failure(self, error: str = None) -> None:
        """Registra falha de execução."""
        self.total_runs += 1
        self.failed_runs += 1
        self.consecutive_failures += 1
        self.last_run_at = datetime.utcnow()
        self.last_failure_at = datetime.utcnow()

        if self.should_pause:
            self.status = ScheduleStatusEnum.FAILED
        else:
            self.next_run_at = self.calculate_next_run()

    def pause(self) -> None:
        """Pausa o agendamento."""
        self.status = ScheduleStatusEnum.PAUSED

    def resume(self) -> None:
        """Retoma o agendamento."""
        self.status = ScheduleStatusEnum.ACTIVE
        self.consecutive_failures = 0
        self.next_run_at = self.calculate_next_run()

    def cancel(self) -> None:
        """Cancela o agendamento."""
        self.status = ScheduleStatusEnum.CANCELLED
        self.next_run_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "name": self.name,
            "template_id": str(self.template_id),
            "status": self.status.value,
            "frequency": self.frequency.value,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "success_rate": self.success_rate,
            "total_runs": self.total_runs,
            "is_due": self.is_due,
        }
