"""Repositories do módulo Analytics Dashboard."""

from .dashboard_repository import DashboardRepository
from .kpi_repository import KPIRepository
from .cache_repository import CacheRepository
from .report_repository import ReportRepository

__all__ = [
    "DashboardRepository",
    "KPIRepository",
    "CacheRepository",
    "ReportRepository",
]
