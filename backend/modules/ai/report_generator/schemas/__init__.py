"""Report Generator Schemas."""

from modules.ai.report_generator.schemas.report_schemas import (
    # Enums
    ReportTypeEnum,
    ReportStatusEnum,
    ReportFormatEnum,
    ReportPriorityEnum,
    TemplateCategoryEnum,
    TemplateStatusEnum,
    DataSourceEnum,
    ScheduleFrequencyEnum,
    ScheduleStatusEnum,
    DeliveryMethodEnum,
    ExecutionStatusEnum,
    ExecutionTriggerEnum,
    SectionTypeEnum,
    SectionLayoutEnum,
    WidgetTypeEnum,
    WidgetSizeEnum,
    # Report
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
    ReportSummary,
    ReportFilter,
    # Template
    ReportTemplateCreate,
    ReportTemplateUpdate,
    ReportTemplateResponse,
    ReportTemplateListResponse,
    TemplateParameter,
    TemplateSectionConfig,
    # Schedule
    ReportScheduleCreate,
    ReportScheduleUpdate,
    ReportScheduleResponse,
    ReportScheduleListResponse,
    # Execution
    ReportExecutionResponse,
    ReportExecutionListResponse,
    ExecutionMetrics,
    # Section
    ReportSectionCreate,
    ReportSectionUpdate,
    ReportSectionResponse,
    # Widget
    ReportWidgetCreate,
    ReportWidgetUpdate,
    ReportWidgetResponse,
    # Generation
    GenerateReportRequest,
    GenerateReportResponse,
    # Export
    ExportReportRequest,
    ExportReportResponse,
    # Dashboard
    ReportDashboardResponse,
    ReportStatsResponse,
)

__all__ = [
    # Enums
    "ReportTypeEnum",
    "ReportStatusEnum",
    "ReportFormatEnum",
    "ReportPriorityEnum",
    "TemplateCategoryEnum",
    "TemplateStatusEnum",
    "DataSourceEnum",
    "ScheduleFrequencyEnum",
    "ScheduleStatusEnum",
    "DeliveryMethodEnum",
    "ExecutionStatusEnum",
    "ExecutionTriggerEnum",
    "SectionTypeEnum",
    "SectionLayoutEnum",
    "WidgetTypeEnum",
    "WidgetSizeEnum",
    # Report
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportListResponse",
    "ReportSummary",
    "ReportFilter",
    # Template
    "ReportTemplateCreate",
    "ReportTemplateUpdate",
    "ReportTemplateResponse",
    "ReportTemplateListResponse",
    "TemplateParameter",
    "TemplateSectionConfig",
    # Schedule
    "ReportScheduleCreate",
    "ReportScheduleUpdate",
    "ReportScheduleResponse",
    "ReportScheduleListResponse",
    # Execution
    "ReportExecutionResponse",
    "ReportExecutionListResponse",
    "ExecutionMetrics",
    # Section
    "ReportSectionCreate",
    "ReportSectionUpdate",
    "ReportSectionResponse",
    # Widget
    "ReportWidgetCreate",
    "ReportWidgetUpdate",
    "ReportWidgetResponse",
    # Generation
    "GenerateReportRequest",
    "GenerateReportResponse",
    # Export
    "ExportReportRequest",
    "ExportReportResponse",
    # Dashboard
    "ReportDashboardResponse",
    "ReportStatsResponse",
]
