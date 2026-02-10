"""
Testes dos Models do Sprint 34 - Relatórios Gerenciais
"""

# pylint: disable=redefined-outer-name,unused-argument
import uuid
from datetime import UTC, datetime

import pytest

from modules.reports.models import (
    AggregationPeriod,
    Benchmark,
    BenchmarkCategory,
    BenchmarkSource,
    BenchmarkStatus,
    BenchmarkType,
    ChartType,
    ComparisonResult,
    DeliveryMethod,
    ExecutiveKPI,
    ExportFormat,
    ExportStatus,
    ExportTrigger,
    KPIAlertLevel,
    KPICategory,
    KPIDirection,
    KPIStatus,
    KPIType,
    ReportCategory,
    ReportExport,
    ReportFormat,
    ReportSchedule,
    ReportTemplate,
    ReportType,
    ScheduleFrequency,
    ScheduleStatus,
    TemplateStatus,
)


class TestReportTemplate:
    """Testes para o model ReportTemplate."""

    def test_create_report_template(self):
        """Testa criação de template de relatório."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT001",
            name="Relatório Financeiro Mensal",
            description="Relatório financeiro consolidado",
            category=ReportCategory.FINANCIAL,
            report_type=ReportType.SUMMARY,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf", "excel", "csv"],
            status=TemplateStatus.ACTIVE,
            ativo=True,
        )
        assert template.code == "RPT001"
        assert template.name == "Relatório Financeiro Mensal"
        assert template.category == ReportCategory.FINANCIAL
        assert template.is_active

    def test_template_activate(self):
        """Testa ativação de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT002",
            name="Template Teste",
            category=ReportCategory.OPERATIONAL,
            report_type=ReportType.DETAILED,
            default_format=ReportFormat.EXCEL,
            supported_formats=["excel"],
            status=TemplateStatus.DRAFT,
            ativo=True,
        )
        template.activate()
        assert template.status == TemplateStatus.ACTIVE

    def test_template_deactivate(self):
        """Testa desativação de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT003",
            name="Template Teste",
            category=ReportCategory.COMMERCIAL,
            report_type=ReportType.SUMMARY,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ACTIVE,
            ativo=True,
        )
        template.deactivate()
        assert template.status == TemplateStatus.INACTIVE

    def test_template_deprecate(self):
        """Testa depreciação de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT004",
            name="Template Antigo",
            category=ReportCategory.COMMERCIAL,
            report_type=ReportType.ANALYTICAL,
            default_format=ReportFormat.CSV,
            supported_formats=["csv"],
            status=TemplateStatus.ACTIVE,
            ativo=True,
        )
        template.deprecate()
        assert template.status == TemplateStatus.DEPRECATED

    def test_template_archive(self):
        """Testa arquivamento de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT005",
            name="Template Arquivado",
            category=ReportCategory.HR,
            report_type=ReportType.DASHBOARD,
            default_format=ReportFormat.HTML,
            supported_formats=["html"],
            status=TemplateStatus.INACTIVE,
            ativo=True,
        )
        template.archive()
        assert template.status == TemplateStatus.ARCHIVED

    def test_template_increment_version(self):
        """Testa incremento de versão."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT006",
            name="Template Versionado",
            category=ReportCategory.OPERATIONAL,
            report_type=ReportType.COMPARATIVE,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ACTIVE,
            version=1,
            ativo=True,
        )
        template.increment_version()
        assert template.version == 2

    def test_template_record_usage(self):
        """Testa registro de uso."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT007",
            name="Template Usado",
            category=ReportCategory.OPERATIONAL,
            report_type=ReportType.CUSTOM,
            default_format=ReportFormat.JSON,
            supported_formats=["json"],
            status=TemplateStatus.ACTIVE,
            usage_count=0,
            ativo=True,
        )
        template.record_usage()
        assert template.usage_count == 1
        assert template.last_used_at is not None

    def test_template_add_section(self):
        """Testa adição de seção."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT008",
            name="Template com Seções",
            category=ReportCategory.EXECUTIVE,
            report_type=ReportType.SUMMARY,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ACTIVE,
            sections=[],
            ativo=True,
        )
        template.add_section({"name": "header", "title": "Cabeçalho", "show_logo": True})
        assert len(template.sections) == 1
        assert template.sections[0]["name"] == "header"

    def test_template_add_chart(self):
        """Testa adição de gráfico."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT009",
            name="Template com Gráficos",
            category=ReportCategory.FINANCIAL,
            report_type=ReportType.ANALYTICAL,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ACTIVE,
            charts=[],
            ativo=True,
        )
        template.add_chart(
            {
                "name": "receitas_chart",
                "chart_type": ChartType.BAR.value,
                "title": "Receitas por Mês",
                "x_axis": "mes",
                "y_axis": "valor",
            }
        )
        assert len(template.charts) == 1
        assert template.charts[0]["chart_type"] == "bar"

    def test_template_add_parameter(self):
        """Testa adição de parâmetro."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            code="RPT010",
            name="Template com Parâmetros",
            category=ReportCategory.OPERATIONAL,
            report_type=ReportType.DETAILED,
            default_format=ReportFormat.EXCEL,
            supported_formats=["excel"],
            status=TemplateStatus.ACTIVE,
            parameters={},
            ativo=True,
        )
        template.add_parameter("data_inicio", "date", {"label": "Data Início", "required": True})
        assert "data_inicio" in template.parameters
        assert template.parameters["data_inicio"]["required"] is True


