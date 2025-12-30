"""Service para ResidentDependent."""

import logging
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.residents.repositories.dependent_repository import DependentRepository
from modules.residents.schemas.dependent import (
    DependentCreate,
    DependentUpdate,
    DependentFilter,
    DependentResponse,
    DependentListResponse,
    DependentStats,
)

logger = logging.getLogger(__name__)


class DependentService:
    """Service para operações de ResidentDependent."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = DependentRepository(session)

    async def create(self, data: DependentCreate) -> DependentResponse:
        """Cria um novo dependente."""
        # Verifica CPF duplicado
        if data.cpf:
            existing = await self.repository.get_by_cpf(data.cpf)
            if existing:
                raise ValueError(f"Já existe dependente com CPF: {data.cpf}")

        # Verifica documento duplicado
        if data.document_number:
            existing = await self.repository.get_by_document(data.document_number)
            if existing:
                raise ValueError(
                    f"Já existe dependente com documento: {data.document_number}"
                )

        dependent = await self.repository.create(data)
        await self.session.commit()
        logger.info("Dependente criado: {dependent.id} - {dependent.name}")
        return DependentResponse.model_validate(dependent)

    async def get_by_id(self, dependent_id: str | UUID) -> Optional[DependentResponse]:
        """Busca dependente por ID."""
        dependent = await self.repository.get_by_id(dependent_id)
        if not dependent:
            return None
        return DependentResponse.model_validate(dependent)

    async def get_by_cpf(self, cpf: str) -> Optional[DependentResponse]:
        """Busca dependente por CPF."""
        dependent = await self.repository.get_by_cpf(cpf)
        if not dependent:
            return None
        return DependentResponse.model_validate(dependent)

    async def get_by_resident(
        self, resident_id: str | UUID, include_inactive: bool = False
    ) -> list[DependentResponse]:
        """Busca dependentes do morador."""
        dependents = await self.repository.get_by_resident(
            resident_id, include_inactive
        )
        return [DependentResponse.model_validate(d) for d in dependents]

    async def get_minors_by_resident(
        self, resident_id: str | UUID
    ) -> list[DependentResponse]:
        """Busca dependentes menores do morador."""
        dependents = await self.repository.get_minors_by_resident(resident_id)
        return [DependentResponse.model_validate(d) for d in dependents]

    async def update(
        self, dependent_id: str | UUID, data: DependentUpdate
    ) -> Optional[DependentResponse]:
        """Atualiza um dependente."""
        # Verifica CPF duplicado
        if data.cpf:
            existing = await self.repository.get_by_cpf(data.cpf)
            if existing and str(existing.id) != str(dependent_id):
                raise ValueError(f"Já existe dependente com CPF: {data.cpf}")

        # Verifica documento duplicado
        if data.document_number:
            existing = await self.repository.get_by_document(data.document_number)
            if existing and str(existing.id) != str(dependent_id):
                raise ValueError(
                    f"Já existe dependente com documento: {data.document_number}"
                )

        dependent = await self.repository.update(dependent_id, data)
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Dependente atualizado: {dependent.id}")
        return DependentResponse.model_validate(dependent)

    async def delete(self, dependent_id: str | UUID) -> bool:
        """Remove dependente (soft delete)."""
        result = await self.repository.soft_delete(dependent_id)
        if result:
            await self.session.commit()
            logger.info("Dependente removido: {dependent_id}")
        return result

    async def list(
        self,
        filters: Optional[DependentFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> DependentListResponse:
        """Lista dependentes com filtros e paginação."""
        skip = (page - 1) * page_size
        dependents, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return DependentListResponse(
            items=[DependentResponse.model_validate(d) for d in dependents],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def search(
        self, query: str, condominium_id: str = None, limit: int = 10
    ) -> list[DependentResponse]:
        """Busca dependentes."""
        dependents = await self.repository.search(query, condominium_id, limit)
        return [DependentResponse.model_validate(d) for d in dependents]

    async def get_blocked(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[DependentResponse]:
        """Lista dependentes bloqueados."""
        skip = (page - 1) * page_size
        dependents = await self.repository.get_blocked(condominium_id, skip, page_size)
        return [DependentResponse.model_validate(d) for d in dependents]

    async def get_employees(
        self, condominium_id: str = None, page: int = 1, page_size: int = 20
    ) -> list[DependentResponse]:
        """Lista funcionários domésticos."""
        skip = (page - 1) * page_size
        dependents = await self.repository.get_employees(
            condominium_id, skip, page_size
        )
        return [DependentResponse.model_validate(d) for d in dependents]

    async def get_temporary_expiring(
        self, days: int = 30, condominium_id: str = None
    ) -> list[DependentResponse]:
        """Lista dependentes temporários expirando."""
        dependents = await self.repository.get_temporary_expiring(days, condominium_id)
        return [DependentResponse.model_validate(d) for d in dependents]

    async def block(
        self, dependent_id: str | UUID, reason: str
    ) -> Optional[DependentResponse]:
        """Bloqueia dependente."""
        dependent = await self.repository.block(dependent_id, reason)
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Dependente bloqueado: {dependent_id} - Motivo: {reason}")
        return DependentResponse.model_validate(dependent)

    async def unblock(self, dependent_id: str | UUID) -> Optional[DependentResponse]:
        """Desbloqueia dependente."""
        dependent = await self.repository.unblock(dependent_id)
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Dependente desbloqueado: {dependent_id}")
        return DependentResponse.model_validate(dependent)

    async def deactivate(self, dependent_id: str | UUID) -> Optional[DependentResponse]:
        """Desativa dependente."""
        dependent = await self.repository.deactivate(dependent_id)
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Dependente desativado: {dependent_id}")
        return DependentResponse.model_validate(dependent)

    async def activate(self, dependent_id: str | UUID) -> Optional[DependentResponse]:
        """Ativa dependente."""
        dependent = await self.repository.activate(dependent_id)
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Dependente ativado: {dependent_id}")
        return DependentResponse.model_validate(dependent)

    async def set_temporary(
        self, dependent_id: str | UUID, valid_from: date, valid_until: date
    ) -> Optional[DependentResponse]:
        """Define como temporário."""
        if valid_from >= valid_until:
            raise ValueError("Data inicial deve ser anterior à data final")

        dependent = await self.repository.set_temporary(
            dependent_id, valid_from, valid_until
        )
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Dependente definido como temporário: {dependent_id}")
        return DependentResponse.model_validate(dependent)

    async def add_authorized_pickup(
        self,
        dependent_id: str | UUID,
        person_name: str,
        person_phone: str,
        document: str = None,
    ) -> Optional[DependentResponse]:
        """Adiciona pessoa autorizada a buscar."""
        dependent = await self.repository.add_authorized_pickup(
            dependent_id, person_name, person_phone, document
        )
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Pessoa autorizada adicionada: {dependent_id} - {person_name}")
        return DependentResponse.model_validate(dependent)

    async def remove_authorized_pickup(
        self, dependent_id: str | UUID, person_name: str
    ) -> Optional[DependentResponse]:
        """Remove pessoa autorizada a buscar."""
        dependent = await self.repository.remove_authorized_pickup(
            dependent_id, person_name
        )
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Pessoa autorizada removida: {dependent_id} - {person_name}")
        return DependentResponse.model_validate(dependent)

    async def set_work_schedule(
        self, dependent_id: str | UUID, schedule: dict
    ) -> Optional[DependentResponse]:
        """Define horário de trabalho para funcionário doméstico."""
        dependent = await self.repository.set_work_schedule(dependent_id, schedule)
        if not dependent:
            return None
        await self.session.commit()
        logger.info("Horário de trabalho definido: {dependent_id}")
        return DependentResponse.model_validate(dependent)

    async def get_stats(self, condominium_id: str = None) -> DependentStats:
        """Retorna estatísticas."""
        stats = await self.repository.get_stats(condominium_id)
        return DependentStats(**stats)

    async def validate_access(
        self, dependent_id: str | UUID
    ) -> dict:
        """Valida se dependente tem acesso."""
        dependent = await self.repository.get_by_id(dependent_id)
        if not dependent:
            return {
                "allowed": False,
                "reason": "Dependente não encontrado",
                "dependent": None,
            }

        if not dependent.is_valid:
            if dependent.is_blocked:
                reason = "Dependente bloqueado"
            elif dependent.valid_until and dependent.valid_until < date.today():
                reason = "Período de validade expirado"
            else:
                reason = "Dependente inativo"
            return {
                "allowed": False,
                "reason": reason,
                "dependent": DependentResponse.model_validate(dependent),
            }

        if not dependent.has_access:
            return {
                "allowed": False,
                "reason": "Dependente sem permissão de acesso",
                "dependent": DependentResponse.model_validate(dependent),
            }

        return {
            "allowed": True,
            "reason": "Acesso permitido",
            "dependent": DependentResponse.model_validate(dependent),
        }
