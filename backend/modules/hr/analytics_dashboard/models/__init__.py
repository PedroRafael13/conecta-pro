"""Models do módulo Analytics Dashboard."""

from .dashboard_config import (
    DashboardConfig,
    DashboardType,
    DashboardVisibility,
    RefreshInterval,
)
from .dashboard_widget import (
    DashboardWidget,
    WidgetType,
    DataSource,
    AggregationType,
)
from .kpi_definition import (
    KPIDefinition,
    KPICategory,
    KPIUnit,
    KPIDirection,
    KPIFrequency,
    DEFAULT_KPIS,
)
from .analytics_cache import (
    AnalyticsCache,
    CacheType,
    CacheStatus,
)
from .scheduled_report import (
    ScheduledReport,
    ReportType,
    ReportFormat,
    ScheduleFrequency,
    DeliveryMethod,
    ReportStatus,
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
