"""
Conversation AI Module - Sistema de IA Conversacional.

Este modulo implementa o sistema de chat inteligente com:
- Intent Classification
- Context Management
- LLM Integration (OpenAI/Claude)
- Response Generation
- Session/Message Management
- REST API Endpoints
"""

from modules.ai.conversation.services.conversation_engine import ConversationEngine
from modules.ai.conversation.services.intent_classifier import IntentClassifier
from modules.ai.conversation.services.context_manager import ContextManager
from modules.ai.conversation.services.llm_provider import LLMProvider
from modules.ai.conversation.services.response_generator import ResponseGenerator
from modules.ai.conversation.controllers.chat_controller import router as chat_router

__all__ = [
    "ConversationEngine",
    "IntentClassifier",
    "ContextManager",
    "LLMProvider",
    "ResponseGenerator",
    "chat_router",
]
