"""
Schemas para dashboard de monitoramento.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MetricStatus(BaseModel):
    """Status de uma metrica individual."""

    name: str
    display_name: str
    category: str
    current_value: float
    unit: str
    level: str  # green, yellow, orange, red
    threshold_yellow: float
    threshold_orange: float
    threshold_red: float
    trend: str = "stable"  # up, down, stable
    last_updated: datetime


class CategoryHealth(BaseModel):
    """Saude de uma categoria de metricas."""

    name: str
    display_name: str
    overall_level: str  # Nivel mais critico da categoria
    metrics_count: int
    green_count: int
    yellow_count: int
    orange_count: int
    red_count: int


class SystemHealthResponse(BaseModel):
    """Resposta de saude geral do sistema."""

    overall_level: str  # green, yellow, orange, red
    overall_score: float = Field(..., ge=0, le=100)
    timestamp: datetime
    uptime_seconds: float
    categories: list[CategoryHealth]
    active_alerts: int
    critical_alerts: int


class DashboardResponse(BaseModel):
    """Resposta completa do dashboard de monitoramento."""

    health: SystemHealthResponse
    metrics: list[MetricStatus]
    recent_alerts: list[dict[str, Any]]
    statistics: dict[str, Any]


class MetricHistory(BaseModel):
    """Historico de valores de uma metrica."""

    metric_name: str
    period: str  # 1h, 6h, 24h, 7d
    data_points: list[dict[str, Any]]  # [{timestamp, value, level}]
    min_value: float
    max_value: float
    avg_value: float
    breach_count: int


class PerformanceOverview(BaseModel):
    """Visao geral de performance."""

    # HTTP
    requests_per_minute: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_rate_percent: float

    # Database
    db_connections_active: int
    db_connections_max: int
    db_query_avg_ms: float
    db_query_p95_ms: float

    # Cache
    cache_hit_rate_percent: float
    cache_memory_used_mb: float
    cache_memory_max_mb: float

    # System
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float


class AlertTrend(BaseModel):
    """Tendencia de alertas."""

    period: str  # 24h, 7d, 30d
    total_alerts: int
    alerts_by_level: dict[str, int]
    alerts_by_hour: list[dict[str, Any]]
    top_metrics: list[dict[str, Any]]
    mttr_trend: list[dict[str, Any]]  # Mean Time To Resolve
