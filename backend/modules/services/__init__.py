"""
Services Module - Gestão de Serviços
Sprint 31: Gestão de Serviços
"""

from modules.services.models import (
    ServiceCatalog, ServiceOrder, ServiceExecution,
    ServiceReport, SLAConfig,
    ServiceCategory, ServiceType, ServiceStatus,
    OrderStatus, OrderPriority, ExecutionStatus,
    ReportType, SLAMetricType
)
from modules.services.services import ServiceManagementService, ServiceAIService
from modules.services.controllers import router

__all__ = [
    # Models
    "ServiceCatalog",
    "ServiceOrder",
    "ServiceExecution",
    "ServiceReport",
    "SLAConfig",
    # Enums
    "ServiceCategory",
    "ServiceType",
    "ServiceStatus",
    "OrderStatus",
    "OrderPriority",
    "ExecutionStatus",
    "ReportType",
    "SLAMetricType",
    # Services
    "ServiceManagementService",
    "ServiceAIService",
    # Router
    "router",
]
