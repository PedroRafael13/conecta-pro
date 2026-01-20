"""Schemas do modulo de monitoramento."""

from .alert_schemas import (
    AlertAcknowledge,
    AlertCreate,
    AlertResponse,
    AlertResolve,
    AlertsListResponse,
)
from .threshold_schemas import (
    ThresholdCreate,
    ThresholdResponse,
    ThresholdUpdate,
)
from .dashboard_schemas import (
    DashboardResponse,
    MetricStatus,
    SystemHealthResponse,
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
