"""Training e Analytics Models - Treinamento e Metricas do Chatbot.

Sprint 38 - Chatbot IA.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models.base import Base


class TrainingStatus(str, enum.Enum):
    """Status do treinamento."""

    PENDING = "pending"
    QUEUED = "queued"
    PREPROCESSING = "preprocessing"
    TRAINING = "training"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingDataSource(str, enum.Enum):
    """Fonte dos dados de treinamento."""

    MANUAL = "manual"
    IMPORTED = "imported"
    CONVERSATION = "conversation"
    FEEDBACK = "feedback"
    AUGMENTED = "augmented"
    SYNTHETIC = "synthetic"


class MetricPeriod(str, enum.Enum):
    """Periodo da metrica."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ChatbotTrainingJob(Base):
    """Modelo de job de treinamento do chatbot."""

    __tablename__ = "chatbot_training_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    job_id = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200))
    description = Column(Text)

    # Status
    status = Column(Enum(TrainingStatus), default=TrainingStatus.PENDING, index=True)
    status_message = Column(Text)
    progress_percent = Column(Float, default=0)

    # Configuracao
    config = Column(JSONB, default={})
    # Estrutura: {
    #   "model_type": "intent_classifier",
    #   "epochs": 100,
    #   "batch_size": 32,
    #   "learning_rate": 0.001,
    #   "validation_split": 0.2
    # }

    # Dados de entrada
    training_data_count = Column(Integer, default=0)
    validation_data_count = Column(Integer, default=0)
    intents_count = Column(Integer, default=0)
    entities_count = Column(Integer, default=0)

    # Versao do modelo
    model_version = Column(String(50))
    previous_version = Column(String(50))
    is_active_version = Column(Boolean, default=False)

    # Metricas de treinamento
    training_loss = Column(Float)
    validation_loss = Column(Float)
    training_accuracy = Column(Float)
    validation_accuracy = Column(Float)
    f1_score = Column(Float)
    precision = Column(Float)
    recall = Column(Float)

    # Metricas por intent
    intent_metrics = Column(JSONB, default={})
    # Estrutura: {
    #   "greeting": {"precision": 0.95, "recall": 0.92, "f1": 0.93, "support": 150},
    #   "schedule": {"precision": 0.88, "recall": 0.85, "f1": 0.86, "support": 80}
    # }

    # Confusion matrix
    confusion_matrix = Column(JSONB)

    # Tempos
    queued_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Artefatos
    model_path = Column(String(500))  # Caminho do modelo salvo
    logs_path = Column(String(500))
    artifacts = Column(JSONB, default={})

    # Erro
    error_code = Column(String(50))
    error_message = Column(Text)
    error_details = Column(JSONB)

    # Deploy
    is_deployed = Column(Boolean, default=False)
    deployed_at = Column(DateTime)
    deployed_by = Column(UUID(as_uuid=True))

    # Controle
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ChatbotTrainingJob {self.job_id} ({self.status.value})>"


class TrainingData(Base):
    """Modelo de dados de treinamento."""

    __tablename__ = "chatbot_training_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Referencia
    intent_id = Column(UUID(as_uuid=True), index=True)
    intent_name = Column(String(100), index=True)

    # Texto
    text = Column(Text, nullable=False)
    normalized_text = Column(Text)
    language = Column(String(10), default="pt_BR")

    # Entidades anotadas
    entities = Column(JSONB, default=[])
    # Estrutura: [
    #   {"entity": "date", "value": "amanha", "start": 10, "end": 16}
    # ]

    # Fonte
    source = Column(Enum(TrainingDataSource), default=TrainingDataSource.MANUAL)
    source_id = Column(String(200))  # ID da origem
    source_url = Column(String(500))

    # Qualidade
    is_validated = Column(Boolean, default=False)
    validated_by = Column(UUID(as_uuid=True))
    validated_at = Column(DateTime)
    quality_score = Column(Float)  # 0-1

    # Deduplicacao
    text_hash = Column(String(64), index=True)  # Hash para detectar duplicatas
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(UUID(as_uuid=True))

    # Uso em treinamento
    used_in_training = Column(Boolean, default=False)
    training_job_id = Column(UUID(as_uuid=True))
    is_in_validation_set = Column(Boolean, default=False)

    # Feedback
    feedback_positive = Column(Integer, default=0)
    feedback_negative = Column(Integer, default=0)

    # Metadata
    extra_data = Column(JSONB, default={})

    # Controle
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<TrainingData {self.text[:30]}...>"


