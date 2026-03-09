"""Repository para o módulo de Empresas (Multi-CNPJ)."""

import logging
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from modules.empresas.models.empresa import Empresa, Liminar, LiminarStatusEnum

logger = logging.getLogger(__name__)


class EmpresaRepository:
    """Repository para operações com Empresa."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def criar_empresa(
        self,
        dados: dict,
        condominio_id: UUID,
    ) -> Empresa:
        """Cria uma nova empresa."""
        empresa = Empresa(
            condominio_id=condominio_id,
            **dados,
        )
        self.session.add(empresa)
        await self.session.flush()
        await self.session.refresh(empresa)
        return empresa

    async def listar_empresas(
        self,
        condominio_id: UUID,
        status: Optional[str] = None,
    ) -> List[Empresa]:
        """Lista empresas do tenant."""
        conditions = [Empresa.condominio_id == condominio_id]
        if status:
            conditions.append(Empresa.status == status)

        stmt = (
            select(Empresa)
            .where(and_(*conditions))
            .options(selectinload(Empresa.liminares))
            .order_by(Empresa.is_principal.desc(), Empresa.razao_social)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obter_empresa(
        self,
        empresa_id: UUID,
        condominio_id: UUID,
    ) -> Optional[Empresa]:
        """Obtém empresa por ID."""
        stmt = (
            select(Empresa)
            .where(
                and_(
                    Empresa.id == empresa_id,
                    Empresa.condominio_id == condominio_id,
                )
            )
            .options(selectinload(Empresa.liminares))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def obter_empresa_por_slug(
        self,
        slug: str,
        condominio_id: UUID,
    ) -> Optional[Empresa]:
        """Obtém empresa pelo slug."""
        stmt = (
            select(Empresa)
            .where(
                and_(
                    Empresa.slug == slug,
                    Empresa.condominio_id == condominio_id,
                )
            )
            .options(selectinload(Empresa.liminares))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def obter_empresa_por_cnpj(
        self,
        cnpj: str,
        condominio_id: UUID,
    ) -> Optional[Empresa]:
        """Obtém empresa pelo CNPJ."""
        stmt = (
            select(Empresa)
            .where(
                and_(
                    Empresa.cnpj == cnpj,
                    Empresa.condominio_id == condominio_id,
                )
            )
            .options(selectinload(Empresa.liminares))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def atualizar_empresa(
        self,
        empresa_id: UUID,
        dados: dict,
        condominio_id: UUID,
    ) -> Optional[Empresa]:
        """Atualiza dados de uma empresa."""
        empresa = await self.obter_empresa(empresa_id, condominio_id)
        if not empresa:
            return None

        dados["updated_at"] = date.today()
        for campo, valor in dados.items():
            if valor is not None:
                setattr(empresa, campo, valor)

        await self.session.flush()
        await self.session.refresh(empresa)
        return empresa

    # ===================================================================
    # LIMINARES
    # ===================================================================

    async def criar_liminar(
        self,
        empresa_id: UUID,
        dados: dict,
    ) -> Liminar:
        """Cria uma nova liminar para a empresa."""
        liminar = Liminar(
            empresa_id=empresa_id,
            **dados,
        )
        self.session.add(liminar)
        await self.session.flush()
        await self.session.refresh(liminar)
        return liminar

    async def listar_liminares(
        self,
        empresa_id: UUID,
        status: Optional[str] = None,
    ) -> List[Liminar]:
        """Lista liminares de uma empresa."""
        conditions = [Liminar.empresa_id == empresa_id]
        if status:
            conditions.append(Liminar.status == status)

        stmt = (
            select(Liminar)
            .where(and_(*conditions))
            .order_by(Liminar.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def obter_liminar(
        self,
        liminar_id: UUID,
    ) -> Optional[Liminar]:
        """Obtém liminar por ID."""
        stmt = select(Liminar).where(Liminar.id == liminar_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def atualizar_liminar(
        self,
        liminar_id: UUID,
        dados: dict,
    ) -> Optional[Liminar]:
        """Atualiza dados de uma liminar."""
        liminar = await self.obter_liminar(liminar_id)
        if not liminar:
            return None

        dados["updated_at"] = date.today()
        for campo, valor in dados.items():
            if valor is not None:
                setattr(liminar, campo, valor)

        await self.session.flush()
        await self.session.refresh(liminar)
        return liminar

    async def liminares_ativas(
        self,
        empresa_id: UUID,
    ) -> List[Liminar]:
        """Retorna liminares ativas (concedidas) de uma empresa."""
        stmt = (
            select(Liminar)
            .where(
                and_(
                    Liminar.empresa_id == empresa_id,
                    Liminar.status == LiminarStatusEnum.CONCEDIDA.value,
                )
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
