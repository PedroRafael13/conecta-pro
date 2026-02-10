"""Testes unitários para models do módulo Analytics Dashboard."""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.hr.analytics_dashboard.models import (
    AggregationType,
    AnalyticsCache,
    CacheStatus,
    CacheType,
    DashboardConfig,
    DashboardType,
    DashboardVisibility,
    DashboardWidget,
    DataSource,
    DeliveryMethod,
    KPICategory,
    KPIDefinition,
    KPIDirection,
    KPIUnit,
    ReportFormat,
    ReportStatus,
    ReportType,
    ScheduledReport,
    ScheduleFrequency,
    WidgetType,
)


class TestDashboardConfig:
    """Testes para DashboardConfig model."""

    def test_create_dashboard_config(self):
        """Testa criação de dashboard config."""
        dashboard = DashboardConfig(
            id=uuid4(),
            name="Dashboard RH",
            slug="dashboard-rh",
            description="Dashboard de métricas de RH",
            dashboard_type=DashboardType.EXECUTIVE,
            visibility=DashboardVisibility.ORGANIZATION,
            condominio_id=uuid4(),
            owner_id=uuid4(),
            is_default=False,
            auto_refresh=False,
        )

        assert dashboard.name == "Dashboard RH"
        assert dashboard.dashboard_type == DashboardType.EXECUTIVE
        assert dashboard.visibility == DashboardVisibility.ORGANIZATION
        assert dashboard.is_default is False
        assert dashboard.auto_refresh is False

    def test_dashboard_type_enum(self):
        """Testa enum DashboardType."""
        assert DashboardType.EXECUTIVE.value == "executive"
        assert DashboardType.OPERATIONAL.value == "operational"
        assert DashboardType.ANALYTICAL.value == "analytical"
        assert DashboardType.COMPLIANCE.value == "compliance"
        assert DashboardType.CUSTOM.value == "custom"

    def test_dashboard_visibility_enum(self):
        """Testa enum DashboardVisibility."""
        assert DashboardVisibility.PRIVATE.value == "private"
        assert DashboardVisibility.TEAM.value == "team"
        assert DashboardVisibility.ORGANIZATION.value == "organization"
        assert DashboardVisibility.PUBLIC.value == "public"

    def test_dashboard_with_layout_config(self):
        """Testa dashboard com configuração de layout."""
        dashboard = DashboardConfig(
            id=uuid4(),
            name="Dashboard Customizado",
            slug="dashboard-customizado",
            dashboard_type=DashboardType.CUSTOM,
            visibility=DashboardVisibility.PRIVATE,
            condominio_id=uuid4(),
            owner_id=uuid4(),
            default_filters={"columns": 12, "rowHeight": 100},
            theme="dark",
            columns=12,
            row_height=100,
        )

        assert dashboard.default_filters == {"columns": 12, "rowHeight": 100}
        assert dashboard.theme == "dark"
        assert dashboard.columns == 12


