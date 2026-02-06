"""
MaintenanceSchedulerService - Agendamento inteligente de manutenções.

Este serviço implementa algoritmos de IA para:
- Sugerir datas ideais para manutenções preventivas
- Otimizar alocação de recursos
- Prever necessidade de manutenção baseado em histórico
- Calcular custos estimados
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from core.logging import logger
from modules.facilities.models.maintenance import MaintenancePriority, MaintenanceType


class MaintenanceSchedulerService:
    """
    Serviço inteligente de agendamento de manutenções.

    Implementa algoritmos de IA para otimizar o agendamento
    e alocação de recursos para manutenções.
    """

    # Intervalos padrão de manutenção preventiva (em dias)
    DEFAULT_INTERVALS = {
        "elevadores": 30,
        "ar_condicionado": 90,
        "bombas": 60,
        "geradores": 180,
        "portoes": 90,
        "cameras": 60,
        "extintores": 365,
        "para_raios": 365,
        "caixas_dagua": 180,
        "iluminacao": 90,
        "jardim": 30,
        "piscina": 7,
        "limpeza_fachada": 365,
        "dedetizacao": 180,
        "default": 90,
    }

    # Custo médio por hora de trabalho (R$)
    DEFAULT_HOURLY_RATE = 80.0

    # Prioridades e seus pesos para ordenação
    PRIORITY_WEIGHTS = {
        MaintenancePriority.CRITICAL.value: 100,
        MaintenancePriority.HIGH.value: 75,
        MaintenancePriority.MEDIUM.value: 50,
        MaintenancePriority.LOW.value: 25,
    }

    def __init__(self) -> None:
        """Inicializa o serviço."""
        self._initialized = True

    def suggest_schedule(
        self,
        maintenance_type: MaintenanceType,
        equipment_type: str,
        last_maintenance: Optional[date] = None,
        priority: MaintenancePriority = MaintenancePriority.MEDIUM,
        available_dates: Optional[List[date]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Sugere data ideal para manutenção.

        Args:
            maintenance_type: Tipo de manutenção
            equipment_type: Tipo de equipamento
            last_maintenance: Data da última manutenção
            priority: Prioridade
            available_dates: Datas disponíveis (se restrito)
            constraints: Restrições adicionais

        Returns:
            Sugestão com data, motivos e estimativas
        """
        logger.info(
            f"Calculando sugestão de agendamento para {equipment_type} "
            f"({maintenance_type.value})"
        )

        # Calcular intervalo ideal
        interval = self._get_interval(equipment_type, maintenance_type)

        # Calcular data ideal
        if last_maintenance:
            ideal_date = last_maintenance + timedelta(days=interval)
        else:
            # Sem histórico, agendar em breve
            ideal_date = date.today() + timedelta(days=7)

        # Ajustar baseado na prioridade
        ideal_date = self._adjust_by_priority(ideal_date, priority)

        # Verificar restrições
        if constraints:
            ideal_date = self._apply_constraints(ideal_date, constraints)

        # Verificar disponibilidade
        if available_dates:
            ideal_date = self._find_closest_available(ideal_date, available_dates)

        # Calcular estimativas
        estimated_hours = self._estimate_hours(equipment_type, maintenance_type)
        estimated_cost = self._estimate_cost(estimated_hours, maintenance_type)

        # Gerar motivos
        reasons = self._generate_reasons(
            equipment_type,
            maintenance_type,
            last_maintenance,
            ideal_date,
            priority,
        )

        # Calcular score de urgência (0-100)
        urgency_score = self._calculate_urgency_score(
            last_maintenance,
            interval,
            priority,
        )

        return {
            "suggested_date": ideal_date,
            "interval_days": interval,
            "estimated_hours": estimated_hours,
            "estimated_cost": estimated_cost,
            "urgency_score": urgency_score,
            "reasons": reasons,
            "is_overdue": last_maintenance
            and (date.today() - last_maintenance).days > interval,
            "days_until": (ideal_date - date.today()).days,
            "recommended_team_size": self._recommend_team_size(
                equipment_type,
                maintenance_type,
            ),
        }

    def optimize_schedule(  # pylint: disable=too-many-locals
        self,
        maintenances: List[Dict[str, Any]],
        available_resources: Dict[str, Any],
        date_range: Tuple[date, date],
    ) -> List[Dict[str, Any]]:
        """
        Otimiza agendamento de múltiplas manutenções.

        Args:
            maintenances: Lista de manutenções a agendar
            available_resources: Recursos disponíveis
            date_range: Período para agendamento

        Returns:
            Lista de manutenções com datas otimizadas
        """
        logger.info(f"Otimizando {len(maintenances)} manutenções")

        start_date, end_date = date_range
        scheduled = []
        daily_capacity = available_resources.get("daily_hours", 8)
        daily_usage = {}

        # Ordenar por urgência e prioridade
        sorted_maintenances = sorted(
            maintenances,
            key=lambda m: (
                -self.PRIORITY_WEIGHTS.get(m.get("priority", "medium"), 50),
                m.get("deadline") or date.max,
            ),
        )

        for maint in sorted_maintenances:
            estimated_hours = maint.get("estimated_hours", 4)
            priority = maint.get("priority", MaintenancePriority.MEDIUM.value)

            # Encontrar melhor data
            best_date = None
            best_score = -1

            current_date = start_date
            while current_date <= end_date:
                # Verificar capacidade
                used = daily_usage.get(current_date, 0)
                if used + estimated_hours <= daily_capacity:
                    # Calcular score da data
                    score = self._score_date(
                        current_date,
                        maint.get("ideal_date"),
                        maint.get("deadline"),
                        priority,
                    )

                    if score > best_score:
                        best_score = score
                        best_date = current_date

                current_date += timedelta(days=1)

            if best_date:
                daily_usage[best_date] = daily_usage.get(best_date, 0) + estimated_hours
                scheduled.append(
                    {
                        **maint,
                        "scheduled_date": best_date,
                        "optimization_score": best_score,
                    }
                )
            else:
                # Não foi possível agendar no período
                scheduled.append(
                    {
                        **maint,
                        "scheduled_date": None,
                        "scheduling_error": "Sem capacidade disponível no período",
                    }
                )

        return scheduled

    def predict_next_maintenance(  # pylint: disable=too-many-locals
        self,
        equipment_id: str,
        maintenance_history: List[Dict[str, Any]],
        equipment_age_days: Optional[int] = None,
        usage_intensity: str = "normal",
    ) -> Dict[str, Any]:
        """
        Prevê próxima manutenção baseado em histórico.

        Args:
            equipment_id: ID do equipamento
            maintenance_history: Histórico de manutenções
            equipment_age_days: Idade do equipamento em dias
            usage_intensity: Intensidade de uso (low, normal, high)

        Returns:
            Previsão com data, tipo e probabilidade
        """
        logger.info(f"Prevendo próxima manutenção para equipamento {equipment_id}")

        if not maintenance_history:
            return {
                "predicted_date": date.today() + timedelta(days=30),
                "predicted_type": MaintenanceType.PREVENTIVA.value,
                "confidence": 0.5,
                "reason": "Sem histórico - recomendação padrão",
            }

        # Analisar histórico
        corretivas = [m for m in maintenance_history if m.get("type") == "corretiva"]
        _ = [m for m in maintenance_history if m.get("type") == "preventiva"]  # Para análise futura

        # Calcular intervalos médios
        intervals = []
        sorted_history = sorted(
            maintenance_history,
            key=lambda m: m.get("date", date.min),
        )
        for i in range(1, len(sorted_history)):
            prev_date = sorted_history[i - 1].get("date")
            curr_date = sorted_history[i].get("date")
            if prev_date and curr_date:
                intervals.append((curr_date - prev_date).days)

        avg_interval = sum(intervals) / len(intervals) if intervals else 90

        # Ajustar por intensidade de uso
        intensity_factors = {"low": 1.3, "normal": 1.0, "high": 0.7}
        adjusted_interval = avg_interval * intensity_factors.get(usage_intensity, 1.0)

        # Ajustar por idade do equipamento
        if equipment_age_days:
            if equipment_age_days > 3650:  # > 10 anos
                adjusted_interval *= 0.7
            elif equipment_age_days > 1825:  # > 5 anos
                adjusted_interval *= 0.85

        # Última manutenção
        last_maintenance = sorted_history[-1].get("date") if sorted_history else None
        if last_maintenance:
            predicted_date = last_maintenance + timedelta(days=int(adjusted_interval))
        else:
            predicted_date = date.today() + timedelta(days=int(adjusted_interval))

        # Determinar tipo provável
        corretiva_ratio = len(corretivas) / len(maintenance_history) if maintenance_history else 0
        if corretiva_ratio > 0.5:
            predicted_type = MaintenanceType.CORRETIVA.value
            confidence = 0.6 + (corretiva_ratio * 0.3)
        else:
            predicted_type = MaintenanceType.PREVENTIVA.value
            confidence = 0.7

        return {
            "predicted_date": predicted_date,
            "predicted_type": predicted_type,
            "confidence": round(min(confidence, 0.95), 2),
            "avg_interval_days": int(avg_interval),
            "adjusted_interval_days": int(adjusted_interval),
            "corretiva_ratio": round(corretiva_ratio, 2),
            "total_maintenances": len(maintenance_history),
            "reason": self._generate_prediction_reason(
                predicted_type,
                corretiva_ratio,
                equipment_age_days,
                usage_intensity,
            ),
        }

    def _get_interval(
        self,
        equipment_type: str,
        maintenance_type: MaintenanceType,
    ) -> int:
        """Retorna intervalo de manutenção em dias."""
        base_interval = self.DEFAULT_INTERVALS.get(
            equipment_type.lower(),
            self.DEFAULT_INTERVALS["default"],
        )

        # Manutenção corretiva não segue intervalo
        if maintenance_type == MaintenanceType.CORRETIVA:
            return 0

        # Manutenção emergencial é imediata
        if maintenance_type == MaintenanceType.EMERGENCIAL:
            return 0

        return base_interval

    def _adjust_by_priority(self, ideal_date: date, priority: MaintenancePriority) -> date:
        """Ajusta data baseado na prioridade."""
        today = date.today()

        if priority == MaintenancePriority.CRITICAL:
            # Crítico: no máximo em 3 dias
            return min(ideal_date, today + timedelta(days=3))
        if priority == MaintenancePriority.HIGH:
            # Alto: no máximo em 7 dias
            return min(ideal_date, today + timedelta(days=7))
        if priority == MaintenancePriority.MEDIUM:
            # Médio: mantém data ideal, mas não mais que 30 dias
            return min(ideal_date, today + timedelta(days=30))

        # Baixo: pode adiar até 60 dias
        return max(ideal_date, today + timedelta(days=7))

    def _apply_constraints(
        self,
        ideal_date: date,
        constraints: Dict[str, Any],
    ) -> date:
        """Aplica restrições à data."""
        result_date = ideal_date

        # Evitar fins de semana
        if constraints.get("avoid_weekends", False):
            while result_date.weekday() >= 5:
                result_date += timedelta(days=1)

        # Data mínima
        min_date = constraints.get("min_date")
        if min_date and result_date < min_date:
            result_date = min_date

        # Data máxima
        max_date = constraints.get("max_date")
        if max_date and result_date > max_date:
            result_date = max_date

        # Evitar datas específicas
        blocked_dates = constraints.get("blocked_dates", [])
        while result_date in blocked_dates:
            result_date += timedelta(days=1)

        return result_date

    def _find_closest_available(
        self,
        ideal_date: date,
        available_dates: List[date],
    ) -> date:
        """Encontra data disponível mais próxima da ideal."""
        if not available_dates:
            return ideal_date

        sorted_dates = sorted(available_dates)
        closest = min(sorted_dates, key=lambda d: abs((d - ideal_date).days))
        return closest

    def _estimate_hours(
        self,
        equipment_type: str,
        maintenance_type: MaintenanceType,
    ) -> float:
        """Estima horas de trabalho."""
        base_hours = {
            "elevadores": 4,
            "ar_condicionado": 2,
            "bombas": 3,
            "geradores": 4,
            "portoes": 2,
            "cameras": 2,
            "extintores": 1,
            "iluminacao": 2,
            "piscina": 3,
            "default": 2,
        }

        hours = base_hours.get(equipment_type.lower(), base_hours["default"])

        # Ajustar por tipo
        if maintenance_type == MaintenanceType.CORRETIVA:
            hours *= 1.5
        elif maintenance_type == MaintenanceType.EMERGENCIAL:
            hours *= 2

        return round(hours, 1)

    def _estimate_cost(
        self,
        hours: float,
        maintenance_type: MaintenanceType,
    ) -> float:
        """Estima custo total."""
        labor_cost = hours * self.DEFAULT_HOURLY_RATE

        # Adicionar margem para materiais
        material_factor = 1.3 if maintenance_type == MaintenanceType.CORRETIVA else 1.1

        return round(labor_cost * material_factor, 2)

    def _calculate_urgency_score(
        self,
        last_maintenance: Optional[date],
        interval: int,
        priority: MaintenancePriority,
    ) -> int:
        """Calcula score de urgência (0-100)."""
        if not last_maintenance:
            return 60  # Sem histórico, urgência média-alta

        days_since = (date.today() - last_maintenance).days
        days_overdue = days_since - interval

        # Base score
        if days_overdue <= 0:
            # Ainda no intervalo
            percentage_used = days_since / interval if interval > 0 else 1
            score = int(percentage_used * 50)
        else:
            # Atrasado
            overdue_percentage = min(days_overdue / interval, 1) if interval > 0 else 1
            score = 50 + int(overdue_percentage * 50)

        # Ajustar por prioridade
        priority_bonus = {
            MaintenancePriority.CRITICAL: 30,
            MaintenancePriority.HIGH: 15,
            MaintenancePriority.MEDIUM: 0,
            MaintenancePriority.LOW: -15,
        }
        score += priority_bonus.get(priority, 0)

        return max(0, min(100, score))

    def _recommend_team_size(
        self,
        equipment_type: str,
        maintenance_type: MaintenanceType,
    ) -> int:
        """Recomenda tamanho da equipe."""
        base_team = {
            "elevadores": 2,
            "geradores": 2,
            "bombas": 2,
            "limpeza_fachada": 4,
            "default": 1,
        }

        size = base_team.get(equipment_type.lower(), base_team["default"])

        if maintenance_type == MaintenanceType.EMERGENCIAL:
            size += 1

        return size

    def _score_date(
        self,
        candidate_date: date,
        ideal_date: Optional[date],
        deadline: Optional[date],
        _priority: str,
    ) -> float:
        """Calcula score de uma data candidata."""
        score = 50.0

        # Proximidade com data ideal
        if ideal_date:
            diff = abs((candidate_date - ideal_date).days)
            score += max(0, 30 - diff * 2)

        # Respeito ao deadline
        if deadline:
            if candidate_date > deadline:
                score -= 50
            else:
                days_before = (deadline - candidate_date).days
                score += min(20, days_before)

        # Evitar segunda-feira (pico de demandas)
        if candidate_date.weekday() == 0:
            score -= 10

        # Preferir meio da semana
        if candidate_date.weekday() in (1, 2, 3):
            score += 5

        return score

    def _generate_reasons(
        self,
        equipment_type: str,
        maintenance_type: MaintenanceType,
        last_maintenance: Optional[date],
        suggested_date: date,
        priority: MaintenancePriority,
    ) -> List[str]:
        """Gera lista de motivos para a sugestão."""
        reasons = []

        if maintenance_type == MaintenanceType.PREVENTIVA:
            reasons.append(f"Manutenção preventiva para {equipment_type}")

        if last_maintenance:
            days_since = (date.today() - last_maintenance).days
            reasons.append(f"Última manutenção há {days_since} dias")
        else:
            reasons.append("Sem registro de manutenção anterior")

        if priority in (MaintenancePriority.CRITICAL, MaintenancePriority.HIGH):
            reasons.append(f"Prioridade {priority.value} - agendamento antecipado")

        days_until = (suggested_date - date.today()).days
        if days_until <= 7:
            reasons.append("Agendamento em até 7 dias recomendado")

        return reasons

    def _generate_prediction_reason(
        self,
        predicted_type: str,
        corretiva_ratio: float,
        equipment_age_days: Optional[int],
        usage_intensity: str,
    ) -> str:
        """Gera explicação para previsão."""
        parts = []

        if predicted_type == MaintenanceType.CORRETIVA.value:
            parts.append(
                f"Histórico indica {int(corretiva_ratio * 100)}% de manutenções corretivas"
            )
        else:
            parts.append("Padrão de manutenção preventiva identificado")

        if equipment_age_days:
            years = equipment_age_days // 365
            if years > 10:
                parts.append(f"Equipamento com {years} anos requer atenção extra")
            elif years > 5:
                parts.append(f"Equipamento com {years} anos em fase de maturidade")

        if usage_intensity == "high":
            parts.append("Uso intensivo reduz intervalo recomendado")
        elif usage_intensity == "low":
            parts.append("Baixo uso permite intervalo estendido")

        return ". ".join(parts)


# Singleton
maintenance_scheduler = MaintenanceSchedulerService()
