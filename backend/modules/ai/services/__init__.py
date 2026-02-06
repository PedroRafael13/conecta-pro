"""AI Services - Sprint 34.

Services para IA Preditiva.
"""

from modules.ai.services.anomaly_detector import AnomalyDetector
from modules.ai.services.churn_predictor import ChurnPredictor
from modules.ai.services.forecast_service import ForecastService
from modules.ai.services.prediction_service import PredictionService
from modules.ai.services.recommendation_engine import RecommendationEngine

__all__ = [
    "PredictionService",
    "ChurnPredictor",
    "ForecastService",
    "AnomalyDetector",
    "RecommendationEngine",
]
