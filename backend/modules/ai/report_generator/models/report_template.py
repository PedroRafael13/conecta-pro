"""
ReportTemplate Model - Templates de relatório.

Permite criar templates reutilizáveis para geração de relatórios.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class TemplateCategoryEnum(str, Enum):
    """Categorias de template."""

    # Por área
    FINANCIAL = "financial"
    SALES = "sales"
    HR = "hr"
    OPERATIONS = "operations"
    INVENTORY = "inventory"
    CUSTOMER = "customer"
    MARKETING = "marketing"

    # Por tipo
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    AUDIT = "audit"

    # Outros
    GENERAL = "general"
    CUSTOM = "custom"


class TemplateStatusEnum(str, Enum):
    """Status do template."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DataSourceEnum(str, Enum):
    """Fontes de dados disponíveis."""

    # CRM
    LEADS = "leads"
    OPPORTUNITIES = "opportunities"
    CUSTOMERS = "customers"
    CONTRACTS = "contracts"

    # Financeiro
    INVOICES = "invoices"
    PAYMENTS = "payments"
    EXPENSES = "expenses"
    BUDGET = "budget"

    # RH
    EMPLOYEES = "employees"
    ATTENDANCE = "attendance"
    PAYROLL = "payroll"
    RECRUITMENT = "recruitment"

    # Operações
    ORDERS = "orders"
    INVENTORY = "inventory"
    MAINTENANCE = "maintenance"
    EQUIPMENT = "equipment"

    # IA
    PREDICTIONS = "predictions"
    ANOMALIES = "anomalies"
    SENTIMENT = "sentiment"
    FRAUD = "fraud"

    # Outros
    CUSTOM_QUERY = "custom_query"
    EXTERNAL_API = "external_api"


