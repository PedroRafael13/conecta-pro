"""
Testes de API - Report Generator (Sprint 47)

Testes de integracao para os endpoints de geracao de relatorios.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient

from modules.ai.report_generator.models import (
    Report,
    ReportTemplate,
    ReportSchedule,
    ReportExecution,
)
from modules.ai.report_generator.models.report import (
    ReportTypeEnum,
    ReportStatusEnum,
    ReportFormatEnum,
    ReportPriorityEnum,
)
from modules.ai.report_generator.models.report_template import (
    TemplateCategoryEnum,
    TemplateStatusEnum,
)
from modules.ai.report_generator.models.report_schedule import (
    ScheduleFrequencyEnum,
    ScheduleStatusEnum,
)
from modules.ai.report_generator.schemas import (
    GenerateReportRequest,
    ReportTemplateCreate,
    ReportScheduleCreate,
)


# ============================================================
# Fixtures
# ============================================================

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
    report.period_start = datetime.utcnow() - timedelta(days=30)
    report.period_end = datetime.utcnow()
    report.period_description = "01/12/2024 a 31/12/2024"
    report.data = {"sales": {"total": 150000, "count": 450}}
    report.summary = {"total_revenue": 150000, "total_orders": 450}
    report.metrics = {"avg_ticket": 333.33, "growth": 15.5}
    report.insights = [
        {"type": "trend", "title": "Crescimento consistente", "description": "Vendas cresceram 15%"}
    ]
    report.recommendations = [
        {"action": "Expandir equipe de vendas", "priority": "high"}
    ]
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
    report.created_at = datetime.utcnow()
    report.generated_at = datetime.utcnow()
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
        "created_at": datetime.utcnow().isoformat(),
    }
    return report


@pytest.fixture
def mock_template():
    """Cria template mock."""
    template = MagicMock(spec=ReportTemplate)
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
    template.created_at = datetime.utcnow()
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
    schedule = MagicMock(spec=ReportSchedule)
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
    schedule.next_run_at = datetime.utcnow() + timedelta(hours=12)
    schedule.last_run_at = datetime.utcnow() - timedelta(hours=12)
    schedule.last_success_at = datetime.utcnow() - timedelta(hours=12)
    schedule.total_runs = 30
    schedule.successful_runs = 28
    schedule.failed_runs = 2
    schedule.success_rate = 93.3
    schedule.is_due = False
    schedule.is_expired = False
    schedule.created_at = datetime.utcnow()
    schedule.to_dict.return_value = {
        "id": str(schedule.id),
        "name": "Relatorio Diario de Vendas",
        "template_id": str(schedule.template_id),
        "frequency": "daily",
        "status": "active",
        "next_run_at": (datetime.utcnow() + timedelta(hours=12)).isoformat(),
        "last_run_at": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
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
    execution.started_at = datetime.utcnow() - timedelta(minutes=2)
    execution.completed_at = datetime.utcnow()
    execution.duration_ms = 120000
    execution.progress_percent = 100
    execution.records_processed = 5000
    execution.errors = []
    execution.created_at = datetime.utcnow()
    return execution


# ============================================================
# Tests - Report Generation Endpoints
# ============================================================

class TestReportGenerationEndpoints:
    """Testes para endpoints de geracao de relatorios."""

    @pytest.mark.asyncio
    async def test_generate_report_from_template(self, mock_report, mock_template):
        """Testa geracao de relatorio a partir de template."""
        request_data = GenerateReportRequest(
            template_id=mock_template.id,
            name="Relatorio Dezembro 2024",
            parameters={
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
            },
        )

        with patch(
            "modules.ai.report_generator.services.ReportGeneratorService"
        ) as MockService:
            mock_instance = AsyncMock()
            mock_instance.generate_report.return_value = mock_report
            MockService.return_value = mock_instance

            service = MockService(None)
            result = await service.generate_report(request_data)

            assert result.status == ReportStatusEnum.COMPLETED
            assert result.report_type == ReportTypeEnum.SALES

    @pytest.mark.asyncio
    async def test_generate_report_ad_hoc(self, mock_report):
        """Testa geracao de relatorio ad-hoc."""
        request_data = {
            "name": "Relatorio Ad-Hoc",
            "report_type": "analytical",
            "data_sources": ["customers", "orders"],
            "period_start": "2024-12-01",
            "period_end": "2024-12-31",
        }

        with patch(
            "modules.ai.report_generator.services.ReportGeneratorService"
        ) as MockService:
            mock_instance = AsyncMock()
            mock_report.report_type = ReportTypeEnum.AD_HOC
            mock_instance.generate_adhoc_report.return_value = mock_report
            MockService.return_value = mock_instance

            service = MockService(None)
            result = await service.generate_adhoc_report(request_data)

            assert result.report_type == ReportTypeEnum.AD_HOC

    @pytest.mark.asyncio
    async def test_list_reports(self, mock_report):
        """Testa listagem de relatorios."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_reports.return_value = ([mock_report], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_reports(page=1, page_size=50)

            assert total == 1
            assert len(items) == 1
            assert items[0].code == "REP-2025-001"

    @pytest.mark.asyncio
    async def test_get_report(self, mock_report):
        """Testa obtencao de relatorio."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_report.return_value = mock_report
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            result = await repo.get_report(mock_report.id)

            assert result.id == mock_report.id
            assert result.name == "Relatorio de Vendas Mensal"

    @pytest.mark.asyncio
    async def test_export_report_pdf(self, mock_report):
        """Testa exportacao de relatorio para PDF."""
        with patch(
            "modules.ai.report_generator.services.ReportExporter"
        ) as MockExporter:
            mock_instance = AsyncMock()
            mock_instance.export_report.return_value = {
                "format": "pdf",
                "filename": "REP-2025-001_20250105.pdf",
                "file_path": "/tmp/reports/REP-2025-001_20250105.pdf",
                "file_size_bytes": 125000,
                "pages": 5,
            }
            MockExporter.return_value = mock_instance

            exporter = MockExporter(None)
            result = await exporter.export_report(
                mock_report.id, ReportFormatEnum.PDF
            )

            assert result["format"] == "pdf"
            assert "file_path" in result

    @pytest.mark.asyncio
    async def test_export_report_excel(self, mock_report):
        """Testa exportacao de relatorio para Excel."""
        with patch(
            "modules.ai.report_generator.services.ReportExporter"
        ) as MockExporter:
            mock_instance = AsyncMock()
            mock_instance.export_report.return_value = {
                "format": "excel",
                "filename": "REP-2025-001_20250105.xlsx",
                "file_path": "/tmp/reports/REP-2025-001_20250105.xlsx",
                "file_size_bytes": 85000,
                "sheets": 4,
            }
            MockExporter.return_value = mock_instance

            exporter = MockExporter(None)
            result = await exporter.export_report(
                mock_report.id, ReportFormatEnum.EXCEL
            )

            assert result["format"] == "excel"
            assert result["sheets"] == 4


# ============================================================
# Tests - Template Endpoints
# ============================================================

class TestTemplateEndpoints:
    """Testes para endpoints de templates."""

    @pytest.mark.asyncio
    async def test_create_template(self, mock_template):
        """Testa criacao de template."""
        template_data = ReportTemplateCreate(
            code="tmpl_new",
            name="Novo Template",
            category=TemplateCategoryEnum.FINANCIAL,
            data_sources=["invoices", "payments"],
        )

        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            mock_instance = AsyncMock()
            mock_instance.create_template.return_value = mock_template
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.create_template(template_data)

            assert result.code == "TMPL-SALES-MONTHLY"

    @pytest.mark.asyncio
    async def test_list_templates(self, mock_template):
        """Testa listagem de templates."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_templates.return_value = ([mock_template], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_templates()

            assert total == 1
            assert items[0].category == TemplateCategoryEnum.SALES

    @pytest.mark.asyncio
    async def test_clone_template(self, mock_template):
        """Testa clonagem de template."""
        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            cloned = MagicMock(spec=ReportTemplate)
            cloned.code = "TMPL-SALES-MONTHLY-CLONE"
            cloned.name = "Template Vendas Mensal (Clone)"
            cloned.parent_template_id = mock_template.id

            mock_instance = AsyncMock()
            mock_instance.clone_template.return_value = cloned
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.clone_template(
                mock_template.id, "TMPL-SALES-MONTHLY-CLONE", "Template Clone"
            )

            assert result.parent_template_id == mock_template.id

    @pytest.mark.asyncio
    async def test_validate_template(self, mock_template):
        """Testa validacao de template."""
        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            mock_instance = AsyncMock()
            mock_instance.validate_template.return_value = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
            }
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.validate_template(mock_template.id)

            assert result["is_valid"] is True
            assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_publish_template(self, mock_template):
        """Testa publicacao de template."""
        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            mock_template.status = TemplateStatusEnum.ACTIVE
            mock_template.published_at = datetime.utcnow()

            mock_instance = AsyncMock()
            mock_instance.publish_template.return_value = mock_template
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.publish_template(mock_template.id)

            assert result.status == TemplateStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_initialize_default_templates(self, mock_template):
        """Testa inicializacao de templates padrao."""
        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            mock_instance = AsyncMock()
            mock_instance.initialize_default_templates.return_value = [mock_template]
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.initialize_default_templates()

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

        with patch(
            "modules.ai.report_generator.services.ReportScheduler"
        ) as MockScheduler:
            mock_instance = AsyncMock()
            mock_instance.create_schedule.return_value = mock_schedule
            MockScheduler.return_value = mock_instance

            scheduler = MockScheduler(None)
            result = await scheduler.create_schedule(schedule_data)

            assert result.frequency == ScheduleFrequencyEnum.DAILY

    @pytest.mark.asyncio
    async def test_list_schedules(self, mock_schedule):
        """Testa listagem de agendamentos."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_schedules.return_value = ([mock_schedule], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_schedules()

            assert total == 1
            assert items[0].status == ScheduleStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_pause_schedule(self, mock_schedule):
        """Testa pausa de agendamento."""
        with patch(
            "modules.ai.report_generator.services.ReportScheduler"
        ) as MockScheduler:
            mock_schedule.status = ScheduleStatusEnum.PAUSED

            mock_instance = AsyncMock()
            mock_instance.pause_schedule.return_value = mock_schedule
            MockScheduler.return_value = mock_instance

            scheduler = MockScheduler(None)
            result = await scheduler.pause_schedule(mock_schedule.id)

            assert result.status == ScheduleStatusEnum.PAUSED

    @pytest.mark.asyncio
    async def test_resume_schedule(self, mock_schedule):
        """Testa retomada de agendamento."""
        with patch(
            "modules.ai.report_generator.services.ReportScheduler"
        ) as MockScheduler:
            mock_schedule.status = ScheduleStatusEnum.ACTIVE

            mock_instance = AsyncMock()
            mock_instance.resume_schedule.return_value = mock_schedule
            MockScheduler.return_value = mock_instance

            scheduler = MockScheduler(None)
            result = await scheduler.resume_schedule(mock_schedule.id)

            assert result.status == ScheduleStatusEnum.ACTIVE

    @pytest.mark.asyncio
    async def test_process_due_schedules(self, mock_schedule, mock_report):
        """Testa processamento de agendamentos pendentes."""
        with patch(
            "modules.ai.report_generator.services.ReportScheduler"
        ) as MockScheduler:
            mock_instance = AsyncMock()
            mock_instance.process_due_schedules.return_value = {
                "processed": 5,
                "successful": 4,
                "failed": 1,
                "reports_generated": [str(mock_report.id)],
            }
            MockScheduler.return_value = mock_instance

            scheduler = MockScheduler(None)
            result = await scheduler.process_due_schedules()

            assert result["processed"] == 5
            assert result["successful"] == 4


# ============================================================
# Tests - Execution Endpoints
# ============================================================

class TestExecutionEndpoints:
    """Testes para endpoints de execucoes."""

    @pytest.mark.asyncio
    async def test_list_executions(self, mock_execution):
        """Testa listagem de execucoes."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_executions.return_value = ([mock_execution], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_executions()

            assert total == 1
            assert items[0].status == "completed"

    @pytest.mark.asyncio
    async def test_get_execution(self, mock_execution):
        """Testa obtencao de execucao."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_execution.return_value = mock_execution
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            result = await repo.get_execution(mock_execution.id)

            assert result.progress_percent == 100
            assert result.records_processed == 5000


# ============================================================
# Tests - Dashboard & Stats Endpoints
# ============================================================

class TestDashboardEndpoints:
    """Testes para endpoints de dashboard e estatisticas."""

    @pytest.mark.asyncio
    async def test_get_dashboard_data(self):
        """Testa obtencao de dados do dashboard."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_dashboard_data.return_value = {
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
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            result = await repo.get_dashboard_data()

            assert result["total_reports"] == 150
            assert result["reports_by_status"]["completed"] == 130

    @pytest.mark.asyncio
    async def test_get_report_stats(self):
        """Testa estatisticas de relatorios."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_report_stats.return_value = {
                "total": 150,
                "avg_generation_time_ms": 2500,
                "avg_quality_score": 82.5,
                "completion_rate": 95.0,
                "by_type": {
                    "sales": 50,
                    "financial": 40,
                },
            }
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            stats = await repo.get_report_stats()

            assert stats["total"] == 150
            assert stats["avg_quality_score"] == 82.5

    @pytest.mark.asyncio
    async def test_get_schedule_stats(self):
        """Testa estatisticas de agendamentos."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_schedule_stats.return_value = {
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
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            stats = await repo.get_schedule_stats()

            assert stats["total"] == 25
            assert stats["avg_success_rate"] == 92.5

    @pytest.mark.asyncio
    async def test_get_execution_metrics(self):
        """Testa metricas de execucoes."""
        with patch(
            "modules.ai.report_generator.repositories.ReportRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_execution_metrics.return_value = {
                "total_executions": 500,
                "successful": 475,
                "failed": 25,
                "success_rate": 95.0,
                "avg_duration_ms": 3500,
                "avg_records_processed": 8500,
            }
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            metrics = await repo.get_execution_metrics()

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
        with patch(
            "modules.ai.report_generator.services.InsightExtractor"
        ) as MockExtractor:
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
            MockExtractor.return_value = mock_instance

            extractor = MockExtractor(None)
            result = await extractor.extract_insights(mock_report.data)

            assert len(result) == 2
            assert result[0]["type"] == "trend"

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, mock_report):
        """Testa geracao de recomendacoes."""
        with patch(
            "modules.ai.report_generator.services.InsightExtractor"
        ) as MockExtractor:
            mock_instance = AsyncMock()
            mock_instance.generate_recommendations.return_value = [
                {
                    "action": "Aumentar equipe de vendas",
                    "expected_impact": "Aumento de 20% em vendas",
                    "priority": "high",
                    "effort": "medium",
                },
            ]
            MockExtractor.return_value = mock_instance

            extractor = MockExtractor(None)
            result = await extractor.generate_recommendations(
                mock_report.insights, mock_report.metrics
            )

            assert len(result) == 1
            assert result[0]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_detect_anomalies(self, mock_report):
        """Testa deteccao de anomalias."""
        with patch(
            "modules.ai.report_generator.services.InsightExtractor"
        ) as MockExtractor:
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
            MockExtractor.return_value = mock_instance

            extractor = MockExtractor(None)
            result = await extractor.detect_anomalies(mock_report.data)

            assert len(result) == 1
            assert result[0]["severity"] == "high"

    @pytest.mark.asyncio
    async def test_analyze_trends(self, mock_report):
        """Testa analise de tendencias."""
        with patch(
            "modules.ai.report_generator.services.InsightExtractor"
        ) as MockExtractor:
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
            MockExtractor.return_value = mock_instance

            extractor = MockExtractor(None)
            result = await extractor.analyze_trends(mock_report.data)

            assert len(result) == 1
            assert result[0]["direction"] == "increasing"


