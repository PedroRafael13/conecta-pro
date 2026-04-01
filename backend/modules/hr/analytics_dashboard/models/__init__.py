"""Models do módulo Analytics Dashboard."""

from .analytics_cache import (
    AnalyticsCache,
    CacheStatus,
    CacheType,
)
from .dashboard_config import (
    DashboardConfig,
    DashboardType,
    DashboardVisibility,
    RefreshInterval,
)
from .dashboard_widget import (
    AggregationType,
    DashboardWidget,
    DataSource,
    WidgetType,
)
from .kpi_definition import (
    DEFAULT_KPIS,
    KPICategory,
    KPIDefinition,
    KPIDirection,
    KPIFrequency,
    KPIUnit,
)
from .scheduled_report import (
    DeliveryMethod,
    ReportFormat,
    ReportStatus,
    ReportType,
    ScheduledReport,
    ScheduleFrequency,
)

__all__ = [
    # Dashboard Config
    "DashboardConfig",
    "DashboardType",
    "DashboardVisibility",
    "RefreshInterval",
    # Dashboard Widget
    "DashboardWidget",
    "WidgetType",
    "DataSource",
    "AggregationType",
    # KPI Definition
    "KPIDefinition",
    "KPICategory",
    "KPIUnit",
    "KPIDirection",
    "KPIFrequency",
    "DEFAULT_KPIS",
    # Analytics Cache
    "AnalyticsCache",
    "CacheType",
    "CacheStatus",
    # Scheduled Report
    "ScheduledReport",
    "ReportType",
    "ReportFormat",
    "ScheduleFrequency",
    "DeliveryMethod",
    "ReportStatus",
]
