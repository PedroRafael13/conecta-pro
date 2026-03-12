"""
Schemas Pydantic do módulo Departamento Pessoal (DP/HR).
"""

from .admission import (
    AdmissionProcessCreate,
    AdmissionProcessResponse,
    AdmissionProcessUpdate,
)
from .benefits import BenefitCreate, BenefitResponse, BenefitUpdate
from .contract import ContractCreate, ContractResponse, ContractUpdate
from .employee import DPEmployeeList, DPEmployeeRead, DPEmployeeUpdate
from .termination import (
    TerminationCalculation,
    TerminationCreate,
    TerminationResponse,
    TerminationUpdate,
)

__all__ = [
    "DPEmployeeRead",
    "DPEmployeeList",
    "DPEmployeeUpdate",
    "AdmissionProcessCreate",
    "AdmissionProcessUpdate",
    "AdmissionProcessResponse",
    "TerminationCreate",
    "TerminationUpdate",
    "TerminationResponse",
    "TerminationCalculation",
    "BenefitCreate",
    "BenefitUpdate",
    "BenefitResponse",
    "ContractCreate",
    "ContractUpdate",
    "ContractResponse",
]
