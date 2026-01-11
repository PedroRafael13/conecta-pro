"""Models do modulo de Saude Ocupacional."""

from modules.health_occupational.models.pcmso import (
    MedicalExam,
    ASO,
    ComplementaryExam,
    ExamType,
    ExamStatus,
    FitnessResult,
)
from modules.health_occupational.models.ppra import (
    RiskMapping,
    OccupationalRisk,
    ControlMeasure,
    RiskCategory,
    RiskLevel,
    RiskAgent,
)
from modules.health_occupational.models.epi import (
    EPI,
    EPIDelivery,
    EPIInventory,
    EPICategory,
    EPIStatus,
    DeliveryReason,
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
