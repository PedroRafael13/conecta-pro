"""Inventory Forecast Schemas."""

from modules.ai.inventory_forecast.schemas.forecast_schemas import (
    BulkForecastRequest,
    DemandPatternCreate,
    DemandPatternResponse,
    ForecastCreate,
    ForecastListResponse,
    ForecastRequest,
    ForecastResponse,
    ForecastResultResponse,
    ForecastSummary,
    ForecastUpdate,
    ReorderSuggestion,
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
