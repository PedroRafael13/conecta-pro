"""
application/interfaces/unit_of_work.py - UNIT OF WORK INTERFACE
===============================================================
Clean Architecture unit of work pattern for transaction management
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from contextlib import asynccontextmanager

from .repository import (
    IProductRepository,
    IStockMovementRepository,
    IJournalEntryRepository,
    IEmployeeRepository,
    IProcurementRepository
)


class IUnitOfWork(ABC):
    """
    Interface para Unit of Work.

    Gerencia transacoes e acesso aos repositorios
    garantindo consistencia atomica.
    """

    # Repositories
    products: IProductRepository
    stock_movements: IStockMovementRepository
    journal_entries: IJournalEntryRepository
    employees: IEmployeeRepository
    procurements: IProcurementRepository

    @abstractmethod
    async def __aenter__(self) -> 'IUnitOfWork':
        """Inicia transacao."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza transacao."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Confirma transacao."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Reverte transacao."""
        pass

    @abstractmethod
    async def refresh(self, entity) -> None:
        """Atualiza entidade do banco."""
        pass
