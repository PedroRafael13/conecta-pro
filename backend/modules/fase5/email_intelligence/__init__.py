"""
modules/fase5/email_intelligence/__init__.py - Email Intelligence Module
========================================================================
Motor de inteligencia para emails com NLP e contextualizacao
"""

from .service import EmailIntelligenceService
from .models import (
    EmailMessage,
    EmailThread,
    EmailAnalysis,
    EmailSuggestion,
    EmailContext
)
from .enums import (
    EmailCategory,
    EmailPriority,
    EmailIntent,
    SentimentType
)

__all__ = [
    "EmailIntelligenceService",
    "EmailMessage",
    "EmailThread",
    "EmailAnalysis",
    "EmailSuggestion",
    "EmailContext",
    "EmailCategory",
    "EmailPriority",
    "EmailIntent",
    "SentimentType"
]