class TestDashboardWidget:
    """Testes para DashboardWidget model."""

    def test_create_widget(self):
        """Testa criação de widget."""
        widget = DashboardWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            title="Taxa de Absenteísmo",
            widget_type=WidgetType.KPI_CARD,
            data_source=DataSource.ABSENCES,
            grid_x=0,
            grid_y=0,
            grid_width=4,
            grid_height=2,
        )

        assert widget.title == "Taxa de Absenteísmo"
        assert widget.widget_type == WidgetType.KPI_CARD
        assert widget.data_source == DataSource.ABSENCES
        assert widget.grid_width == 4

    def test_widget_type_enum(self):
        """Testa enum WidgetType."""
        assert WidgetType.LINE_CHART.value == "line_chart"
        assert WidgetType.BAR_CHART.value == "bar_chart"
        assert WidgetType.KPI_CARD.value == "kpi_card"
        assert WidgetType.DATA_TABLE.value == "data_table"
        assert WidgetType.HEATMAP.value == "heatmap"

    def test_data_source_enum(self):
        """Testa enum DataSource."""
        assert DataSource.TIME_ENTRIES.value == "time_entries"
        assert DataSource.CHECKINS.value == "checkins"
        assert DataSource.EMPLOYEES.value == "employees"
        assert DataSource.OVERTIME.value == "overtime"
        assert DataSource.ABSENCES.value == "absences"

    def test_aggregation_type_enum(self):
        """Testa enum AggregationType."""
        assert AggregationType.COUNT.value == "count"
        assert AggregationType.SUM.value == "sum"
        assert AggregationType.AVG.value == "avg"
        assert AggregationType.MIN.value == "min"
        assert AggregationType.MAX.value == "max"

    def test_widget_with_chart_config(self):
        """Testa widget com configuração de gráfico."""
        widget = DashboardWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            title="Horas Trabalhadas",
            widget_type=WidgetType.LINE_CHART,
            chart_config={
                "showLegend": True,
                "showGrid": True,
                "animation": True,
            },
            colors=["#3B82F6", "#10B981", "#F59E0B"],
        )

        assert widget.chart_config["showLegend"] is True
        assert len(widget.colors) == 3

    def test_widget_with_kpi_config(self):
        """Testa widget com configuração de KPI."""
        widget = DashboardWidget(
            id=uuid4(),
            dashboard_id=uuid4(),
            title="Pontualidade",
            widget_type=WidgetType.KPI_CARD,
            kpi_metric="PUNCTUALITY_RATE",
            kpi_format="percentage",
            show_comparison=True,
            comparison_period="previous_month",
        )

        assert widget.kpi_metric == "PUNCTUALITY_RATE"
        assert widget.show_comparison is True


class TestKPIDefinition:
    """Testes para KPIDefinition model."""

    def test_create_kpi_definition(self):
        """Testa criação de definição de KPI."""
        kpi = KPIDefinition(
            id=uuid4(),
            code="ABSENTEEISM_RATE",
            name="Taxa de Absenteísmo",
            description="Percentual de ausências não justificadas",
            category=KPICategory.ATTENDANCE,
            unit=KPIUnit.PERCENTAGE,
            direction=KPIDirection.DOWN,
            target_value=Decimal("3.0"),
        )

        assert kpi.code == "ABSENTEEISM_RATE"
        assert kpi.category == KPICategory.ATTENDANCE
        assert kpi.unit == KPIUnit.PERCENTAGE
        assert kpi.direction == KPIDirection.DOWN
        assert kpi.target_value == Decimal("3.0")

    def test_kpi_category_enum(self):
        """Testa enum KPICategory."""
        assert KPICategory.ATTENDANCE.value == "attendance"
        assert KPICategory.PUNCTUALITY.value == "punctuality"
        assert KPICategory.OVERTIME.value == "overtime"
        assert KPICategory.PRODUCTIVITY.value == "productivity"
        assert KPICategory.COMPLIANCE.value == "compliance"

    def test_kpi_unit_enum(self):
        """Testa enum KPIUnit."""
        assert KPIUnit.PERCENTAGE.value == "percentage"
        assert KPIUnit.HOURS.value == "hours"
        assert KPIUnit.CURRENCY.value == "currency"
        assert KPIUnit.COUNT.value == "count"
        assert KPIUnit.DAYS.value == "days"

    def test_kpi_direction_enum(self):
        """Testa enum KPIDirection."""
        assert KPIDirection.UP.value == "up"
        assert KPIDirection.DOWN.value == "down"
        assert KPIDirection.TARGET.value == "target"
        assert KPIDirection.NEUTRAL.value == "neutral"

    def test_kpi_with_thresholds(self):
        """Testa KPI com thresholds."""
        kpi = KPIDefinition(
            id=uuid4(),
            code="OVERTIME_HOURS",
            name="Horas Extra",
            category=KPICategory.OVERTIME,
            unit=KPIUnit.HOURS,
            direction=KPIDirection.TARGET,
            target_value=Decimal("20.0"),
            threshold_warning=Decimal("30.0"),
            threshold_critical=Decimal("50.0"),
            min_value=Decimal("0.0"),
            max_value=Decimal("100.0"),
        )

        assert kpi.threshold_warning == Decimal("30.0")
        assert kpi.threshold_critical == Decimal("50.0")

    def test_kpi_with_formula(self):
        """Testa KPI com fórmula."""
        kpi = KPIDefinition(
            id=uuid4(),
            code="WORKED_HOURS_EFFICIENCY",
            name="Eficiência de Horas Trabalhadas",
            category=KPICategory.PRODUCTIVITY,
            unit=KPIUnit.PERCENTAGE,
            calculation_formula="(worked_hours / expected_hours) * 100",
            calculation_params={
                "description": "Horas trabalhadas dividido por horas esperadas",
                "data_sources": ["time_entries", "employees"],
            },
        )

        assert "worked_hours" in kpi.calculation_formula
        assert len(kpi.calculation_params["data_sources"]) == 2


