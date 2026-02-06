"""Seletor inteligente de canal para notificações."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class Channel(Enum):
    """Canais de notificação disponíveis."""

    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"
    SLACK = "slack"
    TEAMS = "teams"


@dataclass
class ChannelRecommendation:
    """Recomendação de canal."""

    primary_channel: Channel
    fallback_channels: list[Channel]
    confidence: float
    reasoning: str
    channel_scores: dict[str, float]
    expected_delivery_rate: float
    expected_engagement_rate: float


@dataclass
class ChannelPerformance:
    """Performance histórica de um canal."""

    channel: Channel
    delivery_rate: float
    open_rate: float
    click_rate: float
    response_rate: float
    avg_delivery_time_seconds: float
    cost_per_notification: float = 0.0
    user_preference_score: float = 0.5


class ChannelSelector:
    """
    Seletor inteligente de canal.

    Escolhe o melhor canal para cada notificação baseado em:
    - Preferências do usuário
    - Performance histórica
    - Tipo da notificação
    - Disponibilidade do canal
    - Contexto atual (online/offline)
    - Custos
    """

    # Pesos para cálculo de score
    PREFERENCE_WEIGHT = 0.30
    PERFORMANCE_WEIGHT = 0.35
    CONTEXT_WEIGHT = 0.20
    COST_WEIGHT = 0.15

    # Mapeamento tipo -> canais recomendados
    TYPE_CHANNEL_AFFINITY = {
        "urgent": [Channel.PUSH, Channel.SMS, Channel.WHATSAPP],
        "system": [Channel.IN_APP, Channel.PUSH, Channel.EMAIL],
        "marketing": [Channel.EMAIL, Channel.PUSH, Channel.IN_APP],
        "reminder": [Channel.PUSH, Channel.EMAIL, Channel.IN_APP],
        "transaction": [Channel.EMAIL, Channel.PUSH, Channel.SMS],
        "social": [Channel.IN_APP, Channel.PUSH],
        "business": [Channel.EMAIL, Channel.SLACK, Channel.TEAMS],
    }

    def __init__(
        self,
        enable_cost_optimization: bool = True,
        default_fallback_count: int = 2,
    ) -> None:
        """
        Inicializa o seletor.

        Args:
            enable_cost_optimization: Considera custo na seleção
            default_fallback_count: Número de canais fallback
        """
        self.enable_cost = enable_cost_optimization
        self.fallback_count = default_fallback_count

    async def select_channel(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        content: Optional[dict] = None,
        force_channel: Optional[Channel] = None,
    ) -> ChannelRecommendation:
        """
        Seleciona o melhor canal para envio.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            notification_type: Tipo da notificação
            content: Conteúdo (para análise de compatibilidade)
            force_channel: Forçar canal específico

        Returns:
            ChannelRecommendation com canal primário e fallbacks
        """
        if force_channel:
            return ChannelRecommendation(
                primary_channel=force_channel,
                fallback_channels=[],
                confidence=1.0,
                reasoning="Channel forced by request",
                channel_scores={force_channel.value: 1.0},
                expected_delivery_rate=0.95,
                expected_engagement_rate=0.5,
            )

        # Obter dados necessários
        preferences = await self._get_channel_preferences(db, user_id)
        performance = await self._get_channel_performance(db, user_id)
        context = await self._get_user_context(db, user_id)
        available = await self._get_available_channels(db, user_id)

        # Calcular scores
        channel_scores = self._calculate_channel_scores(
            notification_type,
            preferences,
            performance,
            context,
            available,
            content,
        )

        # Ordenar por score
        sorted_channels = sorted(
            channel_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        if not sorted_channels:
            # Fallback para push
            return ChannelRecommendation(
                primary_channel=Channel.PUSH,
                fallback_channels=[Channel.EMAIL],
                confidence=0.3,
                reasoning="No optimal channel found, using default",
                channel_scores={"push": 0.3},
                expected_delivery_rate=0.7,
                expected_engagement_rate=0.3,
            )

        primary = sorted_channels[0][0]
        primary_score = sorted_channels[0][1]

        fallbacks = [ch for ch, _ in sorted_channels[1:self.fallback_count + 1]]

        # Estimar métricas
        primary_perf = performance.get(primary, ChannelPerformance(
            channel=primary,
            delivery_rate=0.9,
            open_rate=0.5,
            click_rate=0.2,
            response_rate=0.3,
            avg_delivery_time_seconds=10,
        ))

        return ChannelRecommendation(
            primary_channel=primary,
            fallback_channels=fallbacks,
            confidence=primary_score,
            reasoning=self._generate_reasoning(primary, notification_type, preferences),
            channel_scores={ch.value: score for ch, score in sorted_channels},
            expected_delivery_rate=primary_perf.delivery_rate,
            expected_engagement_rate=primary_perf.open_rate * 0.7 + primary_perf.click_rate * 0.3,
        )

    async def _get_channel_preferences(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[Channel, float]:
        """Obtém preferências do usuário por canal."""
        # TODO: Buscar do repositório real

        return {
            Channel.PUSH: 0.9,
            Channel.EMAIL: 0.8,
            Channel.SMS: 0.6,
            Channel.WHATSAPP: 0.7,
            Channel.IN_APP: 0.95,
            Channel.SLACK: 0.5,
            Channel.TEAMS: 0.5,
        }

    async def _get_channel_performance(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[Channel, ChannelPerformance]:
        """Obtém performance histórica por canal."""
        # TODO: Calcular do histórico real

        return {
            Channel.PUSH: ChannelPerformance(
                channel=Channel.PUSH,
                delivery_rate=0.95,
                open_rate=0.70,
                click_rate=0.25,
                response_rate=0.40,
                avg_delivery_time_seconds=5,
                cost_per_notification=0.0,
                user_preference_score=0.9,
            ),
            Channel.EMAIL: ChannelPerformance(
                channel=Channel.EMAIL,
                delivery_rate=0.98,
                open_rate=0.45,
                click_rate=0.15,
                response_rate=0.20,
                avg_delivery_time_seconds=30,
                cost_per_notification=0.001,
                user_preference_score=0.8,
            ),
            Channel.SMS: ChannelPerformance(
                channel=Channel.SMS,
                delivery_rate=0.99,
                open_rate=0.95,
                click_rate=0.10,
                response_rate=0.60,
                avg_delivery_time_seconds=10,
                cost_per_notification=0.05,
                user_preference_score=0.6,
            ),
            Channel.WHATSAPP: ChannelPerformance(
                channel=Channel.WHATSAPP,
                delivery_rate=0.97,
                open_rate=0.90,
                click_rate=0.20,
                response_rate=0.70,
                avg_delivery_time_seconds=15,
                cost_per_notification=0.03,
                user_preference_score=0.7,
            ),
            Channel.IN_APP: ChannelPerformance(
                channel=Channel.IN_APP,
                delivery_rate=1.0,
                open_rate=0.85,
                click_rate=0.35,
                response_rate=0.50,
                avg_delivery_time_seconds=1,
                cost_per_notification=0.0,
                user_preference_score=0.95,
            ),
        }

    async def _get_user_context(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém contexto atual do usuário."""
        # TODO: Verificar status real do usuário

        return {
            "is_online": True,
            "is_mobile_active": True,
            "last_seen": datetime.utcnow() - timedelta(minutes=5),
            "current_platform": "mobile",
            "in_quiet_hours": False,
        }

    async def _get_available_channels(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[Channel]:
        """Obtém canais disponíveis para o usuário."""
        # TODO: Verificar quais canais estão configurados

        return [
            Channel.PUSH,
            Channel.EMAIL,
            Channel.SMS,
            Channel.WHATSAPP,
            Channel.IN_APP,
        ]

    def _calculate_channel_scores(
        self,
        notification_type: str,
        preferences: dict[Channel, float],
        performance: dict[Channel, ChannelPerformance],
        context: dict,
        available: list[Channel],
        content: Optional[dict],
    ) -> dict[Channel, float]:
        """Calcula score de cada canal."""
        scores = {}

        # Canais recomendados para o tipo
        recommended = self.TYPE_CHANNEL_AFFINITY.get(
            notification_type,
            [Channel.PUSH, Channel.EMAIL],
        )

        for channel in available:
            # Score de preferência
            pref_score = preferences.get(channel, 0.5)

            # Score de performance
            perf = performance.get(channel)
            if perf:
                perf_score = (
                    perf.delivery_rate * 0.3
                    + perf.open_rate * 0.3
                    + perf.click_rate * 0.2
                    + perf.response_rate * 0.2
                )
            else:
                perf_score = 0.5

            # Score de contexto
            ctx_score = self._calculate_context_score(channel, context)

            # Score de custo (inverso)
            if self.enable_cost and perf:
                cost = perf.cost_per_notification
                cost_score = 1.0 - min(cost / 0.1, 1.0)  # Normaliza para 0-1
            else:
                cost_score = 1.0

            # Bonus se canal é recomendado para o tipo
            type_bonus = 0.15 if channel in recommended else 0.0

            # Score final
            total = (
                pref_score * self.PREFERENCE_WEIGHT
                + perf_score * self.PERFORMANCE_WEIGHT
                + ctx_score * self.CONTEXT_WEIGHT
                + cost_score * self.COST_WEIGHT
                + type_bonus
            )

            # Verificar compatibilidade com conteúdo
            if content:
                total *= self._check_content_compatibility(channel, content)

            scores[channel] = min(max(total, 0.0), 1.0)

        return scores

    def _calculate_context_score(
        self,
        channel: Channel,
        context: dict,
    ) -> float:
        """Calcula score baseado no contexto."""
        score = 0.5

        is_online = context.get("is_online", False)
        is_mobile = context.get("is_mobile_active", False)
        in_quiet = context.get("in_quiet_hours", False)

        # Ajustes baseados no contexto
        if channel == Channel.IN_APP:
            score = 1.0 if is_online else 0.2
        elif channel == Channel.PUSH:
            score = 0.9 if is_mobile else 0.6
        elif channel == Channel.EMAIL:
            score = 0.7  # Email é menos dependente de contexto
        elif channel in [Channel.SMS, Channel.WHATSAPP]:
            score = 0.8 if not in_quiet else 0.3

        return score

    def _check_content_compatibility(
        self,
        channel: Channel,
        content: dict,
    ) -> float:
        """Verifica compatibilidade do conteúdo com o canal."""
        multiplier = 1.0

        # Verificar tamanho do conteúdo
        body_length = len(content.get("body", ""))

        if channel == Channel.SMS and body_length > 160:
            multiplier *= 0.7  # SMS tem limite
        elif channel == Channel.PUSH and body_length > 200:
            multiplier *= 0.8  # Push tem limite menor

        # Verificar mídia
        has_image = bool(content.get("image_url"))
        has_rich_content = bool(content.get("html_body"))

        if has_image and channel == Channel.SMS:
            multiplier *= 0.5  # SMS não suporta imagens bem
        if has_rich_content and channel == Channel.SMS:
            multiplier *= 0.3

        return multiplier

    def _generate_reasoning(
        self,
        channel: Channel,
        notification_type: str,
        preferences: dict,
    ) -> str:
        """Gera explicação da seleção."""
        reasons = []

        pref_score = preferences.get(channel, 0)
        if pref_score > 0.8:
            reasons.append("high user preference")

        recommended = self.TYPE_CHANNEL_AFFINITY.get(notification_type, [])
        if channel in recommended:
            reasons.append(f"recommended for {notification_type} notifications")

        if channel == Channel.IN_APP:
            reasons.append("user is currently online")
        elif channel == Channel.PUSH:
            reasons.append("good mobile engagement history")

        return f"Selected {channel.value}: {', '.join(reasons) or 'best overall score'}"

    async def get_multi_channel_strategy(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        importance: str = "normal",
    ) -> list[tuple[Channel, int]]:
        """
        Retorna estratégia multi-canal com delays.

        Para notificações importantes, envia em múltiplos canais
        com delays entre eles.

        Returns:
            Lista de (canal, delay_minutos)
        """
        recommendation = await self.select_channel(
            db=db,
            user_id=user_id,
            notification_type=notification_type,
        )

        strategy = [(recommendation.primary_channel, 0)]

        if importance == "high":
            # Adicionar fallbacks com delays
            for i, fallback in enumerate(recommendation.fallback_channels):
                delay = (i + 1) * 15  # 15, 30 minutos
                strategy.append((fallback, delay))

        elif importance == "critical":
            # Enviar em todos canais principais simultaneamente
            strategy = [
                (Channel.PUSH, 0),
                (Channel.SMS, 0),
                (Channel.EMAIL, 0),
            ]

        return strategy
