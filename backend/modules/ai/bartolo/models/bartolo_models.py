"""
Models SQLAlchemy para persistencia do Bartolo.

Armazena interacoes, feedbacks e padroes aprendidos
para que o aprendizado sobreviva a reinicializacoes.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from core.models.base import Base


class BartoloInteraction(Base):
    """
    Registro de interacao do Bartolo com usuario.

    Armazena mensagem, resposta, intent detectado, agente usado,
    feedback do usuario e metricas de processamento.
    """
    __tablename__ = "bartolo_interactions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Contexto da interacao
    user_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)

    # Mensagem e resposta
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_summary = Column(String(500), nullable=True)

    # Classificacao
    intent_detected = Column(String(100), nullable=True, index=True)
    agent_used = Column(String(100), nullable=True, index=True)
    module = Column(String(100), nullable=True)
    wizard_type = Column(String(100), nullable=True)
    query_type = Column(String(100), nullable=True)

    # Feedback
    feedback_type = Column(String(50), nullable=True, index=True)
    feedback_score = Column(Integer, nullable=True)
    feedback_text = Column(Text, nullable=True)

    # Metricas
    processing_time_ms = Column(Integer, nullable=True, default=0)
    model_used = Column(String(100), nullable=True)

    # Metadados extras
    metadata = Column(JSONB, nullable=True, default=dict)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    is_active = Column(Boolean, nullable=False, default=True)

    # Indices compostos para queries frequentes
    __table_args__ = (
        Index("ix_bartolo_interactions_user_created", "user_id", "created_at"),
        Index("ix_bartolo_interactions_session", "session_id", "created_at"),
        Index(
            "ix_bartolo_interactions_feedback",
            "feedback_type",
            "created_at",
        ),
        Index(
            "ix_bartolo_interactions_intent_agent",
            "intent_detected",
            "agent_used",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<BartoloInteraction(id={self.id}, user_id={self.user_id}, "
            f"intent={self.intent_detected})>"
        )


class BartoloLearning(Base):
    """
    Padrao aprendido pelo Bartolo.

    Armazena padroes identificados a partir de interacoes,
    como saudacoes frequentes, queries comuns, etc.
    """
    __tablename__ = "bartolo_learnings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identificacao do padrao
    pattern_type = Column(String(100), nullable=False, index=True)
    pattern_key = Column(String(200), nullable=False, unique=True, index=True)
    trigger = Column(String(200), nullable=True)

    # Metricas do padrao
    frequency = Column(Integer, nullable=False, default=1)
    success_rate = Column(Float, nullable=False, default=0.0)
    confidence = Column(Float, nullable=False, default=0.5)

    # Template de resposta (para padroes com resposta conhecida)
    response_template = Column(Text, nullable=True)
    action = Column(String(200), nullable=True)

    # Metadados extras (JSONB para flexibilidade)
    metadata = Column(JSONB, nullable=True, default=dict)

    # Timestamps
    last_seen = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    is_active = Column(Boolean, nullable=False, default=True)

    # Indices compostos
    __table_args__ = (
        Index("ix_bartolo_learnings_type_freq", "pattern_type", "frequency"),
        Index(
            "ix_bartolo_learnings_type_success",
            "pattern_type",
            "success_rate",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<BartoloLearning(id={self.id}, type={self.pattern_type}, "
            f"key={self.pattern_key}, freq={self.frequency})>"
        )
