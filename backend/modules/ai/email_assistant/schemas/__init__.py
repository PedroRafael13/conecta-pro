"""
AI Email Assistant Schemas - Sprint 54.
"""

from modules.ai.email_assistant.schemas.email_schemas import (
    # Enums
    EmailStatusEnum,
    EmailCategoryEnum,
    EmailPriorityEnum,
    EmailSentimentEnum,
    # Email
    EmailCreate,
    EmailUpdate,
    EmailResponse,
    EmailListResponse,
    EmailClassificationResult,
    EmailAnalysisRequest,
    # Response
    EmailResponseCreate,
    EmailResponseOut,
    GenerateReplyRequest,
    GenerateReplyResponse,
    # Template
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    # Rule
    EmailRuleCreate,
    EmailRuleUpdate,
    EmailRuleResponse,
    # Dashboard
    EmailAssistantDashboard,
)

__all__ = [
    # Enums
    "EmailStatusEnum",
    "EmailCategoryEnum",
    "EmailPriorityEnum",
    "EmailSentimentEnum",
    # Email
    "EmailCreate",
    "EmailUpdate",
    "EmailResponse",
    "EmailListResponse",
    "EmailClassificationResult",
    "EmailAnalysisRequest",
    # Response
    "EmailResponseCreate",
    "EmailResponseOut",
    "GenerateReplyRequest",
    "GenerateReplyResponse",
    # Template
    "EmailTemplateCreate",
    "EmailTemplateUpdate",
    "EmailTemplateResponse",
    # Rule
    "EmailRuleCreate",
    "EmailRuleUpdate",
    "EmailRuleResponse",
    # Dashboard
    "EmailAssistantDashboard",
]
