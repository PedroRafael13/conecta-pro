"""
application/dto/__init__.py - DATA TRANSFER OBJECTS
==================================================
"""

from .inventory import (
    CreateProductDTO,
    UpdateProductDTO,
    ProductResponseDTO,
    ProductListDTO,
    MovementLineDTO,
    CreateStockMovementDTO,
    StockMovementResponseDTO,
    StockPositionDTO,
    StockValuationDTO,
    StockMovementSummaryDTO
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
    "StockMovementSummaryDTO"
]
