"""Controller de Chat - Endpoints da API de IA Conversacional."""

import logging
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_active_user
from core.database.session import get_db
from modules.ai.conversation.models.chat_message import IntentCategory, MessageType
from modules.ai.conversation.repositories.message_repository import (
    ChatMessageRepository,
)
from modules.ai.conversation.repositories.session_repository import (
    ChatSessionRepository,
)
from modules.ai.conversation.schemas.chat_schemas import (
    ActionItem,
    AIConfigResponse,
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
    ChatSessionUpdate,
    ConversationStats,
    MessageFeedback,
    SendMessageRequest,
    SendMessageResponse,
    SuggestionItem,
)
from modules.ai.conversation.services.conversation_engine import ConversationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat - IA Conversacional"])


# ==============================================================================
# DEPENDENCIAS
# ==============================================================================


async def get_session_repository(
    db: AsyncSession = Depends(get_db),
) -> ChatSessionRepository:
    """Retorna instancia do repository de sessoes."""
    return ChatSessionRepository(db)


async def get_message_repository(
    db: AsyncSession = Depends(get_db),
) -> ChatMessageRepository:
    """Retorna instancia do repository de mensagens."""
    return ChatMessageRepository(db)


async def get_conversation_engine() -> ConversationEngine:
    """Retorna instancia do motor de conversacao."""
    return ConversationEngine()


