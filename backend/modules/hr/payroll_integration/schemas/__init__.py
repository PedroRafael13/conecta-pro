"""Schemas do módulo de integração com folha de pagamento."""

from modules.hr.payroll_integration.schemas.employee_config import (
    BenefitConfigSchema,
    EmployeePayrollConfigCreate,
    EmployeePayrollConfigResponse,
    EmployeePayrollConfigUpdate,
    LoanConfigSchema,
    SalaryCalculationRequest,
    SalaryCalculationResponse,
)
from modules.hr.payroll_integration.schemas.payroll_event import (
    EmployeePayrollSummary,
    EventAdjustmentRequest,
    PayrollEventBulkCreate,
    PayrollEventCreate,
    PayrollEventListResponse,
    PayrollEventResponse,
    PayrollEventUpdate,
)
from modules.hr.payroll_integration.schemas.payroll_export import (
    ESocialExportRequest,
    ESocialTransmissionResponse,
    ExportDownloadResponse,
    ExportProgressResponse,
    PayrollExportCreate,
    PayrollExportListResponse,
    PayrollExportResponse,
    PayrollExportUpdate,
)
from modules.hr.payroll_integration.schemas.payroll_integration import (
    ESocialConfigSchema,
    IntegrationSyncRequest,
    IntegrationSyncResponse,
    PayrollIntegrationCreate,
    PayrollIntegrationResponse,
    PayrollIntegrationUpdate,
)
from modules.hr.payroll_integration.schemas.payroll_period import (
    PayrollPeriodCreate,
    PayrollPeriodListResponse,
    PayrollPeriodResponse,
    PayrollPeriodSummary,
    PayrollPeriodUpdate,
    PeriodCalculationRequest,
    PeriodCalculationResponse,
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
