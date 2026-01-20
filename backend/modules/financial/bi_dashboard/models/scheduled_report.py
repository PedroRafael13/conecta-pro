"""Model de Relatorio Agendado Financeiro."""

from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class ReportType(str, Enum):
    """Tipo de relatorio."""

    CASH_FLOW = "CASH_FLOW"
    INCOME_STATEMENT = "INCOME_STATEMENT"
    BALANCE_SHEET = "BALANCE_SHEET"
    ACCOUNTS_PAYABLE = "ACCOUNTS_PAYABLE"
    ACCOUNTS_RECEIVABLE = "ACCOUNTS_RECEIVABLE"
    BUDGET_VS_ACTUAL = "BUDGET_VS_ACTUAL"
    PROFITABILITY = "PROFITABILITY"
    KPI_SUMMARY = "KPI_SUMMARY"
    COST_ANALYSIS = "COST_ANALYSIS"
    TAX_SUMMARY = "TAX_SUMMARY"
    BANK_RECONCILIATION = "BANK_RECONCILIATION"
    AGING_REPORT = "AGING_REPORT"
    CUSTOM = "CUSTOM"


class ReportFormat(str, Enum):
    """Formato do relatorio."""

    PDF = "PDF"
    EXCEL = "EXCEL"
    CSV = "CSV"
    JSON = "JSON"
    HTML = "HTML"


