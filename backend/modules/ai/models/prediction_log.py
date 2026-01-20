"""PredictionLog Model - Logs de Previsoes.

Sprint 34 - AI Predictions.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class PredictionLog(Base):
    """Log detalhado de previsao."""

    __tablename__ = "ai_prediction_logs"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Previsao
    prediction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_predictions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Modelo
    model_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    model_version = Column(String(50), nullable=True)

    # Request
    request_id = Column(String(100), nullable=True, index=True)
    request_source = Column(String(100), nullable=True)
    # Ex: "api", "batch", "workflow", "scheduled"
    request_ip = Column(String(45), nullable=True)
    request_user_agent = Column(String(500), nullable=True)

    # Input
    input_features = Column(JSONB, nullable=True)
    input_raw = Column(JSONB, nullable=True)  # Dados brutos antes de transformacao
    preprocessing_steps = Column(JSONB, nullable=True)
    # Ex: ["normalize", "encode_categorical", "fill_nulls"]

    # Output
    output_raw = Column(JSONB, nullable=True)  # Output bruto do modelo
    output_processed = Column(JSONB, nullable=True)  # Output processado
    probabilities = Column(JSONB, nullable=True)

    # Performance
    preprocessing_time_ms = Column(Integer, nullable=True)
    inference_time_ms = Column(Integer, nullable=True)
    postprocessing_time_ms = Column(Integer, nullable=True)
    total_time_ms = Column(Integer, nullable=True)

    # Qualidade
    confidence_score = Column(Float, nullable=True)
    uncertainty_score = Column(Float, nullable=True)

    # Explicabilidade
    feature_importance = Column(JSONB, nullable=True)
    shap_values = Column(JSONB, nullable=True)
    lime_explanation = Column(JSONB, nullable=True)

    # Cache
    cache_hit = Column(String(20), nullable=True)
    # Ex: "hit", "miss", "expired"
    cache_key = Column(String(200), nullable=True)

    # Erros
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)

    # Metadados
    extra_metadata = Column("metadata", JSONB, nullable=True)
    # Ex: {"batch_id": "...", "experiment_id": "..."}

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<PredictionLog {self.prediction_id}>"

    @property
    def is_successful(self) -> bool:
        """Verifica se foi sucesso."""
        return self.error_code is None

    @property
    def is_cached(self) -> bool:
        """Verifica se veio do cache."""
        return self.cache_hit == "hit"

    def get_total_time(self) -> int:
        """Retorna tempo total."""
        if self.total_time_ms:
            return self.total_time_ms
        return (
            (self.preprocessing_time_ms or 0)
            + (self.inference_time_ms or 0)
            + (self.postprocessing_time_ms or 0)
        )
