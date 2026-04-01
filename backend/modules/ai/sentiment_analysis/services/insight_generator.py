"""
Insight Generator Service - Sprint 46

Servico para geracao automatica de insights de feedback.
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai.sentiment_analysis.models import (
    FeedbackInsight,
    InsightPriority,
    InsightType,
    SentimentTrend,
    TrendDirection,
    TrendPeriod,
)
from modules.ai.sentiment_analysis.repositories import SentimentRepository

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Servico de geracao de insights."""

    # Thresholds para deteccao
    SENTIMENT_DROP_THRESHOLD = -15  # Queda de 15 pontos
    SENTIMENT_SPIKE_THRESHOLD = 15  # Aumento de 15 pontos
    CHURN_RISK_THRESHOLD = 5  # Mais de 5 clientes em risco
    COMPLAINT_RATE_THRESHOLD = 15  # Mais de 15% de reclamacoes
    DISSATISFACTION_THRESHOLD = 30  # Mais de 30% insatisfeitos

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SentimentRepository(session)

    async def generate_insights_from_trend(
        self,
        trend: SentimentTrend,
    ) -> list[FeedbackInsight]:
        """
        Gera insights baseados em uma tendencia.

        Args:
            trend: Tendencia de sentimento

        Returns:
            Lista de insights gerados
        """
        insights = []

        # Verificar queda de sentimento
        if trend.score_change and trend.score_change <= self.SENTIMENT_DROP_THRESHOLD:
            insight = await self._create_sentiment_drop_insight(trend)
            insights.append(insight)

        # Verificar pico de sentimento
        if trend.score_change and trend.score_change >= self.SENTIMENT_SPIKE_THRESHOLD:
            insight = await self._create_sentiment_spike_insight(trend)
            insights.append(insight)

        # Verificar risco de churn
        if trend.churn_risk_count >= self.CHURN_RISK_THRESHOLD:
            insight = await self._create_churn_risk_insight(trend)
            insights.append(insight)

        # Verificar taxa de reclamacoes
        if trend.complaints_rate >= self.COMPLAINT_RATE_THRESHOLD:
            insight = await self._create_complaint_alert_insight(trend)
            insights.append(insight)

        # Verificar insatisfacao alta
        if trend.dissatisfaction_rate >= self.DISSATISFACTION_THRESHOLD:
            insight = await self._create_dissatisfaction_insight(trend)
            insights.append(insight)

        # Verificar aspectos negativos recorrentes
        if trend.top_negative_aspects:
            insight = await self._create_recurring_issue_insight(trend)
            if insight:
                insights.append(insight)

        # Verificar tendencia de melhora significativa
        if trend.trend_direction == TrendDirection.IMPROVING and trend.trend_strength >= 50:
            insight = await self._create_success_insight(trend)
            insights.append(insight)

        logger.info(f"Gerados {len(insights)} insights para periodo {trend.period_label}")

        return insights

    async def analyze_and_generate(
        self,
        period_type: TrendPeriod = TrendPeriod.DAILY,
        days_back: int = 1,
    ) -> list[FeedbackInsight]:
        """Analisa dados recentes e gera insights."""
        # Buscar tendencias recentes
        now = datetime.utcnow()
        date_from = now - timedelta(days=days_back)

        trends = await self.repository.list_trends(
            period_type=period_type,
            date_from=date_from,
            date_to=now,
            limit=10,
        )

        all_insights = []
        for trend in trends:
            insights = await self.generate_insights_from_trend(trend)
            all_insights.extend(insights)

        # Gerar insights de oportunidade
        opp_insights = await self._generate_opportunity_insights()
        all_insights.extend(opp_insights)

        return all_insights

    async def _create_sentiment_drop_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight:
        """Cria insight de queda de sentimento."""
        insight = FeedbackInsight(
            title=f"Queda de sentimento detectada ({abs(trend.score_change):.1f} pontos)",
            description=(
                f"O sentimento medio caiu de {trend.prev_avg_score:.1f} para "
                f"{trend.avg_sentiment_score:.1f} no periodo {trend.period_label}. "
                f"Esta queda de {abs(trend.score_change):.1f} pontos requer atencao."
            ),
            insight_type=InsightType.SENTIMENT_DROP,
            priority=InsightPriority.HIGH,
            category="sentimento",
            scope="global",
            impact_score=min(100, abs(trend.score_change) * 3),
            confidence_score=trend.trend_confidence or 70,
            urgency_score=min(100, abs(trend.score_change) * 2.5),
            actionability_score=80,
            period_start=trend.period_start,
            period_end=trend.period_end,
            avg_sentiment=trend.avg_sentiment_score,
            sentiment_change=trend.score_change,
            volume=trend.total_analyses,
            affected_customers=trend.churn_risk_count,
            related_keywords=[k["word"] for k in (trend.top_keywords or [])[:5]],
            related_aspects=trend.top_negative_aspects or [],
            generated_by="system",
        )

        # Adicionar recomendacoes
        insight.add_recommendation(
            action="Revisar feedbacks negativos do periodo",
            expected_impact="Identificar causas raiz da queda",
            effort="medium",
            priority=1,
        )
        insight.add_recommendation(
            action="Contatar clientes insatisfeitos proativamente",
            expected_impact="Recuperar satisfacao e evitar churn",
            effort="high",
            priority=2,
        )

        insight.priority = insight.calculate_priority()

        return await self.repository.create_insight(insight)

    async def _create_sentiment_spike_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight:
        """Cria insight de pico positivo."""
        insight = FeedbackInsight(
            title=f"Melhoria de sentimento detectada (+{trend.score_change:.1f} pontos)",
            description=(
                f"O sentimento medio subiu de {trend.prev_avg_score:.1f} para "
                f"{trend.avg_sentiment_score:.1f} no periodo {trend.period_label}. "
                f"Este aumento indica melhoria na percepcao dos clientes."
            ),
            insight_type=InsightType.SENTIMENT_SPIKE,
            priority=InsightPriority.INFO,
            category="sentimento",
            scope="global",
            impact_score=min(100, trend.score_change * 2),
            confidence_score=trend.trend_confidence or 70,
            urgency_score=20,
            actionability_score=60,
            period_start=trend.period_start,
            period_end=trend.period_end,
            avg_sentiment=trend.avg_sentiment_score,
            sentiment_change=trend.score_change,
            volume=trend.total_analyses,
            related_keywords=[k["word"] for k in (trend.top_keywords or [])[:5]],
            related_aspects=trend.top_positive_aspects or [],
            generated_by="system",
        )

        insight.add_recommendation(
            action="Identificar fatores que contribuiram para melhoria",
            expected_impact="Replicar boas praticas",
            effort="low",
            priority=1,
        )

        return await self.repository.create_insight(insight)

    async def _create_churn_risk_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight:
        """Cria insight de risco de churn."""
        insight = FeedbackInsight(
            title=f"{trend.churn_risk_count} clientes com risco de churn identificados",
            description=(
                f"Foram detectados {trend.churn_risk_count} clientes com indicadores "
                f"de intencao de cancelamento no periodo {trend.period_label}. "
                f"Acao imediata e recomendada para retencao."
            ),
            insight_type=InsightType.CHURN_RISK,
            priority=InsightPriority.CRITICAL,
            category="retencao",
            scope="customer",
            impact_score=min(100, trend.churn_risk_count * 15),
            confidence_score=75,
            urgency_score=90,
            actionability_score=95,
            period_start=trend.period_start,
            period_end=trend.period_end,
            avg_sentiment=trend.avg_sentiment_score,
            affected_customers=trend.churn_risk_count,
            predicted_churn_impact=trend.churn_risk_count * 500.0,  # Estimativa
            generated_by="system",
        )

        insight.add_recommendation(
            action="Contatar clientes em risco imediatamente",
            expected_impact="Retencao de clientes, reducao de churn",
            effort="high",
            priority=1,
        )
        insight.add_recommendation(
            action="Oferecer beneficios ou descontos de retencao",
            expected_impact="Melhorar satisfacao e fidelidade",
            effort="medium",
            priority=2,
        )
        insight.add_recommendation(
            action="Identificar padrao comum nos clientes em risco",
            expected_impact="Prevencao futura de churn",
            effort="medium",
            priority=3,
        )

        return await self.repository.create_insight(insight)

    async def _create_complaint_alert_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight:
        """Cria insight de alerta de reclamacoes."""
        insight = FeedbackInsight(
            title=f"Taxa de reclamacoes elevada: {trend.complaints_rate:.1f}%",
            description=(
                f"A taxa de reclamacoes atingiu {trend.complaints_rate:.1f}% "
                f"no periodo {trend.period_label}, acima do limite aceitavel. "
                f"Total de {trend.complaints_count} reclamacoes em "
                f"{trend.total_analyses} feedbacks."
            ),
            insight_type=InsightType.SERVICE_ISSUE,
            priority=InsightPriority.HIGH,
            category="qualidade",
            subcategory="reclamacoes",
            scope="global",
            impact_score=min(100, trend.complaints_rate * 3),
            confidence_score=85,
            urgency_score=min(100, trend.complaints_rate * 2.5),
            actionability_score=85,
            period_start=trend.period_start,
            period_end=trend.period_end,
            volume=trend.complaints_count,
            related_keywords=[k["word"] for k in (trend.top_keywords or [])[:5]],
            related_aspects=trend.top_negative_aspects or [],
            generated_by="system",
        )

        insight.add_recommendation(
            action="Analisar principais motivos de reclamacao",
            expected_impact="Identificar e corrigir problemas sistemicos",
            effort="medium",
            priority=1,
        )
        insight.add_recommendation(
            action="Revisar processos de atendimento",
            expected_impact="Reducao de reclamacoes recorrentes",
            effort="high",
            priority=2,
        )

        return await self.repository.create_insight(insight)

    async def _create_dissatisfaction_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight:
        """Cria insight de insatisfacao alta."""
        insight = FeedbackInsight(
            title=f"Taxa de insatisfacao elevada: {trend.dissatisfaction_rate:.1f}%",
            description=(
                f"A taxa de insatisfacao (feedbacks negativos) atingiu "
                f"{trend.dissatisfaction_rate:.1f}% no periodo {trend.period_label}. "
                f"Isso indica problemas na experiencia do cliente."
            ),
            insight_type=InsightType.SERVICE_ISSUE,
            priority=InsightPriority.HIGH,
            category="satisfacao",
            scope="global",
            impact_score=min(100, trend.dissatisfaction_rate * 2.5),
            confidence_score=80,
            urgency_score=min(100, trend.dissatisfaction_rate * 2),
            actionability_score=75,
            period_start=trend.period_start,
            period_end=trend.period_end,
            avg_sentiment=trend.avg_sentiment_score,
            volume=trend.total_analyses,
            affected_customers=(trend.negative_count or 0) + (trend.very_negative_count or 0),
            related_aspects=trend.top_negative_aspects or [],
            generated_by="system",
        )

        insight.add_recommendation(
            action="Realizar pesquisa detalhada com clientes insatisfeitos",
            expected_impact="Entender causas profundas da insatisfacao",
            effort="medium",
            priority=1,
        )

        return await self.repository.create_insight(insight)

    async def _create_recurring_issue_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight | None:
        """Cria insight de problema recorrente."""
        if not trend.top_negative_aspects:
            return None

        aspects = trend.top_negative_aspects[:3]

        insight = FeedbackInsight(
            title=f"Problemas recorrentes identificados: {', '.join(aspects)}",
            description=(
                f"Os aspectos {', '.join(aspects)} aparecem consistentemente "
                f"com sentimento negativo nos feedbacks do periodo {trend.period_label}."
            ),
            insight_type=InsightType.RECURRING_ISSUE,
            priority=InsightPriority.MEDIUM,
            category="operacional",
            scope="aspect",
            scope_value=aspects[0] if aspects else None,
            impact_score=65,
            confidence_score=70,
            urgency_score=50,
            actionability_score=80,
            period_start=trend.period_start,
            period_end=trend.period_end,
            related_aspects=aspects,
            generated_by="system",
        )

        insight.add_recommendation(
            action=f"Investigar causa dos problemas em {aspects[0]}",
            expected_impact="Resolucao de problema recorrente",
            effort="medium",
            priority=1,
        )

        return await self.repository.create_insight(insight)

    async def _create_success_insight(
        self,
        trend: SentimentTrend,
    ) -> FeedbackInsight:
        """Cria insight de sucesso/melhoria."""
        insight = FeedbackInsight(
            title="Tendencia de melhoria significativa detectada",
            description=(
                f"O sentimento apresenta tendencia de melhoria com forca de "
                f"{trend.trend_strength:.1f}% no periodo {trend.period_label}. "
                f"Taxa de satisfacao: {trend.satisfaction_rate:.1f}%."
            ),
            insight_type=InsightType.SUCCESS_STORY,
            priority=InsightPriority.INFO,
            category="sucesso",
            scope="global",
            impact_score=trend.trend_strength,
            confidence_score=trend.trend_confidence or 70,
            urgency_score=10,
            actionability_score=40,
            period_start=trend.period_start,
            period_end=trend.period_end,
            avg_sentiment=trend.avg_sentiment_score,
            sentiment_change=trend.score_change,
            volume=trend.total_analyses,
            related_aspects=trend.top_positive_aspects or [],
            generated_by="system",
        )

        insight.add_recommendation(
            action="Documentar praticas que levaram a melhoria",
            expected_impact="Replicacao de sucesso",
            effort="low",
            priority=1,
        )

        return await self.repository.create_insight(insight)

    async def _generate_opportunity_insights(self) -> list[FeedbackInsight]:
        """Gera insights de oportunidade baseados em dados historicos."""
        insights = []

        # Buscar analises com sugestoes
        # (Implementacao simplificada - em producao seria mais sofisticada)

        return insights

    async def get_active_insights(
        self,
        limit: int = 20,
    ) -> list[FeedbackInsight]:
        """Retorna insights ativos."""
        return await self.repository.get_active_insights(limit=limit)

    async def get_critical_insights(
        self,
        limit: int = 10,
    ) -> list[FeedbackInsight]:
        """Retorna insights criticos."""
        return await self.repository.get_critical_insights(limit=limit)

    async def acknowledge_insight(
        self,
        insight_id: UUID,
        user_id: UUID,
    ) -> FeedbackInsight | None:
        """Reconhece um insight."""
        insight = await self.repository.get_insight(insight_id)
        if not insight:
            return None

        insight.acknowledge(user_id)
        await self.repository.update_insight(insight_id)
        return insight

    async def assign_insight(
        self,
        insight_id: UUID,
        user_id: UUID,
        team: str | None = None,
    ) -> FeedbackInsight | None:
        """Atribui insight a um usuario."""
        insight = await self.repository.get_insight(insight_id)
        if not insight:
            return None

        insight.assign(user_id, team)
        await self.repository.update_insight(insight_id)
        return insight

    async def resolve_insight(
        self,
        insight_id: UUID,
        user_id: UUID,
        outcome: str,
        notes: str | None = None,
    ) -> FeedbackInsight | None:
        """Resolve um insight."""
        insight = await self.repository.get_insight(insight_id)
        if not insight:
            return None

        insight.resolve(user_id, outcome, notes)
        await self.repository.update_insight(insight_id)
        return insight

    async def add_insight_feedback(
        self,
        insight_id: UUID,
        was_useful: bool,
        rating: int | None = None,
        notes: str | None = None,
    ) -> FeedbackInsight | None:
        """Adiciona feedback sobre utilidade do insight."""
        insight = await self.repository.get_insight(insight_id)
        if not insight:
            return None

        insight.add_feedback(was_useful, rating, notes)
        await self.repository.update_insight(insight_id)
        return insight

    async def get_insight_stats(self) -> dict[str, Any]:
        """Retorna estatisticas de insights."""
        return await self.repository.get_insight_stats()
