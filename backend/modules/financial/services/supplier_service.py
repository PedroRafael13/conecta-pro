"""Service para fornecedores."""

import builtins
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.supplier import Supplier
from modules.financial.repositories.supplier_repository import SupplierRepository
from modules.financial.schemas.supplier import (
    SupplierCreate,
    SupplierFilter,
    SupplierStats,
    SupplierUpdate,
)

logger = logging.getLogger(__name__)


class SupplierService:
    """Service para operações com fornecedores."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = SupplierRepository(session)

    async def create(
        self,
        data: SupplierCreate,
        user_id: UUID,
    ) -> Supplier:
        """Cria um novo fornecedor."""
        # Verifica se já existe com mesmo CPF/CNPJ
        existing = await self.repository.get_by_cpf_cnpj(data.cpf_cnpj, data.condominio_id)
        if existing:
            raise ValueError(f"Já existe fornecedor com CPF/CNPJ {data.cpf_cnpj}")

        supplier = await self.repository.create(data, user_id)
        await self.session.commit()

        logger.info(f"Fornecedor criado: {supplier.id} - {supplier.name}")
        return supplier

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        """Busca fornecedor por ID."""
        return await self.repository.get_by_id(supplier_id)

    async def get_by_cpf_cnpj(
        self,
        cpf_cnpj: str,
        condominio_id: UUID,
    ) -> Supplier | None:
        """Busca fornecedor por CPF/CNPJ."""
        return await self.repository.get_by_cpf_cnpj(cpf_cnpj, condominio_id)

    async def list(
        self,
        condominio_id: UUID | None = None,
        filters: SupplierFilter | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Supplier], int]:
        """Lista fornecedores com filtros e paginação."""
        suppliers = await self.repository.list(condominio_id, filters, skip, limit)
        total = await self.repository.count(condominio_id, filters)
        return suppliers, total

    async def update(
        self,
        supplier_id: UUID,
        data: SupplierUpdate,
    ) -> Supplier | None:
        """Atualiza um fornecedor."""
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            return None

        supplier = await self.repository.update(supplier, data)
        await self.session.commit()

        logger.info(f"Fornecedor atualizado: {supplier_id}")
        return supplier

    async def delete(self, supplier_id: UUID) -> bool:
        """Deleta um fornecedor (soft delete)."""
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            return False

        await self.repository.delete(supplier)
        await self.session.commit()

        logger.info(f"Fornecedor excluído: {supplier_id}")
        return True

    async def block(
        self,
        supplier_id: UUID,
        reason: str,
        user_id: UUID,
    ) -> Supplier | None:
        """Bloqueia um fornecedor."""
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            return None

        if supplier.is_blocked:
            raise ValueError("Fornecedor já está bloqueado")

        supplier = await self.repository.block(supplier, reason, user_id)
        await self.session.commit()

        logger.info(f"Fornecedor bloqueado: {supplier_id} - Motivo: {reason}")
        return supplier

    async def unblock(self, supplier_id: UUID) -> Supplier | None:
        """Desbloqueia um fornecedor."""
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            return None

        if not supplier.is_blocked:
            raise ValueError("Fornecedor não está bloqueado")

        supplier = await self.repository.unblock(supplier)
        await self.session.commit()

        logger.info(f"Fornecedor desbloqueado: {supplier_id}")
        return supplier

    async def qualify(
        self,
        supplier_id: UUID,
        user_id: UUID,
    ) -> Supplier | None:
        """Qualifica um fornecedor."""
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            return None

        if supplier.is_qualified:
            raise ValueError("Fornecedor já está qualificado")

        supplier = await self.repository.qualify(supplier, user_id)
        await self.session.commit()

        logger.info(f"Fornecedor qualificado: {supplier_id}")
        return supplier

    async def get_stats(self, condominio_id: UUID) -> SupplierStats:
        """Retorna estatísticas de fornecedores."""
        return await self.repository.get_stats(condominio_id)

    async def search(
        self,
        condominio_id: UUID,
        query: str,
        limit: int = 10,
    ) -> builtins.list[Supplier]:
        """Busca rápida de fornecedores."""
        return await self.repository.search(condominio_id, query, limit)

    async def validate_for_payment(
        self,
        supplier_id: UUID,
    ) -> tuple[bool, str | None]:
        """Valida se fornecedor pode receber pagamentos."""
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            return False, "Fornecedor não encontrado"

        if not supplier.ativo:
            return False, "Fornecedor inativo"

        if supplier.is_blocked:
            return False, f"Fornecedor bloqueado: {supplier.block_reason}"

        # Verifica dados bancários se requer pagamento eletrônico
        if not supplier.bank_code and not supplier.pix_key:
            return False, "Fornecedor sem dados bancários ou PIX cadastrados"

        return True, None
