"""
Schemas Pydantic do modulo CCT 2026.
"""

from .benefits_schemas import (
    BenefitConfigCreate,
    BenefitConfigResponse,
    BenefitsCCTResponse,
    BenefitsValidationRequest,
    BenefitsValidationResponse,
    TaxaNegocialResponse,
)
from .compliance_schemas import (
    ComplianceCheckRequest,
    ComplianceCheckResponse,
    ComplianceSummaryResponse,
)
from .salary_schemas import (
    SalaryAdjustmentRequest,
    SalaryAdjustmentResponse,
    SalaryTableResponse,
    SalaryValidationRequest,
    SalaryValidationResponse,
)
from .schedule_schemas import (
    NightShiftCalculationRequest,
    NightShiftCalculationResponse,
    OvertimeCalculationRequest,
    OvertimeCalculationResponse,
    ScheduleValidationRequest,
    ScheduleValidationResponse,
)
from .termination_schemas import (
    TerminationValidationRequest,
    TerminationValidationResponse,
    VacationProportionalRequest,
    VacationProportionalResponse,
)

__all__ = [
    "SalaryTableResponse",
    "SalaryValidationRequest",
    "SalaryValidationResponse",
    "SalaryAdjustmentRequest",
    "SalaryAdjustmentResponse",
    "BenefitsCCTResponse",
    "BenefitsValidationRequest",
    "BenefitsValidationResponse",
    "TaxaNegocialResponse",
    "BenefitConfigCreate",
    "BenefitConfigResponse",
    "ScheduleValidationRequest",
    "ScheduleValidationResponse",
    "OvertimeCalculationRequest",
    "OvertimeCalculationResponse",
    "NightShiftCalculationRequest",
    "NightShiftCalculationResponse",
    "ComplianceCheckRequest",
    "ComplianceCheckResponse",
    "ComplianceSummaryResponse",
    "TerminationValidationRequest",
    "TerminationValidationResponse",
    "VacationProportionalRequest",
    "VacationProportionalResponse",
]
