"""
AI Anti-Procrastination Engine - Motor Inteligente Anti-Procrastinação

Este é o componente principal que integra a Central de IA com o sistema
anti-procrastinação existente, transformando-o em um sistema preditivo
e verdadeiramente inteligente.

Funcionalidades:
1. Predição de tarefas antes de se tornarem urgentes
2. Escalação inteligente baseada em contexto e histórico
3. Análise cross-module de dependências de tarefas
4. Alertas personalizados com insights de IA
5. Distribuição inteligente de notificações

Autor: Conecta PRO Team + Central AI
Data: 2026-01-11
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from modules.ai.intelligence_hub.cross_module_analytics import CrossModuleAnalytics
from modules.ai.intelligence_hub.insight_distributor import Insight, InsightDistributor, InsightPriority, InsightType
from modules.ai.intelligence_hub.module_integration_manager import ModuleIntegrationManager
from modules.ai.intelligence_hub.predictive_orchestra import PredictiveOrchestra

# Imports da Central de IA
from modules.ai.intelligence_hub.unified_ai_engine import AIInput, PredictionContext, UnifiedAIEngine

from ..integration.module_integrator import ModuleIntegrator

# Imports do sistema anti-procrastinação existente
from ..models import EscalationLevel, PendingTaskData

logger = logging.getLogger(__name__)


class AIInsightLevel(Enum):
    """Níveis de insights da IA"""

    PREDICTIVE = "predictive"  # Predição de problemas futuros
    REACTIVE = "reactive"  # Reação a problemas atuais
    PREVENTIVE = "preventive"  # Prevenção de problemas
    OPTIMIZATION = "optimization"  # Otimização de processos


@dataclass
class AITaskInsight:
    """Insight gerado pela IA sobre uma tarefa"""

    task_id: str
    insight_level: AIInsightLevel
    prediction_confidence: float
    recommended_action: str
    urgency_score: float
    dependencies: list[str]
    risk_factors: list[str]
    optimization_suggestions: list[str]


@dataclass
class AIEscalationStrategy:
    """Estratégia de escalação sugerida pela IA"""

    task_id: str
    recommended_escalation_level: EscalationLevel
    escalation_reasoning: str
    optimal_timing: datetime
    target_stakeholders: list[str]
    communication_tone: str  # urgent, informative, collaborative
    success_probability: float


class AIAntiProcrastinationEngine:
    """
    Motor Principal da Integração AI + Anti-Procrastinação

    Este é o cérebro do sistema que coordena:
    - Central de IA (predições, analytics, insights)
    - Sistema Anti-Procrastinação existente
    - Módulos do Conecta PRO

    Resultado: Sistema anti-procrastinação verdadeiramente inteligente
    """

    def __init__(self, db_session=None):
        # Componentes da Central de IA
        self.ai_engine = UnifiedAIEngine(db_session)
        self.cross_analytics = CrossModuleAnalytics(db_session)
        self.predictive_orchestra = PredictiveOrchestra()
        self.insight_distributor = InsightDistributor()
        self.module_integration = ModuleIntegrationManager()

        # Sistema anti-procrastinação existente
        self.module_integrator = ModuleIntegrator(db_session) if db_session else None

        # Cache de insights e predições
        self.ai_insights_cache: dict[str, AITaskInsight] = {}
        self.escalation_strategies_cache: dict[str, AIEscalationStrategy] = {}

        # Métricas
        self.metrics = {
            "tasks_predicted": 0,
            "escalations_optimized": 0,
            "procrastination_prevented": 0,
            "ai_accuracy": 0.0,
        }

    async def start_ai_engine(self):
        """Inicia todos os componentes da Central de IA"""
        try:
            logger.info("🧠 Iniciando AI Anti-Procrastination Engine...")

            # Iniciar orquestrador
            await self.predictive_orchestra.start()

            # Iniciar gerenciador de integração
            await self.module_integration.start()

            logger.info("✅ AI Anti-Procrastination Engine iniciado com sucesso!")

        except Exception as e:
            logger.error(f"❌ Erro ao iniciar AI Engine: {e}")
            raise

    async def stop_ai_engine(self):
        """Para todos os componentes da Central de IA"""
        try:
            await self.predictive_orchestra.stop()
            await self.module_integration.stop()
            logger.info("✅ AI Anti-Procrastination Engine parado com sucesso!")

        except Exception as e:
            logger.error(f"❌ Erro ao parar AI Engine: {e}")

    async def predict_future_tasks(self, tenant_id: str, days_ahead: int = 30) -> list[AITaskInsight]:
        """
        Usa IA para prever tarefas que se tornarão urgentes nos próximos dias
        ANTES que elas se tornem problemas
        """
        try:
            logger.info(f"🔮 Predizendo tarefas futuras para tenant {tenant_id}...")

            # Coletar dados históricos de todos os módulos
            historical_data = await self._collect_historical_task_data(tenant_id)

            # Usar IA para predizer padrões
            ai_input = AIInput(
                module_name="notifications",
                data_type="task_prediction",
                data=historical_data,
                context=PredictionContext.SCHEDULED,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            # Processar com Central de IA
            prediction_result = await self.ai_engine.process_ai_request(ai_input)

            # Converter para insights de tarefas
            ai_insights = await self._convert_prediction_to_task_insights(prediction_result, tenant_id, days_ahead)

            # Cache dos insights
            for insight in ai_insights:
                self.ai_insights_cache[insight.task_id] = insight

            self.metrics["tasks_predicted"] += len(ai_insights)

            logger.info(f"✅ {len(ai_insights)} tarefas futuras preditas")
            return ai_insights

        except Exception as e:
            logger.error(f"❌ Erro na predição de tarefas: {e}")
            return []

    async def optimize_escalation_strategy(self, task: PendingTaskData, tenant_id: str) -> AIEscalationStrategy:
        """
        Usa IA para determinar a melhor estratégia de escalação
        baseada em contexto, histórico e análise cross-module
        """
        try:
            # Analisar contexto cross-module
            correlations = await self.cross_analytics.analyze_all_correlations(tenant_id)

            # Preparar dados para IA
            escalation_data = {
                "task_id": str(task.id),
                "priority": task.priority.value,
                "category": task.category.value,
                "overdue_hours": (datetime.now() - task.due_date).total_seconds() / 3600 if task.due_date else 0,
                "department": task.department.value if hasattr(task, "department") else "unknown",
                "cross_module_correlations": len([c for c in correlations if c.strength > 0.7]),
            }

            # Usar IA para otimizar escalação
            ai_input = AIInput(
                module_name="notifications",
                data_type="escalation_optimization",
                data=escalation_data,
                context=PredictionContext.REAL_TIME,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            prediction_result = await self.ai_engine.process_ai_request(ai_input)

            # Converter para estratégia de escalação
            strategy = await self._convert_prediction_to_escalation_strategy(prediction_result, task, tenant_id)

            # Cache da estratégia
            self.escalation_strategies_cache[str(task.id)] = strategy

            self.metrics["escalations_optimized"] += 1

            return strategy

        except Exception as e:
            logger.error(f"❌ Erro na otimização de escalação: {e}")
            # Fallback para estratégia padrão
            return self._create_default_escalation_strategy(task)

    async def generate_intelligent_alerts(self, tenant_id: str) -> list[Insight]:
        """
        Gera alertas inteligentes personalizados usando insights da Central de IA
        """
        try:
            logger.info(f"🚨 Gerando alertas inteligentes para tenant {tenant_id}...")

            # Obter insights integrados da Central de IA
            integrated_insights = await self.cross_analytics.generate_integrated_insights(tenant_id)

            # Obter predições de tarefas
            task_predictions = await self.predict_future_tasks(tenant_id, 7)  # 7 dias

            # Gerar alertas baseados em IA
            intelligent_alerts = []

            # Alertas preditivos
            for prediction in task_predictions:
                if prediction.urgency_score > 0.8:  # Alta urgência
                    alert = Insight(
                        id=str(uuid.uuid4()),
                        type=InsightType.ALERT,
                        priority=InsightPriority.HIGH,
                        source_module="notifications",
                        title=f"⚠️ Tarefa Crítica Prevista: {prediction.recommended_action}",
                        content=f"IA prevê com {prediction.prediction_confidence:.1%} de confiança que esta tarefa se tornará crítica.",
                        data={
                            "task_id": prediction.task_id,
                            "urgency_score": prediction.urgency_score,
                            "risk_factors": prediction.risk_factors,
                            "ai_confidence": prediction.prediction_confidence,
                        },
                        tenant_id=tenant_id,
                    )
                    intelligent_alerts.append(alert)

            # Alertas de correlação cross-module
            risk_modules = integrated_insights.get("risk_modules", [])
            for module in risk_modules:
                alert = Insight(
                    id=str(uuid.uuid4()),
                    type=InsightType.RISK,
                    priority=InsightPriority.NORMAL,
                    source_module="notifications",
                    title=f"🔗 Risco Detectado: Módulo {module}",
                    content=f"Análise cross-module indica risco elevado no módulo {module}. Verificar pendências.",
                    data={"risk_module": module, "correlations": integrated_insights.get("total_correlations", 0)},
                    tenant_id=tenant_id,
                )
                intelligent_alerts.append(alert)

            # Distribuir alertas via Central de IA
            for alert in intelligent_alerts:
                await self.insight_distributor.distribute_insight(alert)

            logger.info(f"✅ {len(intelligent_alerts)} alertas inteligentes gerados e distribuídos")
            return intelligent_alerts

        except Exception as e:
            logger.error(f"❌ Erro na geração de alertas inteligentes: {e}")
            return []

    async def analyze_procrastination_patterns(self, tenant_id: str) -> dict[str, Any]:
        """
        Analisa padrões de procrastinação usando analytics cross-module
        """
        try:
            # Usar analytics da Central de IA para encontrar padrões
            correlations = await self.cross_analytics.analyze_all_correlations(tenant_id)

            # Analisar padrões de procrastinação
            procrastination_patterns = {
                "high_correlation_modules": [
                    {"modules": f"{c.module_a} ↔ {c.module_b}", "strength": c.strength}
                    for c in correlations
                    if c.strength > 0.8
                ],
                "risk_areas": [
                    c.impact_areas
                    for c in correlations
                    if c.strength > 0.7 and "procrastination" in str(c.insights).lower()
                ],
                "optimization_opportunities": [],
            }

            # Gerar recomendações de otimização
            for correlation in correlations:
                if correlation.strength > 0.6:
                    procrastination_patterns["optimization_opportunities"].append(
                        {
                            "area": f"{correlation.module_a} + {correlation.module_b}",
                            "recommendation": f"Sincronizar fluxos entre {correlation.module_a} e {correlation.module_b}",
                            "impact_potential": correlation.strength,
                        }
                    )

            return procrastination_patterns

        except Exception as e:
            logger.error(f"❌ Erro na análise de padrões: {e}")
            return {}

    async def _collect_historical_task_data(self, tenant_id: str) -> dict[str, Any]:
        """Coleta dados históricos de tarefas de todos os módulos"""
        # Simular coleta de dados históricos
        # Em produção, isso consultaria todos os módulos
        return {
            "total_tasks_last_30_days": 250,
            "completed_on_time": 180,
            "overdue_tasks": 45,
            "escalated_tasks": 25,
            "modules_activity": {
                "hr": {"tasks": 50, "completion_rate": 0.85},
                "financial": {"tasks": 80, "completion_rate": 0.92},
                "operations": {"tasks": 60, "completion_rate": 0.78},
                "crm": {"tasks": 35, "completion_rate": 0.88},
            },
            "peak_hours": [9, 14, 16],  # Horários de pico
            "department_performance": {"best": "financial", "worst": "operations", "improving": "hr"},
        }

    async def _convert_prediction_to_task_insights(
        self, prediction_result, tenant_id: str, days_ahead: int
    ) -> list[AITaskInsight]:
        """Converte resultado da IA em insights de tarefas"""
        insights = []

        # Simular conversão de predição para insights
        # Em produção, isso analisaria a predição real da IA
        for i in range(3):  # Simular 3 insights
            insight = AITaskInsight(
                task_id=f"predicted_task_{i}_{uuid.uuid4().hex[:8]}",
                insight_level=AIInsightLevel.PREDICTIVE,
                prediction_confidence=0.85 + (i * 0.05),
                recommended_action=f"Ação preventiva {i + 1}: Verificar pendências do módulo",
                urgency_score=0.7 + (i * 0.1),
                dependencies=["hr", "financial"] if i % 2 == 0 else ["operations", "crm"],
                risk_factors=[f"Risco {i + 1}: Acúmulo de pendências"],
                optimization_suggestions=[f"Otimizar fluxo {i + 1}"],
            )
            insights.append(insight)

        return insights

    async def _convert_prediction_to_escalation_strategy(
        self, prediction_result, task: PendingTaskData, tenant_id: str
    ) -> AIEscalationStrategy:
        """Converte predição da IA em estratégia de escalação"""

        # Determinar nível de escalação baseado na predição
        confidence = prediction_result.confidence

        if confidence > 0.9:
            escalation_level = EscalationLevel.LEVEL_2
            timing_hours = 2
        elif confidence > 0.7:
            escalation_level = EscalationLevel.LEVEL_1
            timing_hours = 6
        else:
            escalation_level = EscalationLevel.LEVEL_0
            timing_hours = 24

        return AIEscalationStrategy(
            task_id=str(task.id),
            recommended_escalation_level=escalation_level,
            escalation_reasoning=f"IA recomenda escalação nível {escalation_level.value} baseado em {confidence:.1%} de confiança",
            optimal_timing=datetime.now() + timedelta(hours=timing_hours),
            target_stakeholders=["manager", "supervisor"] if escalation_level.value > 0 else ["responsible"],
            communication_tone="urgent" if escalation_level.value > 1 else "informative",
            success_probability=confidence,
        )

    def _create_default_escalation_strategy(self, task: PendingTaskData) -> AIEscalationStrategy:
        """Cria estratégia de escalação padrão em caso de erro"""
        return AIEscalationStrategy(
            task_id=str(task.id),
            recommended_escalation_level=EscalationLevel.LEVEL_1,
            escalation_reasoning="Estratégia padrão - erro na análise de IA",
            optimal_timing=datetime.now() + timedelta(hours=12),
            target_stakeholders=["supervisor"],
            communication_tone="informative",
            success_probability=0.5,
        )

    async def get_ai_enhanced_dashboard_data(self, tenant_id: str) -> dict[str, Any]:
        """
        Gera dados para dashboard com insights da Central de IA
        """
        try:
            # Obter predições futuras
            future_tasks = await self.predict_future_tasks(tenant_id, 15)

            # Obter insights integrados
            integrated_insights = await self.cross_analytics.generate_integrated_insights(tenant_id)

            # Obter padrões de procrastinação
            patterns = await self.analyze_procrastination_patterns(tenant_id)

            # Compilar dados do dashboard
            dashboard_data = {
                "ai_predictions": {
                    "future_critical_tasks": len([t for t in future_tasks if t.urgency_score > 0.8]),
                    "prediction_accuracy": self.metrics.get("ai_accuracy", 0.85),
                    "tasks_prevented": self.metrics.get("procrastination_prevented", 0),
                },
                "cross_module_insights": {
                    "total_correlations": integrated_insights.get("total_correlations", 0),
                    "risk_modules": integrated_insights.get("risk_modules", []),
                    "opportunities": integrated_insights.get("opportunity_modules", []),
                },
                "intelligent_metrics": {
                    "tasks_predicted": self.metrics["tasks_predicted"],
                    "escalations_optimized": self.metrics["escalations_optimized"],
                    "ai_insights_generated": len(self.ai_insights_cache),
                },
                "procrastination_patterns": patterns,
                "ai_recommendations": [
                    "Focar no módulo com maior risco de procrastinação",
                    "Implementar automação nos fluxos de maior correlação",
                    "Revisar processo de escalação baseado em insights IA",
                ],
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"❌ Erro ao gerar dados do dashboard: {e}")
            return {}

    async def health_check(self) -> dict[str, Any]:
        """Health check do AI Anti-Procrastination Engine"""
        try:
            # Verificar saúde dos componentes da Central de IA
            ai_health = await self.ai_engine.health_check()
            analytics_health = await self.cross_analytics.health_check()
            orchestra_health = await self.predictive_orchestra.health_check()
            distributor_health = await self.insight_distributor.health_check()
            integration_health = await self.module_integration.health_check()

            return {
                "status": "healthy",
                "ai_components": {
                    "ai_engine": ai_health["status"],
                    "analytics": analytics_health["status"],
                    "orchestra": orchestra_health["status"],
                    "distributor": distributor_health["status"],
                    "integration": integration_health["status"],
                },
                "metrics": self.metrics,
                "cache_status": {
                    "ai_insights_cached": len(self.ai_insights_cache),
                    "escalation_strategies_cached": len(self.escalation_strategies_cache),
                },
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
