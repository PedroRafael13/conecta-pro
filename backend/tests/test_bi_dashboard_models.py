"""Testes unitarios para models de BI Dashboard - Sprint 30."""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.bi_dashboard.models.analytics_cache import (
    AnalyticsCache,
    CacheStatus,
    CacheType,
)
from modules.financial.bi_dashboard.models.dashboard_config import (
    DashboardLayout,
    DashboardStatus,
    DashboardType,
    FinancialDashboard,
    RefreshInterval,
)
from modules.financial.bi_dashboard.models.dashboard_widget import (
    ChartType,
    DataSource,
    FinancialWidget,
    WidgetSize,
    WidgetType,
)
from modules.financial.bi_dashboard.models.kpi_definition import (
    AlertLevel,
    FinancialKPI,
    KPICategory,
    KPIFrequency,
    KPIStatus,
    KPITrend,
)
from modules.financial.bi_dashboard.models.scheduled_report import (
    DeliveryMethod,
    ReportFormat,
    ReportFrequency,
    ReportStatus,
    ReportType,
    ScheduledReport,
)


class TestFinancialDashboard:
    """Testes para FinancialDashboard model."""

    def test_create_dashboard(self):
        """Testa criacao de dashboard."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Dashboard Executivo",
            descricao="Dashboard para diretoria",
            tipo=DashboardType.EXECUTIVE,
            status=DashboardStatus.DRAFT,
            layout=DashboardLayout.GRID_2X2,
            refresh_interval=RefreshInterval.MINUTE_5,
        )
        assert dashboard.nome == "Dashboard Executivo"
        assert dashboard.tipo == DashboardType.EXECUTIVE
        assert dashboard.status == DashboardStatus.DRAFT

    def test_dashboard_is_active_property(self):
        """Testa propriedade is_active."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=DashboardType.CUSTOM,
            status=DashboardStatus.ACTIVE,
            ativo=True,
        )
        assert dashboard.is_active is True

        dashboard.status = DashboardStatus.ARCHIVED
        assert dashboard.is_active is False

        dashboard.status = DashboardStatus.ACTIVE
        dashboard.ativo = False
        assert dashboard.is_active is False

    def test_dashboard_refresh_seconds(self):
        """Testa propriedade refresh_seconds."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=DashboardType.CUSTOM,
            refresh_interval=RefreshInterval.MINUTE_1,
        )
        assert dashboard.refresh_seconds == 60

        dashboard.refresh_interval = RefreshInterval.HOUR_1
        assert dashboard.refresh_seconds == 3600

        dashboard.refresh_interval = RefreshInterval.MANUAL
        assert dashboard.refresh_seconds == 0

    def test_dashboard_increment_view(self):
        """Testa incremento de visualizacoes."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=DashboardType.CUSTOM,
            visualizacoes=0,
        )
        dashboard.increment_view()
        assert dashboard.visualizacoes == 1
        assert dashboard.ultima_visualizacao is not None

    def test_dashboard_publish(self):
        """Testa publicacao de dashboard."""
        user_id = uuid4()
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=DashboardType.CUSTOM,
            status=DashboardStatus.DRAFT,
        )
        dashboard.publish(user_id)
        assert dashboard.status == DashboardStatus.ACTIVE
        assert dashboard.published_by == user_id
        assert dashboard.published_at is not None

    def test_dashboard_archive(self):
        """Testa arquivamento de dashboard."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=DashboardType.CUSTOM,
            status=DashboardStatus.ACTIVE,
        )
        dashboard.archive()
        assert dashboard.status == DashboardStatus.ARCHIVED

    def test_dashboard_duplicate(self):
        """Testa duplicacao de dashboard."""
        original = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Original Dashboard",
            descricao="Descricao original",
            tipo=DashboardType.EXECUTIVE,
            status=DashboardStatus.ACTIVE,
            configuracoes={"theme": "dark"},
        )
        duplicated = original.duplicate("Copia Dashboard")
        assert duplicated.id != original.id
        assert duplicated.nome == "Copia Dashboard"
        assert duplicated.status == DashboardStatus.DRAFT
        assert duplicated.configuracoes == original.configuracoes


class TestFinancialWidget:
    """Testes para FinancialWidget model."""

    def test_create_widget(self):
        """Testa criacao de widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            titulo="Receita Mensal",
            tipo=WidgetType.LINE_CHART,
            tamanho=WidgetSize.LARGE,
            tipo_grafico=ChartType.BAR,
            fonte_dados=DataSource.TIME_ENTRIES,
        )
        assert widget.titulo == "Receita Mensal"
        assert widget.tipo == WidgetType.LINE_CHART
        assert widget.tipo_grafico == ChartType.BAR

    def test_widget_move_to(self):
        """Testa movimentacao de widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            titulo="Test",
            tipo=WidgetType.LINE_CHART,
            posicao_x=0,
            posicao_y=0,
        )
        widget.move_to(5, 10)
        assert widget.posicao_x == 5
        assert widget.posicao_y == 10

    def test_widget_resize(self):
        """Testa redimensionamento de widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            titulo="Test",
            tipo=WidgetType.LINE_CHART,
            largura=4,
            altura=3,
        )
        widget.resize(6, 4)
        assert widget.largura == 6
        assert widget.altura == 4

    def test_widget_set_error(self):
        """Testa definicao de erro no widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            titulo="Test",
            tipo=WidgetType.LINE_CHART,
        )
        widget.set_error("Erro de conexao")
        assert widget.ultimo_erro == "Erro de conexao"
        assert widget.ultimo_refresh is not None

    def test_widget_set_loaded(self):
        """Testa confirmacao de carregamento do widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            titulo="Test",
            tipo=WidgetType.LINE_CHART,
            ultimo_erro="Erro anterior",
        )
        widget.set_loaded()
        assert widget.ultimo_erro is None
        assert widget.ultimo_refresh is not None

    def test_widget_get_color_for_value(self):
        """Testa obtencao de cor baseada em thresholds."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            titulo="Test",
            tipo=WidgetType.GAUGE,
            thresholds={
                "warning": 50.0,
                "critical": 30.0,
                "success": 80.0,
            },
        )
        assert widget.get_color_for_value(90) == "success"
        assert widget.get_color_for_value(60) == "normal"
        assert widget.get_color_for_value(40) == "warning"
        assert widget.get_color_for_value(20) == "critical"


class TestFinancialKPI:
    """Testes para FinancialKPI model."""

    def test_create_kpi(self):
        """Testa criacao de KPI."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="LIQ_001",
            nome="Indice de Liquidez Corrente",
            categoria=KPICategory.FINANCIAL,
            formula="{ativo_circulante} / {passivo_circulante}",
            unidade="ratio",
        )
        assert kpi.codigo == "LIQ_001"
        assert kpi.categoria == KPICategory.FINANCIAL
        assert "{ativo_circulante}" in kpi.formula

    def test_kpi_update_value(self):
        """Testa atualizacao de valor do KPI."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_001",
            nome="Test KPI",
            categoria=KPICategory.FINANCIAL,
            formula="1",
            valor_atual=Decimal("100"),
        )
        kpi.update_value(Decimal("120"))
        assert kpi.valor_atual == Decimal("120")
        assert kpi.valor_anterior == Decimal("100")
        assert kpi.variacao_percent == Decimal("20")
        assert kpi.tendencia == KPITrend.UP

    def test_kpi_update_value_down_trend(self):
        """Testa atualizacao com tendencia de baixa."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_002",
            nome="Test KPI",
            categoria=KPICategory.FINANCIAL,
            formula="1",
            valor_atual=Decimal("100"),
        )
        kpi.update_value(Decimal("80"))
        assert kpi.variacao_percent == Decimal("-20")
        assert kpi.tendencia == KPITrend.DOWN

    def test_kpi_add_to_history(self):
        """Testa adicao ao historico."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_003",
            nome="Test KPI",
            categoria=KPICategory.FINANCIAL,
            formula="1",
            historico=[],
            historico_max_registros=5,
        )
        for i in range(7):
            kpi.add_to_history(Decimal(str(i * 10)))

        assert len(kpi.historico) == 5
        assert kpi.historico[-1]["valor"] == "60"

    def test_kpi_format_value_percent(self):
        """Testa formatacao de valor percentual."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_004",
            nome="Test KPI",
            categoria=KPICategory.FINANCIAL,
            formula="1",
            formato="percent",
            casas_decimais=2,
            valor_atual=Decimal("0.1523"),
        )
        assert kpi.format_value() == "15.23%"

    def test_kpi_format_value_currency(self):
        """Testa formatacao de valor monetario."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_005",
            nome="Test KPI",
            categoria=KPICategory.FINANCIAL,
            formula="1",
            formato="currency",
            casas_decimais=2,
            valor_atual=Decimal("1234.56"),
        )
        assert kpi.format_value() == "R$ 1234.56"

    def test_kpi_alert_level_update(self):
        """Testa atualizacao de nivel de alerta."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_006",
            nome="Test KPI",
            categoria=KPICategory.FINANCIAL,
            formula="1",
            threshold_warning=Decimal("50"),
            threshold_critical=Decimal("30"),
            threshold_success=Decimal("80"),
        )
        kpi.update_value(Decimal("90"))
        assert kpi.alert_level == AlertLevel.GREEN

        kpi.update_value(Decimal("40"))
        assert kpi.alert_level == AlertLevel.GREEN

        kpi.update_value(Decimal("20"))
        assert kpi.alert_level == AlertLevel.GREEN


