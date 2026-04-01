"""
Services Module - Schemas
Sprint 31: Gestão de Serviços
"""

from modules.services.schemas.service_schemas import (
    # AI
    ServiceAnalysis,
    # ServiceCatalog
    ServiceCatalogBase,
    ServiceCatalogCreate,
    ServiceCatalogListResponse,
    ServiceCatalogResponse,
    ServiceCatalogStats,
    ServiceCatalogUpdate,
    # ServiceExecution
    ServiceExecutionBase,
    ServiceExecutionCreate,
    ServiceExecutionResponse,
    ServiceExecutionUpdate,
    # ServiceOrder
    ServiceOrderBase,
    ServiceOrderCreate,
    ServiceOrderFilter,
    ServiceOrderListResponse,
    ServiceOrderResponse,
    ServiceOrderStats,
    ServiceOrderUpdate,
    ServiceRecommendation,
    # ServiceReport
    ServiceReportBase,
    ServiceReportCreate,
    ServiceReportResponse,
    ServiceReportUpdate,
    SLAAnalysis,
    # SLAConfig
    SLAConfigBase,
    SLAConfigCreate,
    SLAConfigResponse,
    SLAConfigUpdate,
)

__all__ = [
    # ServiceCatalog
    "ServiceCatalogBase",
    "ServiceCatalogCreate",
    "ServiceCatalogUpdate",
    "ServiceCatalogResponse",
    "ServiceCatalogListResponse",
    "ServiceCatalogStats",
    # ServiceOrder
    "ServiceOrderBase",
    "ServiceOrderCreate",
    "ServiceOrderUpdate",
    "ServiceOrderResponse",
    "ServiceOrderListResponse",
    "ServiceOrderStats",
    "ServiceOrderFilter",
    # ServiceExecution
    "ServiceExecutionBase",
    "ServiceExecutionCreate",
    "ServiceExecutionUpdate",
    "ServiceExecutionResponse",
    # ServiceReport
    "ServiceReportBase",
    "ServiceReportCreate",
    "ServiceReportUpdate",
    "ServiceReportResponse",
    # SLAConfig
    "SLAConfigBase",
    "SLAConfigCreate",
    "SLAConfigUpdate",
    "SLAConfigResponse",
    # AI
    "ServiceAnalysis",
    "ServiceRecommendation",
    "SLAAnalysis",
]