class TestAnalyticsCache:
    """Testes para AnalyticsCache model."""

    def test_create_cache_entry(self):
        """Testa criação de entrada de cache."""
        now = datetime.utcnow()
        expires = now + timedelta(hours=1)

        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="kpi:ABSENTEEISM_RATE:condo123:2024-12",
            cache_type=CacheType.KPI,
            data={"value": 2.5, "trend": "down"},
            ttl_seconds=3600,
            expires_at=expires,
            status=CacheStatus.VALID,
            condominio_id=uuid4(),
            params_hash="abc123",
        )

        assert cache.cache_type == CacheType.KPI
        assert cache.status == CacheStatus.VALID
        assert cache.ttl_seconds == 3600

    def test_cache_type_enum(self):
        """Testa enum CacheType."""
        assert CacheType.KPI.value == "kpi"
        assert CacheType.WIDGET.value == "widget"
        assert CacheType.REPORT.value == "report"
        assert CacheType.AGGREGATION.value == "aggregation"
        assert CacheType.QUERY.value == "query"

    def test_cache_status_enum(self):
        """Testa enum CacheStatus."""
        assert CacheStatus.VALID.value == "valid"
        assert CacheStatus.EXPIRED.value == "expired"
        assert CacheStatus.STALE.value == "stale"
        assert CacheStatus.COMPUTING.value == "computing"
        assert CacheStatus.ERROR.value == "error"

    def test_cache_with_compression(self):
        """Testa cache com compressão."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="report:monthly:2024-12",
            cache_type=CacheType.REPORT,
            data={"large": "dataset"},
            is_compressed=True,
            data_size_bytes=1024,
            ttl_seconds=86400,
            expires_at=datetime.utcnow() + timedelta(days=1),
            condominio_id=uuid4(),
            params_hash="def456",
        )

        assert cache.is_compressed is True
        assert cache.data_size_bytes == 1024


class TestScheduledReport:
    """Testes para ScheduledReport model."""

    def test_create_scheduled_report(self):
        """Testa criação de relatório agendado."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório Mensal de Ponto",
            description="Relatório mensal de frequência",
            report_type=ReportType.ATTENDANCE,
            output_format=ReportFormat.PDF,
            frequency=ScheduleFrequency.MONTHLY,
            delivery_method=DeliveryMethod.EMAIL,
            condominio_id=uuid4(),
            owner_id=uuid4(),
        )

        assert report.name == "Relatório Mensal de Ponto"
        assert report.report_type == ReportType.ATTENDANCE
        assert report.output_format == ReportFormat.PDF
        assert report.frequency == ScheduleFrequency.MONTHLY

    def test_report_type_enum(self):
        """Testa enum ReportType."""
        assert ReportType.ATTENDANCE.value == "attendance"
        assert ReportType.OVERTIME.value == "overtime"
        assert ReportType.ABSENCES.value == "absences"
        assert ReportType.EXECUTIVE_SUMMARY.value == "executive_summary"
        assert ReportType.COMPLIANCE.value == "compliance"

    def test_report_format_enum(self):
        """Testa enum ReportFormat."""
        assert ReportFormat.PDF.value == "pdf"
        assert ReportFormat.EXCEL.value == "excel"
        assert ReportFormat.CSV.value == "csv"
        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.HTML.value == "html"

    def test_schedule_frequency_enum(self):
        """Testa enum ScheduleFrequency."""
        assert ScheduleFrequency.DAILY.value == "daily"
        assert ScheduleFrequency.WEEKLY.value == "weekly"
        assert ScheduleFrequency.MONTHLY.value == "monthly"
        assert ScheduleFrequency.QUARTERLY.value == "quarterly"

    def test_delivery_method_enum(self):
        """Testa enum DeliveryMethod."""
        assert DeliveryMethod.EMAIL.value == "email"
        assert DeliveryMethod.DOWNLOAD.value == "download"
        assert DeliveryMethod.SFTP.value == "sftp"
        assert DeliveryMethod.WEBHOOK.value == "webhook"

    def test_report_status_enum(self):
        """Testa enum ReportStatus."""
        assert ReportStatus.ACTIVE.value == "active"
        assert ReportStatus.PAUSED.value == "paused"
        assert ReportStatus.DISABLED.value == "disabled"
        assert ReportStatus.FAILED.value == "failed"

    def test_report_with_recipients(self):
        """Testa relatório com destinatários."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório Semanal",
            report_type=ReportType.OVERTIME,
            output_format=ReportFormat.EXCEL,
            frequency=ScheduleFrequency.WEEKLY,
            delivery_method=DeliveryMethod.EMAIL,
            condominio_id=uuid4(),
            owner_id=uuid4(),
            recipients=[
                {"email": "rh@empresa.com", "name": "RH"},
                {"email": "gestor@empresa.com", "name": "Gestor"},
            ],
            report_config={
                "day_of_week": 1,
                "hour": 8,
                "minute": 0,
            },
        )

        assert len(report.recipients) == 2
        assert report.report_config["day_of_week"] == 1

    def test_report_with_filters(self):
        """Testa relatório com filtros."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório por Departamento",
            report_type=ReportType.ATTENDANCE,
            output_format=ReportFormat.PDF,
            frequency=ScheduleFrequency.MONTHLY,
            delivery_method=DeliveryMethod.EMAIL,
            condominio_id=uuid4(),
            owner_id=uuid4(),
            filters={
                "department_ids": ["dept-001", "dept-002"],
                "include_inactive": False,
            },
            columns=["summary", "details", "charts"],
        )

        assert "department_ids" in report.filters
        assert "summary" in report.columns


class TestDefaultKPIs:
    """Testes para KPIs padrão."""

    def test_default_kpis_list(self):
        """Testa lista de KPIs padrão."""
        from modules.hr.analytics_dashboard.models.kpi_definition import DEFAULT_KPIS

        assert len(DEFAULT_KPIS) >= 7

        codes = [kpi["code"] for kpi in DEFAULT_KPIS]
        assert "ABSENTEEISM_RATE" in codes
        assert "PUNCTUALITY_RATE" in codes
        assert "OVERTIME_HOURS" in codes
        assert "BANK_HOURS_BALANCE" in codes

    def test_default_kpi_structure(self):
        """Testa estrutura de KPI padrão."""
        from modules.hr.analytics_dashboard.models.kpi_definition import DEFAULT_KPIS

        for kpi in DEFAULT_KPIS:
            assert "code" in kpi
            assert "name" in kpi
            assert "category" in kpi
            assert "unit" in kpi
            assert "direction" in kpi
