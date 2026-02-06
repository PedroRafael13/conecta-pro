"""
Classe base abstrata para executores de ações.
"""

import logging
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post
from modules.operacional.repositories.employee_repository import EmployeeRepository
from modules.operacional.repositories.post_repository import PostRepository

from ..action_schemas import ActionPreview, ActionRequest, ActionResult

logger = logging.getLogger(__name__)


class BaseActionExecutor(ABC):
    """Classe abstrata para executores de ação."""

    def __init__(self, db: AsyncSession):
        """
        Inicializa executor.

        Args:
            db: Sessão async do SQLAlchemy
        """
        self.db = db

    async def resolve_post(self, params: dict) -> tuple[Post | None, list[str]]:
        """
        Resolve posto a partir de post_code ou post_name nos parâmetros.

        Tenta code primeiro (match exato), depois name (ILIKE fuzzy).

        Args:
            params: Dicionário de parâmetros (post_code e/ou post_name)

        Returns:
            Tupla (post encontrado ou None, lista de warnings)
        """
        warnings: list[str] = []
        post_repo = PostRepository(self.db)
        post_code = params.get("post_code")
        post_name = params.get("post_name")

        # 1. Tentar por código exato
        if post_code:
            post = await post_repo.get_by_code(post_code)
            if post:
                logger.info(f"Post resolvido por código: {post.code} - {post.name}")
                return post, warnings
            # Código não encontrou, avisar
            warnings.append(f"⚠️ Posto '{post_code}' não encontrado por código")

        # 2. Fallback: busca por nome
        if post_name:
            matches = await post_repo.search_by_name(post_name)
            if len(matches) == 1:
                post = matches[0]
                logger.info(f"Post resolvido por nome '{post_name}': {post.code} - {post.name}")
                return post, warnings
            elif len(matches) > 1:
                names_list = ", ".join(f"{p.code} ({p.name})" for p in matches[:3])
                warnings.append(f"⚠️ Múltiplos postos encontrados para '{post_name}': {names_list}")
                # Retorna o primeiro match como melhor candidato
                return matches[0], warnings
            else:
                warnings.append(f"⚠️ Nenhum posto encontrado para '{post_name}'")

        if not post_code and not post_name:
            warnings.append("⚠️ Código ou nome do posto não informado")

        return None, warnings

    async def resolve_employee(self, params: dict) -> tuple[Employee | None, list[str]]:
        """
        Resolve funcionário a partir de employee_id, employee_name ou employee_matricula.

        Tenta ID primeiro, depois matrícula, depois nome (ILIKE fuzzy).

        Args:
            params: Dicionário de parâmetros

        Returns:
            Tupla (employee encontrado ou None, lista de warnings)
        """
        warnings: list[str] = []
        emp_repo = EmployeeRepository(self.db)
        employee_id = params.get("employee_id")
        employee_name = params.get("employee_name")
        employee_matricula = params.get("employee_matricula")

        # 1. Tentar por ID exato
        if employee_id:
            employee = await emp_repo.get_by_id(employee_id)
            if employee:
                logger.info(f"Employee resolvido por ID: {employee.nome}")
                return employee, warnings
            warnings.append(f"⚠️ Funcionário '{employee_id}' não encontrado por ID")

        # 2. Tentar por matrícula
        if employee_matricula:
            employee = await emp_repo.get_by_matricula(employee_matricula)
            if employee:
                logger.info(f"Employee resolvido por matrícula '{employee_matricula}': {employee.nome}")
                return employee, warnings
            warnings.append(f"⚠️ Matrícula '{employee_matricula}' não encontrada")

        # 3. Fallback: busca por nome
        if employee_name:
            matches = await emp_repo.search_by_name(employee_name)
            if len(matches) == 1:
                employee = matches[0]
                logger.info(f"Employee resolvido por nome '{employee_name}': {employee.nome} ({employee.matricula})")
                return employee, warnings
            elif len(matches) > 1:
                names_list = ", ".join(f"{e.nome} ({e.matricula or 'sem mat.'})" for e in matches[:3])
                warnings.append(f"⚠️ Múltiplos funcionários para '{employee_name}': {names_list}")
                return matches[0], warnings
            else:
                warnings.append(f"⚠️ Nenhum funcionário encontrado para '{employee_name}'")

        if not employee_id and not employee_name and not employee_matricula:
            warnings.append("⚠️ ID, nome ou matrícula do funcionário não informado")

        return None, warnings

    @abstractmethod
    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """
        Cria preview da ação para confirmação do usuário.

        Args:
            request: Request de ação

        Returns:
            Preview com detalhes da ação
        """
        pass

    @abstractmethod
    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """
        Executa a ação confirmada.

        Args:
            request: Request de ação
            action_id: ID da ação

        Returns:
            Resultado da execução
        """
        pass
