"""Repository para fornecedores."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.supplier import (
    Supplier,
    SupplierCategory,
    SupplierStatus,
    SupplierType,
)
from modules.financial.schemas.supplier import (
    SupplierCreate,
    SupplierFilter,
    SupplierStats,
    SupplierUpdate,
)


class SupplierRepository:
    """Repository para operações com fornecedores."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: SupplierCreate, user_id: Optional[UUID] = None) -> Supplier:
        """Cria um novo fornecedor."""
        supplier = Supplier(
            **data.model_dump(),
            created_by=user_id,
        )
        self.session.add(supplier)
        await self.session.flush()
        await self.session.refresh(supplier)
        return supplier

    async def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]:
        """Busca fornecedor por ID."""
        result = await self.session.execute(
            select(Supplier).where(
                and_(
                    Supplier.id == supplier_id,
                    Supplier.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_cpf_cnpj(
        self,
        cpf_cnpj: str,
        condominio_id: UUID,
    ) -> Optional[Supplier]:
        """Busca fornecedor por CPF/CNPJ."""
        result = await self.session.execute(
            select(Supplier).where(
                and_(
                    Supplier.cpf_cnpj == cpf_cnpj,
                    Supplier.condominio_id == condominio_id,
                    Supplier.ativo == True,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        condominio_id: UUID,
        filters: Optional[SupplierFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Supplier]:
        """Lista fornecedores com filtros."""
        query = select(Supplier).where(
            and_(
                Supplier.condominio_id == condominio_id,
                Supplier.ativo == True,  # noqa: E712
            )
        )

        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Supplier.name.ilike(search_term),
                        Supplier.trade_name.ilike(search_term),
                        Supplier.cpf_cnpj.ilike(search_term),
                        Supplier.email.ilike(search_term),
                    )
                )

            if filters.supplier_type:
                query = query.where(Supplier.supplier_type == filters.supplier_type.value)

            if filters.category:
                query = query.where(Supplier.category == filters.category.value)

            if filters.status:
                query = query.where(Supplier.status == filters.status.value)

            if filters.is_qualified is not None:
                query = query.where(Supplier.is_qualified == filters.is_qualified)

            if filters.is_blocked is not None:
                query = query.where(Supplier.is_blocked == filters.is_blocked)

            if filters.city:
                query = query.where(Supplier.address_city.ilike(f"%{filters.city}%"))

            if filters.state:
                query = query.where(Supplier.address_state == filters.state.upper())

            if filters.tags:
                for tag in filters.tags:
                    query = query.where(Supplier.tags.contains([tag]))

        query = query.order_by(Supplier.name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        condominio_id: UUID,
        filters: Optional[SupplierFilter] = None,
    ) -> int:
        """Conta fornecedores com filtros."""
        query = select(func.count(Supplier.id)).where(
            and_(
                Supplier.condominio_id == condominio_id,
                Supplier.ativo == True,  # noqa: E712
            )
        )

        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Supplier.name.ilike(search_term),
                        Supplier.trade_name.ilike(search_term),
                        Supplier.cpf_cnpj.ilike(search_term),
                    )
                )

            if filters.supplier_type:
                query = query.where(Supplier.supplier_type == filters.supplier_type.value)

            if filters.category:
                query = query.where(Supplier.category == filters.category.value)

            if filters.status:
                query = query.where(Supplier.status == filters.status.value)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(
        self,
        supplier: Supplier,
        data: SupplierUpdate,
    ) -> Supplier:
        """Atualiza fornecedor."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(supplier, field):
                setattr(supplier, field, value)

        supplier.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(supplier)
        return supplier

    async def delete(self, supplier: Supplier) -> None:
        """Deleta fornecedor (soft delete)."""
        supplier.ativo = False
        supplier.status = SupplierStatus.INATIVO.value
        supplier.updated_at = datetime.utcnow()
        await self.session.flush()

    async def block(
        self,
        supplier: Supplier,
        reason: str,
        user_id: UUID,
    ) -> Supplier:
        """Bloqueia fornecedor."""
        supplier.block(reason, user_id)
        await self.session.flush()
        await self.session.refresh(supplier)
        return supplier

    async def unblock(self, supplier: Supplier) -> Supplier:
        """Desbloqueia fornecedor."""
        supplier.unblock()
        await self.session.flush()
        await self.session.refresh(supplier)
        return supplier

    async def qualify(
        self,
        supplier: Supplier,
        user_id: UUID,
    ) -> Supplier:
        """Qualifica fornecedor."""
        supplier.qualify(user_id)
        await self.session.flush()
        await self.session.refresh(supplier)
        return supplier

    async def get_stats(self, condominio_id: UUID) -> SupplierStats:
        """Retorna estatísticas de fornecedores."""
        # Total e por status
        status_query = (
            select(
                Supplier.status,
                func.count(Supplier.id).label("count"),
            )
            .where(
                and_(
                    Supplier.condominio_id == condominio_id,
                    Supplier.ativo == True,  # noqa: E712
                )
            )
            .group_by(Supplier.status)
        )

        status_result = await self.session.execute(status_query)
        status_data = {row.status: row.count for row in status_result}

        # Por tipo
        type_query = (
            select(
                Supplier.supplier_type,
                func.count(Supplier.id).label("count"),
            )
            .where(
                and_(
                    Supplier.condominio_id == condominio_id,
                    Supplier.ativo == True,  # noqa: E712
                )
            )
            .group_by(Supplier.supplier_type)
        )

        type_result = await self.session.execute(type_query)
        type_data = {row.supplier_type: row.count for row in type_result}

        # Por categoria
        category_query = (
            select(
                Supplier.category,
                func.count(Supplier.id).label("count"),
            )
            .where(
                and_(
                    Supplier.condominio_id == condominio_id,
                    Supplier.ativo == True,  # noqa: E712
                    Supplier.category.isnot(None),
                )
            )
            .group_by(Supplier.category)
        )

        category_result = await self.session.execute(category_query)
        category_data = {row.category: row.count for row in category_result}

        # Qualificados
        qualified_query = select(func.count(Supplier.id)).where(
            and_(
                Supplier.condominio_id == condominio_id,
                Supplier.ativo == True,  # noqa: E712
                Supplier.is_qualified == True,  # noqa: E712
            )
        )
        qualified_result = await self.session.execute(qualified_query)
        qualified_count = qualified_result.scalar_one()

        total = sum(status_data.values())

        return SupplierStats(
            total=total,
            ativos=status_data.get(SupplierStatus.ATIVO.value, 0),
            inativos=status_data.get(SupplierStatus.INATIVO.value, 0),
            bloqueados=status_data.get(SupplierStatus.BLOQUEADO.value, 0),
            qualificados=qualified_count,
            por_tipo=type_data,
            por_categoria=category_data,
        )

    async def search(
        self,
        condominio_id: UUID,
        query: str,
        limit: int = 10,
    ) -> List[Supplier]:
        """Busca rápida de fornecedores."""
        search_term = f"%{query}%"
        result = await self.session.execute(
            select(Supplier)
            .where(
                and_(
                    Supplier.condominio_id == condominio_id,
                    Supplier.ativo == True,  # noqa: E712
                    Supplier.status == SupplierStatus.ATIVO.value,
                    or_(
                        Supplier.name.ilike(search_term),
                        Supplier.trade_name.ilike(search_term),
                        Supplier.cpf_cnpj.ilike(search_term),
                    ),
                )
            )
            .order_by(Supplier.name)
            .limit(limit)
        )
        return list(result.scalars().all())
