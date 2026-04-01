"""Schemas Pydantic para o modulo de conversacao."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from modules.ai.conversation.models.chat_message import (
    MessageStatus,
    MessageType,
)

# ==============================================================================
# SCHEMAS DE SESSAO
# ==============================================================================


class ChatSessionCreate(BaseModel):
    """Schema para criar sessao de chat."""

    title: str = Field(default="Nova Conversa", max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    module_context: str | None = Field(default=None, max_length=50)
    initial_context: dict[str, Any] | None = None
    tags: list[str] | None = None

    model_config = {"from_attributes": True}


class ChatSessionUpdate(BaseModel):
    """Schema para atualizar sessao de chat."""

    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    is_pinned: bool | None = None
    tags: list[str] | None = None

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    """Schema de resposta de sessao."""

    id: UUID
    user_id: int
    title: str
    description: str | None = None
    module_context: str | None = None
    message_count: int = 0
    last_message_at: datetime | None = None
    is_active: bool = True
    is_archived: bool = False
    is_pinned: bool = False
    tags: list[str] | None = None
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
    context_data: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    """Schema de resposta de mensagem."""

    id: UUID
    session_id: UUID
    message_type: str
    content: str
    content_html: str | None = None
    intent: str | None = None
    intent_confidence: float | None = None
    sentiment: str | None = None
    suggestions: list[dict[str, Any]] | None = None
    actions: list[dict[str, Any]] | None = None
    related_links: list[dict[str, Any]] | None = None
    processing_time_ms: int | None = None
    model_used: str | None = None
    user_rating: int | None = None
    was_helpful: bool | None = None
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
    feedback_text: str | None = Field(default=None, max_length=1000)

    model_config = {"from_attributes": True}


# ==============================================================================
# SCHEMAS DE REQUEST/RESPONSE
# ==============================================================================


class SuggestionItem(BaseModel):
    """Item de sugestao."""

    text: str
    type: str = "quick_reply"  # quick_reply, action, link
    action: str | None = None
    payload: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class ActionItem(BaseModel):
    """Item de acao."""

    type: str  # create, update, delete, navigate, export
    label: str
    description: str | None = None
    module: str | None = None
    entity: str | None = None
    entity_id: str | None = None
    params: dict[str, Any] | None = None
    requires_confirmation: bool = False

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    """Request para enviar mensagem."""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: UUID | None = None
    context: dict[str, Any] | None = None
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
    response_html: str | None = None
    intent: str | None = None
    intent_confidence: float | None = None
    sentiment: str | None = None
    suggestions: list[SuggestionItem] = []
    actions: list[ActionItem] = []
    related_links: list[dict[str, Any]] = []
    processing_time_ms: int
    model_used: str
    tokens_used: int | None = None

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Response completa de conversacao."""

    text: str
    html: str | None = None
    intent: str
    confidence: float
    sentiment: str | None = None
    entities: list[dict[str, Any]] = []
    suggestions: list[SuggestionItem] = []
    actions: list[ActionItem] = []
    context_updates: dict[str, Any] | None = None
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
