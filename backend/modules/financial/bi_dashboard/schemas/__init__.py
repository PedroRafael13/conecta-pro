"""Schemas de BI e Dashboards Financeiros - Sprint 30."""

from modules.financial.bi_dashboard.schemas.dashboard_schemas import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardListResponse,
    DashboardFilters,
    DashboardStats,
)
from modules.financial.bi_dashboard.schemas.widget_schemas import (
    WidgetCreate,
    WidgetUpdate,
    WidgetResponse,
    WidgetData,
    WidgetPosition,
    WidgetFilters,
)
from modules.financial.bi_dashboard.schemas.kpi_schemas import (
    KPICreate,
    KPIUpdate,
    KPIResponse,
    KPIValue,
    KPIHistory,
    KPIFilters,
    KPISummary,
)
from modules.financial.bi_dashboard.schemas.report_schemas import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportSchedule,
    ReportExecution,
    ReportFilters,
)
from modules.financial.bi_dashboard.schemas.cache_schemas import (
    CacheEntry,
    CacheStats,
    CacheInvalidate,
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
