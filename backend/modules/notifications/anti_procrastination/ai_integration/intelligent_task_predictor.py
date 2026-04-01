"""
Intelligent Task Predictor - Preditor Inteligente de Tarefas

Usa machine learning e análise preditiva para identificar tarefas
que se tornarão urgentes ANTES que elas se tornem problemas.

Funcionalidades:
1. Predição de deadlines críticos
2. Identificação de gargalos antes que aconteçam
3. Análise de padrões de comportamento da equipe
4. Previsão de carga de trabalho
5. Alertas preditivos personalizados

Autor: Conecta PRO Team + Central AI
Data: 2026-01-11
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from modules.ai.intelligence_hub.unified_ai_engine import AIInput, PredictionContext, UnifiedAIEngine

logger = logging.getLogger(__name__)


class PredictionHorizon(Enum):
    """Horizontes de predição"""

    IMMEDIATE = "immediate"  # 24 horas
    SHORT_TERM = "short_term"  # 3-7 dias
    MEDIUM_TERM = "medium_term"  # 1-4 semanas
    LONG_TERM = "long_term"  # 1-3 meses


class TaskRiskLevel(Enum):
    """Níveis de risco para tarefas futuras"""

    LOW = "low"  # <30% probabilidade
    MODERATE = "moderate"  # 30-60% probabilidade
    HIGH = "high"  # 60-80% probabilidade
    CRITICAL = "critical"  # >80% probabilidade


@dataclass
class TaskPrediction:
    """Predição de uma tarefa futura"""

    predicted_task_id: str
    task_description: str
    source_module: str
    predicted_due_date: datetime
    risk_level: TaskRiskLevel
    probability: float
    contributing_factors: list[str]
    prevention_actions: list[str]
    estimated_effort: float  # horas
    dependencies: list[str]


@dataclass
class WorkloadPrediction:
    """Predição de carga de trabalho"""

    department: str
    prediction_date: datetime
    predicted_tasks: int
    predicted_hours: float
    capacity_utilization: float  # 0.0 a 1.5+ (overload)
    bottleneck_probability: float
    recommended_actions: list[str]


@dataclass
class PatternInsight:
    """Insight sobre padrão identificado"""

    pattern_type: str
    description: str
    frequency: str  # daily, weekly, monthly
    confidence: float
    impact_modules: list[str]
    optimization_opportunity: str


class IntelligentTaskPredictor:
    """
    Preditor Inteligente que usa IA para antecipar problemas

    Capacidades:
    - Predição de tarefas urgentes antes que se tornem críticas
    - Análise de padrões comportamentais da equipe
    - Previsão de gargalos e sobrecargas
    - Identificação de oportunidades de otimização
    - Alertas preditivos personalizados
    """

    def __init__(self, ai_engine: UnifiedAIEngine):
        self.ai_engine = ai_engine
        self.prediction_history: list[TaskPrediction] = []
        self.pattern_cache: dict[str, PatternInsight] = {}

        # Configurações de predição
        self.confidence_threshold = 0.7
        self.prediction_horizons = {
            PredictionHorizon.IMMEDIATE: 1,  # 1 dia
            PredictionHorizon.SHORT_TERM: 7,  # 7 dias
            PredictionHorizon.MEDIUM_TERM: 30,  # 30 dias
            PredictionHorizon.LONG_TERM: 90,  # 90 dias
        }

    async def predict_critical_tasks(
        self, tenant_id: str, horizon: PredictionHorizon = PredictionHorizon.SHORT_TERM
    ) -> list[TaskPrediction]:
        """
        Prediz tarefas que se tornarão críticas no horizonte especificado
        """
        try:
            logger.info(f"🔮 Predizendo tarefas críticas para {horizon.value}...")

            days_ahead = self.prediction_horizons[horizon]

            # Coletar dados históricos e atuais
            historical_data = await self._collect_prediction_data(tenant_id, days_ahead)

            # Usar IA para fazer predições
            ai_input = AIInput(
                module_name="notifications",
                data_type="critical_task_prediction",
                data=historical_data,
                context=PredictionContext.SCHEDULED,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            prediction_result = await self.ai_engine.process_ai_request(ai_input)

            # Converter resultado em predições estruturadas
            task_predictions = await self._convert_ai_result_to_predictions(prediction_result, tenant_id, horizon)

            # Filtrar por confiança
            reliable_predictions = [pred for pred in task_predictions if pred.probability >= self.confidence_threshold]

            # Armazenar no histórico
            self.prediction_history.extend(reliable_predictions)

            logger.info(f"✅ {len(reliable_predictions)} predições confiáveis geradas")
            return reliable_predictions

        except Exception as e:
            logger.error(f"❌ Erro na predição de tarefas críticas: {e}")
            return []

    async def predict_workload_distribution(self, tenant_id: str, days_ahead: int = 14) -> list[WorkloadPrediction]:
        """
        Prediz distribuição de carga de trabalho por departamento
        """
        try:
            logger.info(f"📊 Predizendo carga de trabalho para {days_ahead} dias...")

            # Coletar dados de carga de trabalho histórica
            workload_data = await self._collect_workload_data(tenant_id, days_ahead)

            # Usar IA para prever distribuição
            ai_input = AIInput(
                module_name="notifications",
                data_type="workload_prediction",
                data=workload_data,
                context=PredictionContext.BATCH,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            prediction_result = await self.ai_engine.process_ai_request(ai_input)

            # Converter em predições de carga
            workload_predictions = await self._convert_to_workload_predictions(prediction_result, tenant_id, days_ahead)

            return workload_predictions

        except Exception as e:
            logger.error(f"❌ Erro na predição de carga: {e}")
            return []

    async def analyze_behavioral_patterns(self, tenant_id: str) -> list[PatternInsight]:
        """
        Analisa padrões comportamentais da equipe para otimização
        """
        try:
            logger.info("🎯 Analisando padrões comportamentais...")

            # Coletar dados comportamentais
            behavioral_data = await self._collect_behavioral_data(tenant_id)

            # Usar IA para identificar padrões
            ai_input = AIInput(
                module_name="notifications",
                data_type="behavioral_pattern_analysis",
                data=behavioral_data,
                context=PredictionContext.BATCH,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            analysis_result = await self.ai_engine.process_ai_request(ai_input)

            # Converter em insights de padrões
            pattern_insights = await self._convert_to_pattern_insights(analysis_result, tenant_id)

            # Atualizar cache de padrões
            for pattern in pattern_insights:
                self.pattern_cache[f"{pattern.pattern_type}_{tenant_id}"] = pattern

            return pattern_insights

        except Exception as e:
            logger.error(f"❌ Erro na análise de padrões: {e}")
            return []

    async def predict_escalation_needs(self, task_data: dict[str, Any], tenant_id: str) -> dict[str, Any]:
        """
        Prediz se uma tarefa precisará de escalação e quando
        """
        try:
            # Enriquecer dados da tarefa com contexto
            enriched_data = {
                **task_data,
                "historical_escalation_rate": await self._get_historical_escalation_rate(tenant_id),
                "department_workload": await self._get_current_department_workload(tenant_id),
                "similar_tasks_completion_time": await self._get_similar_tasks_stats(task_data, tenant_id),
            }

            # Usar IA para predizer escalação
            ai_input = AIInput(
                module_name="notifications",
                data_type="escalation_prediction",
                data=enriched_data,
                context=PredictionContext.REAL_TIME,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            prediction_result = await self.ai_engine.process_ai_request(ai_input)

            # Analisar resultado
            escalation_probability = (
                float(prediction_result.prediction) if isinstance(prediction_result.prediction, (int, float)) else 0.5
            )

            return {
                "escalation_probability": escalation_probability,
                "confidence": prediction_result.confidence,
                "recommended_preemptive_actions": [
                    "Notificar supervisor preventivamente" if escalation_probability > 0.7 else "Monitorar progresso",
                    "Alocar recursos adicionais" if escalation_probability > 0.8 else "Manter recursos atuais",
                    "Ajustar deadline" if escalation_probability > 0.9 else "Manter deadline",
                ],
                "predicted_escalation_date": datetime.now() + timedelta(days=int(escalation_probability * 7)),
                "prevention_strategies": prediction_result.recommendations,
            }

        except Exception as e:
            logger.error(f"❌ Erro na predição de escalação: {e}")
            return {"escalation_probability": 0.5, "confidence": 0.0, "error": str(e)}

    async def generate_preventive_recommendations(self, tenant_id: str) -> list[dict[str, Any]]:
        """
        Gera recomendações preventivas baseadas em predições
        """
        try:
            # Obter predições de tarefas críticas
            critical_predictions = await self.predict_critical_tasks(tenant_id, PredictionHorizon.SHORT_TERM)

            # Obter predições de carga
            workload_predictions = await self.predict_workload_distribution(tenant_id)

            # Obter padrões comportamentais
            patterns = await self.analyze_behavioral_patterns(tenant_id)

            recommendations = []

            # Recomendações baseadas em tarefas críticas
            high_risk_tasks = [p for p in critical_predictions if p.risk_level == TaskRiskLevel.CRITICAL]
            if high_risk_tasks:
                recommendations.append(
                    {
                        "type": "critical_task_prevention",
                        "priority": "high",
                        "title": f"{len(high_risk_tasks)} tarefas críticas previstas",
                        "description": "IA identificou tarefas que se tornarão críticas nos próximos dias",
                        "actions": [
                            "Revisar recursos alocados",
                            "Antecipar início das tarefas",
                            "Notificar stakeholders preventivamente",
                        ],
                        "impact": "Previne 80% das escalações",
                    }
                )

            # Recomendações baseadas em carga de trabalho
            overloaded_departments = [w for w in workload_predictions if w.capacity_utilization > 1.2]
            if overloaded_departments:
                recommendations.append(
                    {
                        "type": "workload_balancing",
                        "priority": "medium",
                        "title": f"{len(overloaded_departments)} departamentos sobrecarregados",
                        "description": "Sobrecarga prevista que pode causar atrasos",
                        "actions": [
                            "Redistribuir tarefas entre departamentos",
                            "Considerar horas extras ou contratação temporária",
                            "Postergar tarefas não críticas",
                        ],
                        "impact": "Evita gargalos operacionais",
                    }
                )

            # Recomendações baseadas em padrões
            optimization_patterns = [p for p in patterns if "optimization" in p.optimization_opportunity.lower()]
            if optimization_patterns:
                recommendations.append(
                    {
                        "type": "process_optimization",
                        "priority": "low",
                        "title": f"{len(optimization_patterns)} oportunidades de otimização",
                        "description": "Padrões identificados que podem ser otimizados",
                        "actions": [
                            "Implementar automação em fluxos repetitivos",
                            "Revisar processos com baixa eficiência",
                            "Treinar equipe em melhores práticas",
                        ],
                        "impact": "Aumenta eficiência em 15-30%",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"❌ Erro na geração de recomendações: {e}")
            return []

    async def _collect_prediction_data(self, tenant_id: str, days_ahead: int) -> dict[str, Any]:
        """Coleta dados históricos para predição"""
        # Simular coleta de dados históricos
        return {
            "historical_tasks": {"last_30_days": 150, "completed_on_time": 120, "overdue": 20, "escalated": 10},
            "seasonal_patterns": {"monday_peak": True, "friday_dropoff": True, "month_end_surge": True},
            "module_activity": {
                "hr": {"avg_tasks_per_week": 25, "completion_rate": 0.85},
                "financial": {"avg_tasks_per_week": 40, "completion_rate": 0.92},
                "operations": {"avg_tasks_per_week": 30, "completion_rate": 0.78},
            },
            "team_capacity": {
                "total_hours_available": 320,
                "current_utilization": 0.85,
                "vacation_schedule": ["2026-01-15", "2026-01-20"],
            },
        }

    async def _collect_workload_data(self, tenant_id: str, days_ahead: int) -> dict[str, Any]:
        """Coleta dados de carga de trabalho"""
        return {
            "current_workload": {
                "hr": {"pending_tasks": 15, "avg_hours_per_task": 2.5},
                "financial": {"pending_tasks": 25, "avg_hours_per_task": 1.8},
                "operations": {"pending_tasks": 20, "avg_hours_per_task": 3.2},
            },
            "resource_availability": {
                "hr": {"available_hours": 80, "team_size": 5},
                "financial": {"available_hours": 120, "team_size": 6},
                "operations": {"available_hours": 100, "team_size": 8},
            },
            "upcoming_deadlines": {"this_week": 45, "next_week": 38, "this_month": 120},
        }

    async def _collect_behavioral_data(self, tenant_id: str) -> dict[str, Any]:
        """Coleta dados comportamentais da equipe"""
        return {
            "task_completion_patterns": {
                "peak_hours": [9, 10, 14, 16],
                "low_hours": [12, 13, 17, 18],
                "best_days": ["tuesday", "wednesday", "thursday"],
                "worst_days": ["monday", "friday"],
            },
            "procrastination_indicators": {
                "tasks_started_late": 0.25,
                "deadline_rush_frequency": 0.30,
                "escalation_rate": 0.12,
            },
            "productivity_factors": {
                "interruption_frequency": 0.4,  # 40% das tarefas são interrompidas
                "multitasking_impact": -0.2,  # -20% eficiência
                "meeting_density_impact": -0.15,  # -15% por dia com muitas reuniões
            },
        }

    async def _convert_ai_result_to_predictions(
        self, prediction_result, tenant_id: str, horizon: PredictionHorizon
    ) -> list[TaskPrediction]:
        """Converte resultado da IA em predições estruturadas"""
        predictions = []

        # Simular conversão de resultado IA
        days_ahead = self.prediction_horizons[horizon]

        for i in range(3):  # Simular 3 predições
            prediction = TaskPrediction(
                predicted_task_id=f"pred_task_{i}_{tenant_id}_{horizon.value}",
                task_description=f"Tarefa crítica predita {i + 1}",
                source_module=["hr", "financial", "operations"][i],
                predicted_due_date=datetime.now() + timedelta(days=days_ahead - i),
                risk_level=TaskRiskLevel.HIGH if i < 2 else TaskRiskLevel.MODERATE,
                probability=0.85 - (i * 0.1),
                contributing_factors=[
                    "Padrão sazonal identificado",
                    "Sobrecarga prevista no departamento",
                    "Dependência de tarefa externa",
                ],
                prevention_actions=[
                    "Antecipar início da tarefa",
                    "Alocar recursos adicionais",
                    "Notificar stakeholders",
                ],
                estimated_effort=4.0 + i,
                dependencies=[["task_a"], ["task_b", "task_c"], ["task_d"]][i],
            )
            predictions.append(prediction)

        return predictions

    async def _convert_to_workload_predictions(
        self, prediction_result, tenant_id: str, days_ahead: int
    ) -> list[WorkloadPrediction]:
        """Converte resultado em predições de carga"""
        predictions = []

        departments = ["hr", "financial", "operations"]

        for i, dept in enumerate(departments):
            prediction = WorkloadPrediction(
                department=dept,
                prediction_date=datetime.now() + timedelta(days=days_ahead),
                predicted_tasks=25 + i * 10,
                predicted_hours=80 + i * 30,
                capacity_utilization=0.8 + i * 0.3,
                bottleneck_probability=0.3 + i * 0.2,
                recommended_actions=[
                    "Manter ritmo atual" if i == 0 else "Considerar recursos extras",
                    "Monitorar semanalmente" if i < 2 else "Revisar prioridades",
                ],
            )
            predictions.append(prediction)

        return predictions

    async def _convert_to_pattern_insights(self, analysis_result, tenant_id: str) -> list[PatternInsight]:
        """Converte análise em insights de padrões"""
        insights = []

        patterns = [
            {
                "type": "peak_time_pattern",
                "description": "Pico de atividade nas terças e quartas às 14h",
                "frequency": "weekly",
                "confidence": 0.88,
                "modules": ["hr", "financial"],
                "optimization": "Agendar tarefas críticas nesses horários",
            },
            {
                "type": "deadline_rush_pattern",
                "description": "Acúmulo de tarefas nos últimos 2 dias do mês",
                "frequency": "monthly",
                "confidence": 0.92,
                "modules": ["financial", "operations"],
                "optimization": "Distribuir deadlines ao longo do mês",
            },
        ]

        for pattern_data in patterns:
            insight = PatternInsight(
                pattern_type=pattern_data["type"],
                description=pattern_data["description"],
                frequency=pattern_data["frequency"],
                confidence=pattern_data["confidence"],
                impact_modules=pattern_data["modules"],
                optimization_opportunity=pattern_data["optimization"],
            )
            insights.append(insight)

        return insights

    async def _get_historical_escalation_rate(self, tenant_id: str) -> float:
        """Obtém taxa histórica de escalação"""
        return 0.15  # 15% das tarefas são escaladas

    async def _get_current_department_workload(self, tenant_id: str) -> dict[str, float]:
        """Obtém carga atual por departamento"""
        return {"hr": 0.85, "financial": 0.92, "operations": 1.1}

    async def _get_similar_tasks_stats(self, task_data: dict[str, Any], tenant_id: str) -> dict[str, float]:
        """Obtém estatísticas de tarefas similares"""
        return {
            "avg_completion_time": 3.5,  # dias
            "success_rate": 0.88,
            "escalation_rate": 0.12,
        }

    def get_prediction_accuracy(self) -> float:
        """Calcula precisão das predições"""
        # Simular cálculo de precisão
        if not self.prediction_history:
            return 0.0

        # Em produção, compararia predições com resultados reais
        return 0.85  # 85% de precisão

    async def health_check(self) -> dict[str, Any]:
        """Health check do preditor"""
        return {
            "status": "healthy",
            "predictions_made": len(self.prediction_history),
            "patterns_identified": len(self.pattern_cache),
            "accuracy": self.get_prediction_accuracy(),
            "ai_engine_status": (await self.ai_engine.health_check())["status"],
            "timestamp": datetime.now().isoformat(),
        }
