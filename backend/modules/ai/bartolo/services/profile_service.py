"""
Profile Service - Servico de Perfil do Usuario.

Gerencia contexto do usuario para personalizacao das respostas do Bartolo.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime

from modules.ai.bartolo.config.user_profiles import (
    UserRole,
    Department,
    USER_PROFILES,
    get_profile_context,
    get_profile_modules,
    get_communication_style,
)

logger = logging.getLogger(__name__)


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
    - Carregar dados do usuario
    - Manter contexto de interacoes
    - Adaptar respostas ao perfil
    """

    def __init__(self):
        """Inicializa o servico."""
        self._user_cache: dict[int, UserContext] = {}

    async def get_user_context(self, user_id: int) -> UserContext:
        """
        Recupera ou cria contexto do usuario.

        Args:
            user_id: ID do usuario

        Returns:
            UserContext com dados do usuario
        """
        # Verifica cache
        if user_id in self._user_cache:
            context = self._user_cache[user_id]
            context.last_interaction = datetime.utcnow()
            context.interaction_count += 1
            return context

        # Busca dados do usuario (simulado - integrar com DB)
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

        # Salva no cache
        self._user_cache[user_id] = context

        return context

    async def _load_user_data(self, user_id: int) -> dict:
        """
        Carrega dados do usuario do banco.

        TODO: Integrar com o modelo User do sistema.
        """
        # Simulacao - em producao, buscar do banco
        # Por enquanto retorna dados de teste
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
        """Limpa cache de usuarios."""
        if user_id:
            self._user_cache.pop(user_id, None)
        else:
            self._user_cache.clear()
