"""
application/use_cases/inventory/__init__.py - INVENTORY USE CASES
================================================================
"""

from .create_product import CreateProductResult, CreateProductUseCase
from .receive_stock import ReceiveStockResult, ReceiveStockUseCase

__all__ = ["CreateProductUseCase", "CreateProductResult", "ReceiveStockUseCase", "ReceiveStockResult"]
