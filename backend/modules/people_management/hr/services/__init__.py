"""
Services do módulo Departamento Pessoal (DP/HR).

Exporta todos os serviços disponíveis, tanto novos quanto re-exportados
de módulos existentes.
"""

from .admission_service import AdmissionService
from .benefits_service import BenefitsService
from .contract_service import ContractService
from .discipline_service import DisciplineService
from .document_service import DocumentService
from .employee_service import EmployeeService
from .esocial_service import ESocialEventService
from .occupational_health_service import OccupationalHealthService
from .overtime_bank_service import OvertimeBankService
from .payroll_export_service import PayrollExportService
from .payroll_service import PayrollService
from .reimbursement_service import ReimbursementService
from .termination_service import TerminationService
from .time_record_service import TimeRecordService
from .time_tracking_service import TimeTrackingService
from .vacation_service import VacationService

__all__ = [
    "EmployeeService",
    "AdmissionService",
    "TerminationService",
    "VacationService",
    "DisciplineService",
    "TimeTrackingService",
    "OvertimeBankService",
    "PayrollService",
    "BenefitsService",
    "ContractService",
    "ReimbursementService",
    "DocumentService",
    "OccupationalHealthService",
    "ESocialEventService",
    "PayrollExportService",
    "TimeRecordService",
]
