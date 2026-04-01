"""
Agentes de IA para Operacoes.

Author: Conecta PRO Team
Date: 2026-03-09
"""

from .anomaly_detector import AnomalyDetected, AnomalyDetectorAgent, BehaviorPattern
from .bartolo_v3 import Bartolo3Agent, BartoloChatMessage, BartoloChatResponse, ProactiveInsight
from .comms_automator import ChatbotResponse, CommsAutomatorAgent, MessageTemplate, SendResult
from .cost_predictor import BudgetAlert, CostPredictorAgent, PostCostForecast, ScaleFinancialImpact
from .coverage_predictor import (
    ContingencyPlan,
    CoveragePredictorAgent,
    CoverageRisk,
    EmployeeAbsenceRisk,
    WeeklyRiskMap,
)
from .field_monitor import FieldEvent, FieldMonitorAgent, OperationStatus, PostStatus
from .incident_classifier import IncidentClassification, IncidentClassifierAgent, PatternDetected
from .occurrence_analyzer import (
    ActionSuggestion,
    OccurrenceAnalysis,
    OccurrenceAnalyzer,
    OccurrenceClassification,
    SimilarOccurrence,
)
from .patrol_optimizer import AdaptiveFrequency, GamificationData, PatrolOptimizerAgent, PatrolPlan
from .performance_analyzer import (
    AutomaticFeedback,
    PerformanceAlert,
    PerformanceAnalyzerAgent,
    PerformanceDimension,
    PerformanceScore,
    TopPerformer,
)
from .predictive_analyzer import (
    AbsencePrediction,
    AnomalyPattern,
    OvertimeForecast,
    PredictiveAnalyzer,
    TurnoverRisk,
)
from .route_optimizer import (
    Checkpoint,
    CheckpointSuggestion,
    OptimizedRoute,
    PatrolEfficiencyReport,
    RouteOptimizerAgent,
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
    # Coverage Predictor
    "CoveragePredictorAgent",
    "CoverageRisk",
    "EmployeeAbsenceRisk",
    "WeeklyRiskMap",
    "ContingencyPlan",
    # Performance Analyzer
    "PerformanceAnalyzerAgent",
    "PerformanceScore",
    "PerformanceDimension",
    "TopPerformer",
    "PerformanceAlert",
    "AutomaticFeedback",
    # Anomaly Detector
    "AnomalyDetectorAgent",
    "AnomalyDetected",
    "BehaviorPattern",
    # Field Monitor
    "FieldMonitorAgent",
    "FieldEvent",
    "OperationStatus",
    "PostStatus",
    # Route Optimizer
    "RouteOptimizerAgent",
    "Checkpoint",
    "OptimizedRoute",
    "PatrolEfficiencyReport",
    "CheckpointSuggestion",
    # Comms Automator
    "CommsAutomatorAgent",
    "MessageTemplate",
    "SendResult",
    "ChatbotResponse",
    # Incident Classifier
    "IncidentClassifierAgent",
    "IncidentClassification",
    "PatternDetected",
    # Patrol Optimizer
    "PatrolOptimizerAgent",
    "PatrolPlan",
    "AdaptiveFrequency",
    "GamificationData",
    # Cost Predictor
    "CostPredictorAgent",
    "PostCostForecast",
    "ScaleFinancialImpact",
    "BudgetAlert",
    # Bartolo 3.0
    "Bartolo3Agent",
    "BartoloChatMessage",
    "BartoloChatResponse",
    "ProactiveInsight",
]