class TestReportSchedule:
    """Testes para o model ReportSchedule."""

    def test_create_report_schedule(self):
        """Testa criação de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Diário",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.DAILY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ACTIVE,
            start_date=datetime.now(UTC),
            report_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            ativo=True,
        )
        assert schedule.name == "Agendamento Diário"
        assert schedule.frequency == ScheduleFrequency.DAILY
        assert schedule.is_active

    def test_schedule_activate(self):
        """Testa ativação de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Teste",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.WEEKLY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.PAUSED,
            start_date=datetime.now(UTC),
            report_format="excel",
            delivery_method=DeliveryMethod.DOWNLOAD,
            ativo=True,
        )
        schedule.activate()
        assert schedule.status == ScheduleStatus.ACTIVE

    def test_schedule_pause(self):
        """Testa pausa de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Pausado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.MONTHLY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ACTIVE,
            start_date=datetime.now(UTC),
            report_format="csv",
            delivery_method=DeliveryMethod.WEBHOOK,
            ativo=True,
        )
        schedule.pause()
        assert schedule.status == ScheduleStatus.PAUSED

    def test_schedule_resume(self):
        """Testa retomada de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Retomado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.QUARTERLY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.PAUSED,
            start_date=datetime.now(UTC),
            report_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            ativo=True,
        )
        schedule.resume()
        assert schedule.status == ScheduleStatus.ACTIVE

    def test_schedule_cancel(self):
        """Testa cancelamento de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Cancelado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.YEARLY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ACTIVE,
            start_date=datetime.now(UTC),
            report_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            ativo=True,
        )
        schedule.cancel()
        assert schedule.status == ScheduleStatus.CANCELLED

    def test_schedule_record_execution(self):
        """Testa registro de execução."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Executado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.DAILY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ACTIVE,
            start_date=datetime.now(UTC),
            report_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            execution_count=0,
            success_count=0,
            failure_count=0,
            ativo=True,
        )
        schedule.record_execution(success=True)
        assert schedule.execution_count == 1
        assert schedule.success_count == 1

    def test_schedule_add_recipient(self):
        """Testa adição de destinatário."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento com Destinatários",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.WEEKLY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ACTIVE,
            start_date=datetime.now(UTC),
            report_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            recipients=[],
            ativo=True,
        )
        schedule.add_recipient("user@example.com")
        assert "user@example.com" in schedule.recipients

    def test_schedule_success_rate(self):
        """Testa cálculo de taxa de sucesso."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            name="Agendamento Métricas",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.DAILY,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ACTIVE,
            start_date=datetime.now(UTC),
            report_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            execution_count=10,
            success_count=8,
            failure_count=2,
            ativo=True,
        )
        assert schedule.success_rate == 80.0


