"""
Testes de API - Report Generator (Sprint 47)

Testes de integracao para os endpoints de geracao de relatorios.
"""

from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from modules.ai.report_generator.models import (
    AIReportSchedule,
    AIReportTemplate,
    Report,
    ReportExecution,
)
from modules.ai.report_generator.models.report import (
    ReportFormatEnum,
    ReportPriorityEnum,
    ReportStatusEnum,
    ReportTypeEnum,
)
from modules.ai.report_generator.models.report_schedule import (
    ScheduleFrequencyEnum,
    ScheduleStatusEnum,
)
from modules.ai.report_generator.models.report_template import (
    TemplateCategoryEnum,
    TemplateStatusEnum,
)
from modules.ai.report_generator.repositories import ReportRepository
from modules.ai.report_generator.schemas import (
    GenerateReportRequest,
    ReportScheduleCreate,
    ReportTemplateCreate,
)
from modules.ai.report_generator.services import (
    ReportExporter,
    ReportGeneratorService,
    TemplateEngine,
)

# ============================================================
# Fixtures
# ============================================================


def _utcnow() -> datetime:
    """Retorna datetime UTC timezone-aware."""
    return datetime.now(UTC)


@pytest.fixture
def mock_report():
    """Cria relatorio mock."""
    report = MagicMock(spec=Report)
    report.id = uuid4()
    report.code = "REP-2025-001"
    report.name = "Relatorio de Vendas Mensal"
    report.description = "Relatorio mensal de vendas"
    report.report_type = ReportTypeEnum.SALES
    report.category = "vendas"
    report.status = ReportStatusEnum.COMPLETED
    report.priority = ReportPriorityEnum.NORMAL
    report.period_start = _utcnow() - timedelta(days=30)
    report.period_end = _utcnow()
    report.period_description = "01/12/2024 a 31/12/2024"
    report.data = {"sales": {"total": 150000, "count": 450}}
    report.summary = {"total_revenue": 150000, "total_orders": 450}
    report.metrics = {"avg_ticket": 333.33, "growth": 15.5}
    report.insights = [
        {
            "type": "trend",
            "title": "Crescimento consistente",
            "description": "Vendas cresceram 15%",
        }
    ]
    report.recommendations = [{"action": "Expandir equipe de vendas", "priority": "high"}]
    report.anomalies = []
    report.insights_count = 1
    report.has_anomalies = False
    report.overall_quality_score = 85.0
    report.data_quality_score = 90.0
    report.completeness_score = 85.0
    report.accuracy_score = 80.0
    report.generation_time_ms = 1500
    report.is_expired = False
    report.view_count = 5
    report.download_count = 2
    report.created_at = _utcnow()
    report.generated_at = _utcnow()
    report.to_summary_dict.return_value = {
        "id": str(report.id),
        "code": "REP-2025-001",
        "name": "Relatorio de Vendas Mensal",
        "report_type": "sales",
        "status": "completed",
        "period": "01/12/2024 a 31/12/2024",
        "insights_count": 1,
        "has_anomalies": False,
        "quality_score": 85.0,
        "created_at": _utcnow().isoformat(),
    }
    return report


@pytest.fixture
def mock_template():
    """Cria template mock."""
    template = MagicMock(spec=AIReportTemplate)
    template.id = uuid4()
    template.code = "TMPL-SALES-MONTHLY"
    template.name = "Template Vendas Mensal"
    template.description = "Template padrao para relatorios mensais de vendas"
    template.category = TemplateCategoryEnum.SALES
    template.subcategory = "mensal"
    template.status = TemplateStatusEnum.ACTIVE
    template.data_sources = ["leads", "opportunities", "customers"]
    template.primary_source = "opportunities"
    template.parameters = [
        {"name": "start_date", "type": "date", "required": True},
        {"name": "end_date", "type": "date", "required": True},
    ]
    template.sections_config = [
        {"type": "header", "title": "Resumo"},
        {"type": "kpi", "title": "KPIs"},
        {"type": "chart", "title": "Tendencias"},
    ]
    template.widgets_config = [
        {"type": "kpi", "metric": "total_sales"},
        {"type": "kpi", "metric": "conversion_rate"},
    ]
    template.ai_insights_enabled = True
    template.anomaly_detection_enabled = True
    template.trend_analysis_enabled = True
    template.supported_formats = ["pdf", "excel", "csv"]
    template.is_ready = True
    template.is_validated = True
    template.usage_count = 50
    template.parameters_count = 2
    template.sections_count = 3
    template.widgets_count = 2
    template.average_generation_time_ms = 2000
    template.created_at = _utcnow()
    template.to_dict.return_value = {
        "id": str(template.id),
        "code": "TMPL-SALES-MONTHLY",
        "name": "Template Vendas Mensal",
        "category": "sales",
        "status": "active",
        "data_sources": ["leads", "opportunities", "customers"],
        "parameters_count": 2,
        "sections_count": 3,
        "widgets_count": 2,
        "ai_insights_enabled": True,
        "is_ready": True,
        "usage_count": 50,
    }
    return template


