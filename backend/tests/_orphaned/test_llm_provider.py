"""Tests para LLMProvider."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.ai.conversation.services.llm_provider import (
    ClaudeProvider,
    LLMModel,
    LLMProvider,
    LLMResponse,
    LocalFallbackProvider,
    OpenAIProvider,
)


class TestLLMModel:
    """Testes do enum de modelos."""

    def test_openai_models(self):
        """Testa modelos OpenAI."""
        assert LLMModel.GPT_4.value == "gpt-4"
        assert LLMModel.GPT_4_TURBO.value == "gpt-4-turbo-preview"
        assert LLMModel.GPT_35_TURBO.value == "gpt-3.5-turbo"

    def test_claude_models(self):
        """Testa modelos Claude."""
        assert LLMModel.CLAUDE_3_OPUS.value == "claude-3-opus-20240229"
        assert LLMModel.CLAUDE_3_SONNET.value == "claude-3-sonnet-20240229"
        assert LLMModel.CLAUDE_3_HAIKU.value == "claude-3-haiku-20240307"

    def test_local_model(self):
        """Testa modelo local."""
        assert LLMModel.LOCAL.value == "local"


class TestLLMResponse:
    """Testes do dataclass de resposta."""

    def test_response_creation(self):
        """Testa criacao de resposta."""
        response = LLMResponse(
            content="Olá!",
            model="gpt-4",
            tokens_used=100,
            prompt_tokens=50,
            completion_tokens=50,
            latency_ms=200,
        )

        assert response.content == "Olá!"
        assert response.model == "gpt-4"
        assert response.tokens_used == 100
        assert response.latency_ms == 200
        assert response.finish_reason == "stop"
        assert response.metadata == {}

    def test_response_with_metadata(self):
        """Testa resposta com metadata."""
        response = LLMResponse(
            content="Test",
            model="gpt-4",
            tokens_used=10,
            prompt_tokens=5,
            completion_tokens=5,
            latency_ms=100,
            metadata={"key": "value"},
        )

        assert response.metadata["key"] == "value"


class TestLocalFallbackProvider:
    """Testes do provider de fallback local."""

    @pytest.fixture
    def provider(self):
        """Retorna instancia do provider."""
        return LocalFallbackProvider()

    @pytest.mark.asyncio
    async def test_generate_greeting(self, provider):
        """Testa resposta de saudacao."""
        messages = [{"role": "user", "content": "Oi, tudo bem?"}]

        response = await provider.generate(messages)

        assert isinstance(response, LLMResponse)
        assert response.model == "local-fallback"
        assert "Ola" in response.content or "assistente" in response.content

    @pytest.mark.asyncio
    async def test_generate_help(self, provider):
        """Testa resposta de ajuda."""
        messages = [{"role": "user", "content": "Preciso de ajuda"}]

        response = await provider.generate(messages)

        assert "ajudar" in response.content.lower()

    @pytest.mark.asyncio
    async def test_generate_default(self, provider):
        """Testa resposta padrao."""
        messages = [{"role": "user", "content": "Qualquer coisa aleatória xyz"}]

        response = await provider.generate(messages)

        assert response.content is not None
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_generate_with_metadata(self, provider):
        """Testa metadata de fallback."""
        messages = [{"role": "user", "content": "Teste"}]

        response = await provider.generate(messages)

        assert response.metadata.get("fallback") is True

    @pytest.mark.asyncio
    async def test_generate_stream(self, provider):
        """Testa streaming de fallback."""
        messages = [{"role": "user", "content": "Oi"}]

        chunks = []
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk)

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0


class TestOpenAIProvider:
    """Testes do provider OpenAI."""

    @pytest.fixture
    def provider(self):
        """Retorna instancia do provider."""
        return OpenAIProvider(api_key="test-key")

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, provider):
        """Testa geracao com client mockado."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta do GPT"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        provider._client = mock_client

        messages = [{"role": "user", "content": "Teste"}]
        response = await provider.generate(messages)

        assert response.content == "Resposta do GPT"
        assert response.tokens_used == 100

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, provider):
        """Testa geracao com system prompt."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        provider._client = mock_client

        messages = [{"role": "user", "content": "Teste"}]
        await provider.generate(messages, system_prompt="Você é um assistente")

        # Verifica que o system prompt foi incluido
        call_args = mock_client.chat.completions.create.call_args
        formatted_messages = call_args.kwargs["messages"]
        assert formatted_messages[0]["role"] == "system"


class TestClaudeProvider:
    """Testes do provider Claude."""

    @pytest.fixture
    def provider(self):
        """Retorna instancia do provider."""
        return ClaudeProvider(api_key="test-key")

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, provider):
        """Testa geracao com client mockado."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Resposta do Claude"
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        provider._client = mock_client

        messages = [{"role": "user", "content": "Teste"}]
        response = await provider.generate(messages)

        assert response.content == "Resposta do Claude"
        assert response.tokens_used == 100


