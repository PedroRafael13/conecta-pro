"""Recommendation Model - Recomendacoes IA.

Sprint 34 - AI Predictions.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from core.models import Base


class RecommendationType(StrEnum):
    """Tipo de recomendacao."""

    PRODUCT = "PRODUCT"  # Recomendacao de produto
    SERVICE = "SERVICE"  # Recomendacao de servico
    ACTION = "ACTION"  # Acao recomendada
    CONTENT = "CONTENT"  # Conteudo recomendado
    UPSELL = "UPSELL"  # Upsell
    CROSS_SELL = "CROSS_SELL"  # Cross-sell
    RETENTION = "RETENTION"  # Acao de retencao
    OPTIMIZATION = "OPTIMIZATION"  # Otimizacao
    ALERT = "ALERT"  # Alerta proativo
    INSIGHT = "INSIGHT"  # Insight de negocio
    NEXT_BEST_ACTION = "NEXT_BEST_ACTION"  # Proxima melhor acao


class RecommendationStatus(StrEnum):
    """Status da recomendacao."""

    PENDING = "PENDING"  # Pendente
    SHOWN = "SHOWN"  # Mostrada ao usuario
    CLICKED = "CLICKED"  # Clicada
    ACCEPTED = "ACCEPTED"  # Aceita
    REJECTED = "REJECTED"  # Rejeitada
    EXPIRED = "EXPIRED"  # Expirada
    CONVERTED = "CONVERTED"  # Converteu (gerou resultado)


class Recommendation(Base):
    """Recomendacao gerada por IA."""

    __tablename__ = "ai_recommendations"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Tipo e Status
    recommendation_type = Column(
        Enum(RecommendationType, name="recommendationtype", create_type=True),
        nullable=False,
        index=True,
    )
    status = Column(
        Enum(RecommendationStatus, name="recommendationstatus", create_type=True),
        nullable=False,
        default=RecommendationStatus.PENDING,
        index=True,
    )

    # Destinatario
    target_entity_type = Column(String(100), nullable=False, index=True)
    # Ex: "user", "client", "lead"
    target_entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Item recomendado
    recommended_entity_type = Column(String(100), nullable=True)
    # Ex: "product", "service", "contract"
    recommended_entity_id = Column(UUID(as_uuid=True), nullable=True)
    recommended_entity_name = Column(String(300), nullable=True)

    # Conteudo
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)  # Por que esta recomendacao
    action_text = Column(String(100), nullable=True)  # Ex: "Ver produto", "Entrar em contato"
    action_url = Column(String(500), nullable=True)

    # Scores
    relevance_score = Column(Float, nullable=True)  # 0-1
    confidence_score = Column(Float, nullable=True)  # 0-1
    priority_score = Column(Float, nullable=True)  # 0-100
    expected_value = Column(Float, nullable=True)  # Valor esperado se aceita

    # Ranking
    rank_position = Column(Integer, nullable=True)
    # Ex: 1 = primeira recomendacao
    total_recommendations = Column(Integer, nullable=True)
    # Ex: total de recomendacoes geradas para este usuario

    # Modelo
    model_id = Column(UUID(as_uuid=True), nullable=True)
    model_version = Column(String(50), nullable=True)
    algorithm = Column(String(100), nullable=True)
    # Ex: "collaborative_filtering", "content_based", "hybrid"

    # Contexto
    context = Column(JSONB, nullable=True)
    # Ex: {"page": "dashboard", "time_of_day": "morning", "user_segment": "premium"}
    user_features = Column(JSONB, nullable=True)
    # Ex: {"age": 35, "segment": "premium", "last_purchase_days": 30}
    item_features = Column(JSONB, nullable=True)
    # Ex: {"category": "security", "price": 500, "popularity": 0.8}

    # Explicabilidade
    explanation = Column(Text, nullable=True)
    similar_users_count = Column(Integer, nullable=True)
    # Quantos usuarios similares compraram
    feature_importance = Column(JSONB, nullable=True)

    # Validade
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Interacao
    shown_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    action_at = Column(DateTime(timezone=True), nullable=True)
    # Quando o usuario tomou acao

    # Feedback
    feedback = Column(String(50), nullable=True)
    # Ex: "helpful", "not_relevant", "already_have"
    feedback_text = Column(Text, nullable=True)
    feedback_at = Column(DateTime(timezone=True), nullable=True)

    # Conversao
    converted = Column(Boolean, default=False, nullable=False)
    conversion_value = Column(Float, nullable=True)
    conversion_at = Column(DateTime(timezone=True), nullable=True)
    conversion_entity_id = Column(UUID(as_uuid=True), nullable=True)
    # Ex: ID do pedido gerado

    # Experimento A/B
    experiment_id = Column(UUID(as_uuid=True), nullable=True)
    variant = Column(String(50), nullable=True)  # Ex: "control", "treatment_a"

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_personalized = Column(Boolean, default=True, nullable=False)
    is_realtime = Column(Boolean, default=False, nullable=False)

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

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        """Representacao string."""
        return (
            f"<Recommendation {self.recommendation_type.value} for {self.target_entity_type}:{self.target_entity_id}>"
        )

    @property
    def is_valid(self) -> bool:
        """Verifica se esta valida."""
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return self.active

    @property
    def is_shown(self) -> bool:
        """Verifica se foi mostrada."""
        return self.status != RecommendationStatus.PENDING

    @property
    def is_engaged(self) -> bool:
        """Verifica se houve engajamento."""
        return self.status in [
            RecommendationStatus.CLICKED,
            RecommendationStatus.ACCEPTED,
            RecommendationStatus.CONVERTED,
        ]

    @property
    def time_to_click_seconds(self) -> int | None:
        """Tempo ate o clique."""
        if not self.shown_at or not self.clicked_at:
            return None
        return int((self.clicked_at - self.shown_at).total_seconds())

    @property
    def time_to_conversion_seconds(self) -> int | None:
        """Tempo ate a conversao."""
        if not self.shown_at or not self.conversion_at:
            return None
        return int((self.conversion_at - self.shown_at).total_seconds())

    def mark_shown(self) -> None:
        """Marca como mostrada."""
        self.status = RecommendationStatus.SHOWN
        self.shown_at = datetime.utcnow()

    def mark_clicked(self) -> None:
        """Marca como clicada."""
        self.status = RecommendationStatus.CLICKED
        self.clicked_at = datetime.utcnow()

    def accept(self) -> None:
        """Marca como aceita."""
        self.status = RecommendationStatus.ACCEPTED
        self.action_at = datetime.utcnow()

    def reject(self, feedback: str | None = None, reason: str | None = None) -> None:
        """Rejeita a recomendacao.

        Args:
            feedback: Tipo de feedback.
            reason: Motivo detalhado.
        """
        self.status = RecommendationStatus.REJECTED
        self.action_at = datetime.utcnow()
        if feedback:
            self.feedback = feedback
        if reason:
            self.feedback_text = reason
        self.feedback_at = datetime.utcnow()

    def expire(self) -> None:
        """Marca como expirada."""
        self.status = RecommendationStatus.EXPIRED
        self.active = False

    def convert(
        self,
        value: float | None = None,
        entity_id: str | None = None,
    ) -> None:
        """Marca como convertida.

        Args:
            value: Valor da conversao.
            entity_id: ID da entidade gerada (ex: pedido).
        """
        self.status = RecommendationStatus.CONVERTED
        self.converted = True
        self.conversion_at = datetime.utcnow()
        if value is not None:
            self.conversion_value = value
        if entity_id:
            self.conversion_entity_id = entity_id

    def add_feedback(
        self,
        feedback_type: str,
        feedback_text: str | None = None,
    ) -> None:
        """Adiciona feedback.

        Args:
            feedback_type: Tipo de feedback.
            feedback_text: Texto do feedback.
        """
        self.feedback = feedback_type
        self.feedback_text = feedback_text
        self.feedback_at = datetime.utcnow()