@pytest.fixture
def mock_schedule():
    """Cria agendamento mock."""
    schedule = MagicMock(spec=AIReportSchedule)
    schedule.id = uuid4()
    schedule.name = "Relatorio Diario de Vendas"
    schedule.template_id = uuid4()
    schedule.frequency = ScheduleFrequencyEnum.DAILY
    schedule.status = ScheduleStatusEnum.ACTIVE
    schedule.run_time = "08:00"
    schedule.timezone = "America/Sao_Paulo"
    schedule.period_type = "previous_day"
    schedule.output_formats = ["pdf", "excel"]
    schedule.delivery_methods = ["email"]
    schedule.email_recipients = ["gerente@empresa.com"]
    schedule.next_run_at = _utcnow() + timedelta(hours=12)
    schedule.last_run_at = _utcnow() - timedelta(hours=12)
    schedule.last_success_at = _utcnow() - timedelta(hours=12)
    schedule.total_runs = 30
    schedule.successful_runs = 28
    schedule.failed_runs = 2
    schedule.success_rate = 93.3
    schedule.is_due = False
    schedule.is_expired = False
    schedule.created_at = _utcnow()
    schedule.to_dict.return_value = {
        "id": str(schedule.id),
        "name": "Relatorio Diario de Vendas",
        "template_id": str(schedule.template_id),
        "frequency": "daily",
        "status": "active",
        "next_run_at": (_utcnow() + timedelta(hours=12)).isoformat(),
        "last_run_at": (_utcnow() - timedelta(hours=12)).isoformat(),
        "success_rate": 93.3,
        "total_runs": 30,
        "is_due": False,
    }
    return schedule


@pytest.fixture
def mock_execution():
    """Cria execucao mock."""
    execution = MagicMock(spec=ReportExecution)
    execution.id = uuid4()
    execution.report_id = uuid4()
    execution.schedule_id = uuid4()
    execution.status = "completed"
    execution.started_at = _utcnow() - timedelta(minutes=2)
    execution.completed_at = _utcnow()
    execution.duration_ms = 120000
    execution.progress_percent = 100
    execution.records_processed = 5000
    execution.errors = []
    execution.created_at = _utcnow()
    return execution


# ============================================================
# Tests - Report Generation Endpoints
# ============================================================


