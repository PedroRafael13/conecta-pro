"""
Services Module - Gestão de Serviços

DEPRECATED: Use 'modules.comercial' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.services' is deprecated. "
    "Use 'modules.comercial' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.services.controllers import router  # noqa: E402
from modules.services.models import (  # noqa: E402
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
from modules.services.services import ServiceAIService, ServiceManagementService  # noqa: E402

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
