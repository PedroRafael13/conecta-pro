"""Testes unitarios para models de BI Dashboard - Sprint 30."""

from datetime import datetime, time, timedelta
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
            codigo="DASH-001",
            nome="Dashboard Executivo",
            descricao="Dashboard para diretoria",
            tipo=DashboardType.EXECUTIVE,
            status=DashboardStatus.DRAFT,
            layout=DashboardLayout.GRID_3X2,
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
            codigo="DASH-002",
            nome="Test",
            tipo=DashboardType.CUSTOM,
            status=DashboardStatus.ACTIVE,
        )
        # is_active = ACTIVE status and deleted_at is None
        assert dashboard.is_active is True

        dashboard.status = DashboardStatus.ARCHIVED
        assert dashboard.is_active is False

        dashboard.status = DashboardStatus.ACTIVE
        dashboard.deleted_at = datetime.utcnow()
        assert dashboard.is_active is False

    def test_dashboard_refresh_seconds(self):
        """Testa propriedade refresh_seconds."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="DASH-003",
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
            codigo="DASH-004",
            nome="Test",
            tipo=DashboardType.CUSTOM,
            view_count=0,
        )
        dashboard.increment_view()
        assert dashboard.view_count == 1
        assert dashboard.last_viewed_at is not None

    def test_dashboard_publish(self):
        """Testa publicacao de dashboard."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="DASH-005",
            nome="Test",
            tipo=DashboardType.CUSTOM,
            status=DashboardStatus.DRAFT,
        )
        dashboard.publish()
        assert dashboard.status == DashboardStatus.ACTIVE
        assert dashboard.last_modified_at is not None

    def test_dashboard_archive(self):
        """Testa arquivamento de dashboard."""
        dashboard = FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="DASH-006",
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
            codigo="DASH-007",
            nome="Original Dashboard",
            descricao="Descricao original",
            tipo=DashboardType.EXECUTIVE,
            status=DashboardStatus.ACTIVE,
            extra_metadata={"theme": "dark"},
        )
        duplicated = original.duplicate("Copia Dashboard")
        assert duplicated.id != original.id
        assert duplicated.nome == "Copia Dashboard"
        assert duplicated.status == DashboardStatus.DRAFT


