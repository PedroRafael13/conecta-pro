"""
Core do módulo Health Occupational - Implementações avançadas
============================================================

Código consolidado de 02_health_occupational/

Compliance: NR-7 (PCMSO), NR-6 (EPI), NR-9 (PPRA/PGR)
"""

# Medical Exams (PCMSO - NR-7)
# EPI Management (NR-6)
from .epi_management import (
    CACertificate,
    DeliveryStatus,
    EPICategory,
    EPIManagementError,
    EPIStatus,
)
from .medical_exams import (
    ClinicPartner,
    ComplementaryExam,
    ExamRequirement,
    ExamStatus,
    ExamType,
    FitnessResult,
    MedicalExam,
    MedicalExamError,
    OccupationalFunction,
)

# Risk Mapping (PPRA/PGR - NR-9)
from .risk_mapping import (
    ControlType,
    ExposureFrequency,
    RiskAgent,
    RiskCategory,
    RiskLevel,
    RiskMappingError,
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
