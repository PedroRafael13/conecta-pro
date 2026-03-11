"""AI Predictions Module.

DEPRECATED: Use 'modules.inteligencia' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.ai' is deprecated. "
    "Use 'modules.inteligencia' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.ai.models import (  # noqa: E402
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
from modules.ai.services import (  # noqa: E402
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
