"""Prediction Model - Previsoes IA.

Sprint 34 - AI Predictions.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class PredictionType(str, enum.Enum):
    """Tipo de previsao."""

    CHURN = "CHURN"  # Previsao de churn
    REVENUE_FORECAST = "REVENUE_FORECAST"  # Forecast de receita
    EXPENSE_FORECAST = "EXPENSE_FORECAST"  # Forecast de despesa
    DEMAND_FORECAST = "DEMAND_FORECAST"  # Forecast de demanda
    LEAD_SCORING = "LEAD_SCORING"  # Scoring de leads
    CREDIT_RISK = "CREDIT_RISK"  # Risco de credito
    ANOMALY = "ANOMALY"  # Deteccao de anomalia
    CLASSIFICATION = "CLASSIFICATION"  # Classificacao generica
    REGRESSION = "REGRESSION"  # Regressao generica
    RECOMMENDATION = "RECOMMENDATION"  # Recomendacao
    SENTIMENT = "SENTIMENT"  # Analise de sentimento
    CLUSTER = "CLUSTER"  # Clusterizacao


class PredictionStatus(str, enum.Enum):
    """Status da previsao."""

    PENDING = "PENDING"  # Aguardando processamento
    PROCESSING = "PROCESSING"  # Em processamento
    COMPLETED = "COMPLETED"  # Concluida
    FAILED = "FAILED"  # Falhou
    EXPIRED = "EXPIRED"  # Expirada
    INVALIDATED = "INVALIDATED"  # Invalidada manualmente


class Prediction(Base):
    """Previsao gerada por modelo de IA."""

    __tablename__ = "ai_predictions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Modelo usado
    model_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_ml_models.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Tipo e Status
    prediction_type = Column(
        Enum(PredictionType, name="predictiontype", create_type=True),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(PredictionStatus, name="predictionstatus", create_type=True),
        nullable=False,
        default=PredictionStatus.PENDING,
        index=True,
    )

    # Entidade alvo
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Resultado
    prediction_value = Column(Float, nullable=True)  # Valor numerico
    prediction_label = Column(String(100), nullable=True)  # Label/classe
    prediction_probabilities = Column(JSONB, nullable=True)  # Ex: {"churn": 0.8, "retain": 0.2}
    confidence_score = Column(Float, nullable=True)  # Confianca (0-1)

    # Detalhes
    features_used = Column(JSONB, nullable=True)  # Features usadas
    feature_importance = Column(JSONB, nullable=True)  # Importancia de cada feature
    explanation = Column(Text, nullable=True)  # Explicacao em texto
    shap_values = Column(JSONB, nullable=True)  # SHAP values para explicabilidade

    # Metadados
    model_version = Column(String(50), nullable=True)
    algorithm = Column(String(100), nullable=True)
    threshold_used = Column(Float, nullable=True)

    # Cenarios (para forecast)
    scenarios = Column(JSONB, nullable=True)  # Ex: {"pessimist": 100, "base": 150, "optimist": 200}

    # Validade
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Feedback
    actual_value = Column(Float, nullable=True)  # Valor real (para avaliacao)
    actual_label = Column(String(100), nullable=True)  # Label real
    feedback_at = Column(DateTime(timezone=True), nullable=True)
    feedback_by = Column(UUID(as_uuid=True), nullable=True)
    feedback_notes = Column(Text, nullable=True)

    # Metricas de erro (apos feedback)
    absolute_error = Column(Float, nullable=True)
    percentage_error = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)

    # Processamento
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_batch = Column(Boolean, default=False, nullable=False)
    batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    requested_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    model = relationship("MLModel", back_populates="predictions", lazy="selectin")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Prediction {self.prediction_type.value} for {self.entity_type}:{self.entity_id}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se esta concluida."""
        return self.status == PredictionStatus.COMPLETED

    @property
    def is_valid(self) -> bool:
        """Verifica se esta valida (dentro do periodo)."""
        if not self.is_completed:
            return False
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return True

    @property
    def has_feedback(self) -> bool:
        """Verifica se tem feedback."""
        return self.actual_value is not None or self.actual_label is not None

    @property
    def accuracy(self) -> Optional[float]:
        """Calcula precisao (para classificacao)."""
        if self.is_correct is not None:
            return 1.0 if self.is_correct else 0.0
        return None

    def complete(
        self,
        value: Optional[float] = None,
        label: Optional[str] = None,
        confidence: Optional[float] = None,
        probabilities: Optional[dict] = None,
        processing_time_ms: Optional[int] = None,
    ) -> None:
        """Marca previsao como concluida.

        Args:
            value: Valor numerico previsto.
            label: Label/classe prevista.
            confidence: Score de confianca.
            probabilities: Probabilidades por classe.
            processing_time_ms: Tempo de processamento.
        """
        self.status = PredictionStatus.COMPLETED
        self.prediction_value = value
        self.prediction_label = label
        self.confidence_score = confidence
        self.prediction_probabilities = probabilities
        self.processing_time_ms = processing_time_ms
        self.completed_at = datetime.utcnow()

    def fail(self, error_message: str) -> None:
        """Marca previsao como falha.

        Args:
            error_message: Mensagem de erro.
        """
        self.status = PredictionStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()

    def invalidate(self) -> None:
        """Invalida a previsao."""
        self.status = PredictionStatus.INVALIDATED
        self.active = False

    def expire(self) -> None:
        """Marca como expirada."""
        self.status = PredictionStatus.EXPIRED
        self.active = False

    def add_feedback(
        self,
        actual_value: Optional[float] = None,
        actual_label: Optional[str] = None,
        user_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Adiciona feedback real.

        Args:
            actual_value: Valor real observado.
            actual_label: Label real observada.
            user_id: ID do usuario que deu feedback.
            notes: Notas adicionais.
        """
        self.actual_value = actual_value
        self.actual_label = actual_label
        self.feedback_at = datetime.utcnow()
        if user_id:
            self.feedback_by = user_id
        self.feedback_notes = notes

        # Calcula erro para valores numericos
        if actual_value is not None and self.prediction_value is not None:
            self.absolute_error = abs(actual_value - self.prediction_value)
            if actual_value != 0:
                self.percentage_error = (
                    abs((actual_value - self.prediction_value) / actual_value) * 100
                )

        # Verifica se esta correto para classificacao
        if actual_label is not None and self.prediction_label is not None:
            self.is_correct = actual_label.lower() == self.prediction_label.lower()

    def get_top_features(self, top_n: int = 5) -> list:
        """Retorna as features mais importantes.

        Args:
            top_n: Numero de features a retornar.

        Returns:
            Lista de features ordenadas por importancia.
        """
        if not self.feature_importance:
            return []
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        return sorted_features[:top_n]
