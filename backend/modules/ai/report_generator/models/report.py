"""
Report Model - Relatório gerado.

Armazena relatórios gerados com dados, insights e exportações.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
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


class ReportTypeEnum(StrEnum):
    """Tipos de relatório."""

    # Operacionais
    DASHBOARD = "dashboard"
    SUMMARY = "summary"
    DETAILED = "detailed"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"

    # Por área
    FINANCIAL = "financial"
    SALES = "sales"
    HR = "hr"
    OPERATIONS = "operations"
    INVENTORY = "inventory"
    CUSTOMER = "customer"

    # Específicos
    KPI = "kpi"
    FORECAST = "forecast"
    ANOMALY = "anomaly"
    TREND = "trend"
    AUDIT = "audit"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"

    # Customizados
    CUSTOM = "custom"
    AD_HOC = "ad_hoc"


class ReportStatusEnum(StrEnum):
    """Status do relatório."""

    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class ReportFormatEnum(StrEnum):
    """Formatos de exportação."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    WORD = "word"
    POWERPOINT = "powerpoint"


class ReportPriorityEnum(StrEnum):
    """Prioridade do relatório."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Report(Base):
    """Model de relatório gerado."""

    __tablename__ = "ai_reports"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Classificação
    report_type = Column(
        SQLEnum(ReportTypeEnum, name="report_type_enum"), nullable=False, default=ReportTypeEnum.SUMMARY
    )
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSONB, default=list)

    # Status
    status = Column(
        SQLEnum(ReportStatusEnum, name="report_status_enum"), nullable=False, default=ReportStatusEnum.DRAFT
    )
    priority = Column(
        SQLEnum(ReportPriorityEnum, name="report_priority_enum"), nullable=False, default=ReportPriorityEnum.NORMAL
    )

    # Template
    template_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_templates.id"), nullable=True)
    template = relationship("AIReportTemplate", back_populates="reports")

    # Período do relatório
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    period_type = Column(String(50), nullable=True)  # daily, weekly, monthly, quarterly, yearly

    # Filtros aplicados
    filters = Column(JSONB, default=dict)
    parameters = Column(JSONB, default=dict)

    # Dados do relatório
    data = Column(JSONB, default=dict)
    summary = Column(JSONB, default=dict)
    metrics = Column(JSONB, default=dict)

    # Insights gerados por IA
    insights = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)
    anomalies = Column(JSONB, default=list)
    trends = Column(JSONB, default=list)

    # Visualizações
    charts = Column(JSONB, default=list)
    tables = Column(JSONB, default=list)

    # Scores e métricas de qualidade
    data_quality_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)

    # Exportação
    exported_formats = Column(JSONB, default=list)
    file_paths = Column(JSONB, default=dict)
    file_size_bytes = Column(Integer, default=0)

    # Distribuição
    recipients = Column(JSONB, default=list)
    sent_at = Column(DateTime, nullable=True)
    sent_count = Column(Integer, default=0)

    # Acesso
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime, nullable=True)
    last_downloaded_at = Column(DateTime, nullable=True)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    department_id = Column(UUID(as_uuid=True), nullable=True)

    # Permissões
    is_public = Column(Boolean, default=False)
    allowed_roles = Column(JSONB, default=list)
    allowed_users = Column(JSONB, default=list)

    # Execução
    execution_id = Column(UUID(as_uuid=True), ForeignKey("ai_report_executions.id"), nullable=True)
    generation_time_ms = Column(Integer, default=0)

    # Validade
    expires_at = Column(DateTime, nullable=True)
    retention_days = Column(Integer, default=90)

    # Metadados
    version = Column(Integer, default=1)
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generated_at = Column(DateTime, nullable=True)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    sections = relationship("ReportSection", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, code={self.code}, type={self.report_type})>"

    @property
    def is_expired(self) -> bool:
        """Verifica se o relatório expirou."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    @property
    def period_description(self) -> str:
        """Descrição do período do relatório."""
        if self.period_start and self.period_end:
            return f"{self.period_start.strftime('%d/%m/%Y')} a {self.period_end.strftime('%d/%m/%Y')}"
        return "Período não definido"

    @property
    def insights_count(self) -> int:
        """Número de insights gerados."""
        return len(self.insights) if self.insights else 0

    @property
    def has_anomalies(self) -> bool:
        """Verifica se há anomalias detectadas."""
        return bool(self.anomalies)

    @property
    def overall_quality_score(self) -> float:
        """Score geral de qualidade do relatório."""
        scores = [self.data_quality_score, self.completeness_score, self.accuracy_score]
        valid_scores = [s for s in scores if s > 0]
        if not valid_scores:
            return 0.0
        return sum(valid_scores) / len(valid_scores)

    def add_insight(self, insight: dict[str, Any]) -> None:
        """Adiciona um insight ao relatório."""
        if not self.insights:
            self.insights = []
        insight["added_at"] = datetime.utcnow().isoformat()
        self.insights.append(insight)

    def add_recommendation(self, recommendation: dict[str, Any]) -> None:
        """Adiciona uma recomendação ao relatório."""
        if not self.recommendations:
            self.recommendations = []
        recommendation["added_at"] = datetime.utcnow().isoformat()
        self.recommendations.append(recommendation)

    def mark_as_viewed(self) -> None:
        """Marca o relatório como visualizado."""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()

    def mark_as_downloaded(self, format_type: str) -> None:
        """Marca o relatório como baixado."""
        self.download_count += 1
        self.last_downloaded_at = datetime.utcnow()
        if format_type not in self.exported_formats:
            self.exported_formats.append(format_type)

    def to_summary_dict(self) -> dict[str, Any]:
        """Converte para dicionário resumido."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "report_type": self.report_type.value,
            "status": self.status.value,
            "period": self.period_description,
            "insights_count": self.insights_count,
            "has_anomalies": self.has_anomalies,
            "quality_score": self.overall_quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }
