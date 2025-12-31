"""Modelo ScheduledReport - Relatórios agendados."""

import uuid
from datetime import datetime, time
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Time,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ReportType(str, Enum):
    """Tipo de relatório."""
    ATTENDANCE = "attendance"            # Frequência
    OVERTIME = "overtime"                # Horas extras
    PUNCTUALITY = "punctuality"          # Pontualidade
    ABSENCES = "absences"                # Faltas
    BANK_HOURS = "bank_hours"            # Banco de horas
    TIMESHEET = "timesheet"              # Folha de ponto
    COMPLIANCE = "compliance"            # Conformidade CLT
    EXECUTIVE_SUMMARY = "executive_summary"  # Resumo executivo
    DEPARTMENT_ANALYSIS = "department_analysis"  # Análise por departamento
    EMPLOYEE_DETAIL = "employee_detail"  # Detalhe por funcionário
    CUSTOM = "custom"                    # Personalizado


class ReportFormat(str, Enum):
    """Formato de exportação."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class ScheduleFrequency(str, Enum):
    """Frequência de agendamento."""
    ONCE = "once"              # Uma vez
    DAILY = "daily"            # Diário
    WEEKLY = "weekly"          # Semanal
    BIWEEKLY = "biweekly"      # Quinzenal
    MONTHLY = "monthly"        # Mensal
    QUARTERLY = "quarterly"    # Trimestral
    YEARLY = "yearly"          # Anual


class DeliveryMethod(str, Enum):
    """Método de entrega."""
    EMAIL = "email"
    DOWNLOAD = "download"
    SFTP = "sftp"
    WEBHOOK = "webhook"
    STORAGE = "storage"        # Cloud storage


class ReportStatus(str, Enum):
    """Status do relatório agendado."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"    # Para ONCE
    FAILED = "failed"
    DISABLED = "disabled"


