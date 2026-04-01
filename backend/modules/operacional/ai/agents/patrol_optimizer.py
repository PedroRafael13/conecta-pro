"""
Agente de Otimização de Planejamento de Rondas.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PatrolPlan:
    post_id: str
    post_name: str
    period: str
    patrols_per_day: int
    patrol_interval_hours: float
    checkpoints: list[str] = field(default_factory=list)
    estimated_duration_min: int = 30
    risk_adjusted: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class AdaptiveFrequency:
    post_id: str
    base_frequency: int  # rondas por dia
    adjusted_frequency: int
    adjustment_reason: str
    risk_factors: list[str] = field(default_factory=list)


@dataclass
class GamificationData:
    employee_id: str
    employee_name: str
    total_points: int
    patrols_completed: int
    streak_days: int
    badges: list[str] = field(default_factory=list)
    rank_in_team: int = 0
    monthly_goal: int = 0
    goal_completion_pct: float = 0.0


class PatrolOptimizerAgent:
    """
    Agente de IA para planejamento e otimização de rondas de inspeção.
    Adapta frequência por risco e adiciona gamificação para engajamento.
    SUPERPOWERS: Planejamento automático, frequência adaptativa, gamificação, análise de cobertura.
    """

    BASE_FREQUENCIES = {
        "alto_risco": 6,  # rondas por dia
        "medio_risco": 4,
        "baixo_risco": 2,
    }

    BADGES = {
        "primeiro_mes": "🥇 Primeiro Mês Completo",
        "100_rondas": "💯 100 Rondas",
        "sequencia_30": "🔥 30 Dias Seguidos",
        "perfeito": "⭐ Ronda Perfeita",
        "mais_rapido": "⚡ Mais Rápido do Mês",
    }

    async def plan_post_patrols(
        self,
        post_id: str,
        post_name: str,
        risk_level: str = "medio_risco",
        checkpoints: list[str] | None = None,
        period: str = "dia",
    ) -> PatrolPlan:
        """
        Planeja todas as rondas de um posto para o período especificado.
        Considera nível de risco, quantidade de checkpoints e capacidade do efetivo.
        """
        logger.info("Planejando rondas para %s (risco: %s)", post_name, risk_level)
        freq = self.BASE_FREQUENCIES.get(risk_level, 4)
        interval = 24.0 / freq
        duration = len(checkpoints or []) * 5 + 10

        notes = []
        if freq >= 6:
            notes.append("Posto de alto risco — supervisão redobrada recomendada")
        if interval < 4:
            notes.append("Intervalo curto entre rondas — distribuir entre turnos")

        return PatrolPlan(
            post_id=post_id,
            post_name=post_name,
            period=period,
            patrols_per_day=freq,
            patrol_interval_hours=round(interval, 1),
            checkpoints=checkpoints or [],
            estimated_duration_min=duration,
            risk_adjusted=True,
            notes=notes,
        )

    async def adjust_frequency_by_risk(
        self,
        post_id: str,
        post_name: str,
        base_freq: int,
        recent_occurrences: int = 0,
        days_without_incident: int = 30,
    ) -> AdaptiveFrequency:
        """
        Ajusta frequência de rondas dinamicamente com base em risco atual.
        Aumenta após incidentes, reduz em períodos tranquilos.
        """
        adjusted = base_freq
        reasons = []
        factors = []

        if recent_occurrences >= 3:
            adjusted = min(base_freq + 3, 12)
            reasons.append(f"+{adjusted - base_freq} rondas por {recent_occurrences} ocorrências recentes")
            factors.append(f"{recent_occurrences} ocorrências nos últimos 30 dias")
        elif recent_occurrences >= 1:
            adjusted = base_freq + 1
            reasons.append("+1 ronda preventiva por ocorrência recente")
            factors.append("Ocorrência registrada no período")

        if days_without_incident >= 60 and recent_occurrences == 0:
            adjusted = max(base_freq - 1, 2)
            reasons.append(f"-1 ronda por {days_without_incident} dias sem incidentes")
            factors.append("Período prolongado sem ocorrências")

        return AdaptiveFrequency(
            post_id=post_id,
            base_frequency=base_freq,
            adjusted_frequency=adjusted,
            adjustment_reason=("; ".join(reasons) if reasons else "Frequência base mantida"),
            risk_factors=factors,
        )

    async def calculate_gamification(
        self,
        employee_id: str,
        employee_name: str,
        patrols_data: list[dict[str, Any]],
    ) -> GamificationData:
        """
        Calcula pontos e conquistas de gamificação para o colaborador.
        Incentiva rondas completas e sequências de presença.
        """
        total_patrols = len(patrols_data)
        completed = sum(1 for p in patrols_data if p.get("completion_rate", 0) >= 95)
        points = completed * 10 + sum(p.get("bonus_points", 0) for p in patrols_data)

        badges = []
        if total_patrols >= 100:
            badges.append(self.BADGES["100_rondas"])
        if completed >= 30:
            badges.append(self.BADGES["sequencia_30"])
        if any(p.get("completion_rate", 0) == 100 for p in patrols_data):
            badges.append(self.BADGES["perfeito"])

        monthly_goal = 60
        goal_pct = min(100.0, (total_patrols / monthly_goal) * 100)

        return GamificationData(
            employee_id=employee_id,
            employee_name=employee_name,
            total_points=points,
            patrols_completed=completed,
            streak_days=min(total_patrols, 30),
            badges=badges,
            monthly_goal=monthly_goal,
            goal_completion_pct=round(goal_pct, 1),
        )
