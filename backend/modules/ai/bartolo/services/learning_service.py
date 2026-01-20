"""
Learning Service - Servico de Aprendizado Continuo.

Permite ao Bartolo aprender com interacoes e melhorar respostas.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4
from enum import Enum

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Tipo de feedback."""
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    TOO_LONG = "too_long"
    TOO_SHORT = "too_short"
    OFF_TOPIC = "off_topic"


class LearningEventType(str, Enum):
    """Tipo de evento de aprendizado."""
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    SUCCESSFUL_WIZARD = "successful_wizard"
    FAILED_WIZARD = "failed_wizard"
    QUERY_PATTERN = "query_pattern"
    USER_CORRECTION = "user_correction"


@dataclass
class Interaction:
    """Registro de interacao."""
    id: UUID
    user_id: int
    session_id: str
    message: str
    response: str
    intent: Optional[str] = None
    module: Optional[str] = None
    wizard_type: Optional[str] = None
    feedback: Optional[FeedbackType] = None
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    processing_time_ms: int = 0
    created_at: datetime = None
    metadata: dict = field(default_factory=dict)


@dataclass
class LearningEvent:
    """Evento de aprendizado."""
    id: UUID
    event_type: LearningEventType
    interaction_id: Optional[UUID] = None
    user_id: Optional[int] = None
    data: dict = field(default_factory=dict)
    created_at: datetime = None


@dataclass
class LearnedPattern:
    """Padrao aprendido."""
    id: UUID
    pattern_type: str
    trigger: str
    response_template: Optional[str] = None
    action: Optional[str] = None
    confidence: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None