class TestReportExport:
    """Testes para o model ReportExport."""

    def test_create_report_export(self):
        """Testa criação de exportação."""
        export = ReportExport.create_export(
            template_id=uuid.uuid4(),
            export_format=ExportFormat.PDF,
            trigger=ExportTrigger.MANUAL,
            requested_by=uuid.uuid4(),
        )
        assert export.trigger == ExportTrigger.MANUAL
        assert export.format == ExportFormat.PDF

    def test_export_start_processing(self):
        """Testa início de processamento."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_number="EXP001",
            template_id=uuid.uuid4(),
            status=ExportStatus.PENDING,
            trigger=ExportTrigger.MANUAL,
            format=ExportFormat.EXCEL,
            ativo=True,
        )
        export.start_processing()
        assert export.status == ExportStatus.PROCESSING
        assert export.started_at is not None

    def test_export_complete(self):
        """Testa conclusão de exportação."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_number="EXP002",
            template_id=uuid.uuid4(),
            status=ExportStatus.PROCESSING,
            trigger=ExportTrigger.SCHEDULED,
            format=ExportFormat.CSV,
            started_at=datetime.utcnow(),
            ativo=True,
        )
        export.complete(
            file_path="/exports/report.csv",
            file_size=1024,
            records=100,
        )
        assert export.status == ExportStatus.COMPLETED
        assert export.file_path == "/exports/report.csv"
        assert export.file_size == 1024
        assert export.is_completed

    def test_export_fail(self):
        """Testa falha de exportação."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_number="EXP003",
            template_id=uuid.uuid4(),
            status=ExportStatus.PROCESSING,
            trigger=ExportTrigger.API,
            format=ExportFormat.PDF,
            started_at=datetime.utcnow(),
            ativo=True,
        )
        export.fail("Erro de conexão", error_code="CONN_ERROR")
        assert export.status == ExportStatus.FAILED
        assert export.error_message == "Erro de conexão"

    def test_export_cancel(self):
        """Testa cancelamento de exportação."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_number="EXP004",
            template_id=uuid.uuid4(),
            status=ExportStatus.PENDING,
            trigger=ExportTrigger.MANUAL,
            format=ExportFormat.JSON,
            ativo=True,
        )
        export.cancel()
        assert export.status == ExportStatus.CANCELLED

    def test_export_record_download(self):
        """Testa registro de download."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_number="EXP005",
            template_id=uuid.uuid4(),
            status=ExportStatus.COMPLETED,
            trigger=ExportTrigger.MANUAL,
            format=ExportFormat.PDF,
            download_count=0,
            ativo=True,
        )
        result = export.record_download()
        assert result is True
        assert export.download_count == 1
        assert export.last_download_at is not None

    def test_export_file_size_formatted(self):
        """Testa formatação de tamanho de arquivo."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_number="EXP006",
            template_id=uuid.uuid4(),
            status=ExportStatus.COMPLETED,
            trigger=ExportTrigger.SCHEDULED,
            format=ExportFormat.EXCEL,
            file_size=1536000,  # ~1.5 MB
            ativo=True,
        )
        assert "MB" in export.file_size_formatted


