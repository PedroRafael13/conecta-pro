"""
Template Engine - Motor de templates de relatórios.

Gerencia templates, validação e renderização de relatórios.
"""

import logging
import re
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ai.report_generator.models import (
    AIReportTemplate,
)
from modules.ai.report_generator.models.report_template import (
    TemplateCategoryEnum,
    TemplateStatusEnum,
)
from modules.ai.report_generator.repositories import ReportRepository

logger = logging.getLogger(__name__)


# Templates padrão do sistema
DEFAULT_TEMPLATES = [
    {
        "code": "sales_monthly",
        "name": "Relatório de Vendas Mensal",
        "description": "Relatório mensal de vendas com métricas, tendências e insights.",
        "category": TemplateCategoryEnum.SALES,
        "data_sources": ["opportunities", "customers", "invoices"],
        "sections_config": [
            {
                "code": "header",
                "name": "Cabeçalho",
                "section_type": "header",
                "title": "Relatório de Vendas",
            },
            {
                "code": "kpi_summary",
                "name": "KPIs Principais",
                "section_type": "kpi",
                "layout": "full_width",
            },
            {
                "code": "sales_chart",
                "name": "Gráfico de Vendas",
                "section_type": "chart",
                "chart_type": "line",
                "data_source": "opportunities",
            },
            {
                "code": "top_products",
                "name": "Top Produtos",
                "section_type": "table",
                "data_source": "products",
            },
            {
                "code": "insights",
                "name": "Insights de IA",
                "section_type": "insight",
            },
        ],
        "metrics_config": [
            {"name": "total_sales", "label": "Total de Vendas", "format": "currency"},
            {"name": "sales_count", "label": "Número de Vendas", "format": "number"},
            {"name": "avg_ticket", "label": "Ticket Médio", "format": "currency"},
            {"name": "conversion_rate", "label": "Taxa de Conversão", "format": "percent"},
        ],
        "supported_formats": ["pdf", "excel", "csv"],
        "ai_insights_enabled": True,
        "is_system": True,
    },
    {
        "code": "financial_summary",
        "name": "Resumo Financeiro",
        "description": "Resumo financeiro com DRE simplificado e indicadores.",
        "category": TemplateCategoryEnum.FINANCIAL,
        "data_sources": ["invoices", "payments", "expenses"],
        "sections_config": [
            {
                "code": "header",
                "name": "Cabeçalho",
                "section_type": "header",
                "title": "Resumo Financeiro",
            },
            {
                "code": "dre_summary",
                "name": "DRE Simplificado",
                "section_type": "table",
            },
            {
                "code": "cashflow_chart",
                "name": "Fluxo de Caixa",
                "section_type": "chart",
                "chart_type": "bar",
            },
            {
                "code": "indicators",
                "name": "Indicadores",
                "section_type": "kpi",
            },
        ],
        "metrics_config": [
            {"name": "revenue", "label": "Receita", "format": "currency"},
            {"name": "expenses", "label": "Despesas", "format": "currency"},
            {"name": "profit", "label": "Lucro Líquido", "format": "currency"},
            {"name": "margin", "label": "Margem", "format": "percent"},
        ],
        "supported_formats": ["pdf", "excel"],
        "ai_insights_enabled": True,
        "is_system": True,
    },
    {
        "code": "hr_dashboard",
        "name": "Dashboard de RH",
        "description": "Visão geral de recursos humanos com métricas de equipe.",
        "category": TemplateCategoryEnum.HR,
        "data_sources": ["employees", "attendance", "recruitment"],
        "sections_config": [
            {
                "code": "header",
                "name": "Cabeçalho",
                "section_type": "header",
                "title": "Dashboard de RH",
            },
            {
                "code": "headcount",
                "name": "Headcount",
                "section_type": "kpi",
            },
            {
                "code": "by_department",
                "name": "Por Departamento",
                "section_type": "chart",
                "chart_type": "pie",
            },
            {
                "code": "turnover",
                "name": "Turnover",
                "section_type": "trend",
            },
        ],
        "metrics_config": [
            {"name": "total_employees", "label": "Total de Funcionários", "format": "number"},
            {"name": "turnover_rate", "label": "Taxa de Turnover", "format": "percent"},
            {"name": "avg_tenure", "label": "Tempo Médio de Casa", "format": "years"},
        ],
        "supported_formats": ["pdf", "excel"],
        "ai_insights_enabled": True,
        "is_system": True,
    },
    {
        "code": "customer_analysis",
        "name": "Análise de Clientes",
        "description": "Análise detalhada da base de clientes com segmentação.",
        "category": TemplateCategoryEnum.CUSTOMER,
        "data_sources": ["customers", "contracts", "sentiment"],
        "sections_config": [
            {
                "code": "header",
                "name": "Cabeçalho",
                "section_type": "header",
                "title": "Análise de Clientes",
            },
            {
                "code": "customer_kpis",
                "name": "KPIs de Clientes",
                "section_type": "kpi",
            },
            {
                "code": "segmentation",
                "name": "Segmentação",
                "section_type": "chart",
                "chart_type": "donut",
            },
            {
                "code": "churn_risk",
                "name": "Risco de Churn",
                "section_type": "ranking",
            },
            {
                "code": "sentiment_overview",
                "name": "Sentimento",
                "section_type": "insight",
            },
        ],
        "metrics_config": [
            {"name": "total_customers", "label": "Total de Clientes", "format": "number"},
            {"name": "mrr", "label": "MRR", "format": "currency"},
            {"name": "churn_rate", "label": "Churn Rate", "format": "percent"},
            {"name": "nps", "label": "NPS", "format": "number"},
        ],
        "supported_formats": ["pdf", "excel", "powerpoint"],
        "ai_insights_enabled": True,
        "is_system": True,
    },
    {
        "code": "inventory_report",
        "name": "Relatório de Estoque",
        "description": "Relatório de posição de estoque e movimentações.",
        "category": TemplateCategoryEnum.INVENTORY,
        "data_sources": ["inventory"],
        "sections_config": [
            {
                "code": "header",
                "name": "Cabeçalho",
                "section_type": "header",
                "title": "Relatório de Estoque",
            },
            {
                "code": "stock_summary",
                "name": "Resumo de Estoque",
                "section_type": "kpi",
            },
            {
                "code": "low_stock",
                "name": "Estoque Baixo",
                "section_type": "table",
            },
            {
                "code": "movements",
                "name": "Movimentações",
                "section_type": "chart",
                "chart_type": "bar",
            },
        ],
        "metrics_config": [
            {"name": "total_sku", "label": "Total de SKUs", "format": "number"},
            {"name": "total_value", "label": "Valor em Estoque", "format": "currency"},
            {"name": "low_stock_count", "label": "Itens Baixo Estoque", "format": "number"},
            {"name": "turnover", "label": "Giro de Estoque", "format": "decimal"},
        ],
        "supported_formats": ["pdf", "excel", "csv"],
        "ai_insights_enabled": True,
        "is_system": True,
    },
]


