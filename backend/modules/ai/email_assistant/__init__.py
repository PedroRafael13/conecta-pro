"""
AI Email Assistant Module - Sprint 54.

Assistente inteligente para processamento de emails com:
- Classificacao automatica por categoria e prioridade
- Analise de sentimento e intencao
- Deteccao de spam e phishing
- Geracao automatica de respostas
- Templates e regras de processamento
"""

from modules.ai.email_assistant.models import (
    Email,
    EmailResponse,
    EmailTemplate,
    EmailRule,
    EmailStatusEnum,
    EmailCategoryEnum,
    EmailPriorityEnum,
    EmailSentimentEnum,
)
from modules.ai.email_assistant.services import (
    EmailClassifier,
    EmailResponder,
)
from modules.ai.email_assistant.repositories import EmailRepository
from modules.ai.email_assistant.controllers import router

__all__ = [
    # Models
    "Email",
    "EmailResponse",
    "EmailTemplate",
    "EmailRule",
    # Enums
    "EmailStatusEnum",
    "EmailCategoryEnum",
    "EmailPriorityEnum",
    "EmailSentimentEnum",
    # Services
    "EmailClassifier",
    "EmailResponder",
    # Repository
    "EmailRepository",
    # Router
    "router",
]