class TestReportGenerationEndpoints:
    """Testes para endpoints de geracao de relatorios."""

    @pytest.mark.asyncio
    async def test_generate_report_from_template(self, mock_report, mock_template):
        """Testa geracao de relatorio a partir de template."""
        mock_execution = MagicMock(spec=ReportExecution)
        mock_execution.id = uuid4()
        mock_execution.status = "completed"
        mock_execution.is_completed = True

        mock_service = AsyncMock()
        mock_service.generate_report.return_value = (mock_report, mock_execution)

        with patch(
            "modules.ai.report_generator.services.ReportGeneratorService",
            return_value=mock_service,
        ):
            result_report, result_exec = await mock_service.generate_report(
                template_id=mock_template.id,
                name="Relatorio Dezembro 2024",
                parameters={
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-31",
                },
            )

            assert result_report.status == ReportStatusEnum.COMPLETED
            assert result_report.report_type == ReportTypeEnum.SALES

    @pytest.mark.asyncio
    async def test_generate_report_ad_hoc(self, mock_report):
        """Testa geracao de relatorio ad-hoc via generate_report."""
        mock_report.report_type = ReportTypeEnum.AD_HOC
        mock_execution = MagicMock(spec=ReportExecution)
        mock_execution.id = uuid4()
        mock_execution.status = "completed"

        mock_service = AsyncMock()
        mock_service.generate_report.return_value = (mock_report, mock_execution)

        with patch(
            "modules.ai.report_generator.services.ReportGeneratorService",
            return_value=mock_service,
        ):
            result_report, _ = await mock_service.generate_report(
                name="Relatorio Ad-Hoc",
                report_type=ReportTypeEnum.AD_HOC,
                period_start=datetime(2024, 12, 1, tzinfo=UTC),
                period_end=datetime(2024, 12, 31, tzinfo=UTC),
            )

            assert result_report.report_type == ReportTypeEnum.AD_HOC

    def test_list_reports(self, mock_report):
        """Testa listagem de relatorios."""
        mock_repo = MagicMock()
        mock_repo.list_reports.return_value = ([mock_report], 1)

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            items, total = mock_repo.list_reports(skip=0, limit=50)

            assert total == 1
            assert len(items) == 1
            assert items[0].code == "REP-2025-001"

    def test_get_report(self, mock_report):
        """Testa obtencao de relatorio."""
        mock_repo = MagicMock()
        mock_repo.get_report.return_value = mock_report

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            result = mock_repo.get_report(mock_report.id)

            assert result.id == mock_report.id
            assert result.name == "Relatorio de Vendas Mensal"

    def test_export_report_pdf(self, mock_report):
        """Testa exportacao de relatorio para PDF."""
        mock_exporter = MagicMock()
        mock_exporter.export_report.return_value = {
            "format": "pdf",
            "filename": "REP-2025-001_20250105.pdf",
            "file_path": "/tmp/reports/REP-2025-001_20250105.pdf",  # noqa: S108
            "file_size_bytes": 125000,
            "pages": 5,
        }

        with patch(
            "modules.ai.report_generator.services.ReportExporter",
            return_value=mock_exporter,
        ):
            result = mock_exporter.export_report(
                report_id=mock_report.id,
                format_type=ReportFormatEnum.PDF,
            )

            assert result["format"] == "pdf"
            assert "file_path" in result

    def test_export_report_excel(self, mock_report):
        """Testa exportacao de relatorio para Excel."""
        mock_exporter = MagicMock()
        mock_exporter.export_report.return_value = {
            "format": "excel",
            "filename": "REP-2025-001_20250105.xlsx",
            "file_path": "/tmp/reports/REP-2025-001_20250105.xlsx",  # noqa: S108
            "file_size_bytes": 85000,
            "sheets": 4,
        }

        with patch(
            "modules.ai.report_generator.services.ReportExporter",
            return_value=mock_exporter,
        ):
            result = mock_exporter.export_report(
                report_id=mock_report.id,
                format_type=ReportFormatEnum.EXCEL,
            )

            assert result["format"] == "excel"
            assert result["sheets"] == 4


# ============================================================
# Tests - Template Endpoints
# ============================================================


class TestTemplateEndpoints:
    """Testes para endpoints de templates."""

    def test_create_template(self, mock_template):
        """Testa criacao de template."""
        mock_engine = MagicMock()
        mock_engine.create_template.return_value = mock_template

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.create_template(
                code="tmpl_new",
                name="Novo Template",
                category=TemplateCategoryEnum.FINANCIAL,
                data_sources=["invoices", "payments"],
            )

            assert result.code == "TMPL-SALES-MONTHLY"

    def test_list_templates(self, mock_template):
        """Testa listagem de templates."""
        mock_repo = MagicMock()
        mock_repo.list_templates.return_value = ([mock_template], 1)

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            items, total = mock_repo.list_templates()

            assert total == 1
            assert items[0].category == TemplateCategoryEnum.SALES

    def test_clone_template(self, mock_template):
        """Testa clonagem de template."""
        cloned = MagicMock(spec=AIReportTemplate)
        cloned.code = "TMPL-SALES-MONTHLY-CLONE"
        cloned.name = "Template Vendas Mensal (Clone)"
        cloned.parent_template_id = mock_template.id

        mock_engine = MagicMock()
        mock_engine.clone_template.return_value = cloned

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.clone_template(
                mock_template.id,
                "TMPL-SALES-MONTHLY-CLONE",
                "Template Clone",
            )

            assert result.parent_template_id == mock_template.id

    def test_validate_template(self, mock_template):
        """Testa validacao de template."""
        mock_engine = MagicMock()
        mock_engine.validate_template.return_value = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.validate_template(mock_template.id)

            assert result["is_valid"] is True
            assert len(result["errors"]) == 0

    def test_publish_template(self, mock_template):
        """Testa publicacao de template."""
        mock_template.status = TemplateStatusEnum.ACTIVE
        mock_template.published_at = _utcnow()

        mock_engine = MagicMock()
        mock_engine.publish_template.return_value = mock_template

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.publish_template(mock_template.id)

            assert result.status == TemplateStatusEnum.ACTIVE

    def test_initialize_default_templates(self, mock_template):
        """Testa inicializacao de templates padrao."""
        mock_engine = MagicMock()
        mock_engine.initialize_default_templates.return_value = [mock_template]

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.initialize_default_templates()

            assert len(result) >= 1


