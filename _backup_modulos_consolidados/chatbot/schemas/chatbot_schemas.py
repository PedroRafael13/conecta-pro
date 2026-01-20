"""Schemas Pydantic do módulo Chatbot IA.

Sprint 38 - Chatbot IA.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.ai.chatbot.models import (
    ChatbotPersonality,
    ChatbotProvider,
    ChatbotStatus,
    ConversationChannel,
    ConversationStatus,
    EntityType,
    IntentCategory,
    MessageSender,
    MessageType,
    SentimentType,
    TrainingDataSource,
    TrainingStatus,
)


# ============================================================================
# Chatbot Config Schemas
# ============================================================================


class ChatbotConfigBase(BaseModel):
    """Schema base para chatbot config."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    personality: ChatbotPersonality = ChatbotPersonality.PROFESSIONAL
    greeting_message: str = "Ola! Como posso ajudar?"
    fallback_message: str = "Desculpe, nao entendi. Pode reformular?"
    goodbye_message: str = "Obrigado pelo contato! Ate logo!"


class ChatbotCreateRequest(ChatbotConfigBase):
    """Request para criar chatbot."""

    provider: ChatbotProvider = ChatbotProvider.INTERNAL
    provider_config: Dict[str, Any] = Field(default_factory=dict)
    confidence_threshold: float = Field(default=0.7, ge=0, le=1)
    primary_language: str = "pt_BR"
    supported_languages: List[str] = Field(default_factory=lambda: ["pt_BR", "en_US"])
    enabled_channels: List[str] = Field(default_factory=lambda: ["web", "whatsapp"])
    enable_handoff: bool = True
    handoff_after_failures: int = Field(default=3, ge=1, le=10)


class ChatbotUpdateRequest(BaseModel):
    """Request para atualizar chatbot."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    personality: Optional[ChatbotPersonality] = None
    greeting_message: Optional[str] = None
    fallback_message: Optional[str] = None
    goodbye_message: Optional[str] = None
    status: Optional[ChatbotStatus] = None
    provider: Optional[ChatbotProvider] = None
    provider_config: Optional[Dict[str, Any]] = None
    confidence_threshold: Optional[float] = Field(None, ge=0, le=1)
    enabled_channels: Optional[List[str]] = None
    business_hours: Optional[Dict[str, Any]] = None
    quick_replies: Optional[List[Dict[str, Any]]] = None


class ChatbotResponse(ChatbotConfigBase):
    """Response de chatbot."""

    id: UUID
    tenant_id: UUID
    status: ChatbotStatus
    provider: ChatbotProvider
    model_version: Optional[str]
    model_accuracy: Optional[float]
    total_conversations: int
    total_messages: int
    resolution_rate: Optional[float]
    satisfaction_score: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Intent Schemas
# ============================================================================


class IntentSlotSchema(BaseModel):
    """Schema para slot de intent."""

    name: str
    entity: str
    required: bool = False
    prompt: Optional[str] = None
    default: Optional[Any] = None


class IntentCreateRequest(BaseModel):
    """Request para criar intent."""

    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z_][a-z0-9_]*$")
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: IntentCategory = IntentCategory.CUSTOM
    training_phrases: List[str] = Field(default_factory=list)
    responses: List[str] = Field(default_factory=list)
    action: Optional[str] = None
    action_config: Dict[str, Any] = Field(default_factory=dict)
    input_contexts: List[str] = Field(default_factory=list)
    output_contexts: List[str] = Field(default_factory=list)
    slots: List[IntentSlotSchema] = Field(default_factory=list)
    priority: int = Field(default=50, ge=0, le=100)
    requires_confirmation: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida nome do intent."""
        if v and not v[0].isalpha() and v[0] != "_":
            raise ValueError("Nome deve comecar com letra ou underscore")
        return v.lower()


class IntentUpdateRequest(BaseModel):
    """Request para atualizar intent."""

    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[IntentCategory] = None
    training_phrases: Optional[List[str]] = None
    responses: Optional[List[str]] = None
    action: Optional[str] = None
    action_config: Optional[Dict[str, Any]] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    active: Optional[bool] = None


class IntentResponse(BaseModel):
    """Response de intent."""

    id: UUID
    chatbot_id: UUID
    name: str
    display_name: Optional[str]
    description: Optional[str]
    category: IntentCategory
    training_phrases: List[str]
    responses: List[str]
    action: Optional[str]
    slots: List[Dict[str, Any]]
    priority: int
    total_matches: int
    avg_confidence: Optional[float]
    is_trained: bool
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Entity Schemas
# ============================================================================


class EntityValueSchema(BaseModel):
    """Schema para valor de entidade."""

    value: str
    synonyms: List[str] = Field(default_factory=list)


class EntityCreateRequest(BaseModel):
    """Request para criar entidade."""

    name: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z_][a-z0-9_]*$")
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    entity_type: EntityType = EntityType.CUSTOM
    values: List[EntityValueSchema] = Field(default_factory=list)
    regex_pattern: Optional[str] = None
    enable_fuzzy: bool = True
    fuzzy_threshold: float = Field(default=0.8, ge=0, le=1)


class EntityResponse(BaseModel):
    """Response de entidade."""

    id: UUID
    chatbot_id: UUID
    name: str
    display_name: Optional[str]
    entity_type: EntityType
    values: List[Dict[str, Any]]
    total_extractions: int
    is_trained: bool
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Conversation Schemas
# ============================================================================


