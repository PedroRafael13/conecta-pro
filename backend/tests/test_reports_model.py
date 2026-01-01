"""
Testes dos Models do Sprint 34 - Relatórios Gerenciais
"""
# pylint: disable=redefined-outer-name,unused-argument
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

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
    ChartType,
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
    ComparisonResult,
)


class TestReportTemplate:
    """Testes para o model ReportTemplate."""

    def test_create_report_template(self):
        """Testa criação de template de relatório."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT001",
            nome="Relatório Financeiro Mensal",
            descricao="Relatório financeiro consolidado",
            category=ReportCategory.FINANCEIRO,
            report_type=ReportType.CONSOLIDADO,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf", "excel", "csv"],
            status=TemplateStatus.ATIVO,
        )
        assert template.codigo == "RPT001"
        assert template.nome == "Relatório Financeiro Mensal"
        assert template.category == ReportCategory.FINANCEIRO
        assert template.is_active

    def test_template_activate(self):
        """Testa ativação de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT002",
            nome="Template Teste",
            category=ReportCategory.OPERACIONAL,
            report_type=ReportType.DETALHADO,
            default_format=ReportFormat.EXCEL,
            supported_formats=["excel"],
            status=TemplateStatus.RASCUNHO,
        )
        template.activate()
        assert template.status == TemplateStatus.ATIVO

    def test_template_deactivate(self):
        """Testa desativação de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT003",
            nome="Template Teste",
            category=ReportCategory.VENDAS,
            report_type=ReportType.RESUMIDO,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ATIVO,
        )
        template.deactivate()
        assert template.status == TemplateStatus.INATIVO

    def test_template_deprecate(self):
        """Testa depreciação de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT004",
            nome="Template Antigo",
            category=ReportCategory.COMERCIAL,
            report_type=ReportType.ANALITICO,
            default_format=ReportFormat.CSV,
            supported_formats=["csv"],
            status=TemplateStatus.ATIVO,
        )
        template.deprecate()
        assert template.status == TemplateStatus.DESCONTINUADO

    def test_template_archive(self):
        """Testa arquivamento de template."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT005",
            nome="Template Arquivado",
            category=ReportCategory.RH,
            report_type=ReportType.DASHBOARD,
            default_format=ReportFormat.HTML,
            supported_formats=["html"],
            status=TemplateStatus.INATIVO,
        )
        template.archive()
        assert template.status == TemplateStatus.ARQUIVADO

    def test_template_increment_version(self):
        """Testa incremento de versão."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT006",
            nome="Template Versionado",
            category=ReportCategory.ESTOQUE,
            report_type=ReportType.COMPARATIVO,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ATIVO,
            version=1,
        )
        template.increment_version()
        assert template.version == 2

    def test_template_record_usage(self):
        """Testa registro de uso."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT007",
            nome="Template Usado",
            category=ReportCategory.PRODUCAO,
            report_type=ReportType.CUSTOMIZADO,
            default_format=ReportFormat.JSON,
            supported_formats=["json"],
            status=TemplateStatus.ATIVO,
            usage_count=0,
        )
        template.record_usage()
        assert template.usage_count == 1
        assert template.last_used_at is not None

    def test_template_add_section(self):
        """Testa adição de seção."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT008",
            nome="Template com Seções",
            category=ReportCategory.EXECUTIVO,
            report_type=ReportType.CONSOLIDADO,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ATIVO,
            sections=[],
        )
        template.add_section("header", "Cabeçalho", {"show_logo": True})
        assert len(template.sections) == 1
        assert template.sections[0]["name"] == "header"

    def test_template_add_chart(self):
        """Testa adição de gráfico."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT009",
            nome="Template com Gráficos",
            category=ReportCategory.FINANCEIRO,
            report_type=ReportType.ANALITICO,
            default_format=ReportFormat.PDF,
            supported_formats=["pdf"],
            status=TemplateStatus.ATIVO,
            charts=[],
        )
        template.add_chart(
            "receitas_chart",
            ChartType.BARRA,
            "Receitas por Mês",
            {"x_axis": "mes", "y_axis": "valor"},
        )
        assert len(template.charts) == 1
        assert template.charts[0]["chart_type"] == "barra"

    def test_template_add_parameter(self):
        """Testa adição de parâmetro."""
        template = ReportTemplate(
            id=uuid.uuid4(),
            codigo="RPT010",
            nome="Template com Parâmetros",
            category=ReportCategory.OPERACIONAL,
            report_type=ReportType.DETALHADO,
            default_format=ReportFormat.EXCEL,
            supported_formats=["excel"],
            status=TemplateStatus.ATIVO,
            parameters=[],
        )
        template.add_parameter("data_inicio", "date", "Data Início", required=True)
        assert len(template.parameters) == 1
        assert template.parameters[0]["required"] is True


class TestReportSchedule:
    """Testes para o model ReportSchedule."""

    def test_create_report_schedule(self):
        """Testa criação de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH001",
            nome="Agendamento Diário",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.DIARIO,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ATIVO,
            start_date=datetime.now(timezone.utc),
            output_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
        )
        assert schedule.codigo == "SCH001"
        assert schedule.frequency == ScheduleFrequency.DIARIO
        assert schedule.is_active

    def test_schedule_activate(self):
        """Testa ativação de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH002",
            nome="Agendamento Teste",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.SEMANAL,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.RASCUNHO,
            start_date=datetime.now(timezone.utc),
            output_format="excel",
            delivery_method=DeliveryMethod.STORAGE,
        )
        schedule.activate()
        assert schedule.status == ScheduleStatus.ATIVO

    def test_schedule_pause(self):
        """Testa pausa de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH003",
            nome="Agendamento Pausado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.MENSAL,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ATIVO,
            start_date=datetime.now(timezone.utc),
            output_format="csv",
            delivery_method=DeliveryMethod.WEBHOOK,
        )
        schedule.pause()
        assert schedule.status == ScheduleStatus.PAUSADO

    def test_schedule_resume(self):
        """Testa retomada de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH004",
            nome="Agendamento Retomado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.TRIMESTRAL,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.PAUSADO,
            start_date=datetime.now(timezone.utc),
            output_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
        )
        schedule.resume()
        assert schedule.status == ScheduleStatus.ATIVO

    def test_schedule_cancel(self):
        """Testa cancelamento de agendamento."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH005",
            nome="Agendamento Cancelado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.ANUAL,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ATIVO,
            start_date=datetime.now(timezone.utc),
            output_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
        )
        schedule.cancel()
        assert schedule.status == ScheduleStatus.CANCELADO

    def test_schedule_record_execution(self):
        """Testa registro de execução."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH006",
            nome="Agendamento Executado",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.DIARIO,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ATIVO,
            start_date=datetime.now(timezone.utc),
            output_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            execution_count=0,
            success_count=0,
        )
        schedule.record_execution(success=True)
        assert schedule.execution_count == 1
        assert schedule.success_count == 1

    def test_schedule_add_recipient(self):
        """Testa adição de destinatário."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH007",
            nome="Agendamento com Destinatários",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.SEMANAL,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ATIVO,
            start_date=datetime.now(timezone.utc),
            output_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            recipients=[],
        )
        schedule.add_recipient("user@example.com")
        assert "user@example.com" in schedule.recipients

    def test_schedule_success_rate(self):
        """Testa cálculo de taxa de sucesso."""
        schedule = ReportSchedule(
            id=uuid.uuid4(),
            codigo="SCH008",
            nome="Agendamento Métricas",
            template_id=uuid.uuid4(),
            frequency=ScheduleFrequency.DIARIO,
            timezone="America/Sao_Paulo",
            status=ScheduleStatus.ATIVO,
            start_date=datetime.now(timezone.utc),
            output_format="pdf",
            delivery_method=DeliveryMethod.EMAIL,
            execution_count=10,
            success_count=8,
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
        assert export.status == ExportStatus.PENDENTE
        assert export.trigger == ExportTrigger.MANUAL
        assert export.format == ExportFormat.PDF

    def test_export_start_processing(self):
        """Testa início de processamento."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_id="EXP001",
            template_id=uuid.uuid4(),
            status=ExportStatus.PENDENTE,
            trigger=ExportTrigger.MANUAL,
            format=ExportFormat.EXCEL,
        )
        export.start_processing()
        assert export.status == ExportStatus.PROCESSANDO
        assert export.started_at is not None

    def test_export_complete(self):
        """Testa conclusão de exportação."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_id="EXP002",
            template_id=uuid.uuid4(),
            status=ExportStatus.PROCESSANDO,
            trigger=ExportTrigger.AGENDADO,
            format=ExportFormat.CSV,
            started_at=datetime.now(timezone.utc),
        )
        export.complete(
            file_path="/exports/report.csv",
            file_size=1024,
            row_count=100,
        )
        assert export.status == ExportStatus.CONCLUIDO
        assert export.file_path == "/exports/report.csv"
        assert export.file_size == 1024
        assert export.is_completed

    def test_export_fail(self):
        """Testa falha de exportação."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_id="EXP003",
            template_id=uuid.uuid4(),
            status=ExportStatus.PROCESSANDO,
            trigger=ExportTrigger.API,
            format=ExportFormat.PDF,
            started_at=datetime.now(timezone.utc),
        )
        export.fail("Erro de conexão", {"code": "CONN_ERROR"})
        assert export.status == ExportStatus.ERRO
        assert export.error_message == "Erro de conexão"

    def test_export_cancel(self):
        """Testa cancelamento de exportação."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_id="EXP004",
            template_id=uuid.uuid4(),
            status=ExportStatus.PENDENTE,
            trigger=ExportTrigger.MANUAL,
            format=ExportFormat.JSON,
        )
        export.cancel()
        assert export.status == ExportStatus.CANCELADO

    def test_export_record_download(self):
        """Testa registro de download."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_id="EXP005",
            template_id=uuid.uuid4(),
            status=ExportStatus.CONCLUIDO,
            trigger=ExportTrigger.MANUAL,
            format=ExportFormat.PDF,
            download_count=0,
        )
        export.record_download()
        assert export.download_count == 1
        assert export.last_downloaded_at is not None

    def test_export_file_size_formatted(self):
        """Testa formatação de tamanho de arquivo."""
        export = ReportExport(
            id=uuid.uuid4(),
            export_id="EXP006",
            template_id=uuid.uuid4(),
            status=ExportStatus.CONCLUIDO,
            trigger=ExportTrigger.AGENDADO,
            format=ExportFormat.EXCEL,
            file_size=1536000,  # ~1.5 MB
        )
        assert "MB" in export.file_size_formatted


class TestExecutiveKPI:
    """Testes para o model ExecutiveKPI."""

    def test_create_executive_kpi(self):
        """Testa criação de KPI executivo."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI001",
            nome="Receita Mensal",
            descricao="Receita total do mês",
            category=KPICategory.FINANCEIRO,
            kpi_type=KPIType.RECEITA,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.ATIVO,
            unit="currency",
            current_value=Decimal("100000.00"),
            target_value=Decimal("120000.00"),
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MENSAL,
            visibility="public",
        )
        assert kpi.codigo == "KPI001"
        assert kpi.category == KPICategory.FINANCEIRO
        assert kpi.is_active

    def test_kpi_update_value(self):
        """Testa atualização de valor."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI002",
            nome="Margem de Lucro",
            category=KPICategory.FINANCEIRO,
            kpi_type=KPIType.MARGEM,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.ATIVO,
            unit="percentage",
            current_value=Decimal("15.00"),
            target_value=Decimal("20.00"),
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MENSAL,
            visibility="public",
            history=[],
        )
        kpi.update_value(Decimal("18.50"))
        assert kpi.current_value == Decimal("18.50")
        assert kpi.previous_value == Decimal("15.00")

    def test_kpi_set_target(self):
        """Testa definição de meta."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI003",
            nome="Satisfação Cliente",
            category=KPICategory.CLIENTE,
            kpi_type=KPIType.SATISFACAO,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.ATIVO,
            unit="score",
            current_value=Decimal("4.2"),
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MENSAL,
            visibility="public",
        )
        kpi.set_target(Decimal("4.5"))
        assert kpi.target_value == Decimal("4.5")

    def test_kpi_set_thresholds(self):
        """Testa definição de thresholds."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI004",
            nome="Taxa de Conversão",
            category=KPICategory.VENDAS,
            kpi_type=KPIType.CONVERSAO,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.ATIVO,
            unit="percentage",
            current_value=Decimal("25.00"),
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.SEMANAL,
            visibility="public",
        )
        kpi.set_thresholds(
            critical=Decimal("10.00"),
            warning=Decimal("15.00"),
            target=Decimal("25.00"),
            excellent=Decimal("35.00"),
        )
        assert kpi.threshold_critical == Decimal("10.00")
        assert kpi.threshold_excellent == Decimal("35.00")

    def test_kpi_activate(self):
        """Testa ativação de KPI."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI005",
            nome="KPI Teste",
            category=KPICategory.OPERACIONAL,
            kpi_type=KPIType.EFICIENCIA,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.RASCUNHO,
            unit="percentage",
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.DIARIO,
            visibility="private",
        )
        kpi.activate()
        assert kpi.status == KPIStatus.ATIVO

    def test_kpi_deactivate(self):
        """Testa desativação de KPI."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI006",
            nome="KPI Inativo",
            category=KPICategory.QUALIDADE,
            kpi_type=KPIType.QUALIDADE,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.ATIVO,
            unit="percentage",
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MENSAL,
            visibility="public",
        )
        kpi.deactivate()
        assert kpi.status == KPIStatus.INATIVO

    def test_kpi_target_achievement(self):
        """Testa cálculo de atingimento de meta."""
        kpi = ExecutiveKPI(
            id=uuid.uuid4(),
            codigo="KPI007",
            nome="Meta Teste",
            category=KPICategory.FINANCEIRO,
            kpi_type=KPIType.RECEITA,
            direction=KPIDirection.MAIOR_MELHOR,
            status=KPIStatus.ATIVO,
            unit="currency",
            current_value=Decimal("90000.00"),
            target_value=Decimal("100000.00"),
            alert_level=KPIAlertLevel.NORMAL,
            aggregation_period=AggregationPeriod.MENSAL,
            visibility="public",
        )
        assert kpi.target_achievement == Decimal("90.00")


class TestBenchmark:
    """Testes para o model Benchmark."""

    def test_create_benchmark(self):
        """Testa criação de benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK001",
            nome="Margem EBITDA Setor",
            descricao="Benchmark de margem EBITDA do setor",
            category=BenchmarkCategory.FINANCEIRO,
            benchmark_type=BenchmarkType.INDUSTRIA,
            source=BenchmarkSource.PESQUISA_MERCADO,
            status=BenchmarkStatus.ATIVO,
            industry="Tecnologia",
            unit="percentage",
            reference_value=Decimal("25.00"),
            visibility="public",
        )
        assert benchmark.codigo == "BMK001"
        assert benchmark.category == BenchmarkCategory.FINANCEIRO
        assert benchmark.is_active

    def test_benchmark_update_reference_value(self):
        """Testa atualização de valor de referência."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK002",
            nome="NPS Setor",
            category=BenchmarkCategory.SATISFACAO,
            benchmark_type=BenchmarkType.SETOR,
            source=BenchmarkSource.ASSOCIACAO,
            status=BenchmarkStatus.ATIVO,
            unit="score",
            reference_value=Decimal("50.00"),
            visibility="public",
            history=[],
        )
        benchmark.update_reference_value(Decimal("55.00"), "Q4 2024")
        assert benchmark.reference_value == Decimal("55.00")

    def test_benchmark_update_company_value(self):
        """Testa atualização de valor da empresa."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK003",
            nome="Ticket Médio",
            category=BenchmarkCategory.COMERCIAL,
            benchmark_type=BenchmarkType.CONCORRENTE,
            source=BenchmarkSource.DADOS_INTERNOS,
            status=BenchmarkStatus.ATIVO,
            unit="currency",
            reference_value=Decimal("150.00"),
            visibility="public",
        )
        benchmark.update_company_value(Decimal("180.00"))
        assert benchmark.company_value == Decimal("180.00")
        assert benchmark.comparison_result == ComparisonResult.ACIMA

    def test_benchmark_set_distribution(self):
        """Testa definição de distribuição estatística."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK004",
            nome="Tempo de Entrega",
            category=BenchmarkCategory.OPERACIONAL,
            benchmark_type=BenchmarkType.INDUSTRIA,
            source=BenchmarkSource.CONSULTORIA,
            status=BenchmarkStatus.ATIVO,
            unit="days",
            reference_value=Decimal("5.00"),
            visibility="public",
        )
        benchmark.set_distribution(
            min_val=Decimal("2.00"),
            max_val=Decimal("10.00"),
            median=Decimal("5.00"),
            mean=Decimal("5.50"),
            std_dev=Decimal("1.50"),
            p25=Decimal("3.00"),
            p75=Decimal("7.00"),
            p90=Decimal("8.50"),
            sample_size=100,
        )
        assert benchmark.min_value == Decimal("2.00")
        assert benchmark.percentile_90 == Decimal("8.50")
        assert benchmark.sample_size == 100

    def test_benchmark_activate(self):
        """Testa ativação de benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK005",
            nome="Benchmark Teste",
            category=BenchmarkCategory.QUALIDADE,
            benchmark_type=BenchmarkType.BEST_PRACTICE,
            source=BenchmarkSource.ACADEMIA,
            status=BenchmarkStatus.RASCUNHO,
            unit="percentage",
            visibility="private",
        )
        benchmark.activate()
        assert benchmark.status == BenchmarkStatus.ATIVO

    def test_benchmark_deactivate(self):
        """Testa desativação de benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK006",
            nome="Benchmark Inativo",
            category=BenchmarkCategory.INOVACAO,
            benchmark_type=BenchmarkType.CUSTOMIZADO,
            source=BenchmarkSource.GOVERNO,
            status=BenchmarkStatus.ATIVO,
            unit="count",
            visibility="public",
        )
        benchmark.deactivate()
        assert benchmark.status == BenchmarkStatus.INATIVO

    def test_benchmark_mark_outdated(self):
        """Testa marcação como desatualizado."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK007",
            nome="Benchmark Desatualizado",
            category=BenchmarkCategory.SUSTENTABILIDADE,
            benchmark_type=BenchmarkType.REGULATORIO,
            source=BenchmarkSource.PESQUISA_MERCADO,
            status=BenchmarkStatus.ATIVO,
            unit="index",
            visibility="public",
        )
        benchmark.mark_outdated()
        assert benchmark.status == BenchmarkStatus.DESATUALIZADO

    def test_benchmark_is_above_below(self):
        """Testa comparação com benchmark."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK008",
            nome="Benchmark Comparação",
            category=BenchmarkCategory.FINANCEIRO,
            benchmark_type=BenchmarkType.INDUSTRIA,
            source=BenchmarkSource.DADOS_INTERNOS,
            status=BenchmarkStatus.ATIVO,
            unit="percentage",
            reference_value=Decimal("20.00"),
            company_value=Decimal("25.00"),
            comparison_result=ComparisonResult.ACIMA,
            visibility="public",
        )
        assert benchmark.is_above_benchmark
        assert not benchmark.is_below_benchmark

    def test_benchmark_gap_percentage(self):
        """Testa cálculo de gap percentual."""
        benchmark = Benchmark(
            id=uuid.uuid4(),
            codigo="BMK009",
            nome="Benchmark Gap",
            category=BenchmarkCategory.COMERCIAL,
            benchmark_type=BenchmarkType.CONCORRENTE,
            source=BenchmarkSource.CONSULTORIA,
            status=BenchmarkStatus.ATIVO,
            unit="currency",
            reference_value=Decimal("100.00"),
            company_value=Decimal("80.00"),
            target_value=Decimal("110.00"),
            visibility="public",
        )
        assert benchmark.gap_to_target == Decimal("30.00")


class TestEnums:
    """Testes para os Enums do módulo."""

    def test_report_category_values(self):
        """Testa valores de ReportCategory."""
        assert ReportCategory.FINANCEIRO.value == "financeiro"
        assert ReportCategory.OPERACIONAL.value == "operacional"
        assert ReportCategory.VENDAS.value == "vendas"

    def test_report_format_values(self):
        """Testa valores de ReportFormat."""
        assert ReportFormat.PDF.value == "pdf"
        assert ReportFormat.EXCEL.value == "excel"
        assert ReportFormat.CSV.value == "csv"

    def test_schedule_frequency_values(self):
        """Testa valores de ScheduleFrequency."""
        assert ScheduleFrequency.DIARIO.value == "diario"
        assert ScheduleFrequency.SEMANAL.value == "semanal"
        assert ScheduleFrequency.MENSAL.value == "mensal"

    def test_kpi_direction_values(self):
        """Testa valores de KPIDirection."""
        assert KPIDirection.MAIOR_MELHOR.value == "maior_melhor"
        assert KPIDirection.MENOR_MELHOR.value == "menor_melhor"
        assert KPIDirection.ALVO.value == "alvo"

    def test_comparison_result_values(self):
        """Testa valores de ComparisonResult."""
        assert ComparisonResult.ACIMA.value == "acima"
        assert ComparisonResult.ABAIXO.value == "abaixo"
        assert ComparisonResult.NA_MEDIA.value == "na_media"