# ==============================================================================
# ENDPOINTS DE SESSAO
# ==============================================================================


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar sessao de chat",
    description="Cria uma nova sessao de conversa para o usuario.",
)
async def create_session(
    data: ChatSessionCreate,
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionResponse:
    """Cria nova sessao de chat."""
    try:
        session = await repo.create(
            user_id=current_user.id,
            title=data.title,
            description=data.description,
            module_context=data.module_context,
            initial_context=data.initial_context,
            tags=data.tags,
        )

        logger.info(f"Sessao criada: {session.id} para usuario {current_user.id}")
        return ChatSessionResponse.model_validate(session)

    except Exception as e:
        logger.error(f"Erro ao criar sessao: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar sessao de chat",
        )


@router.get(
    "/sessions",
    response_model=ChatSessionListResponse,
    summary="Listar sessoes",
    description="Lista todas as sessoes de chat do usuario.",
)
async def list_sessions(
    page: int = Query(1, ge=1, description="Pagina"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por pagina"),
    include_archived: bool = Query(False, description="Incluir arquivadas"),
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionListResponse:
    """Lista sessoes do usuario."""
    try:
        skip = (page - 1) * page_size

        sessions = await repo.get_by_user(
            user_id=current_user.id,
            include_archived=include_archived,
            skip=skip,
            limit=page_size + 1,  # +1 para verificar has_more
        )

        has_more = len(sessions) > page_size
        if has_more:
            sessions = sessions[:page_size]

        total = await repo.count_by_user(
            user_id=current_user.id,
            include_archived=include_archived,
        )

        return ChatSessionListResponse(
            sessions=[ChatSessionResponse.model_validate(s) for s in sessions],
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more,
        )

    except Exception as e:
        logger.error(f"Erro ao listar sessoes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar sessoes",
        )


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    summary="Obter sessao",
    description="Retorna detalhes de uma sessao especifica.",
)
async def get_session(
    session_id: UUID,
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionResponse:
    """Retorna sessao por ID."""
    session = await repo.get_by_id(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessao nao encontrada",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )

    return ChatSessionResponse.model_validate(session)


@router.patch(
    "/sessions/{session_id}",
    response_model=ChatSessionResponse,
    summary="Atualizar sessao",
    description="Atualiza dados de uma sessao.",
)
async def update_session(
    session_id: UUID,
    data: ChatSessionUpdate,
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionResponse:
    """Atualiza sessao."""
    session = await repo.get_by_id(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessao nao encontrada",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )

    update_data = data.model_dump(exclude_unset=True)
    updated = await repo.update(session_id, **update_data)

    return ChatSessionResponse.model_validate(updated)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Arquivar sessao",
    description="Arquiva uma sessao (soft delete).",
)
async def delete_session(
    session_id: UUID,
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> None:
    """Arquiva sessao."""
    session = await repo.get_by_id(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessao nao encontrada",
        )

    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado",
        )

    await repo.archive(session_id)
    logger.info(f"Sessao arquivada: {session_id}")


@router.post(
    "/sessions/{session_id}/pin",
    response_model=ChatSessionResponse,
    summary="Fixar sessao",
    description="Fixa uma sessao no topo da lista.",
)
async def pin_session(
    session_id: UUID,
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionResponse:
    """Fixa sessao."""
    session = await repo.get_by_id(session_id)

    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessao nao encontrada",
        )

    updated = await repo.pin(session_id)
    return ChatSessionResponse.model_validate(updated)


@router.delete(
    "/sessions/{session_id}/pin",
    response_model=ChatSessionResponse,
    summary="Desafixar sessao",
    description="Remove fixacao da sessao.",
)
async def unpin_session(
    session_id: UUID,
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionResponse:
    """Remove fixacao."""
    session = await repo.get_by_id(session_id)

    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessao nao encontrada",
        )

    updated = await repo.unpin(session_id)
    return ChatSessionResponse.model_validate(updated)


# ==============================================================================
# ENDPOINTS DE MENSAGEM
# ==============================================================================


@router.post(
    "/send",
    response_model=SendMessageResponse,
    summary="Enviar mensagem",
    description="Envia uma mensagem e recebe resposta da IA.",
)
async def send_message(
    data: SendMessageRequest,
    current_user=Depends(get_current_active_user),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: ChatMessageRepository = Depends(get_message_repository),
    engine: ConversationEngine = Depends(get_conversation_engine),
) -> SendMessageResponse:
    """Envia mensagem e recebe resposta."""
    try:
        # Obtem ou cria sessao
        session = await session_repo.get_or_create(
            user_id=current_user.id,
            session_id=data.session_id,
            title=data.message[:50] + "..." if len(data.message) > 50 else data.message,
        )

        # Processa mensagem
        result = await engine.process_message(
            user_id=current_user.id,
            session_id=str(session.id),
            message=data.message,
            user_name=getattr(current_user, "nome", None),
            context_data=data.context,
        )

        # Salva mensagem do usuario
        await message_repo.create_user_message(
            session_id=session.id,
            content=data.message,
            intent=result.intent,
            intent_confidence=result.intent_confidence,
            entities=[{"name": k, "value": v} for k, v in result.entities.items()],
        )

        # Salva resposta do assistente
        await message_repo.create_assistant_message(
            session_id=session.id,
            content=result.response,
            suggestions=result.suggestions,
            actions=result.actions,
            processing_time_ms=result.processing_time_ms,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
        )

        # Atualiza contador da sessao
        await session_repo.increment_message_count(session.id)
        await session_repo.increment_message_count(session.id)

        return SendMessageResponse(
            message_id=result.message_id,
            session_id=session.id,
            response=result.response,
            response_html=result.response_html,
            intent=result.intent.value,
            intent_confidence=result.intent_confidence,
            suggestions=[SuggestionItem(**s) for s in result.suggestions],
            actions=[ActionItem(**a) for a in result.actions],
            processing_time_ms=result.processing_time_ms,
            model_used=result.model_used,
            tokens_used=result.tokens_used,
        )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar mensagem",
        )


@router.post(
    "/send/stream",
    summary="Enviar mensagem (streaming)",
    description="Envia mensagem e recebe resposta em streaming.",
)
async def send_message_stream(
    data: SendMessageRequest,
    current_user=Depends(get_current_active_user),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    engine: ConversationEngine = Depends(get_conversation_engine),
) -> StreamingResponse:
    """Envia mensagem com streaming."""

    async def generate():
        try:
            session = await session_repo.get_or_create(
                user_id=current_user.id,
                session_id=data.session_id,
            )

            async for chunk in engine.process_message_stream(
                user_id=current_user.id,
                session_id=str(session.id),
                message=data.message,
                user_name=getattr(current_user, "nome", None),
                context_data=data.context,
            ):
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ChatMessageListResponse,
    summary="Listar mensagens",
    description="Lista mensagens de uma sessao.",
)
async def list_messages(
    session_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_active_user),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
    message_repo: ChatMessageRepository = Depends(get_message_repository),
) -> ChatMessageListResponse:
    """Lista mensagens da sessao."""
    session = await session_repo.get_by_id(session_id)

    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessao nao encontrada",
        )

    messages = await message_repo.get_by_session(
        session_id=session_id,
        skip=skip,
        limit=limit + 1,
    )

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    total = await message_repo.count_by_session(session_id)

    return ChatMessageListResponse(
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
        total=total,
        has_more=has_more,
    )


@router.post(
    "/messages/{message_id}/feedback",
    response_model=ChatMessageResponse,
    summary="Enviar feedback",
    description="Envia feedback sobre uma resposta.",
)
async def submit_feedback(
    message_id: UUID,
    feedback: MessageFeedback,
    current_user=Depends(get_current_active_user),
    message_repo: ChatMessageRepository = Depends(get_message_repository),
) -> ChatMessageResponse:
    """Registra feedback de uma mensagem."""
    message = await message_repo.get_by_id(message_id)

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensagem nao encontrada",
        )

    updated = await message_repo.update_feedback(
        message_id=message_id,
        user_rating=feedback.rating,
        was_helpful=feedback.was_helpful,
        user_feedback=feedback.feedback_text,
    )

    logger.info(f"Feedback registrado: msg={message_id}, rating={feedback.rating}")
    return ChatMessageResponse.model_validate(updated)