class SendMessageRequest(BaseModel):
    """Request para enviar mensagem ao chatbot."""

    text: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    channel: ConversationChannel = ConversationChannel.WEB
    user_id: Optional[UUID] = None
    visitor_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """Response de mensagem do chatbot."""

    message_id: str
    conversation_id: str
    text: Optional[str]
    message_type: MessageType
    sender: MessageSender
    intent: Optional[str]
    intent_confidence: Optional[float]
    entities: List[Dict[str, Any]]
    sentiment: Optional[SentimentType]
    buttons: List[Dict[str, Any]]
    quick_replies: List[Dict[str, Any]]
    attachments: List[Dict[str, Any]]
    action_triggered: Optional[str]
    action_result: Optional[Dict[str, Any]]
    is_fallback: bool
    response_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response de conversa."""

    id: UUID
    conversation_id: str
    chatbot_id: UUID
    channel: ConversationChannel
    status: ConversationStatus
    user_name: Optional[str]
    user_email: Optional[str]
    total_messages: int
    overall_sentiment: Optional[SentimentType]
    is_resolved: bool
    satisfaction_rating: Optional[int]
    started_at: datetime
    last_activity_at: Optional[datetime]
    duration_seconds: Optional[int]

    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Response detalhada de conversa."""

    messages: List[MessageResponse]
    detected_intents: List[Dict[str, Any]]
    extracted_entities: Dict[str, Any]
    current_context: Dict[str, Any]
    tags: List[str]


# ============================================================================
# NLU Schemas
# ============================================================================


class NLURequest(BaseModel):
    """Request para analise NLU."""

    text: str = Field(..., min_length=1, max_length=4000)
    context: Dict[str, Any] = Field(default_factory=dict)
    language: Optional[str] = None
    include_sentiment: bool = True
    include_entities: bool = True


class DetectedIntent(BaseModel):
    """Intent detectado."""

    name: str
    confidence: float
    display_name: Optional[str]
    category: Optional[str]


class ExtractedEntity(BaseModel):
    """Entidade extraida."""

    entity: str
    value: str
    original_value: str
    confidence: float
    start: int
    end: int


class NLUResponse(BaseModel):
    """Response de analise NLU."""

    text: str
    normalized_text: str
    language: str
    intents: List[DetectedIntent]
    top_intent: Optional[DetectedIntent]
    entities: List[ExtractedEntity]
    sentiment: Optional[SentimentType]
    sentiment_score: Optional[float]
    is_ambiguous: bool
    processing_time_ms: int


# ============================================================================
# Training Schemas
# ============================================================================


class TrainingDataCreateRequest(BaseModel):
    """Request para criar dado de treinamento."""

    intent_name: str
    text: str = Field(..., min_length=1, max_length=4000)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    language: str = "pt_BR"
    source: TrainingDataSource = TrainingDataSource.MANUAL


class TrainingDataBulkRequest(BaseModel):
    """Request para importar dados em massa."""

    data: List[TrainingDataCreateRequest]
    validate_duplicates: bool = True


class TrainChatbotRequest(BaseModel):
    """Request para treinar chatbot."""

    name: Optional[str] = None
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    intents: Optional[List[str]] = None  # Se None, treina todos


class TrainingJobResponse(BaseModel):
    """Response de job de treinamento."""

    id: UUID
    job_id: str
    chatbot_id: UUID
    status: TrainingStatus
    progress_percent: float
    training_accuracy: Optional[float]
    validation_accuracy: Optional[float]
    f1_score: Optional[float]
    model_version: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# Analytics Schemas
# ============================================================================


class AnalyticsRequest(BaseModel):
    """Request para analytics."""

    start_date: datetime
    end_date: datetime
    channel: Optional[str] = None
    intent: Optional[str] = None
    granularity: str = Field(default="daily", pattern=r"^(hourly|daily|weekly|monthly)$")


class AnalyticsSummaryResponse(BaseModel):
    """Response de resumo de analytics."""

    total_conversations: int
    total_messages: int
    unique_users: int
    avg_satisfaction: Optional[float]
    resolution_rate: Optional[float]
    handoff_rate: Optional[float]
    fallback_rate: Optional[float]
    avg_response_time_ms: Optional[int]
    avg_conversation_duration: Optional[int]
    top_intents: List[Dict[str, Any]]
    sentiment_distribution: Dict[str, int]


class FeedbackCreateRequest(BaseModel):
    """Request para criar feedback."""

    conversation_id: UUID
    message_id: Optional[UUID] = None
    feedback_type: str = Field(..., pattern=r"^(rating|helpful|not_helpful|wrong_intent|suggestion)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_positive: Optional[bool] = None
    corrected_intent: Optional[str] = None
    suggested_response: Optional[str] = None
    comment: Optional[str] = Field(None, max_length=1000)


# ============================================================================
# Handoff Schemas
# ============================================================================


class HandoffRequest(BaseModel):
    """Request para transferir para humano."""

    conversation_id: str
    reason: Optional[str] = None
    queue_id: Optional[UUID] = None
    priority: str = Field(default="normal", pattern=r"^(low|normal|high|urgent)$")
    notes: Optional[str] = None


class HandoffResponse(BaseModel):
    """Response de handoff."""

    success: bool
    conversation_id: str
    queue_id: Optional[UUID]
    queue_position: Optional[int]
    estimated_wait_time: Optional[int]
    message: str
