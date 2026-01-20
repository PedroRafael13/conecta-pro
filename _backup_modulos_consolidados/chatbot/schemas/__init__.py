"""Schemas do módulo Chatbot IA.

Sprint 38 - Chatbot IA.
"""

from modules.ai.chatbot.schemas.chatbot_schemas import (
    AnalyticsRequest,
    AnalyticsSummaryResponse,
    ChatbotConfigBase,
    ChatbotCreateRequest,
    ChatbotResponse,
    ChatbotUpdateRequest,
    ConversationDetailResponse,
    ConversationResponse,
    DetectedIntent,
    EntityCreateRequest,
    EntityResponse,
    EntityValueSchema,
    ExtractedEntity,
    FeedbackCreateRequest,
    HandoffRequest,
    HandoffResponse,
    IntentCreateRequest,
    IntentResponse,
    IntentSlotSchema,
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

__all__ = [
    # Chatbot
    "ChatbotConfigBase",
    "ChatbotCreateRequest",
    "ChatbotUpdateRequest",
    "ChatbotResponse",
    # Intent
    "IntentSlotSchema",
    "IntentCreateRequest",
    "IntentUpdateRequest",
    "IntentResponse",
    # Entity
    "EntityValueSchema",
    "EntityCreateRequest",
    "EntityResponse",
    # Conversation
    "SendMessageRequest",
    "MessageResponse",
    "ConversationResponse",
    "ConversationDetailResponse",
    # NLU
    "NLURequest",
    "NLUResponse",
    "DetectedIntent",
    "ExtractedEntity",
    # Training
    "TrainingDataCreateRequest",
    "TrainingDataBulkRequest",
    "TrainChatbotRequest",
    "TrainingJobResponse",
    # Analytics
    "AnalyticsRequest",
    "AnalyticsSummaryResponse",
    # Feedback
    "FeedbackCreateRequest",
    # Handoff
    "HandoffRequest",
    "HandoffResponse",
]