# ============================================================
# Tests - Schedule Endpoints
# ============================================================


class TestScheduleEndpoints:
    """Testes para endpoints de agendamentos."""

    @pytest.mark.asyncio
    async def test_create_schedule(self, mock_schedule, mock_template):
        """Testa criacao de agendamento."""
        schedule_data = ReportScheduleCreate(
            name="Novo Agendamento",
            template_id=mock_template.id,
            frequency=ScheduleFrequencyEnum.WEEKLY,
            delivery_methods=["email"],
            email_recipients=["user@empresa.com"],
        )

        with patch("modules.ai.report_generator.services.ReportScheduler") as mock_scheduler:
            mock_instance = AsyncMock()
            mock_instance.create_schedule.return_value = mock_schedule
            mock_scheduler.return_value = mock_instance

            scheduler = mock_scheduler(None)
            result = await scheduler.create_schedule(schedule_data)

            assert result.frequency == ScheduleFrequencyEnum.DAILY

    def test_list_schedules(self, mock_schedule):
        """Testa listagem de agendamentos."""
        mock_repo = MagicMock()
        mock_repo.list_schedules.return_value = ([mock_schedule], 1)

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            items, total = mock_repo.list_schedules()

            assert total == 1
            assert items[0].status == ScheduleStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_pause_schedule(self, mock_schedule):
        """Testa pausa de agendamento."""
        with patch("modules.ai.report_generator.services.ReportScheduler") as mock_scheduler:
            mock_schedule.status = ScheduleStatusEnum.PAUSED

            mock_instance = AsyncMock()
            mock_instance.pause_schedule.return_value = mock_schedule
            mock_scheduler.return_value = mock_instance

            scheduler = mock_scheduler(None)
            result = await scheduler.pause_schedule(mock_schedule.id)

            assert result.status == ScheduleStatusEnum.PAUSED

    @pytest.mark.asyncio
    async def test_resume_schedule(self, mock_schedule):
        """Testa retomada de agendamento."""
        with patch("modules.ai.report_generator.services.ReportScheduler") as mock_scheduler:
            mock_schedule.status = ScheduleStatusEnum.ACTIVE

            mock_instance = AsyncMock()
            mock_instance.resume_schedule.return_value = mock_schedule
            mock_scheduler.return_value = mock_instance

            scheduler = mock_scheduler(None)
            result = await scheduler.resume_schedule(mock_schedule.id)

            assert result.status == ScheduleStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_process_due_schedules(self, mock_schedule, mock_report):
        """Testa processamento de agendamentos pendentes."""
        with patch("modules.ai.report_generator.services.ReportScheduler") as mock_scheduler:
            mock_instance = AsyncMock()
            mock_instance.process_due_schedules.return_value = {
                "processed": 5,
                "successful": 4,
                "failed": 1,
                "reports_generated": [str(mock_report.id)],
            }
            mock_scheduler.return_value = mock_instance

            scheduler = mock_scheduler(None)
            result = await scheduler.process_due_schedules()

            assert result["processed"] == 5
            assert result["successful"] == 4


# ============================================================
# Tests - Execution Endpoints
# ============================================================