class ChatbotAnalytics(Base):
    """Modelo de analytics do chatbot."""

    __tablename__ = "chatbot_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Periodo
    period = Column(Enum(MetricPeriod), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Dimensoes (opcional)
    channel = Column(String(50), index=True)
    language = Column(String(10))
    intent = Column(String(100))

    # Metricas de conversa
    total_conversations = Column(Integer, default=0)
    new_conversations = Column(Integer, default=0)
    returning_conversations = Column(Integer, default=0)
    active_conversations = Column(Integer, default=0)

    # Metricas de mensagem
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    bot_messages = Column(Integer, default=0)
    agent_messages = Column(Integer, default=0)

    # Metricas de intent
    total_intents_detected = Column(Integer, default=0)
    unique_intents = Column(Integer, default=0)
    avg_intent_confidence = Column(Float)
    fallback_count = Column(Integer, default=0)
    fallback_rate = Column(Float)

    # Top intents
    top_intents = Column(JSONB, default=[])
    # Estrutura: [
    #   {"intent": "greeting", "count": 150, "confidence": 0.92},
    #   {"intent": "schedule", "count": 80, "confidence": 0.85}
    # ]

    # Metricas de entidade
    total_entities_extracted = Column(Integer, default=0)
    entity_breakdown = Column(JSONB, default={})

    # Metricas de handoff
    handoff_count = Column(Integer, default=0)
    handoff_rate = Column(Float)
    handoff_reasons = Column(JSONB, default={})

    # Metricas de resolucao
    resolved_by_bot = Column(Integer, default=0)
    resolved_by_agent = Column(Integer, default=0)
    unresolved = Column(Integer, default=0)
    resolution_rate = Column(Float)

    # Metricas de tempo
    avg_response_time_ms = Column(Integer)
    avg_conversation_duration_seconds = Column(Integer)
    avg_messages_per_conversation = Column(Float)

    # Metricas de satisfacao
    total_ratings = Column(Integer, default=0)
    avg_satisfaction = Column(Float)
    satisfaction_distribution = Column(JSONB, default={})
    # Estrutura: {"1": 5, "2": 10, "3": 50, "4": 100, "5": 150}

    # Metricas de sentimento
    sentiment_distribution = Column(JSONB, default={})
    # Estrutura: {"very_positive": 10, "positive": 30, "neutral": 50, "negative": 8, "very_negative": 2}
    avg_sentiment_score = Column(Float)

    # Metricas por hora (para DAILY)
    hourly_breakdown = Column(JSONB, default={})

    # Usuarios
    unique_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)

    # Controle
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ChatbotAnalytics {self.period.value} {self.period_start}>"


class ConversationFeedback(Base):
    """Modelo de feedback de conversa."""

    __tablename__ = "chatbot_conversation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    message_id = Column(UUID(as_uuid=True), index=True)

    # Tipo de feedback
    feedback_type = Column(String(50), nullable=False)
    # Tipos: rating, helpful, not_helpful, wrong_intent, wrong_entity, suggestion

    # Valor
    rating = Column(Integer)  # 1-5 para rating
    is_positive = Column(Boolean)  # True/False para helpful
    selected_option = Column(String(100))

    # Correcao
    corrected_intent = Column(String(100))
    corrected_entities = Column(JSONB)
    suggested_response = Column(Text)

    # Comentario
    comment = Column(Text)

    # Contexto
    original_intent = Column(String(100))
    original_confidence = Column(Float)
    original_response = Column(Text)

    # Usuario
    user_id = Column(UUID(as_uuid=True))
    is_anonymous = Column(Boolean, default=True)

    # Processamento
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    created_training_data = Column(Boolean, default=False)

    # Metadata
    extra_data = Column(JSONB, default={})

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ConversationFeedback {self.feedback_type}>"
