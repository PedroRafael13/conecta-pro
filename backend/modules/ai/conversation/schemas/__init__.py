"""Schemas do modulo de conversacao."""

from modules.ai.conversation.schemas.chat_schemas import (
    ActionItem,
    # Message schemas
    ChatMessageCreate,
    ChatMessageListResponse,
    ChatMessageResponse,
    # Session schemas
    ChatSessionCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
    ChatSessionUpdate,
    ConversationResponse,
    MessageFeedback,
    # Request/Response schemas
    SendMessageRequest,
    SendMessageResponse,
    SuggestionItem,
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
