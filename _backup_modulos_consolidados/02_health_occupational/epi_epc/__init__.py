"""
Package: epi_epc
Description: Modulo de Gestao de EPI/EPC (NR-6)
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-6 (Portaria MTb 3.214/78)
"""

from .epi_management import (
    EPIManager,
    EPIModel,
    EPIInventoryItem,
    EPIDelivery,
    EPIRequirement,
    CACertificate,
    EPICategory,
    EPIStatus,
    DeliveryStatus,
    EPIManagementError,
    EPIConfig,
    EPIModelDBModel,
    EPIInventoryDBModel,
    EPIDeliveryDBModel,
    get_epi_manager,
    init_epi_manager,
)

__all__ = [
    "EPIManager",
    "EPIModel",
    "EPIInventoryItem",
    "EPIDelivery",
    "EPIRequirement",
    "CACertificate",
    "EPICategory",
    "EPIStatus",
    "DeliveryStatus",
    "EPIManagementError",
    "EPIConfig",
    "EPIModelDBModel",
    "EPIInventoryDBModel",
    "EPIDeliveryDBModel",
    "get_epi_manager",
    "init_epi_manager",
]

__version__ = "1.0.0"
