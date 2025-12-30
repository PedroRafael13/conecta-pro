"""Service de IA para análise de visitantes."""

import logging
from collections import Counter
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.visitors.models.log import AccessType
from modules.visitors.models.visitor import VisitorType
from modules.visitors.repositories.log_repository import LogRepository
from modules.visitors.repositories.schedule_repository import ScheduleRepository
from modules.visitors.repositories.visitor_repository import VisitorRepository

logger = logging.getLogger(__name__)


class VisitorAIService:
    """Service de IA para análise de padrões de visitantes."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.visitor_repo = VisitorRepository(session)
        self.log_repo = LogRepository(session)
        self.schedule_repo = ScheduleRepository(session)

    async def analyze_visitor_pattern(
        self, visitor_id: str | UUID, days: int = 90
    ) -> dict:
        """Analisa padrões de visita de um visitante."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        visitor = await self.visitor_repo.get_by_id(visitor_id)
        if not visitor:
            return {"error": "Visitante não encontrado"}

        logs = await self.log_repo.get_by_visitor(visitor_id, limit=500)

        # Filtrar por período
        date_from = datetime.utcnow() - timedelta(days=days)
        recent_logs = [
            log for log in logs
            if log.timestamp >= date_from and log.access_type == AccessType.ENTRADA
        ]

        if not recent_logs:
            return {
                "visitor_id": str(visitor_id),
                "visitor_name": visitor.name,
                "pattern": "sem_dados",
                "visits_in_period": 0,
                "insights": ["Sem visitas no período analisado"],
            }

        # Análise por dia da semana
        days_of_week = Counter([log.timestamp.weekday() for log in recent_logs])
        day_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        by_day = {day_names[k]: v for k, v in days_of_week.items()}

        # Análise por hora
        hours = Counter([log.timestamp.hour for log in recent_logs])

        # Análise por unidade
        units = Counter([log.unit_number for log in recent_logs if log.unit_number])

        # Duração média
        durations = [log.duration_minutes for log in recent_logs if log.duration_minutes]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Frequência
        frequency = len(recent_logs) / days * 30  # Visitas por mês

        # Determinar padrão
        pattern = self._determine_pattern(
            frequency, by_day, hours, visitor.visitor_type
        )

        # Insights
        insights = self._generate_insights(
            frequency, by_day, hours, avg_duration, units, visitor.visitor_type
        )

        # Previsão de próxima visita
        next_visit_prediction = self._predict_next_visit(by_day, hours, recent_logs)

        return {
            "visitor_id": str(visitor_id),
            "visitor_name": visitor.name,
            "visitor_type": visitor.visitor_type.value,
            "analysis_period_days": days,
            "visits_in_period": len(recent_logs),
            "pattern": pattern,
            "frequency_per_month": round(frequency, 1),
            "avg_duration_minutes": round(avg_duration, 0),
            "by_day_of_week": by_day,
            "by_hour": dict(sorted(hours.items())),
            "by_unit": dict(units.most_common(5)),
            "insights": insights,
            "next_visit_prediction": next_visit_prediction,
            "risk_level": self._calculate_risk_level(visitor, recent_logs),
        }

    def _determine_pattern(
        self,
        frequency: float,
        by_day: dict,
        by_hour: Counter,
        visitor_type: VisitorType,
    ) -> str:
        """Determina o padrão de visitas."""
        # Ajusta thresholds baseado no tipo de visitante
        threshold_mult = 1.0
        if visitor_type == VisitorType.PRESTADOR:
            threshold_mult = 0.8  # Prestadores são considerados frequentes com menos visitas
        elif visitor_type == VisitorType.ENTREGADOR:
            threshold_mult = 1.5  # Entregadores precisam de mais visitas

        # Analisa consistência de dias/horários
        day_consistency = len(by_day) <= 3  # Visita poucos dias diferentes
        hour_consistency = len(by_hour) <= 4 if by_hour else False

        adjusted_freq = frequency / threshold_mult

        if adjusted_freq >= 20:
            return "muito_frequente"
        if adjusted_freq >= 8:
            if day_consistency and hour_consistency:
                return "frequente_regular"  # Padrão consistente
            return "frequente"
        if adjusted_freq >= 4:
            return "regular"
        if adjusted_freq >= 1:
            return "ocasional"
        return "raro"

    def _generate_insights(
        self,
        frequency: float,
        by_day: dict,
        by_hour: Counter,
        avg_duration: float,
        units: Counter,
        visitor_type: VisitorType,
    ) -> list[str]:
        """Gera insights sobre o visitante."""
        insights = []

        # Frequência
        if frequency >= 20:
            insights.append("Visitante muito frequente - considerar autorização permanente")
        elif frequency >= 8:
            insights.append("Visitante frequente - candidato a cadastro VIP")

        # Dias preferidos
        if by_day:
            preferred_days = sorted(by_day.items(), key=lambda x: x[1], reverse=True)
            if preferred_days[0][1] > sum(by_day.values()) * 0.4:
                insights.append(
                    f"Preferência por {preferred_days[0][0]} "
                    f"({preferred_days[0][1]} visitas)"
                )

        # Horários preferidos
        if by_hour:
            peak_hours = [h for h, c in by_hour.items() if c >= max(by_hour.values()) * 0.7]
            if len(peak_hours) <= 3:
                hours_str = ", ".join([f"{h}h" for h in sorted(peak_hours)])
                insights.append(f"Horários habituais: {hours_str}")

        # Duração
        if avg_duration > 120:
            insights.append("Visitas longas (média > 2h)")
        elif avg_duration < 15:
            insights.append("Visitas rápidas (média < 15min)")

        # Unidades visitadas
        if len(units) == 1:
            insights.append(f"Visita exclusivamente a unidade {list(units.keys())[0]}")
        elif len(units) > 5:
            insights.append("Visita múltiplas unidades - possível prestador")

        # Tipo específico
        if visitor_type == VisitorType.PRESTADOR:
            insights.append("Prestador de serviço - verificar credenciais regularmente")
        elif visitor_type == VisitorType.ENTREGADOR:
            insights.append("Entregador - acesso apenas a áreas comuns")

        return insights

    def _predict_next_visit(
        self, by_day: dict, by_hour: Counter, recent_logs: list
    ) -> dict:
        """Prevê próxima visita."""
        if not recent_logs:
            return {"prediction": "indefinido", "confidence": 0}

        # Dia mais provável
        if by_day:
            day_names = [
                "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"
            ]
            most_likely_day = max(by_day.items(), key=lambda x: x[1])[0]
            day_index = day_names.index(most_likely_day)
        else:
            return {"prediction": "indefinido", "confidence": 0}

        # Hora mais provável
        if by_hour:
            most_likely_hour = max(by_hour.items(), key=lambda x: x[1])[0]
        else:
            most_likely_hour = 10

        # Calcular próxima data
        today = datetime.utcnow()
        days_ahead = day_index - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7

        next_date = today + timedelta(days=days_ahead)
        next_date = next_date.replace(
            hour=most_likely_hour, minute=0, second=0, microsecond=0
        )

        # Confiança baseada na regularidade
        total_visits = sum(by_day.values())
        peak_visits = max(by_day.values())
        confidence = min(100, int((peak_visits / total_visits) * 100 + 20))

        return {
            "prediction": next_date.isoformat(),
            "day": most_likely_day,
            "hour": most_likely_hour,
            "confidence": confidence,
        }

    def _calculate_risk_level(self, visitor, logs: list) -> str:
        """Calcula nível de risco do visitante."""
        risk_score = 0

        # Visitante bloqueado anteriormente
        if visitor.blocked_at:
            risk_score += 30

        # Muitas visitas negadas
        denied_count = sum(1 for log in logs if log.denied)
        if denied_count >= 5:
            risk_score += 25
        elif denied_count >= 2:
            risk_score += 10

        # Visitante temporário sem renovação
        if visitor.valid_until:
            if visitor.valid_until < datetime.utcnow():
                risk_score += 20

        # Tipo de visitante
        if visitor.visitor_type == VisitorType.ENTREGADOR:
            risk_score += 5
        elif visitor.visitor_type == VisitorType.EMERGENCIA:
            risk_score -= 10

        if risk_score >= 50:
            return "alto"
        if risk_score >= 25:
            return "medio"
        return "baixo"

    async def analyze_condominium_trends(
        self, condominium_id: str, days: int = 30
    ) -> dict:
        """Analisa tendências de visitantes do condomínio."""
        date_from = datetime.utcnow() - timedelta(days=days)

        # Buscar logs do período
        logs = await self.log_repo.get_by_date_range(
            condominium_id, date_from, datetime.utcnow()
        )

        if not logs:
            return {
                "condominium_id": condominium_id,
                "period_days": days,
                "total_visits": 0,
                "insights": ["Sem dados no período"],
            }

        # Análises
        entries = [log for log in logs if log.access_type == AccessType.ENTRADA]
        denied = [log for log in logs if log.denied]

        # Por dia da semana
        by_day = Counter([log.timestamp.weekday() for log in entries])
        day_names = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        by_day_named = {day_names[k]: v for k, v in by_day.items()}

        # Por hora
        by_hour = Counter([log.timestamp.hour for log in entries])

        # Por tipo de visitante (através do visitor)
        visitor_types = Counter()
        for log in entries:
            visitor = await self.visitor_repo.get_by_id(log.visitor_id)
            if visitor:
                visitor_types[visitor.visitor_type.value] += 1

        # Picos
        peak_hour = max(by_hour.items(), key=lambda x: x[1])[0] if by_hour else 0
        peak_day = (
            day_names[max(by_day.items(), key=lambda x: x[1])[0]]
            if by_day
            else "N/A"
        )

        # Média diária
        daily_avg = len(entries) / days

        # Taxa de negativa
        denial_rate = len(denied) / len(logs) * 100 if logs else 0

        # Insights
        insights = []

        if daily_avg > 50:
            insights.append("Alto fluxo de visitantes - considerar mais porteiros")
        if denial_rate > 10:
            insights.append(
                f"Taxa de negativa alta ({denial_rate:.1f}%) - "
                "revisar políticas de acesso"
            )
        if peak_hour >= 18:
            insights.append("Pico de visitas no período noturno")
        if visitor_types.get("entregador", 0) > len(entries) * 0.4:
            insights.append("Maioria das visitas são entregas - considerar área de delivery")

        return {
            "condominium_id": condominium_id,
            "period_days": days,
            "total_visits": len(entries),
            "total_denied": len(denied),
            "daily_average": round(daily_avg, 1),
            "denial_rate": round(denial_rate, 2),
            "by_day_of_week": by_day_named,
            "by_hour": dict(sorted(by_hour.items())),
            "by_visitor_type": dict(visitor_types.most_common()),
            "peak_hour": peak_hour,
            "peak_day": peak_day,
            "insights": insights,
        }

    async def suggest_authorization_type(
        self, visitor_id: str | UUID, condominium_id: str
    ) -> dict:
        """Sugere tipo de autorização para visitante."""
        if isinstance(visitor_id, str):
            visitor_id = UUID(visitor_id)

        visitor = await self.visitor_repo.get_by_id(visitor_id)
        if not visitor:
            return {"error": "Visitante não encontrado"}

        logs = await self.log_repo.get_by_visitor(visitor_id, limit=100)
        condo_logs = [log for log in logs if log.condominium_id == condominium_id]

        if not condo_logs:
            return {
                "visitor_id": str(visitor_id),
                "suggested_type": "unica",
                "reason": "Primeira visita ao condomínio",
                "confidence": 100,
            }

        # Análise de frequência
        entries = [log for log in condo_logs if log.access_type == AccessType.ENTRADA]
        last_90_days = [
            log for log in entries
            if log.timestamp >= datetime.utcnow() - timedelta(days=90)
        ]

        frequency = len(last_90_days) / 90 * 30  # Por mês

        # Decisão
        if frequency >= 15:
            return {
                "visitor_id": str(visitor_id),
                "suggested_type": "permanente",
                "reason": f"Alta frequência ({frequency:.0f} visitas/mês)",
                "confidence": 95,
                "recommendation": "Cadastrar como visitante permanente",
            }
        if frequency >= 4:
            return {
                "visitor_id": str(visitor_id),
                "suggested_type": "recorrente",
                "reason": f"Frequência regular ({frequency:.0f} visitas/mês)",
                "confidence": 85,
                "recommendation": "Autorização recorrente semanal",
            }
        if frequency >= 1:
            return {
                "visitor_id": str(visitor_id),
                "suggested_type": "periodo",
                "reason": f"Frequência ocasional ({frequency:.0f} visitas/mês)",
                "confidence": 75,
                "recommendation": "Autorização por período (30 dias)",
            }

        return {
            "visitor_id": str(visitor_id),
            "suggested_type": "unica",
            "reason": "Visitas esporádicas",
            "confidence": 90,
            "recommendation": "Autorização única por visita",
        }

    async def detect_anomalies(
        self, condominium_id: str, hours: int = 24
    ) -> list[dict]:
        """Detecta anomalias nos acessos."""
        date_from = datetime.utcnow() - timedelta(hours=hours)
        logs = await self.log_repo.get_by_date_range(
            condominium_id, date_from, datetime.utcnow()
        )

        anomalies = []

        # Visitante com múltiplas entradas sem saída
        visitor_entries = {}
        for log in logs:
            if log.access_type == AccessType.ENTRADA:
                if log.visitor_id not in visitor_entries:
                    visitor_entries[log.visitor_id] = []
                visitor_entries[log.visitor_id].append(log)

        for visitor_id, entries in visitor_entries.items():
            if len(entries) >= 3:
                anomalies.append({
                    "type": "multiple_entries",
                    "visitor_id": str(visitor_id),
                    "count": len(entries),
                    "severity": "medium",
                    "description": (
                        f"Visitante com {len(entries)} entradas "
                        f"nas últimas {hours}h"
                    ),
                })

        # Acessos em horários incomuns (22h-6h)
        night_entries = [
            log for log in logs
            if log.access_type == AccessType.ENTRADA
            and (log.timestamp.hour >= 22 or log.timestamp.hour < 6)
        ]
        if len(night_entries) > 5:
            anomalies.append({
                "type": "night_access",
                "count": len(night_entries),
                "severity": "low",
                "description": (
                    f"{len(night_entries)} acessos noturnos "
                    f"(22h-6h) nas últimas {hours}h"
                ),
            })

        # Alta taxa de negativas
        denied = [log for log in logs if log.denied]
        if len(denied) >= 5:
            anomalies.append({
                "type": "high_denial_rate",
                "count": len(denied),
                "total": len(logs),
                "rate": round(len(denied) / len(logs) * 100, 1) if logs else 0,
                "severity": "high" if len(denied) >= 10 else "medium",
                "description": f"{len(denied)} acessos negados nas últimas {hours}h",
            })

        # Visitante bloqueado tentando entrar
        for log in denied:
            if log.denial_reason and "bloqueado" in str(log.denial_reason).lower():
                visitor = await self.visitor_repo.get_by_id(log.visitor_id)
                if visitor:
                    anomalies.append({
                        "type": "blocked_visitor_attempt",
                        "visitor_id": str(log.visitor_id),
                        "visitor_name": visitor.name,
                        "timestamp": log.timestamp.isoformat(),
                        "severity": "high",
                        "description": (
                            f"Visitante bloqueado '{visitor.name}' "
                            "tentou acessar"
                        ),
                    })

        return sorted(anomalies, key=lambda x: {
            "high": 0, "medium": 1, "low": 2
        }.get(x["severity"], 3))

    async def get_peak_hours(
        self, condominium_id: str, days: int = 30
    ) -> dict:
        """Retorna horários de pico."""
        date_from = datetime.utcnow() - timedelta(days=days)
        logs = await self.log_repo.get_by_date_range(
            condominium_id, date_from, datetime.utcnow(), AccessType.ENTRADA
        )

        by_hour = Counter([log.timestamp.hour for log in logs])

        if not by_hour:
            return {"peak_hours": [], "recommendations": []}

        avg = sum(by_hour.values()) / len(by_hour)

        peak_hours = [
            {"hour": h, "visits": c, "is_peak": c > avg * 1.5}
            for h, c in sorted(by_hour.items())
        ]

        peaks = [p for p in peak_hours if p["is_peak"]]

        recommendations = []
        if peaks:
            peak_str = ", ".join([f"{p['hour']}h" for p in peaks])
            recommendations.append(f"Horários de pico: {peak_str}")
            recommendations.append("Considerar reforço de portaria nesses horários")

        return {
            "period_days": days,
            "total_entries": len(logs),
            "by_hour": peak_hours,
            "peak_hours": [p["hour"] for p in peaks],
            "recommendations": recommendations,
        }