# ============================================================
# Tests - Metadata Endpoints
# ============================================================

class TestMetadataEndpoints:
    """Testes para endpoints de metadados."""

    @pytest.mark.asyncio
    async def test_get_available_data_sources(self):
        """Testa obtencao de fontes de dados disponiveis."""
        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            mock_instance = AsyncMock()
            mock_instance.get_available_data_sources.return_value = [
                {"code": "leads", "name": "Leads", "category": "crm"},
                {"code": "opportunities", "name": "Oportunidades", "category": "crm"},
                {"code": "invoices", "name": "Faturas", "category": "financial"},
            ]
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.get_available_data_sources()

            assert len(result) == 3
            assert result[0]["code"] == "leads"

    @pytest.mark.asyncio
    async def test_get_available_section_types(self):
        """Testa obtencao de tipos de secao disponiveis."""
        with patch(
            "modules.ai.report_generator.services.TemplateEngine"
        ) as MockEngine:
            mock_instance = AsyncMock()
            mock_instance.get_available_section_types.return_value = [
                {"type": "header", "name": "Cabecalho"},
                {"type": "kpi", "name": "KPIs"},
                {"type": "chart", "name": "Grafico"},
                {"type": "table", "name": "Tabela"},
            ]
            MockEngine.return_value = mock_instance

            engine = MockEngine(None)
            result = await engine.get_available_section_types()

            assert len(result) == 4
            assert result[0]["type"] == "header"

    @pytest.mark.asyncio
    async def test_get_supported_export_formats(self):
        """Testa obtencao de formatos de exportacao."""
        with patch(
            "modules.ai.report_generator.services.ReportExporter"
        ) as MockExporter:
            mock_instance = AsyncMock()
            mock_instance.get_supported_formats.return_value = [
                {"format": "pdf", "name": "PDF", "supports_charts": True},
                {"format": "excel", "name": "Excel", "supports_charts": False},
                {"format": "csv", "name": "CSV", "supports_charts": False},
                {"format": "json", "name": "JSON", "supports_charts": False},
                {"format": "html", "name": "HTML", "supports_charts": True},
            ]
            MockExporter.return_value = mock_instance

            exporter = MockExporter(None)
            result = await exporter.get_supported_formats()

            assert len(result) == 5
            assert result[0]["format"] == "pdf"
