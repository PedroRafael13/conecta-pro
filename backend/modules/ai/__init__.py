"""AI Predictions Module - Sprint 34.

Modulo de IA Preditiva Avancada para o Conecta PRO.

Funcionalidades:
- Previsao de churn de clientes
- Forecast de receitas/despesas
- Deteccao de anomalias
- Motor de recomendacoes
- Feature store para ML
- Gerenciamento de modelos
"""

from modules.ai.models import (
    AnomalyLog,
    AnomalyType,
    Feature,
    FeatureDataType,
    FeatureStatus,
    FeatureStore,
    MLModel,
    ModelStatus,
    ModelType,
    Prediction,
    PredictionLog,
    PredictionStatus,
    PredictionType,
    Recommendation,
    RecommendationStatus,
    RecommendationType,
    TrainingJob,
    TrainingStatus,
)
from modules.ai.services import (
    AnomalyDetector,
    ChurnPredictor,
    ForecastService,
    PredictionService,
    RecommendationEngine,
)

__all__ = [
    # Models
    "Prediction",
    "PredictionType",
    "PredictionStatus",
    "MLModel",
    "ModelType",
    "ModelStatus",
    "FeatureStore",
    "Feature",
    "FeatureStatus",
    "FeatureDataType",
    "TrainingJob",
    "TrainingStatus",
    "PredictionLog",
    "AnomalyLog",
    "AnomalyType",
    "Recommendation",
    "RecommendationType",
    "RecommendationStatus",
    # Services
    "PredictionService",
    "ChurnPredictor",
    "ForecastService",
    "AnomalyDetector",
    "RecommendationEngine",
]
