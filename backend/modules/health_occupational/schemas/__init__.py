"""Schemas do modulo de Saude Ocupacional."""

from modules.health_occupational.schemas.pcmso import (
    MedicalExamRequest,
    MedicalExamResponse,
    MedicalExamListResponse,
    ASORequest,
    ASOResponse,
    ASOListResponse,
    ComplementaryExamRequest,
    ComplementaryExamResponse,
)
from modules.health_occupational.schemas.ppra import (
    RiskMappingRequest,
    RiskMappingResponse,
    RiskMappingListResponse,
    OccupationalRiskRequest,
    OccupationalRiskResponse,
    ControlMeasureRequest,
    ControlMeasureResponse,
)
from modules.health_occupational.schemas.epi import (
    EPICreateRequest,
    EPIUpdateRequest,
    EPIResponse,
    EPIListResponse,
    EPIDeliveryRequest,
    EPIDeliveryResponse,
    EPIDeliveryListResponse,
    EPIInventoryResponse,
)
from modules.health_occupational.schemas.common import (
    StandardResponse,
    PaginationParams,
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
