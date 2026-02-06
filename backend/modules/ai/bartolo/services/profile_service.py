"""
Profile Service - Servico de Perfil do Usuario.

Gerencia contexto do usuario para personalizacao das respostas do Bartolo.
Integra com o modelo User real do sistema via SQLAlchemy async.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai.bartolo.config.user_profiles import (
    UserRole,
    Department,
    USER_PROFILES,
    get_profile_context,
    get_profile_modules,
    get_communication_style,
)

logger = logging.getLogger(__name__)

# TTL do cache em segundos (5 minutos)
CACHE_TTL_SECONDS = 300


@dataclass
class UserContext:
    """Contexto do usuario para o Bartolo."""
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[Department] = None
    is_manager: bool = False
    experience_level: str = "intermediate"
    preferences: dict = field(default_factory=dict)
    permissions: list = field(default_factory=list)
    last_modules: list = field(default_factory=list)
    interaction_count: int = 0
    first_interaction: Optional[datetime] = None
    last_interaction: Optional[datetime] = None

    def to_prompt_context(self) -> str:
        """Converte contexto para texto de prompt."""
        parts = ["CONTEXTO DO USUARIO:"]

        if self.name:
            parts.append(f"- Nome: {self.name}")

        if self.role:
            parts.append(f"- Cargo: {self.role.value}")
            profile_context = get_profile_context(self.role)
            if profile_context:
                parts.append(profile_context)

        if self.department:
            parts.append(f"- Departamento: {self.department.value}")

        if self.is_manager:
            parts.append("- E gestor de equipe")

        if self.experience_level:
            level_desc = {
                "beginner": "Usuario iniciante - usar linguagem mais simples e detalhada",
                "intermediate": "Usuario com experiencia media",
                "advanced": "Usuario avancado - pode usar termos tecnicos",
            }
            parts.append(f"- Nivel: {level_desc.get(self.experience_level, '')}")

        if self.last_modules:
            parts.append(f"- Modulos recentes: {', '.join(self.last_modules[-3:])}")

        return "\n".join(parts)

    def get_priority_modules(self) -> list:
        """Retorna modulos prioritarios para o perfil."""
        if self.role:
            return get_profile_modules(self.role)
        return []

    def get_communication_style(self) -> str:
        """Retorna estilo de comunicacao."""
        if self.role:
            return get_communication_style(self.role)
        return "detailed"


class ProfileService:
    """
    Servico de gerenciamento de perfis de usuario.

    Responsavel por:
    - Carregar dados do usuario do banco real (tabela users)
    - Manter contexto de interacoes com cache TTL
    - Adaptar respostas ao perfil
    - Fallback para dados mock quando db nao disponivel
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        """
        Inicializa o servico.

        Args:
            db: Sessao async do banco de dados (opcional).
                Pode ser definida depois via set_db().
        """
        self._db: Optional[AsyncSession] = db
        self._user_cache: dict[int, UserContext] = {}
        self._cache_timestamps: dict[int, float] = {}

    def set_db(self, db: Optional[AsyncSession]) -> None:
        """
        Define ou atualiza a sessao do banco de dados.

        Args:
            db: Sessao async do SQLAlchemy
        """
        self._db = db

    def _is_cache_valid(self, user_id: int) -> bool:
        """Verifica se o cache do usuario ainda e valido pelo TTL."""
        if user_id not in self._cache_timestamps:
            return False
        elapsed = time.time() - self._cache_timestamps[user_id]
        return elapsed < CACHE_TTL_SECONDS

    async def get_user_context(self, user_id: int) -> UserContext:
        """
        Recupera ou cria contexto do usuario.

        Busca primeiro no cache (com TTL). Se nao encontrar ou expirado,
        consulta o banco de dados real. Se db nao disponivel, usa fallback mock.

        Args:
            user_id: ID do usuario

        Returns:
            UserContext com dados do usuario
        """
        # Verifica cache com TTL
        if user_id in self._user_cache and self._is_cache_valid(user_id):
            context = self._user_cache[user_id]
            context.last_interaction = datetime.utcnow()
            context.interaction_count += 1
            return context

        # Busca dados do usuario no banco real (com fallback mock)
        user_data = await self._load_user_data(user_id)

        # Cria contexto
        context = UserContext(
            user_id=user_id,
            name=user_data.get("name"),
            email=user_data.get("email"),
            role=self._parse_role(user_data.get("role")),
            department=self._parse_department(user_data.get("department")),
            is_manager=user_data.get("is_manager", False),
            experience_level=user_data.get("experience_level", "intermediate"),
            preferences=user_data.get("preferences", {}),
            permissions=user_data.get("permissions", []),
            first_interaction=datetime.utcnow(),
            last_interaction=datetime.utcnow(),
            interaction_count=1,
        )

        # Salva no cache com timestamp
        self._user_cache[user_id] = context
        self._cache_timestamps[user_id] = time.time()

        return context

    async def _load_user_data(self, user_id: int) -> dict:
        """
        Carrega dados do usuario do banco real.

        Tenta buscar na tabela users via SQLAlchemy async.
        Se o banco nao estiver disponivel, usa fallback com dados mock.

        Args:
            user_id: ID do usuario

        Returns:
            Dict com dados do usuario (name, email, role, department, etc.)
        """
        # Tenta buscar do banco real
        if self._db is not None:
            try:
                user_data = await self._load_from_database(user_id)
                if user_data:
                    logger.info(f"Usuario {user_id} carregado do banco: {user_data.get('name')}")
                    return user_data
                else:
                    logger.warning(f"Usuario {user_id} nao encontrado no banco, usando fallback")
            except Exception as e:
                logger.error(f"Erro ao buscar usuario {user_id} no banco: {e}")
                # Continua para fallback

        # Fallback: dados mock para desenvolvimento/testes
        return self._get_fallback_user_data(user_id)

    async def _load_from_database(self, user_id: int) -> Optional[dict]:
        """
        Consulta o modelo User real no banco de dados.

        Args:
            user_id: ID do usuario (pode ser int ou string UUID)

        Returns:
            Dict com dados mapeados ou None se nao encontrado
        """
        from core.models.user import User, UserRole as SystemUserRole, ROLE_HIERARCHY
        from uuid import UUID

        user = None

        # CORRECAO: Tenta primeiro como UUID direto
        try:
            user_uuid = UUID(str(user_id))
            query = select(User).where(
                User.id == user_uuid,
                User.is_active == True  # noqa: E712
            )
            result = await self._db.execute(query)
            user = result.scalar_one_or_none()

            if user:
                logger.info(f"Usuario encontrado por UUID: {user.name}")
                return self._map_user_to_dict(user)
        except (ValueError, TypeError):
            # Nao e um UUID valido, continua com estrategia numerica
            pass

        # Se user_id e int, busca por mapeamento numerico baseado em created_at
        if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
            user_id_int = int(user_id)

            # Busca todos usuarios ativos ordenados por created_at (mesma ordem que a UI)
            query = select(User).where(
                User.is_active == True  # noqa: E712
            ).order_by(User.created_at)

            result = await self._db.execute(query)
            users = result.scalars().all()

            # Mapeia user_id como posicao (1-indexed)
            if 0 < user_id_int <= len(users):
                user = users[user_id_int - 1]
                logger.info(f"Usuario encontrado por indice {user_id_int}: {user.name}")
            else:
                logger.warning(f"user_id {user_id_int} fora do range (1-{len(users)})")
                return None

        if user is None:
            logger.warning(f"Usuario {user_id} nao encontrado no banco")
            return None

        return self._map_user_to_dict(user)

    def _map_user_to_dict(self, user) -> dict:
        """Mapeia User do banco para dict de dados."""
        # Mapeia role do sistema para role do Bartolo
        bartolo_role = self._map_system_role_to_bartolo_role(user.role)

        # Determina departamento baseado no role
        department = self._infer_department_from_role(bartolo_role)

        # Determina se e manager baseado no role do sistema
        is_manager = self._is_manager_role(user.role)

        # Determina nivel de experiencia baseado no role
        experience_level = self._infer_experience_level(user.role)

        return {
            "name": user.name,
            "email": user.email,
            "role": bartolo_role,
            "department": department,
            "is_manager": is_manager,
            "experience_level": experience_level,
            "permissions": user.permissions or [],
            "preferences": {},
        }

    def _map_system_role_to_bartolo_role(self, system_role: str) -> str:
        """
        Mapeia o role do modelo User do sistema para o UserRole do Bartolo.

        O User.role usa valores como 'super_admin', 'admin', 'manager', etc.
        O Bartolo UserRole usa valores mais granulares como 'gerente_operacoes'.

        Args:
            system_role: Role do sistema (super_admin, admin, manager, etc.)

        Returns:
            String correspondente ao UserRole do Bartolo
        """
        role_mapping = {
            "super_admin": "admin",
            "admin": "admin",
            "manager": "gerente_geral",
            "supervisor": "supervisor_operacoes",
            "operator": "assistente_administrativo",
            "client": "assistente_administrativo",
            "viewer": "assistente_administrativo",
        }
        return role_mapping.get(system_role, "assistente_administrativo")

    def _infer_department_from_role(self, bartolo_role: str) -> str:
        """
        Infere o departamento baseado no role do Bartolo.

        Args:
            bartolo_role: Role do Bartolo

        Returns:
            String correspondente ao Department
        """
        profile = USER_PROFILES.get(None)
        # Busca no USER_PROFILES o departamento configurado
        for role_enum, profile_data in USER_PROFILES.items():
            if role_enum.value == bartolo_role:
                dept = profile_data.get("department")
                if dept:
                    return dept.value if hasattr(dept, 'value') else str(dept)
                break

        return "administrativo"

    def _is_manager_role(self, system_role: str) -> bool:
        """
        Determina se o role do sistema indica cargo de gestao.

        Args:
            system_role: Role do sistema

        Returns:
            True se o usuario e gestor
        """
        manager_roles = {"super_admin", "admin", "manager", "supervisor"}
        return system_role in manager_roles

    def _infer_experience_level(self, system_role: str) -> str:
        """
        Infere nivel de experiencia baseado no role do sistema.

        Args:
            system_role: Role do sistema

        Returns:
            Nivel: 'beginner', 'intermediate' ou 'advanced'
        """
        level_mapping = {
            "super_admin": "advanced",
            "admin": "advanced",
            "manager": "advanced",
            "supervisor": "intermediate",
            "operator": "intermediate",
            "client": "beginner",
            "viewer": "beginner",
        }
        return level_mapping.get(system_role, "intermediate")

    @staticmethod
    def _get_fallback_user_data(user_id: int) -> dict:
        """
        Retorna dados mock como fallback quando o banco nao esta disponivel.

        Args:
            user_id: ID do usuario

        Returns:
            Dict com dados mock do usuario
        """
        test_users = {
            1: {
                "name": "Admin",
                "email": "admin@conectapro.com.br",
                "role": "admin",
                "department": "ti",
                "is_manager": True,
                "experience_level": "advanced",
            },
            2: {
                "name": "Maria Silva",
                "email": "maria@conectapro.com.br",
                "role": "analista_comercial",
                "department": "comercial",
                "is_manager": False,
                "experience_level": "intermediate",
            },
            3: {
                "name": "Joao Santos",
                "email": "joao@conectapro.com.br",
                "role": "gerente_operacoes",
                "department": "operacoes",
                "is_manager": True,
                "experience_level": "advanced",
            },
        }

        return test_users.get(user_id, {
            "name": f"Usuario {user_id}",
            "email": f"user{user_id}@conectapro.com.br",
            "role": "assistente_administrativo",
            "department": "administrativo",
            "experience_level": "intermediate",
        })

    def _parse_role(self, role_str: Optional[str]) -> Optional[UserRole]:
        """Converte string para UserRole."""
        if not role_str:
            return None
        try:
            return UserRole(role_str.lower())
        except ValueError:
            return None

    def _parse_department(self, dept_str: Optional[str]) -> Optional[Department]:
        """Converte string para Department."""
        if not dept_str:
            return None
        try:
            return Department(dept_str.lower())
        except ValueError:
            return None

    async def update_user_preferences(
        self,
        user_id: int,
        preferences: dict,
    ) -> None:
        """Atualiza preferencias do usuario."""
        context = await self.get_user_context(user_id)
        context.preferences.update(preferences)

    async def add_recent_module(
        self,
        user_id: int,
        module: str,
    ) -> None:
        """Adiciona modulo aos recentes."""
        context = await self.get_user_context(user_id)

        # Remove se ja existe
        if module in context.last_modules:
            context.last_modules.remove(module)

        # Adiciona no inicio
        context.last_modules.insert(0, module)

        # Limita a 10
        context.last_modules = context.last_modules[:10]

    async def get_user_stats(self, user_id: int) -> dict:
        """Retorna estatisticas do usuario."""
        context = await self.get_user_context(user_id)

        return {
            "user_id": user_id,
            "name": context.name,
            "role": context.role.value if context.role else None,
            "department": context.department.value if context.department else None,
            "interaction_count": context.interaction_count,
            "first_interaction": context.first_interaction.isoformat() if context.first_interaction else None,
            "last_interaction": context.last_interaction.isoformat() if context.last_interaction else None,
            "recent_modules": context.last_modules[:5],
        }

    def clear_cache(self, user_id: Optional[int] = None) -> None:
        """Limpa cache de usuarios e timestamps."""
        if user_id:
            self._user_cache.pop(user_id, None)
            self._cache_timestamps.pop(user_id, None)
        else:
            self._user_cache.clear()
            self._cache_timestamps.clear()
