"""Módulo Analytics Dashboard - Dashboard e KPIs de RH."""

from .controllers import router
from .models import (
    DashboardConfig,
    DashboardWidget,
    KPIDefinition,
    AnalyticsCache,
    ScheduledReport,
    DashboardType,
    DashboardVisibility,
    WidgetType,
    DataSource,
    KPICategory,
    KPIUnit,
    ReportType,
    ReportFormat,
)
from .services import (
    DashboardService,
    KPICalculatorService,
    MetricsAggregatorService,
    ReportGeneratorService,
)

__all__ = [
    # Router
    "router",
    # Models
    "DashboardConfig",
    "DashboardWidget",
    "KPIDefinition",
    "AnalyticsCache",
    "ScheduledReport",
    # Enums
    "DashboardType",
    "DashboardVisibility",
    "WidgetType",
    "DataSource",
    "KPICategory",
    "KPIUnit",
    "ReportType",
    "ReportFormat",
    # Services
    "DashboardService",
    "KPICalculatorService",
    "MetricsAggregatorService",
    "ReportGeneratorService",
]