class LearningService:
    """
    Servico de aprendizado continuo.

    Responsavel por:
    - Registrar interacoes
    - Coletar feedback
    - Identificar padroes
    - Melhorar respostas ao longo do tempo
    """

    def __init__(self):
        """Inicializa o servico."""
        self._interactions: list[Interaction] = []
        self._events: list[LearningEvent] = []
        self._patterns: dict[str, LearnedPattern] = {}

        # Metricas
        self._total_interactions = 0
        self._positive_feedback_count = 0
        self._negative_feedback_count = 0

    async def record_interaction(
        self,
        user_id: int,
        session_id: str,
        message: str,
        response: str,
        intent: Optional[str] = None,
        module: Optional[str] = None,
        wizard_type: Optional[str] = None,
        processing_time_ms: int = 0,
        metadata: Optional[dict] = None,
    ) -> UUID:
        """
        Registra uma interacao.

        Args:
            user_id: ID do usuario
            session_id: ID da sessao
            message: Mensagem do usuario
            response: Resposta do Bartolo
            intent: Intencao detectada
            module: Modulo ativo
            wizard_type: Tipo de wizard se ativo
            processing_time_ms: Tempo de processamento
            metadata: Metadados adicionais

        Returns:
            ID da interacao
        """
        interaction = Interaction(
            id=uuid4(),
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response,
            intent=intent,
            module=module,
            wizard_type=wizard_type,
            processing_time_ms=processing_time_ms,
            created_at=datetime.utcnow(),
            metadata=metadata or {},
        )

        self._interactions.append(interaction)
        self._total_interactions += 1

        # Limita tamanho do historico em memoria
        if len(self._interactions) > 10000:
            self._interactions = self._interactions[-5000:]

        logger.debug(f"Interacao registrada: {interaction.id}")
        return interaction.id

    async def record_feedback(
        self,
        interaction_id: UUID,
        feedback_type: FeedbackType,
        rating: Optional[int] = None,
        feedback_text: Optional[str] = None,
    ) -> bool:
        """
        Registra feedback de uma interacao.

        Args:
            interaction_id: ID da interacao
            feedback_type: Tipo de feedback
            rating: Nota 1-5
            feedback_text: Texto adicional

        Returns:
            True se registrado com sucesso
        """
        # Busca interacao
        interaction = next(
            (i for i in self._interactions if i.id == interaction_id),
            None
        )

        if not interaction:
            logger.warning(f"Interacao nao encontrada: {interaction_id}")
            return False

        # Atualiza interacao
        interaction.feedback = feedback_type
        interaction.rating = rating
        interaction.feedback_text = feedback_text

        # Atualiza metricas
        if feedback_type == FeedbackType.HELPFUL:
            self._positive_feedback_count += 1
        else:
            self._negative_feedback_count += 1

        # Registra evento de aprendizado
        event_type = (
            LearningEventType.POSITIVE_FEEDBACK
            if feedback_type == FeedbackType.HELPFUL
            else LearningEventType.NEGATIVE_FEEDBACK
        )

        await self._record_learning_event(
            event_type=event_type,
            interaction_id=interaction_id,
            user_id=interaction.user_id,
            data={
                "feedback_type": feedback_type.value,
                "rating": rating,
                "message": interaction.message[:100],
                "intent": interaction.intent,
                "module": interaction.module,
            },
        )

        # Analisa para padroes
        await self._analyze_for_patterns(interaction)

        logger.info(f"Feedback registrado: {interaction_id}, tipo={feedback_type.value}")
        return True

    async def _record_learning_event(
        self,
        event_type: LearningEventType,
        interaction_id: Optional[UUID] = None,
        user_id: Optional[int] = None,
        data: Optional[dict] = None,
    ) -> UUID:
        """Registra evento de aprendizado."""
        event = LearningEvent(
            id=uuid4(),
            event_type=event_type,
            interaction_id=interaction_id,
            user_id=user_id,
            data=data or {},
            created_at=datetime.utcnow(),
        )

        self._events.append(event)

        # Limita historico
        if len(self._events) > 5000:
            self._events = self._events[-2500:]

        return event.id

    async def _analyze_for_patterns(self, interaction: Interaction) -> None:
        """Analisa interacao para identificar padroes."""
        # Identifica palavras-chave frequentes
        message_lower = interaction.message.lower()

        # Padroes de saudacao
        if any(g in message_lower for g in ["oi", "ola", "bom dia", "boa tarde"]):
            await self._update_pattern(
                pattern_type="greeting",
                trigger=interaction.message,
                was_successful=interaction.feedback == FeedbackType.HELPFUL,
            )

        # Padroes de consulta
        if any(q in message_lower for q in ["quantos", "listar", "mostrar"]):
            await self._update_pattern(
                pattern_type="data_query",
                trigger=interaction.message,
                was_successful=interaction.feedback == FeedbackType.HELPFUL,
                extra_data={"intent": interaction.intent, "module": interaction.module},
            )

        # Padroes de wizard
        if interaction.wizard_type:
            await self._update_pattern(
                pattern_type=f"wizard_{interaction.wizard_type}",
                trigger=interaction.message,
                was_successful=interaction.feedback == FeedbackType.HELPFUL,
            )

    async def _update_pattern(
        self,
        pattern_type: str,
        trigger: str,
        was_successful: bool,
        extra_data: Optional[dict] = None,
    ) -> None:
        """Atualiza ou cria padrao."""
        pattern_key = f"{pattern_type}:{trigger[:50]}"

        if pattern_key in self._patterns:
            pattern = self._patterns[pattern_key]
            pattern.usage_count += 1
            if was_successful:
                # Atualiza taxa de sucesso
                total = pattern.usage_count
                successes = pattern.success_rate * (total - 1) + (1 if was_successful else 0)
                pattern.success_rate = successes / total
            pattern.updated_at = datetime.utcnow()
        else:
            self._patterns[pattern_key] = LearnedPattern(
                id=uuid4(),
                pattern_type=pattern_type,
                trigger=trigger[:100],
                confidence=0.5,
                usage_count=1,
                success_rate=1.0 if was_successful else 0.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

    async def get_similar_interactions(
        self,
        message: str,
        limit: int = 5,
    ) -> list[Interaction]:
        """
        Busca interacoes similares para referencia.

        Args:
            message: Mensagem para comparar
            limit: Limite de resultados

        Returns:
            Lista de interacoes similares
        """
        # Busca simples por palavras-chave
        # Em producao, usar embeddings e busca semantica
        message_words = set(message.lower().split())

        scored = []
        for interaction in self._interactions:
            if interaction.feedback == FeedbackType.HELPFUL:
                interaction_words = set(interaction.message.lower().split())
                common = len(message_words & interaction_words)
                if common > 0:
                    score = common / len(message_words | interaction_words)
                    scored.append((score, interaction))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [i for _, i in scored[:limit]]

    async def get_successful_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_usage: int = 3,
        min_success_rate: float = 0.7,
    ) -> list[LearnedPattern]:
        """
        Retorna padroes bem-sucedidos.

        Args:
            pattern_type: Filtrar por tipo
            min_usage: Uso minimo
            min_success_rate: Taxa de sucesso minima

        Returns:
            Lista de padroes
        """
        patterns = []
        for pattern in self._patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if pattern.usage_count >= min_usage and pattern.success_rate >= min_success_rate:
                patterns.append(pattern)

        return sorted(patterns, key=lambda p: p.success_rate, reverse=True)

    def get_stats(self) -> dict:
        """Retorna estatisticas de aprendizado."""
        total_feedback = self._positive_feedback_count + self._negative_feedback_count
        satisfaction_rate = (
            self._positive_feedback_count / total_feedback
            if total_feedback > 0 else 0
        )

        return {
            "total_interactions": self._total_interactions,
            "interactions_in_memory": len(self._interactions),
            "total_feedback": total_feedback,
            "positive_feedback": self._positive_feedback_count,
            "negative_feedback": self._negative_feedback_count,
            "satisfaction_rate": round(satisfaction_rate * 100, 1),
            "patterns_learned": len(self._patterns),
            "learning_events": len(self._events),
        }

    async def export_learnings(self) -> dict:
        """Exporta dados de aprendizado."""
        return {
            "patterns": [
                {
                    "id": str(p.id),
                    "type": p.pattern_type,
                    "trigger": p.trigger,
                    "usage_count": p.usage_count,
                    "success_rate": p.success_rate,
                }
                for p in self._patterns.values()
            ],
            "stats": self.get_stats(),
            "exported_at": datetime.utcnow().isoformat(),
        }
