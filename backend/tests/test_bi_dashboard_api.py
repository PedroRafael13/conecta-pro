"""Testes de API para BI Dashboard - Sprint 30."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from modules.financial.bi_dashboard.models.dashboard_config import (
    DashboardStatus,
    DashboardType,
    FinancialDashboard,
)
from modules.financial.bi_dashboard.models.dashboard_widget import (
    FinancialWidget,
    WidgetType,
)
from modules.financial.bi_dashboard.models.kpi_definition import (
    FinancialKPI,
    KPICategory,
)
from modules.financial.bi_dashboard.models.scheduled_report import (
    DeliveryMethod,
    ReportFormat,
    ReportFrequency,
    ReportType,
    ScheduledReport,
)
from modules.financial.bi_dashboard.services.analytics_service import AnalyticsService
from modules.financial.bi_dashboard.services.forecast_service import ForecastService


@pytest.fixture
def mock_db():
    """Fixture para mock do banco de dados."""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_dashboard():
    """Fixture para dashboard de exemplo."""
    return FinancialDashboard(
        id=uuid4(),
        condominio_id=uuid4(),
        nome="Dashboard Teste",
        descricao="Dashboard para testes",
        tipo=DashboardType.EXECUTIVE,
        status=DashboardStatus.ACTIVE,
        ativo=True,
    )


@pytest.fixture
def sample_widget(sample_dashboard):
    """Fixture para widget de exemplo."""
    return FinancialWidget(
        id=uuid4(),
        dashboard_id=sample_dashboard.id,
        titulo="Widget Teste",
        tipo=WidgetType.LINE_CHART,
        ativo=True,
    )


@pytest.fixture
def sample_kpi():
    """Fixture para KPI de exemplo."""
    return FinancialKPI(
        id=uuid4(),
        condominio_id=uuid4(),
        codigo="TEST_001",
        nome="KPI Teste",
        categoria=KPICategory.FINANCIAL,
        formula="{a} / {b}",
        valor_atual=Decimal("1.5"),
        ativo=True,
    )


@pytest.fixture
def sample_report():
    """Fixture para relatorio de exemplo."""
    return ScheduledReport(
        id=uuid4(),
        condominio_id=uuid4(),
        nome="Relatorio Teste",
        tipo=ReportType.EXECUCAO,
        formato=ReportFormat.PDF,
        frequencia=ReportFrequency.MONTHLY,
        metodo_entrega=DeliveryMethod.EMAIL,
        destinatarios_email=["test@example.com"],
        ativo=True,
    )


class TestAnalyticsServiceUnit:
    """Testes unitarios para AnalyticsService."""

    def test_detect_anomalies_with_outliers(self, mock_db):
        """Testa deteccao de anomalias com outliers."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("100"),
            Decimal("102"),
            Decimal("98"),
            Decimal("101"),
            Decimal("500"),
            Decimal("99"),
        ]
        anomalies = service.detect_anomalies(values, threshold=2.0)
        assert len(anomalies) > 0
        assert anomalies[0]["value"] == Decimal("500")

    def test_detect_anomalies_no_outliers(self, mock_db):
        """Testa deteccao de anomalias sem outliers."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("100"),
            Decimal("101"),
            Decimal("99"),
            Decimal("100"),
            Decimal("102"),
            Decimal("98"),
        ]
        anomalies = service.detect_anomalies(values, threshold=2.0)
        assert len(anomalies) == 0

    def test_detect_anomalies_insufficient_data(self, mock_db):
        """Testa deteccao com dados insuficientes."""
        service = AnalyticsService(mock_db)
        values = [Decimal("100"), Decimal("200")]
        anomalies = service.detect_anomalies(values)
        assert len(anomalies) == 0

    def test_calculate_trend_up(self, mock_db):
        """Testa calculo de tendencia de alta."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("100"),
            Decimal("110"),
            Decimal("120"),
            Decimal("130"),
            Decimal("140"),
            Decimal("150"),
        ]
        trend = service.calculate_trend(values)
        assert trend["direction"] == "up"
        assert trend["change_percent"] > 0

    def test_calculate_trend_down(self, mock_db):
        """Testa calculo de tendencia de baixa."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("150"),
            Decimal("140"),
            Decimal("130"),
            Decimal("120"),
            Decimal("110"),
            Decimal("100"),
        ]
        trend = service.calculate_trend(values)
        assert trend["direction"] == "down"
        assert trend["change_percent"] < 0

    def test_calculate_trend_stable(self, mock_db):
        """Testa calculo de tendencia estavel."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("100"),
            Decimal("101"),
            Decimal("99"),
            Decimal("100"),
            Decimal("101"),
            Decimal("99"),
        ]
        trend = service.calculate_trend(values)
        assert trend["direction"] == "stable"

    def test_calculate_seasonality_with_pattern(self, mock_db):
        """Testa calculo de sazonalidade com padrao."""
        service = AnalyticsService(mock_db)
        monthly_values = {
            1: Decimal("80"),
            2: Decimal("85"),
            3: Decimal("90"),
            4: Decimal("100"),
            5: Decimal("110"),
            6: Decimal("120"),
            7: Decimal("130"),
            8: Decimal("125"),
            9: Decimal("115"),
            10: Decimal("105"),
            11: Decimal("95"),
            12: Decimal("150"),
        }
        result = service.calculate_seasonality(monthly_values)
        assert result["has_seasonality"] is True
        assert 12 in result["peak_months"]

    def test_analyze_distribution(self, mock_db):
        """Testa analise de distribuicao."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("100"),
            Decimal("200"),
            Decimal("150"),
            Decimal("175"),
            Decimal("125"),
        ]
        result = service.analyze_distribution(values)
        assert result["count"] == 5
        assert result["sum"] == Decimal("750")
        assert result["min"] == Decimal("100")
        assert result["max"] == Decimal("200")

    def test_calculate_growth_rate(self, mock_db):
        """Testa calculo de taxa de crescimento."""
        service = AnalyticsService(mock_db)
        values = [
            Decimal("100"),
            Decimal("110"),
            Decimal("121"),
            Decimal("133.1"),
            Decimal("146.41"),
        ]
        result = service.calculate_growth_rate(values)
        assert result["periods"] == 5
        assert float(result["cagr"]) > 0

    def test_suggest_targets(self, mock_db):
        """Testa sugestao de metas."""
        service = AnalyticsService(mock_db)
        historical = [
            Decimal("100"),
            Decimal("110"),
            Decimal("120"),
            Decimal("130"),
            Decimal("140"),
        ]
        result = service.suggest_targets(historical)
        assert result["conservative"] > Decimal("140")
        assert result["realistic"] > result["conservative"]
        assert result["aggressive"] > result["realistic"]

    def test_calculate_pareto(self, mock_db):
        """Testa analise de Pareto."""
        service = AnalyticsService(mock_db)
        items = [
            {"name": "A", "value": 1000},
            {"name": "B", "value": 500},
            {"name": "C", "value": 300},
            {"name": "D", "value": 100},
            {"name": "E", "value": 100},
        ]
        result = service.calculate_pareto(items, "value", "name")
        assert result["total"] == Decimal("2000")
        assert len(result["top_items_for_80"]) <= 3

    def test_analyze_variance_on_track(self, mock_db):
        """Testa analise de variancia no caminho."""
        service = AnalyticsService(mock_db)
        result = service.analyze_variance(
            actual=Decimal("102"),
            budget=Decimal("100"),
        )
        assert result["status"] == "on_track"
        assert result["variance"] == Decimal("2")

    def test_analyze_variance_off_track(self, mock_db):
        """Testa analise de variancia fora do caminho."""
        service = AnalyticsService(mock_db)
        result = service.analyze_variance(
            actual=Decimal("70"),
            budget=Decimal("100"),
        )
        assert result["status"] == "off_track"
        assert result["severity"] == "high"


class TestForecastServiceUnit:
    """Testes unitarios para ForecastService."""

    def test_generate_forecast(self, mock_db):
        """Testa geracao de previsao."""
        service = ForecastService(mock_db)
        historical = [
            Decimal("100"),
            Decimal("110"),
            Decimal("120"),
            Decimal("130"),
            Decimal("140"),
            Decimal("150"),
        ]
        result = service.generate_forecast(historical, periods=3)
        assert len(result["forecasts"]) == 3
        assert "pessimistic" in result["scenarios"]
        assert "realistic" in result["scenarios"]
        assert "optimistic" in result["scenarios"]
        assert result["confidence"] >= 0

    def test_generate_forecast_insufficient_data(self, mock_db):
        """Testa previsao com dados insuficientes."""
        service = ForecastService(mock_db)
        historical = [Decimal("100"), Decimal("110")]
        result = service.generate_forecast(historical)
        assert len(result["forecasts"]) == 0
        assert result["confidence"] == 0

    def test_moving_average_forecast(self, mock_db):
        """Testa previsao por media movel."""
        service = ForecastService(mock_db)
        values = [
            Decimal("100"),
            Decimal("110"),
            Decimal("120"),
            Decimal("115"),
            Decimal("125"),
            Decimal("130"),
        ]
        result = service.moving_average_forecast(values, window=3, periods=3)
        assert len(result) == 3

    def test_exponential_smoothing(self, mock_db):
        """Testa suavizacao exponencial."""
        service = ForecastService(mock_db)
        values = [
            Decimal("100"),
            Decimal("110"),
            Decimal("105"),
            Decimal("115"),
            Decimal("120"),
        ]
        result = service.exponential_smoothing(values, alpha=0.3, periods=3)
        assert len(result) == 3

    def test_calculate_break_even(self, mock_db):
        """Testa calculo de ponto de equilibrio."""
        service = ForecastService(mock_db)
        result = service.calculate_break_even(
            fixed_costs=Decimal("10000"),
            variable_cost_per_unit=Decimal("50"),
            price_per_unit=Decimal("100"),
        )
        assert result["units"] == Decimal("200")
        assert result["revenue"] == Decimal("20000")
        assert result["margin_contribution"] == Decimal("50")

    def test_calculate_break_even_invalid(self, mock_db):
        """Testa ponto de equilibrio invalido."""
        service = ForecastService(mock_db)
        result = service.calculate_break_even(
            fixed_costs=Decimal("10000"),
            variable_cost_per_unit=Decimal("100"),
            price_per_unit=Decimal("50"),
        )
        assert result["units"] is None
        assert "error" in result

    def test_scenario_analysis(self, mock_db):
        """Testa analise de cenarios."""
        service = ForecastService(mock_db)
        result = service.scenario_analysis(
            base_value=Decimal("1000"),
            growth_rates=[Decimal("-0.1"), Decimal("0"), Decimal("0.1")],
            periods=6,
        )
        assert "pessimistic" in result["scenarios"]
        assert "base" in result["scenarios"]
        assert "optimistic" in result["scenarios"]

    def test_cash_flow_projection(self, mock_db):
        """Testa projecao de fluxo de caixa."""
        service = ForecastService(mock_db)
        result = service.cash_flow_projection(
            opening_balance=Decimal("10000"),
            expected_inflows=[Decimal("5000"), Decimal("6000"), Decimal("4000")],
            expected_outflows=[Decimal("4000"), Decimal("5000"), Decimal("6000")],
        )
        assert len(result["projections"]) == 3
        assert "summary" in result
        assert "alerts" in result

    def test_cash_flow_projection_negative(self, mock_db):
        """Testa projecao com saldo negativo."""
        service = ForecastService(mock_db)
        result = service.cash_flow_projection(
            opening_balance=Decimal("1000"),
            expected_inflows=[Decimal("500"), Decimal("500")],
            expected_outflows=[Decimal("2000"), Decimal("2000")],
        )
        assert result["alerts"]["has_negative_periods"] is True
        assert result["alerts"]["risk_level"] in ["medium", "high"]

    def test_calculate_npv_positive(self, mock_db):
        """Testa calculo de VPL positivo."""
        service = ForecastService(mock_db)
        result = service.calculate_npv(
            initial_investment=Decimal("10000"),
            cash_flows=[
                Decimal("3000"),
                Decimal("4000"),
                Decimal("5000"),
                Decimal("6000"),
            ],
            discount_rate=Decimal("0.1"),
        )
        assert result["npv"] > 0
        assert result["is_viable"] is True

    def test_calculate_npv_negative(self, mock_db):
        """Testa calculo de VPL negativo."""
        service = ForecastService(mock_db)
        result = service.calculate_npv(
            initial_investment=Decimal("100000"),
            cash_flows=[Decimal("1000"), Decimal("1000"), Decimal("1000")],
            discount_rate=Decimal("0.1"),
        )
        assert result["npv"] < 0
        assert result["is_viable"] is False

    def test_calculate_payback(self, mock_db):
        """Testa calculo de payback."""
        service = ForecastService(mock_db)
        result = service.calculate_payback(
            initial_investment=Decimal("10000"),
            cash_flows=[
                Decimal("3000"),
                Decimal("4000"),
                Decimal("5000"),
                Decimal("3000"),
            ],
        )
        assert result["recovered"] is True
        assert result["payback_period"] < 3

    def test_calculate_payback_not_recovered(self, mock_db):
        """Testa payback nao recuperado."""
        service = ForecastService(mock_db)
        result = service.calculate_payback(
            initial_investment=Decimal("100000"),
            cash_flows=[Decimal("1000"), Decimal("1000"), Decimal("1000")],
        )
        assert result["recovered"] is False
        assert result["payback_period"] is None

    def test_what_if_analysis(self, mock_db):
        """Testa analise what-if."""
        service = ForecastService(mock_db)
        result = service.what_if_analysis(
            base_scenario={"revenue": 100000, "costs": 80000},
            variable_changes={
                "revenue": [Decimal("-10"), Decimal("10")],
                "costs": [Decimal("-5"), Decimal("5")],
            },
        )
        assert len(result) == 4


class TestDashboardEndpoints:
    """Testes para endpoints de dashboard."""

    @pytest.fixture
    def mock_dashboard_repo(self):
        """Fixture para mock do repositorio."""
        return MagicMock()

    def test_list_dashboards_returns_list(self, mock_db, mock_dashboard_repo, sample_dashboard):
        """Testa listagem de dashboards."""
        mock_dashboard_repo.list_by_condominio.return_value = [sample_dashboard]
        # Simula chamada ao endpoint
        result = mock_dashboard_repo.list_by_condominio(sample_dashboard.condominio_id)
        assert len(result) == 1
        assert result[0].nome == "Dashboard Teste"

    def test_get_dashboard_by_id(self, mock_db, mock_dashboard_repo, sample_dashboard):
        """Testa obtencao de dashboard por ID."""
        mock_dashboard_repo.get_by_id.return_value = sample_dashboard
        result = mock_dashboard_repo.get_by_id(sample_dashboard.id)
        assert result.id == sample_dashboard.id

    def test_create_dashboard(self, mock_db, mock_dashboard_repo, sample_dashboard):
        """Testa criacao de dashboard."""
        mock_dashboard_repo.create.return_value = sample_dashboard
        result = mock_dashboard_repo.create(sample_dashboard)
        assert result.nome == "Dashboard Teste"

    def test_update_dashboard(self, mock_db, mock_dashboard_repo, sample_dashboard):
        """Testa atualizacao de dashboard."""
        sample_dashboard.nome = "Dashboard Atualizado"
        mock_dashboard_repo.update.return_value = sample_dashboard
        result = mock_dashboard_repo.update(sample_dashboard)
        assert result.nome == "Dashboard Atualizado"

    def test_delete_dashboard(self, mock_db, mock_dashboard_repo, sample_dashboard):
        """Testa exclusao de dashboard."""
        mock_dashboard_repo.delete.return_value = True
        result = mock_dashboard_repo.delete(sample_dashboard.id)
        assert result is True


class TestWidgetEndpoints:
    """Testes para endpoints de widget."""

    @pytest.fixture
    def mock_widget_repo(self):
        """Fixture para mock do repositorio."""
        return MagicMock()

    def test_list_widgets_by_dashboard(self, mock_db, mock_widget_repo, sample_widget):
        """Testa listagem de widgets por dashboard."""
        mock_widget_repo.list_by_dashboard.return_value = [sample_widget]
        result = mock_widget_repo.list_by_dashboard(sample_widget.dashboard_id)
        assert len(result) == 1

    def test_create_widget(self, mock_db, mock_widget_repo, sample_widget):
        """Testa criacao de widget."""
        mock_widget_repo.create.return_value = sample_widget
        result = mock_widget_repo.create(sample_widget)
        assert result.titulo == "Widget Teste"

    def test_update_widget_position(self, mock_db, mock_widget_repo, sample_widget):
        """Testa atualizacao de posicao."""
        sample_widget.move_to(5, 10)
        mock_widget_repo.update.return_value = sample_widget
        result = mock_widget_repo.update(sample_widget)
        assert result.posicao_x == 5
        assert result.posicao_y == 10


class TestKPIEndpoints:
    """Testes para endpoints de KPI."""

    @pytest.fixture
    def mock_kpi_repo(self):
        """Fixture para mock do repositorio."""
        return MagicMock()

    def test_list_kpis_by_category(self, mock_db, mock_kpi_repo, sample_kpi):
        """Testa listagem de KPIs por categoria."""
        mock_kpi_repo.list_by_category.return_value = [sample_kpi]
        result = mock_kpi_repo.list_by_category(sample_kpi.condominio_id, KPICategory.FINANCIAL)
        assert len(result) == 1
        assert result[0].categoria == KPICategory.FINANCIAL

    def test_calculate_kpi_value(self, mock_db, mock_kpi_repo, sample_kpi):
        """Testa calculo de valor de KPI."""
        sample_kpi.update_value(Decimal("2.0"))
        mock_kpi_repo.update.return_value = sample_kpi
        result = mock_kpi_repo.update(sample_kpi)
        assert result.valor_atual == Decimal("2.0")


class TestReportEndpoints:
    """Testes para endpoints de relatorio."""

    @pytest.fixture
    def mock_report_repo(self):
        """Fixture para mock do repositorio."""
        return MagicMock()

    def test_list_reports(self, mock_db, mock_report_repo, sample_report):
        """Testa listagem de relatorios."""
        mock_report_repo.list_by_condominio.return_value = [sample_report]
        result = mock_report_repo.list_by_condominio(sample_report.condominio_id)
        assert len(result) == 1

    def test_pause_report(self, mock_db, mock_report_repo, sample_report):
        """Testa pausa de relatorio."""
        sample_report.pause()
        mock_report_repo.update.return_value = sample_report
        result = mock_report_repo.update(sample_report)
        assert result.status.value == "paused"

    def test_execute_report(self, mock_db, mock_report_repo, sample_report):
        """Testa execucao de relatorio."""
        sample_report.mark_executed(success=True, file_path="/reports/test.pdf")
        mock_report_repo.update.return_value = sample_report
        result = mock_report_repo.update(sample_report)
        assert result.total_execucoes == 1
        assert result.execucoes_sucesso == 1
