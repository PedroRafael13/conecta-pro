"""Report Generator Schemas."""

from modules.ai.report_generator.schemas.report_schemas import (
    DataSourceEnum,
    DeliveryMethodEnum,
    ExecutionMetrics,
    ExecutionStatusEnum,
    ExecutionTriggerEnum,
    # Export
    ExportReportRequest,
    ExportReportResponse,
    # Generation
    GenerateReportRequest,
    GenerateReportResponse,
    # Report
    ReportCreate,
    # Dashboard
    ReportDashboardResponse,
    ReportExecutionListResponse,
    # Execution
    ReportExecutionResponse,
    ReportFilter,
    ReportFormatEnum,
    ReportListResponse,
    ReportPriorityEnum,
    ReportResponse,
    # Schedule
    ReportScheduleCreate,
    ReportScheduleListResponse,
    ReportScheduleResponse,
    ReportScheduleUpdate,
    # Section
    ReportSectionCreate,
    ReportSectionResponse,
    ReportSectionUpdate,
    ReportStatsResponse,
    ReportStatusEnum,
    ReportSummary,
    # Template
    ReportTemplateCreate,
    ReportTemplateListResponse,
    ReportTemplateResponse,
    ReportTemplateUpdate,
    # Enums
    ReportTypeEnum,
    ReportUpdate,
    # Widget
    ReportWidgetCreate,
    ReportWidgetResponse,
    ReportWidgetUpdate,
    ScheduleFrequencyEnum,
    ScheduleStatusEnum,
    SectionLayoutEnum,
    SectionTypeEnum,
    TemplateCategoryEnum,
    TemplateParameter,
    TemplateSectionConfig,
    TemplateStatusEnum,
    WidgetSizeEnum,
    WidgetTypeEnum,
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
