"""Schemas do modulo de conversacao."""

from modules.ai.conversation.schemas.chat_schemas import (
    # Session schemas
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionListResponse,
    # Message schemas
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageListResponse,
    MessageFeedback,
    # Request/Response schemas
    SendMessageRequest,
    SendMessageResponse,
    ConversationResponse,
    SuggestionItem,
    ActionItem,
)

__all__ = [
    # Session
    "ChatSessionCreate",
    "ChatSessionUpdate",
    "ChatSessionResponse",
    "ChatSessionListResponse",
    # Message
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatMessageListResponse",
    "MessageFeedback",
    # Request/Response
    "SendMessageRequest",
    "SendMessageResponse",
    "ConversationResponse",
    "SuggestionItem",
    "ActionItem",
]