class ReportFrequency(str, Enum):
    """Frequencia de geracao."""

    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class ReportStatus(str, Enum):
    """Status do relatorio."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"


class DeliveryMethod(str, Enum):
    """Metodo de entrega."""

    EMAIL = "EMAIL"
    STORAGE = "STORAGE"
    WEBHOOK = "WEBHOOK"
    API = "API"


class ScheduledReport(Base):
    """Relatorio Financeiro Agendado."""

    __tablename__ = "financial_scheduled_reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    codigo = Column(String(50), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)

    # Tipo e Formato
    tipo = Column(
        SQLEnum(ReportType, name="report_type_enum"),
        default=ReportType.CASH_FLOW,
        nullable=False,
    )
    formato = Column(
        SQLEnum(ReportFormat, name="report_format_enum"),
        default=ReportFormat.PDF,
        nullable=False,
    )
    status = Column(
        SQLEnum(ReportStatus, name="report_status_enum"),
        default=ReportStatus.ACTIVE,
        nullable=False,
    )

    # Agendamento
    frequencia = Column(
        SQLEnum(ReportFrequency, name="report_frequency_enum"),
        default=ReportFrequency.MONTHLY,
        nullable=False,
    )
    hora_execucao = Column(Time, default=datetime.strptime("08:00", "%H:%M").time())
    dia_semana = Column(Integer)
    dia_mes = Column(Integer)
    timezone = Column(String(50), default="America/Sao_Paulo")

    # Periodo de Dados
    periodo_tipo = Column(String(50), default="last_month")
    periodo_dias = Column(Integer, default=30)
    data_inicio = Column(Date)
    data_fim = Column(Date)

    # Validade
    valido_de = Column(Date, default=date.today)
    valido_ate = Column(Date)

    # Entrega
    metodo_entrega = Column(
        SQLEnum(DeliveryMethod, name="delivery_method_enum"),
        default=DeliveryMethod.EMAIL,
        nullable=False,
    )
    destinatarios_email = Column(JSONB, default=list)
    webhook_url = Column(String(500))
    storage_path = Column(String(500))

    # Template
    template_id = Column(String(100))
    template_config = Column(JSONB, default=dict)
    custom_query = Column(Text)
    filtros = Column(JSONB, default=dict)
    ordenacao = Column(JSONB, default=list)
    agrupamento = Column(JSONB, default=list)

    # Aparencia
    logo_url = Column(String(500))
    header_text = Column(Text)
    footer_text = Column(Text)
    show_charts = Column(Boolean, default=True)
    show_summary = Column(Boolean, default=True)
    paper_size = Column(String(20), default="A4")
    orientation = Column(String(20), default="portrait")

    # Execucao
    proxima_execucao_at = Column(DateTime)
    ultima_execucao_at = Column(DateTime)
    ultima_execucao_status = Column(String(50))
    ultima_execucao_erro = Column(Text)
    total_execucoes = Column(Integer, default=0)
    total_erros = Column(Integer, default=0)

    # Arquivo Gerado
    ultimo_arquivo_url = Column(String(500))
    ultimo_arquivo_tamanho = Column(Integer)
    ultimo_arquivo_hash = Column(String(64))

    # Notificacoes
    notificar_sucesso = Column(Boolean, default=True)
    notificar_erro = Column(Boolean, default=True)
    notificar_email = Column(String(255))

    # Metadados
    tags = Column(JSONB, default=list)
    extra_metadata = Column(JSONB, default=dict)

    # Auditoria
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao do relatorio."""
        return f"<ScheduledReport {self.codigo}: {self.nome}>"

    @property
    def is_active(self) -> bool:
        """Verifica se relatorio esta ativo."""
        if self.status != ReportStatus.ACTIVE:
            return False
        if self.valido_ate and date.today() > self.valido_ate:
            return False
        return True

    @property
    def is_due(self) -> bool:
        """Verifica se esta na hora de executar."""
        if not self.is_active:
            return False
        if not self.proxima_execucao_at:
            return True
        return datetime.utcnow() >= self.proxima_execucao_at

    @property
    def success_rate(self) -> Decimal:
        """Taxa de sucesso das execucoes."""
        if self.total_execucoes == 0:
            return Decimal("100")
        success = self.total_execucoes - self.total_erros
        return Decimal(str((success / self.total_execucoes) * 100))

    def calculate_next_execution(self) -> datetime:
        """Calcula proxima data de execucao."""
        now = datetime.utcnow()

        if self.frequencia == ReportFrequency.ONCE:
            return None

        if self.frequencia == ReportFrequency.DAILY:
            next_run = now.replace(
                hour=self.hora_execucao.hour,
                minute=self.hora_execucao.minute,
                second=0,
                microsecond=0,
            )
            if next_run <= now:
                next_run = next_run.replace(day=next_run.day + 1)
            return next_run

        if self.frequencia == ReportFrequency.WEEKLY:
            days_ahead = self.dia_semana - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            return next_run.replace(
                hour=self.hora_execucao.hour,
                minute=self.hora_execucao.minute,
                second=0,
            )

        if self.frequencia == ReportFrequency.MONTHLY:
            day = min(self.dia_mes or 1, 28)
            if now.day >= day:
                month = now.month + 1 if now.month < 12 else 1
                year = now.year if now.month < 12 else now.year + 1
            else:
                month = now.month
                year = now.year
            return datetime(
                year, month, day,
                self.hora_execucao.hour,
                self.hora_execucao.minute,
            )

        return now + timedelta(days=1)

    def mark_executed(self, success: bool, error: str = None) -> None:
        """Marca relatorio como executado."""
        self.ultima_execucao_at = datetime.utcnow()
        self.ultima_execucao_status = "success" if success else "error"
        self.ultima_execucao_erro = error if not success else None
        self.total_execucoes += 1
        if not success:
            self.total_erros += 1

        # Calcula proxima execucao
        self.proxima_execucao_at = self.calculate_next_execution()

        # Verifica expiracao
        if self.valido_ate and date.today() > self.valido_ate:
            self.status = ReportStatus.EXPIRED

    def pause(self) -> None:
        """Pausa o agendamento."""
        self.status = ReportStatus.PAUSED

    def resume(self) -> None:
        """Retoma o agendamento."""
        if self.valido_ate and date.today() > self.valido_ate:
            self.status = ReportStatus.EXPIRED
        else:
            self.status = ReportStatus.ACTIVE
            self.proxima_execucao_at = self.calculate_next_execution()

    def cancel(self) -> None:
        """Cancela o agendamento."""
        self.status = ReportStatus.CANCELLED
        self.proxima_execucao_at = None
