"""Motor de personalização de notificações com IA."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """Perfil do usuário para personalização."""

    user_id: int
    first_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "America/Sao_Paulo"
    locale: str = "pt-BR"
    age_group: Optional[str] = None
    business_sector: Optional[str] = None
    engagement_style: str = "professional"
    activity_patterns: dict = None
    preferences: dict = None
    engagement_metrics: dict = None
    device_info: list = None

    def __post_init__(self):
        self.activity_patterns = self.activity_patterns or {}
        self.preferences = self.preferences or {}
        self.engagement_metrics = self.engagement_metrics or {}
        self.device_info = self.device_info or []


@dataclass
class PersonalizedNotification:
    """Resultado da personalização."""

    user_id: int
    content: dict
    optimal_time: datetime
    preferred_channel: str
    engagement_score: float
    personalization_factors: dict
    ab_test_variant: Optional[str] = None


class PersonalizationEngine:
    """
    Motor de personalização de notificações.

    Funcionalidades:
    - Análise de perfil do usuário
    - Predição de timing ótimo
    - Seleção de canal preferido
    - Personalização de conteúdo
    - Cálculo de probabilidade de engajamento
    """

    def __init__(
        self,
        enable_ml: bool = True,
        default_engagement_threshold: float = 0.5,
    ) -> None:
        """
        Inicializa o motor de personalização.

        Args:
            enable_ml: Habilita modelos de ML
            default_engagement_threshold: Threshold mínimo de engajamento
        """
        self.enable_ml = enable_ml
        self.engagement_threshold = default_engagement_threshold

        # Modelos ML (simplificados para implementação inicial)
        self._timing_weights = {}
        self._channel_weights = {}
        self._engagement_weights = {}

    async def personalize_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        base_content: dict,
        context: Optional[dict] = None,
    ) -> PersonalizedNotification:
        """
        Personaliza notificação para usuário específico.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            notification_type: Tipo da notificação
            base_content: Conteúdo base
            context: Contexto adicional

        Returns:
            Notificação personalizada
        """
        # 1. Obter perfil do usuário
        user_profile = await self.get_user_profile(db, user_id)

        # 2. Analisar histórico de engajamento
        engagement_history = await self.get_engagement_history(db, user_id)

        # 3. Determinar timing ótimo
        optimal_time = await self.calculate_optimal_timing(
            user_profile, engagement_history
        )

        # 4. Selecionar canal preferido
        preferred_channel = await self.select_optimal_channel(
            db, user_profile, notification_type
        )

        # 5. Personalizar conteúdo
        personalized_content = await self.personalize_content(
            base_content, user_profile, context or {}
        )

        # 6. Calcular probabilidade de engajamento
        engagement_score = await self.predict_engagement(
            user_profile, notification_type, optimal_time, preferred_channel
        )

        # 7. Obter fatores de personalização
        personalization_factors = self.get_personalization_factors(user_profile)

        return PersonalizedNotification(
            user_id=user_id,
            content=personalized_content,
            optimal_time=optimal_time,
            preferred_channel=preferred_channel,
            engagement_score=engagement_score,
            personalization_factors=personalization_factors,
        )

    async def get_user_profile(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> UserProfile:
        """Obtém perfil completo do usuário."""
        # TODO: Integrar com repositório de usuários real
        # Por ora, retorna perfil mock

        profile = UserProfile(user_id=user_id)

        # Enriquecer com dados comportamentais
        profile.activity_patterns = await self.analyze_activity_patterns(db, user_id)
        profile.preferences = await self.get_notification_preferences(db, user_id)
        profile.engagement_metrics = await self.calculate_engagement_metrics(db, user_id)

        return profile

    async def analyze_activity_patterns(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Analisa padrões de atividade do usuário."""
        # TODO: Buscar atividades reais do usuário
        # Retorna padrões mock baseados em análise típica

        return {
            "peak_hours": [9, 14, 18],  # Horários de maior atividade
            "active_days": [1, 2, 3, 4, 5],  # Segunda a sexta
            "session_duration": 15.5,  # Minutos médios
            "feature_usage": {
                "leads": 0.4,
                "tasks": 0.3,
                "reports": 0.2,
                "messages": 0.1,
            },
            "response_patterns": {
                "avg_response_time_minutes": 30,
                "quick_response_rate": 0.6,
            },
        }

    async def get_notification_preferences(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém preferências de notificação."""
        # TODO: Buscar preferências reais do repositório

        return {
            "push_enabled": True,
            "email_enabled": True,
            "sms_enabled": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "preferred_channels": ["push", "email"],
            "max_daily_notifications": 10,
        }

    async def calculate_engagement_metrics(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Calcula métricas de engajamento do usuário."""
        # TODO: Calcular métricas reais do histórico

        return {
            "open_rate": 0.65,
            "click_rate": 0.25,
            "response_rate": 0.40,
            "avg_time_to_action_minutes": 45,
            "churn_risk": 0.15,
            "engagement_score": 0.72,
        }

    async def get_engagement_history(
        self,
        db: AsyncSession,
        user_id: int,
        days: int = 30,
    ) -> list[dict]:
        """Obtém histórico de engajamento do usuário."""
        # TODO: Buscar histórico real de notificações

        return []  # Lista vazia por enquanto

    async def calculate_optimal_timing(
        self,
        user_profile: UserProfile,
        engagement_history: list[dict],
    ) -> datetime:
        """
        Calcula timing ótimo para envio.

        Considera:
        - Horários de pico de atividade
        - Horários silenciosos
        - Padrões de resposta históricos
        - Timezone do usuário
        """
        now = datetime.utcnow()

        # Obter horários de pico
        peak_hours = user_profile.activity_patterns.get("peak_hours", [9, 14, 18])

        # Verificar quiet hours
        quiet_start = user_profile.preferences.get("quiet_hours_start", "22:00")
        quiet_end = user_profile.preferences.get("quiet_hours_end", "08:00")

        # Encontrar próximo horário de pico fora do quiet hours
        current_hour = now.hour

        for hour in peak_hours:
            if self._is_outside_quiet_hours(hour, quiet_start, quiet_end):
                if hour > current_hour:
                    # Próximo horário de pico é hoje
                    return now.replace(hour=hour, minute=0, second=0, microsecond=0)

        # Se não encontrou hoje, usar primeiro horário de pico amanhã
        tomorrow = now + timedelta(days=1)
        optimal_hour = peak_hours[0] if peak_hours else 9

        return tomorrow.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)

    def _is_outside_quiet_hours(
        self,
        hour: int,
        quiet_start: str,
        quiet_end: str,
    ) -> bool:
        """Verifica se horário está fora do período silencioso."""
        start_hour = int(quiet_start.split(":")[0])
        end_hour = int(quiet_end.split(":")[0])

        # Quiet hours que cruzam meia-noite
        if start_hour > end_hour:
            return end_hour <= hour < start_hour
        else:
            return hour < start_hour or hour >= end_hour

    async def select_optimal_channel(
        self,
        db: AsyncSession,
        user_profile: UserProfile,
        notification_type: str,
    ) -> str:
        """
        Seleciona canal ótimo baseado no perfil e tipo.

        Considera:
        - Preferências explícitas do usuário
        - Performance histórica por canal
        - Contexto atual (online, offline)
        - Tipo da notificação
        """
        preferences = user_profile.preferences
        preferred_channels = preferences.get("preferred_channels", ["push", "email"])

        # Performance por canal (simplificado)
        channel_performance = await self._get_channel_performance(
            db, user_profile.user_id, notification_type
        )

        # Calcular scores
        channel_scores = {}
        for channel in ["push", "email", "sms", "in_app"]:
            if channel not in preferred_channels:
                continue

            if not preferences.get(f"{channel}_enabled", True):
                continue

            score = self._calculate_channel_score(
                channel,
                channel_performance.get(channel, {}),
                notification_type,
            )
            channel_scores[channel] = score

        if not channel_scores:
            return "push"  # Default

        # Retornar canal com maior score
        return max(channel_scores, key=channel_scores.get)

    async def _get_channel_performance(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
    ) -> dict:
        """Obtém performance histórica por canal."""
        # TODO: Calcular do histórico real

        return {
            "push": {"open_rate": 0.70, "click_rate": 0.25},
            "email": {"open_rate": 0.45, "click_rate": 0.15},
            "sms": {"open_rate": 0.95, "click_rate": 0.10},
            "in_app": {"open_rate": 0.85, "click_rate": 0.35},
        }

    def _calculate_channel_score(
        self,
        channel: str,
        performance: dict,
        notification_type: str,
    ) -> float:
        """Calcula score de um canal."""
        base_score = 0.5

        # Peso por performance
        open_rate = performance.get("open_rate", 0.5)
        click_rate = performance.get("click_rate", 0.2)

        performance_score = (open_rate * 0.6) + (click_rate * 0.4)

        # Ajuste por tipo de notificação
        type_multipliers = {
            "urgent": {"push": 1.5, "sms": 1.4, "email": 0.8, "in_app": 1.0},
            "marketing": {"email": 1.3, "push": 1.0, "in_app": 1.2, "sms": 0.7},
            "reminder": {"push": 1.2, "email": 1.1, "in_app": 1.0, "sms": 0.9},
            "system": {"in_app": 1.3, "push": 1.1, "email": 1.0, "sms": 0.5},
        }

        type_multiplier = type_multipliers.get(
            notification_type, {}
        ).get(channel, 1.0)

        return base_score + (performance_score * type_multiplier)

    async def personalize_content(
        self,
        base_content: dict,
        user_profile: UserProfile,
        context: dict,
    ) -> dict:
        """
        Personaliza conteúdo da notificação.

        Substitui variáveis e ajusta tom de comunicação.
        """
        personalized = base_content.copy()

        # Substituir variáveis de usuário
        if user_profile.first_name:
            personalized["title"] = personalized.get("title", "").replace(
                "{name}", user_profile.first_name
            )
            personalized["body"] = personalized.get("body", "").replace(
                "{name}", user_profile.first_name
            )

        # Substituir variáveis de contexto
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if "title" in personalized:
                personalized["title"] = personalized["title"].replace(
                    placeholder, str(value)
                )
            if "body" in personalized:
                personalized["body"] = personalized["body"].replace(
                    placeholder, str(value)
                )

        # Ajustar tom baseado no perfil
        tone = self._determine_communication_tone(user_profile)
        personalized = self._adjust_content_tone(personalized, tone)

        # Adicionar CTA personalizada
        personalized["cta"] = self._generate_personalized_cta(
            base_content, user_profile
        )

        return personalized

    def _determine_communication_tone(self, user_profile: UserProfile) -> str:
        """Determina tom de comunicação baseado no perfil."""
        engagement_style = user_profile.engagement_style
        age_group = user_profile.age_group

        tone_mapping = {
            ("professional", "adult"): "formal",
            ("professional", None): "formal",
            ("casual", "young"): "informal",
            ("tech", "adult"): "technical",
            ("creative", None): "creative",
        }

        for (style, age), tone in tone_mapping.items():
            if engagement_style == style and (age is None or age_group == age):
                return tone

        return "neutral"

    def _adjust_content_tone(self, content: dict, tone: str) -> dict:
        """Ajusta tom do conteúdo."""
        # Ajustes baseados no tom
        # Em produção, isso usaria LLM para reescrever o conteúdo

        adjusted = content.copy()

        if tone == "informal":
            # Adicionar emojis e linguagem casual
            if "title" in adjusted:
                adjusted["title"] = adjusted["title"].replace("!", " 🎉")
        elif tone == "formal":
            # Remover informalidades
            pass

        return adjusted

    def _generate_personalized_cta(
        self,
        base_content: dict,
        user_profile: UserProfile,
    ) -> dict:
        """Gera CTA personalizada."""
        base_cta = base_content.get("cta", {})

        # Personalizar texto do CTA baseado no comportamento
        engagement = user_profile.engagement_metrics.get("engagement_score", 0.5)

        if engagement > 0.7:
            cta_text = base_cta.get("text", "Ver mais")
        elif engagement > 0.4:
            cta_text = base_cta.get("text", "Confira agora")
        else:
            cta_text = "Não perca!"

        return {
            "text": cta_text,
            "url": base_cta.get("url", ""),
            "action": base_cta.get("action", "navigate"),
        }

    async def predict_engagement(
        self,
        user_profile: UserProfile,
        notification_type: str,
        timing: datetime,
        channel: str,
    ) -> float:
        """
        Prediz probabilidade de engajamento.

        Usa features do usuário, timing, canal e tipo
        para estimar probabilidade de interação.
        """
        # Features base
        base_engagement = user_profile.engagement_metrics.get("engagement_score", 0.5)

        # Ajuste por canal
        channel_rates = {
            "push": 0.70,
            "email": 0.45,
            "sms": 0.95,
            "in_app": 0.85,
        }
        channel_factor = channel_rates.get(channel, 0.5)

        # Ajuste por tipo
        type_factors = {
            "urgent": 1.2,
            "reminder": 1.1,
            "system": 1.0,
            "marketing": 0.8,
        }
        type_factor = type_factors.get(notification_type, 1.0)

        # Ajuste por timing (horário de pico = +10%)
        hour = timing.hour
        peak_hours = user_profile.activity_patterns.get("peak_hours", [])
        timing_factor = 1.1 if hour in peak_hours else 1.0

        # Calcular score final
        engagement_probability = (
            base_engagement * 0.4
            + channel_factor * 0.3
            + (type_factor * 0.15)
            + (timing_factor * 0.15)
        )

        return min(max(engagement_probability, 0.0), 1.0)

    def get_personalization_factors(self, user_profile: UserProfile) -> dict:
        """Retorna fatores usados na personalização."""
        return {
            "user_engagement_level": user_profile.engagement_metrics.get(
                "engagement_score", 0
            ),
            "preferred_channels": user_profile.preferences.get(
                "preferred_channels", []
            ),
            "peak_hours": user_profile.activity_patterns.get("peak_hours", []),
            "communication_tone": self._determine_communication_tone(user_profile),
            "churn_risk": user_profile.engagement_metrics.get("churn_risk", 0),
        }

    async def should_suppress_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Verifica se notificação deve ser suprimida.

        Retorna (should_suppress, reason).
        """
        user_profile = await self.get_user_profile(db, user_id)

        # Verificar quiet hours
        now = datetime.utcnow()
        quiet_start = user_profile.preferences.get("quiet_hours_start", "22:00")
        quiet_end = user_profile.preferences.get("quiet_hours_end", "08:00")

        if not self._is_outside_quiet_hours(now.hour, quiet_start, quiet_end):
            # Permitir urgentes mesmo em quiet hours
            if notification_type != "urgent":
                return True, "quiet_hours"

        # Verificar limite diário
        max_daily = user_profile.preferences.get("max_daily_notifications", 10)
        sent_today = await self._count_notifications_today(db, user_id)

        if sent_today >= max_daily:
            if notification_type not in ["urgent", "system"]:
                return True, "daily_limit_reached"

        # Verificar se canal está desabilitado
        preferred_channels = user_profile.preferences.get("preferred_channels", [])
        if not preferred_channels:
            return True, "all_channels_disabled"

        return False, None

    async def _count_notifications_today(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> int:
        """Conta notificações enviadas hoje."""
        # TODO: Contar do histórico real
        return 3
