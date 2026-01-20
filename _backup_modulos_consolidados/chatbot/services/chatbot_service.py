"""Chatbot Service - Servico principal de orquestracao.

Sprint 38 - Chatbot IA.

Responsavel por:
- Orquestracao do fluxo de conversa
- Gerenciamento de sessoes
- Integracao com NLU e DialogManager
- Tracking e analytics
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.chatbot.models import (
    ChatbotConfig,
    Conversation,
    ConversationChannel,
    ConversationMessage,
    ConversationStatus,
    Entity,
    Intent,
    MessageSender,
    MessageType,
    SentimentType,
)
from modules.ai.chatbot.services.dialog_manager import DialogContext, DialogManager, DialogResponse
from modules.ai.chatbot.services.nlu_service import NLUResult, NLUService


@dataclass
class ChatMessage:
    """Mensagem de chat."""

    message_id: str
    conversation_id: str
    text: str
    sender: MessageSender
    message_type: MessageType = MessageType.TEXT
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: Optional[SentimentType] = None
    buttons: List[Dict[str, Any]] = field(default_factory=list)
    quick_replies: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    is_fallback: bool = False
    action_triggered: Optional[str] = None
    action_result: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationSession:
    """Sessao de conversa."""

    conversation_id: str
    chatbot_id: str
    tenant_id: str
    channel: ConversationChannel
    status: ConversationStatus
    user_id: Optional[str] = None
    visitor_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    context: DialogContext = field(default_factory=lambda: DialogContext(""))
    messages: List[ChatMessage] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    overall_sentiment: SentimentType = SentimentType.NEUTRAL
    is_resolved: bool = False


class ChatbotService:
    """Servico principal do chatbot."""

    def __init__(
        self,
        nlu_service: Optional[NLUService] = None,
        dialog_manager: Optional[DialogManager] = None,
    ):
        """Inicializa o servico do chatbot."""
        self.nlu_service = nlu_service or NLUService()
        self.dialog_manager = dialog_manager or DialogManager()
        self._sessions: Dict[str, ConversationSession] = {}
        self._intents_cache: Dict[str, Dict[str, Intent]] = {}
        self._entities_cache: Dict[str, List[Entity]] = {}

    def process_message(
        self,
        chatbot_config: ChatbotConfig,
        text: str,
        conversation_id: Optional[str] = None,
        channel: ConversationChannel = ConversationChannel.WEB,
        user_id: Optional[str] = None,
        visitor_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        intents: Optional[List[Intent]] = None,
        entities: Optional[List[Entity]] = None,
    ) -> ChatMessage:
        """Processa mensagem do usuario e retorna resposta."""
        start_time = datetime.utcnow()

        # Verificar disponibilidade
        if not chatbot_config.is_available():
            return self._create_unavailable_response(chatbot_config)

        # Verificar horario de funcionamento
        if not chatbot_config.is_within_business_hours():
            return self._create_offline_response(chatbot_config)

        # Obter ou criar sessao
        session = self._get_or_create_session(
            chatbot_config=chatbot_config,
            conversation_id=conversation_id,
            channel=channel,
            user_id=user_id,
            visitor_id=visitor_id,
            user_name=user_name,
            user_email=user_email,
        )

        # Registrar mensagem do usuario
        user_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            conversation_id=session.conversation_id,
            text=text,
            sender=MessageSender.USER,
            attachments=attachments or [],
        )
        session.messages.append(user_message)
        session.last_activity_at = datetime.utcnow()

        # Obter intents e entities
        intent_list = intents or self._get_intents(chatbot_config.id)
        entity_list = entities or self._get_entities(chatbot_config.id)

        # Analise NLU
        nlu_result = self.nlu_service.analyze(
            text=text,
            intents=intent_list,
            entities=entity_list,
            context=self.dialog_manager.save_context(session.context),
            language=chatbot_config.primary_language,
        )

        # Atualizar sentimento
        session.overall_sentiment = self._update_sentiment(
            session.overall_sentiment,
            nlu_result.sentiment,
        )

        # Processar dialogo
        intents_dict = {i.name: i for i in intent_list}
        dialog_response = self.dialog_manager.process_turn(
            nlu_result=nlu_result,
            context=session.context,
            intents=intents_dict,
            greeting_message=chatbot_config.greeting_message,
            fallback_message=chatbot_config.fallback_message,
            goodbye_message=chatbot_config.goodbye_message,
        )

        # Calcular tempo de resposta
        response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Criar resposta
        bot_message = ChatMessage(
            message_id=dialog_response.message_id,
            conversation_id=session.conversation_id,
            text=dialog_response.text,
            sender=MessageSender.BOT,
            message_type=dialog_response.message_type,
            intent=nlu_result.top_intent.name if nlu_result.top_intent else None,
            intent_confidence=nlu_result.top_intent.confidence if nlu_result.top_intent else None,
            entities=[
                {
                    "entity": e.entity,
                    "value": e.value,
                    "confidence": e.confidence,
                    "start": e.start,
                    "end": e.end,
                }
                for e in nlu_result.entities
            ],
            sentiment=nlu_result.sentiment,
            buttons=dialog_response.buttons,
            quick_replies=dialog_response.quick_replies,
            attachments=dialog_response.attachments,
            is_fallback=dialog_response.is_fallback,
            action_triggered=dialog_response.action_triggered,
            action_result=dialog_response.action_result,
            response_time_ms=response_time,
        )

        # Registrar resposta
        session.messages.append(bot_message)

        # Verificar handoff
        if dialog_response.should_handoff:
            session.status = ConversationStatus.HANDOFF

        return bot_message

    def start_conversation(
        self,
        chatbot_config: ChatbotConfig,
        channel: ConversationChannel = ConversationChannel.WEB,
        user_id: Optional[str] = None,
        visitor_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> ChatMessage:
        """Inicia nova conversa com mensagem de boas-vindas."""
        session = self._get_or_create_session(
            chatbot_config=chatbot_config,
            channel=channel,
            user_id=user_id,
            visitor_id=visitor_id,
            user_name=user_name,
            user_email=user_email,
        )

        # Mensagem de boas-vindas
        greeting = ChatMessage(
            message_id=str(uuid.uuid4()),
            conversation_id=session.conversation_id,
            text=chatbot_config.greeting_message,
            sender=MessageSender.BOT,
            message_type=MessageType.TEXT,
            quick_replies=self._get_welcome_quick_replies(chatbot_config),
        )

        session.messages.append(greeting)

        return greeting

    def end_conversation(
        self,
        conversation_id: str,
        resolved: bool = False,
        resolution_notes: Optional[str] = None,
    ) -> bool:
        """Encerra conversa."""
        session = self._sessions.get(conversation_id)
        if not session:
            return False

        session.status = ConversationStatus.RESOLVED if resolved else ConversationStatus.CLOSED
        session.is_resolved = resolved

        return True

    def request_handoff(
        self,
        conversation_id: str,
        reason: Optional[str] = None,
        queue_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Solicita transferencia para atendente humano."""
        session = self._sessions.get(conversation_id)
        if not session:
            return False, "Conversa nao encontrada"

        session.status = ConversationStatus.HANDOFF

        # Aqui integraria com sistema de filas de atendimento
        message = "Transferindo para um atendente. Aguarde um momento."

        return True, message

    def get_conversation(self, conversation_id: str) -> Optional[ConversationSession]:
        """Retorna sessao de conversa."""
        return self._sessions.get(conversation_id)

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[ChatMessage]:
        """Retorna historico de mensagens."""
        session = self._sessions.get(conversation_id)
        if not session:
            return []

        return session.messages[-limit:]

    def add_feedback(
        self,
        conversation_id: str,
        message_id: Optional[str] = None,
        rating: Optional[int] = None,
        is_positive: Optional[bool] = None,
        comment: Optional[str] = None,
    ) -> bool:
        """Adiciona feedback a conversa ou mensagem."""
        session = self._sessions.get(conversation_id)
        if not session:
            return False

        # Aqui salvaria o feedback no banco
        # Por enquanto, apenas retorna sucesso

        return True

    def _get_or_create_session(
        self,
        chatbot_config: ChatbotConfig,
        conversation_id: Optional[str] = None,
        channel: ConversationChannel = ConversationChannel.WEB,
        user_id: Optional[str] = None,
        visitor_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> ConversationSession:
        """Obtem ou cria sessao de conversa."""
        if conversation_id and conversation_id in self._sessions:
            return self._sessions[conversation_id]

        # Criar nova sessao
        new_id = conversation_id or str(uuid.uuid4())
        context = self.dialog_manager.create_context(new_id)

        session = ConversationSession(
            conversation_id=new_id,
            chatbot_id=str(chatbot_config.id),
            tenant_id=str(chatbot_config.tenant_id),
            channel=channel,
            status=ConversationStatus.ACTIVE,
            user_id=user_id,
            visitor_id=visitor_id or str(uuid.uuid4()),
            user_name=user_name,
            user_email=user_email,
            context=context,
        )

        self._sessions[new_id] = session
        return session

    def _get_intents(self, chatbot_id: str) -> List[Intent]:
        """Obtem intents do chatbot (cache)."""
        # Em producao, buscaria do banco de dados
        return list(self._intents_cache.get(str(chatbot_id), {}).values())

    def _get_entities(self, chatbot_id: str) -> List[Entity]:
        """Obtem entities do chatbot (cache)."""
        # Em producao, buscaria do banco de dados
        return self._entities_cache.get(str(chatbot_id), [])

    def load_intents(self, chatbot_id: str, intents: List[Intent]) -> None:
        """Carrega intents no cache."""
        self._intents_cache[chatbot_id] = {i.name: i for i in intents}

    def load_entities(self, chatbot_id: str, entities: List[Entity]) -> None:
        """Carrega entities no cache."""
        self._entities_cache[chatbot_id] = entities

    def _update_sentiment(
        self,
        current: SentimentType,
        new: SentimentType,
    ) -> SentimentType:
        """Atualiza sentimento geral da conversa."""
        # Mapeamento para valores numericos
        sentiment_values = {
            SentimentType.VERY_NEGATIVE: -2,
            SentimentType.NEGATIVE: -1,
            SentimentType.NEUTRAL: 0,
            SentimentType.POSITIVE: 1,
            SentimentType.VERY_POSITIVE: 2,
        }

        # Calcular media ponderada (dando mais peso ao novo)
        current_value = sentiment_values.get(current, 0)
        new_value = sentiment_values.get(new, 0)
        avg = (current_value * 0.6) + (new_value * 0.4)

        # Converter de volta
        if avg >= 1.5:
            return SentimentType.VERY_POSITIVE
        elif avg >= 0.5:
            return SentimentType.POSITIVE
        elif avg <= -1.5:
            return SentimentType.VERY_NEGATIVE
        elif avg <= -0.5:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL

    def _get_welcome_quick_replies(
        self,
        chatbot_config: ChatbotConfig,
    ) -> List[Dict[str, Any]]:
        """Retorna quick replies de boas-vindas."""
        if chatbot_config.quick_replies:
            return chatbot_config.quick_replies[:4]

        # Quick replies padrao
        return [
            {"text": "Ver opcoes", "action": "show_menu"},
            {"text": "Falar com atendente", "action": "handoff"},
        ]

    def _create_unavailable_response(
        self,
        chatbot_config: ChatbotConfig,
    ) -> ChatMessage:
        """Cria resposta para chatbot indisponivel."""
        return ChatMessage(
            message_id=str(uuid.uuid4()),
            conversation_id="",
            text="Desculpe, o atendimento virtual esta temporariamente indisponivel.",
            sender=MessageSender.SYSTEM,
            message_type=MessageType.SYSTEM,
        )

    def _create_offline_response(
        self,
        chatbot_config: ChatbotConfig,
    ) -> ChatMessage:
        """Cria resposta para fora do horario."""
        return ChatMessage(
            message_id=str(uuid.uuid4()),
            conversation_id="",
            text=chatbot_config.offline_message,
            sender=MessageSender.SYSTEM,
            message_type=MessageType.SYSTEM,
        )

    def get_analytics_summary(
        self,
        chatbot_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Retorna resumo de analytics."""
        # Calcular metricas das sessoes em memoria
        # Em producao, buscaria do banco de dados

        sessions = [s for s in self._sessions.values() if s.chatbot_id == chatbot_id]

        if start_date:
            sessions = [s for s in sessions if s.started_at >= start_date]
        if end_date:
            sessions = [s for s in sessions if s.started_at <= end_date]

        total_conversations = len(sessions)
        total_messages = sum(len(s.messages) for s in sessions)

        resolved_count = sum(1 for s in sessions if s.is_resolved)
        resolution_rate = (resolved_count / total_conversations * 100) if total_conversations else 0

        # Contar fallbacks
        fallback_count = sum(
            sum(1 for m in s.messages if m.is_fallback) for s in sessions
        )
        total_bot_messages = sum(
            sum(1 for m in s.messages if m.sender == MessageSender.BOT) for s in sessions
        )
        fallback_rate = (fallback_count / total_bot_messages * 100) if total_bot_messages else 0

        # Tempo medio de resposta
        response_times = [
            m.response_time_ms
            for s in sessions
            for m in s.messages
            if m.response_time_ms
        ]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Distribuicao de sentimento
        sentiment_dist = {st.value: 0 for st in SentimentType}
        for s in sessions:
            sentiment_dist[s.overall_sentiment.value] += 1

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "unique_users": len(set(s.visitor_id for s in sessions)),
            "resolution_rate": resolution_rate,
            "fallback_rate": fallback_rate,
            "avg_response_time_ms": int(avg_response_time),
            "sentiment_distribution": sentiment_dist,
        }