class TestExecutiveKPI:
    """Testes para o model ExecutiveKPI."""

    def test_create_executive_kpi(self):
        """Testa criação de KPI executivo."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI001",
            name="Receita Mensal",
            description="Receita total do mês",
            category=KPICategory.FINANCIAL,
            kpi_type=KPIType.CURRENCY,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.ACTIVE,
            unit="currency",
            current_value=100000.00,
            target_value=120000.00,
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MONTHLY,
            ativo=True,
        )
        assert kpi.code == "KPI001"
        assert kpi.category == KPICategory.FINANCIAL
        assert kpi.is_active

    def test_kpi_update_value(self):
        """Testa atualização de valor."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI002",
            name="Margem de Lucro",
            category=KPICategory.FINANCIAL,
            kpi_type=KPIType.PERCENTAGE,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.ACTIVE,
            unit="percentage",
            current_value=15.00,
            target_value=20.00,
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MONTHLY,
            historical_values=[],
            ativo=True,
        )
        kpi.update_value(18.50)
        assert kpi.current_value == 18.50
        assert kpi.previous_value == 15.00

    def test_kpi_set_target(self):
        """Testa definição de meta."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI003",
            name="Satisfação Cliente",
            category=KPICategory.CUSTOMER,
            kpi_type=KPIType.INDEX,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.ACTIVE,
            unit="score",
            current_value=4.2,
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MONTHLY,
            ativo=True,
        )
        kpi.set_target(4.5)
        assert kpi.target_value == 4.5

    def test_kpi_set_thresholds(self):
        """Testa definição de thresholds."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI004",
            name="Taxa de Conversão",
            category=KPICategory.COMMERCIAL,
            kpi_type=KPIType.PERCENTAGE,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.ACTIVE,
            unit="percentage",
            current_value=25.00,
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.WEEKLY,
            ativo=True,
        )
        kpi.set_thresholds(
            critical_low=10.00,
            warning_low=15.00,
            warning_high=35.00,
            critical_high=40.00,
        )
        assert kpi.critical_threshold_low == 10.00
        assert kpi.warning_threshold_high == 35.00

    def test_kpi_activate(self):
        """Testa ativação de KPI."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI005",
            name="KPI Teste",
            category=KPICategory.OPERATIONAL,
            kpi_type=KPIType.PERCENTAGE,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.DRAFT,
            unit="percentage",
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.DAILY,
            ativo=True,
        )
        kpi.activate()
        assert kpi.status == KPIStatus.ACTIVE

    def test_kpi_deactivate(self):
        """Testa desativação de KPI."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI006",
            name="KPI Inativo",
            category=KPICategory.QUALITY,
            kpi_type=KPIType.INDEX,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.ACTIVE,
            unit="percentage",
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MONTHLY,
            ativo=True,
        )
        kpi.deactivate()
        assert kpi.status == KPIStatus.INACTIVE

    def test_kpi_target_achievement(self):
        """Testa cálculo de atingimento de meta."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            code="KPI007",
            name="Meta Teste",
            category=KPICategory.FINANCIAL,
            kpi_type=KPIType.CURRENCY,
            direction=KPIDirection.INCREASE,
            status=KPIStatus.ACTIVE,
            unit="currency",
            current_value=90000.00,
            target_value=100000.00,
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MONTHLY,
            ativo=True,
        )
        assert kpi.target_achievement == pytest.approx(90.0, rel=1e-2)


class TestBenchmark:
    """Testes para o model Benchmark."""

    def test_create_benchmark(self):
        """Testa criação de benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK001",
            name="Margem EBITDA Setor",
            description="Benchmark de margem EBITDA do setor",
            category=BenchmarkCategory.FINANCIAL,
            benchmark_type=BenchmarkType.INDUSTRY,
            source=BenchmarkSource.MARKET_RESEARCH,
            status=BenchmarkStatus.ACTIVE,
            industry="Tecnologia",
            unit="percentage",
            reference_value=25.00,
            ativo=True,
        )
        assert benchmark.code == "BMK001"
        assert benchmark.category == BenchmarkCategory.FINANCIAL
        assert benchmark.is_active

    def test_benchmark_update_reference_value(self):
        """Testa atualização de valor de referência."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK002",
            name="NPS Setor",
            category=BenchmarkCategory.CUSTOMER,
            benchmark_type=BenchmarkType.EXTERNAL,
            source=BenchmarkSource.ASSOCIATION,
            status=BenchmarkStatus.ACTIVE,
            unit="score",
            reference_value=50.00,
            historical_values=[],
            ativo=True,
        )
        benchmark.update_reference_value(55.00)
        assert benchmark.reference_value == 55.00

    def test_benchmark_update_company_value(self):
        """Testa atualização de valor da empresa."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK003",
            name="Ticket Médio",
            category=BenchmarkCategory.COMMERCIAL,
            benchmark_type=BenchmarkType.COMPETITOR,
            source=BenchmarkSource.INTERNAL_DATA,
            status=BenchmarkStatus.ACTIVE,
            unit="currency",
            reference_value=150.00,
            ativo=True,
        )
        benchmark.update_company_value(180.00)
        assert benchmark.current_company_value == 180.00
        assert benchmark.comparison_result == ComparisonResult.ABOVE

    def test_benchmark_set_distribution(self):
        """Testa definição de distribuição estatística."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK004",
            name="Tempo de Entrega",
            category=BenchmarkCategory.OPERATIONAL,
            benchmark_type=BenchmarkType.INDUSTRY,
            source=BenchmarkSource.CONSULTANT,
            status=BenchmarkStatus.ACTIVE,
            unit="days",
            reference_value=5.00,
            ativo=True,
        )
        benchmark.set_distribution(
            minimum=2.00,
            maximum=10.00,
            median=5.00,
            average=5.50,
            percentile_25=3.00,
            percentile_75=7.00,
            percentile_90=8.50,
        )
        assert benchmark.min_value == 2.00
        assert benchmark.percentile_90 == 8.50

    def test_benchmark_activate(self):
        """Testa ativação de benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK005",
            name="Benchmark Teste",
            category=BenchmarkCategory.QUALITY,
            benchmark_type=BenchmarkType.BEST_PRACTICE,
            source=BenchmarkSource.PUBLIC_DATA,
            status=BenchmarkStatus.DRAFT,
            unit="percentage",
            reference_value=0.0,
            ativo=True,
        )
        benchmark.activate()
        assert benchmark.status == BenchmarkStatus.ACTIVE

    def test_benchmark_deactivate(self):
        """Testa desativação de benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK006",
            name="Benchmark Inativo",
            category=BenchmarkCategory.MARKET,
            benchmark_type=BenchmarkType.HISTORICAL,
            source=BenchmarkSource.GOVERNMENT,
            status=BenchmarkStatus.ACTIVE,
            unit="count",
            reference_value=0.0,
            ativo=True,
        )
        benchmark.deactivate()
        assert benchmark.status == BenchmarkStatus.INACTIVE

    def test_benchmark_mark_outdated(self):
        """Testa marcação como desatualizado."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK007",
            name="Benchmark Desatualizado",
            category=BenchmarkCategory.INDUSTRY,
            benchmark_type=BenchmarkType.EXTERNAL,
            source=BenchmarkSource.MARKET_RESEARCH,
            status=BenchmarkStatus.ACTIVE,
            unit="index",
            reference_value=0.0,
            ativo=True,
        )
        benchmark.mark_outdated()
        assert benchmark.status == BenchmarkStatus.OUTDATED

    def test_benchmark_is_above_below(self):
        """Testa comparação com benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK008",
            name="Benchmark Comparação",
            category=BenchmarkCategory.FINANCIAL,
            benchmark_type=BenchmarkType.INDUSTRY,
            source=BenchmarkSource.INTERNAL_DATA,
            status=BenchmarkStatus.ACTIVE,
            unit="percentage",
            reference_value=20.00,
            current_company_value=25.00,
            comparison_result=ComparisonResult.ABOVE,
            ativo=True,
        )
        assert benchmark.is_above_benchmark
        assert not benchmark.is_below_benchmark

    def test_benchmark_gap_percentage(self):
        """Testa cálculo de gap para meta."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            code="BMK009",
            name="Benchmark Gap",
            category=BenchmarkCategory.COMMERCIAL,
            benchmark_type=BenchmarkType.COMPETITOR,
            source=BenchmarkSource.CONSULTANT,
            status=BenchmarkStatus.ACTIVE,
            unit="currency",
            reference_value=100.00,
            current_company_value=80.00,
            target_value=110.00,
            ativo=True,
        )
        assert benchmark.gap_to_target == 30.00


