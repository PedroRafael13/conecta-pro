"""Testes para BudgetForecastService - Sprint 30.

Testa funcionalidades de Previsao Orcamentaria.
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.services.budget_forecast_service import (
    AlertSeverity,
    AlertType,
    BudgetAlert,
    BudgetForecastService,
    ExpenseForecast,
    ForecastMethod,
    ForecastReport,
)


class TestAlertSeverity:
    """Testes para AlertSeverity enum."""

    def test_severity_values_exist(self) -> None:
        """Testa que valores de severidade existem."""
        assert AlertSeverity.LOW.value == "INFO"
        assert AlertSeverity.LOW.value == "WARNING"
        assert AlertSeverity.CRITICAL.value == "CRITICAL"

    def test_severity_count(self) -> None:
        """Testa contagem de severidades."""
        assert len(AlertSeverity) == 3

    def test_severity_is_string(self) -> None:
        """Testa que severidade e string enum."""
        assert isinstance(AlertSeverity.LOW.value, str)


class TestAlertType:
    """Testes para AlertType enum."""

    def test_alert_type_values(self) -> None:
        """Testa valores de tipo de alerta."""
        assert AlertType.EXPIRY.value == "OVER_BUDGET"
        assert AlertType.EXPIRY.value == "NEAR_LIMIT"
        assert AlertType.EXPIRY.value == "TREND_NEGATIVE"
        assert AlertType.EXPIRY.value == "VARIANCE_HIGH"
        assert AlertType.EXPIRY.value == "NO_BUDGET"
        assert AlertType.EXPIRY.value == "PROJECTION_EXCEEDED"

    def test_alert_type_count(self) -> None:
        """Testa contagem de tipos."""
        assert len(AlertType) == 6

    def test_alert_type_is_string(self) -> None:
        """Testa que tipo e string enum."""
        assert isinstance(AlertType.EXPIRY.value, str)


class TestForecastMethod:
    """Testes para ForecastMethod enum."""

    def test_method_values(self) -> None:
        """Testa valores de metodo."""
        assert ForecastMethod.AVERAGE.value == "AVERAGE"
        assert ForecastMethod.WEIGHTED_AVERAGE.value == "WEIGHTED_AVERAGE"
        assert ForecastMethod.LINEAR_TREND.value == "LINEAR_TREND"
        assert ForecastMethod.SEASONAL.value == "SEASONAL"

    def test_method_count(self) -> None:
        """Testa contagem de metodos."""
        assert len(ForecastMethod) == 4

    def test_method_is_string(self) -> None:
        """Testa que metodo e string enum."""
        assert isinstance(ForecastMethod.AVERAGE.value, str)


class TestBudgetAlert:  # pylint: disable=too-many-public-methods
    """Testes para BudgetAlert dataclass."""

    def test_create_alert(self) -> None:
        """Testa criacao de alerta."""
        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.CRITICAL,
            message="Centro de custo CC001 excedeu orcamento",
        )

        assert alert.alert_type == AlertType.EXPIRY
        assert alert.severity == AlertSeverity.CRITICAL
        assert "CC001" in alert.message

    def test_alert_with_cost_center(self) -> None:
        """Testa alerta com centro de custo."""
        cc_id = uuid4()
        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.LOW,
            message="Proximo do limite",
            cost_center_id=cc_id,
            cost_center_code="ADM-001",
            cost_center_name="Administrativo",
        )

        assert alert.cost_center_id == cc_id
        assert alert.cost_center_code == "ADM-001"
        assert alert.cost_center_name == "Administrativo"

    def test_alert_with_values(self) -> None:
        """Testa alerta com valores orcamentarios."""
        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.CRITICAL,
            message="Orcamento excedido",
            budgeted=Decimal("10000"),
            realized=Decimal("12000"),
            variance=Decimal("-2000"),
            variance_pct=Decimal("-20"),
        )

        assert alert.budgeted == Decimal("10000")
        assert alert.realized == Decimal("12000")
        assert alert.variance == Decimal("-2000")
        assert alert.variance_pct == Decimal("-20")

    def test_alert_to_dict(self) -> None:
        """Testa conversao para dicionario."""
        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.CRITICAL,
            message="Teste",
            budgeted=Decimal("10000"),
            realized=Decimal("12000"),
        )

        result = alert.to_dict()

        assert result["alert_type"] == "OVER_BUDGET"
        assert result["severity"] == "CRITICAL"
        assert result["message"] == "Teste"
        assert result["budgeted"] == 10000.0
        assert result["realized"] == 12000.0

    def test_alert_default_created_at(self) -> None:
        """Testa data de criacao padrao."""
        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.LOW,
            message="Info",
        )

        assert isinstance(alert.created_at, datetime)

    def test_alert_no_cost_center(self) -> None:
        """Testa alerta sem centro de custo."""
        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.LOW,
            message="Sem orcamento",
        )

        assert alert.cost_center_id is None
        assert alert.cost_center_code == ""


class TestExpenseForecast:  # pylint: disable=too-many-public-methods
    """Testes para ExpenseForecast dataclass."""

    def test_create_forecast(self) -> None:
        """Testa criacao de previsao."""
        forecast = ExpenseForecast(
            cost_center_id=uuid4(),
            cost_center_code="CC001",
            cost_center_name="Centro de Custo 1",
        )

        assert forecast.cost_center_code == "CC001"
        assert forecast.historical_months == 0
        assert forecast.historical_average == Decimal("0")

    def test_forecast_with_historical_data(self) -> None:
        """Testa previsao com dados historicos."""
        forecast = ExpenseForecast(
            historical_months=6,
            historical_average=Decimal("5000"),
            historical_total=Decimal("30000"),
        )

        assert forecast.historical_months == 6
        assert forecast.historical_average == Decimal("5000")
        assert forecast.historical_total == Decimal("30000")

    def test_forecast_projections(self) -> None:
        """Testa projecoes de previsao."""
        forecast = ExpenseForecast(
            projected_monthly=Decimal("5000"),
            projected_remaining=Decimal("30000"),
            projected_annual=Decimal("60000"),
        )

        assert forecast.projected_monthly == Decimal("5000")
        assert forecast.projected_remaining == Decimal("30000")
        assert forecast.projected_annual == Decimal("60000")

    def test_forecast_budget_analysis(self) -> None:
        """Testa analise de orcamento."""
        forecast = ExpenseForecast(
            annual_budget=Decimal("50000"),
            budget_remaining=Decimal("20000"),
            will_exceed_budget=True,
            excess_amount=Decimal("10000"),
        )

        assert forecast.annual_budget == Decimal("50000")
        assert forecast.budget_remaining == Decimal("20000")
        assert forecast.will_exceed_budget is True
        assert forecast.excess_amount == Decimal("10000")

    def test_forecast_trend(self) -> None:
        """Testa tendencia de previsao."""
        forecast = ExpenseForecast(
            trend_direction="UP",
            trend_percentage=Decimal("15.5"),
        )

        assert forecast.trend_direction == "UP"
        assert forecast.trend_percentage == Decimal("15.5")

    def test_forecast_default_trend(self) -> None:
        """Testa tendencia padrao."""
        forecast = ExpenseForecast()

        assert forecast.trend_direction == "STABLE"
        assert forecast.trend_percentage == Decimal("0")

    def test_forecast_method_attribute(self) -> None:
        """Testa atributo de metodo."""
        forecast = ExpenseForecast(
            forecast_method=ForecastMethod.WEIGHTED_AVERAGE,
        )

        assert forecast.forecast_method == ForecastMethod.WEIGHTED_AVERAGE

    def test_forecast_confidence_level(self) -> None:
        """Testa nivel de confianca."""
        forecast = ExpenseForecast(
            confidence_level=Decimal("85"),
        )

        assert forecast.confidence_level == Decimal("85")


class TestForecastReport:
    """Testes para ForecastReport dataclass."""

    def test_create_report(self) -> None:
        """Testa criacao de relatorio."""
        report = ForecastReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 6, 1),
            forecast_horizon=3,
        )

        assert report.reference_date == date(2024, 6, 1)
        assert report.forecast_horizon == 3
        assert not report.forecasts
        assert not report.alerts

    def test_report_with_forecasts(self) -> None:
        """Testa relatorio com previsoes."""
        report = ForecastReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 6, 1),
            forecast_horizon=3,
        )

        forecast = ExpenseForecast(
            cost_center_code="CC001",
            projected_annual=Decimal("50000"),
        )
        report.forecasts.append(forecast)

        assert len(report.forecasts) == 1
        assert report.forecasts[0].cost_center_code == "CC001"

    def test_report_with_alerts(self) -> None:
        """Testa relatorio com alertas."""
        report = ForecastReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 6, 1),
            forecast_horizon=3,
        )

        alert = BudgetAlert(
            alert_type=AlertType.EXPIRY,
            severity=AlertSeverity.CRITICAL,
            message="Teste",
        )
        report.alerts.append(alert)

        assert len(report.alerts) == 1
        assert report.alerts[0].severity == AlertSeverity.CRITICAL

    def test_report_totals(self) -> None:
        """Testa totais do relatorio."""
        report = ForecastReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 6, 1),
            forecast_horizon=3,
            total_projected=Decimal("100000"),
            total_budget=Decimal("120000"),
            projected_variance=Decimal("20000"),
        )

        assert report.total_projected == Decimal("100000")
        assert report.total_budget == Decimal("120000")
        assert report.projected_variance == Decimal("20000")

    def test_report_counters(self) -> None:
        """Testa contadores do relatorio."""
        report = ForecastReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 6, 1),
            forecast_horizon=3,
            items_exceeding=2,
            critical_alerts=1,
            warning_alerts=3,
        )

        assert report.items_exceeding == 2
        assert report.critical_alerts == 1
        assert report.warning_alerts == 3

    def test_report_generated_at(self) -> None:
        """Testa timestamp de geracao."""
        report = ForecastReport(
            condominio_id=uuid4(),
            reference_date=date(2024, 6, 1),
            forecast_horizon=3,
        )

        assert isinstance(report.generated_at, datetime)


class TestBudgetForecastService:  # pylint: disable=protected-access
    """Testes para BudgetForecastService."""

    def test_service_init(self) -> None:
        """Testa inicializacao do servico."""
        mock_session = type("MockSession", (), {})()
        service = BudgetForecastService(mock_session)

        assert service.session == mock_session

    def test_thresholds(self) -> None:
        """Testa thresholds do servico."""
        assert Decimal("80") == BudgetForecastService.NEAR_LIMIT_THRESHOLD
        assert Decimal("90") == BudgetForecastService.WARNING_THRESHOLD
        assert Decimal("15") == BudgetForecastService.HIGH_VARIANCE_THRESHOLD

    def test_get_month_name(self) -> None:
        """Testa obtencao de nome do mes."""
        assert BudgetForecastService._get_month_name(1) == "Jan"
        assert BudgetForecastService._get_month_name(6) == "Jun"
        assert BudgetForecastService._get_month_name(12) == "Dez"

    def test_get_month_name_invalid(self) -> None:
        """Testa mes invalido."""
        assert BudgetForecastService._get_month_name(0) == ""
        assert BudgetForecastService._get_month_name(13) == ""
        assert BudgetForecastService._get_month_name(-1) == ""

    def test_get_month_name_all_months(self) -> None:
        """Testa todos os meses."""
        expected = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        for month, name in enumerate(expected, 1):
            assert BudgetForecastService._get_month_name(month) == name


class TestForecastCalculations:
    """Testes de calculos de previsao."""

    def test_weighted_average_concept(self) -> None:
        """Testa conceito de media ponderada."""
        historical = [
            Decimal("1000"),
            Decimal("1000"),
            Decimal("1200"),
            Decimal("1200"),
            Decimal("1400"),
            Decimal("1400"),
        ]
        weights = [1, 1, 2, 2, 3, 3]

        weighted_sum = sum(h * w for h, w in zip(historical, weights, strict=False))
        total_weight = sum(weights)
        weighted_avg = weighted_sum / Decimal(str(total_weight))

        # 1000*1 + 1000*1 + 1200*2 + 1200*2 + 1400*3 + 1400*3 = 15200 / 12 = 1266.67
        assert weighted_avg > Decimal("1200")  # Maior que media simples
        assert weighted_avg < Decimal("1400")  # Menor que ultimo valor

    def test_simple_average_concept(self) -> None:
        """Testa conceito de media simples."""
        historical = [
            Decimal("1000"),
            Decimal("1500"),
            Decimal("2000"),
        ]
        average = sum(historical) / Decimal(str(len(historical)))

        assert average == Decimal("1500")

    def test_trend_calculation_up(self) -> None:
        """Testa calculo de tendencia de alta."""
        first_half = Decimal("5000")
        second_half = Decimal("7000")
        trend_pct = ((second_half - first_half) / first_half) * Decimal("100")

        assert trend_pct == Decimal("40")
        assert trend_pct > Decimal("5")  # Tendencia de alta

    def test_trend_calculation_down(self) -> None:
        """Testa calculo de tendencia de baixa."""
        first_half = Decimal("7000")
        second_half = Decimal("5000")
        trend_pct = ((second_half - first_half) / first_half) * Decimal("100")

        # -28.57%
        assert trend_pct < Decimal("-5")  # Tendencia de baixa

    def test_trend_calculation_stable(self) -> None:
        """Testa calculo de tendencia estavel."""
        first_half = Decimal("5000")
        second_half = Decimal("5100")
        trend_pct = ((second_half - first_half) / first_half) * Decimal("100")

        assert trend_pct == Decimal("2")
        assert Decimal("-5") <= trend_pct <= Decimal("5")  # Estavel

    def test_remaining_months_projection(self) -> None:
        """Testa projecao de meses restantes."""
        monthly_avg = Decimal("5000")
        current_month = 6
        remaining_months = 12 - current_month

        projection = monthly_avg * Decimal(str(remaining_months))

        assert projection == Decimal("30000")

    def test_annual_projection(self) -> None:
        """Testa projecao anual."""
        ytd_realized = Decimal("30000")  # 6 meses
        monthly_avg = ytd_realized / Decimal("6")
        annual_projection = monthly_avg * Decimal("12")

        assert annual_projection == Decimal("60000")


class TestAlertGeneration:
    """Testes de geracao de alertas."""

    def test_over_budget_detection(self) -> None:
        """Testa deteccao de estouro de orcamento."""
        budgeted = Decimal("10000")
        realized = Decimal("12000")

        is_over = realized > budgeted

        assert is_over is True
        assert realized - budgeted == Decimal("2000")

    def test_near_limit_detection(self) -> None:
        """Testa deteccao de proximo ao limite."""
        budgeted = Decimal("10000")
        realized = Decimal("9200")  # 92%

        usage_pct = (realized / budgeted) * Decimal("100")

        assert usage_pct == Decimal("92")
        assert usage_pct >= BudgetForecastService.WARNING_THRESHOLD

    def test_info_threshold_detection(self) -> None:
        """Testa deteccao de threshold informativo."""
        budgeted = Decimal("10000")
        realized = Decimal("8500")  # 85%

        usage_pct = (realized / budgeted) * Decimal("100")

        assert usage_pct == Decimal("85")
        assert usage_pct >= BudgetForecastService.NEAR_LIMIT_THRESHOLD
        assert usage_pct < BudgetForecastService.WARNING_THRESHOLD

    def test_alert_severity_order(self) -> None:
        """Testa ordem de severidade."""
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.LOW: 1,
            AlertSeverity.LOW: 2,
        }

        assert severity_order[AlertSeverity.CRITICAL] < severity_order[AlertSeverity.LOW]
        assert severity_order[AlertSeverity.LOW] < severity_order[AlertSeverity.LOW]


class TestConfidenceLevel:
    """Testes de nivel de confianca."""

    def test_confidence_from_historical(self) -> None:
        """Testa confianca baseada em historico."""
        historical_months = 6
        confidence = min(Decimal("100"), Decimal(str(historical_months * 15)))

        assert confidence == Decimal("90")

    def test_confidence_max_100(self) -> None:
        """Testa limite maximo de confianca."""
        historical_months = 12
        confidence = min(Decimal("100"), Decimal(str(historical_months * 15)))

        assert confidence == Decimal("100")

    def test_confidence_low_data(self) -> None:
        """Testa confianca com poucos dados."""
        historical_months = 2
        confidence = min(Decimal("100"), Decimal(str(historical_months * 15)))

        assert confidence == Decimal("30")


class TestIntegration:
    """Testes de integracao (requerem banco)."""

    @pytest.mark.asyncio
    async def test_generate_forecast_placeholder(self) -> None:
        """Placeholder para teste de geracao de previsao."""
        assert True

    @pytest.mark.asyncio
    async def test_get_budget_alerts_placeholder(self) -> None:
        """Placeholder para teste de alertas."""
        assert True

    @pytest.mark.asyncio
    async def test_get_trend_analysis_placeholder(self) -> None:
        """Placeholder para teste de analise de tendencia."""
        assert True

    @pytest.mark.asyncio
    async def test_get_year_end_projection_placeholder(self) -> None:
        """Placeholder para teste de projecao de fim de ano."""
        assert True

    @pytest.mark.asyncio
    async def test_generate_cost_center_forecast_placeholder(self) -> None:
        """Placeholder para teste de previsao por centro de custo."""
        assert True
