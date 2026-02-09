"""Otimizador de timing para notificações."""

import logging
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class TimingPrediction:
    """Predição de timing ótimo."""

    optimal_datetime: datetime
    confidence: float
    reasoning: str
    alternative_times: list[datetime]
    should_delay: bool = False
    delay_reason: str | None = None


class TimingOptimizer:
    """
    Otimizador de timing para notificações.

    Analisa padrões de comportamento para determinar
    o melhor momento para enviar notificações.
    """

    # Pesos para diferentes fatores
    ACTIVITY_WEIGHT = 0.35
    RESPONSE_WEIGHT = 0.30
    PREFERENCE_WEIGHT = 0.20
    HISTORICAL_WEIGHT = 0.15

    def __init__(
        self,
        default_window_hours: int = 24,
        min_confidence: float = 0.6,
    ) -> None:
        """
        Inicializa o otimizador.

        Args:
            default_window_hours: Janela padrão para busca de timing
            min_confidence: Confiança mínima para usar timing otimizado
        """
        self.default_window = default_window_hours
        self.min_confidence = min_confidence

    async def optimize_send_time(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        earliest_time: datetime | None = None,
        deadline: datetime | None = None,
    ) -> TimingPrediction:
        """
        Otimiza horário de envio.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            notification_type: Tipo da notificação
            earliest_time: Horário mínimo para envio
            deadline: Deadline máximo

        Returns:
            TimingPrediction com horário ótimo
        """
        now = datetime.utcnow()
        earliest = earliest_time or now
        deadline = deadline or (now + timedelta(hours=self.default_window))

        # Obter dados do usuário
        user_patterns = await self._get_user_patterns(db, user_id)
        preferences = await self._get_user_preferences(db, user_id)
        historical = await self._get_historical_performance(db, user_id)

        # Calcular scores por hora
        hourly_scores = self._calculate_hourly_scores(user_patterns, preferences, historical, notification_type)

        # Filtrar horas dentro da janela
        candidate_times = self._get_candidate_times(earliest, deadline, hourly_scores, preferences)

        if not candidate_times:
            # Fallback: usar earliest_time
            return TimingPrediction(
                optimal_datetime=earliest,
                confidence=0.3,
                reasoning="No optimal time found in window, using earliest available",
                alternative_times=[],
                should_delay=False,
            )

        # Ordenar por score
        sorted_times = sorted(
            candidate_times.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        best_time, best_score = sorted_times[0]
        alternatives = [t for t, _ in sorted_times[1:4]]

        # Verificar se deve atrasar
        should_delay, delay_reason = self._check_should_delay(best_time, preferences, notification_type)

        return TimingPrediction(
            optimal_datetime=best_time,
            confidence=best_score,
            reasoning=self._generate_reasoning(user_patterns, best_time),
            alternative_times=alternatives,
            should_delay=should_delay,
            delay_reason=delay_reason,
        )

    async def _get_user_patterns(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém padrões de atividade do usuário."""
        # TODO: Calcular do histórico real de atividades

        return {
            "peak_hours": [9, 10, 14, 15, 18],
            "low_activity_hours": [0, 1, 2, 3, 4, 5, 6, 22, 23],
            "most_active_days": [1, 2, 3, 4, 5],  # Seg-Sex
            "avg_session_start_hour": 9,
            "avg_response_time_by_hour": {h: 30 + (abs(h - 12) * 5) for h in range(24)},
        }

    async def _get_user_preferences(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém preferências de timing do usuário."""
        # TODO: Buscar do repositório real

        return {
            "quiet_hours_start": time(22, 0),
            "quiet_hours_end": time(8, 0),
            "timezone": "America/Sao_Paulo",
            "preferred_days": [1, 2, 3, 4, 5],
            "allow_weekends": False,
        }

    async def _get_historical_performance(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        """Obtém performance histórica por hora."""
        # TODO: Calcular do histórico real

        return {
            "open_rate_by_hour": {h: 0.5 + (0.2 if 9 <= h <= 18 else 0) for h in range(24)},
            "click_rate_by_hour": {h: 0.2 + (0.1 if 9 <= h <= 18 else 0) for h in range(24)},
        }

    def _calculate_hourly_scores(
        self,
        patterns: dict,
        preferences: dict,
        historical: dict,
        notification_type: str,
    ) -> dict[int, float]:
        """Calcula score de cada hora."""
        scores = {}

        for hour in range(24):
            # Componente de atividade
            activity_score = 1.0 if hour in patterns["peak_hours"] else 0.5
            if hour in patterns["low_activity_hours"]:
                activity_score = 0.2

            # Componente de resposta
            avg_response = patterns["avg_response_time_by_hour"].get(hour, 60)
            response_score = 1.0 - (min(avg_response, 120) / 120)

            # Componente de preferência
            pref_score = self._calculate_preference_score(hour, preferences)

            # Componente histórico
            open_rate = historical["open_rate_by_hour"].get(hour, 0.5)
            click_rate = historical["click_rate_by_hour"].get(hour, 0.2)
            hist_score = (open_rate * 0.6) + (click_rate * 0.4)

            # Score final ponderado
            total_score = (
                activity_score * self.ACTIVITY_WEIGHT
                + response_score * self.RESPONSE_WEIGHT
                + pref_score * self.PREFERENCE_WEIGHT
                + hist_score * self.HISTORICAL_WEIGHT
            )

            # Ajuste por tipo de notificação
            total_score *= self._get_type_multiplier(hour, notification_type)

            scores[hour] = min(max(total_score, 0.0), 1.0)

        return scores

    def _calculate_preference_score(
        self,
        hour: int,
        preferences: dict,
    ) -> float:
        """Calcula score baseado em preferências."""
        quiet_start = preferences.get("quiet_hours_start", time(22, 0))
        quiet_end = preferences.get("quiet_hours_end", time(8, 0))

        # Verificar quiet hours
        start_hour = quiet_start.hour
        end_hour = quiet_end.hour

        if start_hour > end_hour:
            # Quiet hours cruzam meia-noite
            if hour >= start_hour or hour < end_hour:
                return 0.0
        else:
            if start_hour <= hour < end_hour:
                return 0.0

        return 1.0

    def _get_type_multiplier(self, hour: int, notification_type: str) -> float:
        """Retorna multiplicador baseado no tipo e hora."""
        multipliers = {
            "urgent": {
                "business_hours": 1.0,
                "evening": 0.9,
                "night": 0.8,  # Urgentes ainda têm prioridade
            },
            "marketing": {
                "business_hours": 1.2,
                "evening": 1.0,
                "night": 0.3,  # Marketing evita noite
            },
            "reminder": {
                "business_hours": 1.1,
                "evening": 1.0,
                "night": 0.5,
            },
            "system": {
                "business_hours": 1.0,
                "evening": 1.0,
                "night": 0.7,
            },
        }

        # Determinar período do dia
        if 9 <= hour <= 18:
            period = "business_hours"
        elif 19 <= hour <= 22:
            period = "evening"
        else:
            period = "night"

        return multipliers.get(notification_type, {}).get(period, 1.0)

    def _get_candidate_times(
        self,
        earliest: datetime,
        deadline: datetime,
        hourly_scores: dict,
        preferences: dict,
    ) -> dict[datetime, float]:
        """Obtém candidatos de datetime dentro da janela."""
        candidates = {}
        current = earliest.replace(minute=0, second=0, microsecond=0)

        while current <= deadline:
            hour = current.hour
            weekday = current.weekday()

            # Verificar se dia é permitido
            preferred_days = preferences.get("preferred_days", list(range(7)))
            allow_weekends = preferences.get("allow_weekends", True)

            if weekday in preferred_days or (weekday >= 5 and allow_weekends):
                score = hourly_scores.get(hour, 0.5)
                if score > 0.3:  # Threshold mínimo
                    candidates[current] = score

            current += timedelta(hours=1)

        return candidates

    def _check_should_delay(
        self,
        optimal_time: datetime,
        preferences: dict,
        notification_type: str,
    ) -> tuple[bool, str | None]:
        """Verifica se deve atrasar o envio."""
        now = datetime.utcnow()

        # Se timing ótimo é no futuro, atrasar
        if optimal_time > now + timedelta(minutes=5):
            return True, f"Optimal time is {optimal_time.strftime('%H:%M')}"

        # Se é fora do horário comercial e não é urgente
        hour = now.hour
        if hour < 8 or hour >= 22:
            if notification_type not in ["urgent", "system"]:
                return True, "Outside business hours"

        return False, None

    def _generate_reasoning(
        self,
        patterns: dict,
        best_time: datetime,
    ) -> str:
        """Gera explicação do timing escolhido."""
        hour = best_time.hour
        reasons = []

        if hour in patterns["peak_hours"]:
            reasons.append(f"{hour}h is a peak activity hour")

        if 9 <= hour <= 18:
            reasons.append("within business hours")

        return f"Selected {best_time.strftime('%H:%M')} because: {', '.join(reasons) or 'default selection'}"

    async def get_next_available_slot(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        duration_minutes: int = 30,
    ) -> datetime:
        """
        Encontra próximo slot disponível.

        Útil para agendamento de campanhas.
        """
        prediction = await self.optimize_send_time(
            db=db,
            user_id=user_id,
            notification_type=notification_type,
        )

        return prediction.optimal_datetime

    async def batch_optimize(
        self,
        db: AsyncSession,
        user_ids: list[int],
        notification_type: str,
    ) -> dict[int, TimingPrediction]:
        """
        Otimiza timing para múltiplos usuários.

        Útil para campanhas em massa.
        """
        results = {}

        for user_id in user_ids:
            prediction = await self.optimize_send_time(
                db=db,
                user_id=user_id,
                notification_type=notification_type,
            )
            results[user_id] = prediction

        return results
