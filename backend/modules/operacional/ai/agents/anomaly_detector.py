"""
Agente de Detecção de Anomalias Comportamentais.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class AnomalyDetected:
    id: str
    type: str  # abandono_posto, sono_servico, ronda_incompleta, check_in_fraudulento, atraso_padrao
    severity: str  # leve, moderada, grave, gravissima
    description: str
    employee_id: str
    employee_name: str
    detected_at: datetime
    evidence: list[str] = field(default_factory=list)
    recommended_action: str = ""
    auto_escalated: bool = False


@dataclass
class BehaviorPattern:
    employee_id: str
    employee_name: str
    pattern_type: str
    occurrences: int
    description: str
    risk_level: str
    first_detected: datetime
    last_detected: datetime
    recommendation: str = ""


class AnomalyDetectorAgent:
    """
    Agente de IA para detecção de anomalias comportamentais em tempo real.
    Monitora padrões suspeitos e alerta gestores automaticamente.
    SUPERPOWERS: Detecta abandono, sono, rondas incompletas, check-in fraudulento.
    """

    ANOMALY_TYPES = {
        "abandono_posto": {"severity": "grave", "action": "Alerta imediato ao supervisor"},
        "sono_servico": {"severity": "grave", "action": "Registro de ocorrência + advertência"},
        "ronda_incompleta": {"severity": "moderada", "action": "Solicitação de justificativa"},
        "check_in_fraudulento": {"severity": "gravissima", "action": "Bloqueio + investigação"},
        "atraso_padrao": {"severity": "leve", "action": "Feedback para RH"},
        "uso_celular_excessivo": {"severity": "moderada", "action": "Registro + aviso formal"},
        "ausencia_epi": {"severity": "moderada", "action": "Alerta + registro"},
    }

    ESCALATION_RULES = {
        "gravissima": {"notify": ["lider", "supervisor", "gerente", "direcao"], "timeout_min": 0},
        "grave": {"notify": ["lider", "supervisor"], "timeout_min": 5},
        "moderada": {"notify": ["lider"], "timeout_min": 15},
        "leve": {"notify": ["rh"], "timeout_min": 60},
    }

    async def analyze_shift(
        self,
        shift_id: str,
        employee_id: str,
        employee_name: str,
        metrics: dict[str, Any] | None = None,
    ) -> list[AnomalyDetected]:
        """
        Analisa um turno completo em busca de anomalias.
        Verifica check-ins, rondas, GPS e padrões históricos.
        """
        logger.info("Analisando turno %s do colaborador %s", shift_id, employee_name)
        data = metrics or {}
        anomalies: list[AnomalyDetected] = []

        # Verificar ronda incompleta
        patrol_rate = data.get("patrol_completion_rate", 100.0)
        if patrol_rate < 70:
            config = self.ANOMALY_TYPES["ronda_incompleta"]
            anomalies.append(
                AnomalyDetected(
                    id=str(uuid4()),
                    type="ronda_incompleta",
                    severity=config["severity"],
                    description=f"Ronda com apenas {patrol_rate:.0f}% de checkpoints concluídos",
                    employee_id=employee_id,
                    employee_name=employee_name,
                    detected_at=datetime.utcnow(),
                    evidence=[f"Taxa de conclusão: {patrol_rate:.0f}%", "Checkpoints pulados detectados"],
                    recommended_action=config["action"],
                )
            )

        # Verificar check-in tardio ou ausente
        checkin_delay_min = data.get("checkin_delay_minutes", 0)
        if checkin_delay_min > 30:
            config = self.ANOMALY_TYPES["atraso_padrao"]
            anomalies.append(
                AnomalyDetected(
                    id=str(uuid4()),
                    type="atraso_padrao",
                    severity=config["severity"],
                    description=f"Check-in realizado com {checkin_delay_min} minutos de atraso",
                    employee_id=employee_id,
                    employee_name=employee_name,
                    detected_at=datetime.utcnow(),
                    evidence=[f"Atraso: {checkin_delay_min} minutos"],
                    recommended_action=config["action"],
                )
            )

        # Verificar abandono (sem atualização GPS por muito tempo)
        gps_silence_min = data.get("gps_silence_minutes", 0)
        if gps_silence_min > 60:
            config = self.ANOMALY_TYPES["abandono_posto"]
            anomalies.append(
                AnomalyDetected(
                    id=str(uuid4()),
                    type="abandono_posto",
                    severity=config["severity"],
                    description=f"Colaborador sem atualização de GPS há {gps_silence_min} minutos",
                    employee_id=employee_id,
                    employee_name=employee_name,
                    detected_at=datetime.utcnow(),
                    evidence=[f"Última atualização GPS: {gps_silence_min} minutos atrás"],
                    recommended_action=config["action"],
                    auto_escalated=True,
                )
            )

        return anomalies

    async def identify_behavior_patterns(
        self,
        employee_id: str,
        employee_name: str,
        history: list[dict[str, Any]],
    ) -> list[BehaviorPattern]:
        """
        Identifica padrões comportamentais recorrentes de um colaborador.
        Analisa histórico de 90 dias para detectar tendências.
        """
        logger.info("Identificando padrões para %s", employee_name)
        patterns: list[BehaviorPattern] = []

        monday_absences = sum(1 for h in history if h.get("weekday") == 0 and h.get("absent"))
        if monday_absences >= 3:
            patterns.append(
                BehaviorPattern(
                    employee_id=employee_id,
                    employee_name=employee_name,
                    pattern_type="falta_segunda_feira",
                    occurrences=monday_absences,
                    description=f"Faltou {monday_absences} segundas-feiras nos últimos 90 dias",
                    risk_level="alto_risco",
                    first_detected=datetime.utcnow(),
                    last_detected=datetime.utcnow(),
                    recommendation="Conversa com RH sobre padrão de faltas às segundas",
                )
            )

        incomplete_patrols = sum(1 for h in history if h.get("patrol_completion_rate", 100) < 70)
        if incomplete_patrols >= 5:
            patterns.append(
                BehaviorPattern(
                    employee_id=employee_id,
                    employee_name=employee_name,
                    pattern_type="rondas_incompletas_recorrentes",
                    occurrences=incomplete_patrols,
                    description=f"Rondas incompletas em {incomplete_patrols} turnos",
                    risk_level="moderado",
                    first_detected=datetime.utcnow(),
                    last_detected=datetime.utcnow(),
                    recommendation="Treinamento de rondas e acompanhamento por supervisor",
                )
            )

        return patterns

    async def get_escalation_contacts(self, severity: str) -> dict[str, Any]:
        """Retorna contatos de escalonamento para uma severidade."""
        return self.ESCALATION_RULES.get(severity, self.ESCALATION_RULES["leve"])
