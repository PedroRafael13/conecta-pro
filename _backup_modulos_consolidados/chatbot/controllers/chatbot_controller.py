"""Controller do módulo Chatbot IA.

Sprint 38 - Chatbot IA.

Endpoints REST para:
- Gerenciamento de chatbots
- Gerenciamento de intents
- Gerenciamento de entities
- Processamento de mensagens
- Conversas
- Treinamento
- Analytics
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser, get_current_active_user
from core.database import get_async_session
from modules.ai.chatbot.models import (
    ChatbotConfig,
    ChatbotStatus,
    Conversation,
    ConversationChannel,
    ConversationFeedback,
    ConversationMessage,
    ConversationStatus,
    Entity,
    Intent,
    TrainingData,
    ChatbotTrainingJob,
    TrainingStatus,
)
from modules.ai.chatbot.schemas import (
    AnalyticsRequest,
    AnalyticsSummaryResponse,
    ChatbotCreateRequest,
    ChatbotResponse,
    ChatbotUpdateRequest,
    ConversationDetailResponse,
    ConversationResponse,
    EntityCreateRequest,
    EntityResponse,
    FeedbackCreateRequest,
    HandoffRequest,
    HandoffResponse,
    IntentCreateRequest,
    IntentResponse,
    IntentUpdateRequest,
    MessageResponse,
    NLURequest,
    NLUResponse,
    SendMessageRequest,
    TrainChatbotRequest,
    TrainingDataBulkRequest,
    TrainingDataCreateRequest,
    TrainingJobResponse,
)
from modules.ai.chatbot.services import ChatbotService, DialogManager, NLUService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["Chatbot IA"])


# ============================================================
# Dependências
# ============================================================


async def get_chatbot_service() -> ChatbotService:
    """Retorna instância do serviço de chatbot."""
    nlu_service = NLUService()
    dialog_manager = DialogManager()
    return ChatbotService(nlu_service=nlu_service, dialog_manager=dialog_manager)


async def get_chatbot_or_404(
    chatbot_id: UUID,
    db: AsyncSession,
    tenant_id: UUID,
) -> ChatbotConfig:
    """Busca chatbot ou retorna 404."""
    result = await db.execute(
        select(ChatbotConfig).where(
            ChatbotConfig.id == chatbot_id,
            ChatbotConfig.tenant_id == tenant_id,
        )
    )
    chatbot = result.scalar_one_or_none()
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot não encontrado",
        )
    return chatbot


# ============================================================
# Chatbot CRUD
# ============================================================


@router.post("/", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def criar_chatbot(
    request: ChatbotCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> ChatbotResponse:
    """Cria novo chatbot."""
    try:
        chatbot = ChatbotConfig(
            tenant_id=current_user.tenant_id,
            name=request.name,
            description=request.description,
            personality=request.personality,
            provider=request.provider,
            primary_language=request.primary_language,
            supported_languages=request.supported_languages,
            greeting_message=request.greeting_message,
            fallback_message=request.fallback_message,
            goodbye_message=request.goodbye_message,
            offline_message=request.offline_message,
            confidence_threshold=request.confidence_threshold,
            handoff_enabled=request.handoff_enabled,
            handoff_threshold=request.handoff_threshold,
            handoff_queue_id=request.handoff_queue_id,
            max_conversation_turns=request.max_conversation_turns,
            session_timeout_minutes=request.session_timeout_minutes,
            quick_replies=request.quick_replies,
            persistent_menu=request.persistent_menu,
            business_hours=request.business_hours,
            channels=request.channels,
            status=ChatbotStatus.DRAFT,
            created_by=current_user.id,
        )

        db.add(chatbot)
        await db.commit()
        await db.refresh(chatbot)

        logger.info(f"Chatbot criado: {chatbot.id} por {current_user.email}")

        return ChatbotResponse.model_validate(chatbot)

    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao criar chatbot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar chatbot",
        )


@router.get("/", response_model=List[ChatbotResponse])
async def listar_chatbots(
    status_filter: Optional[ChatbotStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[ChatbotResponse]:
    """Lista chatbots do tenant."""
    try:
        query = select(ChatbotConfig).where(
            ChatbotConfig.tenant_id == current_user.tenant_id,
        )

        if status_filter:
            query = query.where(ChatbotConfig.status == status_filter)

        query = query.order_by(ChatbotConfig.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        chatbots = result.scalars().all()

        return [ChatbotResponse.model_validate(c) for c in chatbots]

    except Exception as e:
        logger.error(f"Erro ao listar chatbots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar chatbots",
        )


@router.get("/{chatbot_id}", response_model=ChatbotResponse)
async def obter_chatbot(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> ChatbotResponse:
    """Obtém detalhes de um chatbot."""
    chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)
    return ChatbotResponse.model_validate(chatbot)


@router.patch("/{chatbot_id}", response_model=ChatbotResponse)
async def atualizar_chatbot(
    chatbot_id: UUID,
    request: ChatbotUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> ChatbotResponse:
    """Atualiza chatbot."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chatbot, field, value)

        chatbot.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(chatbot)

        logger.info(f"Chatbot atualizado: {chatbot_id}")

        return ChatbotResponse.model_validate(chatbot)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao atualizar chatbot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar chatbot",
        )


