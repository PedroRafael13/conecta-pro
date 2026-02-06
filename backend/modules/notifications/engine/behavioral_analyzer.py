"""Analisador comportamental para notificações."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class EngagementLevel(Enum):
    """Níveis de engajamento."""

    HIGHLY_ENGAGED = "highly_engaged"
    ENGAGED = "engaged"
    MODERATE = "moderate"
    LOW = "low"
    AT_RISK = "at_risk"
    CHURNED = "churned"


class BehaviorPattern(Enum):
    """Padrões de comportamento identificados."""

    MORNING_ACTIVE = "morning_active"
    AFTERNOON_ACTIVE = "afternoon_active"
    EVENING_ACTIVE = "evening_active"
    WEEKEND_ACTIVE = "weekend_active"
    QUICK_RESPONDER = "quick_responder"
    DELAYED_RESPONDER = "delayed_responder"
    BATCH_READER = "batch_reader"
    IMMEDIATE_READER = "immediate_reader"
    SELECTIVE_OPENER = "selective_opener"
    POWER_USER = "power_user"


@dataclass
class UserBehaviorProfile:
    """Perfil comportamental do usuário."""

    user_id: int
    engagement_level: EngagementLevel
    patterns: list[BehaviorPattern]
    preferred_hours: list[int]
    preferred_days: list[int]
    avg_response_time_minutes: float
    notification_fatigue_score: float
    churn_risk_score: float
    segment: str
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BehaviorInsight:
    """Insight comportamental."""

    insight_type: str
    description: str
    confidence: float
    recommendation: str
    data: dict


@dataclass
class EngagementPrediction:
    """Predição de engajamento."""

    will_open: bool
    open_probability: float
    will_click: bool
    click_probability: float
    will_convert: bool
    conversion_probability: float
    best_time_to_send: datetime
    reasoning: str


class BehavioralAnalyzer:
    """
    Analisador de comportamento do usuário.

    Analisa padrões de:
    - Engajamento com notificações
    - Horários de atividade
    - Preferências de conteúdo
    - Sinais de fadiga/churn
    """

    # Thresholds para classificação
    ENGAGEMENT_THRESHOLDS = {
        EngagementLevel.HIGHLY_ENGAGED: {"open_rate": 0.8, "click_rate": 0.3},
        EngagementLevel.ENGAGED: {"open_rate": 0.6, "click_rate": 0.2},
        EngagementLevel.MODERATE: {"open_rate": 0.4, "click_rate": 0.1},
        EngagementLevel.LOW: {"open_rate": 0.2, "click_rate": 0.05},
        EngagementLevel.AT_RISK: {"open_rate": 0.1, "click_rate": 0.02},
    }

    # Pesos para cálculo de fatigue
    FATIGUE_WEIGHTS = {
        "notifications_per_day": 0.3,
        "consecutive_ignores": 0.4,
        "time_since_engagement": 0.3,
    }

    def __init__(
        self,
        lookback_days: int = 30,
        fatigue_threshold: float = 0.7,
        churn_threshold: float = 0.8,
    ) -> None:
        """
        Inicializa o analisador.

        Args:
            lookback_days: Dias para análise histórica
            fatigue_threshold: Threshold de fadiga
            churn_threshold: Threshold de risco de churn
        """
        self.lookback_days = lookback_days
        self.fatigue_threshold = fatigue_threshold
        self.churn_threshold = churn_threshold

    async def analyze_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> UserBehaviorProfile:
        """
        Analisa comportamento completo do usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário

        Returns:
            UserBehaviorProfile com análise completa
        """
        # Obter histórico
        history = await self._get_notification_history(db, user_id)
        activity = await self._get_activity_data(db, user_id)

        # Calcular métricas
        engagement = self._calculate_engagement_level(history)
        patterns = self._identify_patterns(history, activity)
        preferred_hours = self._calculate_preferred_hours(history)
        preferred_days = self._calculate_preferred_days(history)
        avg_response = self._calculate_avg_response_time(history)
        fatigue = self._calculate_fatigue_score(history)
        churn_risk = self._calculate_churn_risk(history, activity)
        segment = self._determine_segment(engagement, patterns)

        return UserBehaviorProfile(
            user_id=user_id,
            engagement_level=engagement,
            patterns=patterns,
            preferred_hours=preferred_hours,
            preferred_days=preferred_days,
            avg_response_time_minutes=avg_response,
            notification_fatigue_score=fatigue,
            churn_risk_score=churn_risk,
            segment=segment,
        )

    async def predict_engagement(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        content_category: Optional[str] = None,
        send_time: Optional[datetime] = None,
    ) -> EngagementPrediction:
        """
        Prediz engajamento para uma notificação.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            notification_type: Tipo da notificação
            content_category: Categoria do conteúdo
            send_time: Horário de envio planejado

        Returns:
            EngagementPrediction com probabilidades
        """
        profile = await self.analyze_user(db, user_id)
        send_time = send_time or datetime.utcnow()

        # Calcular probabilidades base
        base_open = self._get_base_open_rate(profile.engagement_level)
        base_click = self._get_base_click_rate(profile.engagement_level)

        # Ajustar por horário
        hour_factor = self._calculate_hour_factor(send_time.hour, profile.preferred_hours)

        # Ajustar por dia
        day_factor = self._calculate_day_factor(send_time.weekday(), profile.preferred_days)

        # Ajustar por tipo
        type_factor = self._get_type_engagement_factor(notification_type)

        # Ajustar por fadiga
        fatigue_factor = 1.0 - (profile.notification_fatigue_score * 0.5)

        # Calcular probabilidades finais
        open_prob = min(base_open * hour_factor * day_factor * type_factor * fatigue_factor, 0.99)
        click_prob = min(base_click * hour_factor * day_factor * type_factor * fatigue_factor, 0.99)
        convert_prob = click_prob * 0.3  # Estimativa conservadora

        # Determinar melhor horário
        best_time = await self._find_best_send_time(profile, send_time)

        # Gerar reasoning
        reasoning = self._generate_prediction_reasoning(
            profile, open_prob, hour_factor, fatigue_factor
        )

        return EngagementPrediction(
            will_open=open_prob > 0.5,
            open_probability=open_prob,
            will_click=click_prob > 0.15,
            click_probability=click_prob,
            will_convert=convert_prob > 0.05,
            conversion_probability=convert_prob,
            best_time_to_send=best_time,
            reasoning=reasoning,
        )

    async def get_insights(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[BehaviorInsight]:
        """
        Gera insights comportamentais.

        Args:
            db: Sessão do banco
            user_id: ID do usuário

        Returns:
            Lista de BehaviorInsight
        """
        profile = await self.analyze_user(db, user_id)
        insights = []

        # Insight de engajamento
        if profile.engagement_level in [EngagementLevel.AT_RISK, EngagementLevel.LOW]:
            insights.append(
                BehaviorInsight(
                    insight_type="engagement_alert",
                    description=f"Usuário com engajamento {profile.engagement_level.value}",
                    confidence=0.85,
                    recommendation="Reduzir frequência e personalizar mais",
                    data={"level": profile.engagement_level.value},
                )
            )

        # Insight de fadiga
        if profile.notification_fatigue_score > self.fatigue_threshold:
            insights.append(
                BehaviorInsight(
                    insight_type="fatigue_warning",
                    description=f"Score de fadiga alto: {profile.notification_fatigue_score:.2f}",
                    confidence=0.80,
                    recommendation="Implementar período de cooldown",
                    data={"fatigue_score": profile.notification_fatigue_score},
                )
            )

        # Insight de churn
        if profile.churn_risk_score > self.churn_threshold:
            insights.append(
                BehaviorInsight(
                    insight_type="churn_risk",
                    description=f"Risco de churn: {profile.churn_risk_score:.2f}",
                    confidence=0.75,
                    recommendation="Ativar campanha de reengajamento",
                    data={"churn_score": profile.churn_risk_score},
                )
            )

        # Insight de padrões
        for pattern in profile.patterns:
            if pattern == BehaviorPattern.QUICK_RESPONDER:
                insights.append(
                    BehaviorInsight(
                        insight_type="pattern_identified",
                        description="Usuário responde rapidamente",
                        confidence=0.90,
                        recommendation="Enviar notificações time-sensitive",
                        data={"pattern": pattern.value},
                    )
                )
            elif pattern == BehaviorPattern.BATCH_READER:
                insights.append(
                    BehaviorInsight(
                        insight_type="pattern_identified",
                        description="Usuário lê notificações em lote",
                        confidence=0.85,
                        recommendation="Considerar digest diário",
                        data={"pattern": pattern.value},
                    )
                )

        return insights

    async def should_send_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        importance: str = "normal",
    ) -> tuple[bool, str]:
        """
        Determina se deve enviar notificação.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            notification_type: Tipo da notificação
            importance: Importância (low, normal, high, critical)

        Returns:
            Tuple (deve_enviar, razão)
        """
        profile = await self.analyze_user(db, user_id)

        # Notificações críticas sempre enviam
        if importance == "critical":
            return True, "Critical notifications always sent"

        # Verificar fadiga
        if profile.notification_fatigue_score > self.fatigue_threshold:
            if importance in ["low", "normal"]:
                return False, f"User fatigue score too high: {profile.notification_fatigue_score:.2f}"

        # Verificar engajamento
        if profile.engagement_level == EngagementLevel.CHURNED:
            if importance == "low":
                return False, "User appears churned, skipping low priority"

        # Verificar rate limits
        recent_count = await self._get_recent_notification_count(db, user_id)
        daily_limit = self._get_daily_limit(profile.engagement_level)

        if recent_count >= daily_limit:
            if importance != "high":
                return False, f"Daily limit reached: {recent_count}/{daily_limit}"

        return True, "All checks passed"

    async def _get_notification_history(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém histórico de notificações."""
        # TODO: Buscar do repositório real

        return {
            "total_sent": 50,
            "total_opened": 35,
            "total_clicked": 15,
            "total_converted": 5,
            "by_hour": {h: {"sent": 5, "opened": 3} for h in range(24)},
            "by_day": {d: {"sent": 10, "opened": 7} for d in range(7)},
            "response_times": [5, 10, 15, 30, 60, 120],  # minutos
            "last_engagement": datetime.utcnow() - timedelta(days=2),
            "consecutive_ignores": 2,
            "notifications_today": 3,
        }

    async def _get_activity_data(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém dados de atividade do usuário."""
        # TODO: Buscar do repositório real

        return {
            "last_login": datetime.utcnow() - timedelta(hours=5),
            "sessions_30d": 25,
            "avg_session_duration_minutes": 15,
            "pages_viewed_30d": 150,
            "actions_30d": 80,
        }

    def _calculate_engagement_level(self, history: dict) -> EngagementLevel:
        """Calcula nível de engajamento."""
        total_sent = history.get("total_sent", 1)
        total_opened = history.get("total_opened", 0)
        total_clicked = history.get("total_clicked", 0)

        open_rate = total_opened / max(total_sent, 1)
        click_rate = total_clicked / max(total_sent, 1)

        for level, thresholds in self.ENGAGEMENT_THRESHOLDS.items():
            if open_rate >= thresholds["open_rate"] and click_rate >= thresholds["click_rate"]:
                return level

        # Verificar se é churned
        last_engagement = history.get("last_engagement")
        if last_engagement and (datetime.utcnow() - last_engagement).days > 30:
            return EngagementLevel.CHURNED

        return EngagementLevel.AT_RISK

    def _identify_patterns(
        self,
        history: dict,
        activity: dict,
    ) -> list[BehaviorPattern]:
        """Identifica padrões comportamentais."""
        patterns = []

        # Padrões de horário
        by_hour = history.get("by_hour", {})
        morning_engagement = sum(by_hour.get(h, {}).get("opened", 0) for h in range(6, 12))
        afternoon_engagement = sum(by_hour.get(h, {}).get("opened", 0) for h in range(12, 18))
        evening_engagement = sum(by_hour.get(h, {}).get("opened", 0) for h in range(18, 24))

        max_engagement = max(morning_engagement, afternoon_engagement, evening_engagement)
        if max_engagement > 0:
            if morning_engagement == max_engagement:
                patterns.append(BehaviorPattern.MORNING_ACTIVE)
            elif afternoon_engagement == max_engagement:
                patterns.append(BehaviorPattern.AFTERNOON_ACTIVE)
            else:
                patterns.append(BehaviorPattern.EVENING_ACTIVE)

        # Padrão de resposta
        response_times = history.get("response_times", [])
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            if avg_response < 15:
                patterns.append(BehaviorPattern.QUICK_RESPONDER)
            elif avg_response > 60:
                patterns.append(BehaviorPattern.DELAYED_RESPONDER)

        # Padrão de leitura
        consecutive_ignores = history.get("consecutive_ignores", 0)
        if consecutive_ignores >= 3:
            patterns.append(BehaviorPattern.BATCH_READER)
        elif consecutive_ignores == 0:
            patterns.append(BehaviorPattern.IMMEDIATE_READER)

        # Power user
        sessions = activity.get("sessions_30d", 0)
        actions = activity.get("actions_30d", 0)
        if sessions > 20 and actions > 50:
            patterns.append(BehaviorPattern.POWER_USER)

        return patterns

    def _calculate_preferred_hours(self, history: dict) -> list[int]:
        """Calcula horários preferidos."""
        by_hour = history.get("by_hour", {})
        if not by_hour:
            return [9, 10, 14, 15, 18]

        # Ordenar por engajamento
        sorted_hours = sorted(
            by_hour.items(),
            key=lambda x: x[1].get("opened", 0) / max(x[1].get("sent", 1), 1),
            reverse=True,
        )

        return [h for h, _ in sorted_hours[:5]]

    def _calculate_preferred_days(self, history: dict) -> list[int]:
        """Calcula dias preferidos."""
        by_day = history.get("by_day", {})
        if not by_day:
            return [0, 1, 2, 3, 4]  # Segunda a Sexta

        sorted_days = sorted(
            by_day.items(),
            key=lambda x: x[1].get("opened", 0) / max(x[1].get("sent", 1), 1),
            reverse=True,
        )

        return [d for d, _ in sorted_days[:5]]

    def _calculate_avg_response_time(self, history: dict) -> float:
        """Calcula tempo médio de resposta."""
        response_times = history.get("response_times", [])
        if not response_times:
            return 30.0
        return sum(response_times) / len(response_times)

    def _calculate_fatigue_score(self, history: dict) -> float:
        """Calcula score de fadiga."""
        # Fator de frequência
        notifications_today = history.get("notifications_today", 0)
        freq_factor = min(notifications_today / 10, 1.0)

        # Fator de ignores consecutivos
        consecutive_ignores = history.get("consecutive_ignores", 0)
        ignore_factor = min(consecutive_ignores / 5, 1.0)

        # Fator de tempo desde engajamento
        last_engagement = history.get("last_engagement")
        if last_engagement:
            days_since = (datetime.utcnow() - last_engagement).days
            time_factor = min(days_since / 14, 1.0)
        else:
            time_factor = 0.5

        score = (
            freq_factor * self.FATIGUE_WEIGHTS["notifications_per_day"]
            + ignore_factor * self.FATIGUE_WEIGHTS["consecutive_ignores"]
            + time_factor * self.FATIGUE_WEIGHTS["time_since_engagement"]
        )

        return min(max(score, 0.0), 1.0)

    def _calculate_churn_risk(self, history: dict, activity: dict) -> float:
        """Calcula risco de churn."""
        # Fator de engajamento com notificações
        total_sent = history.get("total_sent", 1)
        total_opened = history.get("total_opened", 0)
        open_rate = total_opened / max(total_sent, 1)
        engagement_factor = 1.0 - open_rate

        # Fator de atividade
        last_login = activity.get("last_login")
        if last_login:
            days_since_login = (datetime.utcnow() - last_login).days
            login_factor = min(days_since_login / 30, 1.0)
        else:
            login_factor = 0.8

        # Fator de sessões
        sessions = activity.get("sessions_30d", 0)
        session_factor = 1.0 - min(sessions / 30, 1.0)

        # Score combinado
        score = (engagement_factor * 0.4 + login_factor * 0.35 + session_factor * 0.25)

        return min(max(score, 0.0), 1.0)

    def _determine_segment(
        self,
        engagement: EngagementLevel,
        patterns: list[BehaviorPattern],
    ) -> str:
        """Determina segmento do usuário."""
        if BehaviorPattern.POWER_USER in patterns:
            return "power_user"
        if engagement == EngagementLevel.HIGHLY_ENGAGED:
            return "champion"
        if engagement == EngagementLevel.ENGAGED:
            return "engaged"
        if engagement in [EngagementLevel.AT_RISK, EngagementLevel.CHURNED]:
            return "at_risk"
        return "standard"

    def _get_base_open_rate(self, level: EngagementLevel) -> float:
        """Retorna taxa base de abertura."""
        rates = {
            EngagementLevel.HIGHLY_ENGAGED: 0.85,
            EngagementLevel.ENGAGED: 0.65,
            EngagementLevel.MODERATE: 0.45,
            EngagementLevel.LOW: 0.25,
            EngagementLevel.AT_RISK: 0.15,
            EngagementLevel.CHURNED: 0.05,
        }
        return rates.get(level, 0.5)

    def _get_base_click_rate(self, level: EngagementLevel) -> float:
        """Retorna taxa base de clique."""
        rates = {
            EngagementLevel.HIGHLY_ENGAGED: 0.35,
            EngagementLevel.ENGAGED: 0.25,
            EngagementLevel.MODERATE: 0.15,
            EngagementLevel.LOW: 0.08,
            EngagementLevel.AT_RISK: 0.03,
            EngagementLevel.CHURNED: 0.01,
        }
        return rates.get(level, 0.15)

    def _calculate_hour_factor(self, hour: int, preferred: list[int]) -> float:
        """Calcula fator de ajuste por hora."""
        if hour in preferred[:3]:
            return 1.2
        if hour in preferred:
            return 1.0
        if 0 <= hour <= 6 or hour >= 23:
            return 0.5
        return 0.8

    def _calculate_day_factor(self, day: int, preferred: list[int]) -> float:
        """Calcula fator de ajuste por dia."""
        if day in preferred[:3]:
            return 1.1
        if day in preferred:
            return 1.0
        return 0.9

    def _get_type_engagement_factor(self, notification_type: str) -> float:
        """Retorna fator de engajamento por tipo."""
        factors = {
            "urgent": 1.3,
            "transaction": 1.2,
            "system": 1.1,
            "reminder": 1.0,
            "social": 0.9,
            "marketing": 0.8,
        }
        return factors.get(notification_type, 1.0)

    async def _find_best_send_time(
        self,
        profile: UserBehaviorProfile,
        reference_time: datetime,
    ) -> datetime:
        """Encontra melhor horário para envio."""
        if not profile.preferred_hours:
            # Usar horário comercial padrão
            best_hour = 10
        else:
            best_hour = profile.preferred_hours[0]

        # Ajustar para próximo horário disponível
        result = reference_time.replace(hour=best_hour, minute=0, second=0, microsecond=0)

        if result <= reference_time:
            result += timedelta(days=1)

        return result

    def _generate_prediction_reasoning(
        self,
        profile: UserBehaviorProfile,
        open_prob: float,
        hour_factor: float,
        fatigue_factor: float,
    ) -> str:
        """Gera explicação da predição."""
        reasons = []

        reasons.append(f"User segment: {profile.segment}")
        reasons.append(f"Engagement level: {profile.engagement_level.value}")

        if hour_factor > 1.0:
            reasons.append("Optimal send time")
        elif hour_factor < 0.8:
            reasons.append("Non-optimal time")

        if fatigue_factor < 0.8:
            reasons.append(f"High fatigue ({profile.notification_fatigue_score:.2f})")

        return f"Open probability {open_prob:.0%}: {'; '.join(reasons)}"

    async def _get_recent_notification_count(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> int:
        """Obtém contagem de notificações recentes."""
        # TODO: Buscar do repositório real
        return 3

    def _get_daily_limit(self, level: EngagementLevel) -> int:
        """Retorna limite diário por nível."""
        limits = {
            EngagementLevel.HIGHLY_ENGAGED: 10,
            EngagementLevel.ENGAGED: 8,
            EngagementLevel.MODERATE: 5,
            EngagementLevel.LOW: 3,
            EngagementLevel.AT_RISK: 2,
            EngagementLevel.CHURNED: 1,
        }
        return limits.get(level, 5)
