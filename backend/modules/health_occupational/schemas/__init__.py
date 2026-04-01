"""Schemas do modulo de Saude Ocupacional."""

from modules.health_occupational.schemas.common import (
    PaginationParams,
    StandardResponse,
)
from modules.health_occupational.schemas.epi import (
    EPICreateRequest,
    EPIDeliveryListResponse,
    EPIDeliveryRequest,
    EPIDeliveryResponse,
    EPIInventoryResponse,
    EPIListResponse,
    EPIResponse,
    EPIUpdateRequest,
)
from modules.health_occupational.schemas.pcmso import (
    ASOListResponse,
    ASORequest,
    ASOResponse,
    ComplementaryExamRequest,
    ComplementaryExamResponse,
    MedicalExamListResponse,
    MedicalExamRequest,
    MedicalExamResponse,
)
from modules.health_occupational.schemas.ppra import (
    ControlMeasureRequest,
    ControlMeasureResponse,
    OccupationalRiskRequest,
    OccupationalRiskResponse,
    RiskMappingListResponse,
    RiskMappingRequest,
    RiskMappingResponse,
)

__all__ = [
    # PCMSO
    "MedicalExamRequest",
    "MedicalExamResponse",
    "MedicalExamListResponse",
    "ASORequest",
    "ASOResponse",
    "ASOListResponse",
    "ComplementaryExamRequest",
    "ComplementaryExamResponse",
    # PPRA
    "RiskMappingRequest",
    "RiskMappingResponse",
    "RiskMappingListResponse",
    "OccupationalRiskRequest",
    "OccupationalRiskResponse",
    "ControlMeasureRequest",
    "ControlMeasureResponse",
    # EPI
    "EPICreateRequest",
    "EPIUpdateRequest",
    "EPIResponse",
    "EPIListResponse",
    "EPIDeliveryRequest",
    "EPIDeliveryResponse",
    "EPIDeliveryListResponse",
    "EPIInventoryResponse",
    # Common
    "StandardResponse",
    "PaginationParams",
]
