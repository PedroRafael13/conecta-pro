"""
Sentiment Alert Service - Sprint 46

Servico para gerenciamento de alertas baseados em regras de sentimento.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai.sentiment_analysis.models import (
    SentimentAnalysis,
    SentimentRule,
    RuleCategory,
    RuleAction,
)
from modules.ai.sentiment_analysis.repositories import SentimentRepository
from modules.ai.sentiment_analysis.schemas import (
    SentimentRuleCreate,
    RuleEvaluationResult,
)

logger = logging.getLogger(__name__)


class SentimentAlertService:
    """Servico de alertas de sentimento."""

    # Regras padrao do sistema
    DEFAULT_RULES = [
        {
            "code": "CRITICAL_NEGATIVE",
            "name": "Sentimento Muito Negativo",
            "description": "Alerta para feedbacks com sentimento muito negativo",
            "category": RuleCategory.SENTIMENT,
            "priority": 100,
            "sentiment_threshold": -60,
            "sentiment_types": ["very_negative"],
            "primary_action": RuleAction.ALERT,
            "secondary_actions": [RuleAction.PRIORITY_BOOST],
            "is_system": True,
        },
        {
            "code": "CHURN_RISK",
            "name": "Risco de Churn Detectado",
            "description": "Alerta quando cliente demonstra intencao de cancelar",
            "category": RuleCategory.CHURN,
            "priority": 95,
            "conditions": [
                {"field": "has_intent_to_leave", "operator": "is_true", "value": True}
            ],
            "primary_action": RuleAction.ESCALATE,
            "secondary_actions": [RuleAction.NOTIFY_EMAIL, RuleAction.CREATE_TICKET],
            "is_system": True,
        },
        {
            "code": "URGENT_ATTENTION",
            "name": "Atencao Urgente Requerida",
            "description": "Alerta para feedbacks com alta urgencia",
            "category": RuleCategory.URGENCY,
            "priority": 90,
            "conditions": [
                {"field": "urgency_level", "operator": "greater_than_or_equal", "value": 7}
            ],
            "primary_action": RuleAction.ALERT,
            "secondary_actions": [RuleAction.PRIORITY_BOOST],
            "is_system": True,
        },
        {
            "code": "COMPLAINT_DETECTED",
            "name": "Reclamacao Detectada",
            "description": "Alerta quando reclamacao e identificada",
            "category": RuleCategory.SENTIMENT,
            "priority": 70,
            "conditions": [
                {"field": "has_complaint", "operator": "is_true", "value": True}
            ],
            "sentiment_threshold": -20,
            "primary_action": RuleAction.TAG,
            "action_config": {"tag": {"tags": ["reclamacao", "requer_atencao"]}},
            "is_system": True,
        },
        {
            "code": "VIP_NEGATIVE",
            "name": "Cliente VIP Insatisfeito",
            "description": "Alerta para clientes VIP com feedback negativo",
            "category": RuleCategory.ESCALATION,
            "priority": 85,
            "sentiment_types": ["negative", "very_negative"],
            "customer_tiers": ["vip", "premium", "gold"],
            "primary_action": RuleAction.ESCALATE,
            "secondary_actions": [RuleAction.NOTIFY_EMAIL],
            "is_system": True,
        },
        {
            "code": "NPS_DETRACTOR",
            "name": "Detrator NPS",
            "description": "Alerta para respostas NPS de detratores (0-6)",
            "category": RuleCategory.SENTIMENT,
            "priority": 75,
            "conditions": [
                {"field": "nps_score", "operator": "less_than_or_equal", "value": 6}
            ],
            "primary_action": RuleAction.TAG,
            "secondary_actions": [RuleAction.LOG],
            "action_config": {"tag": {"tags": ["nps_detrator"]}},
            "is_system": True,
        },
        {
            "code": "ANGER_DETECTED",
            "name": "Raiva Detectada",
            "description": "Alerta quando emocao de raiva e detectada",
            "category": RuleCategory.EMOTION,
            "priority": 80,
            "emotion_types": ["anger", "disgust"],
            "primary_action": RuleAction.ALERT,
            "secondary_actions": [RuleAction.PRIORITY_BOOST],
            "is_system": True,
        },
        {
            "code": "POSITIVE_FEEDBACK",
            "name": "Feedback Positivo",
            "description": "Log de feedbacks muito positivos",
            "category": RuleCategory.SENTIMENT,
            "priority": 30,
            "sentiment_types": ["very_positive"],
            "sentiment_threshold": 60,
            "primary_action": RuleAction.LOG,
            "is_system": True,
        },
    ]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SentimentRepository(session)

    async def initialize_default_rules(self) -> List[SentimentRule]:
        """Inicializa regras padrao do sistema."""
        created_rules = []

        for rule_data in self.DEFAULT_RULES:
            existing = await self.repository.get_rule_by_code(rule_data["code"])
            if not existing:
                rule = SentimentRule(**rule_data)
                rule = await self.repository.create_rule(rule)
                created_rules.append(rule)
                logger.info(f"Regra padrao criada: {rule.code}")

        return created_rules

    async def evaluate_analysis(
        self,
        analysis: SentimentAnalysis,
    ) -> List[RuleEvaluationResult]:
        """
        Avalia todas as regras ativas para uma analise.

        Args:
            analysis: Analise de sentimento

        Returns:
            Lista de resultados de avaliacao
        """
        results = []

        # Buscar regras ativas
        rules = await self.repository.get_active_rules(analysis.source_type)

        # Converter analise para dicionario
        analysis_dict = self._analysis_to_dict(analysis)

        for rule in rules:
            # Verificar cooldown
            if not self._check_cooldown(rule, analysis):
                continue

            # Avaliar regra
            evaluation = rule.evaluate(analysis_dict)

            if evaluation["matched"]:
                result = RuleEvaluationResult(
                    rule_id=rule.id,
                    rule_code=rule.code,
                    rule_name=rule.name,
                    matched=True,
                    conditions_matched=evaluation["conditions_matched"],
                    conditions_total=evaluation["conditions_total"],
                    reasons=evaluation["reasons"],
                    actions_to_execute=rule.get_actions(),
                )
                results.append(result)

                # Incrementar contador
                await self.repository.increment_rule_trigger(rule.id)

                logger.info(
                    f"Regra {rule.code} acionada para analise {analysis.id}"
                )

        return results

    async def execute_actions(
        self,
        results: List[RuleEvaluationResult],
        analysis: SentimentAnalysis,
    ) -> Dict[str, Any]:
        """
        Executa acoes das regras acionadas.

        Args:
            results: Resultados da avaliacao de regras
            analysis: Analise de sentimento

        Returns:
            Resumo das acoes executadas
        """
        executed_actions = []
        errors = []

        for result in results:
            if not result.matched:
                continue

            for action_info in result.actions_to_execute:
                action_type = action_info["action"]
                config = action_info.get("config", {})

                try:
                    action_result = await self._execute_action(
                        action_type=action_type,
                        config=config,
                        analysis=analysis,
                        rule_code=result.rule_code,
                    )
                    executed_actions.append({
                        "rule": result.rule_code,
                        "action": action_type,
                        "result": action_result,
                    })
                except Exception as e:
                    errors.append({
                        "rule": result.rule_code,
                        "action": action_type,
                        "error": str(e),
                    })
                    logger.error(
                        f"Erro ao executar acao {action_type} da regra "
                        f"{result.rule_code}: {e}"
                    )

        return {
            "total_rules_triggered": len(results),
            "actions_executed": len(executed_actions),
            "actions": executed_actions,
            "errors": errors,
        }

    async def _execute_action(
        self,
        action_type: str,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Executa uma acao especifica."""
        action_handlers = {
            "alert": self._action_alert,
            "escalate": self._action_escalate,
            "notify_email": self._action_notify_email,
            "notify_sms": self._action_notify_sms,
            "notify_slack": self._action_notify_slack,
            "create_ticket": self._action_create_ticket,
            "assign_agent": self._action_assign_agent,
            "tag": self._action_tag,
            "priority_boost": self._action_priority_boost,
            "auto_respond": self._action_auto_respond,
            "trigger_workflow": self._action_trigger_workflow,
            "log": self._action_log,
        }

        handler = action_handlers.get(action_type, self._action_log)
        return await handler(config, analysis, rule_code)

    async def _action_alert(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Cria alerta."""
        # Em producao, integraria com sistema de alertas
        logger.warning(
            f"[ALERT] Regra {rule_code} - Analise {analysis.id} - "
            f"Score: {analysis.sentiment_score}"
        )
        return {"alert_created": True, "rule": rule_code}

    async def _action_escalate(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Escalona para nivel superior."""
        escalation_level = config.get("level", "supervisor")
        logger.warning(
            f"[ESCALATION] Regra {rule_code} - Escalando para {escalation_level}"
        )
        return {"escalated": True, "level": escalation_level}

    async def _action_notify_email(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Envia notificacao por email."""
        recipients = config.get("recipients", [])
        # Em producao, integraria com servico de email
        logger.info(
            f"[EMAIL] Regra {rule_code} - Notificando: {recipients}"
        )
        return {"email_sent": True, "recipients": recipients}

    async def _action_notify_sms(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Envia notificacao por SMS."""
        recipients = config.get("recipients", [])
        logger.info(
            f"[SMS] Regra {rule_code} - Notificando: {recipients}"
        )
        return {"sms_sent": True, "recipients": recipients}

    async def _action_notify_slack(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Envia notificacao para Slack."""
        channel = config.get("channel", "#alerts")
        logger.info(
            f"[SLACK] Regra {rule_code} - Canal: {channel}"
        )
        return {"slack_sent": True, "channel": channel}

    async def _action_create_ticket(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Cria ticket de atendimento."""
        queue = config.get("queue", "default")
        priority = config.get("priority", "normal")
        # Em producao, integraria com sistema de tickets
        logger.info(
            f"[TICKET] Regra {rule_code} - Fila: {queue}, Prioridade: {priority}"
        )
        return {"ticket_created": True, "queue": queue, "priority": priority}

    async def _action_assign_agent(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Atribui a um agente especifico."""
        agent_id = config.get("agent_id")
        team = config.get("team")
        logger.info(
            f"[ASSIGN] Regra {rule_code} - Agente: {agent_id}, Team: {team}"
        )
        return {"assigned": True, "agent_id": agent_id, "team": team}

    async def _action_tag(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Adiciona tags a analise."""
        tags = config.get("tags", [])
        current_tags = analysis.tags or []
        new_tags = list(set(current_tags + tags))

        await self.repository.update_analysis(analysis.id, tags=new_tags)

        logger.info(f"[TAG] Regra {rule_code} - Tags: {tags}")
        return {"tagged": True, "tags": tags}

    async def _action_priority_boost(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Aumenta prioridade da analise."""
        boost = config.get("boost", 2)
        # Em producao, ajustaria prioridade no sistema
        logger.info(f"[PRIORITY] Regra {rule_code} - Boost: +{boost}")
        return {"priority_boosted": True, "boost": boost}

    async def _action_auto_respond(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Envia resposta automatica."""
        template = config.get("template", "default")
        # Em producao, enviaria resposta via canal apropriado
        logger.info(f"[AUTO_RESPOND] Regra {rule_code} - Template: {template}")
        return {"auto_responded": True, "template": template}

    async def _action_trigger_workflow(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Dispara workflow externo."""
        workflow_id = config.get("workflow_id")
        # Em producao, integraria com sistema de workflows
        logger.info(f"[WORKFLOW] Regra {rule_code} - Workflow: {workflow_id}")
        return {"workflow_triggered": True, "workflow_id": workflow_id}

    async def _action_log(
        self,
        config: Dict[str, Any],
        analysis: SentimentAnalysis,
        rule_code: str,
    ) -> Dict[str, Any]:
        """Apenas registra em log."""
        message = config.get("message", f"Regra {rule_code} acionada")
        logger.info(f"[LOG] {message} - Analise: {analysis.id}")
        return {"logged": True}

    def _check_cooldown(
        self,
        rule: SentimentRule,
        analysis: SentimentAnalysis,
    ) -> bool:
        """Verifica se regra esta em cooldown."""
        if not rule.cooldown_minutes:
            return True

        if not rule.last_triggered_at:
            return True

        cooldown_end = rule.last_triggered_at + timedelta(
            minutes=rule.cooldown_minutes
        )

        if datetime.utcnow() < cooldown_end:
            # Se cooldown por cliente, verificar se e o mesmo cliente
            if rule.cooldown_per_customer and analysis.customer_id:
                # Simplificado - em producao verificaria por cliente
                return True
            return False

        return True

    def _analysis_to_dict(self, analysis: SentimentAnalysis) -> Dict[str, Any]:
        """Converte analise para dicionario."""
        return {
            "sentiment_score": analysis.sentiment_score,
            "sentiment_type": analysis.sentiment_type.value if analysis.sentiment_type else None,
            "primary_emotion": analysis.primary_emotion.value if analysis.primary_emotion else None,
            "secondary_emotion": analysis.secondary_emotion.value if analysis.secondary_emotion else None,
            "has_urgency": analysis.has_urgency,
            "urgency_level": analysis.urgency_level,
            "has_complaint": analysis.has_complaint,
            "has_intent_to_leave": analysis.has_intent_to_leave,
            "source_type": analysis.source_type.value if analysis.source_type else None,
            "original_text": analysis.original_text,
            "customer_segment": analysis.customer_segment,
            "nps_score": analysis.nps_score,
        }

    # ============================================================
    # Rule Management
    # ============================================================

    async def create_rule(
        self,
        data: SentimentRuleCreate,
        user_id: Optional[UUID] = None,
    ) -> SentimentRule:
        """Cria nova regra."""
        rule = SentimentRule(
            code=data.code,
            name=data.name,
            description=data.description,
            category=data.category,
            subcategory=data.subcategory,
            priority=data.priority,
            weight=data.weight,
            conditions=[c.dict() for c in data.conditions] if data.conditions else [],
            sentiment_threshold=data.sentiment_threshold,
            sentiment_types=[st.value for st in data.sentiment_types] if data.sentiment_types else [],
            emotion_types=[et.value for et in data.emotion_types] if data.emotion_types else [],
            emotion_threshold=data.emotion_threshold,
            keywords_include=data.keywords_include or [],
            keywords_exclude=data.keywords_exclude or [],
            keywords_match_all=data.keywords_match_all,
            aspects_include=data.aspects_include or [],
            aspects_sentiment=data.aspects_sentiment,
            source_types=[st.value for st in data.source_types] if data.source_types else [],
            exclude_sources=[st.value for st in data.exclude_sources] if data.exclude_sources else [],
            customer_segments=data.customer_segments or [],
            customer_tiers=data.customer_tiers or [],
            primary_action=data.primary_action,
            secondary_actions=[a.value for a in data.secondary_actions] if data.secondary_actions else [],
            action_config=data.action_config or {},
            notify_channels=data.notify_channels or [],
            notify_recipients=data.notify_recipients or [],
            notify_template=data.notify_template,
            cooldown_minutes=data.cooldown_minutes,
            cooldown_per_customer=data.cooldown_per_customer,
            max_triggers_per_day=data.max_triggers_per_day,
            active_hours_start=data.active_hours_start,
            active_hours_end=data.active_hours_end,
            active_days=data.active_days or [],
            is_active=data.is_active,
            is_test_mode=data.is_test_mode,
            created_by=user_id,
        )

        return await self.repository.create_rule(rule)

    async def update_rule(
        self,
        rule_id: UUID,
        updates: Dict[str, Any],
        user_id: Optional[UUID] = None,
    ) -> Optional[SentimentRule]:
        """Atualiza regra."""
        rule = await self.repository.get_rule(rule_id)
        if not rule:
            return None

        # Nao permitir editar regras do sistema
        if rule.is_system:
            logger.warning(f"Tentativa de editar regra do sistema: {rule.code}")
            return None

        updates["updated_by"] = user_id
        return await self.repository.update_rule(rule_id, **updates)

    async def delete_rule(self, rule_id: UUID) -> bool:
        """Remove regra (apenas nao-sistema)."""
        return await self.repository.delete_rule(rule_id)

    async def toggle_rule(
        self,
        rule_id: UUID,
        is_active: bool,
    ) -> Optional[SentimentRule]:
        """Ativa/desativa regra."""
        return await self.repository.update_rule(rule_id, is_active=is_active)

    async def record_rule_feedback(
        self,
        rule_id: UUID,
        is_correct: bool,
    ) -> Optional[SentimentRule]:
        """Registra feedback de precisao da regra."""
        rule = await self.repository.get_rule(rule_id)
        if not rule:
            return None

        rule.record_feedback(is_correct)
        await self.repository.update_rule(rule_id)
        return rule

    async def get_rule_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas das regras."""
        rules, total = await self.repository.list_rules(page_size=1000)

        stats = {
            "total": total,
            "active": 0,
            "inactive": 0,
            "by_category": {},
            "total_triggers": 0,
            "rules_with_triggers": 0,
            "avg_precision": 0,
        }

        precision_values = []

        for rule in rules:
            if rule.is_active:
                stats["active"] += 1
            else:
                stats["inactive"] += 1

            category = rule.category.value
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            stats["total_triggers"] += rule.total_triggers or 0

            if rule.total_triggers and rule.total_triggers > 0:
                stats["rules_with_triggers"] += 1

            precision = rule.precision_rate
            if precision is not None:
                precision_values.append(precision)

        if precision_values:
            stats["avg_precision"] = sum(precision_values) / len(precision_values)

        return stats
