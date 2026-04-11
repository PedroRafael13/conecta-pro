"""Stubs das classes de AI do módulo operacional.
Mantém compatibilidade de importação enquanto o módulo AI completo não está disponível.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AbsencePrediction:
    employee_id: str = ""
    probability: float = 0.0
    reason: str = ""


@dataclass
class ActionSuggestion:
    action: str = ""
    priority: str = ""


@dataclass
class AnomalyPattern:
    pattern: str = ""
    severity: str = ""


@dataclass
class AutomaticFeedback:
    message: str = ""
    score: float = 0.0


@dataclass
class ContingencyPlan:
    steps: list = field(default_factory=list)


@dataclass
class CoveragePredictorAgent:
    model_id: str = ""

    def predict(self, *args: Any, **kwargs: Any) -> dict:
        return {}


@dataclass
class CoverageRisk:
    risk_level: str = "low"
    details: str = ""


@dataclass
class EmployeeAbsenceRisk:
    employee_id: str = ""
    risk_score: float = 0.0


@dataclass
class EmployeeAvailability:
    employee_id: str = ""
    available: bool = True


@dataclass
class EmployeePreference:
    employee_id: str = ""
    preferences: dict = field(default_factory=dict)


@dataclass
class OccurrenceAnalysis:
    occurrence_id: str = ""
    analysis: str = ""


@dataclass
class OccurrenceAnalyzer:
    def analyze(self, *args: Any, **kwargs: Any) -> OccurrenceAnalysis:
        return OccurrenceAnalysis()


@dataclass
class OccurrenceClassification:
    category: str = ""
    severity: str = ""


@dataclass
class OptimizationConstraints:
    max_hours: float = 0.0
    min_coverage: int = 0


@dataclass
class OptimizationResult:
    score: float = 0.0
    assignments: list = field(default_factory=list)


@dataclass
class OvertimeForecast:
    employee_id: str = ""
    forecast_hours: float = 0.0


@dataclass
class PerformanceAlert:
    employee_id: str = ""
    alert_type: str = ""
    message: str = ""


@dataclass
class PerformanceAnalyzerAgent:
    def analyze(self, *args: Any, **kwargs: Any) -> dict:
        return {}


@dataclass
class PerformanceDimension:
    name: str = ""
    score: float = 0.0


@dataclass
class PerformanceScore:
    employee_id: str = ""
    total: float = 0.0
    dimensions: list = field(default_factory=list)


@dataclass
class PredictiveAnalyzer:
    def predict(self, *args: Any, **kwargs: Any) -> dict:
        return {}


@dataclass
class ScaleOptimizer:
    def optimize(self, *args: Any, **kwargs: Any) -> OptimizationResult:
        return OptimizationResult()


@dataclass
class ShiftSlot:
    start: str = ""
    end: str = ""
    employee_id: str = ""


@dataclass
class SimilarOccurrence:
    occurrence_id: str = ""
    similarity: float = 0.0


@dataclass
class SubstituteSuggestion:
    employee_id: str = ""
    score: float = 0.0


@dataclass
class SubstitutionOptimizer:
    def suggest(self, *args: Any, **kwargs: Any) -> list:
        return []


@dataclass
class SubstitutionRequest:
    original_employee_id: str = ""
    shift_id: str = ""


@dataclass
class TopPerformer:
    employee_id: str = ""
    rank: int = 0
    score: float = 0.0


@dataclass
class TurnoverRisk:
    employee_id: str = ""
    risk_score: float = 0.0
    reason: str = ""


@dataclass
class WeeklyRiskMap:
    week: str = ""
    risks: list = field(default_factory=list)