class AIReportTemplate(Base):
    """Model de template de relatório."""

    __tablename__ = "ai_report_templates"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Classificação
    category = Column(
        SQLEnum(TemplateCategoryEnum, name="template_category_enum"),
        nullable=False,
        default=TemplateCategoryEnum.GENERAL
    )
    subcategory = Column(String(100), nullable=True)
    tags = Column(JSONB, default=list)

    # Status
    status = Column(
        SQLEnum(TemplateStatusEnum, name="template_status_enum"),
        nullable=False,
        default=TemplateStatusEnum.DRAFT
    )

    # Configuração de dados
    data_sources = Column(JSONB, default=list)  # Lista de DataSourceEnum
    primary_source = Column(String(100), nullable=True)
    queries = Column(JSONB, default=dict)  # Queries customizadas
    joins = Column(JSONB, default=list)  # Joins entre fontes

    # Parâmetros configuráveis
    parameters = Column(JSONB, default=list)
    required_parameters = Column(JSONB, default=list)
    default_values = Column(JSONB, default=dict)

    # Filtros padrão
    default_filters = Column(JSONB, default=dict)
    available_filters = Column(JSONB, default=list)

    # Layout e estrutura
    layout = Column(JSONB, default=dict)
    sections_config = Column(JSONB, default=list)
    header_config = Column(JSONB, default=dict)
    footer_config = Column(JSONB, default=dict)

    # Widgets e visualizações
    widgets_config = Column(JSONB, default=list)
    charts_config = Column(JSONB, default=list)
    tables_config = Column(JSONB, default=list)

    # Métricas e KPIs
    metrics_config = Column(JSONB, default=list)
    kpis_config = Column(JSONB, default=list)
    calculations = Column(JSONB, default=list)

    # Insights por IA
    ai_insights_enabled = Column(Boolean, default=True)
    insight_types = Column(JSONB, default=list)  # tipos de insight a gerar
    anomaly_detection_enabled = Column(Boolean, default=True)
    trend_analysis_enabled = Column(Boolean, default=True)
    recommendations_enabled = Column(Boolean, default=True)

    # Exportação
    supported_formats = Column(JSONB, default=["pdf", "excel", "csv"])
    default_format = Column(String(20), default="pdf")
    pdf_config = Column(JSONB, default=dict)
    excel_config = Column(JSONB, default=dict)

    # Branding
    logo_url = Column(String(500), nullable=True)
    brand_colors = Column(JSONB, default=dict)
    custom_css = Column(Text, nullable=True)
    font_family = Column(String(100), default="Arial")

    # Agendamento padrão
    default_schedule = Column(JSONB, default=dict)
    scheduling_enabled = Column(Boolean, default=True)

    # Distribuição
    default_recipients = Column(JSONB, default=list)
    email_subject_template = Column(String(500), nullable=True)
    email_body_template = Column(Text, nullable=True)

    # Permissões
    is_public = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)  # template do sistema
    allowed_roles = Column(JSONB, default=list)
    allowed_organizations = Column(JSONB, default=list)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Uso
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    average_generation_time_ms = Column(Integer, default=0)

    # Versionamento
    version = Column(Integer, default=1)
    parent_template_id = Column(UUID(as_uuid=True), nullable=True)
    changelog = Column(JSONB, default=list)

    # Validação
    validation_rules = Column(JSONB, default=list)
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSONB, default=list)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    reports = relationship("Report", back_populates="template")
    schedules = relationship("AIReportSchedule", back_populates="template")
    sections = relationship("ReportSection", back_populates="template")
    widgets = relationship("ReportWidget", back_populates="template")

    def __repr__(self) -> str:
        return f"<AIReportTemplate(id={self.id}, code={self.code}, category={self.category})>"

    @property
    def is_ready(self) -> bool:
        """Verifica se o template está pronto para uso."""
        return (
            self.status == TemplateStatusEnum.ACTIVE
            and self.is_validated
            and not self.validation_errors
        )

    @property
    def data_sources_list(self) -> List[str]:
        """Lista de fontes de dados."""
        return self.data_sources if self.data_sources else []

    @property
    def parameters_count(self) -> int:
        """Número de parâmetros configuráveis."""
        return len(self.parameters) if self.parameters else 0

    @property
    def sections_count(self) -> int:
        """Número de seções configuradas."""
        return len(self.sections_config) if self.sections_config else 0

    @property
    def widgets_count(self) -> int:
        """Número de widgets configurados."""
        return len(self.widgets_config) if self.widgets_config else 0

    def add_parameter(self, parameter: Dict[str, Any]) -> None:
        """Adiciona um parâmetro configurável."""
        if not self.parameters:
            self.parameters = []
        self.parameters.append(parameter)

    def add_section(self, section_config: Dict[str, Any]) -> None:
        """Adiciona uma seção ao template."""
        if not self.sections_config:
            self.sections_config = []
        section_config["order"] = len(self.sections_config)
        self.sections_config.append(section_config)

    def add_widget(self, widget_config: Dict[str, Any]) -> None:
        """Adiciona um widget ao template."""
        if not self.widgets_config:
            self.widgets_config = []
        self.widgets_config.append(widget_config)

    def add_data_source(self, source: str) -> None:
        """Adiciona uma fonte de dados."""
        if not self.data_sources:
            self.data_sources = []
        if source not in self.data_sources:
            self.data_sources.append(source)

    def increment_usage(self) -> None:
        """Incrementa contador de uso."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()

    def update_average_time(self, generation_time_ms: int) -> None:
        """Atualiza tempo médio de geração."""
        if self.average_generation_time_ms == 0:
            self.average_generation_time_ms = generation_time_ms
        else:
            # Média móvel
            self.average_generation_time_ms = int(
                (self.average_generation_time_ms + generation_time_ms) / 2
            )

    def validate(self) -> List[str]:
        """Valida o template e retorna lista de erros."""
        errors = []

        if not self.name:
            errors.append("Nome é obrigatório")

        if not self.data_sources:
            errors.append("Pelo menos uma fonte de dados é necessária")

        if not self.sections_config:
            errors.append("Pelo menos uma seção é necessária")

        # Valida parâmetros requeridos
        for param in self.required_parameters or []:
            if param not in [p.get("name") for p in self.parameters or []]:
                errors.append(f"Parâmetro requerido '{param}' não definido")

        self.validation_errors = errors
        self.is_validated = len(errors) == 0
        return errors

    def clone(self, new_code: str, new_name: str) -> "AIReportTemplate":
        """Cria uma cópia do template."""
        return AIReportTemplate(
            code=new_code,
            name=new_name,
            description=self.description,
            category=self.category,
            subcategory=self.subcategory,
            tags=self.tags.copy() if self.tags else [],
            data_sources=self.data_sources.copy() if self.data_sources else [],
            primary_source=self.primary_source,
            queries=self.queries.copy() if self.queries else {},
            parameters=self.parameters.copy() if self.parameters else [],
            default_filters=self.default_filters.copy() if self.default_filters else {},
            sections_config=self.sections_config.copy() if self.sections_config else [],
            widgets_config=self.widgets_config.copy() if self.widgets_config else [],
            charts_config=self.charts_config.copy() if self.charts_config else [],
            metrics_config=self.metrics_config.copy() if self.metrics_config else [],
            ai_insights_enabled=self.ai_insights_enabled,
            supported_formats=self.supported_formats.copy() if self.supported_formats else [],
            parent_template_id=self.id,
            status=TemplateStatusEnum.DRAFT,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "status": self.status.value,
            "data_sources": self.data_sources,
            "parameters_count": self.parameters_count,
            "sections_count": self.sections_count,
            "widgets_count": self.widgets_count,
            "ai_insights_enabled": self.ai_insights_enabled,
            "is_ready": self.is_ready,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
