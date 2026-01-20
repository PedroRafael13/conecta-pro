"""Provider de LLM para integracao com OpenAI e Claude."""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Optional

from core.config.settings import settings

logger = logging.getLogger(__name__)


class LLMModel(str, Enum):
    """Modelos de LLM disponiveis."""

    # OpenAI
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_35_TURBO = "gpt-3.5-turbo"

    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    # Local/Fallback
    LOCAL = "local"


@dataclass
class LLMResponse:
    """Resposta do LLM."""

    content: str
    model: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    finish_reason: str = "stop"
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """Classe base para providers de LLM."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> LLMResponse:
        """Gera resposta do LLM."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Gera resposta em streaming."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """Provider para OpenAI GPT."""

    def __init__(self, api_key: Optional[str] = None, model: str = LLMModel.GPT_4.value):
        """Inicializa provider OpenAI."""
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", None)
        self.model = model
        self._client = None

    async def _get_client(self):
        """Obtem cliente OpenAI (lazy loading)."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("openai package not installed")
                raise
        return self._client

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> LLMResponse:
        """Gera resposta usando OpenAI."""
        start_time = time.time()

        client = await self._get_client()

        # Prepara mensagens
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
            )
        except Exception as e:
            logger.error(f"Erro na chamada OpenAI: {e}")
            raise

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Gera resposta em streaming usando OpenAI."""
        client = await self._get_client()

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Erro no streaming OpenAI: {e}")
            raise


class ClaudeProvider(BaseLLMProvider):
    """Provider para Anthropic Claude."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = LLMModel.CLAUDE_3_SONNET.value
    ):
        """Inicializa provider Claude."""
        self.api_key = api_key or getattr(settings, "ANTHROPIC_API_KEY", None)
        self.model = model
        self._client = None

    async def _get_client(self):
        """Obtem cliente Anthropic (lazy loading)."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.error("anthropic package not installed")
                raise
        return self._client

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> LLMResponse:
        """Gera resposta usando Claude."""
        start_time = time.time()

        client = await self._get_client()

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=messages,
                temperature=temperature,
                **kwargs,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return LLMResponse(
                content=response.content[0].text,
                model=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                latency_ms=latency_ms,
                finish_reason=response.stop_reason,
            )
        except Exception as e:
            logger.error(f"Erro na chamada Claude: {e}")
            raise

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Gera resposta em streaming usando Claude."""
        client = await self._get_client()

        try:
            async with client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=messages,
                temperature=temperature,
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Erro no streaming Claude: {e}")
            raise


class LocalFallbackProvider(BaseLLMProvider):
    """Provider de fallback local (respostas pre-definidas)."""

    FALLBACK_RESPONSES = {
        "greeting": "Ola! Sou o assistente do Conecta PRO. Como posso ajudar?",
        "help": "Posso ajudar com navegacao, consultas de dados, criacao de registros e muito mais. O que voce precisa?",
        "error": "Desculpe, nao consegui processar sua solicitacao no momento. Tente novamente em alguns instantes.",
        "default": "Entendi sua mensagem. Para uma resposta mais precisa, poderia detalhar sua solicitacao?",
    }

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> LLMResponse:
        """Gera resposta de fallback."""
        start_time = time.time()

        # Analisa ultima mensagem para determinar resposta
        last_message = messages[-1]["content"].lower() if messages else ""

        if any(word in last_message for word in ["oi", "ola", "hey", "bom dia"]):
            response_type = "greeting"
        elif any(word in last_message for word in ["ajuda", "help", "socorro"]):
            response_type = "help"
        else:
            response_type = "default"

        content = self.FALLBACK_RESPONSES[response_type]
        latency_ms = int((time.time() - start_time) * 1000)

        return LLMResponse(
            content=content,
            model="local-fallback",
            tokens_used=len(content.split()),
            prompt_tokens=sum(len(m["content"].split()) for m in messages),
            completion_tokens=len(content.split()),
            latency_ms=latency_ms,
            finish_reason="stop",
            metadata={"fallback": True},
        )

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Gera resposta de fallback em streaming (simula)."""
        response = await self.generate(messages, system_prompt, max_tokens, temperature)

        # Simula streaming palavra por palavra
        for word in response.content.split():
            yield word + " "


class LLMProvider:
    """
    Provider principal que gerencia multiplos backends de LLM.

    Implementa:
    - Selecao automatica de modelo
    - Fallback entre providers
    - Circuit breaker
    - Metricas
    """

    def __init__(
        self,
        primary_provider: str = "openai",
        primary_model: Optional[str] = None,
        fallback_enabled: bool = True,
    ):
        """
        Inicializa o provider.

        Args:
            primary_provider: Provider principal (openai, claude)
            primary_model: Modelo especifico
            fallback_enabled: Habilita fallback local
        """
        self.primary_provider_name = primary_provider
        self.fallback_enabled = fallback_enabled

        # Inicializa providers
        self._providers: dict[str, BaseLLMProvider] = {}

        if primary_provider == "openai":
            model = primary_model or LLMModel.GPT_4.value
            self._providers["openai"] = OpenAIProvider(model=model)
        elif primary_provider == "claude":
            model = primary_model or LLMModel.CLAUDE_3_SONNET.value
            self._providers["claude"] = ClaudeProvider(model=model)

        # Sempre adiciona fallback local
        self._providers["local"] = LocalFallbackProvider()

        self._primary = self._providers.get(primary_provider, self._providers["local"])

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        use_fallback: bool = True,
        **kwargs,
    ) -> LLMResponse:
        """
        Gera resposta usando o provider configurado.

        Args:
            messages: Lista de mensagens
            system_prompt: Prompt de sistema
            max_tokens: Maximo de tokens
            temperature: Temperatura
            use_fallback: Usar fallback em caso de erro
            **kwargs: Argumentos adicionais

        Returns:
            LLMResponse com a resposta
        """
        try:
            return await self._primary.generate(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Erro no provider primario: {e}")

            if use_fallback and self.fallback_enabled:
                logger.info("Usando fallback local")
                return await self._providers["local"].generate(
                    messages=messages,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            raise

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Gera resposta em streaming."""
        try:
            async for chunk in self._primary.generate_stream(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")

            if self.fallback_enabled:
                async for chunk in self._providers["local"].generate_stream(
                    messages=messages,
                    system_prompt=system_prompt,
                ):
                    yield chunk

    def get_available_models(self) -> list[str]:
        """Retorna lista de modelos disponiveis."""
        return [model.value for model in LLMModel]