# ==============================================================================
# ENDPOINTS DE CONFIGURACAO E STATS
# ==============================================================================


@router.get(
    "/config",
    response_model=AIConfigResponse,
    summary="Configuracao da IA",
    description="Retorna configuracoes do sistema de IA.",
)
async def get_config(
    current_user=Depends(get_current_active_user),
) -> AIConfigResponse:
    """Retorna configuracoes."""
    return AIConfigResponse(
        model="gpt-4",
        max_tokens=2000,
        temperature=0.7,
        available_models=["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet"],
        features_enabled={
            "voice_input": True,
            "voice_output": False,
            "suggestions": True,
            "actions": True,
            "analytics": True,
            "streaming": True,
        },
    )


@router.get(
    "/stats",
    response_model=ConversationStats,
    summary="Estatisticas",
    description="Retorna estatisticas de uso do chat.",
)
async def get_stats(
    current_user=Depends(get_current_active_user),
    session_repo: ChatSessionRepository = Depends(get_session_repository),
) -> ConversationStats:
    """Retorna estatisticas do usuario."""
    try:
        stats = await session_repo.get_stats(current_user.id)

        return ConversationStats(
            total_sessions=stats["total_sessions"],
            total_messages=stats["total_messages"],
            avg_messages_per_session=(
                stats["total_messages"] / stats["total_sessions"]
                if stats["total_sessions"] > 0
                else 0
            ),
        )

    except Exception as e:
        logger.error(f"Erro ao obter stats: {e}")
        return ConversationStats()


@router.get(
    "/sessions/search",
    response_model=ChatSessionListResponse,
    summary="Buscar sessoes",
    description="Busca sessoes por texto.",
)
async def search_sessions(
    q: str = Query(..., min_length=2, description="Termo de busca"),
    limit: int = Query(20, ge=1, le=50),
    current_user=Depends(get_current_active_user),
    repo: ChatSessionRepository = Depends(get_session_repository),
) -> ChatSessionListResponse:
    """Busca sessoes."""
    sessions = await repo.search(
        user_id=current_user.id,
        query=q,
        limit=limit,
    )

    return ChatSessionListResponse(
        sessions=[ChatSessionResponse.model_validate(s) for s in sessions],
        total=len(sessions),
        page=1,
        page_size=limit,
        has_more=False,
    )


# ==============================================================================
# ENDPOINT DE HEALTH CHECK
# ==============================================================================


@router.get(
    "/health",
    summary="Health check",
    description="Verifica status do servico de chat.",
)
async def health_check() -> dict[str, Any]:
    """Health check do servico."""
    return {
        "status": "healthy",
        "service": "chat-ai",
        "version": "1.0.0",
    }