class TestLLMProvider:
    """Testes do provider principal."""

    def test_init_with_openai(self):
        """Testa inicializacao com OpenAI."""
        provider = LLMProvider(primary_provider="openai")

        assert "openai" in provider._providers
        assert "local" in provider._providers

    def test_init_with_claude(self):
        """Testa inicializacao com Claude."""
        provider = LLMProvider(primary_provider="claude")

        assert "claude" in provider._providers
        assert "local" in provider._providers

    def test_init_with_fallback_disabled(self):
        """Testa inicializacao sem fallback."""
        provider = LLMProvider(
            primary_provider="openai",
            fallback_enabled=False,
        )

        assert provider.fallback_enabled is False

    @pytest.mark.asyncio
    async def test_generate_uses_primary(self):
        """Testa que generate usa provider primario."""
        provider = LLMProvider(primary_provider="openai")

        # Mock do provider primario
        mock_response = LLMResponse(
            content="Resposta",
            model="gpt-4",
            tokens_used=100,
            prompt_tokens=50,
            completion_tokens=50,
            latency_ms=100,
        )
        provider._primary.generate = AsyncMock(return_value=mock_response)

        messages = [{"role": "user", "content": "Teste"}]
        response = await provider.generate(messages)

        assert response.content == "Resposta"
        provider._primary.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_fallback_on_error(self):
        """Testa fallback quando primario falha."""
        provider = LLMProvider(primary_provider="openai", fallback_enabled=True)

        # Mock do provider primario com erro
        provider._primary.generate = AsyncMock(side_effect=Exception("API Error"))

        messages = [{"role": "user", "content": "Oi"}]
        response = await provider.generate(messages, use_fallback=True)

        # Deve usar fallback local
        assert response.model == "local-fallback"

    @pytest.mark.asyncio
    async def test_generate_no_fallback_raises(self):
        """Testa que sem fallback propaga erro."""
        provider = LLMProvider(primary_provider="openai", fallback_enabled=False)

        provider._primary.generate = AsyncMock(side_effect=Exception("API Error"))

        messages = [{"role": "user", "content": "Teste"}]

        with pytest.raises(Exception):
            await provider.generate(messages, use_fallback=False)

    def test_get_available_models(self):
        """Testa lista de modelos disponiveis."""
        provider = LLMProvider()

        models = provider.get_available_models()

        assert "gpt-4" in models
        assert "claude-3-opus-20240229" in models
        assert "local" in models

    @pytest.mark.asyncio
    async def test_generate_stream_fallback(self):
        """Testa streaming com fallback."""
        provider = LLMProvider(primary_provider="openai", fallback_enabled=True)

        # Mock do streaming primario com erro
        async def mock_stream_error(*args, **kwargs):
            raise Exception("Stream Error")
            yield  # Nunca executado, mas necessario para ser generator

        provider._primary.generate_stream = mock_stream_error

        messages = [{"role": "user", "content": "Oi"}]

        chunks = []
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk)

        # Deve ter usado fallback
        assert len(chunks) > 0
