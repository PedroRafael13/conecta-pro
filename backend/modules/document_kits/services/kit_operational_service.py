"""
Serviço de Integração entre Document Kits e Módulo Operacional.

Este serviço conecta os módulos operacional (funcionários, postos, alocações)
com o módulo de kits documentais, permitindo buscar colaboradores por condomínio,
período e outros filtros necessários para geração automática de kits mensais.

Autor: CONECTAMAIS ELETRONICA LTDA
Data: 23/01/2026
"""

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.allocation import Allocation, AllocationStatus
from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post


class EmployeeAllocationData:
    """Classe para encapsular dados de funcionário + alocação + posto."""

    def __init__(self, employee: Employee, allocation: Allocation, post: Post):
        self.employee = employee
        self.allocation = allocation
        self.post = post

    def to_dict(self) -> dict:
        """Serializa para dicionário."""
        return {
            "employee": {
                "id": str(self.employee.id),
                "nome": self.employee.nome,
                "cpf": self.employee.cpf,
                "email": self.employee.email,
                "cargo": self.employee.cargo,
                "departamento": self.employee.departamento,
                "data_admissao": self.employee.data_admissao.isoformat() if self.employee.data_admissao else None,
                "status": self.employee.status,
            },
            "allocation": {
                "id": str(self.allocation.id),
                "post_id": str(self.allocation.post_id),
                "start_date": self.allocation.start_date.isoformat(),
                "end_date": self.allocation.end_date.isoformat() if self.allocation.end_date else None,
                "status": self.allocation.status,
                "role": self.allocation.role,
                "monthly_salary": float(self.allocation.monthly_salary) if self.allocation.monthly_salary else None,
                "is_primary": self.allocation.is_primary,
                "is_current": self.allocation.is_current,
            },
            "post": {
                "id": str(self.post.id),
                "code": self.post.code,
                "name": self.post.name,
                "post_type": self.post.post_type,
                "shift_type": self.post.shift_type,
            },
        }


