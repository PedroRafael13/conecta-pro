"""
application/use_cases/inventory/__init__.py - INVENTORY USE CASES
================================================================
"""

from .create_product import CreateProductUseCase, CreateProductResult
from .receive_stock import ReceiveStockUseCase, ReceiveStockResult

__all__ = [
    "CreateProductUseCase",
    "CreateProductResult",
    "ReceiveStockUseCase",
    "ReceiveStockResult"
]
