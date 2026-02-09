"""
application/interfaces/repository.py - REPOSITORY INTERFACES
============================================================
Clean Architecture repository ports (interfaces)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel

# Generic type for entities
T = TypeVar("T", bound=BaseModel)


class IRepository[T: BaseModel](ABC):
    """
    Interface base para repositorios.

    Define contrato padrao para operacoes CRUD
    seguindo Clean Architecture.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Busca entidade por ID."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[T]:
        """Lista entidades com paginacao e filtros."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Cria nova entidade."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Atualiza entidade existente."""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Remove entidade por ID."""
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """Verifica se entidade existe."""
        pass

    @abstractmethod
    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Conta entidades com filtros opcionais."""
        pass


class IProductRepository(IRepository):
    """Interface para repositorio de produtos."""

    @abstractmethod
    async def get_by_sku(self, sku: str, tenant_id: UUID) -> Any | None:
        """Busca produto por SKU."""
        pass

    @abstractmethod
    async def get_by_barcode(self, barcode: str, tenant_id: UUID) -> Any | None:
        """Busca produto por codigo de barras."""
        pass

    @abstractmethod
    async def get_low_stock(self, tenant_id: UUID) -> list[Any]:
        """Lista produtos com estoque baixo."""
        pass

    @abstractmethod
    async def get_by_category(self, category_id: UUID, tenant_id: UUID, skip: int = 0, limit: int = 100) -> list[Any]:
        """Lista produtos por categoria."""
        pass

    @abstractmethod
    async def search(self, query: str, tenant_id: UUID, skip: int = 0, limit: int = 100) -> list[Any]:
        """Busca produtos por termo."""
        pass


class IStockMovementRepository(IRepository):
    """Interface para repositorio de movimentacoes."""

    @abstractmethod
    async def get_by_product(
        self, product_id: UUID, tenant_id: UUID, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> list[Any]:
        """Lista movimentacoes por produto."""
        pass

    @abstractmethod
    async def get_by_warehouse(self, warehouse_id: UUID, tenant_id: UUID, skip: int = 0, limit: int = 100) -> list[Any]:
        """Lista movimentacoes por almoxarifado."""
        pass

    @abstractmethod
    async def get_pending_posting(self, tenant_id: UUID) -> list[Any]:
        """Lista movimentacoes pendentes de contabilizacao."""
        pass


class IJournalEntryRepository(IRepository):
    """Interface para repositorio de lancamentos contabeis."""

    @abstractmethod
    async def get_by_period(self, tenant_id: UUID, year: int, month: int, skip: int = 0, limit: int = 100) -> list[Any]:
        """Lista lancamentos por periodo."""
        pass

    @abstractmethod
    async def get_by_account(
        self, account_id: UUID, tenant_id: UUID, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> list[Any]:
        """Lista lancamentos por conta."""
        pass

    @abstractmethod
    async def get_pending_approval(self, tenant_id: UUID) -> list[Any]:
        """Lista lancamentos pendentes de aprovacao."""
        pass

    @abstractmethod
    async def get_by_source(self, source_document_id: UUID, tenant_id: UUID) -> list[Any]:
        """Lista lancamentos por documento de origem."""
        pass


class IEmployeeRepository(IRepository):
    """Interface para repositorio de colaboradores."""

    @abstractmethod
    async def get_by_cpf(self, cpf: str, tenant_id: UUID) -> Any | None:
        """Busca colaborador por CPF."""
        pass

    @abstractmethod
    async def get_by_department(
        self, department_id: UUID, tenant_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Any]:
        """Lista colaboradores por departamento."""
        pass

    @abstractmethod
    async def get_active(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> list[Any]:
        """Lista colaboradores ativos."""
        pass

    @abstractmethod
    async def get_by_manager(self, manager_id: UUID, tenant_id: UUID) -> list[Any]:
        """Lista colaboradores por gestor."""
        pass


class IProcurementRepository(IRepository):
    """Interface para repositorio de contratacoes."""

    @abstractmethod
    async def get_by_status(self, status: str, tenant_id: UUID, skip: int = 0, limit: int = 100) -> list[Any]:
        """Lista contratacoes por status."""
        pass

    @abstractmethod
    async def get_by_supplier(self, supplier_id: UUID, tenant_id: UUID) -> list[Any]:
        """Lista contratacoes por fornecedor."""
        pass

    @abstractmethod
    async def get_expiring(self, tenant_id: UUID, days_ahead: int = 30) -> list[Any]:
        """Lista contratacoes proximas do vencimento."""
        pass

    @abstractmethod
    async def get_by_budget(self, budget_id: UUID, tenant_id: UUID) -> list[Any]:
        """Lista contratacoes por orcamento."""
        pass