class TemplateEngine:
    """Motor de templates de relatórios."""

    def __init__(self, db: Session):
        """Inicializa motor de templates."""
        self.db = db
        self.repository = ReportRepository(db)

    def initialize_default_templates(self) -> list[AIReportTemplate]:
        """Inicializa templates padrão do sistema."""
        created_templates = []

        for template_config in DEFAULT_TEMPLATES:
            # Verifica se já existe
            existing = self.repository.get_template_by_code(template_config["code"])
            if existing:
                continue

            template = AIReportTemplate(
                code=template_config["code"],
                name=template_config["name"],
                description=template_config.get("description"),
                category=template_config["category"],
                data_sources=template_config.get("data_sources", []),
                sections_config=template_config.get("sections_config", []),
                metrics_config=template_config.get("metrics_config", []),
                supported_formats=template_config.get("supported_formats", ["pdf"]),
                ai_insights_enabled=template_config.get("ai_insights_enabled", True),
                is_system=template_config.get("is_system", False),
                is_public=True,
                status=TemplateStatusEnum.ACTIVE,
                is_validated=True,
            )

            created_templates.append(self.repository.create_template(template))
            logger.info(f"Template padrão criado: {template.code}")

        return created_templates

    def create_template(
        self,
        code: str,
        name: str,
        description: str | None = None,
        category: TemplateCategoryEnum = TemplateCategoryEnum.GENERAL,
        data_sources: list[str] | None = None,
        parameters: list[dict[str, Any]] | None = None,
        sections_config: list[dict[str, Any]] | None = None,
        widgets_config: list[dict[str, Any]] | None = None,
        metrics_config: list[dict[str, Any]] | None = None,
        supported_formats: list[str] | None = None,
        ai_insights_enabled: bool = True,
        created_by: UUID | None = None,
        organization_id: UUID | None = None,
    ) -> AIReportTemplate:
        """Cria novo template."""
        # Verifica código único
        existing = self.repository.get_template_by_code(code)
        if existing:
            raise ValueError(f"Template com código '{code}' já existe")

        template = AIReportTemplate(
            code=code,
            name=name,
            description=description,
            category=category,
            data_sources=data_sources or [],
            parameters=parameters or [],
            sections_config=sections_config or [],
            widgets_config=widgets_config or [],
            metrics_config=metrics_config or [],
            supported_formats=supported_formats or ["pdf", "excel"],
            ai_insights_enabled=ai_insights_enabled,
            created_by=created_by,
            organization_id=organization_id,
            status=TemplateStatusEnum.DRAFT,
        )

        # Valida template
        errors = template.validate()
        if errors:
            logger.warning(f"Template criado com erros de validação: {errors}")

        return self.repository.create_template(template)

    def update_template(self, template_id: UUID, **kwargs) -> AIReportTemplate | None:
        """Atualiza template."""
        template = self.repository.get_template(template_id)
        if not template:
            return None

        # Não permite editar templates do sistema
        if template.is_system and kwargs.get("is_system") is not False:
            raise ValueError("Não é possível editar templates do sistema")

        # Atualiza campos
        for key, value in kwargs.items():
            if hasattr(template, key) and value is not None:
                setattr(template, key, value)

        # Incrementa versão
        template.version += 1

        # Revalida
        template.validate()

        return self.repository.update_template(template)

    def clone_template(
        self,
        template_id: UUID,
        new_code: str,
        new_name: str,
        organization_id: UUID | None = None,
    ) -> AIReportTemplate:
        """Clona um template existente."""
        template = self.repository.get_template(template_id)
        if not template:
            raise ValueError("Template não encontrado")

        # Verifica código único
        existing = self.repository.get_template_by_code(new_code)
        if existing:
            raise ValueError(f"Template com código '{new_code}' já existe")

        cloned = template.clone(new_code, new_name)
        cloned.organization_id = organization_id
        cloned.is_system = False
        cloned.is_public = False

        return self.repository.create_template(cloned)

    def publish_template(self, template_id: UUID) -> AIReportTemplate | None:
        """Publica um template (ativa)."""
        template = self.repository.get_template(template_id)
        if not template:
            return None

        # Valida antes de publicar
        errors = template.validate()
        if errors:
            raise ValueError(f"Template inválido: {', '.join(errors)}")

        template.status = TemplateStatusEnum.ACTIVE
        template.published_at = datetime.utcnow()

        return self.repository.update_template(template)

    def deprecate_template(self, template_id: UUID) -> AIReportTemplate | None:
        """Marca template como obsoleto."""
        template = self.repository.get_template(template_id)
        if not template:
            return None

        template.status = TemplateStatusEnum.DEPRECATED

        return self.repository.update_template(template)

    def validate_template(self, template_id: UUID) -> dict[str, Any]:
        """Valida um template e retorna resultado."""
        template = self.repository.get_template(template_id)
        if not template:
            raise ValueError("Template não encontrado")

        errors = template.validate()

        # Validações adicionais
        warnings = []

        # Verifica se tem pelo menos uma seção visual
        visual_sections = [
            s for s in template.sections_config or [] if s.get("section_type") in ["chart", "table", "kpi"]
        ]
        if not visual_sections:
            warnings.append("Template não possui seções visuais (gráficos, tabelas ou KPIs)")

        # Verifica métricas
        if not template.metrics_config:
            warnings.append("Template não possui métricas configuradas")

        # Verifica formatos
        if not template.supported_formats:
            warnings.append("Template não possui formatos de exportação configurados")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "template_id": str(template_id),
            "template_code": template.code,
        }

    def render_content(
        self,
        content_template: str,
        context: dict[str, Any],
    ) -> str:
        """Renderiza template de conteúdo com variáveis."""
        if not content_template:
            return ""

        rendered = content_template

        # Substitui variáveis simples: {{variavel}}
        pattern = r"\{\{(\w+(?:\.\w+)*)\}\}"
        matches = re.findall(pattern, rendered)

        for match in matches:
            value = self._get_nested_value(context, match)
            placeholder = f"{{{{{match}}}}}"
            rendered = rendered.replace(placeholder, str(value) if value is not None else "")

        # Substitui formatadores: {{variavel|format}}
        pattern_format = r"\{\{(\w+(?:\.\w+)*)\|(\w+)\}\}"
        matches_format = re.findall(pattern_format, rendered)

        for var_name, format_type in matches_format:
            value = self._get_nested_value(context, var_name)
            formatted = self._format_value(value, format_type)
            placeholder = f"{{{{{var_name}|{format_type}}}}}"
            rendered = rendered.replace(placeholder, formatted)

        return rendered

    def _get_nested_value(self, obj: dict[str, Any], path: str) -> Any:
        """Obtém valor aninhado de um dicionário."""
        keys = path.split(".")
        value = obj

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

            if value is None:
                return None

        return value

    def _format_value(self, value: Any, format_type: str) -> str:
        """Formata valor de acordo com o tipo."""
        if value is None:
            return ""

        if format_type == "currency":
            try:
                return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                return str(value)

        if format_type == "percent":
            try:
                return f"{float(value):.2f}%"
            except (ValueError, TypeError):
                return str(value)

        if format_type == "number":
            try:
                return f"{int(value):,}".replace(",", ".")
            except (ValueError, TypeError):
                return str(value)

        if format_type == "decimal":
            try:
                return f"{float(value):.2f}"
            except (ValueError, TypeError):
                return str(value)

        if format_type == "date":
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y")
            return str(value)

        if format_type == "datetime":
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y %H:%M")
            return str(value)

        return str(value)

    def get_available_data_sources(self) -> list[dict[str, Any]]:
        """Retorna lista de fontes de dados disponíveis."""
        return [
            {"code": "leads", "name": "Leads", "category": "crm"},
            {"code": "opportunities", "name": "Oportunidades", "category": "crm"},
            {"code": "customers", "name": "Clientes", "category": "crm"},
            {"code": "contracts", "name": "Contratos", "category": "crm"},
            {"code": "invoices", "name": "Faturas", "category": "financial"},
            {"code": "payments", "name": "Pagamentos", "category": "financial"},
            {"code": "expenses", "name": "Despesas", "category": "financial"},
            {"code": "budget", "name": "Orçamento", "category": "financial"},
            {"code": "employees", "name": "Funcionários", "category": "hr"},
            {"code": "attendance", "name": "Ponto", "category": "hr"},
            {"code": "payroll", "name": "Folha de Pagamento", "category": "hr"},
            {"code": "recruitment", "name": "Recrutamento", "category": "hr"},
            {"code": "orders", "name": "Pedidos", "category": "operations"},
            {"code": "inventory", "name": "Estoque", "category": "operations"},
            {"code": "maintenance", "name": "Manutenção", "category": "operations"},
            {"code": "predictions", "name": "Predições IA", "category": "ai"},
            {"code": "anomalies", "name": "Anomalias", "category": "ai"},
            {"code": "sentiment", "name": "Sentimento", "category": "ai"},
            {"code": "fraud", "name": "Fraude", "category": "ai"},
        ]

    def get_available_section_types(self) -> list[dict[str, Any]]:
        """Retorna tipos de seção disponíveis."""
        return [
            {"code": "header", "name": "Cabeçalho", "category": "structure"},
            {"code": "footer", "name": "Rodapé", "category": "structure"},
            {"code": "text", "name": "Texto", "category": "content"},
            {"code": "table", "name": "Tabela", "category": "content"},
            {"code": "chart", "name": "Gráfico", "category": "visualization"},
            {"code": "kpi", "name": "KPI", "category": "visualization"},
            {"code": "metric", "name": "Métrica", "category": "visualization"},
            {"code": "trend", "name": "Tendência", "category": "analysis"},
            {"code": "comparison", "name": "Comparação", "category": "analysis"},
            {"code": "insight", "name": "Insight IA", "category": "ai"},
            {"code": "recommendation", "name": "Recomendação", "category": "ai"},
            {"code": "anomaly", "name": "Anomalia", "category": "ai"},
        ]

    def get_available_chart_types(self) -> list[dict[str, Any]]:
        """Retorna tipos de gráfico disponíveis."""
        return [
            {"code": "bar", "name": "Barras", "category": "comparison"},
            {"code": "line", "name": "Linha", "category": "trend"},
            {"code": "pie", "name": "Pizza", "category": "composition"},
            {"code": "donut", "name": "Rosca", "category": "composition"},
            {"code": "area", "name": "Área", "category": "trend"},
            {"code": "scatter", "name": "Dispersão", "category": "correlation"},
            {"code": "gauge", "name": "Velocímetro", "category": "kpi"},
            {"code": "funnel", "name": "Funil", "category": "flow"},
            {"code": "heatmap", "name": "Mapa de Calor", "category": "density"},
            {"code": "treemap", "name": "Treemap", "category": "hierarchy"},
        ]
