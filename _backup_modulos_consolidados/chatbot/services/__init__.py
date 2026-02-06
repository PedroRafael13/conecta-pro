"""Services do módulo Chatbot IA.

Sprint 38 - Chatbot IA.
"""

from modules.ai.chatbot.services.chatbot_service import (
    ChatbotService,
    ChatMessage,
    ConversationSession,
)
from modules.ai.chatbot.services.dialog_manager import (
    DialogAction,
    DialogContext,
    DialogManager,
    DialogResponse,
)
from modules.ai.chatbot.services.nlu_service import (
    DetectedIntent,
    ExtractedEntity,
    NLUResult,
    NLUService,
)

__all__ = [
    # NLU Service
    "NLUService",
    "NLUResult",
    "DetectedIntent",
    "ExtractedEntity",
    # Dialog Manager
    "DialogManager",
    "DialogContext",
    "DialogAction",
    "DialogResponse",
    # Chatbot Service
    "ChatbotService",
    "ChatMessage",
    "ConversationSession",
]
