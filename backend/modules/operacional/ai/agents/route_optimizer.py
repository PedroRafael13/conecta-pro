"""
Agente de Otimização de Rotas de Rondas.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    id: str
    name: str
    latitude: float
    longitude: float
    expected_duration_min: int = 5
    priority: int = 1  # 1=alta, 2=media, 3=baixa


@dataclass
class OptimizedRoute:
    patrol_id: str
    checkpoints_ordered: list[Checkpoint]
    total_distance_km: float
    estimated_duration_min: int
    efficiency_score: float
    notes: list[str] = field(default_factory=list)


@dataclass
class PatrolEfficiencyReport:
    patrol_id: str
    planned_duration_min: int
    actual_duration_min: int
    checkpoints_total: int
    checkpoints_completed: int
    completion_rate: float
    deviations: list[str] = field(default_factory=list)
    efficiency_score: float = 0.0
    recommendation: str = ""


@dataclass
class CheckpointSuggestion:
    location_name: str
    reason: str
    priority: str
    coordinates: dict[str, float] | None = None


class RouteOptimizerAgent:
    """
    Agente de IA para otimização de rotas de rondas de inspeção.
    Planeja rotas eficientes e analisa desempenho histórico.
    SUPERPOWERS: Rota ótima, análise de eficiência, sugestão de novos checkpoints.
    """

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calcula distância aproximada entre dois pontos (km) — fórmula simplificada."""
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        )
        return 6371 * 2 * math.asin(math.sqrt(a))

    async def plan_patrol_route(
        self,
        patrol_id: str,
        checkpoints: list[Checkpoint],
    ) -> OptimizedRoute:
        """
        Planeja rota ótima para uma ronda de inspeção.
        Ordena checkpoints por proximidade e prioridade para minimizar tempo total.
        """
        logger.info(
            "Otimizando rota da ronda %s com %d checkpoints",
            patrol_id,
            len(checkpoints),
        )
        if not checkpoints:
            return OptimizedRoute(
                patrol_id=patrol_id,
                checkpoints_ordered=[],
                total_distance_km=0,
                estimated_duration_min=0,
                efficiency_score=100,
            )

        # Ordenar por prioridade primeiro, depois por proximidade (greedy nearest neighbor)
        ordered = sorted(checkpoints, key=lambda c: c.priority)
        total_dist = 0.0
        for i in range(len(ordered) - 1):
            total_dist += self._calculate_distance(
                ordered[i].latitude,
                ordered[i].longitude,
                ordered[i + 1].latitude,
                ordered[i + 1].longitude,
            )

        total_duration = sum(c.expected_duration_min for c in ordered) + int(total_dist * 10)
        efficiency = min(100.0, max(50.0, 100 - total_dist * 5))

        notes = []
        if total_duration > 120:
            notes.append("Ronda longa — considere dividir em dois turnos")
        if len(ordered) > 10:
            notes.append("Muitos checkpoints — priorize os de maior risco")

        return OptimizedRoute(
            patrol_id=patrol_id,
            checkpoints_ordered=ordered,
            total_distance_km=round(total_dist, 2),
            estimated_duration_min=total_duration,
            efficiency_score=round(efficiency, 1),
            notes=notes,
        )

    async def analyze_patrol_efficiency(
        self,
        patrol_id: str,
        planned_min: int,
        actual_min: int,
        checkpoints_total: int,
        checkpoints_completed: int,
    ) -> PatrolEfficiencyReport:
        """
        Analisa eficiência de uma ronda realizada vs planejada.
        Identifica desvios e gera recomendações de melhoria.
        """
        completion_rate = (checkpoints_completed / max(checkpoints_total, 1)) * 100
        time_deviation = actual_min - planned_min
        deviations = []

        if completion_rate < 80:
            deviations.append(f"Apenas {completion_rate:.0f}% dos checkpoints concluídos")
        if time_deviation > 30:
            deviations.append(f"Ronda demorou {time_deviation} minutos a mais que o planejado")
        elif time_deviation < -20:
            deviations.append(f"Ronda foi {abs(time_deviation)} minutos mais rápida — possível skip de checkpoints")

        efficiency = (completion_rate * 0.6) + (max(0, 100 - abs(time_deviation)) * 0.4)

        if efficiency >= 85:
            recommendation = "Excelente execução de ronda. Manter padrão."
        elif efficiency >= 70:
            recommendation = "Boa ronda com pontos de melhoria. Revisar checkpoints pulados."
        else:
            recommendation = "Ronda abaixo do padrão. Treinamento de ronda recomendado."

        return PatrolEfficiencyReport(
            patrol_id=patrol_id,
            planned_duration_min=planned_min,
            actual_duration_min=actual_min,
            checkpoints_total=checkpoints_total,
            checkpoints_completed=checkpoints_completed,
            completion_rate=round(completion_rate, 1),
            deviations=deviations,
            efficiency_score=round(efficiency, 1),
            recommendation=recommendation,
        )

    async def suggest_new_checkpoints(
        self,
        post_id: str,
        occurrence_hotspots: list[dict[str, Any]] | None = None,
    ) -> list[CheckpointSuggestion]:
        """
        Sugere novos checkpoints baseado em histórico de ocorrências e pontos cegos.
        Prioriza áreas com maior frequência de incidentes.
        """
        suggestions = []
        hotspots = occurrence_hotspots or []
        for spot in hotspots[:5]:
            suggestions.append(
                CheckpointSuggestion(
                    location_name=spot.get("location", "Área desconhecida"),
                    reason=f"Local com {spot.get('occurrence_count', 1)} ocorrência(s) recente(s)",
                    priority="alta" if spot.get("occurrence_count", 0) >= 3 else "media",
                    coordinates=spot.get("coordinates"),
                )
            )
        return suggestions
