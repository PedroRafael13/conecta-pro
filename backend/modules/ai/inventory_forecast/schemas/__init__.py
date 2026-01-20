"""Inventory Forecast Schemas."""

from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    ForecastCreate,
    ForecastUpdate,
    ForecastResponse,
    ForecastResultResponse,
    ForecastListResponse,
    ForecastSummary,
    DemandPatternResponse,
    DemandPatternCreate,
    ReorderSuggestion,
    ForecastRequest,
    BulkForecastRequest,
)

__all__ = [
    "ForecastCreate",
    "ForecastUpdate",
    "ForecastResponse",
    "ForecastResultResponse",
    "ForecastListResponse",
    "ForecastSummary",
    "DemandPatternResponse",
    "DemandPatternCreate",
    "ReorderSuggestion",
    "ForecastRequest",
    "BulkForecastRequest",
]
