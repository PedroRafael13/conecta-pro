"""
Testes unitarios para models do BI Dashboard Financeiro.

Sprint 30 - Business Intelligence Dashboard
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.bi_dashboard.models.dashboard_config import (
    DashboardLayout,
    DashboardStatus,
    DashboardType,
    FinancialDashboard,
    RefreshInterval,
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


class TestKPIEnums:
    """Testes para enums do KPI."""

    def test_kpi_category_values(self):
        """Testa valores da categoria de KPI."""
        assert KPICategory.LIQUIDITY.value == "LIQUIDITY"
        assert KPICategory.PROFITABILITY.value == "PROFITABILITY"
        assert KPICategory.CASH_FLOW.value == "CASH_FLOW"
        assert KPICategory.CUSTOM.value == "CUSTOM"

    def test_kpi_frequency_values(self):
        """Testa valores de frequencia do KPI."""
        assert KPIFrequency.REAL_TIME.value == "REAL_TIME"
        assert KPIFrequency.DAILY.value == "DAILY"
        assert KPIFrequency.MONTHLY.value == "MONTHLY"

    def test_kpi_status_values(self):
        """Testa valores de status do KPI."""
        assert KPIStatus.ACTIVE.value == "ACTIVE"
        assert KPIStatus.INACTIVE.value == "INACTIVE"
        assert KPIStatus.DEPRECATED.value == "DEPRECATED"

    def test_kpi_trend_values(self):
        """Testa valores de trend do KPI."""
        assert KPITrend.UP.value == "UP"
        assert KPITrend.DOWN.value == "DOWN"
        assert KPITrend.STABLE.value == "STABLE"

    def test_alert_level_values(self):
        """Testa valores de nivel de alerta."""
        assert AlertLevel.NORMAL.value == "NORMAL"
        assert AlertLevel.WARNING.value == "WARNING"
        assert AlertLevel.CRITICAL.value == "CRITICAL"


class TestFinancialKPI:
    """Testes para model FinancialKPI."""

    @pytest.fixture
    def sample_kpi(self):
        """Fixture para KPI de exemplo."""
        return FinancialKPI(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="KPI-001",
            nome="Indice de Liquidez",
            categoria=KPICategory.LIQUIDITY,
            status=KPIStatus.ACTIVE,
            frequencia=KPIFrequency.DAILY,
            formula="ativo_circulante / passivo_circulante",
            valor_atual=Decimal("1.5"),
            meta_valor=Decimal("1.2"),
            unidade="",
            is_percentage=False,
            casas_decimais=2,
            historico_dias=365,
        )

    def test_kpi_repr(self, sample_kpi):
        """Testa representacao do KPI."""
        assert "KPI-001" in repr(sample_kpi)
        assert "Indice de Liquidez" in repr(sample_kpi)

    def test_is_active_property(self, sample_kpi):
        """Testa propriedade is_active."""
        assert sample_kpi.is_active is True

        sample_kpi.status = KPIStatus.INACTIVE
        assert sample_kpi.is_active is False

    def test_is_on_target_above_meta(self, sample_kpi):
        """Testa is_on_target quando valor esta acima da meta."""
        sample_kpi.valor_atual = Decimal("1.5")
        sample_kpi.meta_valor = Decimal("1.2")
        assert sample_kpi.is_on_target is True

    def test_is_on_target_below_meta(self, sample_kpi):
        """Testa is_on_target quando valor esta abaixo da meta."""
        sample_kpi.valor_atual = Decimal("1.0")
        sample_kpi.meta_valor = Decimal("1.2")
        assert sample_kpi.is_on_target is False

    def test_is_on_target_inverted(self, sample_kpi):
        """Testa is_on_target para KPI invertido."""
        sample_kpi.is_inverted = True
        sample_kpi.valor_atual = Decimal("1.0")
        sample_kpi.meta_valor = Decimal("1.2")
        assert sample_kpi.is_on_target is True

    def test_is_on_target_no_meta(self, sample_kpi):
        """Testa is_on_target sem meta definida."""
        sample_kpi.meta_valor = None
        assert sample_kpi.is_on_target is False

    def test_progress_to_target(self, sample_kpi):
        """Testa calculo de progresso para meta."""
        sample_kpi.valor_atual = Decimal("0.6")
        sample_kpi.meta_valor = Decimal("1.2")
        assert sample_kpi.progress_to_target == Decimal("50")

    def test_progress_to_target_over_100(self, sample_kpi):
        """Testa progresso limitado a 100%."""
        sample_kpi.valor_atual = Decimal("2.0")
        sample_kpi.meta_valor = Decimal("1.0")
        assert sample_kpi.progress_to_target == Decimal("100")

    def test_progress_to_target_no_meta(self, sample_kpi):
        """Testa progresso sem meta definida."""
        sample_kpi.meta_valor = Decimal("0")
        assert sample_kpi.progress_to_target == Decimal("0")

    def test_is_improving_up_trend(self, sample_kpi):
        """Testa is_improving com tendencia de alta."""
        sample_kpi.trend = KPITrend.UP
        sample_kpi.is_inverted = False
        assert sample_kpi.is_improving is True

    def test_is_improving_down_trend_inverted(self, sample_kpi):
        """Testa is_improving com tendencia de baixa para KPI invertido."""
        sample_kpi.trend = KPITrend.DOWN
        sample_kpi.is_inverted = True
        assert sample_kpi.is_improving is True

    def test_is_improving_stable(self, sample_kpi):
        """Testa is_improving com tendencia estavel."""
        sample_kpi.trend = KPITrend.STABLE
        assert sample_kpi.is_improving is False

    def test_update_value_basic(self, sample_kpi):
        """Testa atualizacao basica de valor."""
        sample_kpi.valor_atual = Decimal("1.0")
        sample_kpi.update_value(Decimal("1.5"))

        assert sample_kpi.valor_atual == Decimal("1.5")
        assert sample_kpi.valor_anterior == Decimal("1.0")
        assert sample_kpi.ultimo_calculo_at is not None

    def test_update_value_trend_up(self, sample_kpi):
        """Testa trend de alta apos atualizacao."""
        sample_kpi.valor_atual = Decimal("1.0")
        sample_kpi.update_value(Decimal("1.5"))

        assert sample_kpi.trend == KPITrend.UP
        assert sample_kpi.variacao_percentual == Decimal("50")

    def test_update_value_trend_down(self, sample_kpi):
        """Testa trend de baixa apos atualizacao."""
        sample_kpi.valor_atual = Decimal("1.5")
        sample_kpi.update_value(Decimal("1.0"))

        assert sample_kpi.trend == KPITrend.DOWN

    def test_update_value_trend_stable(self, sample_kpi):
        """Testa trend estavel apos atualizacao."""
        sample_kpi.valor_atual = Decimal("1.0")
        sample_kpi.update_value(Decimal("1.01"))

        assert sample_kpi.trend == KPITrend.STABLE

    def test_update_value_meta_atingida(self, sample_kpi):
        """Testa verificacao de meta apos atualizacao."""
        sample_kpi.meta_valor = Decimal("1.2")
        sample_kpi.update_value(Decimal("1.5"))

        assert sample_kpi.meta_atingida is True
        assert sample_kpi.meta_percentual == Decimal("125")

    def test_update_alert_level_critical(self, sample_kpi):
        """Testa alerta critico."""
        sample_kpi.threshold_critical_min = Decimal("0.5")
        sample_kpi.update_value(Decimal("0.3"))

        assert sample_kpi.alert_level == AlertLevel.CRITICAL
        assert sample_kpi.alert_message is not None

    def test_update_alert_level_warning(self, sample_kpi):
        """Testa alerta de warning."""
        sample_kpi.threshold_warning_min = Decimal("1.0")
        sample_kpi.threshold_critical_min = Decimal("0.5")
        sample_kpi.update_value(Decimal("0.8"))

        assert sample_kpi.alert_level == AlertLevel.WARNING

    def test_update_alert_level_normal(self, sample_kpi):
        """Testa nivel normal de alerta."""
        sample_kpi.threshold_warning_min = Decimal("1.0")
        sample_kpi.threshold_critical_min = Decimal("0.5")
        sample_kpi.update_value(Decimal("1.5"))

        assert sample_kpi.alert_level == AlertLevel.NORMAL
        assert sample_kpi.alert_message is None

    def test_add_to_history(self, sample_kpi):
        """Testa adicao ao historico."""
        sample_kpi.historico_valores = []
        sample_kpi.add_to_history(Decimal("1.5"))

        assert len(sample_kpi.historico_valores) == 1
        assert sample_kpi.historico_valores[0]["value"] == 1.5

    def test_add_to_history_limit(self, sample_kpi):
        """Testa limite do historico."""
        sample_kpi.historico_valores = []
        sample_kpi.historico_dias = 5

        for i in range(10):
            sample_kpi.add_to_history(Decimal(str(i)))

        assert len(sample_kpi.historico_valores) == 5

    def test_format_value_currency(self, sample_kpi):
        """Testa formatacao de valor monetario."""
        sample_kpi.formato = "currency"
        sample_kpi.unidade = "R$"
        sample_kpi.casas_decimais = 2
        sample_kpi.valor_atual = Decimal("1234.56")

        result = sample_kpi.format_value()
        assert "R$" in result
        assert "1,234.56" in result

    def test_format_value_percentage(self, sample_kpi):
        """Testa formatacao de percentual."""
        sample_kpi.is_percentage = True
        sample_kpi.casas_decimais = 1
        sample_kpi.valor_atual = Decimal("75.5")

        result = sample_kpi.format_value()
        assert "75.5%" in result

    def test_format_value_none(self, sample_kpi):
        """Testa formatacao com valor nulo."""
        sample_kpi.valor_atual = None
        assert sample_kpi.format_value() == "-"


class TestDashboardEnums:
    """Testes para enums do Dashboard."""

    def test_dashboard_type_values(self):
        """Testa valores de tipo de dashboard."""
        assert DashboardType.EXECUTIVE.value == "EXECUTIVE"
        assert DashboardType.OPERATIONAL.value == "OPERATIONAL"
        assert DashboardType.CUSTOM.value == "CUSTOM"

    def test_dashboard_status_values(self):
        """Testa valores de status do dashboard."""
        assert DashboardStatus.ACTIVE.value == "ACTIVE"
        assert DashboardStatus.DRAFT.value == "DRAFT"
        assert DashboardStatus.ARCHIVED.value == "ARCHIVED"

    def test_dashboard_layout_values(self):
        """Testa valores de layout."""
        assert DashboardLayout.GRID_2X2.value == "GRID_2X2"
        assert DashboardLayout.GRID_3X3.value == "GRID_3X3"
        assert DashboardLayout.FREEFORM.value == "FREEFORM"

    def test_refresh_interval_values(self):
        """Testa valores de intervalo de refresh."""
        assert RefreshInterval.REAL_TIME.value == "REAL_TIME"
        assert RefreshInterval.MINUTE_5.value == "MINUTE_5"
        assert RefreshInterval.DAILY.value == "DAILY"


class TestFinancialDashboard:
    """Testes para model FinancialDashboard."""

    @pytest.fixture
    def sample_dashboard(self):
        """Fixture para dashboard de exemplo."""
        return FinancialDashboard(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="DASH-001",
            nome="Dashboard Executivo",
            tipo=DashboardType.EXECUTIVE,
            status=DashboardStatus.ACTIVE,
            layout=DashboardLayout.GRID_3X2,
            refresh_interval=RefreshInterval.MINUTE_15,
            view_count=0,
        )

    def test_dashboard_repr(self, sample_dashboard):
        """Testa representacao do dashboard."""
        assert "DASH-001" in repr(sample_dashboard)
        assert "Dashboard Executivo" in repr(sample_dashboard)

    def test_is_active_property(self, sample_dashboard):
        """Testa propriedade is_active."""
        assert sample_dashboard.is_active is True

        sample_dashboard.status = DashboardStatus.DRAFT
        assert sample_dashboard.is_active is False

    def test_is_active_deleted(self, sample_dashboard):
        """Testa is_active quando deletado."""
        sample_dashboard.deleted_at = datetime.now(UTC)
        assert sample_dashboard.is_active is False

    def test_widget_count_empty(self, sample_dashboard):
        """Testa contagem de widgets vazio."""
        sample_dashboard.widgets = []
        assert sample_dashboard.widget_count == 0

    def test_refresh_seconds_mapping(self, sample_dashboard):
        """Testa mapeamento de refresh em segundos."""
        sample_dashboard.refresh_interval = RefreshInterval.REAL_TIME
        assert sample_dashboard.refresh_seconds == 5

        sample_dashboard.refresh_interval = RefreshInterval.MINUTE_5
        assert sample_dashboard.refresh_seconds == 300

        sample_dashboard.refresh_interval = RefreshInterval.HOUR_1
        assert sample_dashboard.refresh_seconds == 3600

        sample_dashboard.refresh_interval = RefreshInterval.DAILY
        assert sample_dashboard.refresh_seconds == 86400

        sample_dashboard.refresh_interval = RefreshInterval.MANUAL
        assert sample_dashboard.refresh_seconds == 0

    def test_increment_view(self, sample_dashboard):
        """Testa incremento de visualizacoes."""
        sample_dashboard.view_count = 5
        sample_dashboard.increment_view()

        assert sample_dashboard.view_count == 6
        assert sample_dashboard.last_viewed_at is not None

    def test_publish(self, sample_dashboard):
        """Testa publicacao do dashboard."""
        sample_dashboard.status = DashboardStatus.DRAFT
        sample_dashboard.publish()

        assert sample_dashboard.status == DashboardStatus.ACTIVE
        assert sample_dashboard.last_modified_at is not None

    def test_archive(self, sample_dashboard):
        """Testa arquivamento do dashboard."""
        sample_dashboard.archive()

        assert sample_dashboard.status == DashboardStatus.ARCHIVED
        assert sample_dashboard.last_modified_at is not None

    def test_duplicate(self, sample_dashboard):
        """Testa duplicacao do dashboard."""
        copy = sample_dashboard.duplicate("Dashboard Copia")

        assert copy.nome == "Dashboard Copia"
        assert copy.codigo == "DASH-001-COPY"
        assert copy.status == DashboardStatus.DRAFT
        assert copy.condominio_id == sample_dashboard.condominio_id
        assert copy.tipo == sample_dashboard.tipo
        assert copy.layout == sample_dashboard.layout


class TestReportEnums:
    """Testes para enums do Relatorio."""

    def test_report_type_values(self):
        """Testa valores de tipo de relatorio."""
        assert ReportType.CASH_FLOW.value == "CASH_FLOW"
        assert ReportType.INCOME_STATEMENT.value == "INCOME_STATEMENT"
        assert ReportType.BALANCE_SHEET.value == "BALANCE_SHEET"

    def test_report_format_values(self):
        """Testa valores de formato."""
        assert ReportFormat.PDF.value == "PDF"
        assert ReportFormat.EXCEL.value == "EXCEL"
        assert ReportFormat.CSV.value == "CSV"

    def test_report_frequency_values(self):
        """Testa valores de frequencia."""
        assert ReportFrequency.DAILY.value == "DAILY"
        assert ReportFrequency.MONTHLY.value == "MONTHLY"
        assert ReportFrequency.ONCE.value == "ONCE"

    def test_report_status_values(self):
        """Testa valores de status."""
        assert ReportStatus.ACTIVE.value == "ACTIVE"
        assert ReportStatus.PAUSED.value == "PAUSED"
        assert ReportStatus.EXPIRED.value == "EXPIRED"

    def test_delivery_method_values(self):
        """Testa valores de metodo de entrega."""
        assert DeliveryMethod.EMAIL.value == "EMAIL"
        assert DeliveryMethod.STORAGE.value == "STORAGE"
        assert DeliveryMethod.WEBHOOK.value == "WEBHOOK"


class TestScheduledReport:
    """Testes para model ScheduledReport."""

    @pytest.fixture
    def sample_report(self):
        """Fixture para relatorio de exemplo."""
        return ScheduledReport(
            id=uuid4(),
            condominio_id=uuid4(),
            codigo="REP-001",
            nome="Relatorio Mensal de Fluxo",
            tipo=ReportType.CASH_FLOW,
            formato=ReportFormat.PDF,
            status=ReportStatus.ACTIVE,
            frequencia=ReportFrequency.MONTHLY,
            hora_execucao=datetime.strptime("08:00", "%H:%M").time(),
            dia_mes=1,
            valido_de=date.today(),
            total_execucoes=0,
            total_erros=0,
        )

    def test_report_repr(self, sample_report):
        """Testa representacao do relatorio."""
        assert "REP-001" in repr(sample_report)
        assert "Relatorio Mensal de Fluxo" in repr(sample_report)

    def test_is_active_property(self, sample_report):
        """Testa propriedade is_active."""
        assert sample_report.is_active is True

        sample_report.status = ReportStatus.PAUSED
        assert sample_report.is_active is False

    def test_is_active_expired(self, sample_report):
        """Testa is_active com validade expirada."""
        sample_report.valido_ate = date.today() - timedelta(days=1)
        assert sample_report.is_active is False

    def test_is_due_no_next_execution(self, sample_report):
        """Testa is_due sem proxima execucao."""
        sample_report.proxima_execucao_at = None
        assert sample_report.is_due is True

    def test_is_due_future(self, sample_report):
        """Testa is_due com execucao futura."""
        sample_report.proxima_execucao_at = datetime.now(UTC) + timedelta(hours=1)
        assert sample_report.is_due is False

    def test_is_due_past(self, sample_report):
        """Testa is_due com execucao passada."""
        sample_report.proxima_execucao_at = datetime.now(UTC) - timedelta(hours=1)
        assert sample_report.is_due is True

    def test_is_due_inactive(self, sample_report):
        """Testa is_due quando inativo."""
        sample_report.status = ReportStatus.PAUSED
        sample_report.proxima_execucao_at = datetime.now(UTC) - timedelta(hours=1)
        assert sample_report.is_due is False

    def test_success_rate_no_executions(self, sample_report):
        """Testa taxa de sucesso sem execucoes."""
        assert sample_report.success_rate == Decimal("100")

    def test_success_rate_with_errors(self, sample_report):
        """Testa taxa de sucesso com erros."""
        sample_report.total_execucoes = 10
        sample_report.total_erros = 2
        assert sample_report.success_rate == Decimal("80")

    def test_calculate_next_execution_once(self, sample_report):
        """Testa calculo de proxima execucao para ONCE."""
        sample_report.frequencia = ReportFrequency.ONCE
        assert sample_report.calculate_next_execution() is None

    def test_calculate_next_execution_daily(self, sample_report):
        """Testa calculo de proxima execucao diaria."""
        sample_report.frequencia = ReportFrequency.DAILY
        sample_report.hora_execucao = datetime.strptime("08:00", "%H:%M").time()

        next_exec = sample_report.calculate_next_execution()
        assert next_exec is not None
        assert next_exec.hour == 8
        assert next_exec.minute == 0

    def test_calculate_next_execution_monthly(self, sample_report):
        """Testa calculo de proxima execucao mensal."""
        sample_report.frequencia = ReportFrequency.MONTHLY
        sample_report.dia_mes = 15

        next_exec = sample_report.calculate_next_execution()
        assert next_exec is not None
        assert next_exec.day == 15

    def test_mark_executed_success(self, sample_report):
        """Testa marcacao de execucao com sucesso."""
        sample_report.mark_executed(success=True)

        assert sample_report.ultima_execucao_status == "success"
        assert sample_report.ultima_execucao_erro is None
        assert sample_report.total_execucoes == 1
        assert sample_report.total_erros == 0

    def test_mark_executed_error(self, sample_report):
        """Testa marcacao de execucao com erro."""
        sample_report.mark_executed(success=False, error="Timeout")

        assert sample_report.ultima_execucao_status == "error"
        assert sample_report.ultima_execucao_erro == "Timeout"
        assert sample_report.total_execucoes == 1
        assert sample_report.total_erros == 1

    def test_mark_executed_expires(self, sample_report):
        """Testa expiracao apos execucao."""
        sample_report.valido_ate = date.today() - timedelta(days=1)
        sample_report.mark_executed(success=True)

        assert sample_report.status == ReportStatus.EXPIRED

    def test_pause(self, sample_report):
        """Testa pausa do agendamento."""
        sample_report.pause()
        assert sample_report.status == ReportStatus.PAUSED

    def test_resume(self, sample_report):
        """Testa retomada do agendamento."""
        sample_report.status = ReportStatus.PAUSED
        sample_report.resume()

        assert sample_report.status == ReportStatus.ACTIVE
        assert sample_report.proxima_execucao_at is not None

    def test_resume_expired(self, sample_report):
        """Testa retomada quando expirado."""
        sample_report.status = ReportStatus.PAUSED
        sample_report.valido_ate = date.today() - timedelta(days=1)
        sample_report.resume()

        assert sample_report.status == ReportStatus.EXPIRED

    def test_cancel(self, sample_report):
        """Testa cancelamento do agendamento."""
        sample_report.cancel()

        assert sample_report.status == ReportStatus.CANCELLED
        assert sample_report.proxima_execucao_at is None
