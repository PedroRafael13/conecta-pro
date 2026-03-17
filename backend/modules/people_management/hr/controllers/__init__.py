"""
Controllers do módulo Departamento Pessoal (DP/HR).

Exporta todos os routers disponíveis para inclusão no aggregator.
"""

from .admission_controller import router as admission_router
from .benefits_controller import router as benefits_router
from .contract_controller import router as contract_router
from .discipline_controller import router as discipline_router
from .employee_controller import router as employee_router
from .esocial_controller import router as esocial_router
from .payroll_controller import router as payroll_router
from .payroll_export_controller import router as payroll_export_router
from .reimbursement_controller import router as reimbursement_router
from .termination_controller import router as termination_router
from .time_tracking_controller import router as time_tracking_router
from .vacation_controller import router as vacation_router

__all__ = [
    "employee_router",
    "admission_router",
    "termination_router",
    "benefits_router",
    "contract_router",
    "vacation_router",
    "discipline_router",
    "time_tracking_router",
    "payroll_router",
    "reimbursement_router",
    "payroll_export_router",
    "esocial_router",
]
