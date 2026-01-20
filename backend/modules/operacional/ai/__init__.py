"""
Module: ai
Description: Modulo de IA Operacional
Author: Conecta PRO Team
Date: 2026-01-18

Este modulo fornece:
- Agentes operacionais inteligentes
- Otimizador de escalas
- Otimizador de substituicoes
- Analisador de ocorrencias
- Analisador preditivo
- Skills operacionais
- Orquestrador de IA
"""

from .agents import (
    # Scale Optimizer
    ScaleOptimizer,
    ShiftSlot,
    EmployeeAvailability,
    EmployeePreference,
    OptimizationConstraints,
    OptimizationResult,
    # Substitution Optimizer
    SubstitutionOptimizer,
    SubstituteSuggestion,
    SubstitutionRequest,
    # Predictive Analyzer
    PredictiveAnalyzer,
    AbsencePrediction,
    TurnoverRisk,
    OvertimeForecast,
    AnomalyPattern,
    # Occurrence Analyzer
    OccurrenceAnalyzer,
    OccurrenceAnalysis,
    OccurrenceClassification,
    ActionSuggestion,
    SimilarOccurrence,
)

__all__ = [
    # Scale Optimizer
    "ScaleOptimizer",
    "ShiftSlot",
    "EmployeeAvailability",
    "EmployeePreference",
    "OptimizationConstraints",
    "OptimizationResult",
    # Substitution Optimizer
    "SubstitutionOptimizer",
    "SubstituteSuggestion",
    "SubstitutionRequest",
    # Predictive Analyzer
    "PredictiveAnalyzer",
    "AbsencePrediction",
    "TurnoverRisk",
    "OvertimeForecast",
    "AnomalyPattern",
    # Occurrence Analyzer
    "OccurrenceAnalyzer",
    "OccurrenceAnalysis",
    "OccurrenceClassification",
    "ActionSuggestion",
    "SimilarOccurrence",
]

__version__ = "1.0.0"
