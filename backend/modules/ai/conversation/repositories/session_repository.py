"""Repository para ChatSession."""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from modules.ai.conversation.models.chat_session import ChatSession

logger = logging.getLogger(__name__)


class ChatSessionRepository:
    """Repository para operacoes de ChatSession."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o repository.

        Args:
            db: Sessao do banco de dados
        """
        self.db = db

    async def create(
        self,
        user_id: int,
        title: str = "Nova Conversa",
        description: str | None = None,
        module_context: str | None = None,
        initial_context: dict | None = None,
        tags: list[str] | None = None,
    ) -> ChatSession:
        """
        Cria nova sessao de chat.

        Args:
            user_id: ID do usuario
            title: Titulo da sessao
            description: Descricao
            module_context: Modulo de contexto
            initial_context: Contexto inicial
            tags: Tags

        Returns:
            ChatSession criada
        """
        session = ChatSession(
            user_id=user_id,
            title=title,
            description=description,
            module_context=module_context,
            context_data=initial_context or {},
            tags=tags or [],
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        logger.info(f"Sessao criada: {session.id}")
        return session

    async def get_by_id(self, session_id: UUID) -> ChatSession | None:
        """
        Busca sessao por ID.

        Args:
            session_id: ID da sessao

        Returns:
            ChatSession ou None
        """
        result = await self.db.execute(select(ChatSession).where(ChatSession.id == session_id))
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: int,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ChatSession]:
        """
        Lista sessoes de um usuario.

        Args:
            user_id: ID do usuario
            include_archived: Incluir arquivadas
            skip: Offset
            limit: Limite

        Returns:
            Lista de sessoes
        """
        query = select(ChatSession).where(ChatSession.user_id == user_id)

        if not include_archived:
            query = query.where(not ChatSession.is_archived)

        query = (
            query.order_by(desc(ChatSession.is_pinned))
            .order_by(desc(ChatSession.last_message_at))
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: int, include_archived: bool = False) -> int:
        """
        Conta sessoes de um usuario.

        Args:
            user_id: ID do usuario
            include_archived: Incluir arquivadas

        Returns:
            Total de sessoes
        """
        query = select(func.count(ChatSession.id)).where(ChatSession.user_id == user_id)

        if not include_archived:
            query = query.where(not ChatSession.is_archived)

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(
        self,
        session_id: UUID,
        **kwargs,
    ) -> ChatSession | None:
        """
        Atualiza sessao.

        Args:
            session_id: ID da sessao
            **kwargs: Campos a atualizar

        Returns:
            Sessao atualizada ou None
        """
        session = await self.get_by_id(session_id)
        if not session:
            return None

        allowed_fields = {
            "title",
            "description",
            "module_context",
            "context_data",
            "is_pinned",
            "is_archived",
            "is_active",
            "tags",
        }

        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(session, key):
                setattr(session, key, value)

        session.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def increment_message_count(self, session_id: UUID) -> None:
        """
        Incrementa contador de mensagens.

        Args:
            session_id: ID da sessao
        """
        session = await self.get_by_id(session_id)
        if session:
            session.message_count += 1
            session.last_message_at = datetime.now(UTC)
            await self.db.commit()

    async def archive(self, session_id: UUID) -> ChatSession | None:
        """
        Arquiva sessao.

        Args:
            session_id: ID da sessao

        Returns:
            Sessao arquivada
        """
        return await self.update(session_id, is_archived=True, is_active=False)

    async def unarchive(self, session_id: UUID) -> ChatSession | None:
        """
        Desarquiva sessao.

        Args:
            session_id: ID da sessao

        Returns:
            Sessao desarquivada
        """
        return await self.update(session_id, is_archived=False, is_active=True)

    async def pin(self, session_id: UUID) -> ChatSession | None:
        """
        Fixa sessao.

        Args:
            session_id: ID da sessao

        Returns:
            Sessao fixada
        """
        return await self.update(session_id, is_pinned=True)

    async def unpin(self, session_id: UUID) -> ChatSession | None:
        """
        Remove fixacao.

        Args:
            session_id: ID da sessao

        Returns:
            Sessao desfixada
        """
        return await self.update(session_id, is_pinned=False)

    async def delete(self, session_id: UUID) -> bool:
        """
        Remove sessao (soft delete via archive).

        Args:
            session_id: ID da sessao

        Returns:
            True se removida
        """
        session = await self.get_by_id(session_id)
        if not session:
            return False

        session.is_active = False
        session.is_archived = True
        session.updated_at = datetime.now(UTC)

        await self.db.commit()
        return True

    async def hard_delete(self, session_id: UUID) -> bool:
        """
        Remove sessao permanentemente.

        Args:
            session_id: ID da sessao

        Returns:
            True se removida
        """
        session = await self.get_by_id(session_id)
        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()

        logger.info(f"Sessao deletada permanentemente: {session_id}")
        return True

    async def search(
        self,
        user_id: int,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ChatSession]:
        """
        Busca sessoes por texto.

        Args:
            user_id: ID do usuario
            query: Texto de busca
            skip: Offset
            limit: Limite

        Returns:
            Lista de sessoes
        """
        search_query = select(ChatSession).where(
            and_(
                ChatSession.user_id == user_id,
                not ChatSession.is_archived,
                or_(
                    ChatSession.title.ilike(f"%{query}%"),
                    ChatSession.description.ilike(f"%{query}%"),
                ),
            )
        )

        search_query = search_query.order_by(desc(ChatSession.last_message_at)).offset(skip).limit(limit)

        result = await self.db.execute(search_query)
        return list(result.scalars().all())

    async def get_active_sessions(
        self,
        user_id: int,
        hours: int = 24,
    ) -> list[ChatSession]:
        """
        Retorna sessoes ativas nas ultimas X horas.

        Args:
            user_id: ID do usuario
            hours: Horas para considerar

        Returns:
            Lista de sessoes ativas
        """
        from datetime import timedelta

        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        query = select(ChatSession).where(
            and_(
                ChatSession.user_id == user_id,
                ChatSession.is_active,
                ChatSession.last_message_at >= cutoff,
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_or_create(
        self,
        user_id: int,
        session_id: UUID | None = None,
        title: str = "Nova Conversa",
    ) -> ChatSession:
        """
        Retorna sessao existente ou cria nova.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao (opcional)
            title: Titulo para nova sessao

        Returns:
            ChatSession
        """
        if session_id:
            session = await self.get_by_id(session_id)
            if session and session.user_id == user_id:
                return session

        return await self.create(user_id=user_id, title=title)

    async def get_stats(self, user_id: int) -> dict:
        """
        Retorna estatisticas das sessoes do usuario.

        Args:
            user_id: ID do usuario

        Returns:
            Dicionario com estatisticas
        """
        # Total de sessoes
        total_query = select(func.count(ChatSession.id)).where(ChatSession.user_id == user_id)
        total = (await self.db.execute(total_query)).scalar() or 0

        # Sessoes ativas
        active_query = select(func.count(ChatSession.id)).where(
            and_(
                ChatSession.user_id == user_id,
                ChatSession.is_active,
                not ChatSession.is_archived,
            )
        )
        active = (await self.db.execute(active_query)).scalar() or 0

        # Total de mensagens
        messages_query = select(func.sum(ChatSession.message_count)).where(ChatSession.user_id == user_id)
        messages = (await self.db.execute(messages_query)).scalar() or 0

        return {
            "total_sessions": total,
            "active_sessions": active,
            "archived_sessions": total - active,
            "total_messages": messages,
        }
