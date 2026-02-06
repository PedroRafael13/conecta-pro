"""
Analisador de Ocorrências com IA.

Analisa ocorrências para identificar padrões, priorizar atendimento
e sugerir ações.
"""

import logging
from typing import List
from datetime import datetime

from modules.campo.models.guardian_occurrence import (
    OccurrenceSeverity,
    OccurrenceType,
)

logger = logging.getLogger(__name__)


class OccurrenceAnalyzer:
    """
    Analisador de ocorrências com inteligência artificial.

    Responsável por:
    - Classificar e priorizar ocorrências
    - Identificar padrões de incidentes
    - Sugerir ações e escalações
    - Calcular métricas de SLA
    """

    def __init__(self) -> None:
        """Inicializa o analisador."""
        self._initialized = True
        self._severity_weights = {
            OccurrenceSeverity.CRITICAL.value: 4,
            OccurrenceSeverity.HIGH.value: 3,
            OccurrenceSeverity.MEDIUM.value: 2,
            OccurrenceSeverity.LOW.value: 1,
        }
        self._type_base_severity = {
            OccurrenceType.FIRE.value: OccurrenceSeverity.CRITICAL.value,
            OccurrenceType.INTRUSION.value: OccurrenceSeverity.CRITICAL.value,
            OccurrenceType.PANIC.value: OccurrenceSeverity.CRITICAL.value,
            OccurrenceType.MEDICAL.value: OccurrenceSeverity.HIGH.value,
            OccurrenceType.THEFT.value: OccurrenceSeverity.HIGH.value,
            OccurrenceType.ALARM.value: OccurrenceSeverity.HIGH.value,
            OccurrenceType.VANDALISM.value: OccurrenceSeverity.MEDIUM.value,
            OccurrenceType.SUSPICIOUS_ACTIVITY.value: OccurrenceSeverity.MEDIUM.value,
            OccurrenceType.EQUIPMENT_FAILURE.value: OccurrenceSeverity.MEDIUM.value,
            OccurrenceType.POWER_OUTAGE.value: OccurrenceSeverity.MEDIUM.value,
            OccurrenceType.VISITOR_INCIDENT.value: OccurrenceSeverity.LOW.value,
            OccurrenceType.VEHICLE_INCIDENT.value: OccurrenceSeverity.LOW.value,
            OccurrenceType.INTERCOM_EMERGENCY.value: OccurrenceSeverity.MEDIUM.value,
            OccurrenceType.OTHER.value: OccurrenceSeverity.LOW.value,
        }

    def classify_occurrence(  # pylint: disable=too-many-locals
        self,
        title: str,
        description: str,
    ) -> dict:
        """
        Classifica uma ocorrência com base no título e descrição.

        Args:
            title: Título da ocorrência
            description: Descrição detalhada

        Returns:
            Classificação sugerida com tipo e gravidade
        """
        text = f"{title} {description}".lower()

        # Palavras-chave para cada tipo
        keywords = {
            OccurrenceType.FIRE.value: [
                "incêndio",
                "fogo",
                "fumaça",
                "chamas",
                "queimando",
            ],
            OccurrenceType.INTRUSION.value: [
                "invasão",
                "intruso",
                "invadido",
                "arrombamento",
                "pulou muro",
            ],
            OccurrenceType.PANIC.value: [
                "pânico",
                "socorro",
                "ajuda",
                "emergência",
                "perigo",
            ],
            OccurrenceType.MEDICAL.value: [
                "médica",
                "ambulância",
                "samu",
                "desmaio",
                "mal",
                "passou mal",
                "acidente",
            ],
            OccurrenceType.THEFT.value: [
                "furto",
                "roubo",
                "assalto",
                "roubado",
                "furtado",
                "ladrão",
            ],
            OccurrenceType.ALARM.value: [
                "alarme",
                "disparou",
                "sensor",
                "acionou",
            ],
            OccurrenceType.VANDALISM.value: [
                "vandalismo",
                "depredação",
                "pichação",
                "quebrado",
                "danificado",
            ],
            OccurrenceType.SUSPICIOUS_ACTIVITY.value: [
                "suspeito",
                "estranho",
                "comportamento",
                "rondando",
                "vigiando",
            ],
            OccurrenceType.EQUIPMENT_FAILURE.value: [
                "equipamento",
                "defeito",
                "não funciona",
                "parou",
                "quebrou",
                "falha",
            ],
            OccurrenceType.POWER_OUTAGE.value: [
                "energia",
                "luz",
                "apagão",
                "falta de luz",
                "queda de energia",
            ],
        }

        # Encontrar tipo com mais correspondências
        best_type = OccurrenceType.OTHER.value
        max_matches = 0

        for occ_type, words in keywords.items():
            matches = sum(1 for word in words if word in text)
            if matches > max_matches:
                max_matches = matches
                best_type = occ_type

        # Determinar gravidade base pelo tipo
        base_severity = self._type_base_severity.get(
            best_type,
            OccurrenceSeverity.LOW.value,
        )

        # Ajustar gravidade por palavras de urgência
        urgency_words = [
            "urgente",
            "imediato",
            "grave",
            "crítico",
            "perigo",
            "risco",
        ]
        has_urgency = any(word in text for word in urgency_words)

        if has_urgency and base_severity != OccurrenceSeverity.CRITICAL.value:
            # Aumentar um nível de gravidade
            severity_order = [
                OccurrenceSeverity.LOW.value,
                OccurrenceSeverity.MEDIUM.value,
                OccurrenceSeverity.HIGH.value,
                OccurrenceSeverity.CRITICAL.value,
            ]
            current_index = severity_order.index(base_severity)
            base_severity = severity_order[min(current_index + 1, 3)]

        confidence = min(0.95, 0.5 + (max_matches * 0.15))

        return {
            "suggested_type": best_type,
            "suggested_severity": base_severity,
            "confidence": round(confidence, 2),
            "keywords_matched": max_matches,
            "has_urgency_indicators": has_urgency,
        }

    def calculate_priority_score(
        self,
        occurrence_type: str,
        severity: str,
        event_timestamp: datetime,
        is_recurring: bool = False,
        affected_people_count: int = 0,
    ) -> dict:
        """
        Calcula score de prioridade para ordenação de atendimento.

        Args:
            occurrence_type: Tipo da ocorrência
            severity: Gravidade
            event_timestamp: Data/hora do evento
            is_recurring: Se é recorrente
            affected_people_count: Número de pessoas afetadas

        Returns:
            Score de prioridade e fatores
        """
        # Score base pela gravidade (0-40 pontos)
        severity_score = self._severity_weights.get(severity, 1) * 10

        # Score por tipo crítico (0-20 pontos)
        critical_types = [
            OccurrenceType.FIRE.value,
            OccurrenceType.INTRUSION.value,
            OccurrenceType.PANIC.value,
            OccurrenceType.MEDICAL.value,
        ]
        type_score = 20 if occurrence_type in critical_types else 0

        # Score por tempo decorrido (0-20 pontos)
        # Ocorrências mais antigas são mais urgentes
        elapsed = datetime.utcnow() - event_timestamp
        elapsed_minutes = elapsed.total_seconds() / 60

        if elapsed_minutes < 5:
            time_score = 20
        elif elapsed_minutes < 15:
            time_score = 15
        elif elapsed_minutes < 30:
            time_score = 10
        elif elapsed_minutes < 60:
            time_score = 5
        else:
            time_score = 0

        # Bonus por recorrência (0-10 pontos)
        recurrence_score = 10 if is_recurring else 0

        # Bonus por pessoas afetadas (0-10 pontos)
        people_score = min(10, affected_people_count * 2)

        total_score = (
            severity_score
            + type_score
            + time_score
            + recurrence_score
            + people_score
        )

        return {
            "total_score": total_score,
            "max_score": 100,
            "severity_score": severity_score,
            "type_score": type_score,
            "time_score": time_score,
            "recurrence_score": recurrence_score,
            "people_score": people_score,
            "priority_level": self._get_priority_level(total_score),
        }

    def _get_priority_level(self, score: int) -> str:
        """Determina nível de prioridade pelo score."""
        if score >= 80:
            return "immediate"
        if score >= 60:
            return "high"
        if score >= 40:
            return "medium"
        return "low"

    def suggest_actions(
        self,
        occurrence_type: str,
        severity: str,
        _location: str | None = None,
    ) -> List[dict]:
        """
        Sugere ações para uma ocorrência.

        Args:
            occurrence_type: Tipo da ocorrência
            severity: Gravidade
            _location: Localização

        Returns:
            Lista de ações sugeridas
        """
        actions = []

        # Ações por tipo
        type_actions = {
            OccurrenceType.FIRE.value: [
                {"action": "Acionar Corpo de Bombeiros", "priority": 1},
                {"action": "Evacuar área afetada", "priority": 2},
                {"action": "Cortar energia elétrica", "priority": 3},
                {"action": "Isolar área", "priority": 4},
            ],
            OccurrenceType.INTRUSION.value: [
                {"action": "Acionar Polícia", "priority": 1},
                {"action": "Verificar câmeras de segurança", "priority": 2},
                {"action": "Bloquear pontos de saída", "priority": 3},
                {"action": "Alertar moradores", "priority": 4},
            ],
            OccurrenceType.MEDICAL.value: [
                {"action": "Acionar SAMU/Ambulância", "priority": 1},
                {"action": "Prestar primeiros socorros", "priority": 2},
                {"action": "Liberar acesso para ambulância", "priority": 3},
                {"action": "Contatar familiares", "priority": 4},
            ],
            OccurrenceType.PANIC.value: [
                {"action": "Verificar situação no local", "priority": 1},
                {"action": "Acionar serviços de emergência", "priority": 2},
                {"action": "Tranquilizar pessoa", "priority": 3},
            ],
            OccurrenceType.THEFT.value: [
                {"action": "Registrar Boletim de Ocorrência", "priority": 1},
                {"action": "Preservar local para perícia", "priority": 2},
                {"action": "Coletar imagens das câmeras", "priority": 3},
                {"action": "Identificar testemunhas", "priority": 4},
            ],
            OccurrenceType.ALARM.value: [
                {"action": "Verificar causa do alarme", "priority": 1},
                {"action": "Inspecionar área do sensor", "priority": 2},
                {"action": "Desativar alarme se falso", "priority": 3},
            ],
            OccurrenceType.EQUIPMENT_FAILURE.value: [
                {"action": "Registrar chamado técnico", "priority": 1},
                {"action": "Ativar equipamento backup", "priority": 2},
                {"action": "Notificar responsável técnico", "priority": 3},
            ],
            OccurrenceType.POWER_OUTAGE.value: [
                {"action": "Verificar disjuntores", "priority": 1},
                {"action": "Acionar gerador backup", "priority": 2},
                {"action": "Contatar concessionária", "priority": 3},
            ],
        }

        # Adicionar ações específicas do tipo
        if occurrence_type in type_actions:
            actions.extend(type_actions[occurrence_type])

        # Ações adicionais por gravidade
        if severity in (
            OccurrenceSeverity.CRITICAL.value,
            OccurrenceSeverity.HIGH.value,
        ):
            actions.append({
                "action": "Notificar supervisor imediatamente",
                "priority": 0,
            })
            actions.append({
                "action": "Documentar com fotos/vídeos",
                "priority": 5,
            })

        # Ordenar por prioridade
        actions.sort(key=lambda x: x.get("priority", 99))

        return actions

    def suggest_escalation(
        self,
        occurrence_type: str,
        severity: str,
        elapsed_minutes: int,
        is_resolved: bool = False,
    ) -> dict:
        """
        Sugere escalação baseada em regras de SLA.

        Args:
            occurrence_type: Tipo da ocorrência
            severity: Gravidade
            elapsed_minutes: Minutos desde o evento
            is_resolved: Se já foi resolvida

        Returns:
            Recomendação de escalação
        """
        if is_resolved:
            return {
                "should_escalate": False,
                "reason": "Ocorrência já resolvida",
            }

        # Limites de tempo por gravidade (em minutos)
        sla_limits = {
            OccurrenceSeverity.CRITICAL.value: {
                "acknowledge": 5,
                "first_response": 15,
                "resolution": 60,
            },
            OccurrenceSeverity.HIGH.value: {
                "acknowledge": 15,
                "first_response": 30,
                "resolution": 120,
            },
            OccurrenceSeverity.MEDIUM.value: {
                "acknowledge": 30,
                "first_response": 60,
                "resolution": 240,
            },
            OccurrenceSeverity.LOW.value: {
                "acknowledge": 60,
                "first_response": 120,
                "resolution": 480,
            },
        }

        limits = sla_limits.get(
            severity,
            sla_limits[OccurrenceSeverity.MEDIUM.value],
        )

        # Verificar violações de SLA
        escalation_path = []

        if elapsed_minutes > limits["acknowledge"]:
            escalation_path.append({
                "level": "Supervisor",
                "reason": "Tempo de reconhecimento excedido",
                "sla_limit": limits["acknowledge"],
                "elapsed": elapsed_minutes,
            })

        if elapsed_minutes > limits["first_response"]:
            escalation_path.append({
                "level": "Gerente Operacional",
                "reason": "Tempo de primeira resposta excedido",
                "sla_limit": limits["first_response"],
                "elapsed": elapsed_minutes,
            })

        if elapsed_minutes > limits["resolution"]:
            escalation_path.append({
                "level": "Diretoria",
                "reason": "Tempo de resolução excedido",
                "sla_limit": limits["resolution"],
                "elapsed": elapsed_minutes,
            })

        return {
            "should_escalate": len(escalation_path) > 0,
            "escalation_path": escalation_path,
            "current_sla_status": "violated" if escalation_path else "within_limits",
            "severity": severity,
            "occurrence_type": occurrence_type,
        }

    def detect_patterns(
        self,
        occurrences: List[dict],
        time_window_hours: int = 24,
    ) -> dict:
        """
        Detecta padrões em um conjunto de ocorrências.

        Args:
            occurrences: Lista de ocorrências
            time_window_hours: Janela de tempo para análise

        Returns:
            Padrões identificados
        """
        if not occurrences:
            return {
                "patterns_found": False,
                "message": "Sem ocorrências para análise",
            }

        patterns = {
            "recurring_types": {},
            "recurring_locations": {},
            "time_patterns": {},
            "severity_trend": [],
        }

        # Contar por tipo
        for occ in occurrences:
            occ_type = occ.get("occurrence_type", "unknown")
            patterns["recurring_types"][occ_type] = (
                patterns["recurring_types"].get(occ_type, 0) + 1
            )

            location = occ.get("location", "unknown")
            patterns["recurring_locations"][location] = (
                patterns["recurring_locations"].get(location, 0) + 1
            )

        # Identificar tipos recorrentes
        recurring = [
            t for t, count in patterns["recurring_types"].items() if count >= 3
        ]

        # Identificar locais problemáticos
        hot_spots = [
            loc for loc, count in patterns["recurring_locations"].items()
            if count >= 3 and loc != "unknown"
        ]

        return {
            "patterns_found": len(recurring) > 0 or len(hot_spots) > 0,
            "recurring_types": recurring,
            "hot_spots": hot_spots,
            "type_distribution": patterns["recurring_types"],
            "location_distribution": patterns["recurring_locations"],
            "time_window_hours": time_window_hours,
            "total_analyzed": len(occurrences),
            "recommendations": self._generate_pattern_recommendations(
                recurring,
                hot_spots,
            ),
        }

    def _generate_pattern_recommendations(
        self,
        recurring_types: List[str],
        hot_spots: List[str],
    ) -> List[str]:
        """Gera recomendações baseadas nos padrões encontrados."""
        recommendations = []

        if OccurrenceType.ALARM.value in recurring_types:
            recommendations.append(
                "Verificar calibração dos sensores de alarme"
            )

        if OccurrenceType.EQUIPMENT_FAILURE.value in recurring_types:
            recommendations.append(
                "Agendar manutenção preventiva nos equipamentos"
            )

        if OccurrenceType.SUSPICIOUS_ACTIVITY.value in recurring_types:
            recommendations.append(
                "Aumentar rondas de vigilância nas áreas afetadas"
            )

        if hot_spots:
            recommendations.append(
                f"Revisar iluminação e câmeras nos locais: {', '.join(hot_spots)}"
            )

        return recommendations


# Instância singleton
occurrence_analyzer = OccurrenceAnalyzer()
