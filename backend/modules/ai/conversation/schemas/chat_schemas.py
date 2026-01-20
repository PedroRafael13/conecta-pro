"""Schemas Pydantic para o modulo de conversacao."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from modules.ai.conversation.models.chat_message import (
    IntentCategory,
    MessageStatus,
    MessageType,
)


# ==============================================================================
# SCHEMAS DE SESSAO
# ==============================================================================


class ChatSessionCreate(BaseModel):
    """Schema para criar sessao de chat."""

    title: str = Field(default="Nova Conversa", max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    module_context: Optional[str] = Field(default=None, max_length=50)
    initial_context: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None

    model_config = {"from_attributes": True}


class ChatSessionUpdate(BaseModel):
    """Schema para atualizar sessao de chat."""

    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_pinned: Optional[bool] = None
    tags: Optional[list[str]] = None

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    """Schema de resposta de sessao."""

    id: UUID
    user_id: int
    title: str
    description: Optional[str] = None
    module_context: Optional[str] = None
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    is_active: bool = True
    is_archived: bool = False
    is_pinned: bool = False
    tags: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionListResponse(BaseModel):
    """Schema de lista de sessoes."""

    sessions: list[ChatSessionResponse]
    total: int
    page: int = 1
    page_size: int = 20
    has_more: bool = False

    model_config = {"from_attributes": True}


# ==============================================================================
# SCHEMAS DE MENSAGEM
# ==============================================================================


class ChatMessageCreate(BaseModel):
    """Schema para criar mensagem."""

    content: str = Field(..., min_length=1, max_length=10000)
    message_type: MessageType = MessageType.USER
    context_data: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """Schema de resposta de mensagem."""

    id: UUID
    session_id: UUID
    message_type: str
    content: str
    content_html: Optional[str] = None
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    sentiment: Optional[str] = None
    suggestions: Optional[list[dict[str, Any]]] = None
    actions: Optional[list[dict[str, Any]]] = None
    related_links: Optional[list[dict[str, Any]]] = None
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    user_rating: Optional[int] = None
    was_helpful: Optional[bool] = None
    status: str = MessageStatus.COMPLETED.value
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageListResponse(BaseModel):
    """Schema de lista de mensagens."""

    messages: list[ChatMessageResponse]
    total: int
    has_more: bool = False

    model_config = {"from_attributes": True}


class MessageFeedback(BaseModel):
    """Schema para feedback de mensagem."""

    message_id: UUID
    rating: int = Field(..., ge=1, le=5)
    was_helpful: bool
    feedback_text: Optional[str] = Field(default=None, max_length=1000)

    model_config = {"from_attributes": True}


# ==============================================================================
# SCHEMAS DE REQUEST/RESPONSE
# ==============================================================================


class SuggestionItem(BaseModel):
    """Item de sugestao."""

    text: str
    type: str = "quick_reply"  # quick_reply, action, link
    action: Optional[str] = None
    payload: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class ActionItem(BaseModel):
    """Item de acao."""

    type: str  # create, update, delete, navigate, export
    label: str
    description: Optional[str] = None
    module: Optional[str] = None
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    params: Optional[dict[str, Any]] = None
    requires_confirmation: bool = False

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    """Request para enviar mensagem."""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[UUID] = None
    context: Optional[dict[str, Any]] = None
    include_suggestions: bool = True
    stream: bool = False  # Para streaming de resposta

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate_message(self) -> "SendMessageRequest":
        """Valida e limpa a mensagem."""
        self.message = self.message.strip()
        return self


class SendMessageResponse(BaseModel):
    """Response ao enviar mensagem."""

    message_id: UUID
    session_id: UUID
    response: str
    response_html: Optional[str] = None
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    sentiment: Optional[str] = None
    suggestions: list[SuggestionItem] = []
    actions: list[ActionItem] = []
    related_links: list[dict[str, Any]] = []
    processing_time_ms: int
    model_used: str
    tokens_used: Optional[int] = None

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Response completa de conversacao."""

    text: str
    html: Optional[str] = None
    intent: str
    confidence: float
    sentiment: Optional[str] = None
    entities: list[dict[str, Any]] = []
    suggestions: list[SuggestionItem] = []
    actions: list[ActionItem] = []
    context_updates: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = {}

    model_config = {"from_attributes": True}


# ==============================================================================
# SCHEMAS DE CONFIGURACAO
# ==============================================================================


class AIConfigResponse(BaseModel):
    """Configuracao do sistema de IA."""

    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7
    available_models: list[str] = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"]
    features_enabled: dict[str, bool] = {
        "voice_input": True,
        "voice_output": False,
        "suggestions": True,
        "actions": True,
        "analytics": True,
    }

    model_config = {"from_attributes": True}


class ConversationStats(BaseModel):
    """Estatisticas de conversacao."""

    total_sessions: int = 0
    total_messages: int = 0
    avg_messages_per_session: float = 0.0
    avg_response_time_ms: float = 0.0
    satisfaction_rate: float = 0.0
    top_intents: list[dict[str, Any]] = []
    active_sessions_today: int = 0

    model_config = {"from_attributes": True}
