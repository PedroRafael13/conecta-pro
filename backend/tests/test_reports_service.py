"""
Testes do Service do Sprint 34 - Relatórios Gerenciais
"""
# pylint: disable=redefined-outer-name,unused-argument
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from modules.reports.models import (
    ReportTemplate,
    ReportSchedule,
    ReportExport,
    ExecutiveKPI,
    Benchmark,
    ReportCategory,
    ReportFormat,
    ReportType,
    TemplateStatus,
    ScheduleFrequency,
    ScheduleStatus,
    DeliveryMethod,
    ExportStatus,
    ExportTrigger,
    ExportFormat,
    KPICategory,
    KPIType,
    KPIDirection,
    KPIStatus,
    KPIAlertLevel,
    AggregationPeriod,
    BenchmarkCategory,
    BenchmarkType,
    BenchmarkSource,
    BenchmarkStatus,
)
from modules.reports.services import ReportService


@pytest.fixture
def mock_db():
    """Fixture do mock de banco de dados."""
    return MagicMock()


@pytest.fixture
def report_service(mock_db):
    """Fixture do ReportService."""
    return ReportService(mock_db)


@pytest.fixture
def sample_template():
    """Fixture de template de exemplo."""
    return ReportTemplate(
        id=uuid.uuid4(),
        codigo="RPT001",
        nome="Relatório Financeiro",
        descricao="Relatório financeiro mensal",
        category=ReportCategory.FINANCEIRO,
        report_type=ReportType.CONSOLIDADO,
        default_format=ReportFormat.PDF,
        supported_formats=["pdf", "excel"],
        status=TemplateStatus.ATIVO,
        version=1,
        visibility="public",
        usage_count=0,
        ativo=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_schedule(sample_template):
    """Fixture de agendamento de exemplo."""
    return ReportSchedule(
        id=uuid.uuid4(),
        codigo="SCH001",
        nome="Agendamento Diário",
        template_id=sample_template.id,
        frequency=ScheduleFrequency.DIARIO,
        timezone="America/Sao_Paulo",
        status=ScheduleStatus.ATIVO,
        start_date=datetime.now(timezone.utc),
        output_format="pdf",
        delivery_method=DeliveryMethod.EMAIL,
        recipients=["user@example.com"],
        execution_count=0,
        success_count=0,
        failure_count=0,
        ativo=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_export(sample_template):
    """Fixture de exportação de exemplo."""
    return ReportExport(
        id=uuid.uuid4(),
        export_id="EXP001",
        template_id=sample_template.id,
        status=ExportStatus.CONCLUIDO,
        trigger=ExportTrigger.MANUAL,
        format=ExportFormat.PDF,
        file_name="report.pdf",
        file_path="/exports/report.pdf",
        file_size=1024,
        download_count=0,
        ativo=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_kpi():
    """Fixture de KPI de exemplo."""
    return ExecutiveKPI(
        id=uuid.uuid4(),
        codigo="KPI001",
        nome="Receita Mensal",
        descricao="Receita total do mês",
        category=KPICategory.FINANCEIRO,
        kpi_type=KPIType.RECEITA,
        direction=KPIDirection.MAIOR_MELHOR,
        status=KPIStatus.ATIVO,
        unit="currency",
        precision=2,
        current_value=Decimal("100000.00"),
        target_value=Decimal("120000.00"),
        alert_level=KPIAlertLevel.NORMAL,
        aggregation_period=AggregationPeriod.MENSAL,
        visibility="public",
        display_order=1,
        ativo=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_benchmark():
    """Fixture de benchmark de exemplo."""
    return Benchmark(
        id=uuid.uuid4(),
        codigo="BMK001",
        nome="Margem EBITDA",
        descricao="Benchmark de margem EBITDA do setor",
        category=BenchmarkCategory.FINANCEIRO,
        benchmark_type=BenchmarkType.INDUSTRIA,
        source=BenchmarkSource.PESQUISA_MERCADO,
        status=BenchmarkStatus.ATIVO,
        industry="Tecnologia",
        unit="percentage",
        precision=2,
        reference_value=Decimal("25.00"),
        company_value=Decimal("28.00"),
        visibility="public",
        ativo=True,
        created_at=datetime.now(timezone.utc),
    )


class TestReportTemplateService:
    """Testes do serviço de ReportTemplate."""

    def test_create_template(self, report_service, mock_db):
        """Testa criação de template."""
        with patch.object(
            report_service.repository, "create_template"
        ) as mock_create:
            mock_create.return_value = MagicMock(
                id=uuid.uuid4(),
                codigo="RPT001",
            )
            data = MagicMock(
                codigo="RPT001",
                nome="Relatório Teste",
                category="financeiro",
                report_type="consolidado",
                default_format="pdf",
                supported_formats=["pdf"],
            )
            result = report_service.create_template(data)
            assert result is not None
            mock_create.assert_called_once()

    def test_get_template(self, report_service, sample_template):
        """Testa busca de template."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            mock_get.return_value = sample_template
            result = report_service.get_template(sample_template.id)
            assert result == sample_template
            mock_get.assert_called_once_with(sample_template.id)

    def test_get_template_not_found(self, report_service):
        """Testa busca de template não encontrado."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            mock_get.return_value = None
            result = report_service.get_template(uuid.uuid4())
            assert result is None

    def test_list_templates(self, report_service, sample_template):
        """Testa listagem de templates."""
        with patch.object(
            report_service.repository, "list_templates"
        ) as mock_list:
            mock_list.return_value = ([sample_template], 1)
            result, total = report_service.list_templates()
            assert len(result) == 1
            assert total == 1

    def test_update_template(self, report_service, sample_template):
        """Testa atualização de template."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_template"
            ) as mock_update:
                mock_get.return_value = sample_template
                mock_update.return_value = sample_template
                data = MagicMock(nome="Relatório Atualizado")
                result = report_service.update_template(sample_template.id, data)
                assert result is not None

    def test_delete_template(self, report_service, sample_template):
        """Testa exclusão de template."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "delete_template"
            ) as mock_delete:
                mock_get.return_value = sample_template
                mock_delete.return_value = True
                result = report_service.delete_template(sample_template.id)
                assert result is True

    def test_activate_template(self, report_service, sample_template):
        """Testa ativação de template."""
        sample_template.status = TemplateStatus.RASCUNHO
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_template"
            ) as mock_update:
                mock_get.return_value = sample_template
                mock_update.return_value = sample_template
                result = report_service.activate_template(sample_template.id)
                assert result is not None

    def test_deactivate_template(self, report_service, sample_template):
        """Testa desativação de template."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_template"
            ) as mock_update:
                mock_get.return_value = sample_template
                mock_update.return_value = sample_template
                result = report_service.deactivate_template(sample_template.id)
                assert result is not None


class TestReportScheduleService:
    """Testes do serviço de ReportSchedule."""

    def test_create_schedule(self, report_service, sample_template):
        """Testa criação de agendamento."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get_template:
            with patch.object(
                report_service.repository, "create_schedule"
            ) as mock_create:
                mock_get_template.return_value = sample_template
                mock_create.return_value = MagicMock(
                    id=uuid.uuid4(),
                    codigo="SCH001",
                )
                data = MagicMock(
                    codigo="SCH001",
                    nome="Agendamento Teste",
                    template_id=sample_template.id,
                    frequency="diario",
                    timezone="America/Sao_Paulo",
                    start_date=datetime.now(timezone.utc),
                    output_format="pdf",
                    delivery_method="email",
                )
                result = report_service.create_schedule(data)
                assert result is not None

    def test_get_schedule(self, report_service, sample_schedule):
        """Testa busca de agendamento."""
        with patch.object(
            report_service.repository, "get_schedule_by_id"
        ) as mock_get:
            mock_get.return_value = sample_schedule
            result = report_service.get_schedule(sample_schedule.id)
            assert result == sample_schedule

    def test_list_schedules(self, report_service, sample_schedule):
        """Testa listagem de agendamentos."""
        with patch.object(
            report_service.repository, "list_schedules"
        ) as mock_list:
            mock_list.return_value = ([sample_schedule], 1)
            result, total = report_service.list_schedules()
            assert len(result) == 1
            assert total == 1

    def test_pause_schedule(self, report_service, sample_schedule):
        """Testa pausa de agendamento."""
        with patch.object(
            report_service.repository, "get_schedule_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_schedule"
            ) as mock_update:
                mock_get.return_value = sample_schedule
                mock_update.return_value = sample_schedule
                result = report_service.pause_schedule(sample_schedule.id)
                assert result is not None

    def test_resume_schedule(self, report_service, sample_schedule):
        """Testa retomada de agendamento."""
        sample_schedule.status = ScheduleStatus.PAUSADO
        with patch.object(
            report_service.repository, "get_schedule_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_schedule"
            ) as mock_update:
                mock_get.return_value = sample_schedule
                mock_update.return_value = sample_schedule
                result = report_service.resume_schedule(sample_schedule.id)
                assert result is not None

    def test_cancel_schedule(self, report_service, sample_schedule):
        """Testa cancelamento de agendamento."""
        with patch.object(
            report_service.repository, "get_schedule_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_schedule"
            ) as mock_update:
                mock_get.return_value = sample_schedule
                mock_update.return_value = sample_schedule
                result = report_service.cancel_schedule(sample_schedule.id)
                assert result is not None


class TestReportExportService:
    """Testes do serviço de ReportExport."""

    def test_request_export(self, report_service, sample_template):
        """Testa requisição de exportação."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get_template:
            with patch.object(
                report_service.repository, "create_export"
            ) as mock_create:
                mock_get_template.return_value = sample_template
                mock_create.return_value = MagicMock(
                    id=uuid.uuid4(),
                    export_id="EXP001",
                    status=ExportStatus.PENDENTE,
                )
                data = MagicMock(
                    template_id=sample_template.id,
                    format="pdf",
                )
                result = report_service.request_export(data, uuid.uuid4())
                assert result is not None

    def test_get_export(self, report_service, sample_export):
        """Testa busca de exportação."""
        with patch.object(
            report_service.repository, "get_export_by_id"
        ) as mock_get:
            mock_get.return_value = sample_export
            result = report_service.get_export(sample_export.id)
            assert result == sample_export

    def test_list_exports(self, report_service, sample_export):
        """Testa listagem de exportações."""
        with patch.object(
            report_service.repository, "list_exports"
        ) as mock_list:
            mock_list.return_value = ([sample_export], 1)
            result, total = report_service.list_exports()
            assert len(result) == 1
            assert total == 1

    def test_cancel_export(self, report_service, sample_export):
        """Testa cancelamento de exportação."""
        sample_export.status = ExportStatus.PENDENTE
        with patch.object(
            report_service.repository, "get_export_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_export"
            ) as mock_update:
                mock_get.return_value = sample_export
                mock_update.return_value = sample_export
                result = report_service.cancel_export(sample_export.id)
                assert result is not None


class TestExecutiveKPIService:
    """Testes do serviço de ExecutiveKPI."""

    def test_create_kpi(self, report_service):
        """Testa criação de KPI."""
        with patch.object(
            report_service.repository, "create_kpi"
        ) as mock_create:
            mock_create.return_value = MagicMock(
                id=uuid.uuid4(),
                codigo="KPI001",
            )
            data = MagicMock(
                codigo="KPI001",
                nome="Receita Mensal",
                category="financeiro",
                kpi_type="receita",
                direction="maior_melhor",
                unit="currency",
                aggregation_period="mensal",
            )
            result = report_service.create_kpi(data)
            assert result is not None

    def test_get_kpi(self, report_service, sample_kpi):
        """Testa busca de KPI."""
        with patch.object(
            report_service.repository, "get_kpi_by_id"
        ) as mock_get:
            mock_get.return_value = sample_kpi
            result = report_service.get_kpi(sample_kpi.id)
            assert result == sample_kpi

    def test_list_kpis(self, report_service, sample_kpi):
        """Testa listagem de KPIs."""
        with patch.object(
            report_service.repository, "list_kpis"
        ) as mock_list:
            mock_list.return_value = ([sample_kpi], 1)
            result, total = report_service.list_kpis()
            assert len(result) == 1
            assert total == 1

    def test_update_kpi_value(self, report_service, sample_kpi):
        """Testa atualização de valor de KPI."""
        with patch.object(
            report_service.repository, "get_kpi_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_kpi"
            ) as mock_update:
                mock_get.return_value = sample_kpi
                mock_update.return_value = sample_kpi
                result = report_service.update_kpi_value(
                    sample_kpi.id,
                    Decimal("150000.00"),
                )
                assert result is not None

    def test_activate_kpi(self, report_service, sample_kpi):
        """Testa ativação de KPI."""
        sample_kpi.status = KPIStatus.RASCUNHO
        with patch.object(
            report_service.repository, "get_kpi_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_kpi"
            ) as mock_update:
                mock_get.return_value = sample_kpi
                mock_update.return_value = sample_kpi
                result = report_service.activate_kpi(sample_kpi.id)
                assert result is not None

    def test_deactivate_kpi(self, report_service, sample_kpi):
        """Testa desativação de KPI."""
        with patch.object(
            report_service.repository, "get_kpi_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_kpi"
            ) as mock_update:
                mock_get.return_value = sample_kpi
                mock_update.return_value = sample_kpi
                result = report_service.deactivate_kpi(sample_kpi.id)
                assert result is not None

    def test_get_kpi_dashboard(self, report_service, sample_kpi):
        """Testa dashboard de KPIs."""
        with patch.object(
            report_service.repository, "get_dashboard_kpis"
        ) as mock_dash:
            with patch.object(
                report_service.repository, "get_kpis_needing_attention"
            ) as mock_attention:
                mock_dash.return_value = [sample_kpi]
                mock_attention.return_value = []
                result = report_service.get_kpi_dashboard()
                assert "kpis" in result


class TestBenchmarkService:
    """Testes do serviço de Benchmark."""

    def test_create_benchmark(self, report_service):
        """Testa criação de benchmark."""
        with patch.object(
            report_service.repository, "create_benchmark"
        ) as mock_create:
            mock_create.return_value = MagicMock(
                id=uuid.uuid4(),
                codigo="BMK001",
            )
            data = MagicMock(
                codigo="BMK001",
                nome="Margem EBITDA",
                category="financeiro",
                benchmark_type="industria",
                source="pesquisa_mercado",
                unit="percentage",
            )
            result = report_service.create_benchmark(data)
            assert result is not None

    def test_get_benchmark(self, report_service, sample_benchmark):
        """Testa busca de benchmark."""
        with patch.object(
            report_service.repository, "get_benchmark_by_id"
        ) as mock_get:
            mock_get.return_value = sample_benchmark
            result = report_service.get_benchmark(sample_benchmark.id)
            assert result == sample_benchmark

    def test_list_benchmarks(self, report_service, sample_benchmark):
        """Testa listagem de benchmarks."""
        with patch.object(
            report_service.repository, "list_benchmarks"
        ) as mock_list:
            mock_list.return_value = ([sample_benchmark], 1)
            result, total = report_service.list_benchmarks()
            assert len(result) == 1
            assert total == 1

    def test_update_benchmark_company_value(
        self, report_service, sample_benchmark
    ):
        """Testa atualização de valor da empresa."""
        with patch.object(
            report_service.repository, "get_benchmark_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_benchmark"
            ) as mock_update:
                mock_get.return_value = sample_benchmark
                mock_update.return_value = sample_benchmark
                result = report_service.update_benchmark_company_value(
                    sample_benchmark.id,
                    Decimal("30.00"),
                )
                assert result is not None

    def test_activate_benchmark(self, report_service, sample_benchmark):
        """Testa ativação de benchmark."""
        sample_benchmark.status = BenchmarkStatus.RASCUNHO
        with patch.object(
            report_service.repository, "get_benchmark_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_benchmark"
            ) as mock_update:
                mock_get.return_value = sample_benchmark
                mock_update.return_value = sample_benchmark
                result = report_service.activate_benchmark(sample_benchmark.id)
                assert result is not None

    def test_deactivate_benchmark(self, report_service, sample_benchmark):
        """Testa desativação de benchmark."""
        with patch.object(
            report_service.repository, "get_benchmark_by_id"
        ) as mock_get:
            with patch.object(
                report_service.repository, "update_benchmark"
            ) as mock_update:
                mock_get.return_value = sample_benchmark
                mock_update.return_value = sample_benchmark
                result = report_service.deactivate_benchmark(sample_benchmark.id)
                assert result is not None


class TestDashboardService:
    """Testes do serviço de Dashboard."""

    def test_get_reports_dashboard(self, report_service):
        """Testa dashboard de relatórios."""
        with patch.object(
            report_service.repository, "get_reports_dashboard_stats"
        ) as mock_stats:
            with patch.object(
                report_service.repository, "get_top_templates"
            ) as mock_top:
                with patch.object(
                    report_service.repository, "get_due_schedules"
                ) as mock_due:
                    with patch.object(
                        report_service.repository, "get_pending_exports"
                    ) as mock_pending:
                        mock_stats.return_value = {
                            "total_templates": 10,
                            "active_templates": 8,
                            "total_schedules": 5,
                            "active_schedules": 4,
                            "total_exports": 100,
                            "completed_exports": 95,
                        }
                        mock_top.return_value = []
                        mock_due.return_value = []
                        mock_pending.return_value = []
                        result = report_service.get_reports_dashboard()
                        assert "stats" in result

    def test_get_executive_dashboard(self, report_service, sample_kpi, sample_benchmark):
        """Testa dashboard executivo."""
        with patch.object(
            report_service.repository, "get_dashboard_kpis"
        ) as mock_kpis:
            with patch.object(
                report_service.repository, "get_dashboard_benchmarks"
            ) as mock_benchmarks:
                with patch.object(
                    report_service.repository, "get_kpis_needing_attention"
                ) as mock_attention:
                    with patch.object(
                        report_service.repository, "get_benchmarks_below_target"
                    ) as mock_below:
                        mock_kpis.return_value = [sample_kpi]
                        mock_benchmarks.return_value = [sample_benchmark]
                        mock_attention.return_value = []
                        mock_below.return_value = []
                        result = report_service.get_executive_dashboard()
                        assert "kpis" in result
                        assert "benchmarks" in result


class TestServiceErrorHandling:
    """Testes de tratamento de erros do serviço."""

    def test_get_nonexistent_template(self, report_service):
        """Testa busca de template inexistente."""
        with patch.object(
            report_service.repository, "get_template_by_id"
        ) as mock_get:
            mock_get.return_value = None
            result = report_service.get_template(uuid.uuid4())
            assert result is None

    def test_get_nonexistent_schedule(self, report_service):
        """Testa busca de agendamento inexistente."""
        with patch.object(
            report_service.repository, "get_schedule_by_id"
        ) as mock_get:
            mock_get.return_value = None
            result = report_service.get_schedule(uuid.uuid4())
            assert result is None

    def test_get_nonexistent_export(self, report_service):
        """Testa busca de exportação inexistente."""
        with patch.object(
            report_service.repository, "get_export_by_id"
        ) as mock_get:
            mock_get.return_value = None
            result = report_service.get_export(uuid.uuid4())
            assert result is None

    def test_get_nonexistent_kpi(self, report_service):
        """Testa busca de KPI inexistente."""
        with patch.object(
            report_service.repository, "get_kpi_by_id"
        ) as mock_get:
            mock_get.return_value = None
            result = report_service.get_kpi(uuid.uuid4())
            assert result is None

    def test_get_nonexistent_benchmark(self, report_service):
        """Testa busca de benchmark inexistente."""
        with patch.object(
            report_service.repository, "get_benchmark_by_id"
        ) as mock_get:
            mock_get.return_value = None
            result = report_service.get_benchmark(uuid.uuid4())
            assert result is None
