"""
Module: ai
Description: Modulo de IA Operacional
Author: Conecta PRO Team
Date: 2026-03-09

Este modulo fornece:
- Agentes operacionais inteligentes
- Otimizador de escalas
- Otimizador de substituicoes
- Analisador de ocorrencias
- Analisador preditivo
- Detector de anomalias
- Monitor de campo
- Otimizador de rotas
- Automacao de comunicacao
- Classificador de incidentes
- Otimizador de rondas
- Previsor de custos
- Bartolo 3.0
- Skills operacionais
- Orquestrador de IA
"""

from .agents import (
    AbsencePrediction,
    ActionSuggestion,
    AdaptiveFrequency,
    AnomalyDetected,
    AnomalyDetectorAgent,
    AnomalyPattern,
    AutomaticFeedback,
    Bartolo3Agent,
    BartoloChatMessage,
    BartoloChatResponse,
    BehaviorPattern,
    BudgetAlert,
    ChatbotResponse,
    Checkpoint,
    CheckpointSuggestion,
    CommsAutomatorAgent,
    ContingencyPlan,
    CostPredictorAgent,
    CoveragePredictorAgent,
    CoverageRisk,
    EmployeeAbsenceRisk,
    EmployeeAvailability,
    EmployeePreference,
    FieldEvent,
    FieldMonitorAgent,
    GamificationData,
    IncidentClassification,
    IncidentClassifierAgent,
    MessageTemplate,
    OccurrenceAnalysis,
    # Occurrence Analyzer
    OccurrenceAnalyzer,
    OccurrenceClassification,
    OperationStatus,
    OptimizationConstraints,
    OptimizationResult,
    OptimizedRoute,
    OvertimeForecast,
    PatrolEfficiencyReport,
    PatrolOptimizerAgent,
    PatrolPlan,
    PatternDetected,
    PerformanceAlert,
    PerformanceAnalyzerAgent,
    PerformanceDimension,
    PerformanceScore,
    PostCostForecast,
    PostStatus,
    # Predictive Analyzer
    PredictiveAnalyzer,
    ProactiveInsight,
    RouteOptimizerAgent,
    ScaleFinancialImpact,
    # Scale Optimizer
    ScaleOptimizer,
    SendResult,
    ShiftSlot,
    SimilarOccurrence,
    SubstituteSuggestion,
    # Substitution Optimizer
    SubstitutionOptimizer,
    SubstitutionRequest,
    TopPerformer,
    TurnoverRisk,
    WeeklyRiskMap,
)
from .controller import ai_router

__all__ = [
    # AI Router
    "ai_router",
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

__version__ = "2.0.0"
