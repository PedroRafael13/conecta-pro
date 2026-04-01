"""
application/dto/__init__.py - DATA TRANSFER OBJECTS
==================================================
"""

from .inventory import (
    CreateProductDTO,
    CreateStockMovementDTO,
    MovementLineDTO,
    ProductListDTO,
    ProductResponseDTO,
    StockMovementResponseDTO,
    StockMovementSummaryDTO,
    StockPositionDTO,
    StockValuationDTO,
    UpdateProductDTO,
)

__all__ = [
    # Product DTOs
    "CreateProductDTO",
    "UpdateProductDTO",
    "ProductResponseDTO",
    "ProductListDTO",
    # Movement DTOs
    "MovementLineDTO",
    "CreateStockMovementDTO",
    "StockMovementResponseDTO",
    # Report DTOs
    "StockPositionDTO",
    "StockValuationDTO",
    "StockMovementSummaryDTO",
]
