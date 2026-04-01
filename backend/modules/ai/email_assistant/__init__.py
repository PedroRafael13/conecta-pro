"""
AI Email Assistant Module - Sprint 54.

Assistente inteligente para processamento de emails com:
- Classificacao automatica por categoria e prioridade
- Analise de sentimento e intencao
- Deteccao de spam e phishing
- Geracao automatica de respostas
- Templates e regras de processamento
"""

from modules.ai.email_assistant.controllers import router
from modules.ai.email_assistant.models import (
    AIEmailTemplate,
    Email,
    EmailCategoryEnum,
    EmailPriorityEnum,
    EmailResponse,
    EmailRule,
    EmailSentimentEnum,
    EmailStatusEnum,
)
from modules.ai.email_assistant.repositories import EmailRepository
from modules.ai.email_assistant.services import (
    EmailClassifier,
    EmailResponder,
)

__all__ = [
    # Models
    "AIEmailTemplate",
    "Email",
    "EmailResponse",
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