class TestFinancialWidget:
    """Testes para FinancialWidget model."""

    def test_create_widget(self):
        """Testa criacao de widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            condominio_id=uuid4(),
            codigo="WDG-001",
            titulo="Receita Mensal",
            tipo=WidgetType.CHART,
            tamanho=WidgetSize.LARGE,
            chart_type=ChartType.BAR,
            data_source=DataSource.CASH_FLOW,
        )
        assert widget.titulo == "Receita Mensal"
        assert widget.tipo == WidgetType.CHART
        assert widget.chart_type == ChartType.BAR

    def test_widget_move_to(self):
        """Testa movimentacao de widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            condominio_id=uuid4(),
            codigo="WDG-002",
            titulo="Test",
            tipo=WidgetType.KPI_CARD,
            position_x=0,
            position_y=0,
        )
        widget.move_to(5, 10)
        assert widget.position_x == 5
        assert widget.position_y == 10

    def test_widget_resize(self):
        """Testa redimensionamento de widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            condominio_id=uuid4(),
            codigo="WDG-003",
            titulo="Test",
            tipo=WidgetType.KPI_CARD,
            width=4,
            height=3,
        )
        widget.resize(6, 4)
        assert widget.width == 6
        assert widget.height == 4

    def test_widget_set_error(self):
        """Testa definicao de erro no widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            condominio_id=uuid4(),
            codigo="WDG-004",
            titulo="Test",
            tipo=WidgetType.KPI_CARD,
        )
        widget.set_error("Erro de conexao")
        assert widget.last_error == "Erro de conexao"
        assert widget.is_loading is False

    def test_widget_set_loaded(self):
        """Testa confirmacao de carregamento do widget."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            condominio_id=uuid4(),
            codigo="WDG-005",
            titulo="Test",
            tipo=WidgetType.KPI_CARD,
            last_error="Erro anterior",
        )
        widget.set_loaded()
        assert widget.last_error is None
        assert widget.last_updated_at is not None

    def test_widget_get_color_for_value(self):
        """Testa obtencao de cor baseada em thresholds."""
        widget = FinancialWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            condominio_id=uuid4(),
            codigo="WDG-006",
            titulo="Test",
            tipo=WidgetType.GAUGE,
            threshold_warning=Decimal("50.0"),
            threshold_critical=Decimal("30.0"),
            threshold_success=Decimal("80.0"),
        )
        assert widget.get_color_for_value(90) == "#4caf50"  # success (>= 80)
        assert widget.get_color_for_value(60) == "#2196f3"  # normal (entre 50 e 80)
        assert widget.get_color_for_value(40) == "#ff9800"  # warning (<= 50)
        assert widget.get_color_for_value(20) == "#f44336"  # critical (<= 30)


class TestFinancialKPI:
    """Testes para FinancialKPI model."""

    def test_create_kpi(self):
        """Testa criacao de KPI."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="LIQ_001",
            nome="Indice de Liquidez Corrente",
            categoria=KPICategory.LIQUIDITY,
            formula="{ativo_circulante} / {passivo_circulante}",
            unidade="ratio",
        )
        assert kpi.codigo == "LIQ_001"
        assert kpi.categoria == KPICategory.LIQUIDITY
        assert "{ativo_circulante}" in kpi.formula

    def test_kpi_update_value(self):
        """Testa atualizacao de valor do KPI."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_001",
            nome="Test KPI",
            categoria=KPICategory.CUSTOM,
            formula="1",
            valor_atual=Decimal("100"),
        )
        kpi.update_value(Decimal("120"))
        assert kpi.valor_atual == Decimal("120")
        assert kpi.valor_anterior == Decimal("100")
        assert kpi.variacao_percentual == Decimal("20")
        assert kpi.trend == KPITrend.UP

    def test_kpi_update_value_down_trend(self):
        """Testa atualizacao com tendencia de baixa."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_002",
            nome="Test KPI",
            categoria=KPICategory.CUSTOM,
            formula="1",
            valor_atual=Decimal("100"),
        )
        kpi.update_value(Decimal("80"))
        assert kpi.variacao_percentual == Decimal("-20")
        assert kpi.trend == KPITrend.DOWN

    def test_kpi_add_to_history(self):
        """Testa adicao ao historico."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_003",
            nome="Test KPI",
            categoria=KPICategory.CUSTOM,
            formula="1",
            historico_valores=[],
            historico_dias=5,
        )
        for i in range(7):
            kpi.add_to_history(Decimal(str(i * 10)))

        assert len(kpi.historico_valores) == 5
        assert kpi.historico_valores[-1]["value"] == 60.0

    def test_kpi_format_value_percent(self):
        """Testa formatacao de valor percentual."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_004",
            nome="Test KPI",
            categoria=KPICategory.CUSTOM,
            formula="1",
            is_percentage=True,
            casas_decimais=2,
            valor_atual=Decimal("15.23"),
        )
        assert kpi.format_value() == "15.23%"

    def test_kpi_format_value_currency(self):
        """Testa formatacao de valor monetario."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_005",
            nome="Test KPI",
            categoria=KPICategory.CUSTOM,
            formula="1",
            formato="currency",
            unidade="R$",
            casas_decimais=2,
            valor_atual=Decimal("1234.56"),
        )
        assert kpi.format_value() == "R$ 1,234.56"

    def test_kpi_alert_level_update(self):
        """Testa atualizacao de nivel de alerta."""
        kpi = FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="TEST_006",
            nome="Test KPI",
            categoria=KPICategory.CUSTOM,
            formula="1",
            threshold_warning_min=Decimal("50"),
            threshold_critical_min=Decimal("30"),
        )
        kpi.update_value(Decimal("90"))
        assert kpi.alert_level == AlertLevel.NORMAL

        kpi.update_value(Decimal("40"))
        assert kpi.alert_level == AlertLevel.WARNING

        kpi.update_value(Decimal("20"))
        assert kpi.alert_level == AlertLevel.CRITICAL


class TestScheduledReport:
    """Testes para ScheduledReport model."""

    def test_create_report(self):
        """Testa criacao de relatorio agendado."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-001",
            nome="Relatorio Mensal",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.MONTHLY,
            metodo_entrega=DeliveryMethod.EMAIL,
            destinatarios_email=["admin@test.com"],
        )
        assert report.nome == "Relatorio Mensal"
        assert report.tipo == ReportType.KPI_SUMMARY
        assert report.formato == ReportFormat.PDF

    def test_report_calculate_next_execution_daily(self):
        """Testa calculo de proxima execucao diaria."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-002",
            nome="Test",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            hora_execucao=time(8, 0),
        )
        next_exec = report.calculate_next_execution()
        expected = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        assert next_exec.date() == expected.date()

    def test_report_calculate_next_execution_weekly(self):
        """Testa calculo de proxima execucao semanal."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-003",
            nome="Test",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.WEEKLY,
            metodo_entrega=DeliveryMethod.EMAIL,
            hora_execucao=time(8, 0),
            dia_semana=0,
        )
        next_exec = report.calculate_next_execution()
        assert next_exec.weekday() == 0  # Segunda-feira

    def test_report_mark_executed_success(self):
        """Testa marcacao de execucao bem-sucedida."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-004",
            nome="Test",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            hora_execucao=time(8, 0),
            total_execucoes=0,
            total_erros=0,
        )
        report.mark_executed(success=True)
        assert report.total_execucoes == 1
        assert report.total_erros == 0
        assert report.ultima_execucao_erro is None

    def test_report_mark_executed_failure(self):
        """Testa marcacao de execucao com falha."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-005",
            nome="Test",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            hora_execucao=time(8, 0),
            total_execucoes=0,
            total_erros=0,
        )
        report.mark_executed(success=False, error="Erro de conexao")
        assert report.total_execucoes == 1
        assert report.total_erros == 1
        assert report.ultima_execucao_erro == "Erro de conexao"

    def test_report_pause_resume(self):
        """Testa pausa e retomada de relatorio."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-006",
            nome="Test",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            hora_execucao=time(8, 0),
            status=ReportStatus.ACTIVE,
        )
        report.pause()
        assert report.status == ReportStatus.PAUSED

        report.resume()
        assert report.status == ReportStatus.ACTIVE
        assert report.proxima_execucao_at is not None

    def test_report_cancel(self):
        """Testa cancelamento de relatorio."""
        report = ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-007",
            nome="Test",
            tipo=ReportType.KPI_SUMMARY,
            formato=ReportFormat.PDF,
            frequencia=ReportFrequency.DAILY,
            metodo_entrega=DeliveryMethod.EMAIL,
            status=ReportStatus.ACTIVE,
        )
        report.cancel()
        assert report.status == ReportStatus.CANCELLED
        assert report.proxima_execucao_at is None


class TestAnalyticsCache:
    """Testes para AnalyticsCache model."""

    def test_create_cache(self):
        """Testa criacao de cache."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="widget_123_data",
            tipo=CacheType.WIDGET,
            condominio_id=uuid4(),
            ttl_seconds=300,
            data={"test": True},
            expires_at=datetime.utcnow() + timedelta(seconds=300),
        )
        assert cache.cache_key == "widget_123_data"
        assert cache.tipo == CacheType.WIDGET
        assert cache.ttl_seconds == 300

    def test_cache_is_expired(self):
        """Testa verificacao de expiracao."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            expires_at=datetime.utcnow() - timedelta(hours=1),
            is_expired=True,
            status=CacheStatus.EXPIRED,
        )
        assert cache.is_expired is True

        cache.expires_at = datetime.utcnow() + timedelta(hours=1)
        cache.is_expired = False
        cache.status = CacheStatus.VALID
        assert cache.is_valid is True

    def test_cache_is_valid(self):
        """Testa verificacao de validade."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            status=CacheStatus.VALID,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        assert cache.is_valid is True

        cache.status = CacheStatus.EXPIRED
        assert cache.is_valid is False

    def test_cache_hit_rate(self):
        """Testa calculo de taxa de acertos."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            expires_at=datetime.utcnow() + timedelta(hours=1),
            hit_count=80,
            miss_count=20,
        )
        assert cache.hit_rate == Decimal("80.0")

        cache.hit_count = 0
        cache.miss_count = 0
        assert cache.hit_rate == Decimal("0")

    def test_cache_set_data(self):
        """Testa definicao de dados no cache."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.WIDGET,
            condominio_id=uuid4(),
            ttl_seconds=300,
            data={},
            expires_at=datetime.utcnow() + timedelta(seconds=300),
            refresh_count=0,
        )
        data = {"value": 100, "labels": ["A", "B", "C"]}
        cache.set_data(data)

        assert cache.data == data
        assert cache.status == CacheStatus.VALID
        assert cache.expires_at is not None
        assert cache.data_size_bytes is not None

    def test_cache_record_hit(self):
        """Testa registro de acerto."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            expires_at=datetime.utcnow() + timedelta(hours=1),
            hit_count=0,
        )
        cache.record_hit()
        assert cache.hit_count == 1
        assert cache.last_hit_at is not None

    def test_cache_record_miss(self):
        """Testa registro de erro."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            expires_at=datetime.utcnow() + timedelta(hours=1),
            miss_count=0,
        )
        cache.record_miss()
        assert cache.miss_count == 1

    def test_cache_invalidate(self):
        """Testa invalidacao do cache."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            expires_at=datetime.utcnow() + timedelta(hours=1),
            status=CacheStatus.VALID,
        )
        cache.invalidate()
        assert cache.status == CacheStatus.EXPIRED

    def test_cache_extend_ttl(self):
        """Testa extensao de TTL."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="test_key",
            tipo=CacheType.KPI,
            condominio_id=uuid4(),
            data={"test": True},
            status=CacheStatus.VALID,
            expires_at=datetime.utcnow() + timedelta(seconds=60),
        )
        original_expiry = cache.expires_at
        cache.extend_ttl(300)

        assert cache.expires_at > original_expiry
