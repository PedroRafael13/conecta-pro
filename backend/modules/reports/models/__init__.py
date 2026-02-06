"""
Models do módulo de Relatórios Gerenciais
Sprint 34: Relatórios Gerenciais
"""

from modules.reports.models.report_template import (
    ReportTemplate,
    ReportCategory,
    ReportFormat,
    ReportType,
    TemplateStatus,
    ChartType,
)

from modules.reports.models.report_schedule import (
    ReportSchedule,
    ScheduleFrequency,
    ScheduleStatus,
    DeliveryMethod,
)

from modules.reports.models.report_export import (
    ReportExport,
    ExportStatus,
    ExportTrigger,
    ExportFormat,
)

from modules.reports.models.executive_kpi import (
    ExecutiveKPI,
    KPICategory,
    KPIType,
    KPIDirection,
    KPIStatus,
    KPIAlertLevel,
    AggregationPeriod,
)

from modules.reports.models.benchmark import (
    Benchmark,
    BenchmarkCategory,
    BenchmarkType,
    BenchmarkSource,
    BenchmarkStatus,
    ComparisonResult,
)

__all__ = [
    # ReportTemplate
    "ReportTemplate",
    "ReportCategory",
    "ReportFormat",
    "ReportType",
    "TemplateStatus",
    "ChartType",
    # ReportSchedule
    "ReportSchedule",
    "ScheduleFrequency",
    "ScheduleStatus",
    "DeliveryMethod",
    # ReportExport
    "ReportExport",
    "ExportStatus",
    "ExportTrigger",
    "ExportFormat",
    # ExecutiveKPI
    "ExecutiveKPI",
    "KPICategory",
    "KPIType",
    "KPIDirection",
    "KPIStatus",
    "KPIAlertLevel",
    "AggregationPeriod",
    # Benchmark
    "Benchmark",
    "BenchmarkCategory",
    "BenchmarkType",
    "BenchmarkSource",
    "BenchmarkStatus",
    "ComparisonResult",
]
