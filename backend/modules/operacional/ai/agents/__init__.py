"""
Agentes de IA para Operacoes.

Author: Conecta PRO Team
Date: 2026-01-18
"""

from .occurrence_analyzer import (
    ActionSuggestion,
    OccurrenceAnalysis,
    OccurrenceAnalyzer,
    OccurrenceClassification,
    SimilarOccurrence,
)
from .predictive_analyzer import (
    AbsencePrediction,
    AnomalyPattern,
    OvertimeForecast,
    PredictiveAnalyzer,
    TurnoverRisk,
)
from .scale_optimizer import (
    EmployeeAvailability,
    EmployeePreference,
    OptimizationConstraints,
    OptimizationResult,
    ScaleOptimizer,
    ShiftSlot,
)
from .substitution_optimizer import (
    SubstituteSuggestion,
    SubstitutionOptimizer,
    SubstitutionRequest,
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
