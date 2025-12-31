"""Schemas do módulo de integração com folha de pagamento."""

from modules.hr.payroll_integration.schemas.payroll_period import (
    PayrollPeriodCreate,
    PayrollPeriodUpdate,
    PayrollPeriodResponse,
    PayrollPeriodSummary,
    PayrollPeriodListResponse,
    PeriodCalculationRequest,
    PeriodCalculationResponse,
)
from modules.hr.payroll_integration.schemas.payroll_event import (
    PayrollEventCreate,
    PayrollEventUpdate,
    PayrollEventResponse,
    PayrollEventListResponse,
    PayrollEventBulkCreate,
    EventAdjustmentRequest,
    EmployeePayrollSummary,
)
from modules.hr.payroll_integration.schemas.payroll_integration import (
    PayrollIntegrationCreate,
    PayrollIntegrationUpdate,
    PayrollIntegrationResponse,
    IntegrationSyncRequest,
    IntegrationSyncResponse,
    ESocialConfigSchema,
)
from modules.hr.payroll_integration.schemas.payroll_export import (
    PayrollExportCreate,
    PayrollExportUpdate,
    PayrollExportResponse,
    ExportProgressResponse,
    ExportDownloadResponse,
    ESocialExportRequest,
    ESocialTransmissionResponse,
    PayrollExportListResponse,
)
from modules.hr.payroll_integration.schemas.employee_config import (
    EmployeePayrollConfigCreate,
    EmployeePayrollConfigUpdate,
    EmployeePayrollConfigResponse,
    SalaryCalculationRequest,
    SalaryCalculationResponse,
    BenefitConfigSchema,
    LoanConfigSchema,
)

__all__ = [
    # PayrollPeriod
    "PayrollPeriodCreate",
    "PayrollPeriodUpdate",
    "PayrollPeriodResponse",
    "PayrollPeriodSummary",
    "PayrollPeriodListResponse",
    "PeriodCalculationRequest",
    "PeriodCalculationResponse",
    # PayrollEvent
    "PayrollEventCreate",
    "PayrollEventUpdate",
    "PayrollEventResponse",
    "PayrollEventListResponse",
    "PayrollEventBulkCreate",
    "EventAdjustmentRequest",
    "EmployeePayrollSummary",
    # PayrollIntegration
    "PayrollIntegrationCreate",
    "PayrollIntegrationUpdate",
    "PayrollIntegrationResponse",
    "IntegrationSyncRequest",
    "IntegrationSyncResponse",
    "ESocialConfigSchema",
    # PayrollExport
    "PayrollExportCreate",
    "PayrollExportUpdate",
    "PayrollExportResponse",
    "PayrollExportListResponse",
    "ExportProgressResponse",
    "ExportDownloadResponse",
    "ESocialExportRequest",
    "ESocialTransmissionResponse",
    # EmployeeConfig
    "EmployeePayrollConfigCreate",
    "EmployeePayrollConfigUpdate",
    "EmployeePayrollConfigResponse",
    "SalaryCalculationRequest",
    "SalaryCalculationResponse",
    "BenefitConfigSchema",
    "LoanConfigSchema",
]
