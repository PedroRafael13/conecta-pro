"""
Core do módulo Health Occupational - Implementações avançadas
============================================================

Código consolidado de 02_health_occupational/

Compliance: NR-7 (PCMSO), NR-6 (EPI), NR-9 (PPRA/PGR)
"""

# Medical Exams (PCMSO - NR-7)
from .medical_exams import (
    ExamType,
    ExamStatus,
    FitnessResult,
    ComplementaryExam,
    MedicalExamError,
    ExamRequirement,
    OccupationalFunction,
    ClinicPartner,
    MedicalExam,
)

# EPI Management (NR-6)
from .epi_management import (
    EPICategory,
    EPIStatus,
    DeliveryStatus,
    EPIManagementError,
    CACertificate,
)

# Risk Mapping (PPRA/PGR - NR-9)
from .risk_mapping import (
    RiskCategory,
    RiskLevel,
    ExposureFrequency,
    ControlType,
    RiskMappingError,
    RiskAgent,
    RiskMeasurement,
)

__all__ = [
    # medical_exams
    "ExamType",
    "ExamStatus",
    "FitnessResult",
    "ComplementaryExam",
    "MedicalExamError",
    "ExamRequirement",
    "OccupationalFunction",
    "ClinicPartner",
    "MedicalExam",
    # epi_management
    "EPICategory",
    "EPIStatus",
    "DeliveryStatus",
    "EPIManagementError",
    "CACertificate",
    # risk_mapping
    "RiskCategory",
    "RiskLevel",
    "ExposureFrequency",
    "ControlType",
    "RiskMappingError",
    "RiskAgent",
    "RiskMeasurement",
]
