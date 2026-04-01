"""Serviço de detecção de anomalias com IA."""

import logging
import math
from statistics import mean, stdev

from modules.hr.time_tracking.models import (
    AnomalyType,
    EntryType,
    TimeEntry,
    WorkSchedule,
)

logger = logging.getLogger(__name__)


class AnomalyScore:  # pylint: disable=too-few-public-methods  # noqa: B903
    """Representa um score de anomalia."""

    def __init__(
        self,
        anomaly_type: AnomalyType,
        score: float,
        description: str,
        severity: str = "medium",
        auto_resolvable: bool = False,
    ):
        self.anomaly_type = anomaly_type
        self.score = score  # 0-100
        self.description = description
        self.severity = severity  # low, medium, high, critical
        self.auto_resolvable = auto_resolvable


class AnomalyDetectionService:
    """Serviço de detecção de anomalias com técnicas de IA/ML."""

    # Limiares de detecção
    LATE_THRESHOLD_MINUTES = 5  # Tolerância de atraso
    EARLY_THRESHOLD_MINUTES = 5  # Tolerância saída antecipada
    MIN_BREAK_MINUTES = 60  # Intervalo mínimo obrigatório
    MAX_WORK_HOURS = 10  # Máximo de horas diárias
    DUPLICATE_THRESHOLD_MINUTES = 2  # Janela para detectar duplicatas
    LOCATION_THRESHOLD_METERS = 100  # Distância máxima do local

    # Pesos para scoring de risco
    WEIGHTS = {
        "atraso": 0.15,
        "falta_entrada": 0.25,
        "falta_saida": 0.25,
        "excesso_jornada": 0.20,
        "intervalo_irregular": 0.10,
        "localizacao": 0.05,
    }

    def analyze_entries(
        self,
        entries: list[TimeEntry],
        schedule: WorkSchedule = None,
        historical_data: list[TimeEntry] = None,
    ) -> list[AnomalyScore]:
        """Analisa registros e detecta anomalias.

        Args:
            entries: Registros do dia a analisar
            schedule: Jornada de trabalho
            historical_data: Histórico para análise estatística

        Returns:
            Lista de anomalias detectadas
        """
        anomalies = []

        if not entries:
            return anomalies

        # 1. Verifica registros faltantes
        missing_anomalies = self._detect_missing_entries(entries, schedule)
        anomalies.extend(missing_anomalies)

        # 2. Verifica atrasos
        late_anomalies = self._detect_late_entries(entries, schedule)
        anomalies.extend(late_anomalies)

        # 3. Verifica saída antecipada
        early_anomalies = self._detect_early_departure(entries, schedule)
        anomalies.extend(early_anomalies)

        # 4. Verifica jornada excessiva
        overtime_anomalies = self._detect_excessive_work(entries)
        anomalies.extend(overtime_anomalies)

        # 5. Verifica intervalo irregular
        break_anomalies = self._detect_irregular_break(entries)
        anomalies.extend(break_anomalies)

        # 6. Verifica duplicatas
        duplicate_anomalies = self._detect_duplicates(entries)
        anomalies.extend(duplicate_anomalies)

        # 7. Verifica localização (se disponível)
        location_anomalies = self._detect_location_issues(entries, schedule)
        anomalies.extend(location_anomalies)

        # 8. Análise estatística (padrões atípicos)
        if historical_data:
            pattern_anomalies = self._detect_pattern_anomalies(entries, historical_data)
            anomalies.extend(pattern_anomalies)

        return anomalies

    def calculate_risk_score(
        self,
        anomalies: list[AnomalyScore],
    ) -> tuple[float, str]:
        """Calcula score de risco consolidado.

        Returns:
            Tuple: (score 0-100, nível de risco)
        """
        if not anomalies:
            return (0.0, "baixo")

        total_score = sum(a.score for a in anomalies)
        weighted_score = min(100, total_score)

        # Determina nível
        if weighted_score >= 80:
            level = "critico"
        elif weighted_score >= 60:
            level = "alto"
        elif weighted_score >= 40:
            level = "medio"
        else:
            level = "baixo"

        return (weighted_score, level)

    def suggest_resolution(
        self,
        anomaly: AnomalyScore,
    ) -> dict:
        """Sugere resolução para anomalia.

        Returns:
            Dict com sugestão de resolução
        """
        resolutions = {
            AnomalyType.ATRASO: {
                "action": "justificar",
                "message": "Solicitar justificativa para o atraso",
                "requires_approval": True,
            },
            AnomalyType.SAIDA_ANTECIPADA: {
                "action": "justificar",
                "message": "Solicitar justificativa para saída antecipada",
                "requires_approval": True,
            },
            AnomalyType.FALTA_ENTRADA: {
                "action": "registrar_manual",
                "message": "Adicionar registro manual de entrada",
                "requires_approval": True,
            },
            AnomalyType.FALTA_SAIDA: {
                "action": "registrar_manual",
                "message": "Adicionar registro manual de saída",
                "requires_approval": True,
            },
            AnomalyType.REGISTRO_DUPLICADO: {
                "action": "remover_duplicata",
                "message": "Remover registro duplicado",
                "requires_approval": False,
            },
            AnomalyType.EXCESSO_JORNADA: {
                "action": "aprovar_he",
                "message": "Avaliar e aprovar hora extra",
                "requires_approval": True,
            },
            AnomalyType.INTERVALO_IRREGULAR: {
                "action": "justificar",
                "message": "Verificar e justificar intervalo irregular",
                "requires_approval": True,
            },
            AnomalyType.LOCALIZACAO_INVALIDA: {
                "action": "investigar",
                "message": "Investigar registro fora do local permitido",
                "requires_approval": True,
            },
            AnomalyType.HORARIO_INCOMUM: {
                "action": "investigar",
                "message": "Verificar padrão atípico de horário",
                "requires_approval": False,
            },
        }

        return resolutions.get(
            anomaly.anomaly_type,
            {
                "action": "verificar",
                "message": "Verificar anomalia manualmente",
                "requires_approval": True,
            },
        )

    def _detect_missing_entries(
        self,
        entries: list[TimeEntry],
        schedule: WorkSchedule = None,
    ) -> list[AnomalyScore]:
        """Detecta registros faltantes."""
        anomalies = []

        entry_types = [e.entry_type for e in entries]

        # Verifica entrada
        if EntryType.ENTRADA not in entry_types:
            anomalies.append(
                AnomalyScore(
                    anomaly_type=AnomalyType.FALTA_ENTRADA,
                    score=80.0,
                    description="Registro de entrada não encontrado",
                    severity="high",
                )
            )

        # Verifica saída
        if EntryType.SAIDA not in entry_types:
            anomalies.append(
                AnomalyScore(
                    anomaly_type=AnomalyType.FALTA_SAIDA,
                    score=80.0,
                    description="Registro de saída não encontrado",
                    severity="high",
                )
            )

        # Verifica intervalo (se jornada > 6h)
        if schedule:
            day_schedule = schedule.get_schedule_for_day(entries[0].entry_date)
            if day_schedule and day_schedule.get("daily_minutes", 0) > 360:
                if EntryType.SAIDA_INTERVALO not in entry_types:
                    anomalies.append(
                        AnomalyScore(
                            anomaly_type=AnomalyType.INTERVALO_IRREGULAR,
                            score=40.0,
                            description="Saída para intervalo não registrada",
                            severity="medium",
                        )
                    )
                if EntryType.RETORNO_INTERVALO not in entry_types:
                    anomalies.append(
                        AnomalyScore(
                            anomaly_type=AnomalyType.INTERVALO_IRREGULAR,
                            score=40.0,
                            description="Retorno de intervalo não registrado",
                            severity="medium",
                        )
                    )

        return anomalies

    def _detect_late_entries(
        self,
        entries: list[TimeEntry],
        schedule: WorkSchedule = None,
    ) -> list[AnomalyScore]:
        """Detecta atrasos na entrada."""
        anomalies = []

        if not schedule:
            return anomalies

        clock_ins = [e for e in entries if e.entry_type == EntryType.ENTRADA]
        if not clock_ins:
            return anomalies

        first_in = min(clock_ins, key=lambda e: e.entry_time)
        day_schedule = schedule.get_schedule_for_day(first_in.entry_date)

        if not day_schedule or not day_schedule.get("start_time"):
            return anomalies

        expected_start = day_schedule["start_time"]
        tolerance = schedule.tolerance_late_minutes or self.LATE_THRESHOLD_MINUTES

        actual_minutes = first_in.entry_time.hour * 60 + first_in.entry_time.minute
        expected_minutes = expected_start.hour * 60 + expected_start.minute

        late_minutes = actual_minutes - expected_minutes

        if late_minutes > tolerance:
            severity = "low" if late_minutes <= 15 else "medium" if late_minutes <= 60 else "high"
            score = min(60, 20 + late_minutes * 0.5)

            anomalies.append(
                AnomalyScore(
                    anomaly_type=AnomalyType.ATRASO,
                    score=score,
                    description=f"Atraso de {late_minutes} minutos na entrada",
                    severity=severity,
                )
            )

        return anomalies

    def _detect_early_departure(
        self,
        entries: list[TimeEntry],
        schedule: WorkSchedule = None,
    ) -> list[AnomalyScore]:
        """Detecta saída antecipada."""
        anomalies = []

        if not schedule:
            return anomalies

        clock_outs = [e for e in entries if e.entry_type == EntryType.SAIDA]
        if not clock_outs:
            return anomalies

        last_out = max(clock_outs, key=lambda e: e.entry_time)
        day_schedule = schedule.get_schedule_for_day(last_out.entry_date)

        if not day_schedule or not day_schedule.get("end_time"):
            return anomalies

        expected_end = day_schedule["end_time"]
        tolerance = schedule.tolerance_early_minutes or self.EARLY_THRESHOLD_MINUTES

        actual_minutes = last_out.entry_time.hour * 60 + last_out.entry_time.minute
        expected_minutes = expected_end.hour * 60 + expected_end.minute

        early_minutes = expected_minutes - actual_minutes

        if early_minutes > tolerance:
            severity = "low" if early_minutes <= 15 else "medium" if early_minutes <= 60 else "high"
            score = min(50, 15 + early_minutes * 0.4)

            anomalies.append(
                AnomalyScore(
                    anomaly_type=AnomalyType.SAIDA_ANTECIPADA,
                    score=score,
                    description=f"Saída {early_minutes} minutos antes do previsto",
                    severity=severity,
                )
            )

        return anomalies

    def _detect_excessive_work(
        self,
        entries: list[TimeEntry],
    ) -> list[AnomalyScore]:
        """Detecta jornada excessiva."""
        anomalies = []

        clock_ins = [e for e in entries if e.entry_type == EntryType.ENTRADA]
        clock_outs = [e for e in entries if e.entry_type == EntryType.SAIDA]

        if not clock_ins or not clock_outs:
            return anomalies

        first_in = min(clock_ins, key=lambda e: e.entry_time)
        last_out = max(clock_outs, key=lambda e: e.entry_time)

        start_minutes = first_in.entry_time.hour * 60 + first_in.entry_time.minute
        end_minutes = last_out.entry_time.hour * 60 + last_out.entry_time.minute

        if end_minutes < start_minutes:
            end_minutes += 24 * 60

        worked_minutes = end_minutes - start_minutes
        worked_hours = worked_minutes / 60

        if worked_hours > self.MAX_WORK_HOURS:
            excess_hours = worked_hours - self.MAX_WORK_HOURS
            if excess_hours <= 2:
                severity = "medium"
            elif excess_hours <= 4:
                severity = "high"
            else:
                severity = "critical"
            score = min(90, 50 + excess_hours * 10)

            description = f"Jornada de {worked_hours:.1f}h excede limite de {self.MAX_WORK_HOURS}h"
            anomalies.append(
                AnomalyScore(
                    anomaly_type=AnomalyType.EXCESSO_JORNADA,
                    score=score,
                    description=description,
                    severity=severity,
                )
            )

        return anomalies

    def _detect_irregular_break(  # pylint: disable=too-many-locals
        self,
        entries: list[TimeEntry],
    ) -> list[AnomalyScore]:
        """Detecta intervalo irregular."""
        anomalies = []

        break_outs = [e for e in entries if e.entry_type == EntryType.SAIDA_INTERVALO]
        break_ins = [e for e in entries if e.entry_type == EntryType.RETORNO_INTERVALO]

        # Calcula tempo total de trabalho
        clock_ins = [e for e in entries if e.entry_type == EntryType.ENTRADA]
        clock_outs = [e for e in entries if e.entry_type == EntryType.SAIDA]

        if clock_ins and clock_outs:
            first_in = min(clock_ins, key=lambda e: e.entry_time)
            last_out = max(clock_outs, key=lambda e: e.entry_time)

            start_minutes = first_in.entry_time.hour * 60 + first_in.entry_time.minute
            end_minutes = last_out.entry_time.hour * 60 + last_out.entry_time.minute

            if end_minutes < start_minutes:
                end_minutes += 24 * 60

            worked_minutes = end_minutes - start_minutes

            # Se jornada > 6h, deve ter intervalo mínimo de 1h
            if worked_minutes > 360:  # 6 horas
                if not break_outs or not break_ins:
                    anomalies.append(
                        AnomalyScore(
                            anomaly_type=AnomalyType.INTERVALO_IRREGULAR,
                            score=50.0,
                            description="Jornada > 6h sem intervalo registrado",
                            severity="high",
                        )
                    )
                else:
                    # Calcula duração do intervalo
                    break_start = min(break_outs, key=lambda e: e.entry_time)
                    break_end = max(break_ins, key=lambda e: e.entry_time)

                    b_start = break_start.entry_time.hour * 60 + break_start.entry_time.minute
                    b_end = break_end.entry_time.hour * 60 + break_end.entry_time.minute
                    break_duration = b_end - b_start

                    if break_duration < self.MIN_BREAK_MINUTES:
                        desc = f"Intervalo de {break_duration}min abaixo do mínimo ({self.MIN_BREAK_MINUTES}min)"
                        anomalies.append(
                            AnomalyScore(
                                anomaly_type=AnomalyType.INTERVALO_IRREGULAR,
                                score=35.0,
                                description=desc,
                                severity="medium",
                            )
                        )

        return anomalies

    def _detect_duplicates(
        self,
        entries: list[TimeEntry],
    ) -> list[AnomalyScore]:
        """Detecta registros duplicados."""
        anomalies = []
        entries_sorted = sorted(entries, key=lambda e: (e.entry_type, e.entry_time))

        for i in range(len(entries_sorted) - 1):
            curr = entries_sorted[i]
            next_entry = entries_sorted[i + 1]

            if curr.entry_type == next_entry.entry_type:
                curr_minutes = curr.entry_time.hour * 60 + curr.entry_time.minute
                next_minutes = next_entry.entry_time.hour * 60 + next_entry.entry_time.minute

                diff = abs(next_minutes - curr_minutes)

                if diff <= self.DUPLICATE_THRESHOLD_MINUTES:
                    anomalies.append(
                        AnomalyScore(
                            anomaly_type=AnomalyType.REGISTRO_DUPLICADO,
                            score=30.0,
                            description=f"Registro duplicado de {curr.entry_type.value}",
                            severity="low",
                            auto_resolvable=True,
                        )
                    )

        return anomalies

    def _detect_location_issues(
        self,
        entries: list[TimeEntry],
        schedule: WorkSchedule = None,
    ) -> list[AnomalyScore]:
        """Detecta problemas de localização."""
        anomalies = []

        if not schedule or not schedule.allowed_locations:
            return anomalies

        for entry in entries:
            if not entry.latitude or not entry.longitude:
                continue

            is_valid = False
            for location in schedule.allowed_locations:
                loc_lat = location.get("latitude")
                loc_lng = location.get("longitude")
                loc_radius = location.get("radius", self.LOCATION_THRESHOLD_METERS)

                if loc_lat and loc_lng:
                    distance = self._haversine_distance(entry.latitude, entry.longitude, loc_lat, loc_lng)
                    if distance <= loc_radius:
                        is_valid = True
                        break

            if not is_valid:
                anomalies.append(
                    AnomalyScore(
                        anomaly_type=AnomalyType.LOCALIZACAO_INVALIDA,
                        score=60.0,
                        description="Registro fora do local de trabalho permitido",
                        severity="high",
                    )
                )
                break  # Uma anomalia por dia é suficiente

        return anomalies

    def _detect_pattern_anomalies(  # pylint: disable=too-many-locals
        self,
        entries: list[TimeEntry],
        historical_data: list[TimeEntry],
    ) -> list[AnomalyScore]:
        """Detecta padrões atípicos usando análise estatística."""
        anomalies = []

        if len(historical_data) < 10:
            return anomalies

        # Agrupa histórico por dia
        historical_by_day = {}
        for entry in historical_data:
            if entry.entry_type == EntryType.ENTRADA:
                day_key = entry.entry_date.isoformat()
                if day_key not in historical_by_day:
                    historical_by_day[day_key] = []
                historical_by_day[day_key].append(entry.entry_time)

        # Calcula média e desvio padrão dos horários de entrada
        entry_times = []
        for day_entries in historical_by_day.values():
            if day_entries:
                first = min(day_entries)
                entry_times.append(first.hour * 60 + first.minute)

        if len(entry_times) < 5:
            return anomalies

        avg_entry = mean(entry_times)
        std_entry = stdev(entry_times) if len(entry_times) > 1 else 0

        # Verifica entrada atual
        current_ins = [e for e in entries if e.entry_type == EntryType.ENTRADA]
        if current_ins:
            first_in = min(current_ins, key=lambda e: e.entry_time)
            current_minutes = first_in.entry_time.hour * 60 + first_in.entry_time.minute

            # Z-score
            if std_entry > 0:
                z_score = abs(current_minutes - avg_entry) / std_entry

                if z_score > 3:  # Mais de 3 desvios padrão
                    anomalies.append(
                        AnomalyScore(
                            anomaly_type=AnomalyType.HORARIO_INCOMUM,
                            score=25.0,
                            description=f"Horário de entrada atípico (z-score: {z_score:.2f})",
                            severity="low",
                        )
                    )

        return anomalies

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calcula distância entre dois pontos usando Haversine."""
        earth_radius = 6371000  # Raio da Terra em metros

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return earth_radius * c
