"""Schemas do modulo de monitoramento."""

from .alert_schemas import (
    AlertAcknowledge,
    AlertCreate,
    AlertResolve,
    AlertResponse,
    AlertsListResponse,
)
from .dashboard_schemas import (
    DashboardResponse,
    MetricStatus,
    SystemHealthResponse,
)
from .threshold_schemas import (
    ThresholdCreate,
    ThresholdResponse,
    ThresholdUpdate,
)

__all__ = [
    # Alert
    "AlertCreate",
    "AlertResponse",
    "AlertAcknowledge",
    "AlertResolve",
    "AlertsListResponse",
    # Threshold
    "ThresholdCreate",
    "ThresholdResponse",
    "ThresholdUpdate",
    # Dashboard
    "DashboardResponse",
    "MetricStatus",
    "SystemHealthResponse",
]
