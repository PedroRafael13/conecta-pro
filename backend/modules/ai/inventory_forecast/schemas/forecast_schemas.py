"""
Forecast Schemas - AI Inventory Forecasting

DTOs para entrada e saida da API de previsao de estoque.
"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.ai.inventory_forecast.models.demand_pattern import (
    PatternType,
    SeasonalityType,
    TrendDirection,
)
from modules.ai.inventory_forecast.models.forecast import (
    ForecastStatus,
    ForecastType,
)

# ============================================================
# Forecast Schemas
# ============================================================


class ForecastRequest(BaseModel):
    """Request para gerar previsao de demanda."""

    product_id: UUID = Field(..., description="ID do produto")
    horizon_days: int = Field(default=30, ge=7, le=365, description="Dias de previsao (7-365)")
    historical_days: int = Field(default=365, ge=30, le=1095, description="Dias de historico a usar (30-1095)")
    forecast_type: ForecastType = Field(default=ForecastType.DEMAND, description="Tipo de previsao")
    model_type: str = Field(default="auto", description="Modelo ML: auto, prophet, arima, exp_smoothing")
    confidence_level: float = Field(default=0.95, ge=0.80, le=0.99, description="Nivel de confianca (0.80-0.99)")

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

    product_ids: list[UUID] = Field(..., min_length=1, max_length=100, description="Lista de IDs de produtos (max 100)")
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
    notes: str | None = None


class ForecastUpdate(BaseModel):
    """Schema para atualizar previsao."""

    status: ForecastStatus | None = None
    mae: float | None = None
    mape: float | None = None
    rmse: float | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=100)
    total_predicted_demand: float | None = None
    avg_daily_demand: float | None = None
    peak_demand: float | None = None
    peak_demand_date: date | None = None
    min_demand: float | None = None
    min_demand_date: date | None = None
    suggested_reorder_point: float | None = None
    suggested_reorder_quantity: float | None = None
    suggested_safety_stock: float | None = None
    notes: str | None = None
    error_message: str | None = None


class ForecastResultResponse(BaseModel):
    """Response para resultado de previsao."""

    id: UUID
    forecast_id: UUID
    date: date
    period_type: str
    predicted_demand: float
    lower_bound: float | None = None
    upper_bound: float | None = None
    confidence_level: float = 0.95
    actual_demand: float | None = None
    variance: float | None = None
    variance_pct: float | None = None
    trend_component: float | None = None
    seasonal_component: float | None = None
    is_anomaly: bool = False
    anomaly_type: str | None = None

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
    mae: float | None = None
    mape: float | None = None
    rmse: float | None = None
    confidence_score: float | None = None

    # Resultados
    total_predicted_demand: float
    avg_daily_demand: float
    peak_demand: float
    peak_demand_date: date | None = None
    min_demand: float
    min_demand_date: date | None = None

    # Recomendacoes
    suggested_reorder_point: float | None = None
    suggested_reorder_quantity: float | None = None
    suggested_safety_stock: float | None = None

    # Metadados
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    is_active: bool
    is_automated: bool
    notes: str | None = None
    error_message: str | None = None

    # Resultados detalhados (opcional)
    results: list[ForecastResultResponse] | None = None

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
    days_until_reorder: int | None = None
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
    seasonal_periods: list[int] | None = None
    peak_periods: list[dict] | None = None

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
    weekday_distribution: dict[str, float] | None = None
    monthly_distribution: dict[str, float] | None = None

    # Recomendacoes
    recommended_model: str | None = None
    recommended_safety_stock_days: int | None = None
    recommended_review_period_days: int | None = None

    # Metadados
    created_at: datetime
    updated_at: datetime | None = None
    is_active: bool
    insights: list[dict] | None = None

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
    estimated_stockout_date: date | None = None
    confidence_score: float
    notes: str | None = None


class ReorderListResponse(BaseModel):
    """Lista de sugestoes de reposicao."""

    items: list[ReorderSuggestion]
    total: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
