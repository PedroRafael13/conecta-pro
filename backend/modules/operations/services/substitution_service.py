"""
SubstitutionService - Serviço de IA para sugestão de substitutos.

Este serviço implementa algoritmos inteligentes para:
- Sugerir substitutos baseado em múltiplos critérios
- Calcular score de adequação
- Estimar custos de substituição
- Considerar disponibilidade e distância
"""

from datetime import date, time
from typing import Any, Dict, Optional, Tuple

from core.logging import logger
from modules.operations.schemas.substitution import SubstituteSuggestion


class SubstitutionService:
    """
    Serviço inteligente de sugestão de substitutos.

    Implementa algoritmos de IA para encontrar o melhor substituto
    considerando múltiplos fatores.
    """

    # Pesos para cálculo de score
    WEIGHTS = {
        "same_post_experience": 30,  # Experiência no mesmo posto
        "same_shift_type": 15,  # Mesmo tipo de turno
        "availability": 20,  # Disponibilidade
        "distance": 15,  # Proximidade
        "cost": 20,  # Custo (preferir menor)
    }

    def __init__(self) -> None:
        """Inicializa o serviço."""

    def suggest_substitutes(  # pylint: disable=too-many-locals
        self,
        shift_date: date,
        post_id: str,
        shift_start: time,
        shift_end: time,
        available_employees: list[dict[str, Any]],
        post_location: Optional[Tuple[float, float]] = None,
        max_suggestions: int = 5,
        config: Optional[dict[str, Any]] = None,
    ) -> list[SubstituteSuggestion]:
        """
        Sugere substitutos para um turno.

        Args:
            shift_date: Data do turno
            post_id: ID do posto
            shift_start: Hora de início
            shift_end: Hora de fim
            available_employees: Lista de funcionários disponíveis
            post_location: Coordenadas do posto (lat, lon)
            max_suggestions: Máximo de sugestões
            config: Configurações adicionais

        Returns:
            Lista de sugestões ordenadas por score
        """
        logger.info(f"Buscando substitutos para turno {shift_date} " f"no posto {post_id}")

        if not available_employees:
            logger.warning("Nenhum funcionário disponível")
            return []

        suggestions = []
        is_night_shift = shift_start >= time(19, 0) or shift_start < time(6, 0)

        for employee in available_employees:
            try:
                score, reasons = self._calculate_score(
                    employee=employee,
                    post_id=post_id,
                    shift_date=shift_date,
                    is_night_shift=is_night_shift,
                    post_location=post_location,
                    config=config,
                )

                is_overtime = self._check_overtime(
                    employee=employee,
                    shift_date=shift_date,
                )

                estimated_cost = self._estimate_cost(
                    employee=employee,
                    shift_hours=self._calculate_shift_hours(shift_start, shift_end),
                    is_overtime=is_overtime,
                )

                distance_km = None
                if post_location and employee.get("location"):
                    distance_km = self._calculate_distance(
                        post_location,
                        employee["location"],
                    )

                suggestion = SubstituteSuggestion(
                    employee_id=employee["id"],
                    employee_name=employee.get("name", "N/A"),
                    score=score,
                    reasons=reasons,
                    is_overtime=is_overtime,
                    estimated_cost=estimated_cost,
                    distance_km=distance_km,
                    availability=self._get_availability_status(employee, shift_date),
                )
                suggestions.append(suggestion)

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"Erro ao avaliar funcionário {employee.get('id')}: {e}")
                continue

        # Ordenar por score decrescente
        suggestions.sort(key=lambda s: s.score, reverse=True)

        # Limitar quantidade
        suggestions = suggestions[:max_suggestions]

        logger.info(f"Encontradas {len(suggestions)} sugestões de substitutos")
        return suggestions

    def _calculate_score(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self,
        employee: dict[str, Any],
        post_id: str,  # pylint: disable=unused-argument
        shift_date: date,  # pylint: disable=unused-argument
        is_night_shift: bool,
        post_location: Optional[Tuple[float, float]],
        config: Optional[dict[str, Any]],  # pylint: disable=unused-argument
    ) -> Tuple[float, list[str]]:
        """
        Calcula score de adequação do funcionário.

        Returns:
            Tupla (score, lista de motivos)
        """
        score = 0.0
        reasons = []

        # 1. Experiência no mesmo posto (30%)
        posts_worked = employee.get("posts_worked", [])
        if post_id in posts_worked:
            score += self.WEIGHTS["same_post_experience"]
            reasons.append("Experiência no posto")
        else:
            # Pontuação parcial se trabalhou em posto similar
            post_types_worked = employee.get("post_types_worked", [])
            if post_types_worked:
                score += self.WEIGHTS["same_post_experience"] * 0.5
                reasons.append("Experiência em posto similar")

        # 2. Preferência por turno (15%)
        preferred_shifts = employee.get("preferred_shifts", [])
        current_shift_type = "noturno" if is_night_shift else "diurno"

        if current_shift_type in preferred_shifts:
            score += self.WEIGHTS["same_shift_type"]
            reasons.append(f"Preferência por turno {current_shift_type}")
        elif not preferred_shifts:
            # Sem preferência = aceita qualquer turno
            score += self.WEIGHTS["same_shift_type"] * 0.7
            reasons.append("Flexível para qualquer turno")

        # 3. Disponibilidade (20%)
        availability_score = self._evaluate_availability(employee, shift_date)
        score += self.WEIGHTS["availability"] * (availability_score / 100)
        if availability_score >= 80:
            reasons.append("Alta disponibilidade")
        elif availability_score >= 50:
            reasons.append("Disponibilidade média")

        # 4. Distância (15%)
        if post_location and employee.get("location"):
            distance = self._calculate_distance(post_location, employee["location"])
            if distance is not None:
                if distance <= 5:
                    score += self.WEIGHTS["distance"]
                    reasons.append(f"Próximo ({distance:.1f}km)")
                elif distance <= 15:
                    score += self.WEIGHTS["distance"] * 0.7
                    reasons.append(f"Distância razoável ({distance:.1f}km)")
                elif distance <= 30:
                    score += self.WEIGHTS["distance"] * 0.4
                else:
                    score += self.WEIGHTS["distance"] * 0.1
                    reasons.append(f"Distante ({distance:.1f}km)")
        else:
            # Sem localização, assume pontuação média
            score += self.WEIGHTS["distance"] * 0.5

        # 5. Custo (20%) - preferir menor custo
        hourly_rate = employee.get("hourly_rate", 0)
        avg_rate = employee.get("avg_market_rate", hourly_rate)

        if avg_rate > 0:
            cost_ratio = hourly_rate / avg_rate
            if cost_ratio <= 0.9:
                score += self.WEIGHTS["cost"]
                reasons.append("Custo abaixo da média")
            elif cost_ratio <= 1.0:
                score += self.WEIGHTS["cost"] * 0.8
                reasons.append("Custo na média")
            elif cost_ratio <= 1.2:
                score += self.WEIGHTS["cost"] * 0.5
            else:
                score += self.WEIGHTS["cost"] * 0.2
                reasons.append("Custo acima da média")
        else:
            score += self.WEIGHTS["cost"] * 0.5

        # Normalizar score para 0-100
        max_score = sum(self.WEIGHTS.values())
        normalized_score = (score / max_score) * 100

        return round(normalized_score, 1), reasons

    def _evaluate_availability(
        self, employee: dict[str, Any], shift_date: date  # pylint: disable=unused-argument
    ) -> float:
        """Avalia disponibilidade do funcionário."""
        # Verificar se já tem turno no dia
        shifts_on_date = employee.get("shifts_on_date", 0)
        if shifts_on_date >= 1:
            return 20  # Baixa disponibilidade

        # Verificar banco de horas
        time_bank_balance = employee.get("time_bank_balance", 0)
        if time_bank_balance < -10:  # Deve muitas horas
            return 90  # Alta disponibilidade

        # Verificar dias trabalhados na semana
        days_worked_week = employee.get("days_worked_this_week", 0)
        if days_worked_week >= 6:
            return 30
        elif days_worked_week >= 5:
            return 60

        return 80  # Disponibilidade padrão

    def _calculate_distance(
        self,
        location1: Tuple[float, float],
        location2: Tuple[float, float],
    ) -> Optional[float]:
        """
        Calcula distância entre dois pontos em km (fórmula de Haversine).
        """
        import math  # pylint: disable=import-outside-toplevel

        try:
            lat1, lon1 = location1
            lat2, lon2 = location2

            earth_radius = 6371  # Raio da Terra em km

            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)

            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(math.radians(lat1))
                * math.cos(math.radians(lat2))
                * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            return round(earth_radius * c, 2)
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def _calculate_shift_hours(self, start: time, end: time) -> float:
        """Calcula horas do turno."""
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute

        if end_minutes <= start_minutes:
            end_minutes += 24 * 60  # Turno noturno

        return (end_minutes - start_minutes) / 60

    def _check_overtime(
        self, employee: dict[str, Any], shift_date: date  # pylint: disable=unused-argument
    ) -> bool:
        """Verifica se será hora extra."""
        weekly_hours = employee.get("weekly_hours_worked", 0)
        return weekly_hours >= 44  # Limite CLT

    def _estimate_cost(
        self,
        employee: Dict[str, Any],
        shift_hours: float,
        is_overtime: bool,
    ) -> float:
        """Estima custo da substituição."""
        hourly_rate = employee.get("hourly_rate", 0)

        if is_overtime:
            # Hora extra: 50% a mais
            return shift_hours * hourly_rate * 1.5
        return shift_hours * hourly_rate

    def _get_availability_status(
        self, employee: dict[str, Any], shift_date: date  # pylint: disable=unused-argument
    ) -> str:
        """Retorna status de disponibilidade."""
        shifts_on_date = employee.get("shifts_on_date", 0)

        if shifts_on_date == 0:
            return "Totalmente disponível"
        if shifts_on_date == 1:
            return "Parcialmente disponível"
        return "Baixa disponibilidade"

    def calculate_substitution_cost(
        self,
        original_employee_rate: float,
        substitute_employee_rate: float,
        shift_hours: float,
        is_overtime: bool = False,
        is_holiday: bool = False,
        is_sunday: bool = False,
    ) -> Dict[str, float]:
        """
        Calcula custo adicional da substituição.

        Returns:
            Dicionário com breakdown de custos
        """
        # Multiplicadores
        overtime_mult = 1.5 if is_overtime else 1.0
        holiday_mult = 2.0 if is_holiday else 1.0
        sunday_mult = 2.0 if is_sunday and not is_holiday else 1.0

        # Maior multiplicador prevalece
        total_mult = max(overtime_mult, holiday_mult, sunday_mult)

        original_cost = original_employee_rate * shift_hours
        substitute_cost = substitute_employee_rate * shift_hours * total_mult
        additional_cost = substitute_cost - original_cost

        return {
            "original_cost": round(original_cost, 2),
            "substitute_cost": round(substitute_cost, 2),
            "additional_cost": round(max(0, additional_cost), 2),
            "multiplier": total_mult,
            "is_overtime": is_overtime,
            "is_holiday": is_holiday,
            "is_sunday": is_sunday,
        }


# Singleton
substitution_service = SubstitutionService()
