"""
Repository para operações de condomínios/tenants.

Usado para buscar condomínio ativo quando necessário.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def get_first_active_condominio(self) -> UUID | None:
        """
        Busca primeiro condomínio ativo disponível.

        Tenta primeiro a tabela `condominios`, depois `tenants` se não encontrar.

        Returns:
            UUID do condomínio ou None se não encontrar nenhum
        """
        from sqlalchemy import text

        # Tenta tabela condominios primeiro com raw SQL (evita problema de metadata)
        try:
            result = await self.db.execute(text("SELECT id FROM condominios WHERE ativo = true ORDER BY id LIMIT 1"))
            row = result.first()
            if row:
                logger.info("Condomínio ativo encontrado na tabela condominios")
                return UUID(str(row[0]))
        except Exception as e:
            logger.debug(f"Tabela condominios não disponível ou erro: {e}")

        # Se não encontrou, tenta tabela tenants
        try:
            result = await self.db.execute(text("SELECT id FROM tenants LIMIT 1"))
            row = result.first()
            if row:
                logger.info("Condomínio encontrado na tabela tenants")
                return UUID(str(row[0]))
        except Exception as e:
            logger.debug(f"Tabela tenants não disponível ou erro: {e}")

        logger.warning("Nenhum condomínio ativo encontrado no sistema")
        return None

    async def get_condominio_by_id(self, condominio_id: UUID) -> dict | None:
        """
        Busca condomínio por ID.

        Args:
            condominio_id: UUID do condomínio

        Returns:
            Dicionário com dados do condomínio ou None
        """
        from core.database import Base

        try:
            table = Base.metadata.tables.get("condominios")
            if table is not None:
                result = await self.db.execute(
                    select(
                        table.c.id,
                        table.c.nome,
                        table.c.ativo,
                    ).where(table.c.id == str(condominio_id))
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