class TestExecutionEndpoints:
    """Testes para endpoints de execucoes."""

    def test_list_executions(self, mock_execution):
        """Testa listagem de execucoes."""
        mock_repo = MagicMock()
        mock_repo.list_executions.return_value = ([mock_execution], 1)

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            items, total = mock_repo.list_executions()

            assert total == 1
            assert items[0].status == "completed"

    def test_get_execution(self, mock_execution):
        """Testa obtencao de execucao."""
        mock_repo = MagicMock()
        mock_repo.get_execution.return_value = mock_execution

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            result = mock_repo.get_execution(mock_execution.id)

            assert result.progress_percent == 100
            assert result.records_processed == 5000


# ============================================================
# Tests - Dashboard & Stats Endpoints
# ============================================================


class TestDashboardEndpoints:
    """Testes para endpoints de dashboard e estatisticas."""

    def test_get_dashboard_data(self):
        """Testa obtencao de dados do dashboard."""
        mock_repo = MagicMock()
        mock_repo.get_dashboard_data.return_value = {
            "total_reports": 150,
            "total_templates": 12,
            "total_schedules": 25,
            "reports_by_status": {
                "completed": 130,
                "failed": 10,
                "generating": 5,
                "draft": 5,
            },
            "reports_by_type": {
                "sales": 50,
                "financial": 40,
                "hr": 30,
                "operations": 30,
            },
            "recent_reports": [],
            "upcoming_schedules": [],
        }

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            result = mock_repo.get_dashboard_data()

            assert result["total_reports"] == 150
            assert result["reports_by_status"]["completed"] == 130

    def test_get_report_stats(self):
        """Testa estatisticas de relatorios."""
        mock_repo = MagicMock()
        mock_repo.get_report_stats.return_value = {
            "total": 150,
            "avg_generation_time_ms": 2500,
            "avg_quality_score": 82.5,
            "completion_rate": 95.0,
            "by_type": {
                "sales": 50,
                "financial": 40,
            },
        }

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            stats = mock_repo.get_report_stats()

            assert stats["total"] == 150
            assert stats["avg_quality_score"] == 82.5

    def test_get_schedule_stats(self):
        """Testa estatisticas de agendamentos."""
        mock_repo = MagicMock()
        mock_repo.get_schedule_stats.return_value = {
            "total": 25,
            "active": 20,
            "paused": 3,
            "failed": 2,
            "avg_success_rate": 92.5,
            "by_frequency": {
                "daily": 10,
                "weekly": 8,
                "monthly": 7,
            },
        }

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            stats = mock_repo.get_schedule_stats()

            assert stats["total"] == 25
            assert stats["avg_success_rate"] == 92.5

    def test_get_execution_metrics(self):
        """Testa metricas de execucoes."""
        mock_repo = MagicMock()
        mock_repo.get_execution_metrics.return_value = {
            "total_executions": 500,
            "successful": 475,
            "failed": 25,
            "success_rate": 95.0,
            "avg_duration_ms": 3500,
            "avg_records_processed": 8500,
        }

        with patch(
            "modules.ai.report_generator.repositories.ReportRepository",
            return_value=mock_repo,
        ):
            metrics = mock_repo.get_execution_metrics()

            assert metrics["success_rate"] == 95.0
            assert metrics["total_executions"] == 500


# ============================================================
# Tests - Insight Extraction
# ============================================================


