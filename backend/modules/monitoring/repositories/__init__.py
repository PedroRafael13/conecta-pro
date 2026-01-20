"""Repositories do modulo de monitoramento."""

from .alert_repository import AlertRepository
from .threshold_repository import ThresholdRepository

__all__ = [
    "AlertRepository",
    "ThresholdRepository",
]
