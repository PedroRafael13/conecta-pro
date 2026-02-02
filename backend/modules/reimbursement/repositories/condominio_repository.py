"""
Repository para operações de condomínios/tenants.

Usado para buscar condomínio ativo quando necessário.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from core.logging import logger


class CondominioRepository:
    """
    Repository para operações de consulta de condomínios.

    Abstrai acesso ao banco de dados para buscar condomínios ativos.
    """

    def __init__(self, db: AsyncSession):
        """
        Inicializa repository.

        Args:
            db: Sessão assíncrona do SQLAlchemy
        """
        self.db = db

    async def get_first_active_condominio(self) -> Optional[UUID]:
        """
        Busca primeiro condomínio ativo disponível.

        Tenta primeiro a tabela `condominios`, depois `tenants` se não encontrar.

        Returns:
            UUID do condomínio ou None se não encontrar nenhum

        Example:
            ```python
            repo = CondominioRepository(db)
            cond_id = await repo.get_first_active_condominio()
            if cond_id:
                print(f"Usando condomínio: {cond_id}")
            ```
        """
        # Tenta tabela condominios primeiro
        try:
            # Importar modelo dinamicamente para evitar dependência circular
            from core.database import Base

            # Verificar se tabela existe
            result = await self.db.execute(
                select(Base.metadata.tables.get('condominios').c.id)
                .where(Base.metadata.tables.get('condominios').c.ativo == True)  # noqa: E712
                .limit(1)
            )
            row = result.first()
            if row:
                logger.info("Condomínio ativo encontrado na tabela condominios")
                return UUID(str(row[0]))
        except (KeyError, AttributeError, Exception) as e:
            logger.debug(f"Tabela condominios não disponível ou erro: {e}")

        # Se não encontrou, tenta tabela tenants
        try:
            result = await self.db.execute(
                select(Base.metadata.tables.get('tenants').c.id)
                .limit(1)
            )
            row = result.first()
            if row:
                logger.info("Condomínio encontrado na tabela tenants")
                return UUID(str(row[0]))
        except (KeyError, AttributeError, Exception) as e:
            logger.debug(f"Tabela tenants não disponível ou erro: {e}")

        logger.warning("Nenhum condomínio ativo encontrado no sistema")
        return None

    async def get_condominio_by_id(self, condominio_id: UUID) -> Optional[dict]:
        """
        Busca condomínio por ID.

        Args:
            condominio_id: UUID do condomínio

        Returns:
            Dicionário com dados do condomínio ou None
        """
        from core.database import Base

        try:
            table = Base.metadata.tables.get('condominios')
            if table is not None:
                result = await self.db.execute(
                    select(
                        table.c.id,
                        table.c.nome,
                        table.c.ativo,
                    )
                    .where(table.c.id == str(condominio_id))
                )
                row = result.first()
                if row:
                    return {
                        "id": UUID(str(row[0])),
                        "nome": row[1],
                        "ativo": row[2],
                    }
        except Exception as e:
            logger.error(f"Erro ao buscar condomínio: {e}")

        return None

    async def condominio_exists(self, condominio_id: UUID) -> bool:
        """
        Verifica se condomínio existe.

        Args:
            condominio_id: UUID do condomínio

        Returns:
            True se existe
        """
        condominio = await self.get_condominio_by_id(condominio_id)
        return condominio is not None
