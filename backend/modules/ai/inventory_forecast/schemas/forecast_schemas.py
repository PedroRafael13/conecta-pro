"""
Forecast Schemas - AI Inventory Forecasting

DTOs para entrada e saida da API de previsao de estoque.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.ai.inventory_forecast.models.forecast import (
    ForecastStatus,
    ForecastType,
)
from modules.ai.inventory_forecast.models.demand_pattern import (
    PatternType,
    SeasonalityType,
    TrendDirection,
)


# ============================================================
# Forecast Schemas
# ============================================================


class ForecastRequest(BaseModel):
    """Request para gerar previsao de demanda."""

    product_id: UUID = Field(..., description="ID do produto")
    horizon_days: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Dias de previsao (7-365)"
    )
    historical_days: int = Field(
        default=365,
        ge=30,
        le=1095,
        description="Dias de historico a usar (30-1095)"
    )
    forecast_type: ForecastType = Field(
        default=ForecastType.DEMAND,
        description="Tipo de previsao"
    )
    model_type: str = Field(
        default="auto",
        description="Modelo ML: auto, prophet, arima, exp_smoothing"
    )
    confidence_level: float = Field(
        default=0.95,
        ge=0.80,
        le=0.99,
        description="Nivel de confianca (0.80-0.99)"
    )

    @field_validator("model_type")
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        """Valida tipo de modelo."""
        valid = {"auto", "prophet", "arima", "exp_smoothing", "ensemble"}
        if v.lower() not in valid:
            raise ValueError(f"Modelo invalido. Validos: {valid}")
        return v.lower()


class BulkForecastRequest(BaseModel):
    """Request para previsao em lote."""

    product_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Lista de IDs de produtos (max 100)"
    )
    horizon_days: int = Field(default=30, ge=7, le=365)
    historical_days: int = Field(default=365, ge=30, le=1095)
    forecast_type: ForecastType = Field(default=ForecastType.DEMAND)


class ForecastCreate(BaseModel):
    """Schema para criar previsao."""

    product_id: UUID
    product_code: str = Field(..., max_length=50)
    product_name: str = Field(..., max_length=200)
    forecast_type: ForecastType = ForecastType.DEMAND
    start_date: date
    end_date: date
    horizon_days: int = Field(default=30, ge=7, le=365)
    historical_days: int = Field(default=365, ge=30, le=1095)
    model_type: str = Field(default="prophet", max_length=50)
    model_params: dict[str, Any] = Field(default_factory=dict)
    is_automated: bool = False
    notes: Optional[str] = None


class ForecastUpdate(BaseModel):
    """Schema para atualizar previsao."""

    status: Optional[ForecastStatus] = None
    mae: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    confidence_score: Optional[float] = Field(default=None, ge=0, le=100)
    total_predicted_demand: Optional[float] = None
    avg_daily_demand: Optional[float] = None
    peak_demand: Optional[float] = None
    peak_demand_date: Optional[date] = None
    min_demand: Optional[float] = None
    min_demand_date: Optional[date] = None
    suggested_reorder_point: Optional[float] = None
    suggested_reorder_quantity: Optional[float] = None
    suggested_safety_stock: Optional[float] = None
    notes: Optional[str] = None
    error_message: Optional[str] = None


class ForecastResultResponse(BaseModel):
    """Response para resultado de previsao."""

    id: UUID
    forecast_id: UUID
    date: date
    period_type: str
    predicted_demand: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence_level: float = 0.95
    actual_demand: Optional[float] = None
    variance: Optional[float] = None
    variance_pct: Optional[float] = None
    trend_component: Optional[float] = None
    seasonal_component: Optional[float] = None
    is_anomaly: bool = False
    anomaly_type: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class ForecastResponse(BaseModel):
    """Response para previsao completa."""

    id: UUID
    product_id: UUID
    product_code: str
    product_name: str
    forecast_type: ForecastType
    status: ForecastStatus
    start_date: date
    end_date: date
    horizon_days: int
    historical_days: int
    data_points: int
    model_type: str
    model_params: dict[str, Any]

    # Metricas
    mae: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    confidence_score: Optional[float] = None

    # Resultados
    total_predicted_demand: float
    avg_daily_demand: float
    peak_demand: float
    peak_demand_date: Optional[date] = None
    min_demand: float
    min_demand_date: Optional[date] = None

    # Recomendacoes
    suggested_reorder_point: Optional[float] = None
    suggested_reorder_quantity: Optional[float] = None
    suggested_safety_stock: Optional[float] = None

    # Metadados
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_active: bool
    is_automated: bool
    notes: Optional[str] = None
    error_message: Optional[str] = None

    # Resultados detalhados (opcional)
    results: Optional[list[ForecastResultResponse]] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class ForecastListResponse(BaseModel):
    """Response para lista de previsoes."""

    items: list[ForecastResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ForecastSummary(BaseModel):
    """Resumo de previsao para dashboard."""

    product_id: UUID
    product_code: str
    product_name: str
    avg_daily_demand: float
    trend_direction: str
    confidence_score: float
    days_until_reorder: Optional[int] = None
    suggested_action: str  # "OK", "REORDER_SOON", "REORDER_NOW", "REVIEW"


# ============================================================
# Demand Pattern Schemas
# ============================================================


class DemandPatternCreate(BaseModel):
    """Schema para criar analise de padrao."""

    product_id: UUID
    product_code: str = Field(..., max_length=50)
    product_name: str = Field(..., max_length=200)
    analysis_start_date: date
    analysis_end_date: date


class DemandPatternResponse(BaseModel):
    """Response para padrao de demanda."""

    id: UUID
    product_id: UUID
    product_code: str
    product_name: str
    analysis_start_date: date
    analysis_end_date: date
    total_data_points: int

    # Classificacao
    pattern_type: PatternType
    pattern_confidence: float
    seasonality_type: SeasonalityType
    seasonality_strength: float
    seasonal_periods: Optional[list[int]] = None
    peak_periods: Optional[list[dict]] = None

    # Tendencia
    trend_direction: TrendDirection
    trend_slope: float
    trend_strength: float

    # Estatisticas
    avg_demand: float
    std_demand: float
    cv_demand: float
    median_demand: float
    min_demand: float
    max_demand: float

    # Analises
    volatility_index: float
    predictability_score: float
    anomalies_detected: int

    # Distribuicoes
    weekday_distribution: Optional[dict[str, float]] = None
    monthly_distribution: Optional[dict[str, float]] = None

    # Recomendacoes
    recommended_model: Optional[str] = None
    recommended_safety_stock_days: Optional[int] = None
    recommended_review_period_days: Optional[int] = None

    # Metadados
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    insights: Optional[list[dict]] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


# ============================================================
# Reorder Schemas
# ============================================================


class ReorderSuggestion(BaseModel):
    """Sugestao de reposicao de estoque."""

    product_id: UUID
    product_code: str
    product_name: str
    current_stock: float
    reorder_point: float
    safety_stock: float
    suggested_quantity: float
    avg_daily_demand: float
    days_of_stock_remaining: int
    lead_time_days: int
    urgency: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    estimated_stockout_date: Optional[date] = None
    confidence_score: float
    notes: Optional[str] = None


class ReorderListResponse(BaseModel):
    """Lista de sugestoes de reposicao."""

    items: list[ReorderSuggestion]
    total: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
