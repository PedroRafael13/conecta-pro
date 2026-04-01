"""
AI Email Assistant Schemas - Sprint 54.
"""

from modules.ai.email_assistant.schemas.email_schemas import (
    EmailAnalysisRequest,
    # Dashboard
    EmailAssistantDashboard,
    EmailCategoryEnum,
    EmailClassificationResult,
    # Email
    EmailCreate,
    EmailListResponse,
    EmailPriorityEnum,
    EmailResponse,
    # Response
    EmailResponseCreate,
    EmailResponseOut,
    # Rule
    EmailRuleCreate,
    EmailRuleResponse,
    EmailRuleUpdate,
    EmailSentimentEnum,
    # Enums
    EmailStatusEnum,
    # Template
    EmailTemplateCreate,
    EmailTemplateResponse,
    EmailTemplateUpdate,
    EmailUpdate,
    GenerateReplyRequest,
    GenerateReplyResponse,
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