@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_chatbot(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> None:
    """Deleta chatbot (soft delete)."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        chatbot.ativo = False
        chatbot.status = ChatbotStatus.ARCHIVED
        chatbot.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Chatbot deletado: {chatbot_id}")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao deletar chatbot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar chatbot",
        )


@router.post("/{chatbot_id}/activate", response_model=ChatbotResponse)
async def ativar_chatbot(
    chatbot_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> ChatbotResponse:
    """Ativa chatbot para uso."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Verificar se tem intents
        intents_result = await db.execute(
            select(func.count(Intent.id)).where(
                Intent.chatbot_id == chatbot_id,
                Intent.active == True,
            )
        )
        intents_count = intents_result.scalar()

        if intents_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chatbot precisa ter pelo menos uma intent ativa para ser ativado",
            )

        chatbot.status = ChatbotStatus.ACTIVE
        chatbot.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(chatbot)

        logger.info(f"Chatbot ativado: {chatbot_id}")

        return ChatbotResponse.model_validate(chatbot)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao ativar chatbot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao ativar chatbot",
        )


# ============================================================
# Intent Management
# ============================================================


@router.post("/{chatbot_id}/intents", response_model=IntentResponse, status_code=status.HTTP_201_CREATED)
async def criar_intent(
    chatbot_id: UUID,
    request: IntentCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> IntentResponse:
    """Cria nova intent para o chatbot."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Verificar nome único
        existing = await db.execute(
            select(Intent).where(
                Intent.chatbot_id == chatbot_id,
                Intent.name == request.name,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma intent com esse nome",
            )

        intent = Intent(
            chatbot_id=chatbot_id,
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            category=request.category,
            training_phrases=request.training_phrases,
            responses=request.responses,
            rich_responses=request.rich_responses,
            slots=request.slots,
            input_contexts=request.input_contexts,
            output_contexts=request.output_contexts,
            action=request.action,
            action_config=request.action_config,
            priority=request.priority,
            is_fallback=request.is_fallback,
            is_welcome=request.is_welcome,
            requires_confirmation=request.requires_confirmation,
            confirmation_message=request.confirmation_message,
            followup_intents=request.followup_intents,
            synonyms=request.synonyms,
            active=True,
        )

        db.add(intent)
        await db.commit()
        await db.refresh(intent)

        logger.info(f"Intent criada: {intent.id} para chatbot {chatbot_id}")

        return IntentResponse.model_validate(intent)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao criar intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar intent",
        )


@router.get("/{chatbot_id}/intents", response_model=List[IntentResponse])
async def listar_intents(
    chatbot_id: UUID,
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[IntentResponse]:
    """Lista intents do chatbot."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        query = select(Intent).where(Intent.chatbot_id == chatbot_id)

        if active_only:
            query = query.where(Intent.active == True)

        query = query.order_by(Intent.priority.desc(), Intent.name)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        intents = result.scalars().all()

        return [IntentResponse.model_validate(i) for i in intents]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar intents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar intents",
        )


