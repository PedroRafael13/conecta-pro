"""
modules/fase5/email_intelligence/__init__.py - Email Intelligence Module
========================================================================
Motor de inteligencia para emails com NLP e contextualizacao
"""

from .enums import EmailCategory, EmailIntent, EmailPriority, SentimentType
from .models import EmailAnalysis, EmailContext, EmailMessage, EmailSuggestion, EmailThread
from .service import EmailIntelligenceService

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
    "SentimentType",
]
