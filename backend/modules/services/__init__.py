"""
Services Module - Gestão de Serviços
Sprint 31: Gestão de Serviços
"""

from modules.services.controllers import router
from modules.services.models import (
    ExecutionStatus,
    OrderPriority,
    OrderStatus,
    ReportType,
    ServiceCatalog,
    ServiceCategory,
    ServiceExecution,
    ServiceOrder,
    ServiceReport,
    ServiceStatus,
    ServiceType,
    SLAConfig,
    SLAMetricType,
)
from modules.services.services import ServiceAIService, ServiceManagementService

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
