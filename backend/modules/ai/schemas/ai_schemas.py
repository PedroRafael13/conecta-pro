"""AI Schemas - Pydantic Schemas para IA.

Sprint 34 - AI Predictions.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from modules.ai.models.anomaly_log import AnomalySeverity, AnomalyType
from modules.ai.models.ml_model import ModelStatus, ModelType
from modules.ai.models.prediction import PredictionStatus, PredictionType
from modules.ai.models.recommendation import RecommendationStatus, RecommendationType

# ============ Prediction Schemas ============


class PredictionCreate(BaseModel):
    """Schema para criar previsao."""

    prediction_type: PredictionType = Field(..., description="Tipo de previsao")
    entity_type: str = Field(..., description="Tipo da entidade")
    entity_id: UUID = Field(..., description="ID da entidade")
    model_id: Optional[UUID] = Field(None, description="ID do modelo a usar")
    features: Optional[dict] = Field(None, description="Features de entrada")
    valid_days: int = Field(30, ge=1, le=365, description="Dias de validade")
    tags: Optional[list[str]] = Field(None, description="Tags")


class PredictionResponse(BaseModel):
    """Schema de resposta de previsao."""

    id: UUID
    tenant_id: UUID
    prediction_type: PredictionType
    status: PredictionStatus
    entity_type: str
    entity_id: UUID
    model_id: Optional[UUID] = None
    prediction_value: Optional[float] = None
    prediction_label: Optional[str] = None
    prediction_probabilities: Optional[dict] = None
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    feature_importance: Optional[dict] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        """Config."""

        from_attributes = True


class PredictionListResponse(BaseModel):
    """Schema de lista de previsoes."""

    items: list[PredictionResponse]
    total: int
    page: int = 1
    page_size: int = 20


class PredictionFeedback(BaseModel):
    """Schema para feedback de previsao."""

    actual_value: Optional[float] = Field(None, description="Valor real")
    actual_label: Optional[str] = Field(None, description="Label real")
    notes: Optional[str] = Field(None, description="Notas")


# ============ ML Model Schemas ============


class MLModelCreate(BaseModel):
    """Schema para criar modelo."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    model_type: ModelType
    algorithm: str = Field(..., min_length=1, max_length=100)
    framework: Optional[str] = None
    hyperparameters: Optional[dict] = None
    input_features: Optional[list[str]] = None
    target_variable: Optional[str] = None
    prediction_threshold: float = Field(0.5, ge=0, le=1)
    confidence_threshold: float = Field(0.7, ge=0, le=1)
    tags: Optional[list[str]] = None


class MLModelUpdate(BaseModel):
    """Schema para atualizar modelo."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    hyperparameters: Optional[dict] = None
    prediction_threshold: Optional[float] = Field(None, ge=0, le=1)
    confidence_threshold: Optional[float] = Field(None, ge=0, le=1)
    auto_retrain: Optional[bool] = None
    tags: Optional[list[str]] = None


class MLModelResponse(BaseModel):
    """Schema de resposta de modelo."""

    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    version: str
    model_type: ModelType
    status: ModelStatus
    algorithm: str
    framework: Optional[str] = None
    hyperparameters: Optional[dict] = None
    input_features: Optional[list[str]] = None
    target_variable: Optional[str] = None
    training_metrics: Optional[dict] = None
    validation_metrics: Optional[dict] = None
    total_predictions: int = 0
    successful_predictions: int = 0
    avg_prediction_time_ms: Optional[int] = None
    is_default: bool = False
    active: bool = True
    created_at: datetime
    trained_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None

    class Config:
        """Config."""

        from_attributes = True


# ============ Feature Store Schemas ============


class FeatureStoreCreate(BaseModel):
    """Schema para criar feature store."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    entity_type: str = Field(..., min_length=1, max_length=100)
    data_source: Optional[str] = None
    refresh_frequency: Optional[str] = None
    tags: Optional[list[str]] = None


class FeatureStoreResponse(BaseModel):
    """Schema de resposta de feature store."""

    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    entity_type: str
    status: str
    total_features: int = 0
    total_entities: int = 0
    data_quality_score: Optional[float] = None
    last_refresh_at: Optional[datetime] = None
    active: bool = True
    created_at: datetime

    class Config:
        """Config."""

        from_attributes = True


class FeatureCreate(BaseModel):
    """Schema para criar feature."""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    data_type: str
    source_column: Optional[str] = None
    transformation: Optional[str] = None
    validation_rules: Optional[dict] = None
    category: Optional[str] = None


class FeatureResponse(BaseModel):
    """Schema de resposta de feature."""

    id: UUID
    feature_store_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    data_type: str
    status: str
    importance_score: Optional[float] = None
    statistics: Optional[dict] = None
    active: bool = True
    created_at: datetime

    class Config:
        """Config."""

        from_attributes = True


# ============ Training Job Schemas ============


class TrainingJobCreate(BaseModel):
    """Schema para criar job de treinamento."""

    model_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    config: Optional[dict] = None
    hyperparameters: Optional[dict] = None
    feature_store_id: Optional[UUID] = None
    validation_split: float = Field(0.2, ge=0, le=0.5)
    test_split: float = Field(0.1, ge=0, le=0.3)
    cv_folds: Optional[int] = Field(None, ge=2, le=10)
    timeout_seconds: int = Field(3600, ge=60, le=86400)