class KitOperationalService:
    """
    Serviço para integrar Document Kits com Operacional.

    Funções principais:
    - Buscar funcionários por condomínio
    - Buscar funcionários por posto
    - Filtrar por período (mês/ano)
    - Obter dados para geração de kits mensais
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employees_by_condominium(
        self,
        condominium_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        include_inactive: bool = False,
    ) -> list[EmployeeAllocationData]:
        """
        Busca TODOS os colaboradores alocados em um condomínio no período.

        Esta é a função PRINCIPAL para geração de kits mensais.

        Args:
            condominium_id: UUID do condomínio
            start_date: Data inicial (default = hoje)
            end_date: Data final (default = hoje)
            include_inactive: Incluir funcionários inativos (default = False)

        Returns:
            Lista de EmployeeAllocationData com dados completos

        Exemplo:
            >>> service = KitOperationalService(db)
            >>> colaboradores = await service.get_employees_by_condominium(
            ...     condominium_id="uuid-ideal-flores",
            ...     start_date=date(2026, 1, 1),
            ...     end_date=date(2026, 1, 31)
            ... )
            >>> print(f"Total de colaboradores: {len(colaboradores)}")
            Total de colaboradores: 13
        """

        # 1. Buscar client_id do condomínio (raw SQL para evitar model quebrado)
        from sqlalchemy import text

        cond_result = await self.db.execute(
            text("SELECT client_id FROM condominiums WHERE id = :cond_id LIMIT 1"), {"cond_id": condominium_id}
        )
        cond_row = cond_result.fetchone()

        if not cond_row:
            raise ValueError(f"Condomínio {condominium_id} não encontrado")

        client_id = cond_row[0]

        # 2. Buscar posts do cliente (condomínio)
        posts_query = select(Post).where(
            Post.client_id == client_id,
            Post.is_active.is_(True),
        )

        posts_result = await self.db.execute(posts_query)
        posts = list(posts_result.scalars().all())

        if not posts:
            return []

        post_ids = [str(p.id) for p in posts]

        # 3. Buscar alocações vigentes no período
        target_start = start_date or date.today()
        target_end = end_date or date.today()

        # Query com JOIN para trazer Employee e Post de uma vez
        query = (
            select(Allocation, Employee, Post)
            .join(Employee, Allocation.employee_id == Employee.id)
            .join(Post, Allocation.post_id == Post.id)
            .where(
                Allocation.post_id.in_(post_ids),
                Allocation.status == AllocationStatus.ACTIVE.value,
                Allocation.start_date <= target_end,
                Allocation.is_active.is_(True),
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= target_start,
                ),
            )
        )

        # Filtrar funcionários inativos se necessário
        if not include_inactive:
            query = query.where(Employee.is_active.is_(True))

        # Ordenar por nome do funcionário
        query = query.order_by(Employee.nome)

        result = await self.db.execute(query)
        rows = result.all()

        # 4. Criar objetos EmployeeAllocationData
        employees_data = [
            EmployeeAllocationData(employee=emp, allocation=alloc, post=post) for alloc, emp, post in rows
        ]

        return employees_data

    async def get_employees_by_month(
        self,
        condominium_id: str,
        month: int,
        year: int,
        include_inactive: bool = False,
    ) -> list[EmployeeAllocationData]:
        """
        Busca colaboradores de um condomínio em um mês específico.

        Helper function para facilitar busca mensal (usa get_employees_by_condominium internamente).

        Args:
            condominium_id: UUID do condomínio
            month: Mês (1-12)
            year: Ano (ex: 2026)
            include_inactive: Incluir inativos

        Returns:
            Lista de EmployeeAllocationData

        Exemplo:
            >>> colaboradores = await service.get_employees_by_month(
            ...     condominium_id="uuid-ideal-flores",
            ...     month=1,
            ...     year=2026
            ... )
        """

        # Calcular primeiro e último dia do mês
        first_day = date(year, month, 1)

        # Último dia do mês
        if month == 12:
            last_day = date(year, 12, 31)
        else:
            next_month = date(year, month + 1, 1)
            last_day = next_month - timedelta(days=1)

        return await self.get_employees_by_condominium(
            condominium_id=condominium_id,
            start_date=first_day,
            end_date=last_day,
            include_inactive=include_inactive,
        )

    async def get_employees_by_post(
        self,
        post_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        include_inactive: bool = False,
    ) -> list[EmployeeAllocationData]:
        """
        Busca colaboradores de um posto específico no período.

        Args:
            post_id: UUID do posto
            start_date: Data inicial (default = hoje)
            end_date: Data final (default = hoje)
            include_inactive: Incluir inativos

        Returns:
            Lista de EmployeeAllocationData
        """

        target_start = start_date or date.today()
        target_end = end_date or date.today()

        query = (
            select(Allocation, Employee, Post)
            .join(Employee, Allocation.employee_id == Employee.id)
            .join(Post, Allocation.post_id == Post.id)
            .where(
                Allocation.post_id == UUID(post_id),
                Allocation.status == AllocationStatus.ACTIVE.value,
                Allocation.start_date <= target_end,
                Allocation.is_active.is_(True),
                or_(
                    Allocation.end_date.is_(None),
                    Allocation.end_date >= target_start,
                ),
            )
        )

        if not include_inactive:
            query = query.where(Employee.is_active.is_(True))

        query = query.order_by(Employee.nome)

        result = await self.db.execute(query)
        rows = result.all()

        return [EmployeeAllocationData(employee=emp, allocation=alloc, post=post) for alloc, emp, post in rows]

    async def count_employees_by_condominium(
        self,
        condominium_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """
        Conta o número de colaboradores de um condomínio no período.

        Args:
            condominium_id: UUID do condomínio
            start_date: Data inicial
            end_date: Data final

        Returns:
            Número de colaboradores
        """

        employees = await self.get_employees_by_condominium(
            condominium_id=condominium_id,
            start_date=start_date,
            end_date=end_date,
        )

        return len(employees)

    async def get_condominiums_with_employees(self) -> list[dict]:
        """
        Busca TODOS os condomínios que possuem funcionários alocados atualmente.

        Útil para geração de kits mensais em lote.

        Returns:
            Lista de dicts com condomínio + contagem de funcionários
            [
                {
                    "condominium_id": "uuid",
                    "condominium_name": "Ideal Flores da Cidade",
                    "client_id": "uuid",
                    "employee_count": 13,
                    "post_count": 5
                },
                ...
            ]
        """

        # Buscar todos os condominios ativos (raw SQL para evitar model quebrado)
        from sqlalchemy import text

        conds_result = await self.db.execute(text("SELECT id, name, client_id FROM condominiums WHERE ativo = true"))
        condominiums = conds_result.fetchall()

        result_list = []

        for cond in condominiums:
            cond_id, cond_name, cond_client_id = cond
            # Buscar posts do condomínio
            posts_result = await self.db.execute(
                select(Post).where(
                    Post.client_id == cond_client_id,
                    Post.is_active.is_(True),
                )
            )
            posts = list(posts_result.scalars().all())

            if not posts:
                continue

            post_ids = [str(p.id) for p in posts]

            # Contar alocações vigentes
            today = date.today()
            count_result = await self.db.execute(
                select(func.count(Allocation.id.distinct())).where(
                    Allocation.post_id.in_(post_ids),
                    Allocation.status == AllocationStatus.ACTIVE.value,
                    Allocation.start_date <= today,
                    Allocation.is_active.is_(True),
                    or_(
                        Allocation.end_date.is_(None),
                        Allocation.end_date >= today,
                    ),
                )
            )
            employee_count = count_result.scalar()

            if employee_count > 0:
                result_list.append(
                    {
                        "condominium_id": str(cond_id),
                        "condominium_name": cond_name,
                        "client_id": str(cond_client_id),
                        "employee_count": employee_count,
                        "post_count": len(posts),
                    }
                )

        return result_list

    async def validate_condominium_has_employees(
        self,
        condominium_id: str,
        month: int | None = None,
        year: int | None = None,
    ) -> dict:
        """
        Valida se um condomínio possui funcionários no período.

        Args:
            condominium_id: UUID do condomínio
            month: Mês (opcional, default = mês atual)
            year: Ano (opcional, default = ano atual)

        Returns:
            {
                "has_employees": bool,
                "employee_count": int,
                "period": "01/2026",
                "message": str
            }
        """

        if not month or not year:
            today = date.today()
            month = month or today.month
            year = year or today.year

        employees = await self.get_employees_by_month(
            condominium_id=condominium_id,
            month=month,
            year=year,
        )

        count = len(employees)

        return {
            "has_employees": count > 0,
            "employee_count": count,
            "period": f"{month:02d}/{year}",
            "message": (
                f"Condomínio possui {count} funcionário(s) no período"
                if count > 0
                else "Condomínio não possui funcionários no período"
            ),
        }
