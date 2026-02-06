"""
Learning Service - Servico de Aprendizado Continuo.

Permite ao Bartolo aprender com interacoes e melhorar respostas.

Persistencia:
- Memoria (hot data): cache em listas/dicts Python para acesso rapido
- PostgreSQL (cold data): persistencia duravel via SQLAlchemy async
- Redis (cache patterns): cache de padroes frequentes com TTL

Se db=None, funciona apenas em memoria (compatibilidade retroativa).
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# TTL padrao para cache Redis de patterns (1 hora)
REDIS_PATTERNS_TTL = 3600
REDIS_PREFIX = "bartolo:learning"


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

    Persistencia hibrida:
    - Memoria: hot data para acesso rapido
    - PostgreSQL: persistencia duravel
    - Redis: cache de patterns frequentes
    """

    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        redis_client: Any = None,
    ):
        """
        Inicializa o servico.

        Args:
            db: Sessao async do SQLAlchemy (opcional).
                Se None, funciona apenas em memoria.
            redis_client: Cliente Redis async (opcional).
                Se None, nao usa cache Redis.
        """
        self.db = db
        self._redis = redis_client

        # Cache em memoria (hot data)
        self._interactions: list[Interaction] = []
        self._events: list[LearningEvent] = []
        self._patterns: dict[str, LearnedPattern] = {}

        # Metricas
        self._total_interactions = 0
        self._positive_feedback_count = 0
        self._negative_feedback_count = 0

    def set_db(self, db: AsyncSession) -> None:
        """Define sessao do banco de dados (permite injecao tardia)."""
        self.db = db

    async def _get_redis(self):
        """Obtem cliente Redis (lazy init via core.cache)."""
        if self._redis is not None:
            return self._redis
        try:
            from core.cache import get_redis
            self._redis = await get_redis()
            return self._redis
        except Exception as e:
            logger.debug(f"Redis nao disponivel: {e}")
            return None

    # ========================================================================
    # Persistencia PostgreSQL
    # ========================================================================

    async def _persist_interaction(self, interaction: Interaction) -> None:
        """
        Persiste interacao no PostgreSQL (fire-and-forget).

        Nao bloqueia o fluxo principal. Erros sao logados mas nao propagados.
        """
        if not self.db:
            return

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloInteraction

            db_interaction = BartoloInteraction(
                id=interaction.id,
                user_id=interaction.user_id,
                session_id=interaction.session_id,
                message=interaction.message[:5000],  # limita tamanho
                response=interaction.response[:5000],
                response_summary=interaction.response[:500] if interaction.response else None,
                intent_detected=interaction.intent,
                module=interaction.module,
                wizard_type=interaction.wizard_type,
                processing_time_ms=interaction.processing_time_ms,
                metadata=interaction.metadata or {},
                created_at=interaction.created_at or datetime.utcnow(),
            )

            self.db.add(db_interaction)
            await self.db.flush()
            logger.debug(f"Interacao persistida no banco: {interaction.id}")

        except Exception as e:
            logger.error(f"Erro ao persistir interacao no banco: {e}")
            # Nao propaga - fire and forget

    async def _persist_feedback(
        self,
        interaction_id: UUID,
        feedback_type: FeedbackType,
        rating: Optional[int],
        feedback_text: Optional[str],
    ) -> None:
        """Persiste feedback no PostgreSQL."""
        if not self.db:
            return

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloInteraction

            stmt = (
                update(BartoloInteraction)
                .where(BartoloInteraction.id == interaction_id)
                .values(
                    feedback_type=feedback_type.value,
                    feedback_score=rating,
                    feedback_text=feedback_text,
                    updated_at=datetime.utcnow(),
                )
            )
            await self.db.execute(stmt)
            await self.db.flush()
            logger.debug(f"Feedback persistido no banco: {interaction_id}")

        except Exception as e:
            logger.error(f"Erro ao persistir feedback no banco: {e}")

    async def _persist_pattern(
        self,
        pattern_key: str,
        pattern: LearnedPattern,
    ) -> None:
        """Persiste ou atualiza padrao no PostgreSQL."""
        if not self.db:
            return

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloLearning

            # Tenta atualizar primeiro (upsert logico)
            stmt = (
                update(BartoloLearning)
                .where(BartoloLearning.pattern_key == pattern_key)
                .values(
                    frequency=pattern.usage_count,
                    success_rate=pattern.success_rate,
                    confidence=pattern.confidence,
                    last_seen=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
            result = await self.db.execute(stmt)

            # Se nao atualizou nenhuma row, insere
            if result.rowcount == 0:
                db_learning = BartoloLearning(
                    id=pattern.id,
                    pattern_type=pattern.pattern_type,
                    pattern_key=pattern_key,
                    trigger=pattern.trigger,
                    response_template=pattern.response_template,
                    action=pattern.action,
                    frequency=pattern.usage_count,
                    success_rate=pattern.success_rate,
                    confidence=pattern.confidence,
                    last_seen=datetime.utcnow(),
                    created_at=pattern.created_at or datetime.utcnow(),
                )
                self.db.add(db_learning)

            await self.db.flush()
            logger.debug(f"Padrao persistido no banco: {pattern_key}")

        except Exception as e:
            logger.error(f"Erro ao persistir padrao no banco: {e}")

    # ========================================================================
    # Cache Redis
    # ========================================================================

    async def _cache_pattern_redis(
        self,
        pattern_key: str,
        pattern: LearnedPattern,
    ) -> None:
        """Cacheia padrao no Redis."""
        redis_client = await self._get_redis()
        if not redis_client:
            return

        try:
            cache_key = f"{REDIS_PREFIX}:pattern:{pattern_key}"
            data = {
                "id": str(pattern.id),
                "pattern_type": pattern.pattern_type,
                "trigger": pattern.trigger,
                "confidence": pattern.confidence,
                "usage_count": pattern.usage_count,
                "success_rate": pattern.success_rate,
                "updated_at": datetime.utcnow().isoformat(),
            }
            await redis_client.setex(
                cache_key,
                REDIS_PATTERNS_TTL,
                json.dumps(data),
            )
        except Exception as e:
            logger.debug(f"Erro ao cachear padrao no Redis: {e}")

    async def _get_pattern_from_redis(
        self,
        pattern_key: str,
    ) -> Optional[dict]:
        """Busca padrao no Redis."""
        redis_client = await self._get_redis()
        if not redis_client:
            return None

        try:
            cache_key = f"{REDIS_PREFIX}:pattern:{pattern_key}"
            data = await redis_client.get(cache_key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.debug(f"Erro ao buscar padrao no Redis: {e}")

        return None

    async def _load_patterns_from_db(self) -> None:
        """
        Carrega padroes do banco para memoria (warmup).

        Chamado opcionalmente na inicializacao para popular cache em memoria.
        """
        if not self.db:
            return

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloLearning

            stmt = (
                select(BartoloLearning)
                .where(BartoloLearning.is_active.is_(True))
                .order_by(BartoloLearning.frequency.desc())
                .limit(500)
            )
            result = await self.db.execute(stmt)
            rows = result.scalars().all()

            for row in rows:
                pattern = LearnedPattern(
                    id=row.id,
                    pattern_type=row.pattern_type,
                    trigger=row.trigger or "",
                    response_template=row.response_template,
                    action=row.action,
                    confidence=row.confidence,
                    usage_count=row.frequency,
                    success_rate=row.success_rate,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                self._patterns[row.pattern_key] = pattern

            logger.info(f"Carregados {len(rows)} padroes do banco para memoria")

        except Exception as e:
            logger.error(f"Erro ao carregar padroes do banco: {e}")

    # ========================================================================
    # API publica (compativel com versao anterior)
    # ========================================================================

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

        # Cache em memoria
        self._interactions.append(interaction)
        self._total_interactions += 1

        # Limita tamanho do historico em memoria
        if len(self._interactions) > 10000:
            self._interactions = self._interactions[-5000:]

        # Persiste no banco (fire-and-forget)
        await self._persist_interaction(interaction)

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
        # Busca interacao em memoria
        interaction = next(
            (i for i in self._interactions if i.id == interaction_id),
            None
        )

        if not interaction:
            # Tenta buscar no banco se nao esta em memoria
            if self.db:
                found = await self._find_interaction_in_db(interaction_id)
                if not found:
                    logger.warning(f"Interacao nao encontrada: {interaction_id}")
                    return False
                # Persiste feedback direto no banco
                await self._persist_feedback(
                    interaction_id, feedback_type, rating, feedback_text
                )
                # Atualiza metricas
                if feedback_type == FeedbackType.HELPFUL:
                    self._positive_feedback_count += 1
                else:
                    self._negative_feedback_count += 1
                logger.info(
                    f"Feedback registrado (banco): {interaction_id}, "
                    f"tipo={feedback_type.value}"
                )
                return True
            else:
                logger.warning(f"Interacao nao encontrada: {interaction_id}")
                return False

        # Atualiza interacao em memoria
        interaction.feedback = feedback_type
        interaction.rating = rating
        interaction.feedback_text = feedback_text

        # Atualiza metricas
        if feedback_type == FeedbackType.HELPFUL:
            self._positive_feedback_count += 1
        else:
            self._negative_feedback_count += 1

        # Persiste feedback no banco
        await self._persist_feedback(
            interaction_id, feedback_type, rating, feedback_text
        )

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

    async def _find_interaction_in_db(self, interaction_id: UUID) -> bool:
        """Verifica se interacao existe no banco."""
        if not self.db:
            return False

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloInteraction

            stmt = select(BartoloInteraction.id).where(
                BartoloInteraction.id == interaction_id
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(f"Erro ao buscar interacao no banco: {e}")
            return False

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

        pattern = self._patterns[pattern_key]

        # Persiste no banco (fire-and-forget)
        await self._persist_pattern(pattern_key, pattern)

        # Cacheia no Redis
        await self._cache_pattern_redis(pattern_key, pattern)

    async def get_similar_interactions(
        self,
        message: str,
        limit: int = 5,
    ) -> list[Interaction]:
        """
        Busca interacoes similares para referencia.

        Tenta memoria primeiro. Se nao encontrar resultados suficientes
        e banco disponivel, complementa com dados do banco.

        Args:
            message: Mensagem para comparar
            limit: Limite de resultados

        Returns:
            Lista de interacoes similares
        """
        # 1. Busca em memoria
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
        results = [i for _, i in scored[:limit]]

        # 2. Se nao tem resultados suficientes, tenta no banco
        if len(results) < limit and self.db:
            try:
                db_results = await self._search_interactions_in_db(
                    message, limit - len(results)
                )
                results.extend(db_results)
            except Exception as e:
                logger.error(f"Erro ao buscar interacoes similares no banco: {e}")

        return results[:limit]

    async def _search_interactions_in_db(
        self,
        message: str,
        limit: int,
    ) -> list[Interaction]:
        """Busca interacoes similares no banco (fallback)."""
        if not self.db:
            return []

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloInteraction

            # Busca por feedback positivo, ordenado por data recente
            # (busca semantica mais avancada requer embeddings)
            words = message.lower().split()[:3]  # primeiras 3 palavras

            stmt = (
                select(BartoloInteraction)
                .where(
                    BartoloInteraction.feedback_type == FeedbackType.HELPFUL.value,
                    BartoloInteraction.is_active.is_(True),
                )
                .order_by(BartoloInteraction.created_at.desc())
                .limit(limit * 3)  # busca mais para filtrar depois
            )
            result = await self.db.execute(stmt)
            rows = result.scalars().all()

            # Filtra por similaridade basica
            message_words = set(message.lower().split())
            scored = []
            for row in rows:
                row_words = set(row.message.lower().split())
                common = len(message_words & row_words)
                if common > 0:
                    score = common / len(message_words | row_words)
                    interaction = Interaction(
                        id=row.id,
                        user_id=row.user_id,
                        session_id=row.session_id,
                        message=row.message,
                        response=row.response,
                        intent=row.intent_detected,
                        module=row.module,
                        feedback=FeedbackType(row.feedback_type) if row.feedback_type else None,
                        rating=row.feedback_score,
                        created_at=row.created_at,
                    )
                    scored.append((score, interaction))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [i for _, i in scored[:limit]]

        except Exception as e:
            logger.error(f"Erro ao buscar interacoes no banco: {e}")
            return []

    async def get_successful_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_usage: int = 3,
        min_success_rate: float = 0.7,
    ) -> list[LearnedPattern]:
        """
        Retorna padroes bem-sucedidos.

        Tenta memoria primeiro. Se vazia e banco disponivel, busca no banco.

        Args:
            pattern_type: Filtrar por tipo
            min_usage: Uso minimo
            min_success_rate: Taxa de sucesso minima

        Returns:
            Lista de padroes
        """
        # 1. Busca em memoria
        patterns = []
        for pattern in self._patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if pattern.usage_count >= min_usage and pattern.success_rate >= min_success_rate:
                patterns.append(pattern)

        # 2. Se memoria vazia e banco disponivel, carrega do banco
        if not patterns and self.db:
            try:
                patterns = await self._get_patterns_from_db(
                    pattern_type, min_usage, min_success_rate
                )
            except Exception as e:
                logger.error(f"Erro ao buscar padroes no banco: {e}")

        return sorted(patterns, key=lambda p: p.success_rate, reverse=True)

    async def _get_patterns_from_db(
        self,
        pattern_type: Optional[str],
        min_usage: int,
        min_success_rate: float,
    ) -> list[LearnedPattern]:
        """Busca padroes no banco (fallback)."""
        if not self.db:
            return []

        try:
            from modules.ai.bartolo.models.bartolo_models import BartoloLearning

            stmt = (
                select(BartoloLearning)
                .where(
                    BartoloLearning.is_active.is_(True),
                    BartoloLearning.frequency >= min_usage,
                    BartoloLearning.success_rate >= min_success_rate,
                )
            )

            if pattern_type:
                stmt = stmt.where(BartoloLearning.pattern_type == pattern_type)

            stmt = stmt.order_by(BartoloLearning.success_rate.desc()).limit(100)

            result = await self.db.execute(stmt)
            rows = result.scalars().all()

            patterns = []
            for row in rows:
                pattern = LearnedPattern(
                    id=row.id,
                    pattern_type=row.pattern_type,
                    trigger=row.trigger or "",
                    response_template=row.response_template,
                    action=row.action,
                    confidence=row.confidence,
                    usage_count=row.frequency,
                    success_rate=row.success_rate,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                patterns.append(pattern)

                # Popula cache em memoria
                self._patterns[row.pattern_key] = pattern

            return patterns

        except Exception as e:
            logger.error(f"Erro ao buscar padroes no banco: {e}")
            return []

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
            "persistence_enabled": self.db is not None,
            "redis_enabled": self._redis is not None,
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

    async def warmup(self) -> None:
        """
        Carrega dados do banco para memoria (warmup).

        Deve ser chamado na inicializacao do servico para popular
        o cache em memoria com padroes existentes.
        """
        await self._load_patterns_from_db()
        logger.info("LearningService warmup concluido")
