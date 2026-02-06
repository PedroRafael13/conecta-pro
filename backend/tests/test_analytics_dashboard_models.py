"""Testes unitários para models do módulo Analytics Dashboard."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from modules.hr.analytics_dashboard.models import (
    DashboardConfig,
    DashboardWidget,
    KPIDefinition,
    AnalyticsCache,
    ScheduledReport,
    DashboardType,
    DashboardVisibility,
    WidgetType,
    DataSource,
    AggregationType,
    KPICategory,
    KPIUnit,
    KPIDirection,
    ReportType,
    ReportFormat,
    ScheduleFrequency,
    DeliveryMethod,
    ReportStatus,
    CacheType,
    CacheStatus,
)


class TestDashboardConfig:
    """Testes para DashboardConfig model."""

    def test_create_dashboard_config(self):
        """Testa criação de dashboard config."""
        dashboard = DashboardConfig(
            id=uuid4(),
            name="Dashboard RH",
            description="Dashboard de métricas de RH",
            dashboard_type=DashboardType.EXECUTIVE,
            visibility=DashboardVisibility.ORGANIZATION,
            condominio_id=uuid4(),
            owner_id=uuid4(),
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
        assert DashboardVisibility.DEPARTMENT.value == "department"
        assert DashboardVisibility.ORGANIZATION.value == "organization"
        assert DashboardVisibility.PUBLIC.value == "public"

    def test_dashboard_with_layout_config(self):
        """Testa dashboard com configuração de layout."""
        dashboard = DashboardConfig(
            id=uuid4(),
            name="Dashboard Customizado",
            dashboard_type=DashboardType.CUSTOM,
            visibility=DashboardVisibility.PRIVATE,
            layout_config={"columns": 12, "rowHeight": 100},
            theme="dark",
            grid_columns=12,
            row_height=100,
        )

        assert dashboard.layout_config == {"columns": 12, "rowHeight": 100}
        assert dashboard.theme == "dark"
        assert dashboard.grid_columns == 12


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
            position_x=0,
            position_y=0,
            width=4,
            height=2,
        )

        assert widget.title == "Taxa de Absenteísmo"
        assert widget.widget_type == WidgetType.KPI_CARD
        assert widget.data_source == DataSource.ABSENCES
        assert widget.width == 4

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
            kpi_code="PUNCTUALITY_RATE",
            kpi_format="percentage",
            show_trend=True,
            show_comparison=True,
            comparison_period="previous_month",
        )

        assert widget.kpi_code == "PUNCTUALITY_RATE"
        assert widget.show_trend is True


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
        assert KPIUnit.NUMBER.value == "number"
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
            formula="(worked_hours / expected_hours) * 100",
            formula_description="Horas trabalhadas dividido por horas esperadas",
            data_sources=["time_entries", "employees"],
        )

        assert "worked_hours" in kpi.formula
        assert len(kpi.data_sources) == 2


class TestAnalyticsCache:
    """Testes para AnalyticsCache model."""

    def test_create_cache_entry(self):
        """Testa criação de entrada de cache."""
        now = datetime.utcnow()
        expires = now + timedelta(hours=1)

        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="kpi:ABSENTEEISM_RATE:condo123:2024-12",
            cache_type=CacheType.KPI_VALUE,
            data={"value": 2.5, "trend": "down"},
            ttl_seconds=3600,
            expires_at=expires,
            status=CacheStatus.VALID,
        )

        assert cache.cache_type == CacheType.KPI_VALUE
        assert cache.status == CacheStatus.VALID
        assert cache.ttl_seconds == 3600

    def test_cache_type_enum(self):
        """Testa enum CacheType."""
        assert CacheType.KPI_VALUE.value == "kpi_value"
        assert CacheType.DASHBOARD_DATA.value == "dashboard_data"
        assert CacheType.WIDGET_DATA.value == "widget_data"
        assert CacheType.AGGREGATION.value == "aggregation"
        assert CacheType.REPORT_DATA.value == "report_data"

    def test_cache_status_enum(self):
        """Testa enum CacheStatus."""
        assert CacheStatus.VALID.value == "valid"
        assert CacheStatus.EXPIRED.value == "expired"
        assert CacheStatus.INVALIDATED.value == "invalidated"
        assert CacheStatus.STALE.value == "stale"

    def test_cache_with_compression(self):
        """Testa cache com compressão."""
        cache = AnalyticsCache(
            id=uuid4(),
            cache_key="report:monthly:2024-12",
            cache_type=CacheType.REPORT_DATA,
            data={"large": "dataset"},
            compressed=True,
            data_size=1024,
            ttl_seconds=86400,
            expires_at=datetime.utcnow() + timedelta(days=1),
        )

        assert cache.compressed is True
        assert cache.data_size == 1024


class TestScheduledReport:
    """Testes para ScheduledReport model."""

    def test_create_scheduled_report(self):
        """Testa criação de relatório agendado."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório Mensal de Ponto",
            description="Relatório mensal de frequência",
            report_type=ReportType.TIME_ATTENDANCE,
            output_format=ReportFormat.PDF,
            schedule_frequency=ScheduleFrequency.MONTHLY,
            delivery_method=DeliveryMethod.EMAIL,
            condominio_id=uuid4(),
            owner_id=uuid4(),
        )

        assert report.name == "Relatório Mensal de Ponto"
        assert report.report_type == ReportType.TIME_ATTENDANCE
        assert report.output_format == ReportFormat.PDF
        assert report.schedule_frequency == ScheduleFrequency.MONTHLY

    def test_report_type_enum(self):
        """Testa enum ReportType."""
        assert ReportType.TIME_ATTENDANCE.value == "time_attendance"
        assert ReportType.OVERTIME_SUMMARY.value == "overtime_summary"
        assert ReportType.ABSENCE_REPORT.value == "absence_report"
        assert ReportType.KPI_SUMMARY.value == "kpi_summary"
        assert ReportType.COMPLIANCE_AUDIT.value == "compliance_audit"

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
        assert ReportStatus.ERROR.value == "error"

    def test_report_with_recipients(self):
        """Testa relatório com destinatários."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório Semanal",
            report_type=ReportType.OVERTIME_SUMMARY,
            output_format=ReportFormat.EXCEL,
            schedule_frequency=ScheduleFrequency.WEEKLY,
            delivery_method=DeliveryMethod.EMAIL,
            recipients=[
                {"email": "rh@empresa.com", "name": "RH"},
                {"email": "gestor@empresa.com", "name": "Gestor"},
            ],
            schedule_config={
                "day_of_week": 1,  # Segunda-feira
                "hour": 8,
                "minute": 0,
            },
        )

        assert len(report.recipients) == 2
        assert report.schedule_config["day_of_week"] == 1

    def test_report_with_filters(self):
        """Testa relatório com filtros."""
        report = ScheduledReport(
            id=uuid4(),
            name="Relatório por Departamento",
            report_type=ReportType.TIME_ATTENDANCE,
            output_format=ReportFormat.PDF,
            schedule_frequency=ScheduleFrequency.MONTHLY,
            delivery_method=DeliveryMethod.EMAIL,
            filters={
                "department_ids": ["dept-001", "dept-002"],
                "include_inactive": False,
            },
            included_sections=["summary", "details", "charts"],
        )

        assert "department_ids" in report.filters
        assert "summary" in report.included_sections


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