class TrainingJobResponse(BaseModel):
    """Schema de resposta de job."""

    id: UUID
    tenant_id: UUID
    model_id: UUID
    name: str
    description: Optional[str] = None
    status: str
    progress_percent: float = 0
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    final_metrics: Optional[dict] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        """Config."""

        from_attributes = True


# ============ Churn Prediction Schemas ============


class ChurnPredictionRequest(BaseModel):
    """Schema para requisitar previsao de churn."""

    client_id: UUID = Field(..., description="ID do cliente")
    days_since_last_interaction: Optional[int] = Field(None, ge=0)
    interaction_frequency: Optional[float] = Field(None, ge=0)
    support_tickets_count: Optional[int] = Field(None, ge=0)
    payment_delays_count: Optional[int] = Field(None, ge=0)
    nps_score: Optional[float] = Field(None, ge=0, le=10)
    csat_score: Optional[float] = Field(None, ge=1, le=5)
    contract_value: Optional[float] = Field(None, ge=0)
    contract_age_months: Optional[int] = Field(None, ge=0)
    days_until_renewal: Optional[int] = Field(None, ge=0)
    feature_usage_rate: Optional[float] = Field(None, ge=0, le=1)


class ChurnPredictionResponse(BaseModel):
    """Schema de resposta de previsao de churn."""

    client_id: UUID
    churn_probability: float = Field(..., ge=0, le=1)
    churn_risk_level: str  # low, medium, high, critical
    confidence: float = Field(..., ge=0, le=1)
    main_factors: list[dict]
    recommendations: list[dict]
    expected_churn_date: Optional[datetime] = None
    lifetime_value_at_risk: float = 0
    prediction_id: Optional[UUID] = None


# ============ Forecast Schemas ============


class ForecastRequest(BaseModel):
    """Schema para requisitar forecast."""

    entity_type: str = Field(..., description="Tipo da entidade")
    entity_id: Optional[UUID] = Field(None, description="ID especifico")
    forecast_type: str = Field(..., description="Tipo: revenue, expense, demand")
    periods: int = Field(6, ge=1, le=24, description="Numero de periodos")
    period_type: str = Field("month", description="day, week, month, quarter")
    confidence_level: float = Field(0.95, ge=0.8, le=0.99)


class ForecastResponse(BaseModel):
    """Schema de resposta de forecast."""

    period_start: datetime
    period_end: datetime
    total_value: float
    avg_value: float
    min_value: float
    max_value: float
    trend: str  # up, down, stable
    confidence: float
    scenarios: dict  # pessimist, base, optimist
    forecasts: list[dict]
    prediction_id: Optional[UUID] = None


# ============ Anomaly Schemas ============


class AnomalyCreate(BaseModel):
    """Schema para criar deteccao de anomalia."""

    entity_type: str = Field(..., description="Tipo da entidade")
    entity_id: UUID = Field(..., description="ID da entidade")
    field: str = Field(..., description="Campo a verificar")
    value: float = Field(..., description="Valor observado")
    historical_values: Optional[list[float]] = Field(None, description="Valores historicos")
    context: Optional[dict] = Field(None, description="Contexto adicional")


class AnomalyResponse(BaseModel):
    """Schema de resposta de anomalia."""

    is_anomaly: bool
    anomaly_type: Optional[AnomalyType] = None
    severity: AnomalySeverity
    anomaly_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    observed_value: float
    expected_value: float
    expected_range: tuple[float, float]
    deviation_score: float
    explanation: str
    contributing_factors: list[dict]
    anomaly_id: Optional[UUID] = None


# ============ Recommendation Schemas ============


class RecommendationRequest(BaseModel):
    """Schema para requisitar recomendacoes."""

    target_entity_type: str = Field(..., description="Tipo da entidade alvo")
    target_entity_id: UUID = Field(..., description="ID da entidade alvo")
    recommendation_type: RecommendationType
    limit: int = Field(5, ge=1, le=20)
    context: Optional[dict] = Field(None, description="Contexto adicional")
    algorithm: str = Field("hybrid", description="Algoritmo a usar")


class RecommendationResponse(BaseModel):
    """Schema de resposta de recomendacao."""

    id: UUID
    recommendation_type: RecommendationType
    status: RecommendationStatus
    target_entity_type: str
    target_entity_id: UUID
    recommended_entity_type: Optional[str] = None
    recommended_entity_id: Optional[UUID] = None
    recommended_entity_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    reason: Optional[str] = None
    relevance_score: Optional[float] = None
    confidence_score: Optional[float] = None
    expected_value: Optional[float] = None
    rank_position: Optional[int] = None
    valid_until: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Config."""

        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema de lista de recomendacoes."""

    recommendations: list[RecommendationResponse]
    algorithm: str
    total_candidates: int
    processing_time_ms: int


# ============ Stats Schemas ============


class PredictionStatsResponse(BaseModel):
    """Schema de estatisticas de previsoes."""

    period_days: int
    total_predictions: int
    completed: int
    failed: int
    success_rate: float
    with_feedback: int
    feedback_rate: float
    accuracy: float
    avg_percentage_error: Optional[float] = None
    avg_processing_time_ms: Optional[float] = None
    by_type: dict


class ModelStatsResponse(BaseModel):
    """Schema de estatisticas de modelo."""

    model_id: UUID
    model_name: str
    total_predictions: int
    success_rate: float
    avg_prediction_time_ms: Optional[int] = None
    drift_score: Optional[float] = None
    drift_detected: bool = False
    needs_retraining: bool = False
