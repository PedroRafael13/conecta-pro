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
from .time_record import (
    ClockInRequest,
    ClockOutRequest,
    DailyRecordsResponse,
    MonthlySummaryResponse,
    TimeRecordCreate,
    TimeRecordListResponse,
    TimeRecordResponse,
    TimeRecordUpdate,
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
    "TimeRecordCreate",
    "TimeRecordUpdate",
    "TimeRecordResponse",
    "TimeRecordListResponse",
    "ClockInRequest",
    "ClockOutRequest",
    "MonthlySummaryResponse",
    "DailyRecordsResponse",
]
