"""
Agentes de IA para Operacoes.

Author: Conecta PRO Team
Date: 2026-01-18
"""

from .scale_optimizer import (
    ScaleOptimizer,
    ShiftSlot,
    EmployeeAvailability,
    EmployeePreference,
    OptimizationConstraints,
    OptimizationResult,
)
from .substitution_optimizer import (
    SubstitutionOptimizer,
    SubstituteSuggestion,
    SubstitutionRequest,
)
from .predictive_analyzer import (
    PredictiveAnalyzer,
    AbsencePrediction,
    TurnoverRisk,
    OvertimeForecast,
    AnomalyPattern,
)
from .occurrence_analyzer import (
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
