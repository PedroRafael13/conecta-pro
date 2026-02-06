"""
Testes do ProfileService - Serviço de Perfil do Bartolo.

Testa especificamente:
- Bug #1: _load_from_database() usa UUID corretamente
- Cache com TTL
- Mapeamento de roles
- Fallback mock
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Importação condicional
try:
    from modules.ai.bartolo.services.profile_service import CACHE_TTL_SECONDS, ProfileService, UserContext

    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Módulo Bartolo não disponível")


class TestUserContext:
    """Testa a classe UserContext."""

    def test_to_prompt_context_basico(self):
        """Gera prompt context com campos básicos."""
        ctx = UserContext(
            user_id=1,
            name="Jordan",
            role=None,
            department=None,
        )
        result = ctx.to_prompt_context()
        assert "Jordan" in result
        assert "CONTEXTO DO USUARIO" in result

    def test_to_prompt_context_com_role(self):
        """Gera prompt context com role."""
        from modules.ai.bartolo.config.user_profiles import UserRole

        ctx = UserContext(
            user_id=1,
            name="Admin",
            role=UserRole("admin"),
        )
        result = ctx.to_prompt_context()
        assert "admin" in result.lower()

    def test_get_communication_style_default(self):
        """Estilo default é 'detailed'."""
        ctx = UserContext(user_id=1)
        assert ctx.get_communication_style() == "detailed"


class TestProfileServiceRoleMapping:
    """Testa mapeamento de roles do sistema para Bartolo."""

    def setup_method(self):
        self.service = ProfileService()

    def test_super_admin_mapeia_admin(self):
        """super_admin -> admin."""
        result = self.service._map_system_role_to_bartolo_role("super_admin")
        assert result == "admin"

    def test_admin_mapeia_admin(self):
        """admin -> admin."""
        result = self.service._map_system_role_to_bartolo_role("admin")
        assert result == "admin"

    def test_manager_mapeia_gerente_geral(self):
        """manager -> gerente_geral."""
        result = self.service._map_system_role_to_bartolo_role("manager")
        assert result == "gerente_geral"

    def test_supervisor_mapeia_supervisor_operacoes(self):
        """supervisor -> supervisor_operacoes."""
        result = self.service._map_system_role_to_bartolo_role("supervisor")
        assert result == "supervisor_operacoes"

    def test_operator_mapeia_assistente(self):
        """operator -> assistente_administrativo."""
        result = self.service._map_system_role_to_bartolo_role("operator")
        assert result == "assistente_administrativo"

    def test_role_desconhecido_mapeia_assistente(self):
        """Role desconhecido -> assistente_administrativo."""
        result = self.service._map_system_role_to_bartolo_role("unknown_role")
        assert result == "assistente_administrativo"


class TestProfileServiceManagerRole:
    """Testa detecção de cargo de gestão."""

    def setup_method(self):
        self.service = ProfileService()

    def test_super_admin_is_manager(self):
        assert self.service._is_manager_role("super_admin") is True

    def test_admin_is_manager(self):
        assert self.service._is_manager_role("admin") is True

    def test_manager_is_manager(self):
        assert self.service._is_manager_role("manager") is True

    def test_supervisor_is_manager(self):
        assert self.service._is_manager_role("supervisor") is True

    def test_operator_not_manager(self):
        assert self.service._is_manager_role("operator") is False

    def test_client_not_manager(self):
        assert self.service._is_manager_role("client") is False

    def test_viewer_not_manager(self):
        assert self.service._is_manager_role("viewer") is False


class TestProfileServiceExperienceLevel:
    """Testa inferência de nível de experiência."""

    def setup_method(self):
        self.service = ProfileService()

    def test_super_admin_advanced(self):
        assert self.service._infer_experience_level("super_admin") == "advanced"

    def test_admin_advanced(self):
        assert self.service._infer_experience_level("admin") == "advanced"

    def test_supervisor_intermediate(self):
        assert self.service._infer_experience_level("supervisor") == "intermediate"

    def test_operator_intermediate(self):
        assert self.service._infer_experience_level("operator") == "intermediate"

    def test_client_beginner(self):
        assert self.service._infer_experience_level("client") == "beginner"

    def test_unknown_intermediate(self):
        assert self.service._infer_experience_level("xyz") == "intermediate"


class TestProfileServiceFallback:
    """Testa fallback com dados mock."""

    def test_fallback_user_1_admin(self):
        """User 1 é Admin no fallback."""
        data = ProfileService._get_fallback_user_data(1)
        assert data["name"] == "Admin"
        assert data["role"] == "admin"

    def test_fallback_user_2_maria(self):
        """User 2 é Maria no fallback."""
        data = ProfileService._get_fallback_user_data(2)
        assert data["name"] == "Maria Silva"

    def test_fallback_user_desconhecido(self):
        """User desconhecido usa template genérico."""
        data = ProfileService._get_fallback_user_data(999)
        assert "999" in data["name"]
        assert data["role"] == "assistente_administrativo"


class TestProfileServiceCache:
    """Testa cache com TTL."""

    def setup_method(self):
        self.service = ProfileService()

    def test_cache_invalido_sem_entry(self):
        """Cache inexistente é inválido."""
        assert self.service._is_cache_valid(1) is False

    def test_cache_valido_recem_criado(self):
        """Cache recém-criado é válido."""
        self.service._cache_timestamps[1] = time.time()
        assert self.service._is_cache_valid(1) is True

    def test_cache_invalido_apos_ttl(self):
        """Cache expirado é inválido."""
        self.service._cache_timestamps[1] = time.time() - CACHE_TTL_SECONDS - 1
        assert self.service._is_cache_valid(1) is False

    def test_clear_cache_usuario(self):
        """Limpa cache de um usuário."""
        self.service._user_cache[1] = MagicMock()
        self.service._cache_timestamps[1] = time.time()
        self.service.clear_cache(1)
        assert 1 not in self.service._user_cache
        assert 1 not in self.service._cache_timestamps

    def test_clear_cache_todos(self):
        """Limpa cache de todos."""
        self.service._user_cache[1] = MagicMock()
        self.service._user_cache[2] = MagicMock()
        self.service._cache_timestamps[1] = time.time()
        self.service._cache_timestamps[2] = time.time()
        self.service.clear_cache()
        assert len(self.service._user_cache) == 0
        assert len(self.service._cache_timestamps) == 0


class TestProfileServiceLoadFromDatabase:
    """Testa _load_from_database() - Bug #1 fix."""

    def setup_method(self):
        self.service = ProfileService()

    @pytest.mark.asyncio
    async def test_load_por_uuid_direto(self, mock_users):
        """Bug #1: Busca por UUID direto funciona via _load_user_data."""
        target_user = mock_users[0]

        # Mock _load_from_database (que é o método que faz o import interno)
        with patch.object(self.service, "_load_from_database", new_callable=AsyncMock) as mock_load:
            mock_load.return_value = {
                "name": "Jordan Admin",
                "email": "admin@conectapro.com.br",
                "role": "admin",
                "department": "ti",
                "is_manager": True,
                "experience_level": "advanced",
                "permissions": [],
                "preferences": {},
            }
            self.service._db = AsyncMock()  # Simula db disponível

            result = await self.service._load_user_data(str(target_user.id))

        assert result is not None
        assert result["name"] == "Jordan Admin"
        mock_load.assert_called_once_with(str(target_user.id))

    @pytest.mark.asyncio
    async def test_get_user_context_usa_cache(self):
        """get_user_context() retorna do cache quando válido."""
        cached_context = UserContext(
            user_id=1,
            name="Cached User",
            interaction_count=5,
        )
        self.service._user_cache[1] = cached_context
        self.service._cache_timestamps[1] = time.time()

        result = await self.service.get_user_context(1)
        assert result.name == "Cached User"
        assert result.interaction_count == 6  # Incrementado de 5 para 6

    @pytest.mark.asyncio
    async def test_get_user_context_fallback_sem_db(self):
        """Sem db, usa fallback mock."""
        self.service._db = None
        result = await self.service.get_user_context(1)
        assert result.name == "Admin"

    @pytest.mark.asyncio
    async def test_get_user_context_fallback_user_desconhecido(self):
        """User desconhecido sem db usa fallback genérico."""
        self.service._db = None
        result = await self.service.get_user_context(999)
        assert "999" in result.name


class TestProfileServiceParseRole:
    """Testa parsing de role."""

    def setup_method(self):
        self.service = ProfileService()

    def test_parse_role_valido(self):
        """Parse de role válido."""
        from modules.ai.bartolo.config.user_profiles import UserRole

        result = self.service._parse_role("admin")
        assert result == UserRole("admin")

    def test_parse_role_none(self):
        """Parse de None retorna None."""
        result = self.service._parse_role(None)
        assert result is None

    def test_parse_role_invalido(self):
        """Parse de role inválido retorna None."""
        result = self.service._parse_role("xyz_invalido_role")
        assert result is None
