"""
Schemas do módulo de Relatórios Gerenciais
Sprint 34: Relatórios Gerenciais
"""

from modules.reports.schemas.report_schemas import (
    # ReportTemplate
    ReportTemplateBase,
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportTemplateList,
    ReportTemplateFilter,
    # ReportSchedule
    ReportScheduleBase,
    ReportScheduleCreate,
    ReportScheduleUpdate,
    ReportScheduleResponse,
    ReportScheduleList,
    ReportScheduleFilter,
    # ReportExport
    ReportExportCreate,
    ReportExportResponse,
    ReportExportList,
    ReportExportDownload,
    ReportExportFilter,
    # ExecutiveKPI
    ExecutiveKPIBase,
    ExecutiveKPICreate,
    ExecutiveKPIUpdate,
    ExecutiveKPIValueUpdate,
    ExecutiveKPIResponse,
    ExecutiveKPIList,
    ExecutiveKPIFilter,
    KPIDashboard,
    # Benchmark
    BenchmarkBase,
    BenchmarkCreate,
    BenchmarkUpdate,
    BenchmarkCompanyValue,
    BenchmarkResponse,
    BenchmarkList,
    BenchmarkFilter,
    # Dashboards
    ReportsDashboard,
    ExecutiveDashboard,
)

__all__ = [
    # ReportTemplate
    "ReportTemplateBase",
    "ReportTemplateCreate",
    "ReportTemplateUpdate",
    "ReportTemplateResponse",
    "ReportTemplateList",
    "ReportTemplateFilter",
    # ReportSchedule
    "ReportScheduleBase",
    "ReportScheduleCreate",
    "ReportScheduleUpdate",
    "ReportScheduleResponse",
    "ReportScheduleList",
    "ReportScheduleFilter",
    # ReportExport
    "ReportExportCreate",
    "ReportExportResponse",
    "ReportExportList",
    "ReportExportDownload",
    "ReportExportFilter",
    # ExecutiveKPI
    "ExecutiveKPIBase",
    "ExecutiveKPICreate",
    "ExecutiveKPIUpdate",
    "ExecutiveKPIValueUpdate",
    "ExecutiveKPIResponse",
    "ExecutiveKPIList",
    "ExecutiveKPIFilter",
    "KPIDashboard",
    # Benchmark
    "BenchmarkBase",
    "BenchmarkCreate",
    "BenchmarkUpdate",
    "BenchmarkCompanyValue",
    "BenchmarkResponse",
    "BenchmarkList",
    "BenchmarkFilter",
    # Dashboards
    "ReportsDashboard",
    "ExecutiveDashboard",
]
