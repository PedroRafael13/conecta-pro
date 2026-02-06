"""Gerenciador de contexto para conversacoes."""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Optional
from uuid import UUID

import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Contexto de uma conversacao."""

    user_id: int
    session_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    module: Optional[str] = None
    entities: dict[str, Any] = field(default_factory=dict)
    preferences: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ContextManager:
    """
    Gerencia contexto das conversacoes usando Redis.

    Funcionalidades:
    - Armazenamento de historico de mensagens
    - Gerenciamento de contexto por sessao
    - Persistencia de entidades extraidas
    - Cache de preferencias do usuario
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        max_context_messages: int = 20,
        context_ttl_hours: int = 24,
    ) -> None:
        """
        Inicializa o gerenciador de contexto.

        Args:
            redis_client: Cliente Redis (opcional)
            max_context_messages: Maximo de mensagens no contexto
            context_ttl_hours: TTL do contexto em horas
        """
        self.redis = redis_client
        self.max_context_messages = max_context_messages
        self.context_ttl = context_ttl_hours * 3600  # Converte para segundos

        # Cache local para quando Redis nao esta disponivel
        self._local_cache: dict[str, ConversationContext] = {}

    def _get_context_key(self, user_id: int, session_id: str) -> str:
        """Gera chave para o contexto no Redis."""
        return f"chat_context:{user_id}:{session_id}"

    def _get_preferences_key(self, user_id: int) -> str:
        """Gera chave para preferencias do usuario."""
        return f"chat_preferences:{user_id}"

    def _get_entities_key(self, user_id: int, session_id: str) -> str:
        """Gera chave para entidades extraidas."""
        return f"chat_entities:{user_id}:{session_id}"

    async def get_context(
        self, user_id: int, session_id: str
    ) -> ConversationContext:
        """
        Recupera contexto da conversa.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao

        Returns:
            ConversationContext com dados da conversa
        """
        key = self._get_context_key(user_id, session_id)

        # Tenta buscar do Redis
        if self.redis:
            try:
                data = await self.redis.get(key)
                if data:
                    context_dict = json.loads(data)
                    return ConversationContext(
                        user_id=user_id,
                        session_id=session_id,
                        messages=context_dict.get("messages", []),
                        metadata=context_dict.get("metadata", {}),
                        module=context_dict.get("module"),
                        entities=context_dict.get("entities", {}),
                        preferences=context_dict.get("preferences", {}),
                    )
            except Exception as e:
                logger.warning(f"Erro ao buscar contexto do Redis: {e}")

        # Fallback para cache local
        if key in self._local_cache:
            return self._local_cache[key]

        # Retorna contexto vazio
        return ConversationContext(user_id=user_id, session_id=session_id)

    async def save_context(self, context: ConversationContext) -> None:
        """
        Salva contexto da conversa.

        Args:
            context: Contexto a ser salvo
        """
        key = self._get_context_key(context.user_id, context.session_id)

        context_dict = {
            "messages": context.messages[-self.max_context_messages :],
            "metadata": context.metadata,
            "module": context.module,
            "entities": context.entities,
            "preferences": context.preferences,
            "updated_at": datetime.now(UTC).isoformat(),
        }

        # Salva no Redis
        if self.redis:
            try:
                await self.redis.setex(
                    key, self.context_ttl, json.dumps(context_dict)
                )
            except Exception as e:
                logger.warning(f"Erro ao salvar contexto no Redis: {e}")

        # Salva no cache local como backup
        self._local_cache[key] = context

    async def add_message(
        self,
        user_id: int,
        session_id: str,
        role: str,  # "user" ou "assistant"
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ConversationContext:
        """
        Adiciona mensagem ao contexto.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            role: Papel (user/assistant)
            content: Conteudo da mensagem
            metadata: Metadados adicionais

        Returns:
            Contexto atualizado
        """
        context = await self.get_context(user_id, session_id)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }

        context.messages.append(message)
        context.updated_at = datetime.now(UTC)

        # Limita quantidade de mensagens
        if len(context.messages) > self.max_context_messages:
            context.messages = context.messages[-self.max_context_messages :]

        await self.save_context(context)
        return context

    async def update_entities(
        self,
        user_id: int,
        session_id: str,
        entities: dict[str, Any],
    ) -> None:
        """
        Atualiza entidades extraidas no contexto.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            entities: Entidades a adicionar/atualizar
        """
        context = await self.get_context(user_id, session_id)
        context.entities.update(entities)
        await self.save_context(context)

    async def set_module(
        self, user_id: int, session_id: str, module: str
    ) -> None:
        """
        Define o modulo ativo na conversa.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            module: Nome do modulo
        """
        context = await self.get_context(user_id, session_id)
        context.module = module
        await self.save_context(context)

    async def get_user_preferences(self, user_id: int) -> dict[str, Any]:
        """
        Recupera preferencias do usuario.

        Args:
            user_id: ID do usuario

        Returns:
            Dicionario com preferencias
        """
        key = self._get_preferences_key(user_id)

        if self.redis:
            try:
                data = await self.redis.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Erro ao buscar preferencias: {e}")

        return {}

    async def save_user_preferences(
        self, user_id: int, preferences: dict[str, Any]
    ) -> None:
        """
        Salva preferencias do usuario.

        Args:
            user_id: ID do usuario
            preferences: Preferencias a salvar
        """
        key = self._get_preferences_key(user_id)

        if self.redis:
            try:
                await self.redis.setex(
                    key,
                    self.context_ttl * 30,  # 30x mais tempo para preferencias
                    json.dumps(preferences),
                )
            except Exception as e:
                logger.warning(f"Erro ao salvar preferencias: {e}")

    async def clear_context(self, user_id: int, session_id: str) -> None:
        """
        Limpa contexto de uma sessao.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
        """
        key = self._get_context_key(user_id, session_id)

        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.warning(f"Erro ao limpar contexto: {e}")

        if key in self._local_cache:
            del self._local_cache[key]

    async def get_messages_for_llm(
        self,
        user_id: int,
        session_id: str,
        max_messages: int = 10,
    ) -> list[dict[str, str]]:
        """
        Recupera mensagens formatadas para envio ao LLM.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            max_messages: Maximo de mensagens a retornar

        Returns:
            Lista de mensagens no formato do LLM
        """
        context = await self.get_context(user_id, session_id)

        # Converte para formato do LLM
        llm_messages = []
        for msg in context.messages[-max_messages:]:
            llm_messages.append(
                {"role": msg["role"], "content": msg["content"]}
            )

        return llm_messages

    def get_system_prompt(
        self,
        context: ConversationContext,
        user_name: Optional[str] = None,
    ) -> str:
        """
        Gera prompt de sistema baseado no contexto.

        Args:
            context: Contexto da conversa
            user_name: Nome do usuario

        Returns:
            Prompt de sistema
        """
        parts = [
            "Voce e um assistente inteligente do sistema Conecta PRO.",
            "Responda de forma clara, objetiva e em portugues brasileiro.",
            "Seja prestativo e proativo em sugerir acoes.",
        ]

        if user_name:
            parts.append(f"O usuario se chama {user_name}.")

        if context.module:
            module_descriptions = {
                "crm": "O usuario esta no modulo de CRM (gestao de clientes e leads).",
                "financial": "O usuario esta no modulo Financeiro.",
                "hr": "O usuario esta no modulo de RH (Recursos Humanos).",
                "inventory": "O usuario esta no modulo de Estoque.",
            }
            if context.module in module_descriptions:
                parts.append(module_descriptions[context.module])

        if context.entities:
            parts.append(
                f"Entidades identificadas na conversa: {json.dumps(context.entities, ensure_ascii=False)}"
            )

        return "\n".join(parts)
