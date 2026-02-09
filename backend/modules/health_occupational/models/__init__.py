"""Models do modulo de Saude Ocupacional."""

from modules.health_occupational.models.epi import (
    EPI,
    DeliveryReason,
    EPICategory,
    EPIDelivery,
    EPIInventory,
    EPIStatus,
)
from modules.health_occupational.models.pcmso import (
    ASO,
    ComplementaryExam,
    ExamStatus,
    ExamType,
    FitnessResult,
    MedicalExam,
)
from modules.health_occupational.models.ppra import (
    ControlMeasure,
    OccupationalRisk,
    RiskAgent,
    RiskCategory,
    RiskLevel,
    RiskMapping,
)

__all__ = [
    # PCMSO
    "MedicalExam",
    "ASO",
    "ComplementaryExam",
    "ExamType",
    "ExamStatus",
    "FitnessResult",
    # PPRA
    "RiskMapping",
    "OccupationalRisk",
    "ControlMeasure",
    "RiskCategory",
    "RiskLevel",
    "RiskAgent",
    # EPI
    "EPI",
    "EPIDelivery",
    "EPIInventory",
    "EPICategory",
    "EPIStatus",
    "DeliveryReason",
]
