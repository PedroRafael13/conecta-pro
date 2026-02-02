"""
Repository para operações de banco de dados com Employee.
"""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee


class EmployeeRepository:
    """Repository para operações de consulta de Employee."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, employee_id: str) -> Employee | None:
        """Busca funcionário por ID (UUID)."""
        result = await self.db.execute(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_matricula(self, matricula: str) -> Employee | None:
        """Busca funcionário por matrícula."""
        result = await self.db.execute(
            select(Employee).where(
                Employee.matricula == matricula,
                Employee.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Employee | None:
        """Busca funcionário por CPF (com ou sem formatação)."""
        cpf_clean = cpf.replace(".", "").replace("-", "")
        result = await self.db.execute(
            select(Employee).where(
                or_(
                    Employee.cpf == cpf,
                    Employee.cpf == cpf_clean,
                ),
                Employee.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def search_by_name(self, name: str, limit: int = 5) -> list[Employee]:
        """
        Busca funcionários por nome usando ILIKE (fuzzy).

        Cada palavra do termo de busca deve estar presente no nome
        ou nome social. Ex: "joao silva" encontra "João Carlos da Silva".

        Args:
            name: Termo de busca (parcial)
            limit: Máximo de resultados

        Returns:
            Lista de funcionários encontrados
        """
        words = name.strip().split()
        if not words:
            return []

        query = select(Employee).where(Employee.is_active.is_(True))
        for word in words:
            if len(word) >= 2:
                query = query.where(
                    or_(
                        Employee.nome.ilike(f"%{word}%"),
                        Employee.nome_social.ilike(f"%{word}%"),
                    )
                )

        query = query.order_by(Employee.nome).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