class TestEnums:
    """Testes para os Enums do módulo."""

    def test_report_category_values(self):
        """Testa valores de ReportCategory."""
        assert ReportCategory.FINANCIAL.value == "financial"
        assert ReportCategory.OPERATIONAL.value == "operational"
        assert ReportCategory.COMMERCIAL.value == "commercial"

    def test_report_format_values(self):
        """Testa valores de ReportFormat."""
        assert ReportFormat.PDF.value == "pdf"
        assert ReportFormat.EXCEL.value == "excel"
        assert ReportFormat.CSV.value == "csv"

    def test_schedule_frequency_values(self):
        """Testa valores de ScheduleFrequency."""
        assert ScheduleFrequency.DAILY.value == "daily"
        assert ScheduleFrequency.WEEKLY.value == "weekly"
        assert ScheduleFrequency.MONTHLY.value == "monthly"

    def test_kpi_direction_values(self):
        """Testa valores de KPIDirection."""
        assert KPIDirection.INCREASE.value == "increase"
        assert KPIDirection.DECREASE.value == "decrease"
        assert KPIDirection.MAINTAIN.value == "maintain"

    def test_comparison_result_values(self):
        """Testa valores de ComparisonResult."""
        assert ComparisonResult.ABOVE.value == "above"
        assert ComparisonResult.BELOW.value == "below"
        assert ComparisonResult.AT_PAR.value == "at_par"
