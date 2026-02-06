"""
Package: pcmso
Description: Modulo PCMSO - Programa de Controle Medico de Saude Ocupacional (NR-7)
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-7 (Portaria MTb 3.214/78)
"""

from .medical_exams import (
    MedicalExamManager,
    MedicalExam,
    ExamType,
    ExamStatus,
    FitnessResult,
    ComplementaryExam,
    MedicalExamError,
    ClinicPartner,
    OccupationalFunction,
    ExamRequirement,
    PCMSOConfig,
    MedicalExamModel,
    ClinicPartnerModel,
    get_exam_manager,
    init_exam_manager,
)

__all__ = [
    "MedicalExamManager",
    "MedicalExam",
    "ExamType",
    "ExamStatus",
    "FitnessResult",
    "ComplementaryExam",
    "MedicalExamError",
    "ClinicPartner",
    "OccupationalFunction",
    "ExamRequirement",
    "PCMSOConfig",
    "MedicalExamModel",
    "ClinicPartnerModel",
    "get_exam_manager",
    "init_exam_manager",
]

__version__ = "1.0.0"
