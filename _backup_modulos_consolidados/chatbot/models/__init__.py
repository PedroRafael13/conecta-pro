"""Models do módulo Chatbot IA.

Sprint 38 - Chatbot IA.
"""

from modules.ai.chatbot.models.chatbot_config import (
    ChatbotConfig,
    ChatbotPersonality,
    ChatbotProvider,
    ChatbotStatus,
)
from modules.ai.chatbot.models.conversation import (
    Conversation,
    ConversationChannel,
    ConversationContext,
    ConversationMessage,
    ConversationStatus,
    MessageSender,
    MessageType,
    SentimentType,
)
from modules.ai.chatbot.models.intent import (
    Entity,
    EntityType,
    Intent,
    IntentCategory,
    IntentExample,
)
from modules.ai.chatbot.models.training import (
    ChatbotAnalytics,
    ChatbotTrainingJob,
    ConversationFeedback,
    MetricPeriod,
    TrainingData,
    TrainingDataSource,
    TrainingStatus,
)

__all__ = [
    # Config
    "ChatbotConfig",
    "ChatbotStatus",
    "ChatbotPersonality",
    "ChatbotProvider",
    # Intent/Entity
    "Intent",
    "IntentCategory",
    "IntentExample",
    "Entity",
    "EntityType",
    # Conversation
    "Conversation",
    "ConversationStatus",
    "ConversationChannel",
    "ConversationMessage",
    "ConversationContext",
    "MessageType",
    "MessageSender",
    "SentimentType",
    # Training
    "ChatbotTrainingJob",
    "TrainingStatus",
    "TrainingData",
    "TrainingDataSource",
    # Analytics
    "ChatbotAnalytics",
    "ConversationFeedback",
    "MetricPeriod",
]