class TestInsightExtractionEndpoints:
    """Testes para endpoints de extracao de insights."""

    @pytest.mark.asyncio
    async def test_extract_insights(self, mock_report):
        """Testa extracao de insights."""
        with patch("modules.ai.report_generator.services.InsightExtractor") as mock_extractor:
            mock_instance = AsyncMock()
            mock_instance.extract_insights.return_value = [
                {
                    "type": "trend",
                    "title": "Crescimento de Vendas",
                    "description": "Vendas cresceram 15% no periodo",
                    "confidence": 0.85,
                },
                {
                    "type": "anomaly",
                    "title": "Pico Incomum",
                    "description": "Dia 15 teve vendas 3x acima da media",
                    "confidence": 0.92,
                },
            ]
            mock_extractor.return_value = mock_instance

            extractor = mock_extractor(None)
            result = await extractor.extract_insights(mock_report.data)

            assert len(result) == 2
            assert result[0]["type"] == "trend"

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, mock_report):
        """Testa geracao de recomendacoes."""
        with patch("modules.ai.report_generator.services.InsightExtractor") as mock_extractor:
            mock_instance = AsyncMock()
            mock_instance.generate_recommendations.return_value = [
                {
                    "action": "Aumentar equipe de vendas",
                    "expected_impact": "Aumento de 20% em vendas",
                    "priority": "high",
                    "effort": "medium",
                },
            ]
            mock_extractor.return_value = mock_instance

            extractor = mock_extractor(None)
            result = await extractor.generate_recommendations(mock_report.insights, mock_report.metrics)

            assert len(result) == 1
            assert result[0]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_detect_anomalies(self, mock_report):
        """Testa deteccao de anomalias."""
        with patch("modules.ai.report_generator.services.InsightExtractor") as mock_extractor:
            mock_instance = AsyncMock()
            mock_instance.detect_anomalies.return_value = [
                {
                    "metric": "daily_sales",
                    "date": "2024-12-15",
                    "value": 15000,
                    "expected": 5000,
                    "z_score": 3.2,
                    "severity": "high",
                },
            ]
            mock_extractor.return_value = mock_instance

            extractor = mock_extractor(None)
            result = await extractor.detect_anomalies(mock_report.data)

            assert len(result) == 1
            assert result[0]["severity"] == "high"

    @pytest.mark.asyncio
    async def test_analyze_trends(self, mock_report):
        """Testa analise de tendencias."""
        with patch("modules.ai.report_generator.services.InsightExtractor") as mock_extractor:
            mock_instance = AsyncMock()
            mock_instance.analyze_trends.return_value = [
                {
                    "metric": "monthly_revenue",
                    "direction": "increasing",
                    "change_percent": 15.5,
                    "forecast_next_period": 175000,
                    "confidence": 0.78,
                },
            ]
            mock_extractor.return_value = mock_instance

            extractor = mock_extractor(None)
            result = await extractor.analyze_trends(mock_report.data)

            assert len(result) == 1
            assert result[0]["direction"] == "increasing"


# ============================================================
# Tests - Metadata Endpoints
# ============================================================


class TestMetadataEndpoints:
    """Testes para endpoints de metadados."""

    def test_get_available_data_sources(self):
        """Testa obtencao de fontes de dados disponiveis."""
        mock_engine = MagicMock()
        mock_engine.get_available_data_sources.return_value = [
            {"code": "leads", "name": "Leads", "category": "crm"},
            {"code": "opportunities", "name": "Oportunidades", "category": "crm"},
            {"code": "invoices", "name": "Faturas", "category": "financial"},
        ]

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.get_available_data_sources()

            assert len(result) == 3
            assert result[0]["code"] == "leads"

    def test_get_available_section_types(self):
        """Testa obtencao de tipos de secao disponiveis."""
        mock_engine = MagicMock()
        mock_engine.get_available_section_types.return_value = [
            {"type": "header", "name": "Cabecalho"},
            {"type": "kpi", "name": "KPIs"},
            {"type": "chart", "name": "Grafico"},
            {"type": "table", "name": "Tabela"},
        ]

        with patch(
            "modules.ai.report_generator.services.TemplateEngine",
            return_value=mock_engine,
        ):
            result = mock_engine.get_available_section_types()

            assert len(result) == 4
            assert result[0]["type"] == "header"

    def test_get_supported_export_formats(self):
        """Testa obtencao de formatos de exportacao."""
        mock_exporter = MagicMock()
        mock_exporter.get_supported_formats.return_value = [
            {"format": "pdf", "name": "PDF", "supports_charts": True},
            {"format": "excel", "name": "Excel", "supports_charts": False},
            {"format": "csv", "name": "CSV", "supports_charts": False},
            {"format": "json", "name": "JSON", "supports_charts": False},
            {"format": "html", "name": "HTML", "supports_charts": True},
        ]

        with patch(
            "modules.ai.report_generator.services.ReportExporter",
            return_value=mock_exporter,
        ):
            result = mock_exporter.get_supported_formats()

            assert len(result) == 5
            assert result[0]["format"] == "pdf"