@router.patch("/{chatbot_id}/intents/{intent_id}", response_model=IntentResponse)
async def atualizar_intent(
    chatbot_id: UUID,
    intent_id: UUID,
    request: IntentUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> IntentResponse:
    """Atualiza intent."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        result = await db.execute(
            select(Intent).where(
                Intent.id == intent_id,
                Intent.chatbot_id == chatbot_id,
            )
        )
        intent = result.scalar_one_or_none()
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intent não encontrada",
            )

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(intent, field, value)

        intent.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(intent)

        logger.info(f"Intent atualizada: {intent_id}")

        return IntentResponse.model_validate(intent)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao atualizar intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar intent",
        )


@router.delete("/{chatbot_id}/intents/{intent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_intent(
    chatbot_id: UUID,
    intent_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> None:
    """Deleta intent (soft delete)."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        result = await db.execute(
            select(Intent).where(
                Intent.id == intent_id,
                Intent.chatbot_id == chatbot_id,
            )
        )
        intent = result.scalar_one_or_none()
        if not intent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intent não encontrada",
            )

        intent.active = False
        intent.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Intent deletada: {intent_id}")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao deletar intent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar intent",
        )


# ============================================================
# Entity Management
# ============================================================


@router.post("/{chatbot_id}/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def criar_entity(
    chatbot_id: UUID,
    request: EntityCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> EntityResponse:
    """Cria nova entity para o chatbot."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Verificar nome único
        existing = await db.execute(
            select(Entity).where(
                Entity.chatbot_id == chatbot_id,
                Entity.name == request.name,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma entity com esse nome",
            )

        entity = Entity(
            chatbot_id=chatbot_id,
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            entity_type=request.entity_type,
            values=request.values,
            regex_pattern=request.regex_pattern,
            enable_fuzzy=request.enable_fuzzy,
            fuzzy_threshold=request.fuzzy_threshold,
            active=True,
        )

        db.add(entity)
        await db.commit()
        await db.refresh(entity)

        logger.info(f"Entity criada: {entity.id} para chatbot {chatbot_id}")

        return EntityResponse.model_validate(entity)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao criar entity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar entity",
        )


@router.get("/{chatbot_id}/entities", response_model=List[EntityResponse])
async def listar_entities(
    chatbot_id: UUID,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[EntityResponse]:
    """Lista entities do chatbot."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        query = select(Entity).where(Entity.chatbot_id == chatbot_id)

        if active_only:
            query = query.where(Entity.active == True)

        query = query.order_by(Entity.name)

        result = await db.execute(query)
        entities = result.scalars().all()

        return [EntityResponse.model_validate(e) for e in entities]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar entities",
        )


# ============================================================
# Message Processing
# ============================================================


@router.post("/{chatbot_id}/message", response_model=MessageResponse)
async def enviar_mensagem(
    chatbot_id: UUID,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_async_session),
    service: ChatbotService = Depends(get_chatbot_service),
    current_user: CurrentActiveUser = ...,  # Required
) -> MessageResponse:
    """Processa mensagem do usuário e retorna resposta do chatbot."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        if chatbot.status != ChatbotStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chatbot não está ativo",
            )

        # Carregar intents e entities do banco
        intents_result = await db.execute(
            select(Intent).where(
                Intent.chatbot_id == chatbot_id,
                Intent.active == True,
            )
        )
        intents = intents_result.scalars().all()

        entities_result = await db.execute(
            select(Entity).where(
                Entity.chatbot_id == chatbot_id,
                Entity.active == True,
            )
        )
        entities = entities_result.scalars().all()

        # Processar mensagem
        response = service.process_message(
            chatbot_config=chatbot,
            text=request.text,
            conversation_id=request.conversation_id,
            channel=request.channel,
            user_id=str(request.user_id) if request.user_id else None,
            visitor_id=request.visitor_id,
            user_name=request.user_name,
            user_email=request.user_email,
            attachments=request.attachments,
            metadata=request.metadata,
            intents=list(intents),
            entities=list(entities),
        )

        logger.info(f"Mensagem processada para chatbot {chatbot_id}")

        return MessageResponse(
            message_id=response.message_id,
            conversation_id=response.conversation_id,
            text=response.text,
            sender=response.sender.value,
            message_type=response.message_type.value,
            intent=response.intent,
            intent_confidence=response.intent_confidence,
            entities=response.entities,
            sentiment=response.sentiment.value if response.sentiment else None,
            buttons=response.buttons,
            quick_replies=response.quick_replies,
            attachments=response.attachments,
            is_fallback=response.is_fallback,
            action_triggered=response.action_triggered,
            action_result=response.action_result,
            response_time_ms=response.response_time_ms,
            created_at=response.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar mensagem",
        )


@router.post("/{chatbot_id}/start", response_model=MessageResponse)
async def iniciar_conversa(
    chatbot_id: UUID,
    channel: ConversationChannel = Query(ConversationChannel.WEB),
    visitor_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session),
    service: ChatbotService = Depends(get_chatbot_service),
    current_user: CurrentActiveUser = ...,  # Required
) -> MessageResponse:
    """Inicia nova conversa com mensagem de boas-vindas."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        if chatbot.status != ChatbotStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chatbot não está ativo",
            )

        response = service.start_conversation(
            chatbot_config=chatbot,
            channel=channel,
            user_id=str(current_user.id),
            visitor_id=visitor_id,
            user_name=current_user.nome,
            user_email=current_user.email,
        )

        return MessageResponse(
            message_id=response.message_id,
            conversation_id=response.conversation_id,
            text=response.text,
            sender=response.sender.value,
            message_type=response.message_type.value,
            quick_replies=response.quick_replies,
            created_at=response.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar conversa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar conversa",
        )


