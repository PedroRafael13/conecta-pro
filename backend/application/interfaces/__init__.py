"""
application/interfaces/__init__.py - INTERFACES
===============================================
Clean Architecture ports (interfaces)
"""

from .repository import (
    IRepository,
    IProductRepository,
    IStockMovementRepository,
    IJournalEntryRepository,
    IEmployeeRepository,
    IProcurementRepository
)
from .unit_of_work import IUnitOfWork

__all__ = [
    "IRepository",
    "IProductRepository",
    "IStockMovementRepository",
    "IJournalEntryRepository",
    "IEmployeeRepository",
    "IProcurementRepository",
    "IUnitOfWork"
]
