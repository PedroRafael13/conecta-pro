"""
AI Enhanced Escalation - Escalação Inteligente com IA

Sistema de escalação otimizado pela Central de IA que determina:
- QUANDO escalar (timing perfeito)
- PARA QUEM escalar (pessoa certa)
- COMO escalar (tom e canal apropriados)
- POR QUE escalar (contexto inteligente)

Baseado em análise preditiva, histórico de sucesso e contexto cross-module.

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
from modules.ai.intelligence_hub.unified_ai_engine import AIInput, PredictionContext, UnifiedAIEngine

from ..models import Department, EscalationLevel, PendingTaskData, TaskPriority

logger = logging.getLogger(__name__)


class EscalationTiming(Enum):
    """Timing de escalação"""

    IMMEDIATE = "immediate"  # Agora
    URGENT = "urgent"  # Em 1-2 horas
    SCHEDULED = "scheduled"  # Em horário específico
    DELAYED = "delayed"  # Aguardar mais evidências


class EscalationChannel(Enum):
    """Canais de escalação"""

    PHONE_CALL = "phone_call"  # Ligação direta
    SMS = "sms"  # SMS urgente
    EMAIL = "email"  # Email formal
    IN_APP = "in_app"  # Notificação no app
    TEAMS_CHAT = "teams_chat"  # Chat colaborativo
    DASHBOARD = "dashboard"  # Dashboard executivo


class EscalationTone(Enum):
    """Tom da comunicação"""

    URGENT = "urgent"  # Tom urgente
    COLLABORATIVE = "collaborative"  # Tom colaborativo
    INFORMATIVE = "informative"  # Tom informativo
    ESCALATED = "escalated"  # Tom de escalação


@dataclass
class EscalationContext:
    """Contexto para decisão de escalação"""

    task: PendingTaskData
    overdue_hours: float
    previous_escalations: int
    department_workload: float
    cross_module_dependencies: list[str]
    business_impact: float  # 0.0 a 1.0
    team_availability: dict[str, bool]
    historical_success_rate: dict[str, float]


@dataclass
class EscalationDecision:
    """Decisão de escalação otimizada pela IA"""

    should_escalate: bool
    recommended_level: EscalationLevel
    optimal_timing: EscalationTiming
    target_stakeholders: list[str]
    communication_channels: list[EscalationChannel]
    message_tone: EscalationTone
    success_probability: float
    reasoning: str
    alternative_actions: list[str]
    follow_up_schedule: list[datetime]


@dataclass
class EscalationOutcome:
    """Resultado de uma escalação"""

    escalation_id: str
    decision: EscalationDecision
    executed_at: datetime
    actual_outcome: str  # success, partial_success, failure
    resolution_time: timedelta | None
    stakeholder_feedback: dict[str, str]
    lessons_learned: list[str]


class AIEnhancedEscalation:
    """
    Sistema de Escalação Inteligente que usa IA para otimizar
    todas as decisões de escalação:

    - Timing perfeito baseado em análise preditiva
    - Seleção inteligente de stakeholders
    - Personalização de comunicação por contexto
    - Aprendizado contínuo com resultados
    - Integração cross-module para contexto completo
    """

    def __init__(
        self, ai_engine: UnifiedAIEngine, cross_analytics: CrossModuleAnalytics, insight_distributor: InsightDistributor
    ):
        self.ai_engine = ai_engine
        self.cross_analytics = cross_analytics
        self.insight_distributor = insight_distributor

        # Histórico e cache
        self.escalation_history: list[EscalationOutcome] = []
        self.decision_cache: dict[str, EscalationDecision] = {}
        self.stakeholder_performance: dict[str, dict[str, float]] = {}

        # Configurações de otimização
        self.success_threshold = 0.7
        self.learning_rate = 0.1

        # Mapeamentos inteligentes
        self.stakeholder_hierarchy = {
            Department.HR: ["hr_supervisor", "hr_manager", "hr_director", "ceo"],
            Department.FINANCIAL: ["financial_supervisor", "financial_manager", "cfo", "ceo"],
            Department.OPERATIONS: ["ops_supervisor", "ops_manager", "operations_director", "ceo"],
            Department.COMMERCIAL: ["sales_supervisor", "sales_manager", "commercial_director", "ceo"],
        }

    async def analyze_escalation_need(self, task: PendingTaskData, tenant_id: str) -> EscalationDecision:
        """
        Analisa se uma tarefa precisa de escalação usando IA avançada
        """
        try:
            logger.info(f"🤖 Analisando necessidade de escalação para tarefa {task.id}...")

            # Construir contexto completo
            context = await self._build_escalation_context(task, tenant_id)

            # Usar IA para análise
            decision = await self._ai_escalation_analysis(context, tenant_id)

            # Cache da decisão
            self.decision_cache[str(task.id)] = decision

            # Log da decisão
            logger.info(
                f"📊 Decisão: {'Escalar' if decision.should_escalate else 'Não escalar'} "
                f"(probabilidade de sucesso: {decision.success_probability:.1%})"
            )

            return decision

        except Exception as e:
            logger.error(f"❌ Erro na análise de escalação: {e}")
            return self._create_fallback_decision(task)

    async def execute_intelligent_escalation(
        self, decision: EscalationDecision, task: PendingTaskData, tenant_id: str
    ) -> str:
        """
        Executa escalação usando estratégia inteligente
        """
        try:
            escalation_id = str(uuid.uuid4())

            logger.info(f"🚀 Executando escalação inteligente {escalation_id}...")

            # Executar comunicação personalizada
            await self._execute_personalized_communication(decision, task, tenant_id)

            # Configurar follow-ups automáticos
            await self._schedule_intelligent_followups(decision, escalation_id)

            # Criar insights para distribuição
            insight = await self._create_escalation_insight(decision, task, tenant_id)
            await self.insight_distributor.distribute_insight(insight)

            # Registrar outcome inicial
            outcome = EscalationOutcome(
                escalation_id=escalation_id,
                decision=decision,
                executed_at=datetime.now(),
                actual_outcome="in_progress",
                resolution_time=None,
                stakeholder_feedback={},
                lessons_learned=[],
            )
            self.escalation_history.append(outcome)

            logger.info(f"✅ Escalação {escalation_id} executada com sucesso")
            return escalation_id

        except Exception as e:
            logger.error(f"❌ Erro na execução da escalação: {e}")
            raise

    async def optimize_escalation_timing(self, task: PendingTaskData, tenant_id: str) -> dict[str, Any]:
        """
        Otimiza timing de escalação usando análise preditiva
        """
        try:
            # Coletar dados para otimização de timing
            timing_data = {
                "task_priority": task.priority.value,
                "overdue_hours": (datetime.now() - task.due_date).total_seconds() / 3600 if task.due_date else 0,
                "department_activity": await self._get_department_activity_pattern(
                    task.department if hasattr(task, "department") else Department.OPERATIONS, tenant_id
                ),
                "stakeholder_availability": await self._get_stakeholder_availability(tenant_id),
                "historical_escalation_success_by_hour": await self._get_success_by_timing(tenant_id),
            }

            # Usar IA para otimizar timing
            ai_input = AIInput(
                module_name="notifications",
                data_type="escalation_timing_optimization",
                data=timing_data,
                context=PredictionContext.REAL_TIME,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            timing_result = await self.ai_engine.process_ai_request(ai_input)

            # Interpretar resultado
            optimal_delay_hours = (
                float(timing_result.prediction) if isinstance(timing_result.prediction, (int, float)) else 2.0
            )

            return {
                "optimal_timing": datetime.now() + timedelta(hours=optimal_delay_hours),
                "confidence": timing_result.confidence,
                "reasoning": f"IA recomenda aguardar {optimal_delay_hours:.1f}h para timing ótimo",
                "success_probability_now": 0.6,
                "success_probability_optimal": timing_result.confidence,
                "factors_considered": timing_result.insights,
            }

        except Exception as e:
            logger.error(f"❌ Erro na otimização de timing: {e}")
            return {"optimal_timing": datetime.now() + timedelta(hours=2), "confidence": 0.5}

    async def personalize_escalation_message(
        self, decision: EscalationDecision, stakeholder: str, task: PendingTaskData, tenant_id: str
    ) -> dict[str, str]:
        """
        Personaliza mensagem de escalação para stakeholder específico
        """
        try:
            # Obter perfil do stakeholder
            stakeholder_profile = await self._get_stakeholder_profile(stakeholder, tenant_id)

            # Dados para personalização
            personalization_data = {
                "stakeholder_role": stakeholder_profile.get("role", "manager"),
                "communication_preference": stakeholder_profile.get("preference", "formal"),
                "historical_response_pattern": stakeholder_profile.get("response_pattern", "collaborative"),
                "task_context": {
                    "priority": task.priority.value,
                    "category": task.category.value,
                    "overdue_status": (datetime.now() - task.due_date) > timedelta(hours=0) if task.due_date else False,
                },
                "decision_context": {
                    "urgency_level": decision.message_tone.value,
                    "success_probability": decision.success_probability,
                    "alternative_actions": decision.alternative_actions,
                },
            }

            # Usar IA para personalizar
            ai_input = AIInput(
                module_name="notifications",
                data_type="message_personalization",
                data=personalization_data,
                context=PredictionContext.REAL_TIME,
                timestamp=datetime.now(),
                tenant_id=tenant_id,
            )

            await self.ai_engine.process_ai_request(ai_input)

            # Gerar mensagem personalizada
            if decision.message_tone == EscalationTone.URGENT:
                base_message = "🚨 URGENTE: Tarefa crítica requer atenção imediata"
            elif decision.message_tone == EscalationTone.COLLABORATIVE:
                base_message = "🤝 Colaboração necessária: Tarefa precisando de suporte"
            else:
                base_message = "📋 Informativo: Atualização sobre tarefa em andamento"

            personalized_messages = {
                "subject": f"{base_message} - {task.title}",
                "body": self._generate_personalized_body(task, decision, stakeholder_profile),
                "summary": f"Tarefa {task.title} escalada para {stakeholder} com {decision.success_probability:.0%} de chance de sucesso",
                "call_to_action": self._generate_call_to_action(decision, stakeholder_profile),
                "tone": decision.message_tone.value,
                "urgency_indicator": "🔴"
                if decision.message_tone == EscalationTone.URGENT
                else "🟡"
                if decision.message_tone == EscalationTone.ESCALATED
                else "🟢",
            }

            return personalized_messages

        except Exception as e:
            logger.error(f"❌ Erro na personalização da mensagem: {e}")
            return {"subject": f"Escalação: {task.title}", "body": "Tarefa requer atenção."}

    async def learn_from_escalation_outcome(self, escalation_id: str, outcome_data: dict[str, Any]):
        """
        Aprende com resultado de escalação para melhorar futuras decisões
        """
        try:
            # Encontrar escalação no histórico
            escalation = next((e for e in self.escalation_history if e.escalation_id == escalation_id), None)
            if not escalation:
                logger.warning(f"Escalação {escalation_id} não encontrada no histórico")
                return

            # Atualizar outcome
            escalation.actual_outcome = outcome_data.get("outcome", "unknown")
            escalation.resolution_time = timedelta(seconds=outcome_data.get("resolution_seconds", 0))
            escalation.stakeholder_feedback = outcome_data.get("feedback", {})
            escalation.lessons_learned = outcome_data.get("lessons", [])

            # Atualizar performance dos stakeholders
            for stakeholder in escalation.decision.target_stakeholders:
                if stakeholder not in self.stakeholder_performance:
                    self.stakeholder_performance[stakeholder] = {"success_rate": 0.5, "avg_response_time": 24}

                # Atualizar taxa de sucesso
                current_rate = self.stakeholder_performance[stakeholder]["success_rate"]
                success = (
                    1.0
                    if escalation.actual_outcome == "success"
                    else 0.5
                    if "partial" in escalation.actual_outcome
                    else 0.0
                )
                new_rate = current_rate + self.learning_rate * (success - current_rate)
                self.stakeholder_performance[stakeholder]["success_rate"] = new_rate

                # Atualizar tempo de resposta
                if escalation.resolution_time:
                    response_hours = escalation.resolution_time.total_seconds() / 3600
                    current_time = self.stakeholder_performance[stakeholder]["avg_response_time"]
                    new_time = current_time + self.learning_rate * (response_hours - current_time)
                    self.stakeholder_performance[stakeholder]["avg_response_time"] = new_time

            # Log do aprendizado
            logger.info(f"📚 Aprendizado registrado para escalação {escalation_id}: {escalation.actual_outcome}")

        except Exception as e:
            logger.error(f"❌ Erro no aprendizado: {e}")

    async def _build_escalation_context(self, task: PendingTaskData, tenant_id: str) -> EscalationContext:
        """Constrói contexto completo para análise"""

        # Calcular horas de atraso
        overdue_hours = 0.0
        if hasattr(task, "due_date") and task.due_date:
            overdue_hours = max(0, (datetime.now() - task.due_date).total_seconds() / 3600)

        # Obter correlações cross-module
        correlations = await self.cross_analytics.analyze_all_correlations(tenant_id)
        dependencies = [c.module_b for c in correlations if c.module_a == task.source_module and c.strength > 0.5]

        return EscalationContext(
            task=task,
            overdue_hours=overdue_hours,
            previous_escalations=await self._get_previous_escalation_count(task, tenant_id),
            department_workload=await self._get_department_workload(
                task.department if hasattr(task, "department") else Department.OPERATIONS, tenant_id
            ),
            cross_module_dependencies=dependencies,
            business_impact=await self._calculate_business_impact(task, tenant_id),
            team_availability=await self._get_team_availability(tenant_id),
            historical_success_rate=await self._get_historical_success_rates(tenant_id),
        )

    async def _ai_escalation_analysis(self, context: EscalationContext, tenant_id: str) -> EscalationDecision:
        """Usa IA para analisar contexto e tomar decisão"""

        # Preparar dados para IA
        analysis_data = {
            "task_priority": context.task.priority.value,
            "overdue_hours": context.overdue_hours,
            "previous_escalations": context.previous_escalations,
            "department_workload": context.department_workload,
            "business_impact": context.business_impact,
            "team_availability_score": sum(context.team_availability.values()) / len(context.team_availability),
            "cross_module_dependency_count": len(context.cross_module_dependencies),
        }

        # Análise com IA
        ai_input = AIInput(
            module_name="notifications",
            data_type="escalation_decision_analysis",
            data=analysis_data,
            context=PredictionContext.REAL_TIME,
            timestamp=datetime.now(),
            tenant_id=tenant_id,
        )

        ai_result = await self.ai_engine.process_ai_request(ai_input)

        # Interpretar resultado e criar decisão
        should_escalate = ai_result.confidence > 0.6

        if should_escalate:
            # Determinar nível de escalação
            if context.overdue_hours > 48 or context.business_impact > 0.8:
                level = EscalationLevel.LEVEL_2
                timing = EscalationTiming.IMMEDIATE
            elif context.overdue_hours > 24 or context.business_impact > 0.6:
                level = EscalationLevel.LEVEL_1
                timing = EscalationTiming.URGENT
            else:
                level = EscalationLevel.LEVEL_1
                timing = EscalationTiming.SCHEDULED

            # Selecionar stakeholders otimizados
            stakeholders = await self._select_optimal_stakeholders(context, level, tenant_id)

            # Determinar canais e tom
            channels = self._determine_optimal_channels(level, timing)
            tone = self._determine_message_tone(context, level)

        else:
            level = EscalationLevel.LEVEL_0
            timing = EscalationTiming.DELAYED
            stakeholders = []
            channels = []
            tone = EscalationTone.INFORMATIVE

        return EscalationDecision(
            should_escalate=should_escalate,
            recommended_level=level,
            optimal_timing=timing,
            target_stakeholders=stakeholders,
            communication_channels=channels,
            message_tone=tone,
            success_probability=ai_result.confidence,
            reasoning=f"Decisão baseada em análise IA: {ai_result.insights[0] if ai_result.insights else 'Análise padrão'}",
            alternative_actions=ai_result.recommendations,
            follow_up_schedule=self._generate_followup_schedule(level, timing),
        )

    async def _select_optimal_stakeholders(
        self, context: EscalationContext, level: EscalationLevel, tenant_id: str
    ) -> list[str]:
        """Seleciona stakeholders otimizados baseado em performance histórica"""

        department = context.task.department if hasattr(context.task, "department") else Department.OPERATIONS
        hierarchy = self.stakeholder_hierarchy.get(department, ["supervisor", "manager", "director", "ceo"])

        # Selecionar baseado no nível
        level_index = min(level.value, len(hierarchy) - 1)
        primary_stakeholder = hierarchy[level_index]

        # Adicionar stakeholder secundário se necessário
        stakeholders = [primary_stakeholder]
        if level.value > 1 and level_index + 1 < len(hierarchy):
            stakeholders.append(hierarchy[level_index + 1])

        return stakeholders

    def _determine_optimal_channels(self, level: EscalationLevel, timing: EscalationTiming) -> list[EscalationChannel]:
        """Determina canais ótimos baseado em nível e timing"""

        if timing == EscalationTiming.IMMEDIATE:
            return [EscalationChannel.PHONE_CALL, EscalationChannel.SMS]
        elif timing == EscalationTiming.URGENT:
            return [EscalationChannel.SMS, EscalationChannel.EMAIL]
        else:
            return [EscalationChannel.EMAIL, EscalationChannel.IN_APP]

    def _determine_message_tone(self, context: EscalationContext, level: EscalationLevel) -> EscalationTone:
        """Determina tom da mensagem baseado em contexto"""

        if context.business_impact > 0.8 or context.overdue_hours > 48:
            return EscalationTone.URGENT
        elif level.value > 1:
            return EscalationTone.ESCALATED
        elif context.cross_module_dependencies:
            return EscalationTone.COLLABORATIVE
        else:
            return EscalationTone.INFORMATIVE

    def _generate_followup_schedule(self, level: EscalationLevel, timing: EscalationTiming) -> list[datetime]:
        """Gera agenda de follow-ups"""

        base_time = datetime.now()
        schedule = []

        if level.value == 0:
            # Nível 0: follow-up em 24h
            schedule.append(base_time + timedelta(hours=24))
        elif level.value == 1:
            # Nível 1: follow-ups em 4h e 24h
            schedule.extend([base_time + timedelta(hours=4), base_time + timedelta(hours=24)])
        else:
            # Nível 2+: follow-ups em 2h, 8h e 24h
            schedule.extend(
                [base_time + timedelta(hours=2), base_time + timedelta(hours=8), base_time + timedelta(hours=24)]
            )

        return schedule

    # Métodos auxiliares simulados (em produção consultariam banco de dados)
    async def _get_previous_escalation_count(self, task: PendingTaskData, tenant_id: str) -> int:
        return len([e for e in self.escalation_history if e.decision.target_stakeholders])

    async def _get_department_workload(self, department: Department, tenant_id: str) -> float:
        workload_map = {Department.HR: 0.85, Department.FINANCIAL: 0.92, Department.OPERATIONS: 1.1}
        return workload_map.get(department, 0.8)

    async def _calculate_business_impact(self, task: PendingTaskData, tenant_id: str) -> float:
        impact_map = {TaskPriority.CRITICAL: 0.9, TaskPriority.HIGH: 0.7, TaskPriority.MEDIUM: 0.4}
        return impact_map.get(task.priority, 0.2)

    async def _get_team_availability(self, tenant_id: str) -> dict[str, bool]:
        return {"manager": True, "supervisor": True, "director": False, "ceo": True}

    async def _get_historical_success_rates(self, tenant_id: str) -> dict[str, float]:
        return {"level_0": 0.6, "level_1": 0.75, "level_2": 0.85}

    def _create_fallback_decision(self, task: PendingTaskData) -> EscalationDecision:
        """Cria decisão padrão em caso de erro"""
        return EscalationDecision(
            should_escalate=task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH],
            recommended_level=EscalationLevel.LEVEL_1,
            optimal_timing=EscalationTiming.URGENT,
            target_stakeholders=["supervisor"],
            communication_channels=[EscalationChannel.EMAIL],
            message_tone=EscalationTone.INFORMATIVE,
            success_probability=0.5,
            reasoning="Decisão padrão devido a erro na análise IA",
            alternative_actions=["Monitorar progresso", "Revisar recursos"],
            follow_up_schedule=[datetime.now() + timedelta(hours=24)],
        )

    # Implementar métodos restantes...
    async def _execute_personalized_communication(
        self, decision: EscalationDecision, task: PendingTaskData, tenant_id: str
    ):
        """Executa comunicação personalizada"""
        logger.info(f"📨 Executando comunicação personalizada para {len(decision.target_stakeholders)} stakeholders")

    async def _schedule_intelligent_followups(self, decision: EscalationDecision, escalation_id: str):
        """Agenda follow-ups inteligentes"""
        logger.info(f"⏰ Agendando {len(decision.follow_up_schedule)} follow-ups para escalação {escalation_id}")

    async def _create_escalation_insight(
        self, decision: EscalationDecision, task: PendingTaskData, tenant_id: str
    ) -> Insight:
        """Cria insight da escalação para distribuição"""
        return Insight(
            id=str(uuid.uuid4()),
            type=InsightType.ALERT,
            priority=InsightPriority.HIGH if decision.recommended_level.value > 1 else InsightPriority.NORMAL,
            source_module="notifications",
            title=f"Escalação Inteligente: {task.title}",
            content=f"IA recomenda escalação nível {decision.recommended_level.value} com {decision.success_probability:.0%} chance de sucesso",
            data={
                "escalation_level": decision.recommended_level.value,
                "success_probability": decision.success_probability,
            },
            tenant_id=tenant_id,
        )

    async def _get_department_activity_pattern(self, department: Department, tenant_id: str) -> dict[str, Any]:
        return {"peak_hours": [9, 14], "response_rate": 0.85}

    async def _get_stakeholder_availability(self, tenant_id: str) -> dict[str, dict[str, Any]]:
        return {
            "manager": {"available": True, "response_time": 2},
            "supervisor": {"available": True, "response_time": 1},
        }

    async def _get_success_by_timing(self, tenant_id: str) -> dict[int, float]:
        return {9: 0.85, 10: 0.9, 14: 0.88, 16: 0.75}  # Success rate by hour

    async def _get_stakeholder_profile(self, stakeholder: str, tenant_id: str) -> dict[str, Any]:
        return {"role": "manager", "preference": "email", "response_pattern": "collaborative"}

    def _generate_personalized_body(
        self, task: PendingTaskData, decision: EscalationDecision, profile: dict[str, Any]
    ) -> str:
        return f"Tarefa {task.title} requer atenção. Recomendação IA: {decision.reasoning}"

    def _generate_call_to_action(self, decision: EscalationDecision, profile: dict[str, Any]) -> str:
        return "Por favor, revisar e tomar ação apropriada."

    async def health_check(self) -> dict[str, Any]:
        """Health check do sistema de escalação"""
        return {
            "status": "healthy",
            "escalations_processed": len(self.escalation_history),
            "decisions_cached": len(self.decision_cache),
            "stakeholder_profiles": len(self.stakeholder_performance),
            "average_success_rate": sum(h.success_probability for h in [e.decision for e in self.escalation_history])
            / max(len(self.escalation_history), 1),
            "timestamp": datetime.now().isoformat(),
        }