class ScheduledReport(Base):
    """Modelo de relatório agendado."""

    __tablename__ = "scheduled_reports"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Informações básicas
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    report_type: Mapped[str] = mapped_column(
        String(30),
        default=ReportType.ATTENDANCE.value,
    )

    # Configuração do relatório
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    report_config: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    columns: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    filters: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    grouping: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    sorting: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Período dos dados
    period_type: Mapped[str] = mapped_column(
        String(30),
        default="previous_month",
    )  # previous_day, previous_week, previous_month, custom, rolling_X_days
    custom_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    custom_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rolling_days: Mapped[Optional[int]] = mapped_column(Integer)

    # Formato de saída
    output_format: Mapped[str] = mapped_column(
        String(10),
        default=ReportFormat.PDF.value,
    )
    include_charts: Mapped[bool] = mapped_column(Boolean, default=True)
    include_summary: Mapped[bool] = mapped_column(Boolean, default=True)
    language: Mapped[str] = mapped_column(String(5), default="pt-BR")

    # Agendamento
    frequency: Mapped[str] = mapped_column(
        String(20),
        default=ScheduleFrequency.MONTHLY.value,
    )
    schedule_time: Mapped[time] = mapped_column(Time, default=time(6, 0))
    schedule_day: Mapped[Optional[int]] = mapped_column(Integer)  # 1-31 para monthly, 0-6 para weekly
    schedule_month: Mapped[Optional[int]] = mapped_column(Integer)  # 1-12 para yearly
    timezone: Mapped[str] = mapped_column(String(50), default="America/Sao_Paulo")

    # Próxima execução
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Entrega
    delivery_method: Mapped[str] = mapped_column(
        String(20),
        default=DeliveryMethod.EMAIL.value,
    )
    recipients: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    cc_recipients: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    email_subject: Mapped[Optional[str]] = mapped_column(String(200))
    email_body: Mapped[Optional[str]] = mapped_column(Text)

    # Configuração de entrega alternativa
    sftp_config: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500))
    storage_path: Mapped[Optional[str]] = mapped_column(String(500))

    # Estatísticas
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_status: Mapped[Optional[str]] = mapped_column(String(20))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    last_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    last_file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    avg_generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=ReportStatus.ACTIVE.value,
        index=True,
    )

    # Data de término (para ONCE ou limite de execuções)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    max_runs: Mapped[Optional[int]] = mapped_column(Integer)

    # Notificações
    notify_on_success: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_on_failure: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_recipients: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Metadados
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Auditoria
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Índices
    __table_args__ = (
        Index("ix_scheduled_reports_condominio_status", "condominio_id", "status"),
        Index("ix_scheduled_reports_next_run", "next_run_at"),
        Index("ix_scheduled_reports_owner", "owner_id"),
    )

    @property
    def is_due(self) -> bool:
        """Verifica se relatório está pronto para execução."""
        if self.status != ReportStatus.ACTIVE.value:
            return False
        if not self.next_run_at:
            return False
        return self.next_run_at <= datetime.utcnow()

    @property
    def success_rate(self) -> float:
        """Retorna taxa de sucesso."""
        if self.run_count == 0:
            return 0.0
        return (self.success_count / self.run_count) * 100

    @property
    def has_reached_limit(self) -> bool:
        """Verifica se atingiu limite de execuções."""
        if not self.max_runs:
            return False
        return self.run_count >= self.max_runs

    @property
    def has_expired(self) -> bool:
        """Verifica se passou da data de término."""
        if not self.end_date:
            return False
        return self.end_date < datetime.utcnow()

    def calculate_next_run(self) -> Optional[datetime]:
        """Calcula próxima execução baseado na frequência."""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta

        base = self.last_run_at or datetime.utcnow()

        # Combinar data base com horário agendado
        next_run = base.replace(
            hour=self.schedule_time.hour,
            minute=self.schedule_time.minute,
            second=0,
            microsecond=0,
        )

        if self.frequency == ScheduleFrequency.ONCE.value:
            return None

        elif self.frequency == ScheduleFrequency.DAILY.value:
            next_run += timedelta(days=1)

        elif self.frequency == ScheduleFrequency.WEEKLY.value:
            next_run += timedelta(weeks=1)
            if self.schedule_day is not None:
                days_ahead = self.schedule_day - next_run.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                next_run += timedelta(days=days_ahead)

        elif self.frequency == ScheduleFrequency.BIWEEKLY.value:
            next_run += timedelta(weeks=2)

        elif self.frequency == ScheduleFrequency.MONTHLY.value:
            next_run += relativedelta(months=1)
            if self.schedule_day:
                try:
                    next_run = next_run.replace(day=self.schedule_day)
                except ValueError:
                    # Último dia do mês se dia não existe
                    next_run = next_run.replace(day=28)

        elif self.frequency == ScheduleFrequency.QUARTERLY.value:
            next_run += relativedelta(months=3)

        elif self.frequency == ScheduleFrequency.YEARLY.value:
            next_run += relativedelta(years=1)

        return next_run

    def record_run(self, success: bool, error: str = None, file_path: str = None, file_size: int = None, duration_ms: int = None) -> None:
        """Registra execução do relatório."""
        self.run_count += 1
        self.last_run_at = datetime.utcnow()

        if success:
            self.success_count += 1
            self.last_status = "success"
            self.last_error = None
        else:
            self.failure_count += 1
            self.last_status = "failed"
            self.last_error = error

        if file_path:
            self.last_file_path = file_path
        if file_size:
            self.last_file_size_bytes = file_size

        if duration_ms:
            if self.avg_generation_time_ms:
                # Média móvel
                self.avg_generation_time_ms = int(
                    (self.avg_generation_time_ms * (self.run_count - 1) + duration_ms) / self.run_count
                )
            else:
                self.avg_generation_time_ms = duration_ms

        # Calcular próxima execução
        if not self.has_reached_limit and not self.has_expired:
            self.next_run_at = self.calculate_next_run()
            if not self.next_run_at:
                self.status = ReportStatus.COMPLETED.value
        else:
            self.status = ReportStatus.COMPLETED.value
            self.next_run_at = None

    def pause(self) -> None:
        """Pausa o agendamento."""
        self.status = ReportStatus.PAUSED.value

    def resume(self) -> None:
        """Retoma o agendamento."""
        self.status = ReportStatus.ACTIVE.value
        if not self.next_run_at or self.next_run_at < datetime.utcnow():
            self.next_run_at = self.calculate_next_run()

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "name": self.name,
            "report_type": self.report_type,
            "frequency": self.frequency,
            "status": self.status,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "run_count": self.run_count,
            "success_rate": self.success_rate,
        }
