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
    AbsencePrediction,
    ActionSuggestion,
    AnomalyPattern,
    EmployeeAvailability,
    EmployeePreference,
    OccurrenceAnalysis,
    # Occurrence Analyzer
    OccurrenceAnalyzer,
    OccurrenceClassification,
    OptimizationConstraints,
    OptimizationResult,
    OvertimeForecast,
    # Predictive Analyzer
    PredictiveAnalyzer,
    # Scale Optimizer
    ScaleOptimizer,
    ShiftSlot,
    SimilarOccurrence,
    SubstituteSuggestion,
    # Substitution Optimizer
    SubstitutionOptimizer,
    SubstitutionRequest,
    TurnoverRisk,
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
