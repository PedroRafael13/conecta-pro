"""
Package: health_occupational
Description: Modulo de Saude Ocupacional - PCMSO, PPRA/PGR, EPI/EPC
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-4, NR-6, NR-7, NR-9 (Portaria MTb 3.214/78)
"""

from .pcmso import (
    MedicalExamManager,
    MedicalExam,
    ExamType,
    ExamStatus,
    FitnessResult,
    ComplementaryExam,
    PCMSOConfig,
    get_exam_manager,
    init_exam_manager,
)

from .ppra import (
    RiskMappingManager,
    OccupationalRisk,
    RiskAgent,
    RiskCategory,
    RiskLevel,
    ControlType,
    PPRAConfig,
    get_risk_manager,
    init_risk_manager,
)

from .epi_epc import (
    EPIManager,
    EPIModel,
    EPIInventoryItem,
    EPIDelivery,
    EPICategory,
    EPIStatus,
    EPIConfig,
    get_epi_manager,
    init_epi_manager,
)

__all__ = [
    # PCMSO
    "MedicalExamManager",
    "MedicalExam",
    "ExamType",
    "ExamStatus",
    "FitnessResult",
    "ComplementaryExam",
    "PCMSOConfig",
    "get_exam_manager",
    "init_exam_manager",
    # PPRA
    "RiskMappingManager",
    "OccupationalRisk",
    "RiskAgent",
    "RiskCategory",
    "RiskLevel",
    "ControlType",
    "PPRAConfig",
    "get_risk_manager",
    "init_risk_manager",
    # EPI
    "EPIManager",
    "EPIModel",
    "EPIInventoryItem",
    "EPIDelivery",
    "EPICategory",
    "EPIStatus",
    "EPIConfig",
    "get_epi_manager",
    "init_epi_manager",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
