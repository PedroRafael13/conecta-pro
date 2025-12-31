"""Módulo de integração com folha de pagamento.

Este módulo fornece funcionalidades completas para:
- Gestão de períodos de folha (mensal, quinzenal, etc.)
- Cálculo automático de folha (INSS, IRRF, banco de horas)
- Rubricas e eventos de folha
- Exportação em múltiplos formatos (CSV, JSON, TXT, CNAB240)
- Integração com eSocial
- Integração com sistemas externos (TOTVS, Senior, etc.)
"""

from modules.hr.payroll_integration.controllers import router
from modules.hr.payroll_integration.models import (
    PayrollPeriod,
    PeriodType,
    PeriodStatus,
    PayrollEvent,
    EventType,
    EventCategory,
    EventStatus,
    PayrollIntegration,
    IntegrationType,
    IntegrationStatus,
    PayrollExport,
    ExportFormat,
    ExportStatus,
    EmployeePayrollConfig,
    OvertimeRule,
    BankHoursPolicy,
    ContractType,
    WorkScheduleType,
)
from modules.hr.payroll_integration.services import (
    PayrollCalculationService,
    PayrollEventService,
    PayrollExportService,
    ESocialService,
)

__all__ = [
    # Router
    "router",
    # Models
    "PayrollPeriod",
    "PeriodType",
    "PeriodStatus",
    "PayrollEvent",
    "EventType",
    "EventCategory",
    "EventStatus",
    "PayrollIntegration",
    "IntegrationType",
    "IntegrationStatus",
    "PayrollExport",
    "ExportFormat",
    "ExportStatus",
    "EmployeePayrollConfig",
    "OvertimeRule",
    "BankHoursPolicy",
    "ContractType",
    "WorkScheduleType",
    # Services
    "PayrollCalculationService",
    "PayrollEventService",
    "PayrollExportService",
    "ESocialService",
]
