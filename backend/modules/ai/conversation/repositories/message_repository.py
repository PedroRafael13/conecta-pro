"""Repository para ChatMessage."""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from modules.ai.conversation.models.chat_message import (
    ChatMessage,
    IntentCategory,
    MessageStatus,
    MessageType,
)

logger = logging.getLogger(__name__)


class ChatMessageRepository:
    """Repository para operacoes de ChatMessage."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao do banco de dados
        """
        self.db = db

    async def create(
        self,
        session_id: UUID,
        message_type: MessageType,
        content: str,
        intent: IntentCategory | None = None,
        intent_confidence: float | None = None,
        sentiment: str | None = None,
        entities: list[dict] | None = None,
        suggestions: list[dict] | None = None,
        actions: list[dict] | None = None,
        related_links: list[dict] | None = None,
        processing_time_ms: int | None = None,
        model_used: str | None = None,
        tokens_used: int | None = None,
        context_snapshot: dict | None = None,
    ) -> ChatMessage:
        """
        Cria nova mensagem.

        Args:
            session_id: ID da sessao
            message_type: Tipo da mensagem
            content: Conteudo
            intent: Intencao classificada
            intent_confidence: Confianca da intencao
            sentiment: Sentimento
            entities: Entidades extraidas
            suggestions: Sugestoes
            actions: Acoes
            related_links: Links relacionados
            processing_time_ms: Tempo de processamento
            model_used: Modelo usado
            tokens_used: Tokens utilizados
            context_snapshot: Snapshot do contexto

        Returns:
            ChatMessage criada
        """
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            intent=intent,
            intent_confidence=intent_confidence,
            sentiment=sentiment,
            entities=entities or [],
            suggestions=suggestions or [],
            actions=actions or [],
            related_links=related_links or [],
            processing_time_ms=processing_time_ms,
            model_used=model_used,
            tokens_used=tokens_used,
            context_snapshot=context_snapshot or {},
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        logger.debug(f"Mensagem criada: {message.id}")
        return message

    async def create_user_message(
        self,
        session_id: UUID,
        content: str,
        intent: IntentCategory | None = None,
        intent_confidence: float | None = None,
        entities: list[dict] | None = None,
    ) -> ChatMessage:
        """
        Cria mensagem do usuario.

        Args:
            session_id: ID da sessao
            content: Conteudo
            intent: Intencao
            intent_confidence: Confianca
            entities: Entidades

        Returns:
            ChatMessage do usuario
        """
        return await self.create(
            session_id=session_id,
            message_type=MessageType.USER,
            content=content,
            intent=intent,
            intent_confidence=intent_confidence,
            entities=entities,
        )

    async def create_assistant_message(
        self,
        session_id: UUID,
        content: str,
        suggestions: list[dict] | None = None,
        actions: list[dict] | None = None,
        related_links: list[dict] | None = None,
        processing_time_ms: int | None = None,
        model_used: str | None = None,
        tokens_used: int | None = None,
    ) -> ChatMessage:
        """
        Cria mensagem do assistente.

        Args:
            session_id: ID da sessao
            content: Conteudo
            suggestions: Sugestoes
            actions: Acoes
            related_links: Links
            processing_time_ms: Tempo
            model_used: Modelo
            tokens_used: Tokens

        Returns:
            ChatMessage do assistente
        """
        return await self.create(
            session_id=session_id,
            message_type=MessageType.ASSISTANT,
            content=content,
            suggestions=suggestions,
            actions=actions,
            related_links=related_links,
            processing_time_ms=processing_time_ms,
            model_used=model_used,
            tokens_used=tokens_used,
        )

    async def get_by_id(self, message_id: UUID) -> ChatMessage | None:
        """
        Busca mensagem por ID.

        Args:
            message_id: ID da mensagem

        Returns:
            ChatMessage ou None
        """
        result = await self.db.execute(select(ChatMessage).where(ChatMessage.id == message_id))
        return result.scalar_one_or_none()

    async def get_by_session(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 50,
        order_asc: bool = True,
    ) -> list[ChatMessage]:
        """
        Lista mensagens de uma sessao.

        Args:
            session_id: ID da sessao
            skip: Offset
            limit: Limite
            order_asc: Ordenar ascendente (mais antigas primeiro)

        Returns:
            Lista de mensagens
        """
        query = select(ChatMessage).where(ChatMessage.session_id == session_id)

        if order_asc:
            query = query.order_by(ChatMessage.created_at)
        else:
            query = query.order_by(desc(ChatMessage.created_at))

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_session(self, session_id: UUID) -> int:
        """
        Conta mensagens de uma sessao.

        Args:
            session_id: ID da sessao

        Returns:
            Total de mensagens
        """
        result = await self.db.execute(select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id))
        return result.scalar() or 0

    async def get_last_messages(
        self,
        session_id: UUID,
        count: int = 10,
    ) -> list[ChatMessage]:
        """
        Retorna ultimas N mensagens.

        Args:
            session_id: ID da sessao
            count: Quantidade

        Returns:
            Lista de mensagens
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(count)
        )

        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        # Retorna em ordem cronologica
        return list(reversed(messages))

    async def update_feedback(
        self,
        message_id: UUID,
        user_rating: int | None = None,
        was_helpful: bool | None = None,
        user_feedback: str | None = None,
    ) -> ChatMessage | None:
        """
        Atualiza feedback de uma mensagem.

        Args:
            message_id: ID da mensagem
            user_rating: Rating (1-5)
            was_helpful: Foi util
            user_feedback: Texto de feedback

        Returns:
            Mensagem atualizada
        """
        message = await self.get_by_id(message_id)
        if not message:
            return None

        if user_rating is not None:
            message.user_rating = user_rating
        if was_helpful is not None:
            message.was_helpful = was_helpful
        if user_feedback is not None:
            message.user_feedback = user_feedback

        message.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def update_status(
        self,
        message_id: UUID,
        status: MessageStatus,
        error_message: str | None = None,
    ) -> ChatMessage | None:
        """
        Atualiza status de uma mensagem.

        Args:
            message_id: ID da mensagem
            status: Novo status
            error_message: Mensagem de erro

        Returns:
            Mensagem atualizada
        """
        message = await self.get_by_id(message_id)
        if not message:
            return None

        message.status = status
        if error_message:
            message.error_message = error_message
        message.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def delete(self, message_id: UUID) -> bool:
        """
        Remove mensagem.

        Args:
            message_id: ID da mensagem

        Returns:
            True se removida
        """
        message = await self.get_by_id(message_id)
        if not message:
            return False

        await self.db.delete(message)
        await self.db.commit()

        return True

    async def delete_by_session(self, session_id: UUID) -> int:
        """
        Remove todas as mensagens de uma sessao.

        Args:
            session_id: ID da sessao

        Returns:
            Quantidade removida
        """
        result = await self.db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id))
        messages = list(result.scalars().all())

        count = len(messages)
        for msg in messages:
            await self.db.delete(msg)

        await self.db.commit()
        return count

    async def get_messages_for_llm(
        self,
        session_id: UUID,
        max_messages: int = 10,
    ) -> list[dict[str, str]]:
        """
        Retorna mensagens formatadas para LLM.

        Args:
            session_id: ID da sessao
            max_messages: Maximo de mensagens

        Returns:
            Lista de dicts com role e content
        """
        messages = await self.get_last_messages(session_id, max_messages)

        return [
            {
                "role": "user" if msg.message_type == MessageType.USER else "assistant",
                "content": msg.content,
            }
            for msg in messages
        ]

    async def get_stats_by_session(self, session_id: UUID) -> dict[str, Any]:
        """
        Retorna estatisticas de uma sessao.

        Args:
            session_id: ID da sessao

        Returns:
            Dicionario com estatisticas
        """
        messages = await self.get_by_session(session_id, limit=1000)

        if not messages:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "avg_response_time_ms": 0,
                "total_tokens": 0,
                "helpful_count": 0,
                "unhelpful_count": 0,
            }

        user_count = sum(1 for m in messages if m.message_type == MessageType.USER)
        assistant_count = len(messages) - user_count

        response_times = [m.processing_time_ms for m in messages if m.processing_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        total_tokens = sum(m.tokens_used or 0 for m in messages)

        helpful_count = sum(1 for m in messages if m.was_helpful is True)
        unhelpful_count = sum(1 for m in messages if m.was_helpful is False)

        return {
            "total_messages": len(messages),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "avg_response_time_ms": round(avg_response_time, 2),
            "total_tokens": total_tokens,
            "helpful_count": helpful_count,
            "unhelpful_count": unhelpful_count,
        }

    async def get_intent_distribution(
        self,
        session_id: UUID | None = None,
        user_id: int | None = None,
    ) -> dict[str, int]:
        """
        Retorna distribuicao de intencoes.

        Args:
            session_id: ID da sessao (opcional)
            user_id: ID do usuario (opcional)

        Returns:
            Dicionario intent -> count
        """
        query = select(
            ChatMessage.intent,
            func.count(ChatMessage.id).label("count"),
        ).where(ChatMessage.intent.isnot(None))

        if session_id:
            query = query.where(ChatMessage.session_id == session_id)

        query = query.group_by(ChatMessage.intent)

        result = await self.db.execute(query)
        rows = result.all()

        return {row.intent.value if row.intent else "unknown": row.count for row in rows}

    async def search_messages(
        self,
        session_id: UUID,
        query: str,
        limit: int = 20,
    ) -> list[ChatMessage]:
        """
        Busca mensagens por texto.

        Args:
            session_id: ID da sessao
            query: Texto de busca
            limit: Limite

        Returns:
            Lista de mensagens
        """
        search_query = select(ChatMessage).where(
            and_(
                ChatMessage.session_id == session_id,
                ChatMessage.content.ilike(f"%{query}%"),
            )
        )

        search_query = search_query.order_by(desc(ChatMessage.created_at)).limit(limit)

        result = await self.db.execute(search_query)
        return list(result.scalars().all())