class TestScheduledReport:
    """Testes para ScheduledReport model."""

    def test_create_report(self):
        """Testa criacao de relatorio agendado."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Relatorio Mensal",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.MONTHLY,
            metodo_entrega=DeliveryMethod.EMAIL,
            destinatarios_email=["admin@test.com"],
        )
        assert report.nome == "Relatorio Mensal"
        assert report.tipo == ReportType.EXECUCAO
        assert report.formato == ReportFormat.PDF

    def test_report_calculate_next_execution_daily(self):
        """Testa calculo de proxima execucao diaria."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
        )
        next_exec = report.calculate_next_execution()
        expected = datetime.utcnow().replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)
        assert next_exec.date() == expected.date()

    def test_report_calculate_next_execution_weekly(self):
        """Testa calculo de proxima execucao semanal."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.WEEKLY,
            metodo_entrega=DeliveryMethod.EMAIL,
        )
        next_exec = report.calculate_next_execution()
        assert next_exec.weekday() == 0  # Segunda-feira

    def test_report_mark_executed_success(self):
        """Testa marcacao de execucao bem-sucedida."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            total_execucoes=0,
            execucoes_sucesso=0,
        )
        report.mark_executed(success=True, file_path="/reports/test.pdf")
        assert report.total_execucoes == 1
        assert report.execucoes_sucesso == 1
        assert report.ultimo_arquivo == "/reports/test.pdf"
        assert report.ultimo_erro is None

    def test_report_mark_executed_failure(self):
        """Testa marcacao de execucao com falha."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            total_execucoes=0,
            execucoes_falha=0,
        )
        report.mark_executed(success=False, error="Erro de conexao")
        assert report.total_execucoes == 1
        assert report.execucoes_falha == 1
        assert report.ultimo_erro == "Erro de conexao"

    def test_report_pause_resume(self):
        """Testa pausa e retomada de relatorio."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            status=ReportStatus.ACTIVE,
        )
        report.pause()
        assert report.status == ReportStatus.PAUSED

        report.resume()
        assert report.status == ReportStatus.ACTIVE
        assert report.proxima_execucao is not None

    def test_report_cancel(self):
        """Testa cancelamento de relatorio."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            nome="Test",
            tipo=ReportType.EXECUCAO,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            status=ReportStatus.ACTIVE,
        )
        report.cancel()
        assert report.status == ReportStatus.ACTIVE
        assert report.proxima_execucao is None


class TestAnalyticsCache:
    """Testes para AnalyticsCache model."""

    def test_create_cache(self):
        """Testa criacao de cache."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="widget_123_data",
            cache_type=CacheType.KPI,
            condominio_id=uuid4(),
            ttl_segundos=300,
        )
        assert cache.cache_key == "widget_123_data"
        assert cache.cache_type == CacheType.KPI
        assert cache.ttl_segundos == 300

    def test_cache_is_expired(self):
        """Testa verificacao de expiracao."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            expira_em=datetime.utcnow() - timedelta(hours=1),
        )
        assert cache.is_expired is True

        cache.expira_em = datetime.utcnow() + timedelta(hours=1)
        assert cache.is_expired is False

    def test_cache_is_valid(self):
        """Testa verificacao de validade."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            status=CacheStatus.VALID,
            expira_em=datetime.utcnow() + timedelta(hours=1),
        )
        assert cache.is_valid is True

        cache.status = CacheStatus.VALID
        assert cache.is_valid is False

    def test_cache_hit_rate(self):
        """Testa calculo de taxa de acertos."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            hits=80,
            misses=20,
        )
        assert cache.hit_rate == 80.0

        cache.hits = 0
        cache.misses = 0
        assert cache.hit_rate == 0.0

    def test_cache_set_data(self):
        """Testa definicao de dados no cache."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            ttl_segundos=300,
        )
        data = {"value": 100, "labels": ["A", "B", "C"]}
        cache.set_data(data)

        assert cache.data == data
        assert cache.status == CacheStatus.VALID
        assert cache.expira_em is not None
        assert cache.tamanho_bytes is not None

    def test_cache_record_hit(self):
        """Testa registro de acerto."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            hits=0,
        )
        cache.record_hit()
        assert cache.hits == 1
        assert cache.ultimo_hit is not None

    def test_cache_record_miss(self):
        """Testa registro de erro."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            misses=0,
        )
        cache.record_miss()
        assert cache.misses == 1

    def test_cache_invalidate(self):
        """Testa invalidacao do cache."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            status=CacheStatus.VALID,
        )
        cache.invalidate()
        assert cache.status == CacheStatus.VALID

    def test_cache_extend_ttl(self):
        """Testa extensao de TTL."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            cache_type=CacheType.KPI,
            status=CacheStatus.VALID,
            expira_em=datetime.utcnow() + timedelta(seconds=60),
        )
        original_expiry = cache.expira_em
        cache.extend_ttl(300)

        assert cache.expira_em > original_expiry
