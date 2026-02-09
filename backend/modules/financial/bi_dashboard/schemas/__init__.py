"""Schemas de BI e Dashboards Financeiros - Sprint 30."""

from modules.financial.bi_dashboard.schemas.cache_schemas import (
    CacheEntry,
    CacheInvalidate,
    CacheStats,
)
from modules.financial.bi_dashboard.schemas.dashboard_schemas import (
    DashboardCreate,
    DashboardFilters,
    DashboardListResponse,
    DashboardResponse,
    DashboardStats,
    DashboardUpdate,
)
from modules.financial.bi_dashboard.schemas.kpi_schemas import (
    KPICreate,
    KPIFilters,
    KPIHistory,
    KPIResponse,
    KPISummary,
    KPIUpdate,
    KPIValue,
)
from modules.financial.bi_dashboard.schemas.report_schemas import (
    ReportCreate,
    ReportExecution,
    ReportFilters,
    ReportResponse,
    ReportSchedule,
    ReportUpdate,
)
from modules.financial.bi_dashboard.schemas.widget_schemas import (
    WidgetCreate,
    WidgetData,
    WidgetFilters,
    WidgetPosition,
    WidgetResponse,
    WidgetUpdate,
)

__all__ = [
    # Dashboard
    "DashboardCreate",
    "DashboardUpdate",
    "DashboardResponse",
    "DashboardListResponse",
    "DashboardFilters",
    "DashboardStats",
    # Widget
    "WidgetCreate",
    "WidgetUpdate",
    "WidgetResponse",
    "WidgetData",
    "WidgetPosition",
    "WidgetFilters",
    # KPI
    "KPICreate",
    "KPIUpdate",
    "KPIResponse",
    "KPIValue",
    "KPIHistory",
    "KPIFilters",
    "KPISummary",
    # Report
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportSchedule",
    "ReportExecution",
    "ReportFilters",
    # Cache
    "CacheEntry",
    "CacheStats",
    "CacheInvalidate",
]
