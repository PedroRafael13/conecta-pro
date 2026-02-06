"""Tests para ContextManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC

from modules.ai.conversation.services.context_manager import (
    ContextManager,
    ConversationContext,
)


@pytest.fixture
def context_manager():
    """Retorna instancia do gerenciador sem Redis."""
    return ContextManager(redis_client=None)


@pytest.fixture
def context_manager_with_redis():
    """Retorna instancia do gerenciador com Redis mockado."""
    mock_redis = AsyncMock()
    return ContextManager(redis_client=mock_redis)


class TestConversationContext:
    """Testes do dataclass ConversationContext."""

    def test_context_creation(self):
        """Testa criacao de contexto."""
        context = ConversationContext(
            user_id=1,
            session_id="test-session",
        )

        assert context.user_id == 1
        assert context.session_id == "test-session"
        assert context.messages == []
        assert context.metadata == {}
        assert context.module is None

    def test_context_with_messages(self):
        """Testa contexto com mensagens."""
        context = ConversationContext(
            user_id=1,
            session_id="test-session",
            messages=[
                {"role": "user", "content": "Oi"},
                {"role": "assistant", "content": "Olá!"},
            ],
        )

        assert len(context.messages) == 2
        assert context.messages[0]["role"] == "user"


class TestContextManager:
    """Testes do gerenciador de contexto."""

    def test_get_context_key(self, context_manager):
        """Testa geracao de chave."""
        key = context_manager._get_context_key(1, "session-123")

        assert key == "chat_context:1:session-123"

    def test_get_preferences_key(self, context_manager):
        """Testa chave de preferencias."""
        key = context_manager._get_preferences_key(1)

        assert key == "chat_preferences:1"

    @pytest.mark.asyncio
    async def test_get_context_empty(self, context_manager):
        """Testa busca de contexto vazio."""
        context = await context_manager.get_context(1, "new-session")

        assert isinstance(context, ConversationContext)
        assert context.user_id == 1
        assert context.session_id == "new-session"
        assert context.messages == []

    @pytest.mark.asyncio
    async def test_save_and_get_context_local(self, context_manager):
        """Testa salvar e recuperar contexto local."""
        context = ConversationContext(
            user_id=1,
            session_id="test-session",
            messages=[{"role": "user", "content": "Teste"}],
            module="crm",
        )

        await context_manager.save_context(context)

        # Recupera do cache local
        retrieved = await context_manager.get_context(1, "test-session")

        assert retrieved.user_id == 1
        assert retrieved.module == "crm"

    @pytest.mark.asyncio
    async def test_add_message(self, context_manager):
        """Testa adicionar mensagem."""
        context = await context_manager.add_message(
            user_id=1,
            session_id="test-session",
            role="user",
            content="Olá, tudo bem?",
        )

        assert len(context.messages) == 1
        assert context.messages[0]["role"] == "user"
        assert context.messages[0]["content"] == "Olá, tudo bem?"

    @pytest.mark.asyncio
    async def test_add_multiple_messages(self, context_manager):
        """Testa adicionar multiplas mensagens."""
        await context_manager.add_message(1, "session", "user", "Mensagem 1")
        await context_manager.add_message(1, "session", "assistant", "Resposta 1")
        context = await context_manager.add_message(1, "session", "user", "Mensagem 2")

        assert len(context.messages) == 3

    @pytest.mark.asyncio
    async def test_max_messages_limit(self, context_manager):
        """Testa limite maximo de mensagens."""
        context_manager.max_context_messages = 5

        for i in range(10):
            await context_manager.add_message(
                1, "session", "user", f"Mensagem {i}"
            )

        context = await context_manager.get_context(1, "session")

        # Deve manter apenas as ultimas 5
        assert len(context.messages) <= 5

    @pytest.mark.asyncio
    async def test_update_entities(self, context_manager):
        """Testa atualizacao de entidades."""
        await context_manager.update_entities(
            user_id=1,
            session_id="session",
            entities={"email": "test@test.com", "phone": "123456"},
        )

        context = await context_manager.get_context(1, "session")

        assert context.entities["email"] == "test@test.com"
        assert context.entities["phone"] == "123456"

    @pytest.mark.asyncio
    async def test_set_module(self, context_manager):
        """Testa definicao de modulo."""
        await context_manager.set_module(1, "session", "crm")

        context = await context_manager.get_context(1, "session")

        assert context.module == "crm"

    @pytest.mark.asyncio
    async def test_clear_context(self, context_manager):
        """Testa limpar contexto."""
        # Adiciona dados
        await context_manager.add_message(1, "session", "user", "Teste")

        # Limpa
        await context_manager.clear_context(1, "session")

        # Verifica que foi limpo (retorna novo contexto vazio)
        context = await context_manager.get_context(1, "session")

        # O cache local foi removido, entao retorna contexto vazio
        assert len(context.messages) == 0

    @pytest.mark.asyncio
    async def test_get_messages_for_llm(self, context_manager):
        """Testa formatacao de mensagens para LLM."""
        await context_manager.add_message(1, "session", "user", "Oi")
        await context_manager.add_message(1, "session", "assistant", "Olá!")
        await context_manager.add_message(1, "session", "user", "Tudo bem?")

        messages = await context_manager.get_messages_for_llm(1, "session")

        assert len(messages) == 3
        assert messages[0] == {"role": "user", "content": "Oi"}
        assert messages[1] == {"role": "assistant", "content": "Olá!"}

    @pytest.mark.asyncio
    async def test_get_messages_for_llm_limited(self, context_manager):
        """Testa limite de mensagens para LLM."""
        for i in range(15):
            await context_manager.add_message(1, "session", "user", f"Msg {i}")

        messages = await context_manager.get_messages_for_llm(1, "session", max_messages=5)

        assert len(messages) == 5

    def test_get_system_prompt_basic(self, context_manager):
        """Testa prompt de sistema basico."""
        context = ConversationContext(user_id=1, session_id="test")

        prompt = context_manager.get_system_prompt(context)

        assert "Conecta PRO" in prompt
        assert "portugues brasileiro" in prompt

    def test_get_system_prompt_with_user(self, context_manager):
        """Testa prompt com nome do usuario."""
        context = ConversationContext(user_id=1, session_id="test")

        prompt = context_manager.get_system_prompt(context, user_name="João")

        assert "João" in prompt

    def test_get_system_prompt_with_module(self, context_manager):
        """Testa prompt com modulo."""
        context = ConversationContext(user_id=1, session_id="test", module="crm")

        prompt = context_manager.get_system_prompt(context)

        assert "CRM" in prompt

    def test_get_system_prompt_with_entities(self, context_manager):
        """Testa prompt com entidades."""
        context = ConversationContext(
            user_id=1,
            session_id="test",
            entities={"email": "test@test.com"},
        )

        prompt = context_manager.get_system_prompt(context)

        assert "test@test.com" in prompt


class TestContextManagerWithRedis:
    """Testes com Redis mockado."""

    @pytest.mark.asyncio
    async def test_save_to_redis(self, context_manager_with_redis):
        """Testa salvamento no Redis."""
        context = ConversationContext(
            user_id=1,
            session_id="test",
            messages=[{"role": "user", "content": "Test"}],
        )

        await context_manager_with_redis.save_context(context)

        # Verifica que o Redis foi chamado
        context_manager_with_redis.redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_from_redis(self, context_manager_with_redis):
        """Testa busca do Redis."""
        import json

        context_data = {
            "messages": [{"role": "user", "content": "Test"}],
            "metadata": {},
            "module": "crm",
            "entities": {},
            "preferences": {},
        }

        context_manager_with_redis.redis.get.return_value = json.dumps(context_data)

        context = await context_manager_with_redis.get_context(1, "test")

        assert len(context.messages) == 1
        assert context.module == "crm"

    @pytest.mark.asyncio
    async def test_redis_error_fallback(self, context_manager_with_redis):
        """Testa fallback quando Redis falha."""
        context_manager_with_redis.redis.get.side_effect = Exception("Redis error")

        # Deve retornar contexto vazio sem erro
        context = await context_manager_with_redis.get_context(1, "test")

        assert context.user_id == 1
        assert context.messages == []

    @pytest.mark.asyncio
    async def test_clear_from_redis(self, context_manager_with_redis):
        """Testa limpeza do Redis."""
        await context_manager_with_redis.clear_context(1, "test")

        context_manager_with_redis.redis.delete.assert_called_once()