@router.post("/{chatbot_id}/nlu/analyze", response_model=NLUResponse)
async def analisar_nlu(
    chatbot_id: UUID,
    request: NLURequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> NLUResponse:
    """Analisa texto usando NLU sem criar conversa."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Carregar intents e entities
        intents_result = await db.execute(
            select(Intent).where(
                Intent.chatbot_id == chatbot_id,
                Intent.active == True,
            )
        )
        intents = list(intents_result.scalars().all())

        entities_result = await db.execute(
            select(Entity).where(
                Entity.chatbot_id == chatbot_id,
                Entity.active == True,
            )
        )
        entities = list(entities_result.scalars().all())

        # Analisar
        nlu_service = NLUService()
        result = nlu_service.analyze(
            text=request.text,
            intents=intents,
            entities=entities,
            context=request.context,
            language=chatbot.primary_language,
        )

        return NLUResponse(
            text=result.text,
            normalized_text=result.normalized_text,
            language=result.language,
            intents=[
                {
                    "name": i.name,
                    "confidence": i.confidence,
                    "display_name": i.display_name,
                    "category": i.category,
                }
                for i in result.intents
            ],
            top_intent={
                "name": result.top_intent.name,
                "confidence": result.top_intent.confidence,
            }
            if result.top_intent
            else None,
            entities=[
                {
                    "entity": e.entity,
                    "entity_type": e.entity_type.value,
                    "value": e.value,
                    "original_value": e.original_value,
                    "confidence": e.confidence,
                    "start": e.start,
                    "end": e.end,
                }
                for e in result.entities
            ],
            sentiment=result.sentiment.value,
            sentiment_score=result.sentiment_score,
            is_ambiguous=result.is_ambiguous,
            processing_time_ms=result.processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na análise NLU: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro na análise NLU",
        )


# ============================================================
# Conversations
# ============================================================


@router.get("/{chatbot_id}/conversations", response_model=List[ConversationResponse])
async def listar_conversas(
    chatbot_id: UUID,
    status_filter: Optional[ConversationStatus] = Query(None, alias="status"),
    channel: Optional[ConversationChannel] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[ConversationResponse]:
    """Lista conversas do chatbot."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        query = select(Conversation).where(Conversation.chatbot_id == chatbot_id)

        if status_filter:
            query = query.where(Conversation.status == status_filter)
        if channel:
            query = query.where(Conversation.channel == channel)

        query = query.order_by(Conversation.last_activity_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        conversations = result.scalars().all()

        return [ConversationResponse.model_validate(c) for c in conversations]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar conversas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar conversas",
        )


@router.get("/{chatbot_id}/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def obter_conversa(
    chatbot_id: UUID,
    conversation_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> ConversationDetailResponse:
    """Obtém detalhes de uma conversa com mensagens."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        result = await db.execute(
            select(Conversation).where(
                Conversation.chatbot_id == chatbot_id,
                Conversation.conversation_id == conversation_id,
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada",
            )

        # Buscar mensagens
        messages_result = await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.created_at)
        )
        messages = messages_result.scalars().all()

        return ConversationDetailResponse(
            **ConversationResponse.model_validate(conversation).model_dump(),
            messages=[MessageResponse.model_validate(m) for m in messages],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter conversa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter conversa",
        )


@router.post("/{chatbot_id}/conversations/{conversation_id}/handoff", response_model=HandoffResponse)
async def solicitar_handoff(
    chatbot_id: UUID,
    conversation_id: str,
    request: HandoffRequest,
    db: AsyncSession = Depends(get_async_session),
    service: ChatbotService = Depends(get_chatbot_service),
    current_user: CurrentActiveUser = ...,  # Required
) -> HandoffResponse:
    """Solicita transferência para atendente humano."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        success, message = service.request_handoff(
            conversation_id=conversation_id,
            reason=request.reason,
            queue_id=request.queue_id,
        )

        return HandoffResponse(
            success=success,
            message=message,
            queue_position=1 if success else None,
            estimated_wait_time=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao solicitar handoff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao solicitar handoff",
        )


@router.post("/{chatbot_id}/conversations/{conversation_id}/feedback")
async def adicionar_feedback(
    chatbot_id: UUID,
    conversation_id: str,
    request: FeedbackCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> dict:
    """Adiciona feedback à conversa."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Buscar conversa
        result = await db.execute(
            select(Conversation).where(
                Conversation.chatbot_id == chatbot_id,
                Conversation.conversation_id == conversation_id,
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada",
            )

        feedback = ConversationFeedback(
            conversation_id=conversation.id,
            message_id=request.message_id,
            rating=request.rating,
            is_positive=request.is_positive,
            comment=request.comment,
            feedback_type=request.feedback_type,
            user_id=current_user.id,
        )

        db.add(feedback)
        await db.commit()

        logger.info(f"Feedback adicionado para conversa {conversation_id}")

        return {"success": True, "message": "Feedback registrado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao adicionar feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar feedback",
        )


# ============================================================
# Training
# ============================================================


@router.post("/{chatbot_id}/training/data", status_code=status.HTTP_201_CREATED)
async def adicionar_training_data(
    chatbot_id: UUID,
    request: TrainingDataCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> dict:
    """Adiciona dado de treinamento."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        training_data = TrainingData(
            chatbot_id=chatbot_id,
            intent_id=request.intent_id,
            text=request.text,
            source=request.source,
            metadata=request.metadata,
            is_validated=False,
        )

        db.add(training_data)
        await db.commit()

        return {"success": True, "message": "Dado de treinamento adicionado"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao adicionar training data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar dado de treinamento",
        )


@router.post("/{chatbot_id}/training/data/bulk", status_code=status.HTTP_201_CREATED)
async def adicionar_training_data_bulk(
    chatbot_id: UUID,
    request: TrainingDataBulkRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> dict:
    """Adiciona múltiplos dados de treinamento."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        added = 0
        for item in request.items:
            training_data = TrainingData(
                chatbot_id=chatbot_id,
                intent_id=item.intent_id,
                text=item.text,
                source=item.source,
                metadata=item.metadata,
                is_validated=False,
            )
            db.add(training_data)
            added += 1

        await db.commit()

        return {"success": True, "added": added}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao adicionar training data bulk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar dados de treinamento",
        )


@router.post("/{chatbot_id}/training/train", response_model=TrainingJobResponse)
async def iniciar_treinamento(
    chatbot_id: UUID,
    request: TrainChatbotRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> TrainingJobResponse:
    """Inicia job de treinamento do chatbot."""
    try:
        chatbot = await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Verificar se já existe treinamento em andamento
        existing_job = await db.execute(
            select(ChatbotTrainingJob).where(
                ChatbotTrainingJob.chatbot_id == chatbot_id,
                ChatbotTrainingJob.status.in_([TrainingStatus.PENDING, TrainingStatus.RUNNING]),
            )
        )
        if existing_job.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um treinamento em andamento",
            )

        # Contar dados de treinamento
        count_result = await db.execute(
            select(func.count(TrainingData.id)).where(
                TrainingData.chatbot_id == chatbot_id,
                TrainingData.is_validated == True,
            )
        )
        training_count = count_result.scalar()

        # Criar job
        job = ChatbotTrainingJob(
            chatbot_id=chatbot_id,
            model_version=request.model_version or f"v{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            status=TrainingStatus.PENDING,
            training_data_count=training_count,
            config=request.config,
            started_by=current_user.id,
        )

        db.add(job)

        # Atualizar status do chatbot
        chatbot.status = ChatbotStatus.TRAINING

        await db.commit()
        await db.refresh(job)

        logger.info(f"Treinamento iniciado para chatbot {chatbot_id}: job {job.id}")

        # Aqui dispararia o job de treinamento em background
        # Simulação: marcar como running
        job.status = TrainingStatus.RUNNING
        job.started_at = datetime.utcnow()
        await db.commit()

        return TrainingJobResponse.model_validate(job)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Erro ao iniciar treinamento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar treinamento",
        )


@router.get("/{chatbot_id}/training/jobs", response_model=List[TrainingJobResponse])
async def listar_training_jobs(
    chatbot_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session),
    current_user: CurrentActiveUser = ...,  # Required
) -> List[TrainingJobResponse]:
    """Lista jobs de treinamento."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        query = (
            select(ChatbotTrainingJob)
            .where(ChatbotTrainingJob.chatbot_id == chatbot_id)
            .order_by(ChatbotTrainingJob.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        jobs = result.scalars().all()

        return [TrainingJobResponse.model_validate(j) for j in jobs]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar training jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar jobs de treinamento",
        )


# ============================================================
# Analytics
# ============================================================


@router.get("/{chatbot_id}/analytics", response_model=AnalyticsSummaryResponse)
async def obter_analytics(
    chatbot_id: UUID,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_async_session),
    service: ChatbotService = Depends(get_chatbot_service),
    current_user: CurrentActiveUser = ...,  # Required
) -> AnalyticsSummaryResponse:
    """Obtém analytics do chatbot."""
    try:
        await get_chatbot_or_404(chatbot_id, db, current_user.tenant_id)

        # Buscar dados das conversas
        query = select(Conversation).where(Conversation.chatbot_id == chatbot_id)

        if start_date:
            query = query.where(Conversation.started_at >= start_date)
        if end_date:
            query = query.where(Conversation.started_at <= end_date)

        result = await db.execute(query)
        conversations = result.scalars().all()

        # Calcular métricas
        total_conversations = len(conversations)
        total_messages = sum(c.message_count for c in conversations)
        unique_users = len(set(c.visitor_id for c in conversations if c.visitor_id))

        resolved = [c for c in conversations if c.is_resolved]
        resolution_rate = (len(resolved) / total_conversations * 100) if total_conversations else 0

        # Buscar mensagens para fallback rate
        if total_conversations > 0:
            messages_result = await db.execute(
                select(ConversationMessage).where(
                    ConversationMessage.conversation_id.in_([c.id for c in conversations])
                )
            )
            messages = messages_result.scalars().all()

            bot_messages = [m for m in messages if m.sender.value == "bot"]
            fallback_messages = [m for m in bot_messages if m.is_fallback]
            fallback_rate = (len(fallback_messages) / len(bot_messages) * 100) if bot_messages else 0

            response_times = [m.response_time_ms for m in bot_messages if m.response_time_ms]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        else:
            fallback_rate = 0
            avg_response_time = 0

        # Distribuição de sentimento
        sentiment_dist = {}
        for c in conversations:
            sentiment = c.overall_sentiment.value if c.overall_sentiment else "neutral"
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1

        return AnalyticsSummaryResponse(
            total_conversations=total_conversations,
            total_messages=total_messages,
            unique_users=unique_users,
            resolution_rate=round(resolution_rate, 2),
            fallback_rate=round(fallback_rate, 2),
            avg_response_time_ms=int(avg_response_time),
            sentiment_distribution=sentiment_dist,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter analytics",
        )
