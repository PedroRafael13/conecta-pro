"""
HR AI Service - RH Preditivo
============================
Sistema de IA para previsão de rotatividade e retenção de talentos.
Target: Reter talentos através de análise preditiva.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ChurnRisk(Enum):
    """Níveis de risco de rotatividade."""

    MUITO_BAIXO = "muito_baixo"
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class RetentionStrategy(Enum):
    """Estratégias de retenção."""

    DESENVOLVIMENTO_CARREIRA = "desenvolvimento_carreira"
    MELHORIA_SALARIO = "melhoria_salario"
    FLEXIBILIDADE = "flexibilidade"
    RECONHECIMENTO = "reconhecimento"
    CLIMA_ORGANIZACIONAL = "clima_organizacional"
    BENEFICIOS = "beneficios"


@dataclass
class ChurnPrediction:
    """Resultado da previsão de rotatividade."""

    employee_id: str
    churn_risk: ChurnRisk
    churn_probability: float  # 0-1
    time_to_churn_days: int | None
    key_risk_factors: list[str]
    retention_strategies: list[RetentionStrategy]
    confidence: float
    prediction_date: datetime


@dataclass
class EmployeeProfile:
    """Perfil do funcionário para análise."""

    employee_id: str
    job_satisfaction: float
    salary_percentile: float
    tenure_months: int
    last_performance_rating: float
    manager_satisfaction: float
    work_life_balance: float
    promotions_received: int
    internal_applications: int
    absences_per_month: float


class HRAIService:
    """Serviço de IA para RH Preditivo."""

    def __init__(self):
        """Inicializa o serviço de IA de RH."""
        self._churn_cache: dict[str, ChurnPrediction] = {}
        logger.info("HR AI Service inicializado")

    async def predict_employee_churn(self, profile: EmployeeProfile) -> ChurnPrediction:
        """Prediz probabilidade de rotatividade de um funcionário."""
        try:
            logger.info(f"Predizendo churn: {profile.employee_id}")

            # Cache check
            cache_key = f"{profile.employee_id}_{datetime.now().date()}"
            if cache_key in self._churn_cache:
                return self._churn_cache[cache_key]

            # Calcular probabilidade baseada em regras
            probability = self._calculate_churn_probability(profile)
            risk_level = self._determine_churn_risk(probability)

            # Identificar fatores de risco
            risk_factors = self._identify_risk_factors(profile)

            # Gerar estratégias
            strategies = self._generate_retention_strategies(profile, risk_factors)

            # Estimar tempo
            time_to_churn = self._estimate_time_to_churn(profile, probability)

            prediction = ChurnPrediction(
                employee_id=profile.employee_id,
                churn_risk=risk_level,
                churn_probability=probability,
                time_to_churn_days=time_to_churn,
                key_risk_factors=risk_factors,
                retention_strategies=strategies,
                confidence=0.8,
                prediction_date=datetime.now(),
            )

            self._churn_cache[cache_key] = prediction
            return prediction

        except Exception as e:
            logger.error(f"Erro na predição: {e}")
            return ChurnPrediction(
                employee_id=profile.employee_id,
                churn_risk=ChurnRisk.MEDIO,
                churn_probability=0.5,
                time_to_churn_days=None,
                key_risk_factors=["Análise inconclusiva"],
                retention_strategies=[RetentionStrategy.CLIMA_ORGANIZACIONAL],
                confidence=0.3,
                prediction_date=datetime.now(),
            )

    def _calculate_churn_probability(self, profile: EmployeeProfile) -> float:
        """Calcula probabilidade usando regras de negócio."""
        probability = 0.3  # Base

        # Fatores de aumento
        if profile.job_satisfaction < 5:
            probability += 0.3
        elif profile.job_satisfaction < 6:
            probability += 0.2

        if profile.salary_percentile < 40:
            probability += 0.25

        if profile.tenure_months > 24 and profile.promotions_received == 0:
            probability += 0.15

        if profile.manager_satisfaction < 5:
            probability += 0.2

        if profile.internal_applications > 2:
            probability += 0.15

        # Fatores de redução
        if profile.job_satisfaction > 8:
            probability -= 0.1

        if profile.salary_percentile > 70:
            probability -= 0.15

        if profile.last_performance_rating > 4:
            probability -= 0.1

        return max(0.05, min(0.95, probability))

    def _determine_churn_risk(self, probability: float) -> ChurnRisk:
        """Determina nível de risco."""
        if probability >= 0.8:
            return ChurnRisk.CRITICO
        elif probability >= 0.6:
            return ChurnRisk.ALTO
        elif probability >= 0.4:
            return ChurnRisk.MEDIO
        elif probability >= 0.2:
            return ChurnRisk.BAIXO
        else:
            return ChurnRisk.MUITO_BAIXO

    def _identify_risk_factors(self, profile: EmployeeProfile) -> list[str]:
        """Identifica fatores de risco."""
        factors = []

        if profile.job_satisfaction < 6:
            factors.append("💔 Baixa satisfação no trabalho")

        if profile.salary_percentile < 50:
            factors.append("💰 Salário abaixo da média do mercado")

        if profile.tenure_months > 24 and profile.promotions_received == 0:
            factors.append("📈 Estagnação na carreira")

        if profile.manager_satisfaction < 6:
            factors.append("👤 Relacionamento ruim com gestor")

        if profile.work_life_balance < 6:
            factors.append("⚖️ Work-life balance inadequado")

        if profile.internal_applications > 1:
            factors.append("🔍 Buscando outras oportunidades")

        if profile.absences_per_month > 2:
            factors.append("😷 Alto índice de faltas")

        return factors

    def _generate_retention_strategies(self, profile: EmployeeProfile, factors: list[str]) -> list[RetentionStrategy]:
        """Gera estratégias de retenção."""
        strategies = []

        if any("salário" in f.lower() for f in factors):
            strategies.append(RetentionStrategy.MELHORIA_SALARIO)

        if any("carreira" in f.lower() for f in factors):
            strategies.append(RetentionStrategy.DESENVOLVIMENTO_CARREIRA)

        if any("work-life" in f.lower() for f in factors):
            strategies.append(RetentionStrategy.FLEXIBILIDADE)

        if any("gestor" in f.lower() for f in factors):
            strategies.append(RetentionStrategy.CLIMA_ORGANIZACIONAL)

        if profile.last_performance_rating > 4 and profile.job_satisfaction < 7:
            strategies.append(RetentionStrategy.RECONHECIMENTO)

        if not strategies:
            strategies.append(RetentionStrategy.RECONHECIMENTO)

        return list(set(strategies))

    def _estimate_time_to_churn(self, profile: EmployeeProfile, probability: float) -> int | None:
        """Estima tempo até saída."""
        if probability < 0.3:
            return None

        base_days = 180  # 6 meses base

        if probability > 0.8:
            base_days = 30
        elif probability > 0.6:
            base_days = 90

        if profile.internal_applications > 2:
            base_days = int(base_days * 0.6)

        if profile.job_satisfaction < 4:
            base_days = int(base_days * 0.5)

        return max(7, base_days)

    async def analyze_department_retention(
        self, department_id: str, employees: list[EmployeeProfile]
    ) -> dict[str, Any]:
        """Analisa retenção no departamento."""
        predictions = []
        for employee in employees:
            pred = await self.predict_employee_churn(employee)
            predictions.append(pred)

        high_risk = [p for p in predictions if p.churn_risk in [ChurnRisk.ALTO, ChurnRisk.CRITICO]]
        avg_prob = sum(p.churn_probability for p in predictions) / len(predictions)

        return {
            "department_id": department_id,
            "total_employees": len(employees),
            "high_risk_count": len(high_risk),
            "average_churn_risk": avg_prob,
            "retention_score": (1 - avg_prob) * 100,
            "high_risk_employees": [
                {"id": p.employee_id, "probability": p.churn_probability, "factors": p.key_risk_factors[:3]}
                for p in high_risk
            ],
        }


def create_hr_ai_service() -> HRAIService:
    """Factory para criar instância do serviço."""
    return HRAIService()
